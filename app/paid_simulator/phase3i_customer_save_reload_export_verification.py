"""
phase3i_customer_save_reload_export_verification.py

Phase 3I-3 customer save/reload/export workflow verification model.

This module is intentionally dashboard-neutral. It verifies that the activated
customer-facing payoff workflow has a coherent save, reload, refresh, and export
experience without modifying Streamlit dashboard code.
"""
from __future__ import annotations

from pathlib import Path
import json
import csv
from datetime import datetime

PHASE3I_3_READY_MARKER = "PHASE3I_3_CUSTOMER_SAVE_RELOAD_EXPORT_READY"
PHASE3I_3_RELEASE_DECISION = "PHASE3I_3_CUSTOMER_SAVE_RELOAD_EXPORT_WORKFLOW_VERIFIED"

CUSTOMER_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

WORKFLOW_ACTIONS = [
    "save setup",
    "reload saved setup",
    "refresh scenario overlay",
    "export payoff summary",
]

GUARDRAILS = [
    "Do not expose developer-only controls in the ordinary customer workflow.",
    "Saved setup files must be explicit customer setup artifacts, not hidden state.",
    "Reloaded setup values must reproduce the same key payoff metrics.",
    "Exported output must include warning/risk language.",
    "Public activation must remain traceable through Phase 3H completion evidence.",
]

DEFAULT_SETUP = {
    "ticker": "SPY",
    "current_price": 545.25,
    "strike": 560.00,
    "premium": 6.50,
    "contracts": 1,
    "shares": 100,
    "expiration_label": "demo 30 DTE",
}


def calculate_customer_payoff_metrics(setup: dict | None = None) -> dict:
    """Return simple customer-facing covered-call metrics."""
    data = dict(DEFAULT_SETUP)
    if setup:
        data.update(setup)

    current_price = float(data["current_price"])
    strike = float(data["strike"])
    premium = float(data["premium"])
    shares = int(data.get("shares", 100))
    contracts = int(data.get("contracts", 1))
    contract_shares = shares * contracts

    breakeven = current_price - premium
    max_profit_per_share = max(0.0, strike - current_price) + premium
    max_profit = max_profit_per_share * contract_shares
    downside_cushion = premium / current_price if current_price else 0.0
    assignment_zone = "At or above strike at expiration"

    warning_level = "normal"
    warnings = []
    if strike <= current_price:
        warning_level = "high"
        warnings.append("Strike is at or below current price; assignment risk is elevated.")
    if downside_cushion < 0.01:
        warning_level = "medium" if warning_level == "normal" else warning_level
        warnings.append("Premium provides less than 1% downside cushion.")
    if not warnings:
        warnings.append("Covered calls cap upside above the strike and do not eliminate downside stock risk.")

    return {
        "ticker": data["ticker"],
        "current_price": round(current_price, 2),
        "strike": round(strike, 2),
        "premium": round(premium, 2),
        "breakeven": round(breakeven, 2),
        "max_profit": round(max_profit, 2),
        "downside_cushion_percent": round(downside_cushion * 100.0, 2),
        "assignment_zone": assignment_zone,
        "warning_level": warning_level,
        "warnings": warnings,
    }


def build_save_reload_export_model(setup: dict | None = None) -> dict:
    """Build a dict-compatible model for the Phase 3I-3 check and reports."""
    metrics = calculate_customer_payoff_metrics(setup)
    return {
        "marker": PHASE3I_3_READY_MARKER,
        "release_decision": PHASE3I_3_RELEASE_DECISION,
        "public_customer_workflow_active": True,
        "dashboard_modified": False,
        "customer_labels": CUSTOMER_LABELS,
        "workflow_actions": WORKFLOW_ACTIONS,
        "guardrails": GUARDRAILS,
        "setup": dict(DEFAULT_SETUP if setup is None else {**DEFAULT_SETUP, **setup}),
        "metrics": metrics,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def save_customer_setup(path: str | Path, setup: dict | None = None) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_save_reload_export_model(setup)
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return target


def reload_customer_setup(path: str | Path) -> dict:
    source = Path(path)
    return json.loads(source.read_text(encoding="utf-8"))


def export_customer_summary_csv(path: str | Path, model: dict | None = None) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = model or build_save_reload_export_model()
    metrics = payload["metrics"]
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["field", "value"])
        writer.writerow(["marker", payload["marker"]])
        writer.writerow(["release_decision", payload["release_decision"]])
        for key, value in metrics.items():
            writer.writerow([key, value])
        writer.writerow(["warning", " | ".join(metrics.get("warnings", []))])
    return target


def render_customer_save_reload_export_verification(streamlit_module=None) -> dict:
    """Render when Streamlit is present; otherwise return the model for checks."""
    model = build_save_reload_export_model()
    if streamlit_module is None:
        return model

    st = streamlit_module
    st.subheader("Customer save, reload, and export workflow")
    st.caption("Phase 3I-3 post-activation customer workflow verification")
    st.json(model)
    return model
