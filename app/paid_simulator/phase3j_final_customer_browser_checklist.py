"""
phase3j_final_customer_browser_checklist.py

Phase 3J-3 final customer browser checklist model for the Covered Call Simulator.

This module is intentionally dashboard-safe. It builds a plain dictionary model
that can be rendered in Streamlit or written to Markdown by the checkpoint script.
No dashboard code is modified here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


READY_MARKER = "PHASE3J_3_FINAL_CUSTOMER_BROWSER_CHECKLIST_READY"
RELEASE_DECISION = "PHASE3J_3_FINAL_CUSTOMER_BROWSER_CHECKLIST_CREATED_NO_DASHBOARD_CHANGE"


CUSTOMER_BROWSER_CHECKS = [
    {
        "section": "Dashboard launch",
        "check": "Dashboard opens without a red traceback.",
        "expected": "The Streamlit app loads normally.",
    },
    {
        "section": "Customer workflow visibility",
        "check": "Customer-facing payoff workflow is visible after controlled activation.",
        "expected": "The workflow appears in the intended customer-facing path.",
    },
    {
        "section": "Setup inputs",
        "check": "Current price, strike, premium, and share/contract assumptions are understandable.",
        "expected": "A non-technical customer can identify the required inputs.",
    },
    {
        "section": "Payoff labels",
        "check": "Breakeven, max profit, downside cushion, and assignment zone are clearly labeled.",
        "expected": "The labels are customer-facing rather than developer-facing.",
    },
    {
        "section": "Risk warnings",
        "check": "Assignment risk, downside risk, capped upside, and estimate/not-guarantee language are visible.",
        "expected": "Risk language is direct and not hidden in developer notes.",
    },
    {
        "section": "Save/reload/export",
        "check": "Save setup, reload setup, refresh scenario overlay, and export summary actions are visible or staged.",
        "expected": "The workflow can support repeatable customer use.",
    },
    {
        "section": "Scenario overlay",
        "check": "Scenario updates do not expose developer-only controls.",
        "expected": "Only customer-safe assumptions and results are shown.",
    },
    {
        "section": "Developer protections",
        "check": "Developer/test sections remain separated from the customer workflow.",
        "expected": "Customer path does not show Phase labels or internal checkpoint language.",
    },
    {
        "section": "Overall customer readability",
        "check": "The workflow can be understood without knowing Python, Streamlit, or option-model internals.",
        "expected": "The page reads like a customer product feature, not a test harness.",
    },
]


def build_final_customer_browser_checklist_model() -> dict[str, Any]:
    """Return the Phase 3J-3 checklist model as a plain dictionary."""
    return {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_changed": False,
        "phase": "Phase 3J-3",
        "title": "Final Customer Browser Checklist",
        "summary": (
            "Final manual browser checklist for the activated customer-facing "
            "covered-call payoff workflow."
        ),
        "browser_checks": list(CUSTOMER_BROWSER_CHECKS),
        "customer_facing_terms": [
            "current price",
            "strike",
            "premium",
            "breakeven",
            "max profit",
            "downside cushion",
            "assignment zone",
            "warning",
            "capped upside",
            "assignment risk",
            "downside risk",
            "estimate",
        ],
        "manual_dashboard_command": "streamlit run app\\paid_simulator\\config_form_app.py",
    }


def render_final_customer_browser_checklist(streamlit_module: Any | None = None) -> dict[str, Any]:
    """
    Render the checklist if Streamlit is supplied; otherwise return the model.

    The fallback path is deliberately a plain dictionary so checkpoint scripts can
    call this function in bare Python without Streamlit context warnings becoming
    functional failures.
    """
    model = build_final_customer_browser_checklist_model()

    if streamlit_module is None:
        return model

    st = streamlit_module
    st.subheader(model["title"])
    st.write(model["summary"])
    st.info("Use this checklist after launching the Streamlit dashboard in a browser.")

    for idx, item in enumerate(model["browser_checks"], start=1):
        st.markdown(f"**{idx}. {item['section']}**")
        st.write(item["check"])
        st.caption(item["expected"])

    return model


def write_browser_checklist_markdown(output_path: str | Path) -> Path:
    """Write the browser checklist to a Markdown file and return the path."""
    model = build_final_customer_browser_checklist_model()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Phase 3J-3 Final Customer Browser Checklist",
        "",
        f"Ready marker: `{model['ready_marker']}`",
        f"Release decision: `{model['release_decision']}`",
        "",
        "Run the dashboard:",
        "",
        f"```text\n{model['manual_dashboard_command']}\n```",
        "",
        "## Manual browser checks",
        "",
    ]

    for idx, item in enumerate(model["browser_checks"], start=1):
        lines.extend(
            [
                f"### {idx}. {item['section']}",
                "",
                f"Check: {item['check']}",
                "",
                f"Expected: {item['expected']}",
                "",
            ]
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# Backward-compatible aliases for checker variations.
build_checklist_model = build_final_customer_browser_checklist_model
render_checklist = render_final_customer_browser_checklist
