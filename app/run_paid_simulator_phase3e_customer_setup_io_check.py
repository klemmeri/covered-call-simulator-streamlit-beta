"""
run_paid_simulator_phase3e_customer_setup_io_check.py

Phase 3E-2 checkpoint for the Covered Call Simulator paid customer payoff workflow.

This script validates that the customer setup save/reload utilities work without
requiring the Streamlit dashboard. It writes deterministic checkpoint files to:

    outputs/saved_setups/paid_simulator/checkpoint

Expected final status:

    Overall Phase 3E-2 checkpoint status: PASS
"""

from __future__ import annotations

from pathlib import Path
import json
import sys
import traceback


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.phase3e_customer_setup_io import (  # noqa: E402
    CUSTOMER_SECTION_LABELS,
    CoveredCallSetup,
    build_customer_payload,
    build_demo_setup,
    build_warning_messages,
    calculate_payoff_metrics,
    export_setup_summary_text,
    list_saved_customer_setups,
    load_customer_setup,
    save_customer_setup,
    save_setup_summary_text,
    validate_setup,
)


CHECK_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "saved_setups" / "paid_simulator" / "checkpoint"
REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3e_customer_setup_io_checkpoint_report.txt"


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []

    def add(self, status: str, label: str, detail: str = "") -> None:
        self.rows.append((status, label, detail))
        print(f"{status:<10} {label:<65} {detail}")

    def pass_check(self, label: str, detail: str = "") -> None:
        self.add("PASS", label, detail)

    def fail_check(self, label: str, detail: str = "") -> None:
        self.add("FAIL", label, detail)

    @property
    def passed(self) -> bool:
        return all(status == "PASS" for status, _, _ in self.rows)

    def write_report(self) -> None:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "Phase 3E-2 customer setup save/reload checkpoint report",
            "========================================================",
            "",
        ]
        for status, label, detail in self.rows:
            lines.append(f"{status:<10} {label:<65} {detail}")
        lines.extend(
            [
                "",
                "Overall Phase 3E-2 checkpoint status: " + ("PASS" if self.passed else "FAIL"),
                "",
            ]
        )
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def check_equal(recorder: CheckRecorder, label: str, actual, expected) -> None:
    if actual == expected:
        recorder.pass_check(label, f"{actual}")
    else:
        recorder.fail_check(label, f"expected {expected!r}, got {actual!r}")


def main() -> int:
    print("=" * 96)
    print("Phase 3E-2 customer setup save/reload workflow check")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Checkpoint output: {CHECK_OUTPUT_DIR}")
    print()

    recorder = CheckRecorder()

    try:
        CHECK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        demo_setup = build_demo_setup()
        errors = validate_setup(demo_setup)
        if not errors:
            recorder.pass_check("Demo setup validation", "No validation errors")
        else:
            recorder.fail_check("Demo setup validation", "; ".join(errors))

        metrics = calculate_payoff_metrics(demo_setup)
        check_equal(recorder, "Breakeven calculation", metrics.breakeven_price, 541.05)
        check_equal(recorder, "Premium income calculation", metrics.premium_income_dollars, 420.00)
        check_equal(recorder, "Assignment-zone label calculation", metrics.assignment_zone_starts_at, 555.00)

        payload = build_customer_payload(demo_setup)
        required_payload_sections = ["version", "created_at", "section_labels", "setup", "payoff_metrics", "risk_warnings"]
        for section in required_payload_sections:
            if section in payload:
                recorder.pass_check(f"Payload section '{section}'", "Present")
            else:
                recorder.fail_check(f"Payload section '{section}'", "Missing")

        for key, expected_label in CUSTOMER_SECTION_LABELS.items():
            actual_label = payload["section_labels"].get(key)
            check_equal(recorder, f"Customer section label '{key}'", actual_label, expected_label)

        saved_json = save_customer_setup(
            demo_setup,
            output_dir=CHECK_OUTPUT_DIR,
            filename="phase3e_2_demo_customer_setup.json",
        )
        if saved_json.exists():
            recorder.pass_check("Saved setup JSON", str(saved_json.relative_to(PROJECT_ROOT)))
        else:
            recorder.fail_check("Saved setup JSON", "File was not created")

        loaded_payload = load_customer_setup(saved_json)
        check_equal(recorder, "Reloaded ticker", loaded_payload["setup"]["ticker"], "SPY")
        check_equal(recorder, "Reloaded strike", loaded_payload["setup"]["strike_price"], 555.00)
        check_equal(recorder, "Reloaded breakeven", loaded_payload["payoff_metrics"]["breakeven_price"], 541.05)

        listed_setups = list_saved_customer_setups(CHECK_OUTPUT_DIR)
        if saved_json in listed_setups:
            recorder.pass_check("Saved setup listing", f"Found {saved_json.name}")
        else:
            recorder.fail_check("Saved setup listing", "Saved JSON was not returned by list_saved_customer_setups")

        summary_text = export_setup_summary_text(loaded_payload)
        required_summary_markers = [
            "Covered Call Setup Summary",
            "Payoff Metrics",
            "Breakeven price",
            "Maximum profit",
            "Risk Warnings",
        ]
        for marker in required_summary_markers:
            if marker in summary_text:
                recorder.pass_check(f"Summary marker '{marker}'", "Present")
            else:
                recorder.fail_check(f"Summary marker '{marker}'", "Missing")

        saved_summary = save_setup_summary_text(
            loaded_payload,
            output_dir=CHECK_OUTPUT_DIR,
            filename="phase3e_2_demo_customer_summary.txt",
        )
        if saved_summary.exists():
            recorder.pass_check("Saved customer summary text", str(saved_summary.relative_to(PROJECT_ROOT)))
        else:
            recorder.fail_check("Saved customer summary text", "File was not created")

        risky_setup = CoveredCallSetup(
            setup_name="Risk warning demo",
            ticker="SPY",
            current_price=545.25,
            strike_price=544.00,
            option_premium=1.00,
            share_count=100,
        )
        warnings = build_warning_messages(risky_setup)
        if any("assignment zone" in warning.lower() for warning in warnings):
            recorder.pass_check("Risk warning for ITM/assignment-zone setup", "Triggered")
        else:
            recorder.fail_check("Risk warning for ITM/assignment-zone setup", json.dumps(warnings))

    except Exception as exc:  # pragma: no cover - checkpoint safety net
        recorder.fail_check("Unexpected checkpoint exception", repr(exc))
        traceback.print_exc()

    print()
    print("=" * 96)
    final_status = "PASS" if recorder.passed else "FAIL"
    print(f"Overall Phase 3E-2 checkpoint status: {final_status}")
    print("=" * 96)

    recorder.write_report()
    print()
    print(f"Saved checkpoint report: {REPORT_PATH}")

    return 0 if recorder.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
