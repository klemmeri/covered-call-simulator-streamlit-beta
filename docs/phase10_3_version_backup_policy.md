# Phase 10-3 — Version and backup policy

This checkpoint defines release-version, backup-name, and maintenance-version rules.

It is add-only and makes no dashboard or engine change.

Recommended release candidate version:

`v1.0.0-rc1`

Recommended backup names:

`CoveredCallSimulator_v1_0_0_rc1_YYYY-MM-DD.zip`

`CoveredCallSimulator_Phase10_Complete_v1_0_0_YYYY-MM-DD.zip`

Policy summary:

- Use semantic versioning.
- Use patch versions for bug fixes.
- Use minor versions for backward-compatible features.
- Use major versions only for substantial workflow or architecture changes.
- Keep local and Google Drive backups.
- Exclude secrets, payment credentials, and private deployment tokens from release backups.

Run:

`app\run_paid_simulator_phase10_3_version_backup_policy_check.py`
