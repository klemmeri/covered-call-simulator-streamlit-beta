# Phase 5-3 Controlled Historical Path Engine Hook — Summary Contract Repair

This repair replaces `app\paid_simulator\phase5_controlled_historical_path_engine_hook.py`.

It preserves the pandas `fillna()` repair and restores the exact summary keys expected by the Phase 5-3 checkpoint script:

- `release_decision`
- `dashboard_change_required`
- `hook_mode`
- `requested_mode`
- `selected_mode`
- `hook_contract_created`
- `engine_patch_applied`
- `hook_contract_rows`
- `required_engine_columns_present`
- `historical_engine_ready_path_rows`

No dashboard change is made.
No simulator engine patch is made.
Synthetic mode remains the default until a later controlled engine patch.
