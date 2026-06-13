# Paid Simulator Beta Demo Readiness Checklist

## Purpose

This checklist is used before showing the Covered Call Strategy Stress Test to a customer, beta tester, collaborator, or potential user.

The goal is to make sure the dashboard starts from a clean and understandable state, produces current outputs, and does not expose development clutter unless Developer view is intentionally selected.

## Pre-demo setup

1. Open the project in PyCharm:

   ```text
   C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
   ```

2. Run the Streamlit dashboard launcher:

   ```text
   app\run_paid_simulator_form.py
   ```

3. In the dashboard sidebar, set:

   ```text
   Dashboard mode: Customer view
   ```

4. Use the demo controls to reset the dashboard:

   ```text
   Reset and run clean demo
   ```

5. Confirm the Overview tab shows:

   - Product title: Covered Call Strategy Stress Test
   - Ticker: SPY
   - Configuration status: valid
   - HTML report: found
   - Latest result metrics visible
   - Decision guidance visible

## Required demo path

Use this order during a customer-facing walkthrough:

1. **Overview**
   - Explain the purpose: compare a covered-call setup against buy-and-hold across modeled market paths.
   - Point out the best, worst, and average relative results.
   - Explain that a negative average relative result does not necessarily mean the covered call lost money; it means it lagged buy-and-hold across the modeled paths.

2. **Setup & run**
   - Show the clean demo setup.
   - Explain account size, max position size, contracts, target delta, and days to expiration.
   - Show validation and position-size checks.
   - Click Run simulator only if needed.

3. **Latest results**
   - Show the plain-English interpretation.
   - Show decision guidance.
   - Open one or two scenario detail cards.
   - Export a PDF decision memo.

4. **Preset comparison**
   - Explain that presets compare alternative assumptions.
   - Show the recommended preset from the latest comparison.

5. **Report**
   - Open the full HTML report if the user wants more detail.

6. **Help & assumptions**
   - Show limitations and explain that the dashboard is a scenario-analysis tool, not a forecasting engine.

## What not to claim

Do not claim that the simulator:

- Predicts the future.
- Detects the true market regime with certainty.
- Guarantees better returns than buy-and-hold.
- Replaces broker risk controls, tax advice, or personal financial advice.
- Handles every real-world option detail perfectly.

## Customer-facing positioning

Use this phrasing:

> The dashboard is designed to help a user understand the income, risk, and upside tradeoffs of a covered-call setup before opening or comparing positions. It is a decision-support tool, not a trade recommendation engine.

## Demo pass criteria

The demo is ready if:

- Customer view opens cleanly.
- Clean demo reset works.
- Simulator run completes.
- Overview tab summarizes the latest result.
- Latest results tab shows interpretation and decision guidance.
- PDF decision memo exports successfully.
- Report tab opens the generated HTML report.
- Help & assumptions clearly explains limitations.

