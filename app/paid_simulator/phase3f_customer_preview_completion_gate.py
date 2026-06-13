"""
phase3f_customer_preview_completion_gate.py

Completion gate model for Phase 3F of the Covered Call Simulator paid dashboard.

Phase 3F created a protected customer-preview path for the Phase 3E customer payoff
workbench. This module intentionally does not enable the ordinary Customer view.
It summarizes whether the preview layer is structurally ready for a later, explicit
customer-facing release step.
"""

from __future__ import annotations

PHASE3F_8_COMPLETION_GATE_READY = "PHASE3F_8_COMPLETION_GATE_READY"
PHASE3F_8_PUBLIC_CUSTOMER_ENABLED = False
PHASE3F_8_PROTECTED_PREVIEW_ENABLED = True


REQUIRED_PRIOR_CHECKPOINTS = [
    "Phase 3E-9 completion guardrail",
    "Phase 3F-1 customer promotion gate",
    "Phase 3F-2 protected customer preview shell",
    "Phase 3F-3 guarded customer preview route",
    "Phase 3F-4 preview visual verification",
    "Phase 3F-5 preview access gate",
    "Phase 3F-6 release-readiness gate",
    "Phase 3F-7 activation plan",
]

COMPLETION_GUARDRAILS = [
    "Ordinary Customer view remains disabled for Phase 3F preview work.",
    "Protected preview mode remains available for controlled review only.",
    "Customer-facing labels must remain plain-English and non-developer-facing.",
    "Risk/warning language must remain visible before future release.",
    "Dashboard syntax and Phase 3D/3E markers must remain intact.",
]

NEXT_RELEASE_REQUIREMENTS = [
    "Manual browser review of the protected preview route.",
    "Confirmation that no developer/test controls appear in ordinary Customer view.",
    "A separate explicit package before enabling any public Customer workflow.",
    "A rollback point or backup before any future dashboard switch is changed.",
]


class Phase3FCompletionGateModel:
    """Small plain-Python model with a stable to_dict interface."""

    def __init__(self) -> None:
        self.marker = PHASE3F_8_COMPLETION_GATE_READY
        self.public_customer_enabled = PHASE3F_8_PUBLIC_CUSTOMER_ENABLED
        self.protected_preview_enabled = PHASE3F_8_PROTECTED_PREVIEW_ENABLED
        self.status = "preview_complete_not_public"
        self.required_prior_checkpoints = list(REQUIRED_PRIOR_CHECKPOINTS)
        self.guardrails = list(COMPLETION_GUARDRAILS)
        self.next_release_requirements = list(NEXT_RELEASE_REQUIREMENTS)
        self.recommendation = (
            "Treat Phase 3F as complete for protected preview purposes only. "
            "Do not expose the workflow in ordinary Customer view until a later explicit release package passes."
        )

    def to_dict(self) -> dict:
        return {
            "marker": self.marker,
            "public_customer_enabled": self.public_customer_enabled,
            "protected_preview_enabled": self.protected_preview_enabled,
            "status": self.status,
            "required_prior_checkpoints": list(self.required_prior_checkpoints),
            "guardrails": list(self.guardrails),
            "next_release_requirements": list(self.next_release_requirements),
            "recommendation": self.recommendation,
        }


def build_phase3f_completion_gate_model() -> Phase3FCompletionGateModel:
    """Build the Phase 3F completion-gate model."""
    return Phase3FCompletionGateModel()


def render_phase3f_completion_gate(streamlit_module=None):
    """
    Render the completion gate or return a dictionary fallback.

    Returning a dictionary in fallback mode keeps non-Streamlit check scripts simple
    and avoids depending on Streamlit script context during validation.
    """
    model = build_phase3f_completion_gate_model()
    model_dict = model.to_dict()

    if streamlit_module is None:
        return model_dict

    st = streamlit_module
    st.subheader("Phase 3F customer-preview completion gate")
    st.caption("Protected preview is available. Ordinary Customer view remains disabled.")

    st.info(model_dict["recommendation"])

    st.markdown("#### Completion guardrails")
    for item in model_dict["guardrails"]:
        st.write(f"- {item}")

    st.markdown("#### Before any public Customer release")
    for item in model_dict["next_release_requirements"]:
        st.write(f"- {item}")

    return model_dict
