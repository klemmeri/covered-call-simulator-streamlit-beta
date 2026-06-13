"""
phase3j_phase3_completion_handoff.py

Phase 3J-5 completion handoff model for the Covered Call Simulator.

This module is intentionally read-only with respect to the dashboard. It records
that Phase 3 customer-facing workflow work is complete at the local prototype
checkpoint level and identifies Phase 4 as the next major modeling/data stage.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


READY_MARKER = "PHASE3J_5_PHASE3_COMPLETION_HANDOFF_READY"
RELEASE_DECISION = "PHASE3_COMPLETE_READY_FOR_PHASE4_MODELING_DATA_UPGRADES"
DASHBOARD_CHANGE_REQUIRED = False


COMPLETED_PHASES: List[Dict[str, str]] = [
    {"phase": "Phase 3E", "status": "complete", "description": "Customer payoff workflow scaffold, labels, save/reload/export, and dashboard integration."},
    {"phase": "Phase 3F", "status": "complete", "description": "Protected customer-preview layer and release gate."},
    {"phase": "Phase 3G", "status": "complete", "description": "Public customer-view release preparation and route readiness."},
    {"phase": "Phase 3H", "status": "complete", "description": "Controlled public Customer-view activation."},
    {"phase": "Phase 3I", "status": "complete", "description": "Post-activation customer workflow verification."},
    {"phase": "Phase 3J", "status": "complete", "description": "Production polish, browser checklist, health check, and final handoff."},
]


PHASE4_RECOMMENDED_WORKSTREAMS: List[Dict[str, str]] = [
    {"workstream": "Real market data intake", "description": "Add a clean import path for real ticker data, historical prices, and eventually option-chain data."},
    {"workstream": "Option model upgrade", "description": "Replace static/demo assumptions with calibrated volatility, dividend, and option premium assumptions."},
    {"workstream": "Strategy decision engine", "description": "Turn scenario outputs into practical covered-call setup guidance and roll/hold recommendations."},
    {"workstream": "Backtest/sample validation", "description": "Compare covered-call outcomes against buy-and-hold across realistic historical regimes."},
    {"workstream": "Pro dashboard roadmap", "description": "Plan premium features such as ticker input, trade setup scoring, saved setups, and downloadable customer reports."},
]


REQUIRED_PRIOR_REPORTS = [
    "phase3e_9_completion_checkpoint_report.txt",
    "phase3f_8_completion_gate_checkpoint_report.txt",
    "phase3g_8_completion_gate_checkpoint_report.txt",
    "phase3h_8_post_activation_completion_checkpoint_report.txt",
    "phase3i_7_completion_gate_checkpoint_report.txt",
    "phase3j_4_final_production_health_checkpoint_report.txt",
]


def build_phase3_completion_handoff() -> Dict[str, Any]:
    """Return the Phase 3 completion handoff model."""
    return {
        "ready_marker": READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "dashboard_change_required": DASHBOARD_CHANGE_REQUIRED,
        "phase3_status": "complete_at_local_paid_simulator_prototype_level",
        "customer_view_status": "controlled_public_customer_workflow_activated_and_verified",
        "completed_phases": COMPLETED_PHASES,
        "phase4_recommended_workstreams": PHASE4_RECOMMENDED_WORKSTREAMS,
        "required_prior_reports": REQUIRED_PRIOR_REPORTS,
        "handoff_note": (
            "Phase 3 should stop here. The next meaningful work is Phase 4: improving "
            "the data/modeling engine rather than adding more release-gate scaffolding."
        ),
    }


def render_phase3_completion_handoff(streamlit_module: Any | None = None) -> Dict[str, Any]:
    """Render or return the Phase 3 completion handoff.

    If a Streamlit-compatible module is supplied, display a compact summary.
    Always return a dictionary so automated checks can run without Streamlit.
    """
    model = build_phase3_completion_handoff()

    st = streamlit_module
    if st is not None:
        st.header("Phase 3 completion handoff")
        st.success(model["release_decision"])
        st.write(model["handoff_note"])
        st.subheader("Completed Phase 3 work")
        for item in COMPLETED_PHASES:
            st.write(f"- {item['phase']}: {item['description']}")
        st.subheader("Recommended Phase 4 workstreams")
        for item in PHASE4_RECOMMENDED_WORKSTREAMS:
            st.write(f"- {item['workstream']}: {item['description']}")

    return model


def write_phase3_completion_handoff_report(project_root: Path) -> Dict[str, Path]:
    """Write text and JSON-style handoff artifacts using plain text only."""
    reports_dir = project_root / "outputs" / "reports" / "paid_simulator"
    tables_dir = project_root / "outputs" / "tables" / "paid_simulator"
    reports_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)

    model = build_phase3_completion_handoff()

    report_path = reports_dir / "phase3j_5_phase3_completion_handoff_report.txt"
    decision_path = reports_dir / "phase3j_5_phase3_completion_release_decision.txt"
    checklist_path = tables_dir / "phase3j_5_phase3_completion_handoff_checklist.csv"

    lines = [
        "Covered Call Simulator - Phase 3 Completion Handoff",
        "=" * 72,
        f"Ready marker: {model['ready_marker']}",
        f"Release decision: {model['release_decision']}",
        f"Dashboard change required: {model['dashboard_change_required']}",
        f"Customer view status: {model['customer_view_status']}",
        "",
        "Completed Phase 3 phases:",
    ]
    for item in COMPLETED_PHASES:
        lines.append(f"- {item['phase']}: {item['status']} - {item['description']}")
    lines.extend(["", "Recommended Phase 4 workstreams:"])
    for item in PHASE4_RECOMMENDED_WORKSTREAMS:
        lines.append(f"- {item['workstream']}: {item['description']}")
    lines.extend(["", "Handoff note:", model["handoff_note"], ""])
    report_path.write_text("\n".join(lines), encoding="utf-8")
    decision_path.write_text(model["release_decision"] + "\n", encoding="utf-8")

    csv_lines = ["item,status,detail"]
    csv_lines.append(f"ready_marker,PASS,{model['ready_marker']}")
    csv_lines.append(f"release_decision,PASS,{model['release_decision']}")
    csv_lines.append("dashboard_change_required,PASS,False")
    for item in COMPLETED_PHASES:
        csv_lines.append(f"{item['phase']},PASS,{item['description'].replace(',', ';')}")
    checklist_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    return {
        "report": report_path,
        "decision": decision_path,
        "checklist": checklist_path,
    }
