# Phase 10-5 - Final release candidate smoke test

This checkpoint verifies release-candidate readiness before the final Phase 10
completion handoff.

It is add-only and makes no dashboard or engine change.

It confirms:

- dashboard and core engine files exist;
- Phase 6, Phase 7, Phase 8, and Phase 9 completion handoffs exist;
- Phase 10 release manifest, backup policy, and issue-log template exist;
- synthetic scenarios remain the default;
- historical mode remains explicit opt-in only;
- historical data is scenario input, not a forecast;
- regime detection remains probabilistic guidance, not an oracle.

Run:

`app\run_paid_simulator_phase10_5_final_release_candidate_smoke_test_check.py`
