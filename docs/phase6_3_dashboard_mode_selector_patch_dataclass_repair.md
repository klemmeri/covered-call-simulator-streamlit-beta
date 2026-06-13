# Phase 6-3 dashboard mode selector patch dataclass repair

This repair replaces `app\paid_simulator\phase6_dashboard_mode_selector_patch.py` with a functionally equivalent version that avoids `@dataclass`.

The Phase 6-3 check script dynamically imports the module. Under Python 3.13, that dynamic import path can trigger a dataclass namespace lookup error before the module is registered in `sys.modules`. The replacement uses plain dictionaries instead.

The repair preserves:

- synthetic mode as the default;
- historical-import mode as explicit opt-in only;
- unknown-mode fallback to synthetic;
- customer caution text that avoids describing historical data as a forecast;
- the Phase 6-3 output artifacts expected by the checkpoint.

No dashboard behavior is changed beyond the already-applied bounded Phase 6-3 helper block.
