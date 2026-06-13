"""
phase3g_public_customer_final_pre_activation_gate.py

Phase 3G-6 final pre-activation decision gate for the Covered Call Simulator.

This module intentionally does not enable the public Customer view. It builds a
plain-Python decision model used by the checkpoint script to verify that the
public customer payoff workflow remains staged, protected, and ready for a later
explicit activation step.
"""

PHASE3G_6_FINAL_PRE_ACTIVATION_GATE_READY = "PHASE3G_6_FINAL_PRE_ACTIVATION_GATE_READY"
PHASE3G_6_PUBLIC_CUSTOMER_ENABLED = False
PHASE3G_6_PROTECTED_PREVIEW_REQUIRED = True
PHASE3G_6_RELEASE_DECISION = "DO_NOT_ENABLE_PUBLIC_CUSTOMER_VIEW_YET"


CUSTOMER_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
]

RELEASE_REQUIREMENTS = [
    "Phase 3E customer payoff workbench checkpoint complete",
    "Phase 3F protected customer-preview checkpoint complete",
    "Phase 3G public-route smoke test complete",
    "Customer-facing labels present",
    "Warning/risk language present",
    "Dashboard syntax remains valid",
    "Public Customer view remains disabled until explicit release",
]

GUARDRAILS = [
    "Do not enable ordinary Customer view during Phase 3G-6.",
    "Keep protected preview as the only customer-like route.",
    "Require a separate installer/checkpoint for public activation.",
    "Preserve Phase 3D, Phase 3E, and Phase 3F markers.",
    "Keep warning/risk language visible before any customer release.",
]

NEXT_STEPS = [
    "Run the dashboard manually in Streamlit.",
    "Confirm Customer view remains clean.",
    "Confirm Developer/protected preview still renders the payoff workflow.",
    "Only after visual confirmation, create a separate explicit activation package.",
]


class Phase3GFinalPreActivationGateModel:
    """Plain-Python render model with deterministic serialization."""

    def __init__(self):
        self.marker = PHASE3G_6_FINAL_PRE_ACTIVATION_GATE_READY
        self.title = "Phase 3G-6 final pre-activation decision gate"
        self.public_customer_enabled = PHASE3G_6_PUBLIC_CUSTOMER_ENABLED
        self.protected_preview_required = PHASE3G_6_PROTECTED_PREVIEW_REQUIRED
        self.release_decision = PHASE3G_6_RELEASE_DECISION
        self.customer_labels = list(CUSTOMER_LABELS)
        self.release_requirements = list(RELEASE_REQUIREMENTS)
        self.guardrails = list(GUARDRAILS)
        self.next_steps = list(NEXT_STEPS)

    def to_dict(self):
        return {
            "marker": self.marker,
            "title": self.title,
            "public_customer_enabled": self.public_customer_enabled,
            "protected_preview_required": self.protected_preview_required,
            "release_decision": self.release_decision,
            "customer_labels": list(self.customer_labels),
            "release_requirements": list(self.release_requirements),
            "guardrails": list(self.guardrails),
            "next_steps": list(self.next_steps),
        }


def build_phase3g_6_final_pre_activation_gate_model():
    """Return the Phase 3G-6 final pre-activation gate model."""
    return Phase3GFinalPreActivationGateModel()


def render_phase3g_6_final_pre_activation_gate(streamlit_module=None):
    """Render the gate when Streamlit is available; otherwise return a dict."""
    model = build_phase3g_6_final_pre_activation_gate_model()
    data = model.to_dict()

    st = streamlit_module
    if st is None:
        return data

    st.subheader(data["title"])
    st.warning("Public Customer view remains disabled. This is a release gate, not activation.")
    st.write(f"Release decision: {data['release_decision']}")
    st.write("Customer-facing labels")
    st.write(data["customer_labels"])
    st.write("Guardrails")
    for item in data["guardrails"]:
        st.write(f"- {item}")
    st.write("Release requirements")
    for item in data["release_requirements"]:
        st.write(f"- {item}")
    return data
