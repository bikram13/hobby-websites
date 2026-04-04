# Phase A1-2 Summary — Finance Tools

**Completed:** 2026-04-03
**Commit:** feat(A1-2): implement finance tools (tip, percentage, EMI calculators)

## What Was Built

Three fully-functional vanilla-JS finance tools implemented inside the existing Eleventy scaffold.

### 1. Tip Calculator (`/finance/tip-calculator/`)
- Inputs: bill amount ($ prefix), tip % via quick-select buttons (10/15/18/20/25/Custom), number of people
- Custom tip shows/hides an input field when selected
- Outputs: tip amount, total bill, per-person share — highlighted row in accent blue
- Calculates on every keystroke; gracefully shows "—" when bill is zero

### 2. Percentage Calculator (`/finance/percentage-calculator/`)
- Three modes accessed via tab buttons: "X% of Y", "X is what % of Y", "% Change"
- Each mode has its own input pair with a formula hint below
- % Change result box turns green for increases, red for decreases
- Handles division-by-zero gracefully (Y=0 → "—")

### 3. Loan / EMI Calculator (`/finance/loan-calculator/`)
- Inputs: principal (₹ prefix), annual interest rate (% suffix), tenure with Years/Months toggle
- Formula: EMI = P × r × (1+r)^n / ((1+r)^n − 1), r = annual_rate/12/100
- Handles zero-rate edge case (EMI = P/n)
- Outputs: monthly EMI (large, accent colour), total interest, total payment
- Disclaimer displayed below results in bordered italic block

## Implementation Details

- All logic in `<script>` blocks inside each `.njk` file — no external dependencies
- Scoped CSS via `<style>` blocks per page — no changes to `main.css`
- Mobile-first responsive layout: single-column on mobile, grid on 560px+
- Each tool has a formula explanation section and 5 FAQ items (HTML only, JSON-LD in A1-3+)
- `aria-live="polite"` on loan results region for screen-reader accessibility

## Status Updates

`_data/tools.js` updated: tip-calculator, percentage-calculator, loan-calculator → `status: "live"`

## Build

Eleventy build passes clean: 14 files written, 0 errors.
