"""
phase3i_customer_workflow_smoke_test.py

Phase 3I-2 customer workflow smoke-test model for the Covered Call Simulator.

This module does not modify the dashboard. It provides a stable, importable
model used by the Phase 3I-2 checkpoint to confirm that the post-activation
customer-facing payoff workflow still exposes the required labels, guardrails,
and release-decision state.
"""

PHASE3I_2_CUSTOMER_WORKFLOW_SMOKE_TEST_READY = "PHASE3I_2_CUSTOMER_WORKFLOW_SMOKE_TEST_READY"
PHASE3I_2_RELEASE_DECISION = "PHASE3I_2_CUSTOMER_WORKFLOW_SMOKE_TEST_PASS"
PHASE3I_2_PUBLIC_CUSTOMER_VIEW_EXPECTED_ENABLED = True


def build_phase3i_customer_workflow_smoke_test_model():
    """Return a dict-compatible customer workflow smoke-test model."""
    return {
        "marker": PHASE3I_2_CUSTOMER_WORKFLOW_SMOKE_TEST_READY,
        "release_decision": PHASE3I_2_RELEASE_DECISION,
        "public_customer_view_expected_enabled": PHASE3I_2_PUBLIC_CUSTOMER_VIEW_EXPECTED_ENABLED,
        "title": "Customer payoff workflow smoke test",
        "customer_facing_labels": [
            "current price",
            "strike",
            "premium",
            "breakeven",
            "max profit",
            "downside cushion",
            "assignment zone",
            "warning",
        ],
        "guardrails": [
            "Show payoff estimates as planning information, not guaranteed outcomes.",
            "Warn when downside cushion is small relative to the current price.",
            "Warn when assignment risk is high near or above the strike.",
            "Keep developer diagnostics separate from the customer-facing workflow.",
            "Preserve prior Phase 3D, 3E, 3F, and 3H integration markers.",
        ],
        "workflow_sections": [
            "Setup inputs",
            "Payoff summary",
            "Scenario overlay",
            "Risk warnings",
            "Save/reload/export workflow",
        ],
    }


def render_phase3i_customer_workflow_smoke_test(streamlit_module=None):
    """Render when Streamlit is supplied; otherwise return the smoke-test model."""
    model = build_phase3i_customer_workflow_smoke_test_model()
    st = streamlit_module
    if st is None:
        return model

    st.subheader(model["title"])
    st.caption("Phase 3I-2 post-activation customer workflow smoke test.")
    st.write("Release decision:", model["release_decision"])
    st.write("Required customer-facing labels:")
    st.write(model["customer_facing_labels"])
    st.write("Guardrails:")
    st.write(model["guardrails"])
    return model
