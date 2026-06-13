# Phase 4-4 Historical Price Path Adapter — Path ID Repair

This narrow repair replaces `app\paid_simulator\phase4_historical_price_path_adapter.py`.

The previous repair resolved the Python 3.13 dynamic-import/dataclass issue, but the checkpoint still failed because the generated historical path ID could become blank/NaN when the sample underlying-price input had only one row and no source path identifier.

This repair guarantees a stable default historical path ID:

```text
historical_path_001
```

No dashboard file is changed.
