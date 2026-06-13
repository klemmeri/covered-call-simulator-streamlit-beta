"""
phase3h_public_customer_activation_route.py

Phase 3H-2 public customer activation route scaffold.

This module defines the guarded public Customer-view route model for the
Covered Call Simulator paid dashboard. It intentionally keeps public customer
activation disabled. The route exists so future activation can be tested and
reviewed without exposing the workflow prematurely.
"""

PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY = "PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY"
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False
PHASE3H_2_RELEASE_DECISION = "PHASE3H_2_ROUTE_STAGED_PUBLIC_CUSTOMER_VIEW_DISABLED"

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

GUARDRAILS = [
    "Public Customer view remains disabled until an explicit release step changes the activation flag.",
    "Protected customer-preview mode must pass visual verification before public exposure.",
    "Risk and warning language must remain visible in the customer-facing workflow.",
    "Developer-only controls must not appear in the ordinary Customer view.",
    "Dashboard syntax and prior Phase 3D/3E/3F/3G markers must remain intact.",
]

SECTIONS = [
    {
        "name": "Route status",
        "summary": "Public Customer route is staged but disabled.",
    },
    {
        "name": "Customer-facing workflow",
        "summary": "The payoff workbench labels are ready for customer review.",
    },
    {
        "name": "Release controls",
        "summary": "Activation requires a later explicit release gate.",
    },
    {
        "name": "Guardrails",
        "summary": "Customer protection and risk language remain mandatory.",
    },
]


class Phase3HPublicActivationRouteModel:
    """Small explicit model with a stable to_dict contract."""

    def __init__(self):
        self.marker = PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY
        self.public_customer_enabled = PHASE3H_2_PUBLIC_CUSTOMER_ENABLED
        self.release_decision = PHASE3H_2_RELEASE_DECISION
        self.customer_labels = list(CUSTOMER_LABELS)
        self.guardrails = list(GUARDRAILS)
        self.sections = list(SECTIONS)

    def to_dict(self):
        return {
            "marker": self.marker,
            "public_customer_enabled": self.public_customer_enabled,
            "release_decision": self.release_decision,
            "customer_labels": list(self.customer_labels),
            "guardrails": list(self.guardrails),
            "sections": list(self.sections),
        }


def build_phase3h_public_activation_route_model():
    """Return the Phase 3H-2 route model."""
    return Phase3HPublicActivationRouteModel()


def render_phase3h_public_activation_route(streamlit_module=None):
    """Render with Streamlit when supplied, otherwise return a plain dict."""
    model = build_phase3h_public_activation_route_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader("Public Customer-view activation route")
    st.caption("Phase 3H-2 guarded route. Public Customer view remains disabled.")
    st.warning("Public Customer view is not enabled yet. This route is staged for controlled release testing only.")

    for section in data["sections"]:
        st.markdown(f"**{section['name']}**")
        st.write(section["summary"])

    st.markdown("**Required customer-facing labels**")
    st.write(", ".join(data["customer_labels"]))

    st.markdown("**Guardrails**")
    for guardrail in data["guardrails"]:
        st.write(f"- {guardrail}")

    return data
