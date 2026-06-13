"""
phase3f_customer_preview_access_gate.py

Controlled access gate for the Phase 3F customer-preview workflow.

This module does not expose the preview workflow to the ordinary Customer view.
It provides a small, explicit promotion model that later dashboard code can use
when the project is ready for a controlled customer-preview release.
"""

from __future__ import annotations

from typing import Any, Dict, List


PHASE3F_5_ACCESS_GATE_READY = "PHASE3F_5_ACCESS_GATE_READY"
PHASE3F_5_ORDINARY_CUSTOMER_ENABLED = False
PHASE3F_5_PREVIEW_MODE_LABEL = "Protected Customer Preview"


class Phase3FPreviewAccessGate:
    """Plain Python model used by check scripts and future dashboard wiring."""

    def __init__(self) -> None:
        self.marker = PHASE3F_5_ACCESS_GATE_READY
        self.preview_mode_label = PHASE3F_5_PREVIEW_MODE_LABEL
        self.ordinary_customer_enabled = PHASE3F_5_ORDINARY_CUSTOMER_ENABLED
        self.preview_customer_enabled = True
        self.public_release_enabled = False
        self.sections = [
            {
                "name": "Preview purpose",
                "status": "ready",
                "description": "Allow protected review of the customer payoff workflow before public release.",
            },
            {
                "name": "Customer protection",
                "status": "protected",
                "description": "The ordinary Customer view remains disabled for Phase 3F preview features.",
            },
            {
                "name": "Developer review",
                "status": "available",
                "description": "Developer view can inspect preview routing, labels, warnings, and customer-facing language.",
            },
            {
                "name": "Release decision",
                "status": "not released",
                "description": "A later checkpoint must explicitly enable public customer exposure.",
            },
        ]
        self.guardrails = [
            "Do not expose Phase 3F preview controls in the ordinary Customer view.",
            "Keep Customer view free of developer/test controls until final release gate passes.",
            "Require dashboard syntax validation after any config_form_app.py change.",
            "Require a browser visual check before promotion from preview to customer-facing release.",
            "Keep the preview route reversible with backup and marker checks.",
        ]
        self.customer_labels = [
            "Current price",
            "Strike",
            "Premium",
            "Breakeven",
            "Max profit",
            "Downside cushion",
            "Assignment zone",
            "Risk warning",
        ]
        self.next_steps = [
            "Verify the preview shell in the browser.",
            "Confirm customer-facing labels are plain English.",
            "Confirm warnings appear before public release.",
            "Only then consider a controlled Customer-view enablement checkpoint.",
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "marker": self.marker,
            "preview_mode_label": self.preview_mode_label,
            "ordinary_customer_enabled": self.ordinary_customer_enabled,
            "preview_customer_enabled": self.preview_customer_enabled,
            "public_release_enabled": self.public_release_enabled,
            "sections": list(self.sections),
            "guardrails": list(self.guardrails),
            "customer_labels": list(self.customer_labels),
            "next_steps": list(self.next_steps),
        }


def build_phase3f_customer_preview_access_gate() -> Phase3FPreviewAccessGate:
    """Build the Phase 3F-5 preview-access gate model."""
    return Phase3FPreviewAccessGate()


def render_phase3f_customer_preview_access_gate(streamlit_module: Any = None) -> Dict[str, Any]:
    """
    Render the access gate if Streamlit is supplied; always return a dictionary.

    Returning a dictionary keeps this function easy to inspect from bare Python
    check scripts and avoids Streamlit dependency issues during tests.
    """
    model = build_phase3f_customer_preview_access_gate()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader(PHASE3F_5_PREVIEW_MODE_LABEL)
    st.caption("Protected preview gate. Ordinary Customer view remains disabled.")
    st.warning("This is a protected preview gate, not a public Customer-view release.")

    for section in data["sections"]:
        st.markdown(f"**{section['name']}** — {section['status']}")
        st.write(section["description"])

    st.markdown("**Guardrails**")
    for guardrail in data["guardrails"]:
        st.write(f"- {guardrail}")

    return data
