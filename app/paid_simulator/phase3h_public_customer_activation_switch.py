"""
phase3h_public_customer_activation_switch.py

Phase 3H-1: Public Customer-view activation switch scaffold.

This module defines a conservative activation switch model for the public
customer-facing payoff workbench. It deliberately keeps public activation
disabled until a later explicit dashboard integration checkpoint.
"""

PHASE3H_1_PUBLIC_CUSTOMER_ACTIVATION_SWITCH_READY = "PHASE3H_1_PUBLIC_CUSTOMER_ACTIVATION_SWITCH_READY"

PUBLIC_CUSTOMER_VIEW_ENABLED = False
PROTECTED_PREVIEW_REQUIRED = True
REQUIRES_EXPLICIT_DASHBOARD_ACTIVATION = True

RELEASE_DECISION = "PHASE3H_1_SWITCH_SCAFFOLD_READY_PUBLIC_CUSTOMER_VIEW_DISABLED"

CUSTOMER_FACING_REQUIREMENTS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

ACTIVATION_GUARDRAILS = [
    "Do not enable public Customer view until the explicit activation checkpoint passes.",
    "Keep protected preview available for verification before public exposure.",
    "Require dashboard syntax validation before any config_form_app.py change.",
    "Require Customer-view protection checks after any dashboard change.",
    "Require rollback backup before modifying config_form_app.py.",
]

ACTIVATION_REQUIREMENTS = [
    "Phase 3E customer payoff workbench checkpoint complete.",
    "Phase 3F protected customer-preview checkpoint complete.",
    "Phase 3G public-release-preparation checkpoint complete.",
    "Customer-facing labels and risk warnings visible.",
    "Public activation flag remains disabled until explicitly changed.",
]


class Phase3HActivationSwitchModel:
    """Plain Python render model with a stable to_dict interface."""

    def __init__(self):
        self.marker = PHASE3H_1_PUBLIC_CUSTOMER_ACTIVATION_SWITCH_READY
        self.public_customer_view_enabled = PUBLIC_CUSTOMER_VIEW_ENABLED
        self.protected_preview_required = PROTECTED_PREVIEW_REQUIRED
        self.requires_explicit_dashboard_activation = REQUIRES_EXPLICIT_DASHBOARD_ACTIVATION
        self.release_decision = RELEASE_DECISION
        self.customer_facing_requirements = list(CUSTOMER_FACING_REQUIREMENTS)
        self.activation_guardrails = list(ACTIVATION_GUARDRAILS)
        self.activation_requirements = list(ACTIVATION_REQUIREMENTS)
        self.next_checkpoint = "Phase 3H-2 guarded public Customer-view activation route"

    def to_dict(self):
        return {
            "marker": self.marker,
            "public_customer_view_enabled": self.public_customer_view_enabled,
            "protected_preview_required": self.protected_preview_required,
            "requires_explicit_dashboard_activation": self.requires_explicit_dashboard_activation,
            "release_decision": self.release_decision,
            "customer_facing_requirements": list(self.customer_facing_requirements),
            "activation_guardrails": list(self.activation_guardrails),
            "activation_requirements": list(self.activation_requirements),
            "next_checkpoint": self.next_checkpoint,
        }



def build_phase3h_activation_switch_model():
    """Build the Phase 3H-1 activation switch model."""
    return Phase3HActivationSwitchModel()



def render_phase3h_activation_switch(streamlit_module=None):
    """
    Render the activation switch when Streamlit is available.

    In bare-mode checks, return a dictionary so the checker can validate the
    model without a Streamlit runtime.
    """
    model = build_phase3h_activation_switch_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader("Phase 3H-1: Public Customer-view activation switch")
    st.info("Public Customer view remains disabled. This is an activation scaffold only.")
    st.write("Release decision:", data["release_decision"])

    st.markdown("### Activation guardrails")
    for item in data["activation_guardrails"]:
        st.write("- " + item)

    st.markdown("### Customer-facing requirements")
    for item in data["customer_facing_requirements"]:
        st.write("- " + item)

    return data
