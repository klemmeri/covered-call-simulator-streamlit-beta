"""
phase3i_customer_workflow_completion_gate.py

Phase 3I-7 customer workflow completion gate for the Covered Call Simulator.

This module is intentionally lightweight and deterministic. It summarizes the
post-activation customer workflow checks that must remain true before Phase 3I
is considered complete.
"""

from __future__ import annotations

PHASE3I_7_CUSTOMER_WORKFLOW_COMPLETION_READY = "PHASE3I_7_CUSTOMER_WORKFLOW_COMPLETION_READY"
PHASE3I_7_RELEASE_DECISION = "PHASE3I_COMPLETE_CUSTOMER_WORKFLOW_VERIFIED"
PUBLIC_CUSTOMER_WORKFLOW_EXPECTED = True


def build_customer_workflow_completion_model() -> dict:
    """Return a dict-compatible Phase 3I-7 completion model."""
    customer_labels = [
        "current price",
        "strike",
        "premium",
        "breakeven",
        "max profit",
        "downside cushion",
        "assignment zone",
        "warning",
    ]

    completed_checks = [
        "post-activation browser verification",
        "customer workflow smoke test",
        "save reload export verification",
        "risk warning disclosure verification",
        "customer explanation wording verification",
        "customer output report verification",
    ]

    guardrails = [
        "Covered-call payoff outputs are estimates, not guarantees.",
        "Customer-facing workflow must explain capped upside and assignment risk.",
        "Customer-facing workflow must show downside risk and breakeven clearly.",
        "Saved setup, reload, refresh, and export language must remain visible.",
        "Developer-only diagnostics must remain separated from ordinary customer language.",
    ]

    required_reports = [
        "phase3i_1_post_activation_browser_checkpoint_report.txt",
        "phase3i_2_customer_workflow_smoke_test_checkpoint_report.txt",
        "phase3i_3_save_reload_export_checkpoint_report.txt",
        "phase3i_4_customer_risk_warning_checkpoint_report.txt",
        "phase3i_5_customer_explanation_checkpoint_report.txt",
        "phase3i_6_customer_output_report_checkpoint_report.txt",
    ]

    return {
        "ready_marker": PHASE3I_7_CUSTOMER_WORKFLOW_COMPLETION_READY,
        "release_decision": PHASE3I_7_RELEASE_DECISION,
        "public_customer_workflow_expected": PUBLIC_CUSTOMER_WORKFLOW_EXPECTED,
        "customer_labels": customer_labels,
        "completed_checks": completed_checks,
        "guardrails": guardrails,
        "required_reports": required_reports,
        "summary": (
            "Phase 3I is complete when the activated customer workflow has passed "
            "browser, smoke-test, save/reload/export, risk-warning, explanation, "
            "and output-report checks."
        ),
    }


def render_customer_workflow_completion_gate(streamlit_module=None) -> dict:
    """Render when Streamlit is available; otherwise return the model dict."""
    model = build_customer_workflow_completion_model()

    st = streamlit_module
    if st is None:
        return model

    st.header("Customer workflow completion gate")
    st.write(model["summary"])
    st.subheader("Completion checks")
    for item in model["completed_checks"]:
        st.write(f"- {item}")
    st.subheader("Customer-facing labels")
    st.write(", ".join(model["customer_labels"]))
    st.subheader("Guardrails")
    for item in model["guardrails"]:
        st.warning(item)

    return model
