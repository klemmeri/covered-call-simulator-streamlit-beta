"""
run_paid_simulator_phase3e_7b_panel_check.py

Phase 3E-7B checkpoint:
Validate the customer payoff workbench Streamlit panel before modifying the main
dashboard file. This check uses a fake Streamlit object so it can be run safely
from PyCharm without launching a browser.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

for path in (PROJECT_ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


class FakeStreamlit:
    """Tiny Streamlit stand-in used to validate render behavior."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def _record(self, method: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append({"method": method, "args": [str(arg) for arg in args], "kwargs": {key: str(value) for key, value in kwargs.items()}})

    def subheader(self, *args: Any, **kwargs: Any) -> None:
        self._record("subheader", *args, **kwargs)

    def warning(self, *args: Any, **kwargs: Any) -> None:
        self._record("warning", *args, **kwargs)

    def caption(self, *args: Any, **kwargs: Any) -> None:
        self._record("caption", *args, **kwargs)

    def markdown(self, *args: Any, **kwargs: Any) -> None:
        self._record("markdown", *args, **kwargs)

    def metric(self, *args: Any, **kwargs: Any) -> None:
        self._record("metric", *args, **kwargs)

    def error(self, *args: Any, **kwargs: Any) -> None:
        self._record("error", *args, **kwargs)

    def success(self, *args: Any, **kwargs: Any) -> None:
        self._record("success", *args, **kwargs)

    def info(self, *args: Any, **kwargs: Any) -> None:
        self._record("info", *args, **kwargs)

    def dataframe(self, *args: Any, **kwargs: Any) -> None:
        self._record("dataframe", *args, **kwargs)

    def button(self, *args: Any, **kwargs: Any) -> bool:
        self._record("button", *args, **kwargs)
        return False


