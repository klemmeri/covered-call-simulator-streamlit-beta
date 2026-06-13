# Phase 5-5 Historical-Mode Smoke Test Price Repair

This repair replaces:

```text
app\paid_simulator\phase5_historical_mode_simulation_smoke_test.py
```

The prior Phase 5-5 smoke test successfully created the comparison artifacts but reported:

```text
start_price = 0.0
end_price = 0.0
```

The cause was brittle price-column detection when reading the Phase 5-4 historical-path artifact.

This repair adds a robust price-column fallback that searches common historical-path column names, then falls back to positive numeric price-like columns. It preserves the Phase 5-5 contract:

- no dashboard change
- synthetic mode remains default
- historical mode remains explicit only
- smoke-test comparison remains deterministic and scaffolded

Expected checkpoint result:

```text
Overall Phase 5-5 checkpoint status: PASS
```
