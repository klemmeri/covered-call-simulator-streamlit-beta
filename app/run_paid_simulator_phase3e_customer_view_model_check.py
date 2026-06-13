"""
run_paid_simulator_phase3e_customer_view_model_check.py

Phase 3E-6 checkpoint runner for the customer payoff workbench view model.
Run this file from PyCharm after installing the Phase 3E-6 package.
"""

from __future__ import annotations

from pathlib import Path
import csv
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.phase3e_customer_workbench_view_model import (  # noqa: E402
    CustomerInputFieldSpec,
    CustomerWorkbenchViewModel,
    build_customer_actions,
    build_customer_input_fields,
    build_customer_workbench_view_model,
    run_phase3e_customer_workbench_view_model_checkpoint,
    update_customer_workbench_view_model,
    view_model_to_dict,
)
from app.paid_simulator.phase3e_customer_payoff_workbench import (  # noqa: E402
    CustomerPayoffWorkbenchInput,
)


def print_result(status: str, item: str, detail: str = "") -> None:
    print(f"{status:<10} {item:<70} {detail}")


def require(condition: bool, item: str, detail: str = "") -> bool:
    if condition:
        print_result("PASS", item, detail)
        return True
    print_result("FAIL", item, detail)
    return False


def section_by_key(view_model: CustomerWorkbenchViewModel, key: str):
    for section in view_model.sections:
        if section.key == key:
            return section
    return None


