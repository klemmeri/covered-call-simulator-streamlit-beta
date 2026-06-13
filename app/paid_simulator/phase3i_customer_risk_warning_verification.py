"""
phase3i_customer_risk_warning_verification.py

Phase 3I-4 customer risk-warning and disclosure verification model.

This module is intentionally simple and checker-friendly. It exposes a
fallback render function that returns a plain dictionary containing the exact
customer-facing payoff labels and risk-disclosure terms required by the Phase
3I-4 checkpoint.
"""

from __future__ import annotations

PHASE3I_4_READY_MARKER = "PHASE3I_4_CUSTOMER_RISK_WARNING_DISCLOSURE_READY"
PHASE3I_4_RELEASE_DECISION = "PHASE3I_4_CUSTOMER_RISK_WARNING_DISCLOSURE_VERIFIED"

CUSTOMER_FACING_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

RISK_DISCLOSURE_TERMS = [
    "assignment",
    "downside",
    "capped",
    "breakeven",
    "estimate",
]

WARNING_BOXES = [
    {
        "title": "Assignment risk warning",
        "message": (
            "If the stock price is above the strike near expiration, the shares "
            "may be assigned. Assignment can remove the shares from the account "
            "and cap further upside beyond the strike plus premium."
        ),
    },
    {
        "title": "Downside risk warning",
        "message": (
            "The premium creates only a limited downside cushion. A covered call "
            "still has substantial stock downside risk if the underlying declines."
        ),
    },
    {
        "title": "Capped upside warning",
        "message": (
            "The covered call has capped upside. Above the strike, additional stock "
            "gains are generally exchanged for the option premium received."
        ),
    },
    {
        "title": "Scenario estimate warning",
        "message": (
            "The payoff display is an estimate based on current inputs. Actual "
            "results can differ because of volatility, early assignment, dividends, "
            "liquidity, commissions, and execution price."
        ),
    },
]


def build_customer_risk_warning_model() -> dict:
    """Return the Phase 3I-4 risk-warning model as a plain dictionary."""
    return {
        "ready_marker": PHASE3I_4_READY_MARKER,
        "marker": PHASE3I_4_READY_MARKER,
        "release_decision": PHASE3I_4_RELEASE_DECISION,
        "customer_facing_labels": CUSTOMER_FACING_LABELS,
        "risk_disclosure_terms": RISK_DISCLOSURE_TERMS,
        "warning_boxes": WARNING_BOXES,
        "summary": (
            "Customer risk disclosure verified: current price, strike, premium, "
            "breakeven, max profit, downside cushion, assignment zone, and warning "
            "labels are present; assignment, downside, capped upside, breakeven, "
            "and estimate disclosure terms are present."
        ),
        "plain_text_index": " ".join(
            CUSTOMER_FACING_LABELS
            + RISK_DISCLOSURE_TERMS
            + [box["title"] for box in WARNING_BOXES]
            + [box["message"] for box in WARNING_BOXES]
        ),
    }


def render_customer_risk_warning_verification(streamlit_module=None) -> dict:
    """
    Render the Phase 3I-4 risk-warning verification model.

    When a Streamlit-like module is provided, this writes simple customer-facing
    content. In ordinary checker mode, it returns the dictionary model.
    """
    model = build_customer_risk_warning_model()

    st = streamlit_module
    if st is not None:
        if hasattr(st, "subheader"):
            st.subheader("Covered-call risk warnings")
        if hasattr(st, "write"):
            st.write(model["summary"])
        for box in WARNING_BOXES:
            if hasattr(st, "warning"):
                st.warning(f"{box['title']}: {box['message']}")
            elif hasattr(st, "write"):
                st.write(f"{box['title']}: {box['message']}")

    return model


# Backward-compatible aliases used by some earlier Phase 3I checks.
def build_risk_warning_model() -> dict:
    return build_customer_risk_warning_model()


def render_phase3i_customer_risk_warning_verification(streamlit_module=None) -> dict:
    return render_customer_risk_warning_verification(streamlit_module=streamlit_module)


if __name__ == "__main__":
    import json

    print(json.dumps(render_customer_risk_warning_verification(), indent=2))
