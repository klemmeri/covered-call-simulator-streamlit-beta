"""
phase6_dashboard_mode_selector_patch.py

Phase 6-3 dashboard mode-selector patch support for the Covered Call Simulator.

This repaired version avoids dataclasses so the module can be imported safely by
Python 3.13 dynamic-import checkpoint scripts. Synthetic scenario mode remains
the default. Historical-import mode remains explicit-only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import pandas as pd


PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY = (
    "PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY"
)

PHASE6_3_RELEASE_DECISION = (
    "PHASE6_3_CONTROLLED_DASHBOARD_MODE_SELECTOR_PATCH_READY"
)

DEFAULT_MODE = "synthetic"
HISTORICAL_MODE = "historical_import"

MODE_LABELS = {
    DEFAULT_MODE: "Synthetic scenarios",
    HISTORICAL_MODE: "Imported historical data",
}

MODE_DESCRIPTIONS = {
    DEFAULT_MODE: (
        "Use generated scenario paths. This remains the default dashboard mode."
    ),
    HISTORICAL_MODE: (
        "Use imported historical price data as a scenario input. Historical paths "
        "are examples of what happened in the past, not forecasts."
    ),
}

CUSTOMER_CAUTION_TEXT = (
    "Historical data mode uses imported past price behavior as an input scenario. "
    "It should not be interpreted as a forecast or regime oracle."
)


def normalize_dashboard_mode(mode: Any) -> str:
    """
    Normalize a requested dashboard mode.

    Unknown values fall back to synthetic mode. This protects existing customer
    behavior and prevents historical import from becoming the accidental default.
    """

    if mode is None:
        return DEFAULT_MODE

    requested = str(mode).strip().lower()

    aliases = {
        "synthetic": DEFAULT_MODE,
        "synthetic_scenarios": DEFAULT_MODE,
        "synthetic scenarios": DEFAULT_MODE,
        "default": DEFAULT_MODE,
        "historical": HISTORICAL_MODE,
        "historical_import": HISTORICAL_MODE,
        "historical import": HISTORICAL_MODE,
        "imported historical data": HISTORICAL_MODE,
    }

    return aliases.get(requested, DEFAULT_MODE)


def build_dashboard_mode_selection(requested_mode: Any = None) -> dict[str, Any]:
    """Return a plain dictionary describing the selected dashboard data mode."""

    selected_mode = normalize_dashboard_mode(requested_mode)
    return {
        "selected_mode": selected_mode,
        "selected_label": MODE_LABELS[selected_mode],
        "is_default": selected_mode == DEFAULT_MODE,
        "historical_mode_explicit_only": True,
        "customer_caution_text": CUSTOMER_CAUTION_TEXT,
    }


def build_phase6_3_summary(requested_mode: Any = None) -> dict[str, Any]:
    selection = build_dashboard_mode_selection(requested_mode)

    summary = {
        "ready_marker": PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY,
        "release_decision": PHASE6_3_RELEASE_DECISION,
        "phase": "Phase 6-3",
        "checkpoint_name": "Controlled dashboard mode selector patch",
        "dashboard_patch_required": True,
        "dashboard_patch_applied_by_check": True,
        "dashboard_file_target": "app\\paid_simulator\\config_form_app.py",
        "dashboard_change_type": "controlled_append_only_integration_block",
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_mode_falls_back_to_synthetic": (
            normalize_dashboard_mode("unknown") == DEFAULT_MODE
        ),
        "default_mode": DEFAULT_MODE,
        "historical_mode": HISTORICAL_MODE,
        "available_modes_count": len(MODE_LABELS),
        "customer_caution_text": CUSTOMER_CAUTION_TEXT,
    }
    summary.update(selection)
    return summary


def build_phase6_3_mode_table() -> pd.DataFrame:
    rows = []
    for mode, label in MODE_LABELS.items():
        rows.append(
            {
                "mode": mode,
                "label": label,
                "is_default": mode == DEFAULT_MODE,
                "explicit_only": mode == HISTORICAL_MODE,
                "description": MODE_DESCRIPTIONS[mode],
            }
        )
    return pd.DataFrame(rows)


def render_phase6_3_dashboard_mode_selector(default_mode: Any = DEFAULT_MODE) -> dict[str, Any]:
    """
    Optional Streamlit renderer for the paid dashboard.

    This function is safe to import even when Streamlit is unavailable. When
    Streamlit is unavailable, it returns the normalized default selection.
    """

    normalized_default = normalize_dashboard_mode(default_mode)

    try:
        import streamlit as st  # type: ignore
    except Exception:
        return build_dashboard_mode_selection(normalized_default)

    labels_by_mode = MODE_LABELS.copy()
    mode_by_label = {label: mode for mode, label in labels_by_mode.items()}
    label_options = [MODE_LABELS[DEFAULT_MODE], MODE_LABELS[HISTORICAL_MODE]]
    default_index = 0 if normalized_default == DEFAULT_MODE else 1

    selected_label = st.radio(
        "Data mode",
        options=label_options,
        index=default_index,
        help=(
            "Synthetic scenarios remain the default. Imported historical data is "
            "an explicit scenario input, not a forecast."
        ),
    )
    selected_mode = mode_by_label.get(selected_label, DEFAULT_MODE)

    if selected_mode == HISTORICAL_MODE:
        st.caption(CUSTOMER_CAUTION_TEXT)

    return build_dashboard_mode_selection(selected_mode)


def write_phase6_3_outputs(project_root: Path | None = None) -> dict[str, Any]:
    if project_root is None:
        project_root = Path(__file__).resolve().parents[2]

    output_table_dir = project_root / "outputs" / "tables" / "paid_simulator"
    output_report_dir = project_root / "outputs" / "reports" / "paid_simulator"
    output_table_dir.mkdir(parents=True, exist_ok=True)
    output_report_dir.mkdir(parents=True, exist_ok=True)

    summary = build_phase6_3_summary()
    mode_table = build_phase6_3_mode_table()

    mode_table_path = output_table_dir / "phase6_3_dashboard_mode_selector_modes.csv"
    summary_csv_path = output_table_dir / "phase6_3_dashboard_mode_selector_patch_summary.csv"
    json_path = output_report_dir / "phase6_3_dashboard_mode_selector_patch.json"
    report_path = output_report_dir / "phase6_3_dashboard_mode_selector_patch_report.txt"

    mode_table.to_csv(mode_table_path, index=False)
    pd.DataFrame([summary]).to_csv(summary_csv_path, index=False)

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    report_lines = [
        "Phase 6-3 controlled dashboard mode selector patch",
        "=" * 72,
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        f"Dashboard patch target: {summary['dashboard_file_target']}",
        "",
        "Customer caution text:",
        summary["customer_caution_text"],
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    summary["output_paths"] = {
        "mode_table_csv": str(mode_table_path),
        "summary_csv": str(summary_csv_path),
        "json": str(json_path),
        "report": str(report_path),
    }
    return summary


if __name__ == "__main__":
    write_phase6_3_outputs()
