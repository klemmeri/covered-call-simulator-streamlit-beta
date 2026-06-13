"""
phase3h_public_customer_activation.py

Controlled public Customer-view activation model for the paid Covered Call Simulator.

This module intentionally separates the activation decision model from the Streamlit
app wiring. The dashboard installer stages an activation marker and public-enabled
flag only after the prior Phase 3H review gates have passed.
"""

from __future__ import annotations

PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY = "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY"
PHASE3H_7_PUBLIC_CUSTOMER_ENABLED = True
PHASE3H_7_RELEASE_DECISION = "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED"

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
    "Public Customer view is enabled only through the Phase 3H-7 controlled activation marker.",
    "Developer-view diagnostics remain separate from the public customer workflow.",
    "Risk warnings must remain visible for weak or unsafe payoff setups.",
    "Save/reload/export language must remain customer-facing and non-technical.",
    "Activation can be reversed by restoring the timestamped config_form_app.py backup.",
]


def build_phase3h_7_activation_model() -> dict:
    """Return a plain dictionary activation model for check scripts and dashboard helpers."""
    return {
        "marker": PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY,
        "public_customer_enabled": PHASE3H_7_PUBLIC_CUSTOMER_ENABLED,
        "release_decision": PHASE3H_7_RELEASE_DECISION,
        "customer_labels": CUSTOMER_LABELS,
        "guardrails": GUARDRAILS,
        "status": "controlled_public_customer_activation_enabled",
    }


def render_phase3h_7_public_customer_activation(streamlit_module=None) -> dict:
    """
    Render the activation summary when Streamlit is available.

    In bare Python/check mode, return the dict model directly.
    """
    model = build_phase3h_7_activation_model()
    st = streamlit_module
    if st is None:
        return model

    st.subheader("Customer payoff workbench")
    st.caption("Controlled public Customer-view activation is enabled.")
    st.info("Use this workflow to review covered-call payoff metrics, risk warnings, and setup scenarios.")
    cols = st.columns(3)
    cols[0].metric("Current price", "Customer input")
    cols[1].metric("Breakeven", "Calculated")
    cols[2].metric("Max profit", "Calculated")
    st.warning("Warning: covered calls cap upside and do not remove downside stock risk.")
    return model
