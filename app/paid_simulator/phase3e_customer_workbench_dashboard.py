"""
phase3e_customer_workbench_dashboard.py

Developer-view dashboard adapter for the Phase 3E customer payoff workbench.

This module is intentionally isolated from the main Streamlit dashboard.  It
provides a single render function that can be imported by config_form_app.py
when the Phase 3E workbench is ready to appear as a Developer-view tab.

Design goals
------------
1. Keep the customer view protected.
2. Keep Phase 3E workbench rendering separate from test/check scripts.
3. Reuse the Phase 3E view-model layer rather than duplicating calculations.
4. Fail gracefully if Streamlit is unavailable during command-line checks.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping


TAB_TITLE = "Phase 3E customer payoff workbench"
CUSTOMER_PROTECTION_NOTE = (
    "Developer-view only. Do not expose this tab in the Customer view until the "
    "Phase 3E completion checkpoint passes."
)


@dataclass(frozen=True)
class DashboardSection:
    """Simple dashboard section descriptor used by tests and Streamlit rendering."""

    title: str
    body: str
    section_type: str = "info"


@dataclass(frozen=True)
class DashboardRenderModel:
    """Serializable view model for the Phase 3E dashboard tab."""

    tab_title: str
    protection_note: str
    sections: List[DashboardSection]
    source_modules: List[str]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "tab_title": self.tab_title,
            "protection_note": self.protection_note,
            "sections": [section.__dict__ for section in self.sections],
            "source_modules": list(self.source_modules),
        }


def _import_workbench_view_model() -> Any:
    """Import the Phase 3E-6 view-model module lazily.

    Lazy import keeps command-line checks robust even when this file is imported
    outside the full dashboard runtime.
    """

    try:
        from app.paid_simulator import phase3e_customer_workbench_view_model

        return phase3e_customer_workbench_view_model
    except Exception:
        try:
            import phase3e_customer_workbench_view_model

            return phase3e_customer_workbench_view_model
        except Exception as exc:  # pragma: no cover - surfaced by check script
            raise RuntimeError(
                "Could not import phase3e_customer_workbench_view_model. "
                "Install/pass Phase 3E-6 before enabling the dashboard tab."
            ) from exc


def build_dashboard_render_model() -> DashboardRenderModel:
    """Build the non-Streamlit render model for the Developer-view tab."""

    sections = [
        DashboardSection(
            title="Purpose",
            body=(
                "Customer-ready covered-call payoff workflow for current price, "
                "strike, premium, breakeven, max profit, downside cushion, "
                "assignment-zone guidance, setup save/reload, and scenario refresh."
            ),
            section_type="info",
        ),
        DashboardSection(
            title="Protection boundary",
            body=CUSTOMER_PROTECTION_NOTE,
            section_type="warning",
        ),
        DashboardSection(
            title="Expected workflow",
            body=(
                "Open or enter a covered-call setup, review customer-facing payoff "
                "labels, inspect warnings, save/export the setup, reload it, then "
                "refresh one-click scenario overlays."
            ),
            section_type="info",
        ),
        DashboardSection(
            title="Integration status",
            body=(
                "This adapter is ready to be imported into the Developer-view tab "
                "area of config_form_app.py. It should not be called from Customer view."
            ),
            section_type="success",
        ),
    ]

    return DashboardRenderModel(
        tab_title=TAB_TITLE,
        protection_note=CUSTOMER_PROTECTION_NOTE,
        sections=sections,
        source_modules=[
            "phase3e_customer_payoff_workflow",
            "phase3e_customer_setup_io",
            "phase3e_customer_payoff_labels",
            "phase3e_customer_scenario_overlay",
            "phase3e_customer_payoff_workbench",
            "phase3e_customer_workbench_view_model",
        ],
    )


def render_phase3e_customer_workbench_dashboard(st: Any | None = None) -> DashboardRenderModel:
    """Render the Phase 3E workbench tab when Streamlit is available.

    Parameters
    ----------
    st:
        Optional Streamlit-like object.  Passing this explicitly makes the
        function easy to test.  If omitted, the function tries to import
        streamlit.  If Streamlit is unavailable, the render model is still
        returned without raising.

    Returns
    -------
    DashboardRenderModel
        The same model used for rendering, useful for checks and tests.
    """

    model = build_dashboard_render_model()

    if st is None:
        try:
            import streamlit as st  # type: ignore
        except Exception:
            return model

    st.subheader(model.tab_title)
    st.warning(model.protection_note)

    for section in model.sections:
        if section.section_type == "warning":
            st.warning(section.body)
        elif section.section_type == "success":
            st.success(section.body)
        else:
            st.info(section.body)

    try:
        view_model_module = _import_workbench_view_model()
        if hasattr(view_model_module, "build_customer_workbench_view_model"):
            customer_model = view_model_module.build_customer_workbench_view_model()
            st.caption("Phase 3E view-model loaded successfully.")
            if hasattr(customer_model, "as_dict"):
                st.json(customer_model.as_dict())
        else:
            st.caption("Phase 3E view-model module found; render hook name not detected.")
    except Exception as exc:
        st.error(str(exc))

    return model


def get_dashboard_integration_snippet() -> str:
    """Return the exact integration snippet for the Developer-view tab area.

    This is documentation/check material only.  It is not executed by this
    package, which avoids an unsafe blind edit of config_form_app.py.
    """

    return '''
from app.paid_simulator.phase3e_customer_workbench_dashboard import (
    render_phase3e_customer_workbench_dashboard,
)

# File to edit when enabling the tab: app/paid_simulator/config_form_app.py
# Inside the Developer-view tab block only:
with st.expander("Phase 3E customer payoff workbench", expanded=False):
    render_phase3e_customer_workbench_dashboard(st)
'''.strip()
