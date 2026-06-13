"""
phase3j_production_ui_wording_polish.py

Phase 3J-2 production UI wording and polish model for the Covered Call Simulator.
This module is intentionally dashboard-neutral. It defines the customer-facing
wording requirements that should be satisfied before deeper production UI work.
"""

from __future__ import annotations

PHASE3J_2_READY_MARKER = "PHASE3J_2_PRODUCTION_UI_WORDING_POLISH_READY"
PHASE3J_2_RELEASE_DECISION = "PHASE3J_2_UI_WORDING_POLISH_CHECKLIST_CREATED_NO_DASHBOARD_CHANGE"


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

POLISH_AREAS = [
    "Use plain-language labels before technical terms.",
    "Keep risk-warning language close to the inputs and payoff summary.",
    "Explain capped upside and assignment risk without implying certainty.",
    "Make save, reload, refresh, and export actions easy to distinguish.",
    "Avoid developer/test terms in customer-facing panels.",
]

PRODUCTION_GUARDRAILS = [
    "Do not remove Developer-view diagnostics until production replacement checks pass.",
    "Do not weaken downside-risk, capped-upside, or assignment-risk disclosures.",
    "Do not treat scenario overlays as forecasts or guarantees.",
    "Do not expose unfinished developer controls in the public Customer view.",
]


def build_ui_wording_polish_model() -> dict:
    """Return a dict-compatible Phase 3J-2 wording/polish model."""
    return {
        "marker": PHASE3J_2_READY_MARKER,
        "release_decision": PHASE3J_2_RELEASE_DECISION,
        "dashboard_changed": False,
        "customer_labels": list(CUSTOMER_LABELS),
        "polish_areas": list(POLISH_AREAS),
        "guardrails": list(PRODUCTION_GUARDRAILS),
        "plain_language_summary": (
            "Phase 3J-2 defines production wording and UI-polish requirements "
            "for the activated customer payoff workflow without changing the dashboard."
        ),
    }


def render_ui_wording_polish(streamlit_module=None) -> dict:
    """Render-compatible fallback for Streamlit or bare Python checks."""
    model = build_ui_wording_polish_model()
    if streamlit_module is None:
        return model

    st = streamlit_module
    st.subheader("Phase 3J-2 — Production UI wording polish")
    st.write(model["plain_language_summary"])
    st.write("Customer labels:", model["customer_labels"])
    st.write("Polish areas:", model["polish_areas"])
    st.write("Guardrails:", model["guardrails"])
    return model
