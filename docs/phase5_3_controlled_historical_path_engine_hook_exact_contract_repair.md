# Phase 5-3 Exact Contract Repair

This repair replaces only:

`app/paid_simulator/phase5_controlled_historical_path_engine_hook.py`

It preserves the pandas `fillna` fix and restores the exact keys and marker values required by the Phase 5-3 checkpoint script:

- `release_decision = PHASE5_3_ENGINE_HOOK_CONTRACT_CREATED_NO_DASHBOARD_CHANGE`
- `source_mode = controlled_historical_path_hook`
- `engine_hook_contract_created = True`
- `required_column_count >= 5`
- `historical_path_rows >= 1`

No dashboard change is made, and no simulator engine patch is applied.
