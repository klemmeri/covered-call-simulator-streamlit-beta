"""
phase3g_public_customer_pre_activation_verification.py

Phase 3G-3 public Customer-view pre-activation verification model.

This module defines a conservative, customer-release pre-activation checklist
for the Covered Call Simulator paid dashboard. It deliberately does not enable
public Customer-view access. It only describes and verifies the conditions that
must remain true before a later guarded activation step.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


PHASE3G_3_PRE_ACTIVATION_READY = "PHASE3G_3_PRE_ACTIVATION_READY"
PHASE3G_3_PUBLIC_CUSTOMER_ENABLED = False
PHASE3G_3_PROTECTED_PREVIEW_REQUIRED = True


class Phase3GPreActivationVerificationModel:
    """Plain Python render model with a stable to_dict API."""

    def __init__(self) -> None:
        self.marker = PHASE3G_3_PRE_ACTIVATION_READY
        self.title = "Phase 3G-3 public Customer-view pre-activation verification"
        self.public_customer_enabled = PHASE3G_3_PUBLIC_CUSTOMER_ENABLED
        self.protected_preview_required = PHASE3G_3_PROTECTED_PREVIEW_REQUIRED
        self.status = "pre_activation_only"
        self.sections = [
            "Customer-facing payoff workflow is present",
            "Protected preview remains the required review path",
            "Ordinary Customer view remains disabled for Phase 3G",
            "Public activation requires a later explicit release checkpoint",
        ]
        self.release_requirements = [
            "Dashboard imports without syntax or runtime errors.",
            "Phase 3D integrated overlay markers remain present.",
            "Phase 3E customer payoff workbench markers remain present.",
            "Phase 3F protected preview markers remain present.",
            "Phase 3G public-release planning markers remain present.",
            "Customer-facing payoff labels remain available.",
            "Risk, warning, and assignment-zone language remain available.",
            "Public Customer-view enablement remains False until the explicit activation checkpoint.",
        ]
        self.guardrails = [
            "Do not expose developer-only controls in ordinary Customer view.",
            "Do not enable public Customer view from this checkpoint.",
            "Do not remove Phase 3D or Phase 3E dashboard safeguards.",
            "Do not treat regime/model output as an oracle; keep guidance scenario-based.",
        ]
        self.customer_labels = [
            "current price",
            "strike",
            "premium",
            "breakeven",
            "max profit",
            "downside cushion",
            "assignment zone",
            "warning",
        ]
        self.next_step = "Phase 3G-4 guarded public Customer-view activation installer"

    def to_dict(self) -> dict[str, Any]:
        return {
            "marker": self.marker,
            "title": self.title,
            "public_customer_enabled": self.public_customer_enabled,
            "protected_preview_required": self.protected_preview_required,
            "status": self.status,
            "sections": list(self.sections),
            "release_requirements": list(self.release_requirements),
            "guardrails": list(self.guardrails),
            "customer_labels": list(self.customer_labels),
            "next_step": self.next_step,
        }


def build_phase3g_3_pre_activation_model() -> Phase3GPreActivationVerificationModel:
    """Build the Phase 3G-3 pre-activation model."""
    return Phase3GPreActivationVerificationModel()


def render_phase3g_3_pre_activation_verification(streamlit_module: Any | None = None) -> dict[str, Any]:
    """Render the pre-activation model or return it as a dictionary.

    Returning a dictionary when Streamlit is absent keeps the function safe for
    bare PyCharm checkpoint runs.
    """
    model = build_phase3g_3_pre_activation_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader(data["title"])
    st.info("Pre-activation only. Public Customer view remains disabled.")
    st.write("Protected preview required:", data["protected_preview_required"])
    st.write("Public Customer enabled:", data["public_customer_enabled"])

    st.markdown("### Release requirements")
    for item in data["release_requirements"]:
        st.write(f"- {item}")

    st.markdown("### Guardrails")
    for item in data["guardrails"]:
        st.warning(item)

    return data


if __name__ == "__main__":
    import json

    print(json.dumps(render_phase3g_3_pre_activation_verification(), indent=2))
