# Customer-view hard release-label repair

This repair removes remaining local/pre-release label text from the dashboard source:

- `Local prototype / pre-release dashboard`
- `2026-06-11 local checkpoint`
- `local checkpoint`

It replaces the wording with:

- `Beta release`

No simulator engine or option-calculation logic is changed.

Run:

`app\run_customer_view_hard_release_label_repair.py`

Then run:

`app\run_customer_view_hard_release_label_repair_check.py`
