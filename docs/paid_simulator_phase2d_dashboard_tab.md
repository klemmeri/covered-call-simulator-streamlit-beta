# Phase 2D Tuning Dashboard Tab

Generated: 2026-06-12

## Purpose

This package adds a Developer-view-only **Phase 2D tuning** tab to the main Streamlit dashboard.

Phase 2D reviews the premium-model outputs and creates tuning recommendations. The dashboard tab makes those recommendations easy to inspect inside the main application while keeping them hidden from Customer view.

## Replaced file

```text
app\paid_simulator\config_form_app.py
```

## Added files

```text
app\run_paid_simulator_phase2d_dashboard_tab_check.py
docs\paid_simulator_phase2d_dashboard_tab.md
```

## New dashboard tab

In Developer view, the dashboard now includes:

```text
Phase 2D tuning
```

The tab shows:

```text
Phase 2D tuning file status
Tuning summary text
Tuning recommendations table
Validation context
Option premium estimates
Premium-aware payoff context
Buttons to run the Phase 2D tuning pipeline
Button to open the standalone Phase 2D tuning viewer
Links to Phase 2D HTML/text reports
```

The tab is intentionally not shown in Customer view.

## How to test

Run this file in PyCharm:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_phase2d_dashboard_tab_check.py
```

Expected result:

```text
PASS: The Developer-view-only Phase 2D tuning tab is installed and the Phase 2D tuning outputs are present.
```

Then launch the main dashboard:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_form.py
```

Switch the sidebar to:

```text
Dashboard mode: Developer view
```

You should see:

```text
Phase 2D tuning
```

## Important limitation

This tab exposes diagnostic and tuning information only. It does not change the customer-facing simulator logic and does not automatically apply tuning recommendations to the pricing model.
