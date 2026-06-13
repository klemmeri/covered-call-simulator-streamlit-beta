# Phase 5-3 Range Fillna Repair

This repair replaces `app\paid_simulator\phase5_controlled_historical_path_engine_hook.py`.

The prior version attempted to call `fillna()` with a Python `range` object when creating fallback step numbers. Pandas requires a scalar, dict, or Series for `fillna()`. This repair converts the fallback steps to a pandas Series with the same index as the output DataFrame.

No dashboard files are changed.
No simulator engine files are patched.
Synthetic mode remains the default contract behavior unless historical import is explicitly requested.
