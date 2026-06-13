"""
phase3h_public_activation_route_smoke_test.py

Phase 3H-3 smoke-test model for the guarded public activation route.

This module is intentionally conservative. It confirms that the public
Customer-view route is staged for review while the public Customer view remains
disabled. It is safe to import outside Streamlit and returns plain dictionaries
for checkpoint compatibility.
"""

PHASE3H_3_PUBLIC_ACTIVATION_SMOKE_TEST_READY = "PHASE3H_3_PUBLIC_ACTIVATION_SMOKE_TEST_READY"
PHASE3H_3_PUBLIC_CUSTOMER_ENABLED = False
PHASE3H_3_RELEASE_DECISION = "PHASE3H_3_ROUTE_SMOKE_TEST_PASS_PUBLIC_CUSTOMER_VIEW_DISABLED"

CUSTOMER_FACING_LABELS = [
    "current price",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]

GUARDRAILS = [
    "Public Customer view remains disabled until an explicit activation checkpoint passes.",
    "Protected preview remains the only customer-like route during Phase 3H-3.",
    "Risk and warning language must remain visible before public release.",
    "Customer-facing labels must be present before promotion.",
    "Dashboard syntax and prior phase markers must remain valid.",
]

SECTIONS = [
    {
        "name": "Route status",
        "purpose": "Confirm that the public activation route is staged but disabled.",
    },
    {
        "name": "Customer-facing payoff labels",
        "purpose": "Confirm current price, breakeven, max profit, downside cushion, assignment zone, and warning labels.",
    },
    {
        "name": "Guardrails",
        "purpose": "Confirm public activation remains blocked until an explicit release step.",
    },
    {
        "name": "Release decision",
        "purpose": "Record the conservative decision to keep public Customer view disabled.",
    },
]


def build_phase3h_3_smoke_test_model():
    """Return a dict-compatible smoke-test model."""
    return {
        "ready_marker": PHASE3H_3_PUBLIC_ACTIVATION_SMOKE_TEST_READY,
        "marker": PHASE3H_3_PUBLIC_ACTIVATION_SMOKE_TEST_READY,
        "public_customer_enabled": PHASE3H_3_PUBLIC_CUSTOMER_ENABLED,
        "customer_enabled": PHASE3H_3_PUBLIC_CUSTOMER_ENABLED,
        "release_decision": PHASE3H_3_RELEASE_DECISION,
        "customer_facing_labels": list(CUSTOMER_FACING_LABELS),
        "guardrails": list(GUARDRAILS),
        "sections": list(SECTIONS),
        "summary": "Phase 3H-3 smoke test passed with public Customer view disabled.",
    }


def build_smoke_test_model():
    """Compatibility alias used by checkpoint scripts."""
    return build_phase3h_3_smoke_test_model()


def build_render_model():
    """Compatibility alias used by checkpoint scripts."""
    return build_phase3h_3_smoke_test_model()


def render_phase3h_3_activation_route_smoke_test(streamlit_module=None):
    """
    Render or return the smoke-test model.

    If a Streamlit-like module is provided, write a small status panel. In bare
    Python/checkpoint mode, return the dictionary model directly.
    """
    model = build_phase3h_3_smoke_test_model()

    if streamlit_module is None:
        return model

    st = streamlit_module
    if hasattr(st, "subheader"):
        st.subheader("Phase 3H-3 public activation route smoke test")
    if hasattr(st, "warning"):
        st.warning("Public Customer view remains disabled. This is a protected smoke test only.")
    if hasattr(st, "write"):
        st.write("Release decision:", model["release_decision"])
        st.write("Guardrails:", model["guardrails"])
        st.write("Customer-facing labels:", model["customer_facing_labels"])

    return model


def render_smoke_test(streamlit_module=None):
    """Compatibility alias used by checkpoint scripts."""
    return render_phase3h_3_activation_route_smoke_test(streamlit_module=streamlit_module)


def render_phase3h_public_activation_route_smoke_test(streamlit_module=None):
    """Compatibility alias used by checkpoint scripts."""
    return render_phase3h_3_activation_route_smoke_test(streamlit_module=streamlit_module)
