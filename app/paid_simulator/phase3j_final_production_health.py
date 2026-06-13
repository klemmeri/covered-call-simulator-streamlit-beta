"""
phase3j_final_production_health.py

Final production health model for the Covered Call Simulator paid dashboard.

This module is intentionally read-only. It does not modify the dashboard. It
summarizes the customer-facing production readiness evidence gathered through
Phase 3J.
"""

from __future__ import annotations

PHASE3J_4_READY_MARKER = "PHASE3J_4_FINAL_PRODUCTION_HEALTH_READY"
PHASE3J_4_RELEASE_DECISION = "PHASE3J_4_FINAL_PRODUCTION_HEALTH_PASS_NO_DASHBOARD_CHANGE"


def build_final_production_health_model() -> dict:
    """Return the final production health model as a plain dictionary."""
    return {
        "ready_marker": PHASE3J_4_READY_MARKER,
        "release_decision": PHASE3J_4_RELEASE_DECISION,
        "dashboard_change": False,
        "health_domains": [
            "dashboard syntax",
            "controlled public activation",
            "customer workflow verification",
            "risk warning disclosure",
            "save reload export workflow",
            "customer browser checklist",
            "production wording polish",
            "checkpoint report availability",
        ],
        "required_customer_labels": [
            "current price",
            "strike",
            "premium",
            "breakeven",
            "max profit",
            "downside cushion",
            "assignment zone",
            "warning",
        ],
        "required_risk_terms": [
            "assignment",
            "downside",
            "capped",
            "breakeven",
            "estimate",
        ],
        "final_status": "Ready for Phase 3 completion handoff after browser spot-check.",
    }


def render_final_production_health(streamlit_module=None) -> dict:
    """Render when Streamlit is supplied; otherwise return the model."""
    model = build_final_production_health_model()
    if streamlit_module is None:
        return model

    st = streamlit_module
    st.subheader("Final production health check")
    st.caption("Read-only validation summary. No dashboard changes are made by this check.")
    st.json(model)
    return model
