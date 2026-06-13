"""
phase3g_public_customer_route_readiness.py

Phase 3G-4 public Customer-view route-readiness model.

This module prepares the public Customer-view route structure for the Covered
Call Simulator paid dashboard while keeping actual public activation disabled.
It is a readiness layer only, not a release switch.
"""

from __future__ import annotations

from typing import Any


PHASE3G_4_PUBLIC_ROUTE_READY = "PHASE3G_4_PUBLIC_ROUTE_READY"
PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = False
PHASE3G_4_PROTECTED_PREVIEW_REQUIRED = True
PHASE3G_4_REQUIRES_EXPLICIT_RELEASE = True


class Phase3GPublicRouteReadinessModel:
    """Plain Python route-readiness model with a stable to_dict API."""

    def __init__(self) -> None:
        self.marker = PHASE3G_4_PUBLIC_ROUTE_READY
        self.title = "Phase 3G-4 public Customer-view route readiness"
        self.status = "route_ready_public_disabled"
        self.public_customer_enabled = PHASE3G_4_PUBLIC_CUSTOMER_ENABLED
        self.protected_preview_required = PHASE3G_4_PROTECTED_PREVIEW_REQUIRED
        self.requires_explicit_release = PHASE3G_4_REQUIRES_EXPLICIT_RELEASE
        self.route_name = "customer_payoff_workbench_public_candidate"
        self.route_scope = "Public-candidate route structure; ordinary Customer view remains disabled."
        self.customer_sections = [
            "Covered-call setup inputs",
            "Payoff summary",
            "Scenario overlay",
            "Warnings and guardrails",
            "Save, reload, refresh, and export workflow",
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
        self.release_requirements = [
            "Protected customer-preview route has passed visual verification.",
            "Public Customer view remains disabled until a separate activation checkpoint.",
            "Customer-facing labels are present and not developer-only labels.",
            "Risk and assignment-zone language are visible before public release.",
            "Dashboard imports without syntax or runtime errors.",
            "Phase 3D, Phase 3E, and Phase 3F markers remain intact.",
            "Regime/model descriptions remain scenario guidance, not market oracles.",
        ]
        self.guardrails = [
            "Do not expose Developer-view controls to ordinary Customer view.",
            "Do not enable public Customer view in Phase 3G-4.",
            "Do not bypass protected-preview review.",
            "Do not remove backup/rollback capability before dashboard edits.",
            "Do not present simulated payoff results as guaranteed outcomes.",
        ]
        self.next_step = "Phase 3G-5 public Customer-view activation switch rehearsal"

    def to_dict(self) -> dict[str, Any]:
        return {
            "marker": self.marker,
            "title": self.title,
            "status": self.status,
            "public_customer_enabled": self.public_customer_enabled,
            "protected_preview_required": self.protected_preview_required,
            "requires_explicit_release": self.requires_explicit_release,
            "route_name": self.route_name,
            "route_scope": self.route_scope,
            "customer_sections": list(self.customer_sections),
            "customer_labels": list(self.customer_labels),
            "release_requirements": list(self.release_requirements),
            "guardrails": list(self.guardrails),
            "next_step": self.next_step,
        }


def build_phase3g_4_public_route_readiness_model() -> Phase3GPublicRouteReadinessModel:
    """Build the Phase 3G-4 public route-readiness model."""
    return Phase3GPublicRouteReadinessModel()


def render_phase3g_4_public_route_readiness(streamlit_module: Any | None = None) -> dict[str, Any]:
    """Render the public route-readiness model or return it as a dictionary."""
    model = build_phase3g_4_public_route_readiness_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader(data["title"])
    st.info("Route-readiness only. Public Customer view remains disabled.")
    st.write("Public Customer enabled:", data["public_customer_enabled"])
    st.write("Protected preview required:", data["protected_preview_required"])
    st.write("Requires explicit release:", data["requires_explicit_release"])

    st.markdown("### Customer route sections")
    for item in data["customer_sections"]:
        st.write(f"- {item}")

    st.markdown("### Release requirements")
    for item in data["release_requirements"]:
        st.write(f"- {item}")

    st.markdown("### Guardrails")
    for item in data["guardrails"]:
        st.warning(item)

    return data


if __name__ == "__main__":
    import json

    print(json.dumps(render_phase3g_4_public_route_readiness(), indent=2))
