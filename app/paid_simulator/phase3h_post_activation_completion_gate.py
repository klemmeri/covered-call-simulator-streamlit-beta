"""
phase3h_post_activation_completion_gate.py

Phase 3H-8 post-activation completion gate for the Covered Call Simulator.

This module summarizes the controlled public Customer-view activation state.
It does not mutate dashboard files. It produces a plain dictionary render model
so checkpoint scripts and Streamlit wrappers can consume it safely.
"""

PHASE3H_8_POST_ACTIVATION_COMPLETION_READY = "PHASE3H_8_POST_ACTIVATION_COMPLETION_READY"
PHASE3H_8_RELEASE_DECISION = "PHASE3H_COMPLETE_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_VERIFIED"
PHASE3H_8_PUBLIC_CUSTOMER_VIEW_ENABLED = True

CUSTOMER_LABELS = [
    "current price",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

GUARDRAILS = [
    "Activation must remain explicitly controlled by Phase 3H markers.",
    "Prior Developer-view Phase 3D, Phase 3E, and Phase 3F markers must remain present.",
    "Dashboard syntax must remain valid after the activation block is appended.",
    "A timestamped dashboard backup must exist before activation.",
    "The customer-facing workflow must retain warning and risk language.",
]

REQUIRED_PRIOR_REPORTS = [
    "phase3e_9_completion_checkpoint_report.txt",
    "phase3f_8_completion_gate_checkpoint_report.txt",
    "phase3g_8_completion_gate_checkpoint_report.txt",
    "phase3h_6_final_activation_review_checkpoint_report.txt",
    "phase3h_7_public_activation_checkpoint_report.txt",
]


def build_phase3h_8_completion_model() -> dict:
    """Return a dict-compatible Phase 3H-8 completion model."""
    return {
        "marker": PHASE3H_8_POST_ACTIVATION_COMPLETION_READY,
        "public_customer_view_enabled": PHASE3H_8_PUBLIC_CUSTOMER_VIEW_ENABLED,
        "release_decision": PHASE3H_8_RELEASE_DECISION,
        "title": "Phase 3H-8 post-activation completion gate",
        "summary": (
            "Controlled public Customer-view activation has been staged and must now "
            "be verified against dashboard syntax, prior phase markers, backups, and "
            "customer-facing guardrails."
        ),
        "customer_labels": list(CUSTOMER_LABELS),
        "guardrails": list(GUARDRAILS),
        "required_prior_reports": list(REQUIRED_PRIOR_REPORTS),
    }


def render_phase3h_8_completion_gate(streamlit_module=None) -> dict:
    """Render or return the Phase 3H-8 completion model."""
    model = build_phase3h_8_completion_model()
    if streamlit_module is None:
        return model

    st = streamlit_module
    st.subheader(model["title"])
    st.success(model["release_decision"])
    st.write(model["summary"])
    st.markdown("**Customer-facing labels verified**")
    for label in model["customer_labels"]:
        st.write(f"- {label}")
    st.markdown("**Guardrails**")
    for guardrail in model["guardrails"]:
        st.write(f"- {guardrail}")
    return model
