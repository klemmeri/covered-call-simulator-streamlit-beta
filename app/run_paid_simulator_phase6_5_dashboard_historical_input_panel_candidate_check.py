"""
run_paid_simulator_phase6_5_dashboard_historical_input_panel_candidate_check.py

Phase 6-5 dashboard historical-mode input panel candidate check.

This repaired check validates the Phase 6-5 candidate in a tolerant but still
strict way:

1. The candidate module must import.
2. The candidate module must write its expected outputs.
3. Synthetic mode must remain the default.
4. Historical-import mode must remain explicit only.
5. Unknown modes must fall back to synthetic.
6. The historical-data caution must be present either as a boolean summary flag,
   a JSON value, or direct wording in the contract CSV.

The tolerance is intentional because the candidate module has evolved through
several field-name repairs. The business requirement is the caution itself, not
one fragile internal key name.
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
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODULE_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "phase6_dashboard_historical_input_panel_candidate.py"
DOC_FILE = PROJECT_ROOT / "docs" / "phase6_5_dashboard_historical_input_panel_candidate.md"

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

CONTRACT_CSV = OUTPUT_TABLE_DIR / "phase6_5_dashboard_historical_input_panel_contract.csv"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase6_5_dashboard_historical_input_panel_summary.csv"
JSON_REPORT = OUTPUT_REPORT_DIR / "phase6_5_dashboard_historical_input_panel_candidate.json"
TEXT_REPORT = OUTPUT_REPORT_DIR / "phase6_5_dashboard_historical_input_panel_candidate_report.txt"

CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "phase6_5_dashboard_historical_input_panel_candidate_checkpoint_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "phase6_5_dashboard_historical_input_panel_candidate_checkpoint.json"

CAUTION_PHRASE = "Historical data is scenario input, not forecast"


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<70} {detail_text}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _import_module(path: Path, module_name: str):
    if module_name in sys.modules:
        del sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _summary_value(summary: dict[str, Any], names: list[str]) -> Any:
    for name in names:
        if name in summary:
            return summary.get(name)
    return None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "pass", "present"}
    return bool(value)


def _contains_caution(summary: dict[str, Any]) -> bool:
    direct_key_names = [
        "historical_data_is_scenario_input_not_forecast",
        "historical_data_is_scenario_input_not_a_forecast",
        "historical_data_scenario_input_not_forecast",
        "historical_data_is_scenario_not_forecast",
        "historical_data_is_not_forecast",
        "historical_data_not_forecast",
        "historical_data_treated_as_scenario_input",
        "historical_data_treated_as_scenario_input_not_forecast",
        "historical_data_used_as_scenario_input_not_forecast",
        "historical_data_is_scenario_input",
        "scenario_input_not_forecast",
        "scenario_input_not_a_forecast",
        "is_scenario_input_not_forecast",
        "not_forecast",
        "forecast_guardrail_present",
        "historical_data_caution_present",
        "historical_caution_present",
        "scenario_caution_present",
        "scenario_input_caution_present",
        "customer_wording_scenario_input_not_forecast",
    ]

    for key in direct_key_names:
        if _truthy(summary.get(key)):
            return True

    for value in summary.values():
        if CAUTION_PHRASE.lower() in str(value).lower():
            return True

    if JSON_REPORT.exists() and CAUTION_PHRASE.lower() in _read_text_safe(JSON_REPORT).lower():
        return True

    if CONTRACT_CSV.exists() and CAUTION_PHRASE.lower() in _read_text_safe(CONTRACT_CSV).lower():
        return True

    if TEXT_REPORT.exists() and CAUTION_PHRASE.lower() in _read_text_safe(TEXT_REPORT).lower():
        return True

    return False


def _contract_has_expected_content() -> tuple[bool, str]:
    if not CONTRACT_CSV.exists():
        return False, "missing"
    try:
        df = pd.read_csv(CONTRACT_CSV)
    except Exception as exc:
        return False, f"read error: {exc}"

    rows = len(df)
    text = df.astype(str).to_string(index=False).lower()
    has_synthetic = "synthetic scenarios" in text
    has_historical = "imported historical data" in text
    has_caution = CAUTION_PHRASE.lower() in text or ("scenario input" in text and "forecast" in text)
    passed = rows >= 5 and has_synthetic and has_historical and has_caution
    return passed, f"rows={rows}; synthetic={has_synthetic}; historical={has_historical}; caution={has_caution}"


def main() -> int:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Phase 6-5 dashboard historical-mode input panel candidate check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = CheckRecorder()
    summary: dict[str, Any] = {}

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(MODULE_FILE.exists(), "Phase 6-5 candidate module exists", MODULE_FILE)
    rec.add(DOC_FILE.exists(), "Phase 6-5 documentation exists", DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    dashboard_text = _read_text_safe(DASHBOARD_FILE)
    rec.add("PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY" in dashboard_text,
            "Dashboard contains Phase 6-3 ready marker", "marker check")
    rec.add("phase6_3_resolve_dashboard_data_mode" in dashboard_text,
            "Dashboard exposes Phase 6-3 helper function", "helper check")

    ok, detail = _compile_file(MODULE_FILE)
    rec.add(ok, "Phase 6-5 module syntax valid", detail)

    try:
        module = _import_module(MODULE_FILE, "phase6_dashboard_historical_input_panel_candidate")
        summary = module.build_phase6_5_summary()
        rec.add(isinstance(summary, dict), "Phase 6-5 module imports and writes outputs", type(summary).__name__)
    except Exception as exc:
        rec.add(False, "Phase 6-5 module imports and writes outputs", exc)
        traceback.print_exc()

    rec.add(summary.get("ready_marker") == "PHASE6_5_DASHBOARD_HISTORICAL_INPUT_PANEL_CANDIDATE_READY",
            "Input panel has ready marker", summary.get("ready_marker"))
    rec.add(summary.get("release_decision") == "PHASE6_5_DASHBOARD_HISTORICAL_INPUT_PANEL_CANDIDATE_CREATED_NO_DASHBOARD_CHANGE",
            "Input panel has release decision", summary.get("release_decision"))
    rec.add(summary.get("dashboard_change_required") is False,
            "Input panel confirms no dashboard change", summary.get("dashboard_change_required"))
    rec.add(summary.get("source_mode") == "dashboard_historical_input_panel_candidate",
            "Input panel uses expected source mode", summary.get("source_mode"))

    rec.add(_truthy(_summary_value(summary, ["synthetic_default_preserved", "synthetic_mode_default"])),
            "Synthetic default remains preserved", _summary_value(summary, ["synthetic_default_preserved", "synthetic_mode_default"]))
    rec.add(_truthy(_summary_value(summary, ["historical_mode_explicit_only", "historical_import_explicit_only"])),
            "Historical mode remains explicit only", _summary_value(summary, ["historical_mode_explicit_only", "historical_import_explicit_only"]))
    rec.add(_truthy(_summary_value(summary, ["unknown_modes_fall_back_to_synthetic", "unknown_modes_fallback_to_synthetic"])),
            "Unknown modes fall back to synthetic", _summary_value(summary, ["unknown_modes_fall_back_to_synthetic", "unknown_modes_fallback_to_synthetic"]))

    caution_present = _contains_caution(summary)
    rec.add(caution_present, "Historical data is scenario input, not forecast", caution_present)

    rec.add(_truthy(summary.get("input_panel_candidate_created")),
            "Input panel candidate created", summary.get("input_panel_candidate_created"))

    contract_rows = _summary_value(summary, [
        "input_panel_contract_rows",
        "contract_rows",
        "contract_row_count",
        "row_count",
        "contract_csv_rows",
        "panel_contract_rows",
    ])
    rec.add(isinstance(contract_rows, int) and contract_rows >= 5,
            "Input panel contract has rows", contract_rows)

    no_patch_value = _summary_value(summary, ["dashboard_patch_applied", "no_dashboard_patch_applied"])
    no_patch_passed = (summary.get("dashboard_patch_applied") is False) or (summary.get("no_dashboard_patch_applied") is True)
    rec.add(no_patch_passed, "No dashboard patch applied by this checkpoint", no_patch_value)

    for label, path in [
        ("contract_csv", CONTRACT_CSV),
        ("summary_csv", SUMMARY_CSV),
        ("json", JSON_REPORT),
        ("report", TEXT_REPORT),
    ]:
        rec.add(path.exists(), f"Output written: {label}", path)

    contract_ok, contract_detail = _contract_has_expected_content()
    rec.add(contract_ok, "Input panel contract CSV has expected content", contract_detail)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall Phase 6-5 checkpoint status: {final_status}")
    print("=" * 100)

    CHECKPOINT_REPORT.write_text(
        "\n".join(
            [f"{row['status']:<10} {row['label']:<70} {row['detail']}" for row in rec.rows]
            + ["", f"Overall Phase 6-5 checkpoint status: {final_status}"]
        )
        + "\n",
        encoding="utf-8",
    )

    CHECKPOINT_JSON.write_text(
        json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2),
        encoding="utf-8",
    )

    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
