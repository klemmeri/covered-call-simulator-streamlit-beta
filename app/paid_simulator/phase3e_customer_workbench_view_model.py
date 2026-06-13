"""
phase3e_customer_workbench_view_model.py

Phase 3E-6 customer payoff workbench view model for the Covered Call Simulator.

This module prepares the Phase 3E customer payoff workbench for later Streamlit
customer-dashboard integration without changing the dashboard yet.

It converts the calculation result from phase3e_customer_payoff_workbench.py into
simple dashboard-ready sections:

1. Header summary
2. Customer input panel fields
3. Metric cards
4. Risk warning boxes
5. Scenario overlay table rows
6. Save/export/reload action labels
7. Readiness checklist for eventual dashboard placement

The module intentionally avoids importing Streamlit. That keeps the checkpoint
safe to run from PyCharm and protects the customer dashboard from unfinished
integration work.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import csv
import json

from app.paid_simulator.phase3e_customer_payoff_workbench import (
    CustomerPayoffWorkbenchInput,
    CustomerPayoffWorkbenchResult,
    build_customer_payoff_workbench,
    update_customer_payoff_workbench,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"


@dataclass(frozen=True)
class CustomerInputFieldSpec:
    """One customer-facing input field for the future dashboard form."""

    key: str
    label: str
    help_text: str
    default_value: str
    field_type: str


@dataclass(frozen=True)
class CustomerActionSpec:
    """One customer-facing workflow action for future dashboard buttons."""

    key: str
    label: str
    help_text: str
    action_type: str


@dataclass(frozen=True)
class CustomerWorkbenchSection:
    """One dashboard-ready customer section."""

    key: str
    title: str
    purpose: str
    items: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class CustomerWorkbenchViewModel:
    """Dashboard-ready view model for the customer payoff workflow."""

    title: str
    subtitle: str
    ticker: str
    setup_name: str
    sections: tuple[CustomerWorkbenchSection, ...]
    readiness_checks: tuple[str, ...]


def build_customer_input_fields(setup: CustomerPayoffWorkbenchInput) -> tuple[CustomerInputFieldSpec, ...]:
    """Return a stable list of customer-facing input fields."""

    return (
        CustomerInputFieldSpec(
            key="ticker",
            label="Ticker",
            help_text="Underlying stock or ETF symbol for the covered call.",
            default_value=setup.ticker.upper().strip(),
            field_type="text",
        ),
        CustomerInputFieldSpec(
            key="current_price",
            label="Current price",
            help_text="Current market price of the stock or ETF.",
            default_value=f"{setup.current_price:.2f}",
            field_type="number",
        ),
        CustomerInputFieldSpec(
            key="stock_cost_basis",
            label="Stock cost basis",
            help_text="Your average stock cost before option premium is applied.",
            default_value=f"{setup.stock_cost_basis:.2f}",
            field_type="number",
        ),
        CustomerInputFieldSpec(
            key="strike_price",
            label="Call strike",
            help_text="The price where assignment risk begins and upside becomes capped.",
            default_value=f"{setup.strike_price:.2f}",
            field_type="number",
        ),
        CustomerInputFieldSpec(
            key="premium",
            label="Call premium",
            help_text="Option premium received per share.",
            default_value=f"{setup.premium:.2f}",
            field_type="number",
        ),
        CustomerInputFieldSpec(
            key="shares",
            label="Shares covered",
            help_text="Number of shares covered by the short call position.",
            default_value=str(setup.shares),
            field_type="integer",
        ),
        CustomerInputFieldSpec(
            key="expiration_date",
            label="Expiration date",
            help_text="Optional expiration date for customer records and saved setups.",
            default_value=setup.expiration_date,
            field_type="date_or_text",
        ),
    )


def build_customer_actions() -> tuple[CustomerActionSpec, ...]:
    """Return customer workflow actions for future dashboard buttons."""

    return (
        CustomerActionSpec(
            key="update_overlay",
            label="Update payoff scenarios",
            help_text="Refresh the payoff table after changing price, strike, premium, or scenarios.",
            action_type="primary_button",
        ),
        CustomerActionSpec(
            key="save_setup",
            label="Save setup",
            help_text="Save the current covered-call setup for later review.",
            action_type="secondary_button",
        ),
        CustomerActionSpec(
            key="reload_setup",
            label="Reload saved setup",
            help_text="Reload a previously saved covered-call setup.",
            action_type="secondary_button",
        ),
        CustomerActionSpec(
            key="export_scenarios",
            label="Export scenario table",
            help_text="Export the payoff scenario table as a CSV file.",
            action_type="secondary_button",
        ),
    )


def _field_specs_to_items(fields: tuple[CustomerInputFieldSpec, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "key": field.key,
            "label": field.label,
            "help_text": field.help_text,
            "default_value": field.default_value,
            "field_type": field.field_type,
        }
        for field in fields
    )


def _metric_cards_to_items(result: CustomerPayoffWorkbenchResult) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "label": card.label,
            "value": card.value,
            "explanation": card.explanation,
        }
        for card in result.metric_cards
    )


def _warnings_to_items(result: CustomerPayoffWorkbenchResult) -> tuple[dict[str, Any], ...]:
    if not result.warnings:
        return (
            {
                "level": "info",
                "title": "No major setup warnings",
                "message": "The setup passed the current customer-facing warning checks.",
            },
        )

    return tuple(
        {
            "level": warning.level,
            "title": warning.title,
            "message": warning.message,
        }
        for warning in result.warnings
    )


def _scenario_rows_to_items(result: CustomerPayoffWorkbenchResult) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "scenario_price": row.scenario_price,
            "stock_only_profit": row.stock_only_profit,
            "covered_call_profit": row.covered_call_profit,
            "option_effect": row.option_effect,
            "assignment_zone": row.assignment_zone,
            "customer_zone": row.customer_zone,
            "explanation": row.explanation,
        }
        for row in result.scenario_rows
    )


def _actions_to_items(actions: tuple[CustomerActionSpec, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "key": action.key,
            "label": action.label,
            "help_text": action.help_text,
            "action_type": action.action_type,
        }
        for action in actions
    )


def build_customer_workbench_view_model(
    setup: CustomerPayoffWorkbenchInput,
) -> CustomerWorkbenchViewModel:
    """Build the full dashboard-ready customer view model."""

    result = build_customer_payoff_workbench(setup)
    fields = build_customer_input_fields(setup)
    actions = build_customer_actions()

    sections = (
        CustomerWorkbenchSection(
            key="input_panel",
            title="Covered-call setup",
            purpose="Customer enters the basic covered-call inputs.",
            items=_field_specs_to_items(fields),
        ),
        CustomerWorkbenchSection(
            key="metric_cards",
            title="Payoff summary",
            purpose="Customer sees the key payoff numbers in plain language.",
            items=_metric_cards_to_items(result),
        ),
        CustomerWorkbenchSection(
            key="risk_warnings",
            title="Risk warnings",
            purpose="Customer sees setup-specific warnings before relying on the scenario table.",
            items=_warnings_to_items(result),
        ),
        CustomerWorkbenchSection(
            key="scenario_overlay",
            title="Scenario overlay",
            purpose="Customer compares stock-only and covered-call outcomes across selected prices.",
            items=_scenario_rows_to_items(result),
        ),
        CustomerWorkbenchSection(
            key="workflow_actions",
            title="Workflow actions",
            purpose="Customer can update, save, reload, and export the payoff workflow.",
            items=_actions_to_items(actions),
        ),
    )

    readiness_checks = (
        "Uses customer-facing labels only",
        "Contains no developer-only controls",
        "Supports update, save, reload, and export action labels",
        "Can be rendered by Streamlit later without recalculating business logic in the UI",
        "Keeps dashboard integration separate until the standalone checkpoint passes",
    )

    return CustomerWorkbenchViewModel(
        title="Covered Call Payoff Workbench",
        subtitle="Estimate income, breakeven, assignment zone, and scenario outcomes before placing a covered call.",
        ticker=result.ticker,
        setup_name=result.setup_name,
        sections=sections,
        readiness_checks=readiness_checks,
    )


def update_customer_workbench_view_model(
    setup: CustomerPayoffWorkbenchInput,
    **changes: Any,
) -> CustomerWorkbenchViewModel:
    """Update setup values and rebuild the customer view model."""

    updated_result = update_customer_payoff_workbench(setup, **changes)
    updated_setup = CustomerPayoffWorkbenchInput(
        ticker=updated_result.ticker,
        current_price=updated_result.current_price,
        stock_cost_basis=updated_result.stock_cost_basis,
        strike_price=updated_result.strike_price,
        premium=updated_result.premium,
        shares=updated_result.shares,
        expiration_date=updated_result.expiration_date,
        setup_name=updated_result.setup_name,
        scenario_prices=tuple(row.scenario_price for row in updated_result.scenario_rows),
    )
    return build_customer_workbench_view_model(updated_setup)


def view_model_to_dict(view_model: CustomerWorkbenchViewModel) -> dict[str, Any]:
    """Convert a view model to a JSON-serializable dictionary."""

    return {
        "title": view_model.title,
        "subtitle": view_model.subtitle,
        "ticker": view_model.ticker,
        "setup_name": view_model.setup_name,
        "sections": [
            {
                "key": section.key,
                "title": section.title,
                "purpose": section.purpose,
                "items": list(section.items),
            }
            for section in view_model.sections
        ],
        "readiness_checks": list(view_model.readiness_checks),
    }


def export_view_model_json(
    view_model: CustomerWorkbenchViewModel,
    path: Path | None = None,
) -> Path:
    """Export the customer view model to JSON for checkpoint review."""

    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = path or OUTPUT_REPORT_DIR / "phase3e_customer_workbench_view_model.json"
    output_path.write_text(json.dumps(view_model_to_dict(view_model), indent=2), encoding="utf-8")
    return output_path


def export_view_model_sections_csv(
    view_model: CustomerWorkbenchViewModel,
    path: Path | None = None,
) -> Path:
    """Export a compact section inventory CSV for checkpoint review."""

    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = path or OUTPUT_TABLE_DIR / "phase3e_customer_workbench_view_model_sections.csv"

    rows = []
    for section in view_model.sections:
        rows.append(
            {
                "section_key": section.key,
                "section_title": section.title,
                "purpose": section.purpose,
                "item_count": len(section.items),
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(
            file_obj,
            fieldnames=("section_key", "section_title", "purpose", "item_count"),
        )
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def build_dashboard_integration_notes(view_model: CustomerWorkbenchViewModel) -> str:
    """Build plain-text notes for the next dashboard integration step."""

    lines: list[str] = []
    lines.append("Phase 3E-6 Customer Workbench View Model")
    lines.append("=" * 54)
    lines.append("")
    lines.append(f"Title: {view_model.title}")
    lines.append(f"Ticker: {view_model.ticker}")
    lines.append(f"Setup: {view_model.setup_name}")
    lines.append("")
    lines.append("Dashboard-ready sections")
    lines.append("-" * 54)
    for section in view_model.sections:
        lines.append(f"- {section.title} ({section.key}): {len(section.items)} items")
        lines.append(f"  Purpose: {section.purpose}")
    lines.append("")
    lines.append("Readiness checks")
    lines.append("-" * 54)
    for check in view_model.readiness_checks:
        lines.append(f"- {check}")
    lines.append("")
    lines.append("Next recommended step")
    lines.append("-" * 54)
    lines.append(
        "Add a Developer-view dashboard tab that imports this view model and renders it with Streamlit, "
        "while keeping the customer view protected until the tab passes."
    )
    return "\n".join(lines) + "\n"


def write_dashboard_integration_notes(
    view_model: CustomerWorkbenchViewModel,
    path: Path | None = None,
) -> Path:
    """Write integration notes for checkpoint review."""

    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = path or OUTPUT_REPORT_DIR / "phase3e_customer_workbench_view_model_integration_notes.txt"
    output_path.write_text(build_dashboard_integration_notes(view_model), encoding="utf-8")
    return output_path


def run_phase3e_customer_workbench_view_model_checkpoint() -> dict[str, str]:
    """Run the Phase 3E-6 standalone checkpoint and save review outputs."""

    setup = CustomerPayoffWorkbenchInput(
        ticker="SPY",
        current_price=545.25,
        stock_cost_basis=542.00,
        strike_price=555.00,
        premium=4.50,
        shares=100,
        expiration_date="2026-07-17",
        setup_name="Phase 3E-6 customer view-model checkpoint",
        scenario_prices=(515.0, 530.0, 545.25, 555.0, 570.0, 590.0),
    )

    view_model = build_customer_workbench_view_model(setup)
    json_path = export_view_model_json(view_model)
    csv_path = export_view_model_sections_csv(view_model)
    notes_path = write_dashboard_integration_notes(view_model)

    return {
        "json_path": str(json_path),
        "csv_path": str(csv_path),
        "notes_path": str(notes_path),
    }
