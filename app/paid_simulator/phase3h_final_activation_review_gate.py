"""
phase3h_final_activation_review_gate.py

Phase 3H-6 final activation-review gate for the Covered Call Simulator paid dashboard.

This module does not enable the public Customer view. It records that the public
activation route has passed protected preparation and is ready for an explicit,
separate activation decision.
"""

PHASE3H_6_FINAL_ACTIVATION_REVIEW_READY = "PHASE3H_6_FINAL_ACTIVATION_REVIEW_READY"
PHASE3H_6_PUBLIC_CUSTOMER_ENABLED = False
PHASE3H_6_RELEASE_DECISION = (
    "PHASE3H_6_FINAL_REVIEW_READY_PUBLIC_CUSTOMER_VIEW_STILL_DISABLED"
)

CUSTOMER_LABELS = [
    "current price",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

GUARDRAILS = [
    "Do not enable public Customer view without an explicit activation package.",
    "Keep protected preview and public release paths separate.",
    "Preserve Phase 3D, Phase 3E, Phase 3F, and Phase 3G dashboard markers.",
    "Verify customer-facing labels before public activation.",
    "Keep warning language visible for risky covered-call setups.",
]

REQUIREMENTS = [
    "Dashboard syntax remains valid.",
    "Public Customer view remains disabled.",
    "Protected preview route remains staged.",
    "Activation readiness report exists.",
    "Final activation requires a separate intentional package.",
]


def build_phase3h_6_final_activation_review_model() -> dict:
    """Return the final activation-review model as a plain dictionary."""
    return {
        "marker": PHASE3H_6_FINAL_ACTIVATION_REVIEW_READY,
        "public_customer_enabled": PHASE3H_6_PUBLIC_CUSTOMER_ENABLED,
        "release_decision": PHASE3H_6_RELEASE_DECISION,
        "customer_labels": list(CUSTOMER_LABELS),
        "guardrails": list(GUARDRAILS),
        "requirements": list(REQUIREMENTS),
        "status": "ready_for_explicit_activation_review",
    }


def render_phase3h_6_final_activation_review(streamlit_module=None) -> dict:
    """Render when Streamlit is supplied; otherwise return the model for checks."""
    model = build_phase3h_6_final_activation_review_model()
    st = streamlit_module
    if st is None:
        return model

    st.subheader("Phase 3H-6 — Final activation review")
    st.info("Public Customer view remains disabled. This is a final review gate only.")
    st.write("Release decision:", model["release_decision"])
    st.write("Guardrails")
    for item in model["guardrails"]:
        st.write(f"- {item}")
    return model
