# Phase 5-16 Historical Import Engine-Runner Candidate — Price Repair

This repair replaces:

```text
app\paid_simulator\phase5_historical_import_engine_runner_candidate.py
```

It fixes the Phase 5-16 checkpoint failure where `start_price` and `end_price` were reported as `0.0` even though a historical path row existed.

The repaired module now uses a robust price-column fallback that checks common price fields such as:

```text
price
close
adj_close
underlying_price
spot_price
last_price
demo_price
```

If none are found, it falls back to the first positive numeric column that is not obviously an index/count/Greek field.

No dashboard change is made. Synthetic mode remains the default. Historical-import mode remains explicit only.
