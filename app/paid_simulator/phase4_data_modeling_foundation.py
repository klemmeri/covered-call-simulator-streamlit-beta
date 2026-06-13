"""
phase4_data_modeling_foundation.py

Phase 4-1 foundation model for the Covered Call Simulator.

Purpose
-------
Phase 4 begins the data/modeling upgrade stage after the Phase 3 customer
workflow activation work. This module does not change the dashboard. It creates
a conservative inventory of the modeling/data upgrade path so future work can
improve the simulator engine without disturbing the customer-facing interface.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


PHASE4_1_READY_MARKER = "PHASE4_1_DATA_MODELING_FOUNDATION_READY"
PHASE4_1_RELEASE_DECISION = "PHASE4_1_FOUNDATION_CREATED_NO_DASHBOARD_CHANGE"


@dataclass(frozen=True)
class Phase4UpgradeArea:
    name: str
    purpose: str
    customer_value: str
    risk_control: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Phase4FoundationModel:
    ready_marker: str
    release_decision: str
    dashboard_change: bool
    phase3_status: str
    upgrade_areas: list[Phase4UpgradeArea]
    immediate_next_steps: list[str]
    guardrails: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


def build_phase4_foundation_model() -> Phase4FoundationModel:
    """Build the Phase 4-1 data/modeling foundation model."""
    upgrade_areas = [
        Phase4UpgradeArea(
            name="Real ticker data ingestion",
            purpose="Define how real price histories will enter the simulator.",
            customer_value="Use realistic market movement rather than only synthetic examples.",
            risk_control="Keep imported data read-only until validation checks pass.",
        ),
        Phase4UpgradeArea(
            name="Option-chain input scaffold",
            purpose="Prepare a clean schema for strikes, expirations, bid, ask, mid, delta, and implied volatility.",
            customer_value="Let the simulator evaluate covered calls using actual option-chain-like inputs.",
            risk_control="Do not trade or recommend brokerage actions; keep this as simulation input only.",
        ),
        Phase4UpgradeArea(
            name="Volatility and premium model calibration",
            purpose="Compare modeled premiums against real option-chain premiums.",
            customer_value="Make estimated premium, breakeven, and max-profit outputs more credible.",
            risk_control="Report model error and uncertainty rather than presenting the model as exact.",
        ),
        Phase4UpgradeArea(
            name="Strategy-comparison metrics",
            purpose="Extend comparison reports beyond payoff diagrams into repeatable modeled outcomes.",
            customer_value="Help customers compare buy-and-hold, covered-call, and management-rule outcomes.",
            risk_control="Keep scenario assumptions visible and avoid overfitting claims.",
        ),
    ]

    return Phase4FoundationModel(
        ready_marker=PHASE4_1_READY_MARKER,
        release_decision=PHASE4_1_RELEASE_DECISION,
        dashboard_change=False,
        phase3_status="Phase 3 complete; customer-facing workflow activated and verified at local prototype level.",
        upgrade_areas=upgrade_areas,
        immediate_next_steps=[
            "Create a data-source inventory for price data and option-chain-style data.",
            "Define canonical CSV schemas for daily prices and option chains.",
            "Add validation checks for required columns and numeric ranges.",
            "Create a sample-data loader that does not depend on internet access.",
            "Keep dashboard changes out of Phase 4 until the data layer passes standalone checks.",
        ],
        guardrails=[
            "No dashboard code change in Phase 4-1.",
            "No live brokerage connection or automated trading behavior.",
            "No claim that regime detection or premium modeling is an oracle.",
            "Imported data must pass schema validation before being used by reports.",
            "Customer-facing outputs must continue to show warning and estimate language.",
        ],
    )


def render_phase4_foundation_model(streamlit_module: Any | None = None) -> dict[str, Any]:
    """Render or return the Phase 4 foundation model.

    When Streamlit is not supplied, this returns a plain dict for checkpoint
    scripts and automated tests.
    """
    model = build_phase4_foundation_model().to_dict()
    if streamlit_module is None:
        return model

    st = streamlit_module
    st.header("Phase 4 — Data/modeling foundation")
    st.caption("Foundation checkpoint only. No dashboard behavior is changed.")
    st.write(model["phase3_status"])
    st.subheader("Upgrade areas")
    for area in model["upgrade_areas"]:
        st.markdown(f"**{area['name']}**")
        st.write(area["purpose"])
    st.subheader("Guardrails")
    for item in model["guardrails"]:
        st.write(f"- {item}")
    return model
