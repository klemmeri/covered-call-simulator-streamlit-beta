"""
phase3h_activation_readiness_report.py

Phase 3H-5 controlled activation-readiness model for the Covered Call Simulator.

This module is intentionally conservative. It summarizes whether the public
customer-view route is staged, whether the protected-route checks have passed,
and whether the public Customer view should remain disabled.
"""

PHASE3H_5_ACTIVATION_READINESS_READY = "PHASE3H_5_ACTIVATION_READINESS_READY"
PHASE3H_5_PUBLIC_CUSTOMER_ENABLED = False
PHASE3H_5_RELEASE_DECISION = "PHASE3H_5_READY_FOR_FINAL_ACTIVATION_REVIEW_PUBLIC_CUSTOMER_VIEW_DISABLED"

CUSTOMER_FACING_LABELS = [
    "current price",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

GUARDRAILS = [
    "Public Customer view remains disabled until an explicit activation package changes the flag.",
    "Protected preview must remain available for review before public activation.",
    "Customer-facing labels must remain plain-English and non-developer-facing.",
    "Risk and warning language must remain visible before promotion.",
    "Dashboard syntax and prior phase markers must be checked before activation.",
]

READINESS_REQUIREMENTS = [
    "Phase 3E customer payoff workflow complete.",
    "Phase 3F protected customer-preview workflow complete.",
    "Phase 3G public-release preparation complete.",
    "Phase 3H protected pre-activation validation complete.",
    "No public Customer-view exposure until final activation is explicitly approved.",
]


def build_activation_readiness_model() -> dict:
    """Return a dict-compatible activation-readiness model."""
    return {
        "marker": PHASE3H_5_ACTIVATION_READINESS_READY,
        "public_customer_enabled": PHASE3H_5_PUBLIC_CUSTOMER_ENABLED,
        "release_decision": PHASE3H_5_RELEASE_DECISION,
        "customer_facing_labels": list(CUSTOMER_FACING_LABELS),
        "guardrails": list(GUARDRAILS),
        "readiness_requirements": list(READINESS_REQUIREMENTS),
        "status": "ready for final activation review, not public activation",
    }


def render_activation_readiness_report(streamlit_module=None) -> dict:
    """
    Render or return the activation-readiness model.

    In bare/check mode this returns a dictionary. With Streamlit available it
    writes a small protected readiness panel and still returns the model.
    """
    model = build_activation_readiness_model()
    st = streamlit_module
    if st is None:
        return model

    st.subheader("Phase 3H-5 activation readiness")
    st.info("Public Customer view remains disabled. This is a readiness report, not activation.")
    st.write("Release decision:", model["release_decision"])
    st.write("Guardrails")
    for item in model["guardrails"]:
        st.write("- " + item)
    st.write("Customer-facing labels")
    for label in model["customer_facing_labels"]:
        st.write("- " + label)
    return model
