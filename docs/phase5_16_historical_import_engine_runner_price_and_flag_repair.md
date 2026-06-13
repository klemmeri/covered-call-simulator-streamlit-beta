# Phase 5-16 Historical Import Engine Runner Price and Flag Repair

This repair consolidates the prior Phase 5-16 fixes:

- preserves the robust historical-path price-column fallback,
- reports positive `start_price` and `end_price`, and
- restores the exact checkpoint flag `live_core_engine_replaced = False`.

No dashboard change is made. Historical-import mode remains explicit only, and synthetic mode remains the default.
