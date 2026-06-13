"""
phase3g_public_customer_completion_gate.py

Phase 3G-8 completion gate for the Covered Call Simulator paid dashboard.

This module records that Phase 3G public-customer release preparation has
completed at the checkpoint level while intentionally keeping the public
Customer-view activation disabled.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


PHASE3G_8_PUBLIC_CUSTOMER_COMPLETION_READY = "PHASE3G_8_PUBLIC_CUSTOMER_COMPLETION_READY"
PHASE3G_8_PUBLIC_CUSTOMER_ENABLED = False
PHASE3G_8_RELEASE_DECISION = "PHASE_3G_COMPLETE_PUBLIC_CUSTOMER_VIEW_STILL_DISABLED"


class Phase3GCompletionGateModel:
    """Small explicit model used by the Phase 3G-8 completion check."""

    def __init__(self) -> None:
        self.marker = PHASE3G_8_PUBLIC_CUSTOMER_COMPLETION_READY
        self.public_customer_enabled = PHASE3G_8_PUBLIC_CUSTOMER_ENABLED
        self.release_decision = PHASE3G_8_RELEASE_DECISION
        self.title = "Phase 3G public customer-view completion gate"
        self.status = "Phase 3G preparation complete; public activation remains disabled."
        self.required_prior_phases = [
            "Phase 3D integrated overlay",
            "Phase 3E customer payoff workflow",
            "Phase 3F protected customer-preview layer",
            "Phase 3G public-release preparation",
        ]
        self.guardrails = [
            "Do not enable the public Customer view until an explicit release package changes the activation flag.",
            "Keep Developer-view and protected-preview controls separate from ordinary Customer view.",
            "Preserve Phase 3D, Phase 3E, and Phase 3F dashboard markers during any future release patch.",
            "Require browser verification before public release.",
            "Keep rollback backups for every dashboard-modifying package.",
        ]
        self.customer_facing_requirements = [
            "current price",
            "strike",
            "premium",
            "breakeven",
            "max profit",
            "downside cushion",
            "assignment zone",
            "warning/risk language",
            "save/reload/refresh/export workflow language",
        ]
        self.next_recommended_step = "Phase 3H-1 explicit public activation package, only if you decide to expose the workflow."

    def to_dict(self) -> dict[str, Any]:
        return {
            "marker": self.marker,
            "public_customer_enabled": self.public_customer_enabled,
            "release_decision": self.release_decision,
            "title": self.title,
            "status": self.status,
            "required_prior_phases": list(self.required_prior_phases),
            "guardrails": list(self.guardrails),
            "customer_facing_requirements": list(self.customer_facing_requirements),
            "next_recommended_step": self.next_recommended_step,
        }


def build_phase3g_completion_gate_model() -> Phase3GCompletionGateModel:
    return Phase3GCompletionGateModel()


def render_phase3g_completion_gate(streamlit_module: Any | None = None) -> dict[str, Any]:
    """Render with Streamlit when supplied; otherwise return a plain dictionary."""
    model = build_phase3g_completion_gate_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader(data["title"])
    st.info(data["status"])
    st.write("Release decision:", data["release_decision"])
    st.write("Public Customer view enabled:", data["public_customer_enabled"])

    st.markdown("#### Guardrails")
    for item in data["guardrails"]:
        st.write(f"- {item}")

    st.markdown("#### Customer-facing requirements")
    for item in data["customer_facing_requirements"]:
        st.write(f"- {item}")

    return data


def expected_prior_report_paths(project_root: Path) -> list[Path]:
    return [
        project_root / "outputs" / "reports" / "paid_simulator" / "phase3e_9_completion_checkpoint_report.txt",
        project_root / "outputs" / "reports" / "paid_simulator" / "phase3f_8_completion_gate_checkpoint_report.txt",
        project_root / "outputs" / "reports" / "paid_simulator" / "phase3g_1_public_release_gate_checkpoint_report.txt",
        project_root / "outputs" / "reports" / "paid_simulator" / "phase3g_5_public_route_smoke_test_checkpoint_report.txt",
        project_root / "outputs" / "reports" / "paid_simulator" / "phase3g_6_final_pre_activation_checkpoint_report.txt",
        project_root / "outputs" / "reports" / "paid_simulator" / "phase3g_7_activation_dry_run_checkpoint_report.txt",
    ]
