"""
phase3e_customer_workbench_streamlit_panel.py

Streamlit-facing panel adapter for the Phase 3E customer payoff workbench.

This module is intentionally safe to import in two modes:

1. Normal Streamlit dashboard mode.
2. Bare Python checkpoint mode, where Streamlit may be unavailable or may not
   have an active ScriptRunContext.

The module exports stable names used by the Phase 3E dashboard/checkpoint layer:

    PHASE3E_PANEL_TITLE
    build_panel_render_model
    render_phase3e_customer_workbench_panel

Customer-view protection rule:
    This panel is Developer-view only until the Phase 3E completion checkpoint
    explicitly promotes the workflow to the customer dashboard.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


PHASE3E_PANEL_TITLE = "Phase 3E customer payoff workbench"
PHASE3E_PANEL_PROTECTION_NOTE = (
    "Developer-view only. Customer view remains protected until the Phase 3E "
    "completion checkpoint explicitly enables this workflow."
)


DEFAULT_SETUP: Dict[str, Any] = {
    "ticker": "SPY",
    "current_price": 545.25,
    "strike": 555.00,
    "premium": 4.20,
    "contracts": 1,
    "shares": 100,
    "expiration_label": "sample 30 DTE setup",
}


@dataclass
class PanelMetric:
    label: str
    value: str
    help_text: str


@dataclass
class PanelSection:
    title: str
    description: str
    items: List[str]


def _money(value: float) -> str:
    return f"${value:,.2f}"


def _percent(value: float) -> str:
    return f"{value:.2f}%"


def _normalize_setup(setup: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    merged = dict(DEFAULT_SETUP)
    if setup:
        merged.update(setup)
    return merged


def _compute_customer_metrics(setup: Dict[str, Any]) -> Dict[str, Any]:
    current_price = float(setup.get("current_price", DEFAULT_SETUP["current_price"]))
    strike = float(setup.get("strike", DEFAULT_SETUP["strike"]))
    premium = float(setup.get("premium", DEFAULT_SETUP["premium"]))
    shares = int(setup.get("shares", DEFAULT_SETUP["shares"]))
    contracts = int(setup.get("contracts", DEFAULT_SETUP["contracts"]))
    controlled_shares = max(shares, contracts * 100)

    breakeven = current_price - premium
    max_profit_per_share = max(strike - current_price + premium, premium)
    max_profit = max_profit_per_share * controlled_shares
    downside_cushion = premium / current_price if current_price else 0.0
    assignment_zone = "Above strike at expiration" if strike >= current_price else "Already near or in assignment zone"

    return {
        "current_price": current_price,
        "strike": strike,
        "premium": premium,
        "breakeven": breakeven,
        "max_profit": max_profit,
        "downside_cushion": downside_cushion,
        "assignment_zone": assignment_zone,
        "controlled_shares": controlled_shares,
    }


def _build_warning_items(metrics: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    current_price = float(metrics["current_price"])
    strike = float(metrics["strike"])
    premium = float(metrics["premium"])
    cushion = float(metrics["downside_cushion"])

    if strike <= current_price:
        warnings.append("Assignment risk is elevated because the strike is at or below the current price.")
    if cushion < 0.01:
        warnings.append("Downside cushion is small; a modest stock decline can exceed the premium received.")
    if premium <= 0:
        warnings.append("Premium must be positive before this setup can be treated as a real covered-call candidate.")
    if not warnings:
        warnings.append("No severe setup warning was detected, but covered calls still retain downside stock risk.")
    return warnings


def build_panel_render_model(setup: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build a dashboard-safe render model for the Phase 3E panel.

    The function first attempts to reuse the Phase 3E-6 workbench view-model
    builder if available. If the prior module changes or is unavailable, this
    function falls back to a local customer-facing render model so checkpoint
    scripts and the dashboard remain stable.
    """

    normalized_setup = _normalize_setup(setup)
    metrics = _compute_customer_metrics(normalized_setup)
    warnings = _build_warning_items(metrics)

    upstream_model: Optional[Dict[str, Any]] = None
    try:
        from app.paid_simulator.phase3e_customer_workbench_view_model import (  # type: ignore
            build_customer_workbench_view_model,
        )

        try:
            candidate = build_customer_workbench_view_model(normalized_setup)
        except TypeError:
            candidate = build_customer_workbench_view_model(setup=normalized_setup)
        if isinstance(candidate, dict):
            upstream_model = candidate
    except Exception:
        upstream_model = None

    metric_cards = [
        PanelMetric("Current price", _money(metrics["current_price"]), "Stock or ETF price used in the payoff estimate."),
        PanelMetric("Strike", _money(metrics["strike"]), "Covered-call strike price."),
        PanelMetric("Premium", _money(metrics["premium"]), "Option premium collected per share."),
        PanelMetric("Breakeven", _money(metrics["breakeven"]), "Approximate stock price where premium offsets the first loss."),
        PanelMetric("Max profit", _money(metrics["max_profit"]), "Approximate maximum gain if shares are called away at the strike."),
        PanelMetric("Downside cushion", _percent(metrics["downside_cushion"] * 100), "Premium cushion as a percentage of current price."),
        PanelMetric("Assignment zone", metrics["assignment_zone"], "Where assignment risk becomes relevant."),
    ]

    sections = [
        PanelSection(
            "Setup inputs",
            "Customer-facing inputs for the covered-call payoff estimate.",
            ["current price", "strike", "premium", "contracts", "expiration"],
        ),
        PanelSection(
            "Payoff summary",
            "Plain-language payoff labels for the customer workflow.",
            ["breakeven", "max profit", "downside cushion", "assignment zone"],
        ),
        PanelSection(
            "Scenario overlay",
            "One-click scenario refresh area for testing price changes.",
            ["base case", "lower price scenario", "higher price scenario", "overlay update"],
        ),
        PanelSection(
            "Save and reload workflow",
            "Staged actions for saving, reloading, refreshing, and exporting setups.",
            ["save setup", "reload saved setup", "refresh scenario overlay", "export setup"],
        ),
        PanelSection(
            "Warnings and risk notes",
            "Customer-readable warning/risk language for risky setups.",
            warnings,
        ),
    ]

    return {
        "title": PHASE3E_PANEL_TITLE,
        "protection_note": PHASE3E_PANEL_PROTECTION_NOTE,
        "setup": normalized_setup,
        "metrics": metrics,
        "metric_cards": [asdict(card) for card in metric_cards],
        "sections": [asdict(section) for section in sections],
        "warnings": warnings,
        "actions": [
            "Save setup",
            "Reload saved setup",
            "Refresh scenario overlay",
            "Export setup",
        ],
        "upstream_model_available": upstream_model is not None,
        "upstream_model": upstream_model,
        "customer_view_enabled": False,
        "developer_view_only": True,
    }


