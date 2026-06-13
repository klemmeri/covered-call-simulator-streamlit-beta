"""
phase3h_protected_pre_activation_validation.py

Phase 3H-4 protected pre-activation validation model for the Covered Call Simulator.

This module consolidates the Phase 3H activation-switch, activation-route, and
smoke-test evidence before any public Customer-view activation is allowed.

Important: public Customer-view access remains disabled.
"""

PHASE3H_4_PROTECTED_PRE_ACTIVATION_READY = "PHASE3H_4_PROTECTED_PRE_ACTIVATION_READY"
PHASE3H_4_PUBLIC_CUSTOMER_ENABLED = False
PHASE3H_4_RELEASE_DECISION = "PHASE3H_4_PRE_ACTIVATION_VALIDATED_PUBLIC_CUSTOMER_VIEW_DISABLED"

CUSTOMER_LABELS = [
    "current price",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

GUARDRAILS = [
    "Public Customer view remains disabled until an explicit activation package changes the release flag.",
    "Protected preview route must remain available for internal review before public release.",
    "Dashboard syntax must remain valid after every guarded helper append.",
    "Phase 3D, Phase 3E, Phase 3F, Phase 3G, and Phase 3H markers must remain detectable.",
    "Customer-facing payoff labels and warning language must remain visible in the staged workflow.",
]

REQUIRED_PRIOR_REPORTS = [
    "phase3g_8_completion_gate_checkpoint_report.txt",
    "phase3h_1_activation_switch_checkpoint_report.txt",
    "phase3h_2_activation_route_checkpoint_report.txt",
    "phase3h_3_activation_route_smoke_test_checkpoint_report.txt",
]


def build_phase3h_4_validation_model():
    """Build a dict-compatible Phase 3H-4 validation model."""
    return {
        "marker": PHASE3H_4_PROTECTED_PRE_ACTIVATION_READY,
        "public_customer_enabled": PHASE3H_4_PUBLIC_CUSTOMER_ENABLED,
        "release_decision": PHASE3H_4_RELEASE_DECISION,
        "mode": "protected_pre_activation_validation",
        "customer_labels": list(CUSTOMER_LABELS),
        "guardrails": list(GUARDRAILS),
        "required_prior_reports": list(REQUIRED_PRIOR_REPORTS),
        "summary": (
            "Phase 3H protected pre-activation checks are staged. "
            "Public Customer view remains disabled."
        ),
    }


def render_phase3h_4_validation(streamlit_module=None):
    """Render the validation model when Streamlit is available; otherwise return the model dict."""
    model = build_phase3h_4_validation_model()
    st = streamlit_module
    if st is None:
        return model

    st.subheader("Phase 3H-4 protected pre-activation validation")
    st.info("Public Customer view remains disabled. This is a validation gate only.")
    st.write(model["summary"])
    st.write("Release decision:", model["release_decision"])
    st.write("Guardrails")
    for item in model["guardrails"]:
        st.write("- " + item)
    return model
