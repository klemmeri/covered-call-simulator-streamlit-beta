"""
phase3f_customer_preview_activation_plan.py

Phase 3F-7: Controlled Customer-Preview Activation Plan.

This module does not enable public customer access. It defines the release
criteria for moving from protected preview to a controlled customer-preview
state and builds a plain Python model that the checkpoint script can inspect.
"""

from __future__ import annotations

from pathlib import Path

PHASE3F_7_CUSTOMER_PREVIEW_ACTIVATION_READY = "PHASE3F_7_CUSTOMER_PREVIEW_ACTIVATION_READY"
PHASE3F_7_PUBLIC_CUSTOMER_RELEASE_ENABLED = False
PHASE3F_7_PROTECTED_PREVIEW_ALLOWED = True


class Phase3FActivationPlan:
    """Small serializable model for the Phase 3F-7 activation decision."""

    def __init__(self, project_root: Path | str | None = None):
        self.project_root = Path(project_root) if project_root is not None else Path.cwd()
        self.marker = PHASE3F_7_CUSTOMER_PREVIEW_ACTIVATION_READY
        self.public_customer_release_enabled = PHASE3F_7_PUBLIC_CUSTOMER_RELEASE_ENABLED
        self.protected_preview_allowed = PHASE3F_7_PROTECTED_PREVIEW_ALLOWED
        self.decision = "READY_FOR_CONTROLLED_PREVIEW_REVIEW"
        self.status = "not_publicly_released"
        self.required_prior_checkpoints = [
            "Phase 3E-9 completion guardrail PASS",
            "Phase 3F-1 customer promotion gate PASS",
            "Phase 3F-2 protected customer preview shell PASS",
            "Phase 3F-3 guarded customer preview route PASS",
            "Phase 3F-4 preview visual verification PASS",
            "Phase 3F-5 customer preview access gate PASS",
            "Phase 3F-6 customer-preview release-readiness PASS",
        ]
        self.activation_guardrails = [
            "Do not enable ordinary Customer view automatically.",
            "Keep public customer release flag set to False.",
            "Require manual browser verification before any public release.",
            "Retain Developer-view diagnostics until customer-preview behavior is stable.",
            "Maintain timestamped backups before any dashboard patch.",
        ]
        self.customer_preview_requirements = [
            "Customer-facing payoff labels are visible.",
            "Warning and risk language is visible.",
            "Save/reload/refresh/export workflow language is visible or staged.",
            "Scenario overlay can be refreshed without developer-only terminology.",
            "Customer view remains clean unless explicitly promoted later.",
        ]
        self.next_recommended_step = "Phase 3F-8 guarded customer-preview switch installer"

    def to_dict(self) -> dict:
        return {
            "marker": self.marker,
            "public_customer_release_enabled": self.public_customer_release_enabled,
            "protected_preview_allowed": self.protected_preview_allowed,
            "decision": self.decision,
            "status": self.status,
            "required_prior_checkpoints": list(self.required_prior_checkpoints),
            "activation_guardrails": list(self.activation_guardrails),
            "customer_preview_requirements": list(self.customer_preview_requirements),
            "next_recommended_step": self.next_recommended_step,
        }


def build_phase3f_7_activation_plan(project_root: Path | str | None = None) -> Phase3FActivationPlan:
    """Build the Phase 3F-7 activation plan model."""
    return Phase3FActivationPlan(project_root=project_root)


def render_phase3f_7_activation_plan(streamlit_module=None, project_root: Path | str | None = None):
    """Render, or return a dict when Streamlit is absent.

    The fallback dict is intentional so bare-mode checkpoint scripts can inspect
    the model without a browser session.
    """
    model = build_phase3f_7_activation_plan(project_root=project_root)
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader("Phase 3F-7 — Customer-preview activation plan")
    st.info("Protected preview may be reviewed, but public Customer release remains disabled.")
    st.write("Decision:", data["decision"])
    st.write("Status:", data["status"])
    st.write("Guardrails:")
    for item in data["activation_guardrails"]:
        st.write(f"- {item}")
    return data