def render_phase3e_customer_workbench_panel(
    setup: Optional[Dict[str, Any]] = None,
    streamlit_module: Optional[Any] = None,
    st: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Render the Phase 3E panel when Streamlit is available.

    Parameters
    ----------
    setup:
        Optional covered-call setup dictionary.
    streamlit_module / st:
        Optional Streamlit-like object. Both names are supported because prior
        checkpoints used different argument names.

    Returns
    -------
    dict
        The same render model used to draw the panel. Returning the model makes
        this function testable in bare Python mode.
    """

    model = build_panel_render_model(setup=setup)
    ui = streamlit_module if streamlit_module is not None else st

    if ui is None:
        try:
            import streamlit as ui  # type: ignore
        except Exception:
            return model

    try:
        ui.subheader(model["title"])
        ui.caption(model["protection_note"])

        metric_cards = model.get("metric_cards", [])
        if hasattr(ui, "columns") and metric_cards:
            cols = ui.columns(min(4, len(metric_cards)))
            for index, card in enumerate(metric_cards):
                col = cols[index % len(cols)]
                if hasattr(col, "metric"):
                    col.metric(card["label"], card["value"], help=card.get("help_text"))
                else:
                    ui.write(f"{card['label']}: {card['value']}")
        else:
            for card in metric_cards:
                ui.write(f"{card['label']}: {card['value']}")

        for warning in model.get("warnings", []):
            if hasattr(ui, "warning"):
                ui.warning(warning)
            else:
                ui.write(f"Warning: {warning}")

        for section in model.get("sections", []):
            if hasattr(ui, "markdown"):
                ui.markdown(f"### {section['title']}")
                ui.write(section["description"])
                for item in section.get("items", []):
                    ui.write(f"- {item}")
            else:
                ui.write(section)
    except Exception:
        # Rendering should not break dashboard import/checks. The model is still
        # returned so diagnostics can proceed.
        return model

    return model


__all__ = [
    "PHASE3E_PANEL_TITLE",
    "PHASE3E_PANEL_PROTECTION_NOTE",
    "build_panel_render_model",
    "render_phase3e_customer_workbench_panel",
]
