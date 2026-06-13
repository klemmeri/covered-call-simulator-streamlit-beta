"""
phase3f_customer_preview_release_readiness.py

Phase 3F-6 customer-preview release-readiness model for the Covered Call Simulator.

This module does not enable the ordinary Customer view. It summarizes whether the
protected customer-preview workflow has enough guardrails to be considered ready
for a later explicit promotion step.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

PHASE3F_6_RELEASE_READINESS_MARKER = "PHASE3F_6_CUSTOMER_PREVIEW_RELEASE_READINESS_READY"
PHASE3F_6_PUBLIC_CUSTOMER_ENABLED = False
PHASE3F_6_PROTECTED_PREVIEW_ALLOWED = True

REQUIRED_REPORTS = [
    "outputs/reports/paid_simulator/phase3e_9_completion_checkpoint_report.txt",
    "outputs/reports/paid_simulator/phase3f_3_customer_preview_route_checkpoint_report.txt",
    "outputs/reports/paid_simulator/phase3f_4_browser_preview_checklist.md",
]

REQUIRED_MODULES = [
    "app/paid_simulator/phase3f_customer_preview_access_gate.py",
    "app/paid_simulator/phase3f_customer_preview_route.py",
    "app/paid_simulator/phase3f_customer_preview_shell.py",
    "app/paid_simulator/phase3e_customer_workbench_streamlit_panel.py",
]

READINESS_GUARDRAILS = [
    "ordinary Customer view remains disabled",
    "protected customer-preview mode is explicitly separated from public release",
    "risk and warning language must remain visible",
    "save, reload, refresh, and export workflow labels must remain staged",
    "Phase 3E/3F preview work must not be promoted without a separate release checkpoint",
]

CUSTOMER_LABELS = [
    "current price",
    "strike",
    "premium",
    "breakeven",
    "max profit",
    "downside cushion",
    "assignment zone",
    "warning",
]


def _exists(project_root: Path, relative_path: str) -> bool:
    return (project_root / relative_path).exists()


def build_release_readiness_model(project_root: str | Path | None = None) -> dict[str, Any]:
    if project_root is None:
        root = Path(__file__).resolve().parents[2]
    else:
        root = Path(project_root)

    modules = [
        {"path": path, "exists": _exists(root, path)}
        for path in REQUIRED_MODULES
    ]
    reports = [
        {"path": path, "exists": _exists(root, path)}
        for path in REQUIRED_REPORTS
    ]

    all_modules_present = all(item["exists"] for item in modules)
    all_reports_present = all(item["exists"] for item in reports)

    public_customer_enabled = PHASE3F_6_PUBLIC_CUSTOMER_ENABLED
    protected_preview_allowed = PHASE3F_6_PROTECTED_PREVIEW_ALLOWED

    ready_for_later_controlled_promotion = (
        all_modules_present
        and all_reports_present
        and protected_preview_allowed
        and not public_customer_enabled
        and len(READINESS_GUARDRAILS) >= 4
    )

    return {
        "marker": PHASE3F_6_RELEASE_READINESS_MARKER,
        "phase": "Phase 3F-6",
        "title": "Customer-preview release-readiness gate",
        "public_customer_enabled": public_customer_enabled,
        "protected_preview_allowed": protected_preview_allowed,
        "ready_for_later_controlled_promotion": ready_for_later_controlled_promotion,
        "modules": modules,
        "reports": reports,
        "guardrails": list(READINESS_GUARDRAILS),
        "customer_labels": list(CUSTOMER_LABELS),
        "next_step": "Phase 3F-7 should be an explicit controlled customer-preview enablement step, not an automatic public release.",
    }


def render_release_readiness_summary(project_root: str | Path | None = None, streamlit_module=None) -> dict[str, Any]:
    model = build_release_readiness_model(project_root)
    st = streamlit_module
    if st is not None:
        st.subheader(model["title"])
        st.caption("Protected preview remains separate from ordinary Customer view.")
        st.write("Public customer enabled:", model["public_customer_enabled"])
        st.write("Protected preview allowed:", model["protected_preview_allowed"])
        st.write("Ready for later controlled promotion:", model["ready_for_later_controlled_promotion"])
        st.write("Guardrails:")
        for guardrail in model["guardrails"]:
            st.write(f"- {guardrail}")
    return model
