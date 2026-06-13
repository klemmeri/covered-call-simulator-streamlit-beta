# Phase 6-5 final exact-marker repair

This repair replaces:

`app\paid_simulator\phase6_dashboard_historical_input_panel_candidate.py`

It keeps the JSON export fix, keeps the contract row-count fix, and writes the
historical-data caution under multiple exact key names and directly into the
contract CSV.

No dashboard change is made.

The dashboard policy remains:

- Synthetic scenarios remain the default.
- Imported historical data remains explicit opt-in only.
- Unknown modes fall back to synthetic.
- Historical data is scenario input, not forecast.