def main() -> int:
    print("=" * 100)
    print("Phase 3E-6 customer payoff workbench view-model checkpoint")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    checks: list[bool] = []

    setup = CustomerPayoffWorkbenchInput(
        ticker="SPY",
        current_price=545.25,
        stock_cost_basis=542.00,
        strike_price=555.00,
        premium=4.50,
        shares=100,
        expiration_date="2026-07-17",
        setup_name="Phase 3E-6 checkpoint setup",
        scenario_prices=(515.0, 530.0, 545.25, 555.0, 570.0, 590.0),
    )

    fields = build_customer_input_fields(setup)
    checks.append(require(len(fields) >= 7, "Customer input field specs created", str(len(fields))))
    checks.append(require(all(isinstance(field, CustomerInputFieldSpec) for field in fields), "Input field specs use dataclass structure"))
    checks.append(require(any(field.label == "Current price" for field in fields), "Current price input label present"))
    checks.append(require(any(field.label == "Call strike" for field in fields), "Call strike input label present"))
    checks.append(require(any(field.label == "Call premium" for field in fields), "Call premium input label present"))

    actions = build_customer_actions()
    action_keys = {action.key for action in actions}
    checks.append(require("update_overlay" in action_keys, "One-click scenario update action present"))
    checks.append(require("save_setup" in action_keys, "Save setup action present"))
    checks.append(require("reload_setup" in action_keys, "Reload setup action present"))
    checks.append(require("export_scenarios" in action_keys, "Export scenario action present"))

    view_model = build_customer_workbench_view_model(setup)
    checks.append(require(view_model.title == "Covered Call Payoff Workbench", "Workbench title is customer-ready", view_model.title))
    checks.append(require(view_model.ticker == "SPY", "Ticker is propagated to view model", view_model.ticker))
    checks.append(require(len(view_model.sections) == 5, "Five dashboard-ready sections created", str(len(view_model.sections))))

    expected_sections = {
        "input_panel",
        "metric_cards",
        "risk_warnings",
        "scenario_overlay",
        "workflow_actions",
    }
    section_keys = {section.key for section in view_model.sections}
    checks.append(require(expected_sections.issubset(section_keys), "Expected customer sections present", str(sorted(section_keys))))

    input_panel = section_by_key(view_model, "input_panel")
    metric_cards = section_by_key(view_model, "metric_cards")
    warnings = section_by_key(view_model, "risk_warnings")
    scenarios = section_by_key(view_model, "scenario_overlay")
    workflow_actions = section_by_key(view_model, "workflow_actions")

    checks.append(require(input_panel is not None and len(input_panel.items) >= 7, "Input panel has customer fields"))
    checks.append(require(metric_cards is not None and len(metric_cards.items) >= 7, "Metric-card section has payoff labels"))
    checks.append(require(warnings is not None and len(warnings.items) >= 1, "Risk-warning section has at least one item"))
    checks.append(require(scenarios is not None and len(scenarios.items) == 6, "Scenario-overlay section has supplied scenarios"))
    checks.append(require(workflow_actions is not None and len(workflow_actions.items) == 4, "Workflow action section has four actions"))

    if metric_cards is not None:
        labels = {item["label"] for item in metric_cards.items}
        checks.append(require("Breakeven price" in labels, "Breakeven metric card present"))
        checks.append(require("Distance to assignment zone" in labels or "Assignment zone" in labels, "Assignment-zone metric card present"))

    if scenarios is not None:
        sample = scenarios.items[0]
        checks.append(require("covered_call_profit" in sample, "Scenario rows include covered-call profit"))
        checks.append(require("stock_only_profit" in sample, "Scenario rows include stock-only profit"))
        checks.append(require("assignment_zone" in sample, "Scenario rows include assignment-zone marker"))

    checks.append(require(any("no developer" in item.lower() for item in view_model.readiness_checks), "Readiness checks protect customer view"))
    checks.append(require(any("Streamlit" in item for item in view_model.readiness_checks), "Readiness checks prepare Streamlit integration"))

    updated_view = update_customer_workbench_view_model(setup, current_price=552.50)
    checks.append(require(updated_view.ticker == "SPY", "Updated view model preserves ticker", updated_view.ticker))
    updated_input_panel = section_by_key(updated_view, "input_panel")
    current_price_field = None
    if updated_input_panel is not None:
        for item in updated_input_panel.items:
            if item["key"] == "current_price":
                current_price_field = item
                break
    checks.append(require(current_price_field is not None and current_price_field["default_value"] == "552.50", "Updated view model reflects changed current price"))

    view_dict = view_model_to_dict(view_model)
    checks.append(require("sections" in view_dict, "View model converts to dictionary"))
    checks.append(require(len(view_dict["sections"]) == 5, "Dictionary contains five sections"))

    outputs = run_phase3e_customer_workbench_view_model_checkpoint()
    json_path = Path(outputs["json_path"])
    csv_path = Path(outputs["csv_path"])
    notes_path = Path(outputs["notes_path"])

    checks.append(require(json_path.exists(), "View-model JSON exported", str(json_path)))
    checks.append(require(csv_path.exists(), "View-model section CSV exported", str(csv_path)))
    checks.append(require(notes_path.exists(), "Dashboard integration notes written", str(notes_path)))

    json_payload = json.loads(json_path.read_text(encoding="utf-8"))
    checks.append(require(json_payload["title"] == "Covered Call Payoff Workbench", "Exported JSON title verified"))
    checks.append(require(len(json_payload["sections"]) == 5, "Exported JSON section count verified"))

    with csv_path.open("r", newline="", encoding="utf-8") as file_obj:
        rows = list(csv.DictReader(file_obj))
    checks.append(require(len(rows) == 5, "Exported section CSV contains five rows", str(len(rows))))
    checks.append(require(any(row["section_key"] == "scenario_overlay" for row in rows), "Exported section CSV includes scenario overlay"))

    notes_text = notes_path.read_text(encoding="utf-8")
    checks.append(require("Developer-view dashboard tab" in notes_text, "Integration notes identify next dashboard step"))

    print()
    print("=" * 100)
    if all(checks):
        print("Overall Phase 3E-6 checkpoint status: PASS")
        print("=" * 100)
        print(f"View-model JSON: {outputs['json_path']}")
        print(f"Section CSV:     {outputs['csv_path']}")
        print(f"Notes report:    {outputs['notes_path']}")
        return 0

    print("Overall Phase 3E-6 checkpoint status: FAIL")
    print("=" * 100)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
