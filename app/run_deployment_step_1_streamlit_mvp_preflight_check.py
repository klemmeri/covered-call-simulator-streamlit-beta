"""
run_deployment_step_1_streamlit_mvp_preflight_check.py

Post-Phase-10 deployment Step 1 preflight check.

This script does not modify dashboard or engine code. It verifies that the local
Covered Call Simulator project has the expected files for a Streamlit-style MVP
deployment and writes a small deployment-preflight report.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import platform
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
PRICE_PATHS_FILE = PROJECT_ROOT / "app" / "price_paths.py"
SIMULATOR_FILE = PROJECT_ROOT / "app" / "simulator.py"
STRATEGY_FILE = PROJECT_ROOT / "app" / "strategy.py"
PORTFOLIO_FILE = PROJECT_ROOT / "app" / "portfolio.py"
CONFIG_FILE = PROJECT_ROOT / "app" / "config.py"

REQUIREMENTS_MVP = PROJECT_ROOT / "requirements_streamlit_mvp.txt"
STREAMLIT_CONFIG = PROJECT_ROOT / ".streamlit" / "config.toml"
DOC_FILE = PROJECT_ROOT / "docs" / "deployment_step_1_streamlit_mvp_preflight.md"

OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

REPORT_TXT = OUTPUT_REPORT_DIR / "deployment_step_1_streamlit_mvp_preflight_report.txt"
REPORT_JSON = OUTPUT_REPORT_DIR / "deployment_step_1_streamlit_mvp_preflight_report.json"
SUMMARY_CSV = OUTPUT_TABLE_DIR / "deployment_step_1_streamlit_mvp_preflight_summary.csv"

REQUIRED_PACKAGES = ["pandas", "numpy", "matplotlib", "streamlit"]


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = "") -> None:
        status = "PASS" if passed else "FAIL"
        detail_text = "" if detail is None else str(detail)
        self.rows.append({"status": status, "label": label, "detail": detail_text})
        print(f"{status:<10} {label:<72} {detail_text}")

    @property
    def passed(self) -> bool:
        return all(row["status"] == "PASS" for row in self.rows)


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def _package_available(name: str) -> tuple[bool, str]:
    try:
        spec = importlib.util.find_spec(name)
        if spec is None:
            return False, "not installed or not visible to this interpreter"
        return True, "available"
    except Exception as exc:
        return False, str(exc)


def _write_reports(rec: Recorder, final_status: str) -> None:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    REPORT_TXT.write_text(
        "\n".join(
            [f"{row['status']:<10} {row['label']:<72} {row['detail']}" for row in rec.rows]
            + ["", f"Overall deployment Step 1 status: {final_status}"]
        )
        + "\n",
        encoding="utf-8",
    )

    REPORT_JSON.write_text(
        json.dumps(
            {
                "overall_status": final_status,
                "python_version": sys.version,
                "platform": platform.platform(),
                "checks": rec.rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    SUMMARY_CSV.write_text(
        "status,label,detail\n"
        + "\n".join(
            f"{row['status']},{json.dumps(row['label'])},{json.dumps(row['detail'])}"
            for row in rec.rows
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    print("=" * 100)
    print("Deployment Step 1 - Streamlit MVP preflight check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print()

    rec = Recorder()

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(REQUIREMENTS_MVP.exists(), "MVP requirements file exists", REQUIREMENTS_MVP)
    rec.add(STREAMLIT_CONFIG.exists(), "Streamlit config file exists", STREAMLIT_CONFIG)
    rec.add(DOC_FILE.exists(), "Deployment Step 1 documentation exists", DOC_FILE)

    for label, path in [
        ("price_paths.py", PRICE_PATHS_FILE),
        ("simulator.py", SIMULATOR_FILE),
        ("strategy.py", STRATEGY_FILE),
        ("portfolio.py", PORTFOLIO_FILE),
        ("config.py", CONFIG_FILE),
    ]:
        rec.add(path.exists(), f"Core file exists: {label}", path)

    if DASHBOARD_FILE.exists():
        ok, detail = _compile_file(DASHBOARD_FILE)
        rec.add(ok, "Dashboard syntax remains valid", detail)
        dashboard_text = DASHBOARD_FILE.read_text(encoding="utf-8")
        rec.add("Synthetic scenarios" in dashboard_text, "Synthetic scenario label present", "present" if "Synthetic scenarios" in dashboard_text else None)
        rec.add("Imported historical data" in dashboard_text, "Historical opt-in label present", "present" if "Imported historical data" in dashboard_text else None)
        rec.add("Historical data is scenario input, not forecast" in dashboard_text, "Historical-data caution present", "present" if "Historical data is scenario input, not forecast" in dashboard_text else None)

    for package in REQUIRED_PACKAGES:
        ok, detail = _package_available(package)
        rec.add(ok, f"Python package available: {package}", detail)

    if REQUIREMENTS_MVP.exists():
        req_text = REQUIREMENTS_MVP.read_text(encoding="utf-8").lower()
        for package in REQUIRED_PACKAGES:
            rec.add(package in req_text, f"Requirements file includes {package}", "listed" if package in req_text else None)

    print()
    print("=" * 100)
    final_status = "PASS" if rec.passed else "FAIL"
    print(f"Overall deployment Step 1 status: {final_status}")
    print("=" * 100)

    _write_reports(rec, final_status)
    print(f"Saved report: {REPORT_TXT}")
    print(f"Saved JSON:   {REPORT_JSON}")
    print(f"Saved CSV:    {SUMMARY_CSV}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
