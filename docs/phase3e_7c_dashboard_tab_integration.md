# Phase 3E-7C — Guarded Dashboard-Tab Integration

## Purpose

Phase 3E-7C prepares the customer payoff workbench for dashboard use while preserving the existing dashboard boundary.

This checkpoint does **not** enable Phase 3E in the Customer view. It adds guarded Developer-view integration hooks and verifies that the older dashboard markers remain intact.

## Added files

```text
app\install_phase3e_7c_dashboard_tab.py
app\run_paid_simulator_phase3e_7c_dashboard_tab_check.py
docs\phase3e_7c_dashboard_tab_integration.md
```

## Existing files touched by installer

The installer may modify:

```text
app\paid_simulator\config_form_app.py
```

Before modifying it, the installer creates a timestamped backup in:

```text
outputs\backups\paid_simulator
```

The backup filename pattern is:

```text
config_form_app_before_phase3e_7c_YYYYMMDD_HHMMSS.py
```

## Safety checks

The installer checks all of the following before patching:

1. The dashboard file exists.
2. Customer-view markers are present.
3. Phase 3D markers are present.
4. The Phase 3E Streamlit panel imports correctly.
5. A backup is created.
6. The patch does not duplicate prior Phase 3E hooks.

## How to run

First run the installer:

```text
app\install_phase3e_7c_dashboard_tab.py
```

Then run the checkpoint:

```text
app\run_paid_simulator_phase3e_7c_dashboard_tab_check.py
```

Expected final line:

```text
Overall Phase 3E-7C checkpoint status: PASS
```

## What this checkpoint means

A PASS means the dashboard is ready for actual Developer-view tab wiring in the next bundled checkpoint.

It does not mean the Phase 3E workbench is customer-facing yet. Customer-view exposure remains blocked until the Phase 3E completion checkpoint.
