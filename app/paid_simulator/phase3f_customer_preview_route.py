"""
phase3f_customer_preview_route.py

Phase 3F-3 protected customer-preview dashboard route.

This module intentionally keeps the ordinary Customer view disabled while
providing a renderable preview route model for controlled review.
"""

from __future__ import annotations

from typing import Any


PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY = "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"
PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED = False
PHASE3F_3_PREVIEW_ROUTE_TITLE = "Phase 3F customer preview route"


class Phase3FPreviewRouteModel:
    """Small plain-Python model with explicit serialization for check scripts."""

    def __init__(self) -> None:
        self.marker = PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY
        self.title = PHASE3F_3_PREVIEW_ROUTE_TITLE
        self.customer_enabled = PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED
        self.preview_mode = "Protected preview only"
        self.sections = [
            {
                "section": "Preview status",
                "label": "Customer preview is staged but not enabled",
                "detail": "The ordinary Customer view remains protected while this route is reviewed.",
            },
            {
                "section": "Payoff workflow",
                "label": "Customer-facing payoff workbench",
                "detail": "Current price, strike, premium, breakeven, max profit, downside cushion, and assignment zone remain visible in preview language.",
            },
            {
                "section": "Scenario overlay",
                "label": "One-click scenario refresh path",
                "detail": "Scenario overlay language is available for preview without exposing developer controls.",
            },
            {
                "section": "Save and reload workflow",
                "label": "Protected setup persistence path",
                "detail": "Save, reload, refresh, and export actions remain staged for controlled review.",
            },
        ]
        self.guardrails = [
            "Ordinary Customer view is not enabled for Phase 3F-3.",
            "Developer-view Phase 3E readiness markers must remain present.",
            "Phase 3D dashboard markers must remain detectable.",
            "Risk and warning language must remain visible in the preview route.",
        ]
        self.customer_warning = "Preview route only; do not expose as the public Customer workflow until the release gate passes."

    def to_dict(self) -> dict[str, Any]:
        """Return the exact dictionary shape expected by Phase 3F-3 checks."""
        return {
            "marker": self.marker,
            "title": self.title,
            "customer_enabled": self.customer_enabled,
            "preview_mode": self.preview_mode,
            "sections": list(self.sections),
            "guardrails": list(self.guardrails),
            "customer_warning": self.customer_warning,
        }


def build_customer_preview_route_model() -> Phase3FPreviewRouteModel:
    """Build the protected customer-preview route model."""
    return Phase3FPreviewRouteModel()


def render_customer_preview_route(streamlit_module: Any | None = None) -> dict[str, Any]:
    """
    Render the protected preview route when Streamlit is supplied.

    In bare Python/check mode, return the serialized model dictionary. This is
    deliberate: the checkpoint expects ``isinstance(fallback, dict)``.
    """
    model = build_customer_preview_route_model().to_dict()

    if streamlit_module is None:
        return model

    st = streamlit_module
    st.subheader(model["title"])
    st.warning(model["customer_warning"])

    for section in model["sections"]:
        st.markdown(f"**{section['section']}**")
        st.caption(section["label"])
        st.write(section["detail"])

    st.markdown("**Preview guardrails**")
    for guardrail in model["guardrails"]:
        st.write(f"- {guardrail}")

    return model
