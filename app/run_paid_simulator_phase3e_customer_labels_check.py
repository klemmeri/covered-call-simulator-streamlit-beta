"""
run_paid_simulator_phase3e_customer_labels_check.py

Phase 3E-3 checkpoint for customer-facing payoff labels and warnings.
"""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase3e_customer_labels_checkpoint_report.txt"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


from paid_simulator.phase3e_customer_payoff_labels import (  # noqa: E402
    CoveredCallSetup,
    build_customer_payoff_view_model,
    build_risk_warnings,
    compute_customer_metrics,
    demo_setup,
)


def check(condition: bool, label: str, details: str = "") -> tuple[bool, str]:
    status = "PASS" if condition else "FAIL"
    line = f"{status:<10} {label}"
    if details:
        line += f"    {details}"
    return condition, line


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("=" * 96)
    lines.append("Phase 3E-3 customer payoff labels checkpoint")
    lines.append("=" * 96)

    setup = demo_setup()
    metrics = compute_customer_metrics(setup)
    view_model = build_customer_payoff_view_model(setup)
    labels = view_model["labels"]
    warnings = view_model["warnings"]

    checks: list[tuple[bool, str]] = []
    checks.append(check(setup.ticker == "SPY", "Demo setup ticker available", setup.ticker))
    checks.append(check(round(metrics["breakeven"], 2) == 540.45, "Breakeven calculation", f"{metrics['breakeven']:.2f}"))
    checks.append(check(round(metrics["max_profit"], 2) == 1455.00, "Maximum profit calculation", f"{metrics['max_profit']:.2f}"))
    checks.append(check("Current stock price" in labels["current_price_label"], "Customer label: current price"))
    checks.append(check("Covered-call strike" in labels["strike_label"], "Customer label: strike"))
    checks.append(check("Option premium collected" in labels["premium_label"], "Customer label: premium"))
    checks.append(check("Breakeven" in labels["breakeven_label"], "Customer label: breakeven"))
    checks.append(check("Maximum profit" in labels["max_profit_label"], "Customer label: max profit"))
    checks.append(check("Downside cushion" in labels["downside_cushion_label"], "Customer label: downside cushion"))
    checks.append(check("Assignment" in labels["assignment_zone_label"], "Customer label: assignment zone"))
    checks.append(check(len(warnings) >= 1, "Warning block list exists", f"count={len(warnings)}"))

    itm_setup = CoveredCallSetup("SPY", 545.25, 535.00, 12.00)
    itm_warnings = build_risk_warnings(itm_setup)
    checks.append(check(any(w["level"] == "high" for w in [item.to_dict() for item in itm_warnings]), "High warning for ITM covered call"))

    tiny_premium_setup = CoveredCallSetup("SPY", 545.25, 555.00, 0.25)
    tiny_warnings = build_risk_warnings(tiny_premium_setup)
    checks.append(check(any("Small downside cushion" == item.title for item in tiny_warnings), "Medium warning for tiny premium"))

    for passed, line in checks:
        lines.append(line)

    all_passed = all(passed for passed, _ in checks)
    lines.append("")
    lines.append("=" * 96)
    lines.append(f"Overall Phase 3E-3 checkpoint status: {'PASS' if all_passed else 'FAIL'}")
    lines.append("=" * 96)
    lines.append("")
    lines.append(f"Saved checkpoint report: {REPORT_PATH}")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
