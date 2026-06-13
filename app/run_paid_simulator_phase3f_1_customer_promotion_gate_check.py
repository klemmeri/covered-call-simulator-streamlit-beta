"""
run_paid_simulator_phase3f_1_customer_promotion_gate_check.py

Checkpoint runner for Phase 3F-1.

Run from PyCharm using:

    app\run_paid_simulator_phase3f_1_customer_promotion_gate_check.py
"""

from __future__ import annotations

from pathlib import Path
import sys


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.phase3f_customer_promotion_gate import (  # noqa: E402
    PHASE3F_CUSTOMER_PROMOTION_READY_MARKER,
    build_phase3f_customer_promotion_gate,
    write_phase3f_customer_promotion_outputs,
)


def print_header(title: str) -> None:
    print("=" * 100)
    print(title)
    print("=" * 100)


def main() -> int:
    print_header("Phase 3F-1 customer promotion release-gate check")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Readiness marker: {PHASE3F_CUSTOMER_PROMOTION_READY_MARKER}")
    print()

    result = build_phase3f_customer_promotion_gate(PROJECT_ROOT)

    print("Checks")
    print("-" * 100)
    for check in result.checks:
        print(f"{check.status:<10} {check.name:<70} {check.detail}")

    outputs = write_phase3f_customer_promotion_outputs(result, PROJECT_ROOT)

    print()
    print("Recommendation")
    print("-" * 100)
    print(result.recommendation)
    print()
    print("Next action")
    print("-" * 100)
    print(result.next_action)
    print()
    print("Outputs")
    print("-" * 100)
    for label, path in outputs.items():
        print(f"{label:<10} {path}")

    print()
    print("=" * 100)
    print(f"Overall Phase 3F-1 checkpoint status: {'PASS' if result.passed else 'FAIL'}")
    print("=" * 100)

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
