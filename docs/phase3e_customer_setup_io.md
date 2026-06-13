# Phase 3E-2 — Customer Setup Save/Reload Workflow

This checkpoint adds a standalone customer setup input/output layer for the paid Covered Call Simulator.

It does not modify the Streamlit dashboard yet.

## Added files

```text
app\paid_simulator\phase3e_customer_setup_io.py
app\run_paid_simulator_phase3e_customer_setup_io_check.py
docs\phase3e_customer_setup_io.md
```

## Purpose

Phase 3E-1 created the customer-ready payoff workflow scaffold.

Phase 3E-2 makes the next part functional by adding utilities to:

1. Validate a covered-call setup.
2. Calculate customer-facing payoff metrics.
3. Build a stable JSON payload.
4. Save a setup to disk.
5. Reload a saved setup.
6. List saved customer setups.
7. Export a readable plain-text summary.
8. Generate customer-facing warning messages for risky setups.

## Default saved setup location

Saved setup files are stored under:

```text
outputs\saved_setups\paid_simulator
```

The checkpoint script writes test files under:

```text
outputs\saved_setups\paid_simulator\checkpoint
```

## Customer-facing metrics

The new module calculates:

- breakeven price
- maximum profit in dollars
- maximum profit percentage
- downside cushion in dollars per share
- downside cushion percentage
- assignment-zone starting price
- premium income in dollars
- stock value in dollars

## Warning logic

The warning-message function currently flags:

- strike below current price
- strike very close to current price
- premium that provides only a small downside cushion
- unusually large premium relative to stock price
- very large share positions
- invalid or missing setup fields

These warnings are intentionally conservative and customer-readable.

## Check script

Run this from PyCharm:

```text
app\run_paid_simulator_phase3e_customer_setup_io_check.py
```

Expected final line:

```text
Overall Phase 3E-2 checkpoint status: PASS
```

The checkpoint report is saved to:

```text
outputs\reports\paid_simulator\phase3e_customer_setup_io_checkpoint_report.txt
```

## Installation instructions

1. Open File Explorer.
2. Go to:

```text
C:\Users\ctran\Downloads
```

3. Find the downloaded zip file.
4. Right-click the zip file.
5. Choose:

```text
Extract All...
```

6. Extract directly into:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

7. If Windows asks to merge folders, choose **Yes**.
8. If Windows asks to replace files, choose **Replace the files in the destination**.
9. In PyCharm, right-click the project folder or `app` folder and choose **Reload from Disk**.
10. Run:

```text
app\run_paid_simulator_phase3e_customer_setup_io_check.py
```

## Next checkpoint

After this passes, the next logical checkpoint is:

**Phase 3E-3 — Customer payoff workflow layout model**

That checkpoint should assemble the setup inputs, payoff metrics, warning boxes, and save/reload actions into a customer-facing layout object before integrating it into the dashboard.
