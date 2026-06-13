"""
phase3i_customer_explanation_verification.py

Phase 3I-5 customer-facing explanation and wording verification model.

This module is intentionally standalone. It does not modify the Streamlit
app and can be imported by checkpoint scripts without requiring Streamlit.
"""

from __future__ import annotations

READY_MARKER = "PHASE3I_5_CUSTOMER_EXPLANATION_WORDING_READY"
RELEASE_DECISION = "PHASE3I_5_CUSTOMER_EXPLANATION_WORDING_VERIFIED"


def build_customer_explanation_verification_model() -> dict:
    """Return the Phase 3I-5 customer explanation verification model."""
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

    explanations = [
        {
            "topic": "Current price",
            "customer_text": "The current price is the stock price used for this payoff estimate.",
        },
        {
            "topic": "Strike",
            "customer_text": "The strike is the price where the covered call may cap further upside.",
        },
        {
            "topic": "Premium",
            "customer_text": "The premium is the option income received for selling the call.",
        },
        {
            "topic": "Breakeven",
            "customer_text": "Breakeven is the approximate stock price where the premium offsets the stock loss.",
        },
        {
            "topic": "Max profit",
            "customer_text": "Max profit is capped because the short call limits gains above the strike.",
        },
        {
            "topic": "Downside cushion",
            "customer_text": "Downside cushion is the limited protection provided by the premium received.",
        },
        {
            "topic": "Assignment zone",
            "customer_text": "Assignment zone means the stock may be called away if the option is in the money.",
        },
        {
            "topic": "Warning",
            "customer_text": "These results are estimates, not guarantees, and covered calls still carry stock downside risk.",
        },
    ]

    readability_guardrails = [
        "Use customer-facing wording, not developer terminology.",
        "Explain capped upside explicitly.",
        "Explain that premium provides only limited downside cushion.",
        "Explain assignment risk in plain language.",
        "State that scenario outputs are estimates, not guarantees.",
    ]

    return {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "public_customer_view_status": "controlled-enabled",
        "labels": labels,
        "explanations": explanations,
        "readability_guardrails": readability_guardrails,
        "plain_language_terms": [
            "current price",
            "strike",
            "premium",
            "breakeven",
            "max profit",
            "downside cushion",
            "assignment zone",
            "capped upside",
            "estimate",
            "warning",
        ],
    }


def render_customer_explanation_verification(streamlit_module=None) -> dict:
    """Render or return the Phase 3I-5 verification model."""
    model = build_customer_explanation_verification_model()
    if streamlit_module is None:
        return model

    st = streamlit_module
    st.subheader("Customer explanation verification")
    st.write("This verification confirms that the activated workflow uses plain customer-facing explanations.")
    for item in model["explanations"]:
        st.markdown(f"**{item['topic']}**: {item['customer_text']}")
    return model
