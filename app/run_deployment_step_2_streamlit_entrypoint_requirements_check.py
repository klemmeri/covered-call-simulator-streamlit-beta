"""
Deployment Step 2 - Streamlit entry point and requirements readiness check.

This check is passive. It does not change the simulator engine or dashboard.
It verifies that the project has a deployable Streamlit entry point plan and a
hosting requirements file suitable for a Streamlit-compatible MVP deployment.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REQUIREMENTS_MVP = PROJECT_ROOT / "requirements_streamlit_mvp.txt"
REQUIREMENTS_HOSTING = PROJECT_ROOT / "requirements.txt"
STREAMLIT_CONFIG = PROJECT_ROOT / ".streamlit" / "config.toml"
DEPLOYMENT_DOC = PROJECT_ROOT / "docs" / "deployment_step_2_streamlit_entrypoint_requirements.md"

OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / "deployment_step_2_streamlit_entrypoint_requirements_report.txt"
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / "deployment_step_2_streamlit_entrypoint_requirements.json"
CHECKPOINT_CSV = OUTPUT_TABLE_DIR / "deployment_step_2_streamlit_entrypoint_requirements.csv"

REQUIRED_PACKAGES = ["streamlit", "pandas", "numpy", "matplotlib"]
REQUIRED_DASHBOARD_MARKERS = [
    "Synthetic scenarios",
    "Imported historical data",
    "Historical data is scenario input, not forecast",
]


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


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _requirements_contain(path: Path, packages: list[str]) -> tuple[bool, str]:
    text = _read_text(path).lower()
    missing = [package for package in packages if package.lower() not in text]
    return not missing, "missing=" + ",".join(missing) if missing else "all required packages present"


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 100)
    print("Deployment Step 2 - Streamlit entry point and requirements readiness check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    rec = Recorder()

    rec.add(DASHBOARD_FILE.exists(), "Dashboard file exists", DASHBOARD_FILE)
    rec.add(REQUIREMENTS_MVP.exists(), "MVP requirements file exists", REQUIREMENTS_MVP)
    rec.add(REQUIREMENTS_HOSTING.exists(), "Hosting requirements.txt exists", REQUIREMENTS_HOSTING)
    rec.add(STREAMLIT_CONFIG.exists(), "Streamlit config exists", STREAMLIT_CONFIG)
    rec.add(DEPLOYMENT_DOC.exists(), "Deployment Step 2 documentation exists", DEPLOYMENT_DOC)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, "Dashboard syntax remains valid", detail)

    dashboard_text = _read_text(DASHBOARD_FILE)
    for marker in REQUIRED_DASHBOARD_MARKERS:
        rec.add(marker in dashboard_text, f"Dashboard contains marker: {marker}", "present" if marker in dashboard_text else None)

    ok, detail = _requirements_contain(REQUIREMENTS_MVP, REQUIRED_PACKAGES)
    rec.add(ok, "MVP requirements include core packages", detail)

    ok, detail = _requirements_contain(REQUIREMENTS_HOSTING, REQUIRED_PACKAGES)
    rec.add(ok, "Hosting requirements.txt includes core packages", detail)

    config_text = _read_text(STREAMLIT_CONFIG)
    rec.add("[server]" in config_text, "Streamlit config has server section", "present" if "[server]" in config_text else None)
    rec.add("headless" in config_text.lower(), "Streamlit config has headless setting", "present" if "headless" in config_text.lower() else None)

    doc_text = _read_text(DEPLOYMENT_DOC)
    rec.add("streamlit run" in doc_text.lower(), "Deployment doc includes streamlit run command", "present" if "streamlit run" in doc_text.lower() else None)
    rec.add("app/paid_simulator/config_form_app.py" in doc_text or "app\\paid_simulator\\config_form_app.py" in doc_text, "Deployment doc identifies dashboard entry point", "present")
    rec.add("requirements.txt" in doc_text, "Deployment doc identifies requirements.txt", "present" if "requirements.txt" in doc_text else None)

    final_status = "PASS" if rec.passed else "FAIL"

    CHECKPOINT_REPORT.write_text(
        "\n".join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ["", f"Overall deployment Step 2 status: {final_status}"]) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_JSON.write_text(json.dumps({"overall_status": final_status, "checks": rec.rows}, indent=2), encoding="utf-8")
    CHECKPOINT_CSV.write_text(
        "status,label,detail\n" + "\n".join([f"{r['status']},{json.dumps(r['label'])},{json.dumps(r['detail'])}" for r in rec.rows]) + "\n",
        encoding="utf-8",
    )

    print()
    print("=" * 100)
    print(f"Overall deployment Step 2 status: {final_status}")
    print("=" * 100)
    print(f"Saved checkpoint report: {CHECKPOINT_REPORT}")
    print(f"Saved checkpoint JSON:   {CHECKPOINT_JSON}")

    return 0 if rec.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
