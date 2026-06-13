# Phase 6-5 JSON serialization repair

This repair replaces `app\paid_simulator\phase6_dashboard_historical_input_panel_candidate.py`.

The original Phase 6-5 candidate failed during JSON export with:

```text
Object of type bool is not JSON serializable
```

The replacement keeps the same dashboard input-panel contract, but writes the JSON report from a plain Python dictionary rather than from a structure containing nonstandard scalar types.

No dashboard patch is applied.

Synthetic scenarios remain the default. Imported historical data remains explicit opt-in only. Historical data is described as scenario input, not as a forecast.
