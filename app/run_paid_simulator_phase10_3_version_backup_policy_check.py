"""
run_paid_simulator_phase10_3_version_backup_policy_check.py

Phase 10-3 version and backup policy check.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
import traceback
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase10_version_backup_policy.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase10_3_version_backup_policy.md"
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

POLICY_CSV = OUTPUT_TABLE_DIR / "phase10_3_version_backup_policy.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase10_3_version_backup_policy_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase10_3_version_backup_policy.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase10_3_version_backup_policy_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase10_3_version_backup_policy_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase10_3_version_backup_policy_checkpoint.json"

READY_MARKER = "PHASE10_3_VERSION_BACKUP_POLICY_READY"
RELEASE_DECISION = "PHASE10_3_VERSION_BACKUP_POLICY_CREATED_NO_DASHBOARD_OR_ENGINE_CHANGE"
SOURCE_MODE = "version_backup_policy"


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<76} {detail_text}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    if module_name in sys.modules:
        del sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 10-3 version and backup policy check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 10-3 version/backup policy module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 10-3 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 10-3 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase10_version_backup_policy")
        summary = module.build_phase10_3_summary()
        rec.add(isinstance(summary, dict), "Phase 10-3 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 10-3 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == READY_MARKER, "Version/backup policy has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == RELEASE_DECISION, "Version/backup policy has release decision", summary.get("release_decision"))
    rec.add(summary.get("source_mode") == SOURCE_MODE, "Version/backup policy uses expected source mode", summary.get("source_mode"))
    rec.add(summary.get("dashboard_change_required") is False, "No dashboard change required", summary.get("dashboard_change_required"))
    rec.add(summary.get("engine_change_required") is False, "No engine change required", summary.get("engine_change_required"))
    rec.add(summary.get("version_backup_policy_created") is True, "Version/backup policy created", summary.get("version_backup_policy_created"))
    rec.add(summary.get("semantic_versioning_policy_defined") is True, "Semantic versioning policy defined", summary.get("semantic_versioning_policy_defined"))
    rec.add(summary.get("google_drive_backup_policy_defined") is True, "Google Drive backup policy defined", summary.get("google_drive_backup_policy_defined"))
    rec.add(summary.get("secrets_exclusion_policy_defined") is True, "Secrets exclusion policy defined", summary.get("secrets_exclusion_policy_defined"))
    rec.add(summary.get("maintenance_version_rules_defined") is True, "Maintenance version rules defined", summary.get("maintenance_version_rules_defined"))
    rec.add(str(summary.get("recommended_release_version", "")).startswith("v1.0.0"), "Recommended release version present", summary.get("recommended_release_version"))
    rec.add("CoveredCallSimulator" in str(summary.get("recommended_backup_name", "")), "Recommended backup name present", summary.get("recommended_backup_name"))
    rec.add(isinstance(summary.get("policy_rows"), int) and summary.get("policy_rows", 0) >= 8, "Policy table has rows", summary.get("policy_rows"))
    rec.add(isinstance(summary.get("required_policy_items"), int) and summary.get("required_policy_items", 0) >= 7, "Required policy items present", summary.get("required_policy_items"))

    for label, path in [
        ("policy_csv", POLICY_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    policy_ok = False
    policy_detail = "missing"
    if POLICY_CSV.exists():
        try:
            df = pd.read_csv(POLICY_CSV)
            text = df.astype(str).to_string(index=False)
            policy_ok = len(df) >= 8 and "release_version" in text and "backup_zip_name" in text and "secrets_policy" in text
            policy_detail = f"rows={len(df)}"
        except Exception as exc:
            policy_detail = str(exc)
    rec.add(policy_ok, "Version/backup policy CSV has expected content", policy_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 10-3 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows]
            + ["", f"Overall Phase 10-3 checkpoint status: {final_status}"]
        )
        + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
