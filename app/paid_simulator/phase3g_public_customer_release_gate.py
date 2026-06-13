"""
phase3g_public_customer_release_gate.py

Phase 3G-1 public Customer-view release gate for the Covered Call Simulator.

This module does not enable the public Customer view. It creates a formal
release-gate model that distinguishes three states:

1. Developer view: available for internal workbench testing.
2. Protected customer-preview mode: available for controlled preview only.
3. Public Customer view: still disabled until a later explicit release step.
"""

PHASE3G_1_PUBLIC_RELEASE_GATE_READY = "PHASE3G_1_PUBLIC_RELEASE_GATE_READY"
PHASE3G_1_PUBLIC_CUSTOMER_RELEASE_ENABLED = False
PHASE3G_1_PROTECTED_PREVIEW_REQUIRED = True


class Phase3GPublicReleaseGateModel:
    """Plain Python render model used by the Phase 3G-1 check script."""

    def __init__(self):
        self.marker = PHASE3G_1_PUBLIC_RELEASE_GATE_READY
        self.public_customer_release_enabled = PHASE3G_1_PUBLIC_CUSTOMER_RELEASE_ENABLED
        self.protected_preview_required = PHASE3G_1_PROTECTED_PREVIEW_REQUIRED
        self.title = "Phase 3G public Customer-view release gate"
        self.status = "NOT PUBLICLY ENABLED"
        self.release_decision = "DO NOT ENABLE PUBLIC CUSTOMER VIEW YET"
        self.sections = [
            "Developer-view workbench validation",
            "Protected customer-preview validation",
            "Customer-view safety verification",
            "Public-release decision checklist",
        ]
        self.customer_facing_requirements = [
            "current price label visible",
            "strike label visible",
            "premium label visible",
            "breakeven label visible",
            "max profit label visible",
            "downside cushion label visible",
            "assignment zone label visible",
            "warning/risk language visible",
            "save/reload workflow language visible",
            "scenario refresh/export workflow language visible",
        ]
        self.guardrails = [
            "Ordinary Customer view must remain disabled until explicit release.",
            "Developer-only markers must not appear in the public Customer view.",
            "Risk warnings must remain visible before any public release.",
            "Phase 3D, Phase 3E, and Phase 3F regression markers must remain detectable.",
            "A rollback path must exist before changing config_form_app.py.",
        ]
        self.required_prior_reports = [
            "outputs/reports/paid_simulator/phase3e_9_completion_checkpoint_report.txt",
            "outputs/reports/paid_simulator/phase3f_3_customer_preview_route_checkpoint_report.txt",
            "outputs/reports/paid_simulator/phase3f_4_preview_visual_checkpoint_report.txt",
            "outputs/reports/paid_simulator/phase3f_8_completion_gate_checkpoint_report.txt",
        ]

    def to_dict(self):
        return {
            "marker": self.marker,
            "public_customer_release_enabled": self.public_customer_release_enabled,
            "protected_preview_required": self.protected_preview_required,
            "title": self.title,
            "status": self.status,
            "release_decision": self.release_decision,
            "sections": list(self.sections),
            "customer_facing_requirements": list(self.customer_facing_requirements),
            "guardrails": list(self.guardrails),
            "required_prior_reports": list(self.required_prior_reports),
        }


def build_phase3g_public_release_gate_model():
    """Build the Phase 3G-1 release-gate model."""
    return Phase3GPublicReleaseGateModel()


def render_phase3g_public_release_gate(streamlit_module=None):
    """
    Render the Phase 3G-1 release gate.

    If no Streamlit module is supplied, return a plain dictionary so the
    checkpoint can run in PyCharm without launching Streamlit.
    """
    model = build_phase3g_public_release_gate_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader(data["title"])
    st.warning("Public Customer view is not enabled by this gate.")
    st.write(f"Status: {data['status']}")
    st.write(f"Decision: {data['release_decision']}")

    st.markdown("### Release sections")
    for section in data["sections"]:
        st.write(f"- {section}")

    st.markdown("### Guardrails")
    for guardrail in data["guardrails"]:
        st.write(f"- {guardrail}")

    return data
