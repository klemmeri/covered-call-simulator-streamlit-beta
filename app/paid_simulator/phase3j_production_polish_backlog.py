"""
phase3j_production_polish_backlog.py

Phase 3J-1 production polish backlog for the Covered Call Simulator.

This module defines the first production-polish planning gate after Phase 3I
customer workflow verification. It does not modify dashboard behavior. It
creates a structured, customer-facing launch-readiness backlog for the next
phase of development.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


READY_MARKER = "PHASE3J_1_PRODUCTION_POLISH_BACKLOG_READY"
RELEASE_DECISION = "PHASE3J_1_PRODUCTION_POLISH_BACKLOG_CREATED_NO_DASHBOARD_CHANGE"


def build_phase3j_production_polish_backlog() -> dict[str, Any]:
    """Return the Phase 3J-1 production polish backlog model."""
    backlog_items = [
        {
            "area": "Customer workflow",
            "priority": "High",
            "item": "Review the activated payoff workflow in the browser with a typical customer setup.",
            "acceptance": "Customer can identify current price, strike, premium, breakeven, max profit, downside cushion, assignment zone, and warnings without developer guidance.",
        },
        {
            "area": "Wording polish",
            "priority": "High",
            "item": "Simplify any remaining technical language in customer-facing explanations.",
            "acceptance": "Explanations remain accurate but avoid developer/test vocabulary.",
        },
        {
            "area": "Risk disclosure",
            "priority": "High",
            "item": "Confirm assignment, downside, capped upside, and estimate/not-guarantee language remains visible in the activated workflow.",
            "acceptance": "Risk language appears before or near any customer-facing payoff interpretation.",
        },
        {
            "area": "Export workflow",
            "priority": "Medium",
            "item": "Verify saved setup, reload, scenario refresh, and export labels are clear to a first-time user.",
            "acceptance": "A customer can save and recover a setup without needing to inspect developer output folders.",
        },
        {
            "area": "Visual layout",
            "priority": "Medium",
            "item": "Polish spacing, section order, and metric-card grouping for the public customer route.",
            "acceptance": "The workflow reads from setup inputs to payoff interpretation to risk warnings to save/export actions.",
        },
        {
            "area": "Regression safety",
            "priority": "High",
            "item": "Preserve Phase 3D, Phase 3E, Phase 3F, Phase 3G, Phase 3H, and Phase 3I checkpoint reports and markers.",
            "acceptance": "Production polish does not break the developer view, customer activation state, or prior verification outputs.",
        },
    ]

    guardrails = [
        "Do not remove Developer-view diagnostics until the customer route has a separate production-only entry point.",
        "Do not weaken covered-call risk warnings for a cleaner appearance.",
        "Do not present scenario estimates as forecasts or guarantees.",
        "Do not change dashboard routing without creating a timestamped backup first.",
        "Keep customer wording plain, but keep the math and risk interpretation correct.",
    ]

    return {
        "marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "phase": "Phase 3J-1",
        "title": "Production polish backlog",
        "dashboard_modified": False,
        "public_customer_view_status": "controlled activation remains in place from Phase 3H",
        "backlog_items": backlog_items,
        "guardrails": guardrails,
        "next_recommended_phase": "Phase 3J-2 customer layout polish plan",
    }


def render_phase3j_production_polish_backlog(streamlit_module: Any | None = None) -> dict[str, Any]:
    """Render with Streamlit if supplied; otherwise return the model dictionary."""
    model = build_phase3j_production_polish_backlog()
    st = streamlit_module
    if st is None:
        return model

    st.subheader("Phase 3J-1 — Production polish backlog")
    st.caption(model["release_decision"])
    st.write("This planning gate does not modify the dashboard.")

    for item in model["backlog_items"]:
        st.markdown(f"**{item['priority']} — {item['area']}**")
        st.write(item["item"])
        st.caption(f"Acceptance: {item['acceptance']}")

    st.warning("Guardrails remain active: risk language must stay visible and scenario estimates must not be presented as guarantees.")
    return model


def write_phase3j_outputs(project_root: str | Path) -> dict[str, str]:
    """Write Phase 3J-1 report artifacts."""
    root = Path(project_root)
    reports_dir = root / "outputs" / "reports" / "paid_simulator"
    tables_dir = root / "outputs" / "tables" / "paid_simulator"
    reports_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    model = build_phase3j_production_polish_backlog()
    report_path = reports_dir / "phase3j_1_production_polish_backlog_report.txt"
    csv_path = tables_dir / "phase3j_1_production_polish_backlog.csv"
    decision_path = reports_dir / "phase3j_1_production_polish_release_decision.txt"

    lines = [
        "Phase 3J-1 Production Polish Backlog",
        "=" * 80,
        f"Marker: {model['marker']}",
        f"Release decision: {model['release_decision']}",
        "",
        "Backlog items:",
    ]
    for index, item in enumerate(model["backlog_items"], start=1):
        lines.extend([
            f"{index}. [{item['priority']}] {item['area']}",
            f"   Item: {item['item']}",
            f"   Acceptance: {item['acceptance']}",
        ])
    lines.extend(["", "Guardrails:"])
    for guardrail in model["guardrails"]:
        lines.append(f"- {guardrail}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    csv_lines = ["area,priority,item,acceptance"]
    for item in model["backlog_items"]:
        csv_lines.append(
            ",".join(
                '"' + str(item[field]).replace('"', '""') + '"'
                for field in ("area", "priority", "item", "acceptance")
            )
        )
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    decision_path.write_text(model["release_decision"] + "\n", encoding="utf-8")

    return {
        "report": str(report_path),
        "csv": str(csv_path),
        "decision": str(decision_path),
    }
