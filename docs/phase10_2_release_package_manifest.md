# Phase 10-2 — Release package manifest

This checkpoint defines the final release-package manifest for the Covered Call
Simulator.

It is add-only and makes no dashboard or engine change.

The manifest distinguishes:

- core files that belong in a release package;
- generated outputs that should usually be recreated;
- local caches and secrets that must not be shipped;
- requirements and release notes that should be included.

Run:

`app\run_paid_simulator_phase10_2_release_package_manifest_check.py`
