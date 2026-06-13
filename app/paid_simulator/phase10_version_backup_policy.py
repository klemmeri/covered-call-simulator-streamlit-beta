"""
phase10_version_backup_policy.py

Phase 10-3 version and backup policy.

This module is passive. It defines release-version, backup-name, and maintenance
versioning rules for the Covered Call Simulator final release workflow.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

POLICY_CSV = OUTPUT_TABLE_DIR / "phase10_3_version_backup_policy.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_3_version_backup_policy_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_3_version_backup_policy.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_3_version_backup_policy_report.txt"

READY_MARKER = "PHASE10_3_VERSION_BACKUP_POLICY_READY"
RELEASE_DECISION = "PHASE10_3_VERSION_BACKUP_POLICY_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "version_backup_policy"

RECOMMENDED_RELEASE_VERSION = "v1.0.0-rc1"
RECOMMENDED_BACKUP_NAME = "CoveredCallSimulator_v1_0_0_rc1_YYYY-MM-DD.zip"
RECOMMENDED_STABLE_BACKUP_NAME = "CoveredCallSimulator_Phase10_Complete_v1_0_0_YYYY-MM-DD.zip"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase10_3_policy() -> list[dict[str, Any]]:
    return [
        {
            "policy_area": "release_version",
            "rule": "Use semantic versioning for customer-facing releases.",
            "recommended_value": RECOMMENDED_RELEASE_VERSION,
            "reason": "v1.0.0-rc1 clearly marks the first release candidate before final v1.0.0.",
            "required_for_release": True,
        },
        {
            "policy_area": "backup_zip_name",
            "rule": "Name backups with product, version, and date.",
            "recommended_value": RECOMMENDED_BACKUP_NAME,
            "reason": "Version and date make Google Drive backups sortable and recoverable.",
            "required_for_release": True,
        },
        {
            "policy_area": "stable_backup_zip_name",
            "rule": "After final smoke testing, create a stable complete-project backup.",
            "recommended_value": RECOMMENDED_STABLE_BACKUP_NAME,
            "reason": "Marks the final Phase 10 complete state separately from release candidates.",
            "required_for_release": True,
        },
        {
            "policy_area": "patch_version",
            "rule": "Use patch versions for bug fixes that do not change customer workflow.",
            "recommended_value": "v1.0.1, v1.0.2, ...",
            "reason": "Bug fixes should not look like major product changes.",
            "required_for_release": True,
        },
        {
            "policy_area": "minor_version",
            "rule": "Use minor versions for new features that preserve backward compatibility.",
            "recommended_value": "v1.1.0, v1.2.0, ...",
            "reason": "Feature additions should be visible but not treated as a new product generation.",
            "required_for_release": True,
        },
        {
            "policy_area": "major_version",
            "rule": "Use major versions only for large architecture or customer-workflow changes.",
            "recommended_value": "v2.0.0",
            "reason": "Major versions should be rare and reserved for material product changes.",
            "required_for_release": False,
        },
        {
            "policy_area": "backup_location",
            "rule": "Keep local backup and Google Drive backup for each release candidate.",
            "recommended_value": "Local project backup plus Google Drive backup folder",
            "reason": "Protects against accidental overwrites, sync issues, and local file corruption.",
            "required_for_release": True,
        },
        {
            "policy_area": "secrets_policy",
            "rule": "Never include secrets, payment credentials, or private deployment tokens in release backups.",
            "recommended_value": "Exclude secrets and deployment credentials",
            "reason": "Release backups should be safe to store and share internally.",
            "required_for_release": True,
        },
    ]


def build_phase10_3_summary() -> dict[str, Any]:
    _ensure_dirs()

    policy = build_phase10_3_policy()
    policy_df = pd.DataFrame(policy)
    policy_df.to_csv(POLICY_CSV, index=False)

    required_count = int(policy_df["required_for_release"].sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "version_backup_policy_created": True,
        "recommended_release_version": RECOMMENDED_RELEASE_VERSION,
        "recommended_backup_name": RECOMMENDED_BACKUP_NAME,
        "recommended_stable_backup_name": RECOMMENDED_STABLE_BACKUP_NAME,
        "semantic_versioning_policy_defined": True,
        "google_drive_backup_policy_defined": True,
        "secrets_exclusion_policy_defined": True,
        "maintenance_version_rules_defined": True,
        "policy_rows": int(len(policy_df)),
        "required_policy_items": required_count,
        "row_count": int(len(policy_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 10-3 version and backup policy",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Recommended release version: {RECOMMENDED_RELEASE_VERSION}",
        f"Recommended backup name: {RECOMMENDED_BACKUP_NAME}",
        f"Recommended stable backup name: {RECOMMENDED_STABLE_BACKUP_NAME}",
        f"Policy rows: {summary['policy_rows']}",
        f"Required policy items: {summary['required_policy_items']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase10_3_summary(), indent=2))
