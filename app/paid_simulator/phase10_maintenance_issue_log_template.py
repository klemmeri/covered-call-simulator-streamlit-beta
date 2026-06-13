"""
phase10_maintenance_issue_log_template.py

Phase 10-4 maintenance and issue-log template.

This module is passive. It creates the maintenance checklist and issue-log
schema for post-release operation of the Covered Call Simulator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

ISSUE_LOG_CSV = OUTPUT_TABLE_DIR / "phase10_4_maintenance_issue_log_template.csv"
MAINTENANCE_CHECKLIST_CSV = OUTPUT_TABLE_DIR / "phase10_4_maintenance_checklist.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_4_maintenance_issue_log_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_4_maintenance_issue_log_template.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_4_maintenance_issue_log_template_report.txt"

READY_MARKER = "PHASE10_4_MAINTENANCE_ISSUE_LOG_TEMPLATE_READY"
RELEASE_DECISION = "PHASE10_4_MAINTENANCE_ISSUE_LOG_TEMPLATE_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "maintenance_issue_log_template"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase10_4_issue_log_template() -> list[dict[str, Any]]:
    return [
        {
            "field": "issue_id",
            "description": "Unique issue identifier, e.g. CCS-0001.",
            "required": True,
            "example": "CCS-0001",
        },
        {
            "field": "date_reported",
            "description": "Date the issue was reported.",
            "required": True,
            "example": "2026-06-13",
        },
        {
            "field": "reported_by",
            "description": "Tester, customer, or internal source.",
            "required": True,
            "example": "beta_tester_01",
        },
        {
            "field": "area",
            "description": "Dashboard, engine, reports, deployment, documentation, or access control.",
            "required": True,
            "example": "dashboard",
        },
        {
            "field": "severity",
            "description": "low, medium, high, or critical.",
            "required": True,
            "example": "medium",
        },
        {
            "field": "status",
            "description": "open, investigating, fixed, deferred, or closed.",
            "required": True,
            "example": "open",
        },
        {
            "field": "description",
            "description": "Plain-English description of the issue.",
            "required": True,
            "example": "Historical mode label was confusing to the tester.",
        },
        {
            "field": "reproduction_steps",
            "description": "Steps needed to reproduce the issue.",
            "required": False,
            "example": "Open app, select imported historical data, run scenario.",
        },
        {
            "field": "resolution_notes",
            "description": "What was changed or why the issue was deferred.",
            "required": False,
            "example": "Updated customer wording in dashboard help text.",
        },
        {
            "field": "version_fixed",
            "description": "Version where the issue was fixed.",
            "required": False,
            "example": "v1.0.1",
        },
    ]


def build_phase10_4_maintenance_checklist() -> list[dict[str, Any]]:
    return [
        {
            "maintenance_area": "Backups",
            "routine": "Create a dated Google Drive backup before each release or patch.",
            "frequency": "each release",
            "required": True,
        },
        {
            "maintenance_area": "Issue log",
            "routine": "Record all beta/customer defects, wording concerns, and deployment issues.",
            "frequency": "as reported",
            "required": True,
        },
        {
            "maintenance_area": "Regression checks",
            "routine": "Run the final smoke test before every release candidate.",
            "frequency": "each release",
            "required": True,
        },
        {
            "maintenance_area": "Disclaimer review",
            "routine": "Confirm no advisory, guaranteed-profit, risk-free, or oracle wording has reappeared.",
            "frequency": "each release",
            "required": True,
        },
        {
            "maintenance_area": "Data-mode guardrails",
            "routine": "Confirm synthetic default and historical explicit opt-in are preserved.",
            "frequency": "each release",
            "required": True,
        },
        {
            "maintenance_area": "Dependency review",
            "routine": "Check hosted dependencies before deploying or changing hosting providers.",
            "frequency": "each deployment change",
            "required": True,
        },
        {
            "maintenance_area": "Versioning",
            "routine": "Use patch/minor/major version increments according to Phase 10-3 policy.",
            "frequency": "each release",
            "required": True,
        },
        {
            "maintenance_area": "Customer feedback",
            "routine": "Summarize feedback into actionable changes rather than adding open-ended phases.",
            "frequency": "weekly during beta",
            "required": False,
        },
    ]


def build_phase10_4_summary() -> dict[str, Any]:
    _ensure_dirs()

    issue_rows = build_phase10_4_issue_log_template()
    checklist_rows = build_phase10_4_maintenance_checklist()

    issue_df = pd.DataFrame(issue_rows)
    checklist_df = pd.DataFrame(checklist_rows)

    issue_df.to_csv(ISSUE_LOG_CSV, index=False)
    checklist_df.to_csv(MAINTENANCE_CHECKLIST_CSV, index=False)

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "maintenance_issue_log_template_created": True,
        "maintenance_checklist_created": True,
        "issue_log_rows": int(len(issue_df)),
        "maintenance_checklist_rows": int(len(checklist_df)),
        "row_count": int(len(issue_df) + len(checklist_df)),
        "version_policy_reference": "Phase 10-3",
        "backup_policy_reference": "Phase 10-3",
        "final_smoke_test_next": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "regime_detection_probabilistic_not_oracle": True,
        "no_guaranteed_profit_wording": True,
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 10-4 maintenance and issue-log template",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Issue-log rows: {summary['issue_log_rows']}",
        f"Maintenance checklist rows: {summary['maintenance_checklist_rows']}",
        f"Version policy reference: {summary['version_policy_reference']}",
        f"Backup policy reference: {summary['backup_policy_reference']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase10_4_summary(), indent=2))
