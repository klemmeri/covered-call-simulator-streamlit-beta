# Phase 5-16 Live Core Engine Replacement Flag Repair

This narrow repair preserves the Phase 5-16 historical import engine-runner candidate behavior and explicitly reports:

- `live_core_engine_replaced = False`

The checkpoint expects that exact field to confirm that Phase 5-16 is still a runner-candidate checkpoint and has not replaced any additional live core engine files.

No dashboard change is made.
Synthetic mode remains the default.
Historical-import mode remains explicit only.