def status_line(ok: bool, label: str, detail: str = "") -> str:
    status = "PASS" if ok else "FAIL"
    return f"{status:<10} {label:<72} {detail}"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    checks: list[bool] = []

    lines.append("=" * 100)
    lines.append("Phase 3E-7B customer workbench Streamlit panel check")
    lines.append("=" * 100)
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    expected_files = [
        APP_DIR / "paid_simulator" / "phase3e_customer_workbench_streamlit_panel.py",
        APP_DIR / "run_paid_simulator_phase3e_7b_panel_check.py",
        PROJECT_ROOT / "docs" / "phase3e_7b_customer_workbench_panel.md",
    ]

    lines.append("Expected files")
    lines.append("-" * 100)
    for file_path in expected_files:
        ok = file_path.exists()
        checks.append(ok)
        lines.append(status_line(ok, file_path.name, str(file_path)))
    lines.append("")

    try:
        from app.paid_simulator.phase3e_customer_workbench_streamlit_panel import (
            DEVELOPER_ONLY_NOTICE,
            PANEL_TITLE,
            build_phase3e_panel_summary,
            get_phase3e_developer_tab_snippet,
            render_phase3e_customer_workbench_panel,
        )

        import_ok = True
        import_detail = "module imported"
    except Exception as exc:
        import_ok = False
        import_detail = repr(exc)

    checks.append(import_ok)
    lines.append("Import check")
    lines.append("-" * 100)
    lines.append(status_line(import_ok, "Panel module import", import_detail))
    lines.append("")

    summary_dict: dict[str, Any] = {}
    fake_calls: list[dict[str, Any]] = []
    snippet = ""

    if import_ok:
        try:
            summary = build_phase3e_panel_summary()
            fake_st = FakeStreamlit()
            render_summary = render_phase3e_customer_workbench_panel(fake_st)
            snippet = get_phase3e_developer_tab_snippet()
            summary_dict = render_summary.as_dict()
            fake_calls = fake_st.calls

            rendered_text = "\n".join(
                " ".join(call.get("args", [])) + " " + " ".join(call.get("kwargs", {}).values())
                for call in fake_calls
            )

            behavior_checks = [
                (summary.title == PANEL_TITLE, "Summary title matches panel title", summary.title),
                (summary.developer_only is True, "Panel remains Developer-view only", str(summary.developer_only)),
                ("Customer view" in DEVELOPER_ONLY_NOTICE, "Protection notice explicitly names Customer view", DEVELOPER_ONLY_NOTICE),
                (render_summary.metric_count >= 4, "At least four metric cards available", str(render_summary.metric_count)),
                (render_summary.warning_count >= 1, "At least one warning/info box available", str(render_summary.warning_count)),
                (render_summary.scenario_row_count >= 3, "Scenario overlay rows available", str(render_summary.scenario_row_count)),
                (render_summary.action_count >= 3, "Save/reload/refresh actions available", str(render_summary.action_count)),
                (len(fake_calls) >= 8, "Fake Streamlit render produced UI calls", str(len(fake_calls))),
                ("Phase 3E customer payoff workbench" in rendered_text, "Rendered text contains Phase 3E title", "title marker"),
                ("render_phase3e_customer_workbench_panel" in snippet, "Developer-tab snippet references panel renderer", "snippet marker"),
                ("Developer view only" in snippet or "Developer-view" in snippet, "Snippet is Developer-view scoped", "developer scoped"),
            ]
        except Exception as exc:
            behavior_checks = [(False, "Build/render panel", repr(exc))]

        lines.append("Panel behavior")
        lines.append("-" * 100)
        for ok, label, detail in behavior_checks:
            checks.append(ok)
            lines.append(status_line(ok, label, detail))
        lines.append("")

    # Boundary check: this package should not expose Phase 3E in Customer view by editing the dashboard.
    config_file = APP_DIR / "paid_simulator" / "config_form_app.py"
    lines.append("Dashboard boundary check")
    lines.append("-" * 100)
    config_exists = config_file.exists()
    checks.append(config_exists)
    lines.append(status_line(config_exists, "Existing dashboard file found", str(config_file)))
    if config_exists:
        text = config_file.read_text(encoding="utf-8", errors="replace")
        customer_view_present = "Customer" in text or "customer" in text.lower()
        phase3d_present = "Phase 3D" in text or "phase3d" in text.lower()
        not_customer_exposed = "render_phase3e_customer_workbench_panel" not in text
        checks.extend([customer_view_present, phase3d_present, not_customer_exposed])
        lines.append(status_line(customer_view_present, "Customer-view markers still detectable", "marker search"))
        lines.append(status_line(phase3d_present, "Phase 3D markers still detectable", "marker search"))
        lines.append(status_line(not_customer_exposed, "Panel not blindly injected into dashboard", "safe boundary"))
    lines.append("")

    if summary_dict:
        summary_path = REPORT_DIR / "phase3e_7b_panel_summary.json"
        summary_path.write_text(json.dumps(summary_dict, indent=2), encoding="utf-8")
        checks.append(summary_path.exists())
        lines.append(status_line(summary_path.exists(), "Panel summary JSON written", str(summary_path)))

        calls_path = REPORT_DIR / "phase3e_7b_fake_streamlit_calls.json"
        calls_path.write_text(json.dumps(fake_calls, indent=2), encoding="utf-8")
        checks.append(calls_path.exists())
        lines.append(status_line(calls_path.exists(), "Fake Streamlit call log written", str(calls_path)))

        snippet_path = REPORT_DIR / "phase3e_7b_developer_tab_snippet.txt"
        snippet_path.write_text(snippet + "\n", encoding="utf-8")
        checks.append(snippet_path.exists())
        lines.append(status_line(snippet_path.exists(), "Developer-tab snippet written", str(snippet_path)))

    lines.append("")
    lines.append("=" * 100)
    all_ok = all(checks)
    final_status = "PASS" if all_ok else "FAIL"
    lines.append(f"Overall Phase 3E-7B checkpoint status: {final_status}")
    lines.append("=" * 100)

    report_path = REPORT_DIR / "phase3e_7b_panel_checkpoint_report.txt"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nSaved checkpoint report: {report_path}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
