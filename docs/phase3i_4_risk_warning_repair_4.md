# Phase 3I-4 Risk-Warning Repair 4

This repair replaces the Phase 3I-4 checker only.

The prior run showed the risk-warning model and disclosure content were valid. The only remaining failure was a brittle literal check for `PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_ENABLED`, even though the broader controlled-activation evidence was already present and passing.

This checker accepts controlled activation evidence from the dashboard or the Phase 3H-8 post-activation completion report, while still confirming that the workflow remains in the controlled-enabled state.

No dashboard code is modified.
