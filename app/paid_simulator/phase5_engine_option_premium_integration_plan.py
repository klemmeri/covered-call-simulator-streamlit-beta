"""
phase5_engine_option_premium_integration_plan.py

Phase 5-19 checkpoint for the Covered Call Simulator paid-simulator track.

Purpose
-------
Create an engine-level plan for integrating imported option-chain premiums into
the core simulator flow while preserving the existing synthetic default behavior.

This checkpoint is intentionally add-only. It does not patch strategy.py,
portfolio.py, simulator.py, price_paths.py, or the Streamlit dashboard.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PHASE_READY_MARKER = "PHASE5_19_ENGINE_OPTION_PREMIUM_INTEGRATION_PLAN_READY"
RELEASE_DECISION = "PHASE5_19_ENGINE_OPTION_PREMIUM_INTEGRATION_PLAN_CREATED_NO_DASHBOARD_CHANGE"
SOURCE_MODE = "engine_option_premium_integration_plan"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

PHASE5_19_SUMMARY_CSV = OUTPUT_TABLE_DIR / "phase5_19_engine_option_premium_integration_plan_summary.csv"
PHASE5_19_TOUCHPOINTS_CSV = OUTPUT_TABLE_DIR / "phase5_19_option_premium_engine_touchpoints.csv"
PHASE5_19_PATCH_ORDER_CSV = OUTPUT_TABLE_DIR / "phase5_19_option_premium_patch_order.csv"
PHASE5_19_PRIOR_ARTIFACTS_CSV = OUTPUT_TABLE_DIR / "phase5_19_prior_option_artifact_status.csv"
PHASE5_19_JSON = OUTPUT_REPORT_DIR / "phase5_19_engine_option_premium_integration_plan.json"
PHASE5_19_REPORT = OUTPUT_REPORT_DIR / "phase5_19_engine_option_premium_integration_plan_report.txt"

PRIOR_ARTIFACTS = [
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_5_best_covered_call_candidate.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_6_premium_model_calibration_rows.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_6_premium_model_calibration_summary.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_18_historical_mode_engine_regression_summary.csv",
]

ENGINE_TOUCHPOINTS = [
    {
        "file": "app/strategy.py",
        "role": "covered_call_rule",
        "integration_need": "Allow a selected imported premium to override or calibrate the synthetic premium estimate when explicit historical/import mode is requested.",
        "default_behavior": "Synthetic premium model remains default.",
        "risk_level": "medium",
    },
    {
        "file": "app/portfolio.py",
        "role": "path_cycle_accounting",
        "integration_need": "Carry the selected option-chain premium into cycle-level accounting without changing existing synthetic-mode output fields.",
        "default_behavior": "Existing cycle accounting remains unchanged unless imported premium mode is explicit.",
        "risk_level": "medium",
    },
    {
        "file": "app/simulator.py",
        "role": "engine_orchestration",
        "integration_need": "Pass an optional premium source/mode flag through the SimulationEngine configuration path.",
        "default_behavior": "Existing SimulationEngine(config).run() remains compatible.",
        "risk_level": "medium",
    },
    {
        "file": "app/config.py",
        "role": "configuration_contract",
        "integration_need": "Add optional fields for premium_source_mode and imported_premium_path, with synthetic default fallback.",
        "default_behavior": "No existing configuration should be required to add fields.",
        "risk_level": "low",
    },
    {
        "file": "app/paid_simulator/config_form_app.py",
        "role": "dashboard_later",
        "integration_need": "Expose premium-source choice later in Phase 6 only after engine regression passes.",
        "default_behavior": "No dashboard change in Phase 5-19.",
        "risk_level": "deferred",
    },
]

PATCH_ORDER = [
    {
        "step": 1,
        "checkpoint": "Phase 5-20",
        "action": "Close Phase 5 with a completion handoff before patching option premium logic.",
        "reason": "Avoid extending Phase 5 indefinitely and keep option-premium patching as a clean Phase 6/early Phase 6A decision.",
    },
    {
        "step": 2,
        "checkpoint": "Phase 6-1 or Phase 6A-1",
        "action": "Create an option-premium integration candidate for strategy.py without replacing the live file.",
        "reason": "strategy.py is the first natural premium-selection touchpoint.",
    },
    {
        "step": 3,
        "checkpoint": "Phase 6-2 or Phase 6A-2",
        "action": "Run synthetic-default regression after the strategy candidate.",
        "reason": "Verify synthetic-mode behavior is unchanged before promotion.",
    },
    {
        "step": 4,
        "checkpoint": "Phase 6 dashboard integration after engine regression",
        "action": "Expose a simple premium-source choice only after engine behavior is stable.",
        "reason": "Customer workflow should remain simple and not expose internal scaffolding.",
    },
]


def _safe_read_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        return int(len(pd.read_csv(path)))
    except Exception:
        return 0


def _prior_artifact_status() -> pd.DataFrame:
    rows = []
    for path in PRIOR_ARTIFACTS:
        rows.append(
            {
                "artifact": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "exists": bool(path.exists()),
                "row_count": _safe_read_rows(path),
            }
        )
    return pd.DataFrame(rows)


def _write_report(summary: dict[str, Any], touchpoints: pd.DataFrame, patch_order: pd.DataFrame, prior: pd.DataFrame) -> None:
    lines = [
        "Phase 5-19 Engine-Level Option-Premium Integration Plan",
        "=" * 70,
        "",
        f"Ready marker: {summary['ready_marker']}",
        f"Release decision: {summary['release_decision']}",
        f"Source mode: {summary['source_mode']}",
        f"Dashboard change required: {summary['dashboard_change_required']}",
        f"Core engine patched: {summary['core_engine_patched']}",
        f"Synthetic default preserved: {summary['synthetic_default_preserved']}",
        f"Historical mode explicit only: {summary['historical_mode_explicit_only']}",
        "",
        "Integration conclusion:",
        summary["integration_conclusion"],
        "",
        "Engine touchpoints:",
    ]
    for _, row in touchpoints.iterrows():
        lines.append(f"- {row['file']}: {row['integration_need']}")
    lines.extend(["", "Recommended patch order:"])
    for _, row in patch_order.iterrows():
        lines.append(f"{row['step']}. {row['checkpoint']}: {row['action']}")
    lines.extend(["", "Prior artifact status:"])
    for _, row in prior.iterrows():
        lines.append(f"- {row['artifact']}: exists={row['exists']}, rows={row['row_count']}")
    PHASE5_19_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_phase5_19_summary() -> dict[str, Any]:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    prior_df = _prior_artifact_status()
    touchpoints_df = pd.DataFrame(ENGINE_TOUCHPOINTS)
    patch_order_df = pd.DataFrame(PATCH_ORDER)

    candidate_artifact_exists = bool((PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_5_best_covered_call_candidate.csv").exists())
    calibration_artifact_exists = bool((PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase4_6_premium_model_calibration_summary.csv").exists())

    summary = {
        "ready_marker": PHASE_READY_MARKER,
        "release_decision": RELEASE_DECISION,
        "source_mode": SOURCE_MODE,
        "dashboard_change_required": False,
        "core_engine_patched": False,
        "live_core_engine_replaced": False,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "option_premium_integration_plan_created": True,
        "candidate_option_artifact_exists": candidate_artifact_exists,
        "calibration_artifact_exists": calibration_artifact_exists,
        "prior_artifact_rows": int(len(prior_df)),
        "engine_touchpoint_rows": int(len(touchpoints_df)),
        "recommended_patch_order_rows": int(len(patch_order_df)),
        "next_recommended_checkpoint": "PHASE5_20_COMPLETION_HANDOFF",
        "overall_status": "PASS",
        "integration_conclusion": (
            "Imported option-chain premium integration is ready to be planned as a controlled engine change, "
            "but it should not be exposed in the dashboard until synthetic-default regression and engine-level "
            "premium tests pass. Phase 5 should close after this plan and the Phase 5 completion handoff."
        ),
    }

    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(PHASE5_19_SUMMARY_CSV, index=False)
    touchpoints_df.to_csv(PHASE5_19_TOUCHPOINTS_CSV, index=False)
    patch_order_df.to_csv(PHASE5_19_PATCH_ORDER_CSV, index=False)
    prior_df.to_csv(PHASE5_19_PRIOR_ARTIFACTS_CSV, index=False)

    PHASE5_19_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_report(summary, touchpoints_df, patch_order_df, prior_df)

    return summary


if __name__ == "__main__":
    result = build_phase5_19_summary()
    print(json.dumps(result, indent=2))
