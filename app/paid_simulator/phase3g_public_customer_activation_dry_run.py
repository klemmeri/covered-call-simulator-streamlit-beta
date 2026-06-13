"""
phase3g_public_customer_activation_dry_run.py

Phase 3G-7 — Public Customer-view Activation Dry Run.

This module models the public customer activation decision without enabling
public customer access. It is intentionally conservative: the public route
remains disabled unless a later explicit activation package changes the flag.
"""

from __future__ import annotations

PHASE3G_7_PUBLIC_ACTIVATION_DRY_RUN_READY = "PHASE3G_7_PUBLIC_ACTIVATION_DRY_RUN_READY"
PHASE3G_7_PUBLIC_CUSTOMER_ENABLED = False
PHASE3G_7_PROTECTED_PREVIEW_REQUIRED = True
PHASE3G_7_RELEASE_DECISION = "DRY_RUN_ONLY_DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW"


class Phase3GActivationDryRunModel:
    """Plain Python render model used by the Phase 3G-7 check script."""

    def __init__(self):
        self.marker = PHASE3G_7_PUBLIC_ACTIVATION_DRY_RUN_READY
        self.phase = "Phase 3G-7"
        self.title = "Public Customer-view Activation Dry Run"
        self.public_customer_enabled = PHASE3G_7_PUBLIC_CUSTOMER_ENABLED
        self.protected_preview_required = PHASE3G_7_PROTECTED_PREVIEW_REQUIRED
        self.release_decision = PHASE3G_7_RELEASE_DECISION
        self.customer_labels = [
            "Current price",
            "Strike",
            "Premium",
            "Breakeven",
            "Max profit",
            "Downside cushion",
            "Assignment zone",
        ]
        self.guardrails = [
            "Public Customer view remains disabled during this dry run.",
            "Protected preview remains required before public exposure.",
            "Dashboard syntax must remain valid before any activation package.",
            "Risk and warning language must remain visible in customer-facing panels.",
            "No activation is allowed without an explicit later enablement step.",
        ]
        self.activation_requirements = [
            "Phase 3E completion report available.",
            "Phase 3F protected preview completion report available.",
            "Phase 3G pre-activation and smoke-test reports available.",
            "Customer-facing labels verified.",
            "Ordinary Customer view protection verified.",
            "Manual browser review completed before final activation.",
        ]
        self.dry_run_steps = [
            "Read all prior release-gate reports.",
            "Confirm public customer flag remains False.",
            "Confirm protected preview route remains available.",
            "Confirm customer labels and warning language are present.",
            "Write dry-run release decision report.",
        ]

    def to_dict(self):
        return {
            "marker": self.marker,
            "phase": self.phase,
            "title": self.title,
            "public_customer_enabled": self.public_customer_enabled,
            "protected_preview_required": self.protected_preview_required,
            "release_decision": self.release_decision,
            "customer_labels": list(self.customer_labels),
            "guardrails": list(self.guardrails),
            "activation_requirements": list(self.activation_requirements),
            "dry_run_steps": list(self.dry_run_steps),
        }


def build_phase3g_public_activation_dry_run_model():
    """Build the Phase 3G-7 activation dry-run model."""
    return Phase3GActivationDryRunModel()


def render_phase3g_public_activation_dry_run(streamlit_module=None):
    """Render or return the dry-run model.

    In check scripts, streamlit_module is None and this returns a dictionary.
    In Streamlit, the same function writes a conservative preview panel.
    """
    model = build_phase3g_public_activation_dry_run_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader(data["title"])
    st.warning("Dry run only. Public Customer view remains disabled.")
    st.write("Release decision:", data["release_decision"])
    st.write("Public Customer enabled:", data["public_customer_enabled"])
    st.write("Protected preview required:", data["protected_preview_required"])

    st.markdown("### Customer-facing labels")
    for label in data["customer_labels"]:
        st.write(f"- {label}")

    st.markdown("### Guardrails")
    for item in data["guardrails"]:
        st.write(f"- {item}")

    st.markdown("### Activation dry-run steps")
    for item in data["dry_run_steps"]:
        st.write(f"- {item}")

    return data
