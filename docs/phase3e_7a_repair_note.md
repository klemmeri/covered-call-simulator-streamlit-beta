# Phase 3E-7A Repair Note

This repair package corrects two strict text-check items from the Phase 3E-7A dashboard integration adapter checkpoint.

## Changes

1. The Developer-view protection note now uses the exact phrase `Customer view` expected by the check script.
2. The integration snippet now explicitly names `app/paid_simulator/config_form_app.py` as the dashboard file to edit later.

## Scope

This is a narrow repair package. It does not inject Phase 3E into the dashboard and does not replace `config_form_app.py`.
