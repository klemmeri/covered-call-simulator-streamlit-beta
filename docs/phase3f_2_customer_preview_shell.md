# Phase 3F-2 — Protected Customer Preview Shell

## Purpose

Phase 3F-2 introduces a protected customer-preview shell for the covered-call payoff workbench.

This is not a public Customer-view release. It is a controlled preview layer that lets the project verify customer-facing wording, payoff labels, warning language, and workflow actions before promoting anything into the ordinary Customer view.

## Files added

```text
app\paid_simulator\phase3f_customer_preview_shell.py
app\run_paid_simulator_phase3f_2_customer_preview_shell_check.py
docs\phase3f_2_customer_preview_shell.md
```

## Dashboard safety rule

This package does not modify:

```text
app\paid_simulator\config_form_app.py
```

The customer preview shell remains standalone. The main dashboard must not show Phase 3F as public Customer-view functionality until a later explicit release checkpoint passes.

## Customer-facing labels verified

The check script verifies these customer-facing concepts:

- Current price
- Call strike
- Option premium received
- Breakeven
- Max profit
- Downside cushion
- Assignment zone
- Risk warnings
- Save setup
- Reload saved setup
- Refresh payoff scenario
- Export summary

## Check script

Run:

```text
app\run_paid_simulator_phase3f_2_customer_preview_shell_check.py
```

Expected final line:

```text
Overall Phase 3F-2 checkpoint status: PASS
```

## Outputs

The check writes:

```text
outputs\reports\paid_simulator\phase3f_2_customer_preview_shell_checkpoint_report.txt
outputs\reports\paid_simulator\phase3f_2_customer_preview_shell_checkpoint.json
outputs\tables\paid_simulator\phase3f_2_customer_preview_shell_checklist.csv
```

## Next checkpoint

If Phase 3F-2 passes, the likely next step is Phase 3F-3: a guarded customer-preview dashboard tab or preview route. That step should still keep the ordinary Customer view protected.
