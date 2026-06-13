"""
phase3g_public_customer_activation_plan.py

Phase 3G-2 public Customer-view activation plan for the Covered Call Simulator.

This module defines a release-plan model for eventually promoting the protected
Phase 3F customer-preview workflow into the ordinary Customer view. It does not
enable public customer access.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

PHASE3G_2_PUBLIC_CUSTOMER_ACTIVATION_PLAN_READY = "PHASE3G_2_PUBLIC_CUSTOMER_ACTIVATION_PLAN_READY"
PHASE3G_2_PUBLIC_CUSTOMER_ENABLED = False
PHASE3G_2_PROTECTED_PREVIEW_REQUIRED = True
PHASE3G_2_RELEASE_STAGE = "activation_plan_only"

CUSTOMER_FACING_LABELS = [
    "Current price",
    "Strike",
    "Premium",
    "Breakeven",
    "Max profit",
    "Downside cushion",
    "Assignment zone",
]

ACTIVATION_REQUIREMENTS = [
    "Phase 3E customer payoff workbench completion check has passed.",
    "Phase 3F protected customer-preview completion check has passed.",
    "Public Customer view remains disabled until an explicit release checkpoint.",
    "Customer-facing labels must remain plain-English and non-developer-facing.",
    "Risk and assignment warnings must be visible before any public release.",
    "Save, reload, refresh, and export language must be staged before release.",
]

RELEASE_GUARDRAILS = [
    "Do not expose developer/test tabs in the ordinary Customer view.",
    "Do not remove Phase 3D, Phase 3E, or Phase 3F markers during release planning.",
    "Do not promote the preview route without a dashboard backup.",
    "Do not treat payoff estimates as guarantees of future performance.",
    "Keep public release disabled until Phase 3G final release checkpoint passes.",
]

CUSTOMER_COPY_REQUIREMENTS = [
    "Explain the payoff diagram in terms of stock price, option premium, and strike.",
    "Explain breakeven as stock purchase price minus premium received.",
    "Explain max profit as premium plus stock appreciation up to the strike.",
    "Explain downside cushion as the premium buffer before losses begin.",
    "Warn that assignment can occur when the option is in the money.",
]


def build_phase3g_public_customer_activation_plan(project_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(project_root) if project_root else Path.cwd()
    return {
        "marker": PHASE3G_2_PUBLIC_CUSTOMER_ACTIVATION_PLAN_READY,
        "release_stage": PHASE3G_2_RELEASE_STAGE,
        "public_customer_enabled": PHASE3G_2_PUBLIC_CUSTOMER_ENABLED,
        "protected_preview_required": PHASE3G_2_PROTECTED_PREVIEW_REQUIRED,
        "project_root": str(root),
        "customer_facing_labels": list(CUSTOMER_FACING_LABELS),
        "activation_requirements": list(ACTIVATION_REQUIREMENTS),
        "release_guardrails": list(RELEASE_GUARDRAILS),
        "customer_copy_requirements": list(CUSTOMER_COPY_REQUIREMENTS),
        "decision": "DO NOT ENABLE PUBLIC CUSTOMER VIEW YET",
        "next_step": "Build a public Customer-view shell check before dashboard activation.",
    }


def render_phase3g_public_customer_activation_plan(streamlit_module=None, project_root: str | Path | None = None) -> dict[str, Any]:
    model = build_phase3g_public_customer_activation_plan(project_root=project_root)
    st = streamlit_module
    if st is None:
        return model

    st.subheader("Phase 3G-2 — Public Customer-view activation plan")
    st.warning("Public Customer view remains disabled. This is a release-planning checkpoint only.")
    st.write(f"Decision: {model['decision']}")
    st.write("Activation requirements")
    for item in model["activation_requirements"]:
        st.write(f"- {item}")
    st.write("Release guardrails")
    for item in model["release_guardrails"]:
        st.write(f"- {item}")
    return model
