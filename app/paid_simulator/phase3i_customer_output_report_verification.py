"""
Phase 3I-6 customer output/report verification.

This module defines the customer-facing output/report verification model for the
post-activation covered-call workflow. It intentionally does not modify the
Streamlit dashboard.
"""

PHASE3I_6_READY_MARKER = "PHASE3I_6_CUSTOMER_OUTPUT_REPORT_VERIFICATION_READY"
PHASE3I_6_RELEASE_DECISION = "PHASE3I_6_CUSTOMER_OUTPUT_REPORTS_VERIFIED"


def build_customer_output_report_verification_model():
    """Return a dict-compatible customer output/report verification model."""
    labels = [
        "current price",
        "strike",
        "premium",
        "breakeven",
        "max profit",
        "downside cushion",
        "assignment zone",
        "warning",
    ]
    expected_outputs = [
        "customer payoff summary",
        "saved setup JSON",
        "scenario overlay CSV",
        "browser checklist",
        "checkpoint report",
        "release decision",
    ]
    guardrails = [
        "Customer reports must use customer-facing language, not developer/debug language.",
        "Scenario values are estimates and must not be presented as guarantees.",
        "Risk warnings must remain visible in generated customer outputs.",
        "Saved setup and exported reports must preserve current price, strike, premium, breakeven, max profit, downside cushion, and assignment zone fields.",
    ]
    customer_report_text = (
        "Customer payoff summary includes current price, strike, premium, breakeven, "
        "max profit, downside cushion, assignment zone, warning language, capped upside, "
        "assignment risk, downside risk, and estimate/not-guarantee disclosure."
    )
    return {
        "ready_marker": PHASE3I_6_READY_MARKER,
        "release_decision": PHASE3I_6_RELEASE_DECISION,
        "public_customer_activation_state": "controlled-enabled",
        "labels": labels,
        "expected_outputs": expected_outputs,
        "guardrails": guardrails,
        "customer_report_text": customer_report_text,
    }


def render_customer_output_report_verification(streamlit_module=None):
    """Render or return the Phase 3I-6 verification model."""
    model = build_customer_output_report_verification_model()
    if streamlit_module is None:
        return model
    st = streamlit_module
    st.subheader("Customer output and report verification")
    st.write(model["customer_report_text"])
    for guardrail in model["guardrails"]:
        st.warning(guardrail)
    return model
