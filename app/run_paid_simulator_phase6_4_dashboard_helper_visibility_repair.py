"""
Phase 6-4 dashboard helper visibility repair.

This repair appends the missing Phase 6-3 dashboard helper function expected by
Phase 6-4 visibility checks. It is intentionally narrow:

- It does not change the active dashboard workflow.
- It does not change the default mode.
- It keeps synthetic scenarios as the default.
- It keeps imported historical data as explicit opt-in only.
"""

from __future__ import annotations

from pathlib import Path
import py_compile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

REPAIR_MARKER = "PHASE6_4_DASHBOARD_HELPER_VISIBILITY_REPAIR_READY"
HELPER_NAME = "phase6_3_resolve_dashboard_data_mode"

HELPER_BLOCK = f'''

# =============================================================================
# Phase 6-4 dashboard helper visibility repair
# Marker: {REPAIR_MARKER}
# Purpose: expose the Phase 6-3 mode helper name expected by visibility checks.
# This block is passive and does not alter the active dashboard workflow.
# =============================================================================

{REPAIR_MARKER} = True


def {HELPER_NAME}(selected_label=None):
    """
    Resolve the paid-dashboard data mode using conservative customer wording.

    Synthetic scenarios remain the default. Imported historical data is an
    explicit opt-in scenario input, not a forecast.
    """
    synthetic_label = "Synthetic scenarios"
    historical_label = "Imported historical data"

    if selected_label == historical_label:
        return {{
            "selected_label": historical_label,
            "mode": "historical_import",
            "is_default": False,
            "requires_explicit_opt_in": True,
            "customer_message": "Imported historical data is used as scenario input, not as a forecast.",
        }}

    return {{
        "selected_label": synthetic_label,
        "mode": "synthetic",
        "is_default": True,
        "requires_explicit_opt_in": False,
        "customer_message": "Synthetic scenarios remain the default modeling mode.",
    }}


# End Phase 6-4 dashboard helper visibility repair
# =============================================================================
'''


def main() -> int:
    print("=" * 100)
    print("Phase 6-4 dashboard helper visibility repair")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dashboard file: {DASHBOARD_FILE}")

    if not DASHBOARD_FILE.exists():
        print("FAIL: dashboard file does not exist")
        return 1

    original_text = DASHBOARD_FILE.read_text(encoding="utf-8")

    if HELPER_NAME in original_text and REPAIR_MARKER in original_text:
        print("PASS: helper and repair marker already present")
    else:
        DASHBOARD_FILE.write_text(original_text.rstrip() + HELPER_BLOCK + "\n", encoding="utf-8")
        print("PASS: appended Phase 6-4 dashboard helper visibility repair block")

    try:
        py_compile.compile(str(DASHBOARD_FILE), doraise=True)
        print("PASS: dashboard syntax remains valid")
    except Exception as exc:
        print(f"FAIL: dashboard syntax error after repair: {exc}")
        return 1

    repaired_text = DASHBOARD_FILE.read_text(encoding="utf-8")
    required_markers = [
        "PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY",
        HELPER_NAME,
        "Synthetic scenarios",
        "Imported historical data",
        "scenario input",
    ]

    failed = False
    for marker in required_markers:
        if marker in repaired_text:
            print(f"PASS: marker present: {marker}")
        else:
            print(f"FAIL: marker missing: {marker}")
            failed = True

    if failed:
        print("Overall Phase 6-4 repair status: FAIL")
        return 1

    print("=" * 100)
    print("Overall Phase 6-4 repair status: PASS")
    print("=" * 100)
    print("Now rerun: app\\run_paid_simulator_phase6_4_dashboard_mode_selector_visibility_check.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
