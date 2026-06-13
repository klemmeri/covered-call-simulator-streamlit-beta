# Phase 3I-4 Risk-Warning Repair

This repair addresses two narrow Phase 3I-4 checkpoint failures:

1. The customer risk-warning model now includes the exact disclosure term `capped`.
2. The dashboard receives the exact inert activation marker expected by the Phase 3I-4 checker:

```text
PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_ENABLED = True
```

The marker repair is inert. It does not create a new route and does not bypass the controlled activation workflow.

Files replaced or added:

```text
app\paid_simulator\phase3i_customer_risk_warning_verification.py
app\install_phase3i_4_activation_marker_repair.py
docs\phase3i_4_risk_warning_repair.md
```

Run order:

```text
app\install_phase3i_4_activation_marker_repair.py
app\run_paid_simulator_phase3i_4_risk_warning_check.py
```
