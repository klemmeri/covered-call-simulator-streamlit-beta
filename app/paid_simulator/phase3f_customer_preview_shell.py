"""
phase3f_customer_preview_shell.py

Protected Customer Preview Shell for the Covered Call Simulator paid dashboard.

Phase 3F-2 purpose
------------------
This module prepares a customer-preview version of the Phase 3E payoff workbench
without exposing it to the ordinary Customer view. It is intentionally separate
from config_form_app.py so the existing dashboard remains protected until a later
controlled promotion step.

Design rules
------------
1. Customer preview is not the same as public customer release.
2. The shell exposes customer-facing labels and guidance only.
3. Developer/test language remains outside the customer-facing body.
4. Risk warnings remain visible.
5. The module can be imported and checked without a Streamlit runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


PHASE3F_PREVIEW_TITLE = "Customer preview: Covered-call payoff workbench"
PHASE3F_PREVIEW_STATUS = "Protected preview only"
PHASE3F_PREVIEW_MARKER = "PHASE3F_2_CUSTOMER_PREVIEW_SHELL_READY"
CUSTOMER_PREVIEW_NOT_PUBLIC_MARKER = "CUSTOMER_PREVIEW_NOT_PUBLIC_RELEASE"


@dataclass(frozen=True)
class CustomerPreviewMetric:
    """One customer-facing metric card for the preview shell."""

    label: str
    value: str
    explanation: str


@dataclass(frozen=True)
class CustomerPreviewAction:
    """One customer-facing action label for the preview shell."""

    label: str
    purpose: str
    enabled_in_preview: bool


@dataclass(frozen=True)
class CustomerPreviewShell:
    """Serializable render model for the protected customer preview shell."""

    title: str
    status: str
    marker: str
    protection_marker: str
    protection_note: str
    customer_summary: str
    setup_labels: List[str]
    payoff_metrics: List[CustomerPreviewMetric]
    warnings: List[str]
    actions: List[CustomerPreviewAction]
    release_gate_notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_customer_preview_shell() -> CustomerPreviewShell:
    """Build the protected Phase 3F customer-preview shell model."""

    setup_labels = [
        "Current price",
        "Call strike",
        "Option premium received",
        "Days to expiration",
        "Share quantity",
        "Estimated assignment zone",
    ]

    payoff_metrics = [
        CustomerPreviewMetric(
            label="Breakeven",
            value="current price - premium received",
            explanation="The approximate stock price where the premium offsets the initial downside move.",
        ),
        CustomerPreviewMetric(
            label="Max profit",
            value="strike gain + premium received",
            explanation="The approximate best-case outcome if the stock finishes at or above the call strike.",
        ),
        CustomerPreviewMetric(
            label="Downside cushion",
            value="premium received",
            explanation="The amount of decline absorbed by the option premium before the position begins losing versus entry price.",
        ),
        CustomerPreviewMetric(
            label="Assignment zone",
            value="stock price above short-call strike",
            explanation="The area where shares may be called away at expiration or near expiration.",
        ),
    ]

    warnings = [
        "Covered calls do not eliminate downside risk in the stock.",
        "Large stock declines can exceed the premium received.",
        "High premium may indicate higher implied risk, not free income.",
        "Assignment can occur when the short call is in the money, especially near expiration or dividend events.",
    ]

    actions = [
        CustomerPreviewAction(
            label="Refresh payoff scenario",
            purpose="Recalculate the payoff summary after the setup assumptions change.",
            enabled_in_preview=True,
        ),
        CustomerPreviewAction(
            label="Save setup",
            purpose="Store the current setup for later review.",
            enabled_in_preview=True,
        ),
        CustomerPreviewAction(
            label="Reload saved setup",
            purpose="Restore a previously saved covered-call setup.",
            enabled_in_preview=True,
        ),
        CustomerPreviewAction(
            label="Export summary",
            purpose="Create a customer-readable setup summary for records or review.",
            enabled_in_preview=True,
        ),
    ]

    release_gate_notes = [
        "This preview shell is protected and is not yet public Customer view functionality.",
        "Promotion requires a later checkpoint that explicitly enables the customer route.",
        "Developer-view Phase 3E integration should remain intact while this shell is reviewed.",
        "Customer-facing labels and warnings must remain present before promotion.",
    ]

    return CustomerPreviewShell(
        title=PHASE3F_PREVIEW_TITLE,
        status=PHASE3F_PREVIEW_STATUS,
        marker=PHASE3F_PREVIEW_MARKER,
        protection_marker=CUSTOMER_PREVIEW_NOT_PUBLIC_MARKER,
        protection_note="Protected customer preview only. Do not expose as the ordinary Customer view until a later release checkpoint passes.",
        customer_summary="Preview the main payoff features of a covered-call setup using plain customer-facing labels.",
        setup_labels=setup_labels,
        payoff_metrics=payoff_metrics,
        warnings=warnings,
        actions=actions,
        release_gate_notes=release_gate_notes,
    )


def render_customer_preview_shell(streamlit_module: Optional[Any] = None) -> CustomerPreviewShell:
    """Render the preview shell when Streamlit is available; otherwise return the model.

    The return value is always the model so check scripts can validate behavior in
    normal Python execution.
    """

    model = build_customer_preview_shell()
    st = streamlit_module

    if st is None:
        return model

    st.subheader(model.title)
    st.caption(model.status)
    st.info(model.protection_note)
    st.write(model.customer_summary)

    st.markdown("#### Setup inputs")
    for label in model.setup_labels:
        st.write(f"- {label}")

    st.markdown("#### Payoff summary")
    for metric in model.payoff_metrics:
        st.write(f"**{metric.label}:** {metric.value}")
        st.caption(metric.explanation)

    st.markdown("#### Risk warnings")
    for warning in model.warnings:
        st.warning(warning)

    st.markdown("#### Preview workflow actions")
    for action in model.actions:
        status = "enabled" if action.enabled_in_preview else "disabled"
        st.write(f"**{action.label}** ({status}) - {action.purpose}")

    return model


__all__ = [
    "PHASE3F_PREVIEW_TITLE",
    "PHASE3F_PREVIEW_STATUS",
    "PHASE3F_PREVIEW_MARKER",
    "CUSTOMER_PREVIEW_NOT_PUBLIC_MARKER",
    "CustomerPreviewMetric",
    "CustomerPreviewAction",
    "CustomerPreviewShell",
    "build_customer_preview_shell",
    "render_customer_preview_shell",
]
