# NEXUS BRAIN — XGBoost + LightGBM Ensemble Signal Gate (Layer 2)
# Filters raw strategy BUY signals — only passes through high-confidence ones.
#
# How it works:
#   Strategy says BUY → Gate computes 19 features → Ensemble predicts win probability
#   Ensemble: 60% XGBoost + 40% LightGBM blended probabilities
#   If P(win) >= threshold (default 0.60) → pass the signal through
#   Otherwise → suppress (treat as no signal)
#
# Sprint 5: Replaced sklearn GBM with XGBoost+LightGBM ensemble for higher accuracy.

import os
import json
import pickle
import numpy as np
import pandas as pd

from ml.feature_engineer import compute_features, FEATURE_COLS

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../data/ml/signal_gate.pkl")
META_PATH  = os.path.join(os.path.dirname(__file__), "../../data/ml/signal_gate_meta.json")


class SignalGate:
    """
    XGBoost binary classifier that filters BUY signals.

    Usage:
        gate = SignalGate()
        gate.load()   # loads trained model from disk

        # At signal time:
        approved = gate.approve(df_window, raw_signal)
        # approved is the original signal dict if approved, else {"signal": 0, ...}
    """

    def __init__(self, threshold: float = 0.60):
        self.threshold   = threshold
        self.xgb_model   = None   # XGBoost classifier (60% ensemble weight)
        self.lgbm_model  = None   # LightGBM classifier (40% ensemble weight)
        self.model       = None   # kept for backward-compat (unused after Sprint 5)
        self.meta        = {}
        self.trained     = False
        self.nifty_df    = None
        self.live_sentiment: float = 0.0
        self.vix_value:     float = 0.0
        self.sector_data: dict = {}

    # ── Training ──────────────────────────────────────────────────────────────

    def train(self, df_train: pd.DataFrame, threshold: float = None):
        """
        Train XGBoost + LightGBM ensemble on labelled feature DataFrame.
        df_train must have columns = FEATURE_COLS + ['label'].
        Ensemble: 60% XGBoost + 40% LightGBM blended probabilities.
        """
        from xgboost import XGBClassifier
        from lightgbm import LGBMClassifier
        from sklearn.utils.class_weight import compute_sample_weight

        if threshold is not None:
            self.threshold = threshold

        X = df_train[FEATURE_COLS].values
        y = df_train["label"].values
        sample_weights = compute_sample_weight("balanced", y)

        # XGBoost (60% weight in ensemble)
        self.xgb_model = XGBClassifier(
            n_estimators     = 500,
            max_depth        = 4,
            learning_rate    = 0.05,
            subsample        = 0.8,
            colsample_bytree = 0.8,
            eval_metric      = "logloss",
            random_state     = 42,
            verbosity        = 0,
        )
        self.xgb_model.fit(X, y, sample_weight=sample_weights)

        # LightGBM (40% weight in ensemble)
        self.lgbm_model = LGBMClassifier(
            n_estimators     = 500,
            max_depth        = 4,
            learning_rate    = 0.05,
            subsample        = 0.8,
            colsample_bytree = 0.8,
            random_state     = 42,
            verbose          = -1,
        )
        self.lgbm_model.fit(X, y, sample_weight=sample_weights)

        self.trained = True

        # Feature importances: weighted average of both models
        xgb_imp  = self.xgb_model.feature_importances_
        lgbm_imp = self.lgbm_model.feature_importances_
        avg_imp  = xgb_imp * 0.6 + lgbm_imp * 0.4
        importances = dict(zip(FEATURE_COLS, avg_imp))
        sorted_imp  = sorted(importances.items(), key=lambda x: x[1], reverse=True)

        # In-sample accuracy (indicative only)
        xgb_probs  = self.xgb_model.predict_proba(X)[:, 1]
        lgbm_probs = self.lgbm_model.predict_proba(X)[:, 1]
        blended    = 0.6 * xgb_probs + 0.4 * lgbm_probs
        preds      = (blended >= 0.5).astype(int)
        acc        = float((preds == y).mean())

        n_pos = int(y.sum())
        n_neg = len(y) - n_pos
        self.meta = {
            "threshold":          self.threshold,
            "ensemble":           "xgb60_lgbm40",
            "n_train":            len(y),
            "n_positive":         n_pos,
            "n_negative":         n_neg,
            "in_sample_acc":      round(acc, 4),
            "feature_importances": {k: round(float(v), 5) for k, v in sorted_imp},
        }
        return self.meta

    def find_threshold(self, df_val: pd.DataFrame, target_win_rate: float = 0.70) -> float:
        """Find minimum threshold achieving target_win_rate on validation set."""
        if not self.trained:
            raise RuntimeError("Train the model first")

        X          = df_val[FEATURE_COLS].values
        y          = df_val["label"].values
        xgb_probs  = self.xgb_model.predict_proba(X)[:, 1]
        lgbm_probs = self.lgbm_model.predict_proba(X)[:, 1]
        probs      = 0.6 * xgb_probs + 0.4 * lgbm_probs

        best_thresh = self.threshold
        for t in np.arange(0.45, 0.90, 0.01):
            mask     = probs >= t
            kept     = mask.sum()
            if kept < max(10, len(y) * 0.15):
                break
            win_rate = float(y[mask].mean())
            if win_rate >= target_win_rate:
                best_thresh = round(float(t), 2)
                break

        self.threshold = best_thresh
        if self.meta:
            self.meta["threshold"] = best_thresh
        return best_thresh

    # ── Inference ─────────────────────────────────────────────────────────────

    def approve(self, df_window: pd.DataFrame, raw_signal: dict) -> dict:
        """
        Given the OHLCV window up to the signal date and the raw strategy signal,
        return the signal if approved, else a zero-signal dict.

        Two-stage filter:
          Stage 1 — GBM gate: 19 technical features, P(win) >= effective_thresh
          Stage 2 — Sentiment veto/boost (live only, no effect during training):
            live_sentiment < -0.4  → veto even if GBM approved
            live_sentiment > +0.3  → lower effective threshold by 0.05
        """
        if not self.trained or raw_signal["signal"] != 1:
            return raw_signal

        features = compute_features(df_window, nifty_df=self.nifty_df,
                                    sector_data=self.sector_data,
                                    symbol=raw_signal.get("symbol"))
        if features is None:
            return {"signal": 0, "strength": 0, "reason": "Gate: insufficient features"}

        X          = np.array([[features[c] for c in FEATURE_COLS]])
        xgb_prob   = float(self.xgb_model.predict_proba(X)[0, 1])
        lgbm_prob  = float(self.lgbm_model.predict_proba(X)[0, 1])
        prob       = 0.6 * xgb_prob + 0.4 * lgbm_prob

        # Stage 1: Nifty bear-market soft gate
        bear_market      = features.get("nifty_above_ema200", 1.0) == 0.0
        effective_thresh = 0.75 if bear_market else self.threshold

        # VIX-based threshold adjustment (live only — vix_value defaults to 0.0 during training)
        if self.vix_value > 25:
            effective_thresh = min(0.95, effective_thresh + 0.20)
        elif self.vix_value > 20:
            effective_thresh = min(0.95, effective_thresh + 0.10)

        # Sentiment boost: only in bull regime (never weakens bear-market gate)
        sentiment_boost = False
        if self.live_sentiment > 0.3 and not bear_market:
            effective_thresh = max(0.40, effective_thresh - 0.05)
            sentiment_boost  = True

        if prob >= effective_thresh:
            # Stage 2: Sentiment veto (applied after GBM approves)
            if self.live_sentiment < -0.4:
                return {
                    "signal":           0,
                    "strength":         0,
                    "reason":           f"Sentiment veto (score={self.live_sentiment:.2f} < -0.40)",
                    "gate_prob":        round(prob, 3),
                    "gate_approved":    True,
                    "sentiment_vetoed": True,
                    "bear_market":      bear_market,
                }
            approved = dict(raw_signal)
            approved["strength"]        = round(prob, 3)
            approved["gate_prob"]       = round(prob, 3)
            approved["gate_approved"]   = True
            approved["bear_market"]     = bear_market
            approved["sentiment_boost"] = sentiment_boost
            approved["sentiment_score"] = self.live_sentiment
            approved["vix_value"] = self.vix_value
            return approved

        return {
            "signal":        0,
            "strength":      0,
            "reason":        f"Gate blocked (P={prob:.2f} < {effective_thresh:.2f}{'  [bear]' if bear_market else ''})",
            "gate_prob":     round(prob, 3),
            "gate_approved": False,
            "bear_market":   bear_market,
        }

    def predict_proba_batch(self, df_features: pd.DataFrame) -> np.ndarray:
        """Return blended win probability for a batch DataFrame of pre-computed features."""
        if not self.trained:
            raise RuntimeError("Model not trained")
        X          = df_features[FEATURE_COLS].values
        xgb_probs  = self.xgb_model.predict_proba(X)[:, 1]
        lgbm_probs = self.lgbm_model.predict_proba(X)[:, 1]
        return 0.6 * xgb_probs + 0.4 * lgbm_probs

    # ── Persistence ───────────────────────────────────────────────────────────

    def save(self, model_path: str = None, meta_path: str = None):
        model_path = model_path or MODEL_PATH
        meta_path  = meta_path  or META_PATH
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, "wb") as f:
            pickle.dump({"xgb": self.xgb_model, "lgbm": self.lgbm_model}, f)
        with open(meta_path, "w") as f:
            json.dump(self.meta, f, indent=2)
        return model_path

    def load(self, model_path: str = None, meta_path: str = None) -> bool:
        model_path = model_path or MODEL_PATH
        meta_path  = meta_path  or META_PATH
        if not os.path.exists(model_path):
            return False
        with open(model_path, "rb") as f:
            saved = pickle.load(f)
        if isinstance(saved, dict) and "xgb" in saved:
            self.xgb_model  = saved["xgb"]
            self.lgbm_model = saved["lgbm"]
        else:
            print("WARNING: Old GBM model format detected. Retrain required.")
            return False
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                self.meta = json.load(f)
            self.threshold = self.meta.get("threshold", self.threshold)
        self.trained = True
        return True
