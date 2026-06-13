"""
phase3g_public_customer_route_smoke_test.py

Phase 3G-5 public Customer-view route smoke-test model.

This module does not enable the public Customer view. It provides a small,
import-safe model used by the Phase 3G-5 checkpoint to verify that the public
route remains staged, protected, and ready for a later explicit activation step.
"""

PHASE3G_5_PUBLIC_ROUTE_SMOKE_TEST_READY = "PHASE3G_5_PUBLIC_ROUTE_SMOKE_TEST_READY"
PHASE3G_5_PUBLIC_CUSTOMER_ENABLED = False
PHASE3G_5_PROTECTED_PREVIEW_REQUIRED = True
PHASE3G_5_PUBLIC_RELEASE_DECISION = "DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET"

CUSTOMER_FACING_LABELS = [
    "Current price",
    "Strike",
    "Premium",
    "Breakeven",
    "Max profit",
    "Downside cushion",
    "Assignment zone",
]

ROUTE_SMOKE_TESTS = [
    "Dashboard syntax remains valid.",
    "Public Customer route helper is staged.",
    "Public Customer view remains disabled.",
    "Protected preview remains required before public exposure.",
    "Phase 3D, Phase 3E, Phase 3F, and Phase 3G markers remain detectable.",
]

PUBLIC_RELEASE_GUARDRAILS = [
    "Do not enable public Customer view until a dedicated activation package passes.",
    "Do not expose developer-only diagnostics to ordinary Customer view.",
    "Keep payoff language customer-facing and non-technical where possible.",
    "Keep warning and risk language visible near the payoff workflow.",
    "Require browser verification before any public release switch is changed.",
]

PROMOTION_CRITERIA = [
    "Protected preview route passes import and render checks.",
    "Public route readiness marker is present in the dashboard.",
    "Customer view has not been prematurely enabled.",
    "Prior Phase 3E and Phase 3F completion reports are available.",
    "Browser visual checklist is current.",
]


class Phase3GPublicRouteSmokeTestModel:
    """Simple render model with a stable to_dict contract."""

    def __init__(self):
        self.marker = PHASE3G_5_PUBLIC_ROUTE_SMOKE_TEST_READY
        self.public_customer_enabled = PHASE3G_5_PUBLIC_CUSTOMER_ENABLED
        self.protected_preview_required = PHASE3G_5_PROTECTED_PREVIEW_REQUIRED
        self.public_release_decision = PHASE3G_5_PUBLIC_RELEASE_DECISION
        self.customer_facing_labels = list(CUSTOMER_FACING_LABELS)
        self.route_smoke_tests = list(ROUTE_SMOKE_TESTS)
        self.guardrails = list(PUBLIC_RELEASE_GUARDRAILS)
        self.promotion_criteria = list(PROMOTION_CRITERIA)

    def to_dict(self):
        return {
            "marker": self.marker,
            "public_customer_enabled": self.public_customer_enabled,
            "protected_preview_required": self.protected_preview_required,
            "public_release_decision": self.public_release_decision,
            "customer_facing_labels": list(self.customer_facing_labels),
            "route_smoke_tests": list(self.route_smoke_tests),
            "guardrails": list(self.guardrails),
            "promotion_criteria": list(self.promotion_criteria),
        }


def build_public_route_smoke_test_model():
    """Build the Phase 3G-5 smoke-test model."""
    return Phase3GPublicRouteSmokeTestModel()


def render_public_route_smoke_test(streamlit_module=None):
    """Render through Streamlit when supplied; otherwise return a dictionary."""
    model = build_public_route_smoke_test_model()
    data = model.to_dict()

    if streamlit_module is None:
        return data

    st = streamlit_module
    st.subheader("Phase 3G-5 Public Customer-view Route Smoke Test")
    st.caption("Public Customer view remains disabled. This is a release-readiness checkpoint only.")
    st.write("Release decision:", data["public_release_decision"])
    st.write("Public Customer enabled:", data["public_customer_enabled"])
    st.write("Protected preview required:", data["protected_preview_required"])
    st.markdown("### Customer-facing labels")
    for label in data["customer_facing_labels"]:
        st.write(f"- {label}")
    st.markdown("### Guardrails")
    for guardrail in data["guardrails"]:
        st.warning(guardrail)
    return data
