# NEXUS TRADING AGENT — Risk Manager
# Position sizing, trailing stop-loss, daily loss limits
# Trailing stops: floor rises as price rises, locking in gains (Level 1 from strategy notes)

import logging
logger = logging.getLogger(__name__)


class RiskManager:
    """
    Controls position sizing and enforces risk rules.
    NEXUS never risks more than configured limits.

    Trailing stop logic (from TRADING_STRATEGIES_NOTES Level 1):
    - On entry: hard floor at entry * (1 - stop_loss_pct)
    - As price rises: floor trails up to peak * (1 - trail_pct), only moves upward
    - This locks in gains — a +7% trade that reverses won't come back to zero
    """

    def __init__(self, config):
        self.max_position_pct   = config.MAX_POSITION_SIZE_PCT
        self.stop_loss_pct      = config.STOP_LOSS_PCT
        self.target_pct         = config.TARGET_PCT
        self.max_positions      = config.MAX_OPEN_POSITIONS
        self.max_daily_loss_pct = config.MAX_DAILY_LOSS_PCT
        # Trailing stop trails at this % below the running peak
        self.trail_pct = getattr(config, "TRAIL_STOP_PCT", self.stop_loss_pct * 0.8)

    # ── Position sizing ───────────────────────────────────────────────────────

    def calculate_position_size(self, portfolio_value: float, price: float,
                                signal_strength: float = 1.0,
                                gate_prob: float = 0.55) -> int:
        """
        How many shares to buy, scaled by gate_prob (ML win probability).

        gate_prob=0.55 (min threshold) → 8% of portfolio
        gate_prob=1.00 (max confidence) → 15% of portfolio
        Linear interpolation between these. If gate_prob not provided,
        defaults to 0.55 (minimum position). Pass gate_prob=None explicitly
        to fall back to legacy signal_strength scaling.

        Returns 0 if position would be too small.
        """
        if gate_prob is not None:
            # Clamp to [0.55, 1.0] range
            gp = max(0.55, min(1.0, gate_prob))
            # Linear: 0.55→8%, 1.0→15%
            size_pct = 0.08 + (gp - 0.55) / 0.45 * 0.07
        else:
            # Legacy: signal_strength 0→1 maps to 0.5×–1.0× of max_position_pct
            size_pct = self.max_position_pct * (0.5 + signal_strength * 0.5)

        max_capital = portfolio_value * size_pct
        qty = int(max_capital / price)
        if qty < 1:
            logger.warning(f"Position too small: ₹{max_capital:.0f} / ₹{price:.0f} = {qty}")
            return 0
        return qty

    def calculate_stops(self, entry_price: float) -> tuple:
        """
        Returns (initial_stop_loss, target_price).
        Trailing stop starts at this floor; it will be updated via update_trailing_stop().
        """
        stop_loss = entry_price * (1 - self.stop_loss_pct)
        target    = entry_price * (1 + self.target_pct)
        return round(stop_loss, 2), round(target, 2)

    # ── Trailing stop update ─────────────────────────────────────────────────

    def update_trailing_stop(self, position: dict, current_price: float) -> dict:
        """
        Ratchet the trailing stop upward as price rises. Never moves down.
        Call this each day after market close.

        Adds/updates keys in position:
          - peak_price    : highest price seen since entry
          - trailing_stop : current trailing floor (only goes up)
        """
        peak = max(position.get("peak_price", position["entry_price"]), current_price)
        position["peak_price"] = peak

        # New floor = peak * (1 - trail_pct)
        new_trail = round(peak * (1 - self.trail_pct), 2)

        # Only ratchet upward — never lower the floor
        current_trail = position.get("trailing_stop", position["stop_loss"])
        position["trailing_stop"] = max(new_trail, current_trail)

        return position

    # ── Exit conditions ───────────────────────────────────────────────────────

    def check_exit_conditions(self, symbol: str, position: dict,
                               current_price: float) -> tuple:
        """
        Returns (should_exit: bool, reason: str).
        Checks trailing stop first, then hard target.
        """
        # Update trailing stop with today's price
        position = self.update_trailing_stop(position, current_price)

        effective_stop = position.get("trailing_stop", position["stop_loss"])

        if current_price <= effective_stop:
            pnl_pct = (current_price - position["entry_price"]) / position["entry_price"] * 100
            trail_moved = effective_stop > position["stop_loss"]
            label = "Trailing stop" if trail_moved else "Stop loss"
            return True, f"{label} hit: ₹{current_price:.2f} (floor ₹{effective_stop:.2f}, {pnl_pct:+.1f}%)"

        if current_price >= position["target"]:
            gain_pct = (current_price - position["entry_price"]) / position["entry_price"] * 100
            return True, f"Target hit: ₹{current_price:.2f} (+{gain_pct:.1f}%)"

        return False, ""

    # ── Portfolio-level guards ────────────────────────────────────────────────

    def should_stop_trading(self, portfolio_value: float, _initial_capital: float,
                             daily_start_value: float) -> bool:
        """Check if daily loss limit has been hit."""
        daily_loss_pct = (daily_start_value - portfolio_value) / daily_start_value
        if daily_loss_pct >= self.max_daily_loss_pct:
            logger.warning(f"Daily loss limit hit: {daily_loss_pct*100:.1f}%. Halting.")
            return True
        return False

    def can_open_position(self, symbol: str, open_positions: dict) -> bool:
        """Check if we can open a new position."""
        if symbol in open_positions:
            return False
        if len(open_positions) >= self.max_positions:
            return False
        return True
