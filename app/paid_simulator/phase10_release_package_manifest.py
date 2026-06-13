"""
phase10_release_package_manifest.py

Phase 10-2 release package manifest.

This module is passive. It defines the files and categories that should be
included in the final release package for the Covered Call Simulator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

MANIFEST_CSV = OUTPUT_TABLE_DIR / "phase10_2_release_package_manifest.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_2_release_package_manifest_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_2_release_package_manifest.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_2_release_package_manifest_report.txt"

READY_MARKER = "PHASE10_2_RELEASE_PACKAGE_MANIFEST_READY"
RELEASE_DECISION = "PHASE10_2_RELEASE_PACKAGE_MANIFEST_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "release_package_manifest"


def _ensure_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def build_phase10_2_manifest() -> list[dict[str, Any]]:
    return [
        {
            "category": "Core app",
            "path_pattern": "app/*.py",
            "include_in_release": True,
            "reason": "Core simulator engine, runners, and project entry scripts.",
        },
        {
            "category": "Paid simulator modules",
            "path_pattern": "app/paid_simulator/*.py",
            "include_in_release": True,
            "reason": "Paid dashboard helpers, validation modules, and launch-readiness support.",
        },
        {
            "category": "Configuration",
            "path_pattern": "config/*.json",
            "include_in_release": True,
            "reason": "Default simulator configuration and customer-facing setup defaults.",
        },
        {
            "category": "Input samples",
            "path_pattern": "inputs/market_data/*.csv",
            "include_in_release": True,
            "reason": "Sample historical price and option-chain inputs for demos and smoke tests.",
        },
        {
            "category": "Documentation",
            "path_pattern": "docs/*.md",
            "include_in_release": True,
            "reason": "Phase documentation, handoffs, release notes, and maintenance guidance.",
        },
        {
            "category": "Customer outputs",
            "path_pattern": "outputs/reports/paid_simulator/*.txt",
            "include_in_release": False,
            "reason": "Generated reports should normally be recreated, not shipped as fixed release artifacts.",
        },
        {
            "category": "Generated tables",
            "path_pattern": "outputs/tables/paid_simulator/*.csv",
            "include_in_release": False,
            "reason": "Generated validation tables should normally be recreated during checks.",
        },
        {
            "category": "Local caches",
            "path_pattern": "__pycache__/; .pytest_cache/; .streamlit/secrets.toml",
            "include_in_release": False,
            "reason": "Local caches and secrets must not be included in customer release packages.",
        },
        {
            "category": "Release requirements",
            "path_pattern": "requirements.txt or deployment requirements file",
            "include_in_release": True,
            "reason": "Hosted deployment needs reproducible package dependencies.",
        },
        {
            "category": "Release notes",
            "path_pattern": "docs/release_notes.md or versioned release note file",
            "include_in_release": True,
            "reason": "Customer and maintenance history should be explicit.",
        },
    ]


def build_phase10_2_summary() -> dict[str, Any]:
    _ensure_dirs()

    manifest = build_phase10_2_manifest()
    manifest_df = pd.DataFrame(manifest)
    manifest_df.to_csv(MANIFEST_CSV, index=False)

    include_count = int(manifest_df["include_in_release"].sum())
    exclude_count = int((~manifest_df["include_in_release"]).sum())

    summary: dict[str, Any] = {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "engine_change_required": False,
        "release_package_manifest_created": True,
        "manifest_rows": int(len(manifest_df)),
        "include_count": include_count,
        "exclude_count": exclude_count,
        "local_caches_excluded": True,
        "secrets_excluded": True,
        "requirements_needed": True,
        "release_notes_needed": True,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "historical_data_is_scenario_input_not_forecast": True,
        "row_count": int(len(manifest_df)),
    }

    pd.DataFrame([{"field": k, "value": v} for k, v in summary.items()]).to_csv(SUMMARY_CSV, index=False)
    JSON_REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    report = [
        "Phase 10-2 release package manifest",
        "=" * 72,
        f"Ready marker: {READY_MARKER}",
        f"Release decision: {RELEASE_DECISION}",
        f"Source mode: {SOURCE_MODE}",
        f"Manifest rows: {summary['manifest_rows']}",
        f"Include count: {include_count}",
        f"Exclude count: {exclude_count}",
        f"Local caches excluded: {summary['local_caches_excluded']}",
        f"Secrets excluded: {summary['secrets_excluded']}",
        "Dashboard changed: False",
        "Engine changed: False",
    ]
    TEXT_REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    return summary


if __name__ == "__main__":
    print(json.dumps(build_phase10_2_summary(), indent=2))
