# Phase 3H-7 — Controlled Public Customer-view Activation

This checkpoint intentionally enables the public Customer-view activation marker after the prior Phase 3H review gates have passed.

The package adds a small activation model and a guarded installer. The installer appends a syntax-safe block to `app\paid_simulator\config_form_app.py`, after creating a timestamped backup in `outputs\backups\paid_simulator`.

The activation remains controlled because the release is traceable through:

- `PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY`
- `PHASE3H_7_PUBLIC_CUSTOMER_ENABLED = True`
- `PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED`

The checkpoint verifies dashboard syntax, the activation model, customer-facing labels, guardrails, prior phase markers, and backup creation.

If rollback is needed, restore the latest `config_form_app_before_phase3h_7_*.py` backup from `outputs\backups\paid_simulator`.
