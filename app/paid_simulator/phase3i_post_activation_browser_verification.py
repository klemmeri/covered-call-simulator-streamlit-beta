"""
phase3i_post_activation_browser_verification.py

Phase 3I-1 model for post-activation browser/customer workflow verification.
This module is intentionally read-only. It does not modify the dashboard.
"""

PHASE3I_1_READY_MARKER = "PHASE3I_1_POST_ACTIVATION_BROWSER_VERIFICATION_READY"
PHASE3I_1_RELEASE_DECISION = "PHASE3I_1_VERIFY_PUBLIC_CUSTOMER_WORKFLOW_IN_BROWSER"

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
    "Dashboard syntax must remain valid.",
    "Phase 3H controlled activation marker must remain present.",
    "Prior Phase 3D, Phase 3E, Phase 3F, and Phase 3G markers must remain present.",
    "Customer-facing labels must remain visible in the public workflow.",
    "Risk/warning language must remain visible before relying on the workflow.",
]

BROWSER_CHECKLIST = [
    "Run the Streamlit dashboard with streamlit run app\\paid_simulator\\config_form_app.py.",
    "Confirm the dashboard opens without a red traceback.",
    "Confirm the public Customer-view activation path is present after Phase 3H-7.",
    "Confirm the customer payoff workflow uses customer-facing labels rather than developer labels.",
    "Confirm warning/risk language appears for risky covered-call setups.",
    "Confirm Developer-view Phase 3D/3E/3F material is still available where expected.",
]


def build_phase3i_1_model():
    """Return a dict-compatible model for the Phase 3I-1 verification checkpoint."""
    return {
        "marker": PHASE3I_1_READY_MARKER,
        "release_decision": PHASE3I_1_RELEASE_DECISION,
        "public_customer_activation_expected": True,
        "dashboard_changes_made": False,
        "customer_labels": list(CUSTOMER_LABELS),
        "guardrails": list(GUARDRAILS),
        "browser_checklist": list(BROWSER_CHECKLIST),
    }


def render_phase3i_1_model(streamlit_module=None):
    """Render if Streamlit is supplied; otherwise return the model dictionary."""
    model = build_phase3i_1_model()
    st = streamlit_module
    if st is None:
        return model
    st.subheader("Phase 3I-1 — Post-activation browser verification")
    st.write(model["release_decision"])
    st.write("Customer labels:")
    st.write(model["customer_labels"])
    st.write("Guardrails:")
    st.write(model["guardrails"])
    return model
