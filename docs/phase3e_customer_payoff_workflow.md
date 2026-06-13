# Phase 3E-1 — Customer Payoff Workflow Scaffold

This checkpoint adds a standalone customer-ready payoff workflow scaffold for the Covered Call Simulator paid dashboard.

It does not replace the main dashboard and does not expose developer/test features to the customer view.

## Added files

```text
app\paid_simulator\phase3e_customer_payoff_workflow.py
app\run_paid_simulator_phase3e_customer_workflow_check.py
docs\phase3e_customer_payoff_workflow.md
```

## Purpose

Phase 3E moves the integrated payoff-overlay work toward a customer-ready Pro workflow.

This first checkpoint creates the foundation only:

1. Customer-facing covered-call setup object.
2. Customer-facing payoff metric calculations.
3. Warning-box logic for risky setups.
4. Save/export setup hook.
5. Reload saved setup hook.
6. A check script that verifies the scaffold without touching the existing dashboard.

## Customer-facing labels included

The scaffold includes clean labels for:

- Current stock price
- Call strike price
- Premium received
- Breakeven price
- Maximum profit if assigned
- Downside cushion from premium
- Assignment zone
- Scenario overlay

## Warning-box logic included

The module currently flags:

- Invalid setup inputs
- Calls already in the assignment zone
- Non-positive maximum profit
- Small downside cushion
- Strike close to current price
- No major setup warnings

These messages are deliberately written for customers rather than developers.

## Export/reload behavior

The export and reload functions are already functional for JSON files.

Default export location:

```text
outputs\tables\paid_simulator\phase3e_customer_payoff_setup.json
```

The check script writes a test export snapshot here:

```text
outputs\tables\paid_simulator\phase3e_customer_payoff_setup_check.json
```

## PyCharm check script

Run this file:

```text
app\run_paid_simulator_phase3e_customer_workflow_check.py
```

Expected final result:

```text
Overall Phase 3E-1 checkpoint status: PASS
```

The checkpoint report is saved to:

```text
outputs\reports\paid_simulator\phase3e_customer_workflow_checkpoint_report.txt
```

## Installation instructions for Windows/PyCharm

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

7. If Windows asks to merge folders, choose Yes.

8. If Windows asks to replace files, choose Replace the files in the destination.

9. In PyCharm, right-click the project folder or app folder and choose Reload from Disk.

10. Run:

    ```text
    app\run_paid_simulator_phase3e_customer_workflow_check.py
    ```

## Next checkpoint after PASS

After this passes, the next logical checkpoint is:

```text
Phase 3E-2 — Customer workflow Streamlit view
```

That checkpoint should add a standalone Streamlit-renderable customer workflow function, still without wiring it into the main dashboard until it passes independently.
