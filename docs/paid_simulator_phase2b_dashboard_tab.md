# Phase 2B Premium-Model Dashboard Tab

## Purpose

This package adds a **Developer-view-only** tab to the main paid simulator dashboard:

```text
Phase 2B premium model
```

The tab lets the developer inspect the newer premium-aware modeling layer from inside the main dashboard without exposing it in Customer view.

## Files replaced or added

```text
REPLACED:
app\paid_simulator\config_form_app.py

ADDED:
app\run_paid_simulator_phase2b_dashboard_tab_check.py
docs\paid_simulator_phase2b_dashboard_tab.md
```

## Why this is still safe

The stable customer workflow remains unchanged. The new tab appears only when the sidebar is set to:

```text
Dashboard mode: Developer view
```

Customer view remains limited to the cleaner customer-facing tabs.

## What the new tab shows

The tab displays:

```text
Option premium estimates
Premium-aware payoff output
Premium-aware vs older Phase 2 scaffold comparison
Premium-model file status
Buttons to run the Phase 2B pipeline and open the standalone Phase 2B viewer
Links to Phase 2B HTML reports
```

## Test

After extracting the package into the project root, run:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2b_dashboard_tab_check.py
```

Expected final line:

```text
PASS: The Developer-view-only Phase 2B premium-model tab is installed and the Phase 2B outputs are present.
```

## Manual dashboard check

Run the main dashboard:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_form.py
```

Then:

1. Use the sidebar.
2. Select **Developer view**.
3. Open the **Phase 2B premium model** tab.
4. Confirm the tables and status panels display the Phase 2B output files.

## Next likely step

After this passes, the next safe step is a Phase 2B integration-readiness check that confirms the premium-aware model is ready to be promoted from developer diagnostics into the customer-facing workflow.
