# Phase 4-4 Historical Price Path Adapter Function Restore

This repair replaces `app\paid_simulator\phase4_historical_price_path_adapter.py`.

It restores the checkpoint-required public function:

```python
build_phase4_4_summary()
```

It also preserves the prior repair behavior that guarantees a nonblank default historical path ID:

```text
historical_path_001
```

No dashboard changes are included.
