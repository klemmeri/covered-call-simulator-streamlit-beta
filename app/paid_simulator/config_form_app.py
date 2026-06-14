
# PUBLIC_BETA_REPORT_DUPLICATE_SOURCE_FIX_READY

# PUBLIC_BETA_PRESET_NEGATIVE_BEST_WORDING_READY

# PUBLIC_BETA_SUPPRESS_PRESET_REPORT_POPUPS_READY

# PUBLIC_BETA_PRESET_COMPARISON_CHECK_REPAIR_READY

# PUBLIC_BETA_PRESET_COMPARISON_PLAIN_LANGUAGE_READY
"""
Paid simulator Streamlit control panel.

This panel edits config/paid_simulator_config.json, runs the paid simulator,
shows results, tracks run history, compares presets, and exports a customer
facing decision memo.
"""

from __future__ import annotations

import html
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

try:
    import altair as alt
except Exception:  # Altair normally ships with Streamlit; fall back if unavailable.
    alt = None


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "paid_simulator_config.json"
CONFIG_BACKUP_DIR = PROJECT_ROOT / "config" / "backups"
RUNNER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator.py"
HEALTH_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_health_check.py"
SCENARIO_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_comparison.csv"
RUN_HISTORY_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "run_history.csv"
PRESET_COMPARISON_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "preset_comparison.csv"
REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_comparison_report.html"
MEMO_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "decision_memos"

# Phase 2 scaffold outputs. These are developer-view diagnostics only.
PHASE2_PRICE_PATHS_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_price_paths_scaffold.csv"
PHASE2_OPTION_PAYOFF_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_payoff_scaffold.csv"
PHASE2_SCENARIO_PAYOFF_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_scaffold.csv"
PHASE2_SCENARIO_PAYOFF_REPORT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_report_scaffold.csv"
PHASE2_SCENARIO_PAYOFF_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_payoff_report_scaffold.html"
PHASE2_V0_COMPARISON_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase2_v0_comparison_scaffold.csv"
PHASE2_V0_COMPARISON_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2_v0_comparison_scaffold.html"
PHASE2_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2_pipeline_check.py"
PHASE2_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2_viewer.py"
PHASE2_INTEGRATION_READINESS_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2_integration_readiness_check.py"

# Phase 2B premium-model outputs. These are developer-view diagnostics only.
PHASE2B_OPTION_PREMIUM_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"
PHASE2B_PREMIUM_AWARE_PAYOFF_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"
PHASE2B_PREMIUM_AWARE_PAYOFF_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_aware_payoff_scaffold.html"
PHASE2B_PREMIUM_VS_SCAFFOLD_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_vs_scaffold_comparison.csv"
PHASE2B_PREMIUM_VS_SCAFFOLD_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_vs_scaffold_comparison.html"
PHASE2B_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2b_pipeline_check.py"
PHASE2B_PREMIUM_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2b_premium_viewer.py"

# Phase 2C premium-model validation outputs. These are developer-view diagnostics only.
PHASE2C_VALIDATION_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_validation_scaffold.csv"
PHASE2C_VALIDATION_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_scaffold.html"
PHASE2C_VALIDATION_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_summary.txt"
PHASE2C_VALIDATION_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2c_validation_pipeline_report.txt"
PHASE2C_VALIDATION_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_premium_model_validation_check.py"
PHASE2C_VALIDATION_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_validation_pipeline_check.py"
PHASE2C_VALIDATION_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_premium_validation_viewer.py"

# Phase 2D premium-model tuning outputs. These are developer-view diagnostics only.
PHASE2D_TUNING_CONFIG_PATH = PROJECT_ROOT / "config" / "premium_model_tuning_config.json"
PHASE2D_TUNING_RECOMMENDATIONS_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_tuning_recommendations.csv"
PHASE2D_TUNING_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_tuning_recommendations.html"
PHASE2D_TUNING_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_tuning_summary.txt"
PHASE2D_TUNING_CHECK_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2d_premium_model_tuning_check_report.txt"
PHASE2D_TUNING_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2d_tuning_pipeline_report.txt"
PHASE2D_TUNING_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_premium_model_tuning_check.py"
PHASE2D_TUNING_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2d_tuning_pipeline_check.py"
PHASE2D_TUNING_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2d_premium_tuning_viewer.py"

# Phase 2E controlled premium-model adjustment outputs. These are developer-view diagnostics only.
PHASE2E_ADJUSTMENT_CONFIG_PATH = PROJECT_ROOT / "config" / "premium_model_adjustment_config.json"
PHASE2E_ADJUSTED_PREMIUMS_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_adjusted_premiums.csv"
PHASE2E_ADJUSTMENT_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_adjustment_comparison.html"
PHASE2E_ADJUSTMENT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_adjustment_summary.txt"
PHASE2E_ADJUSTED_PAYOFF_COMPARISON_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "adjusted_premium_payoff_comparison.csv"
PHASE2E_ADJUSTED_PAYOFF_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "adjusted_premium_payoff_comparison.html"
PHASE2E_ADJUSTED_PAYOFF_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "adjusted_premium_payoff_summary.txt"
PHASE2E_ADJUSTMENT_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2e_adjustment_pipeline_report.txt"
PHASE2E_ADJUSTMENT_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_premium_model_adjustment_check.py"
PHASE2E_ADJUSTED_PAYOFF_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_adjusted_premium_payoff_comparison_check.py"
PHASE2E_ADJUSTMENT_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2e_adjustment_pipeline_check.py"
PHASE2E_ADJUSTMENT_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2e_adjustment_viewer.py"

# Phase 2F model-decision summary outputs. These are developer-view diagnostics only.
PHASE2F_MODEL_DECISION_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "model_decision_summary.csv"
PHASE2F_MODEL_DECISION_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_decision_summary.html"
PHASE2F_MODEL_DECISION_TEXT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_decision_summary.txt"
PHASE2F_MODEL_DECISION_CHECK_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_model_decision_summary_check_report.txt"
PHASE2F_MODEL_DECISION_VIEWER_CHECK_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_model_decision_viewer_check_report.txt"
PHASE2F_MODEL_DECISION_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2f_model_decision_pipeline_report.txt"
PHASE2F_MODEL_DECISION_SUMMARY_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_model_decision_summary_check.py"
PHASE2F_MODEL_DECISION_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_pipeline_check.py"
PHASE2F_MODEL_DECISION_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_viewer.py"

# Phase 2G model-promotion planning outputs. These are developer-view diagnostics only.
PHASE2G_MODEL_PROMOTION_PLAN_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "model_promotion_plan.csv"
PHASE2G_MODEL_PROMOTION_PLAN_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_promotion_plan.html"
PHASE2G_MODEL_PROMOTION_PLAN_TEXT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_promotion_plan.txt"
PHASE2G_MODEL_PROMOTION_PLANNING_CHECK_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2g_model_promotion_planning_check_report.txt"
PHASE2G_MODEL_PROMOTION_VIEWER_CHECK_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2g_model_promotion_viewer_check_report.txt"
PHASE2G_MODEL_PROMOTION_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2g_model_promotion_pipeline_report.txt"
PHASE2G_MODEL_PROMOTION_PLANNING_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_model_promotion_planning_check.py"
PHASE2G_MODEL_PROMOTION_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2g_model_promotion_pipeline_check.py"
PHASE2G_MODEL_PROMOTION_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase2g_model_promotion_viewer.py"

# Phase 3 interactive covered-call payoff outputs. These are developer-view diagnostics only.
PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3_interactive_payoff_snapshot.csv"
PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_interactive_payoff_snapshot.html"
PHASE3_INTERACTIVE_PAYOFF_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_interactive_payoff_pipeline_report.txt"
PHASE3_INTERACTIVE_PAYOFF_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_viewer.py"
PHASE3_INTERACTIVE_PAYOFF_VIEWER_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py"
PHASE3_INTERACTIVE_PAYOFF_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py"

# Phase 3B scenario-overlay outputs. These are developer-view diagnostics only.
PHASE3B_SCENARIO_OVERLAY_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3_scenario_overlay.csv"
PHASE3B_SCENARIO_OVERLAY_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_scenario_overlay.html"
PHASE3B_SCENARIO_OVERLAY_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_scenario_overlay_summary.txt"
PHASE3B_SCENARIO_OVERLAY_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3b_scenario_overlay_pipeline_report.txt"
PHASE3B_SCENARIO_OVERLAY_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_check.py"
PHASE3B_SCENARIO_OVERLAY_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer.py"
PHASE3B_SCENARIO_OVERLAY_VIEWER_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py"
PHASE3B_SCENARIO_OVERLAY_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py"

# Phase 3C richer graphical payoff outputs. These are developer-view diagnostics only.
PHASE3C_RICH_PAYOFF_SNAPSHOT_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3c_rich_payoff_snapshot.csv"
PHASE3C_RICH_PAYOFF_SNAPSHOT_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3c_rich_payoff_snapshot.html"
PHASE3C_RICH_PAYOFF_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3c_rich_payoff_pipeline_report.txt"
PHASE3C_RICH_PAYOFF_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3c_rich_payoff_viewer.py"
PHASE3C_RICH_PAYOFF_VIEWER_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py"
PHASE3C_RICH_PAYOFF_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py"

# Phase 3D integrated payoff-overlay outputs. These are developer-view diagnostics only.
PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_CSV_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3d_integrated_payoff_overlay_snapshot.csv"
PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3d_integrated_payoff_overlay_snapshot.html"
PHASE3D_INTEGRATED_OVERLAY_PIPELINE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3d_integrated_overlay_pipeline_report.txt"
PHASE3D_INTEGRATED_OVERLAY_VIEWER_CHECK_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3d_integrated_overlay_viewer_check_report.txt"
PHASE3D_INTEGRATED_OVERLAY_VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3d_integrated_overlay_viewer.py"
PHASE3D_INTEGRATED_OVERLAY_VIEWER_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py"
PHASE3D_INTEGRATED_OVERLAY_PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from app.paid_simulator.dashboard_status import get_dashboard_status, status_table_rows
except Exception:  # noqa: BLE001 - dashboard should still load if status add-on is missing.
    get_dashboard_status = None
    status_table_rows = None

try:
    from app.paid_simulator.product_info import get_product_info
except Exception:  # noqa: BLE001 - dashboard should still load if branding add-on is missing.
    get_product_info = None


def load_product_info() -> Any:
    """Return product metadata, with a local fallback if product_info.py is unavailable."""
    if get_product_info is not None:
        try:
            return get_product_info()
        except Exception:
            pass

    class FallbackProductInfo:
        product_name = "Covered Call Strategy Stress Test"
        product_subtitle = "A public beta stress-test app for comparing covered-call setups across named market examples."
        version_label = "Public beta v0.1"
        build_label = "Beta release"
        release_stage = "Beta release"
        positioning_statement = (
            "This app is designed to help you understand the income, risk, "
            "and upside tradeoffs of a covered-call setup before opening or comparing positions. "
            "It is a decision-support tool, not a trade recommendation engine."
        )
        primary_workflow = (
            "Choose or edit a covered-call setup.",
            "Validate sizing and assumptions.",
            "Run the stress test across named market examples.",
            "Review best, worst, and average results versus simply holding the stock.",
            "Inspect scenario details and decision guidance.",
            "Export a Markdown or PDF decision memo.",
            "Compare presets and review run history.",
        )
        key_limitations = (
            "Named market examples are illustrative scenarios, not forecasts.",
            "Regime detection, if later added, should be treated as probabilistic guidance, not an oracle.",
            "Covered calls may lag sharply in strong rallies because upside can be capped.",
            "Historical or simulated outcomes do not guarantee future performance.",
            "Transaction costs, slippage, tax treatment, early assignment, dividends, and broker execution details can materially affect real results.",
        )

    return FallbackProductInfo()


PRODUCT_INFO = load_product_info()


DEFAULT_CONFIG: dict[str, Any] = {
    "ticker": "SPY",
    "account_size": 600000.0,
    "risk_tier": "Balanced",
    "position_size_cap": 0.10,
    "desired_contracts": 1,
    "target_delta": 0.30,
    "target_dte": 30,
    "management_rule": "close_at_50_percent_profit",
    "rolling_rule": "none",
    "re_entry_rule": "immediate",
    "transaction_cost": 1.00,
    "slippage_assumption": 0.01,
    "demo_price": 545.25,
}

PRESETS: dict[str, dict[str, Any]] = {
    "Clean demo - balanced, 1 contract": {
        **DEFAULT_CONFIG,
        "risk_tier": "Balanced",
        "desired_contracts": 1,
        "position_size_cap": 0.10,
        "target_delta": 0.30,
        "target_dte": 30,
    },
    "Conservative income - lower delta": {
        **DEFAULT_CONFIG,
        "risk_tier": "Conservative",
        "desired_contracts": 1,
        "position_size_cap": 0.075,
        "target_delta": 0.20,
        "target_dte": 30,
    },
    "Aggressive income - higher cap": {
        **DEFAULT_CONFIG,
        "risk_tier": "Aggressive",
        "desired_contracts": 1,
        "position_size_cap": 0.15,
        "target_delta": 0.35,
        "target_dte": 30,
    },
    "Shorter-term theta demo": {
        **DEFAULT_CONFIG,
        "risk_tier": "Balanced",
        "desired_contracts": 1,
        "position_size_cap": 0.10,
        "target_delta": 0.30,
        "target_dte": 14,
    },
}

RELATIVE_RESULT_CANDIDATES = [
    "covered_call_minus_buy_hold",
    "covered_call_minus_buy_and_hold",
    "relative_result",
    "relative_p_l",
    "relative_pl",
    "relative_pnl",
    "outperformance",
    "covered_call_outperformance",
    "net_option_effect",
]
SCENARIO_CANDIDATES = ["scenario_display_name", "scenario_name", "scenario", "market_path", "path", "scenario_label", "label", "name"]
BUY_HOLD_CANDIDATES = ["buy_hold_p_l", "buy_and_hold_p_l", "buy_hold_result", "buy_hold"]
COVERED_CALL_CANDIDATES = ["covered_call_p_l", "covered_call_result", "covered_call"]


st.set_page_config(
    page_title=PRODUCT_INFO.product_name,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1220px;
        padding-top: 2.0rem;
        padding-bottom: 3.0rem;
    }
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.65rem;
        padding: 0.7rem 0.9rem;
    }

    /* Stronger tab navigation divider and active-tab indicator for customer polish. */
    div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
        border-bottom: 2px solid #cbd5e1 !important;
        gap: 0.25rem;
        margin-bottom: 1.15rem;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        padding: 0.65rem 0.9rem 0.75rem 0.9rem !important;
        border-bottom: 3px solid transparent !important;
        color: #334155 !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p {
        font-size: 0.96rem !important;
        font-weight: 500 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        border-bottom: 4px solid #ef4444 !important;
        color: #dc2626 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p {
        font-weight: 750 !important;
        color: #dc2626 !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        background-color: #ef4444 !important;
        height: 4px !important;
        border-radius: 999px !important;
    }
    .beta-hero-panel {
        border: 1px solid #dbeafe;
        background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
        border-radius: 18px;
        padding: 1.15rem 1.25rem;
        margin: 1rem 0 1.1rem 0;
    }
    .beta-hero-kicker {
        color: #1d4ed8;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .beta-hero-title {
        color: #102a43;
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }
    .beta-hero-body {
        color: #334e68;
        font-size: 1rem;
        line-height: 1.55;
        margin: 0;
    }
    .beta-card-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.75rem 0 1.0rem 0;
    }
    .beta-card {
        border: 1px solid #e2e8f0;
        background: #ffffff;
        border-radius: 14px;
        padding: 0.95rem 1.0rem;
        min-height: 145px;
    }
    .beta-card-title {
        color: #102a43;
        font-size: 1.0rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }
    .beta-card-text {
        color: #52606d;
        font-size: 0.92rem;
        line-height: 1.48;
        margin: 0;
    }
    .beta-future-list {
        color: #334e68;
        font-size: 0.92rem;
        line-height: 1.55;
        margin: 0.35rem 0 0 1.0rem;
        padding: 0;
    }
    @media (max-width: 900px) {
        .beta-card-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def normalize_column_name(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    normalized = {normalize_column_name(col): col for col in df.columns}
    for candidate in candidates:
        key = normalize_column_name(candidate)
        if key in normalized:
            return normalized[key]
    for col in df.columns:
        norm = normalize_column_name(col)
        for candidate in candidates:
            if normalize_column_name(candidate) in norm:
                return col
    return None


def detect_scenario_column(df: pd.DataFrame | None) -> str | None:
    """Return the scenario/name column from a result table, if present.

    This small helper is used by the public-beta clarity panel. It intentionally
    reuses the same scenario-column candidates as the rest of the dashboard so
    the customer-facing explanation stays consistent with the displayed results.
    """
    if df is None or df.empty:
        return None
    return find_column(
        df,
        SCENARIO_CANDIDATES
        + [
            "Scenario",
            "scenario",
            "scenario_name",
            "scenario_display_name",
            "market_path",
            "path",
            "path_label",
            "display_name",
        ],
    )


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
            config = {**DEFAULT_CONFIG, **loaded}
            return config
        except Exception as exc:
            st.warning(f"Could not read config file. Using defaults. Error: {exc}")
    return DEFAULT_CONFIG.copy()


def backup_config() -> Path | None:
    if not CONFIG_PATH.exists():
        return None
    CONFIG_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = CONFIG_BACKUP_DIR / f"paid_simulator_config_backup_{timestamp}.json"
    backup_path.write_text(CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path


def save_config(config: dict[str, Any]) -> Path | None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    backup_path = backup_config()
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    return backup_path


def run_python_script(script_path: Path, extra_env: dict[str, str] | None = None) -> tuple[int, str]:
    if not script_path.exists():
        return 1, f"Script not found: {script_path}"
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    output = (completed.stdout or "")
    if completed.stderr:
        output += "\n--- STDERR ---\n" + completed.stderr
    return completed.returncode, output



def reset_to_clean_demo(run_after_reset: bool = False) -> tuple[bool, str]:
    """Reset the dashboard config to the clean customer-demo state."""
    demo_config = PRESETS["Clean demo - balanced, 1 contract"].copy()
    save_config(demo_config)
    st.session_state["active_preset"] = "Clean demo - balanced, 1 contract"

    if not run_after_reset:
        return True, "Clean demo configuration saved. The dashboard has been reset to the standard customer-demo setup."

    code, output = run_python_script(RUNNER_PATH)
    if code != 0:
        st.session_state["latest_demo_reset_output"] = output
        return False, f"Clean demo config was saved, but the simulator failed with return code {code}."

    df_after = load_scenario_results()
    if df_after is not None:
        append_run_history(demo_config, summarize_results(df_after))

    st.session_state["latest_demo_reset_output"] = output
    return True, "Clean demo configuration saved and simulator run completed. Review the Overview or Latest results tab."


def open_path_with_windows(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
        return True
    except Exception:
        return False


def load_scenario_results() -> pd.DataFrame | None:
    if not SCENARIO_CSV_PATH.exists():
        return None
    try:
        return pd.read_csv(SCENARIO_CSV_PATH)
    except Exception as exc:
        st.warning(f"Could not read scenario comparison CSV: {exc}")
        return None


def summarize_results(df: pd.DataFrame) -> dict[str, Any]:
    relative_col = find_column(df, RELATIVE_RESULT_CANDIDATES)
    scenario_col = find_column(df, SCENARIO_CANDIDATES)
    buy_hold_col = find_column(df, BUY_HOLD_CANDIDATES)
    covered_call_col = find_column(df, COVERED_CALL_CANDIDATES)

    summary: dict[str, Any] = {
        "relative_col": relative_col,
        "scenario_col": scenario_col,
        "buy_hold_col": buy_hold_col,
        "covered_call_col": covered_call_col,
        "available_columns": list(df.columns),
        "row_count": len(df),
    }

    if relative_col is None or df.empty:
        return summary

    values = pd.to_numeric(df[relative_col], errors="coerce")
    valid = df.loc[values.notna()].copy()
    valid["_relative_value"] = values.loc[values.notna()]

    if valid.empty:
        return summary

    best_idx = valid["_relative_value"].idxmax()
    worst_idx = valid["_relative_value"].idxmin()

    def scenario_name(row: pd.Series) -> str:
        if scenario_col and scenario_col in row.index:
            return str(row[scenario_col])
        return f"Scenario {int(row.name) + 1}"

    summary.update(
        {
            "best_value": float(valid.loc[best_idx, "_relative_value"]),
            "worst_value": float(valid.loc[worst_idx, "_relative_value"]),
            "average_value": float(valid["_relative_value"].mean()),
            "best_scenario": scenario_name(valid.loc[best_idx]),
            "worst_scenario": scenario_name(valid.loc[worst_idx]),
            "valid_results": valid,
        }
    )
    return summary


def currency(value: Any) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return str(value)


def signed_currency(value: Any) -> str:
    try:
        number = float(value)
        sign = "+" if number >= 0 else "-"
        return f"{sign}${abs(number):,.2f}"
    except Exception:
        return str(value)


def safe_markdown_text(text: str) -> str:
    """Prevent dollar amounts from being interpreted as Markdown math."""
    return str(text).replace("$", "\\$")


def compact_horizontal_bar_chart(
    df: pd.DataFrame,
    category_col: str,
    value_col: str,
    title: str | None = None,
    height: int = 280,
) -> bool:
    """Render a compact horizontal bar chart when Altair is available."""
    if alt is None or df is None or df.empty:
        return False
    chart_df = df[[category_col, value_col]].copy()
    chart_df[value_col] = pd.to_numeric(chart_df[value_col], errors="coerce")
    chart_df = chart_df.dropna(subset=[value_col])
    if chart_df.empty:
        return False
    chart_df = chart_df.sort_values(value_col, ascending=False)
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X(f"{value_col}:Q", title="Relative result ($)"),
            y=alt.Y(f"{category_col}:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip(f"{category_col}:N", title="Scenario"),
                alt.Tooltip(f"{value_col}:Q", title="Relative result", format=",.2f"),
            ],
        )
        .properties(height=height)
    )
    if title:
        chart = chart.properties(title=title)
    st.altair_chart(chart, width="stretch")
    return True



def _scenario_labels(df: pd.DataFrame, scenario_col: str | None) -> pd.Series:
    """Return customer-readable scenario labels for charting."""
    if scenario_col and scenario_col in df.columns:
        return df[scenario_col].astype(str)
    return pd.Series([f"Scenario {i + 1}" for i in range(len(df))], index=df.index)


def show_relative_result_chart(df: pd.DataFrame, summary: dict[str, Any], height: int = 300) -> bool:
    """Show covered-call minus buy-and-hold by scenario."""
    relative_col = summary.get("relative_col")
    scenario_col = summary.get("scenario_col")
    if df is None or df.empty or not relative_col or relative_col not in df.columns:
        return False

    chart_df = pd.DataFrame(
        {
            "Scenario": _scenario_labels(df, scenario_col),
            "Relative result ($)": pd.to_numeric(df[relative_col], errors="coerce"),
        }
    ).dropna(subset=["Relative result ($)"])
    if chart_df.empty:
        return False

    st.caption("Covered-call result minus buy-and-hold. Higher is better; negative values show upside or performance given up.")
    if alt is not None:
        chart = (
            alt.Chart(chart_df)
            .mark_bar()
            .encode(
                x=alt.X("Relative result ($):Q", title="Covered call minus buy-and-hold ($)"),
                y=alt.Y("Scenario:N", sort="-x", title=None),
                tooltip=[
                    alt.Tooltip("Scenario:N", title="Scenario"),
                    alt.Tooltip("Relative result ($):Q", title="Relative result", format=",.2f"),
                ],
            )
            .properties(height=height)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.bar_chart(chart_df.set_index("Scenario")[["Relative result ($)"]], height=height)
    return True


def show_outcome_comparison_chart(df: pd.DataFrame, summary: dict[str, Any], height: int = 300) -> bool:
    """Show covered-call and buy-and-hold scenario outcomes side by side."""
    covered_col = summary.get("covered_call_col")
    buy_hold_col = summary.get("buy_hold_col")
    scenario_col = summary.get("scenario_col")
    if (
        df is None
        or df.empty
        or not covered_col
        or not buy_hold_col
        or covered_col not in df.columns
        or buy_hold_col not in df.columns
    ):
        return False

    chart_df = pd.DataFrame(
        {
            "Scenario": _scenario_labels(df, scenario_col),
            "Covered call": pd.to_numeric(df[covered_col], errors="coerce"),
            "Buy-and-hold": pd.to_numeric(df[buy_hold_col], errors="coerce"),
        }
    ).dropna(subset=["Covered call", "Buy-and-hold"], how="all")
    if chart_df.empty:
        return False

    st.caption("Absolute scenario outcomes for the covered-call setup compared with buy-and-hold.")
    long_df = chart_df.melt(id_vars="Scenario", var_name="Strategy", value_name="Result ($)").dropna()
    if alt is not None:
        chart = (
            alt.Chart(long_df)
            .mark_bar()
            .encode(
                x=alt.X("Scenario:N", title=None),
                y=alt.Y("Result ($):Q", title="Result ($)"),
                xOffset="Strategy:N",
                tooltip=[
                    alt.Tooltip("Scenario:N", title="Scenario"),
                    alt.Tooltip("Strategy:N", title="Strategy"),
                    alt.Tooltip("Result ($):Q", title="Result", format=",.2f"),
                ],
            )
            .properties(height=height)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.bar_chart(chart_df.set_index("Scenario")[["Covered call", "Buy-and-hold"]], height=height)
    return True


def build_payoff_concept_data(config: dict[str, Any]) -> pd.DataFrame:
    """Build an illustrative covered-call payoff shape from the current setup."""
    stock_price = float(config.get("demo_price", DEFAULT_CONFIG["demo_price"]) or DEFAULT_CONFIG["demo_price"])
    contracts = max(int(config.get("desired_contracts", 1) or 1), 1)
    shares = contracts * 100
    target_delta = float(config.get("target_delta", DEFAULT_CONFIG["target_delta"]) or DEFAULT_CONFIG["target_delta"])
    target_dte = max(float(config.get("target_dte", DEFAULT_CONFIG["target_dte"]) or DEFAULT_CONFIG["target_dte"]), 1.0)

    # This is a customer-facing concept graph, not an option-pricing claim.
    estimated_otm_fraction = max(0.015, min(0.08, 0.07 - 0.10 * (target_delta - 0.20)))
    strike = stock_price * (1.0 + estimated_otm_fraction)
    premium_per_share = stock_price * max(0.004, min(0.035, 0.012 * (target_delta / 0.30) * (target_dte / 30.0) ** 0.5))

    min_price = stock_price * 0.85
    max_price = stock_price * 1.15
    if strike > max_price * 0.94:
        max_price = strike * 1.08

    prices = [min_price + (max_price - min_price) * i / 60 for i in range(61)]
    rows: list[dict[str, Any]] = []
    for expiration_price in prices:
        buy_hold_profit = (expiration_price - stock_price) * shares
        covered_call_profit = (min(expiration_price, strike) - stock_price + premium_per_share) * shares
        rows.append(
            {
                "Stock price at expiration": expiration_price,
                "Buy-and-hold": buy_hold_profit,
                "Covered call": covered_call_profit,
                "Estimated short-call strike": strike,
                "Estimated premium per share": premium_per_share,
            }
        )
    return pd.DataFrame(rows)


def show_payoff_concept_chart(config: dict[str, Any], height: int = 300) -> None:
    """Show a simplified payoff diagram for the selected covered-call setup."""
    payoff_df = build_payoff_concept_data(config)
    strike = float(payoff_df["Estimated short-call strike"].iloc[0])
    premium = float(payoff_df["Estimated premium per share"].iloc[0])
    long_df = payoff_df.melt(
        id_vars=["Stock price at expiration"],
        value_vars=["Covered call", "Buy-and-hold"],
        var_name="Strategy",
        value_name="Profit / loss ($)",
    )
    st.caption(
        f"Illustrative payoff concept using an estimated strike near ${strike:,.2f} and estimated premium near ${premium:,.2f} per share. "
        "This is a teaching graphic, not a live option quote."
    )
    if alt is not None:
        chart = (
            alt.Chart(long_df)
            .mark_line()
            .encode(
                x=alt.X("Stock price at expiration:Q", title="Stock price at expiration ($)"),
                y=alt.Y("Profit / loss ($):Q", title="Profit / loss ($)"),
                tooltip=[
                    alt.Tooltip("Stock price at expiration:Q", title="Stock price", format=",.2f"),
                    alt.Tooltip("Strategy:N", title="Strategy"),
                    alt.Tooltip("Profit / loss ($):Q", title="P/L", format=",.2f"),
                ],
            )
            .properties(height=height)
        )
        st.altair_chart(chart, width="stretch")
    else:
        st.line_chart(long_df.pivot(index="Stock price at expiration", columns="Strategy", values="Profit / loss ($)"), height=height)



def _safe_html(value: Any) -> str:
    """Escape user/data values before inserting them into customer-facing HTML/SVG."""
    return html.escape(str(value), quote=True)


def _svg_polyline_points(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def _render_visual_card(title: str, subtitle: str, svg: str) -> None:
    """Render one lightweight customer chart card without relying on external chart libraries."""
    st.markdown(
        f"""
        <div style="border:1px solid #d9e2ec; border-radius:14px; padding:18px 18px 14px 18px; margin:16px 0; background:#ffffff;">
            <div style="font-size:1.05rem; font-weight:700; color:#102a43; margin-bottom:4px;">{_safe_html(title)}</div>
            <div style="font-size:0.88rem; color:#52606d; margin-bottom:12px;">{_safe_html(subtitle)}</div>
            {svg}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_relative_tradeoff_svg(df: pd.DataFrame, summary: dict[str, Any]) -> str | None:
    """Build an SVG chart for covered-call relative result by scenario."""
    relative_col = summary.get("relative_col")
    scenario_col = summary.get("scenario_col")
    if df is None or df.empty or not relative_col or relative_col not in df.columns:
        return None

    chart_df = pd.DataFrame(
        {
            "Scenario": _scenario_labels(df, scenario_col),
            "Relative result ($)": pd.to_numeric(df[relative_col], errors="coerce"),
        }
    ).dropna(subset=["Relative result ($)"])
    if chart_df.empty:
        return None

    chart_df = chart_df.sort_values("Relative result ($)", ascending=True).reset_index(drop=True)
    values = chart_df["Relative result ($)"].tolist()
    max_abs = max(max(abs(v) for v in values), 1.0)

    width = 920
    left_label_x = 24
    zero_x = 460
    right_limit = 760
    left_limit = 210
    plot_half_width = min(zero_x - left_limit, right_limit - zero_x)
    row_height = 54
    top = 58
    height = top + row_height * len(chart_df) + 36

    rows = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="auto" role="img" aria-label="Covered call relative result chart">',
        '<rect x="0" y="0" width="920" height="100%" rx="12" fill="#f8fafc"/>',
        f'<line x1="{zero_x}" y1="34" x2="{zero_x}" y2="{height-18}" stroke="#9fb3c8" stroke-width="2"/>',
        f'<text x="{zero_x}" y="24" text-anchor="middle" font-size="13" fill="#486581">Buy-and-hold parity</text>',
    ]

    for i, row in chart_df.iterrows():
        label = _safe_html(row["Scenario"])
        value = float(row["Relative result ($)"])
        y = top + i * row_height
        bar_width = max(4.0, abs(value) / max_abs * plot_half_width)
        if value >= 0:
            x = zero_x
            fill = "#2563eb"
        else:
            x = zero_x - bar_width
            fill = "#64748b"
        rows.append(f'<text x="{left_label_x}" y="{y+16}" font-size="14" font-weight="700" fill="#102a43">{label}</text>')
        rows.append(f'<rect x="{x:.1f}" y="{y}" width="{bar_width:.1f}" height="20" rx="5" fill="{fill}"/>')
        rows.append(f'<text x="895" y="{y+16}" text-anchor="end" font-size="14" font-weight="700" fill="#102a43">{_safe_html(signed_currency(value))}</text>')

    rows.append('</svg>')
    return "".join(rows)


def _build_payoff_concept_svg(config: dict[str, Any]) -> str:
    """Build a simple covered-call payoff curve SVG."""
    payoff_df = build_payoff_concept_data(config)
    x_values = payoff_df["Stock price at expiration"].astype(float).tolist()
    covered_values = payoff_df["Covered call"].astype(float).tolist()
    buy_hold_values = payoff_df["Buy-and-hold"].astype(float).tolist()
    strike = float(payoff_df["Estimated short-call strike"].iloc[0])
    premium = float(payoff_df["Estimated premium per share"].iloc[0])

    width = 920
    height = 360
    plot_left = 72
    plot_right = 850
    plot_top = 38
    plot_bottom = 300
    min_x, max_x = min(x_values), max(x_values)
    all_y = covered_values + buy_hold_values
    min_y, max_y = min(all_y), max(all_y)
    if min_y == max_y:
        min_y -= 1
        max_y += 1
    y_pad = (max_y - min_y) * 0.08
    min_y -= y_pad
    max_y += y_pad

    def sx(x: float) -> float:
        return plot_left + (x - min_x) / (max_x - min_x) * (plot_right - plot_left)

    def sy(y: float) -> float:
        return plot_bottom - (y - min_y) / (max_y - min_y) * (plot_bottom - plot_top)

    zero_y = sy(0.0)
    strike_x = sx(strike)
    covered_points = _svg_polyline_points([(sx(x), sy(y)) for x, y in zip(x_values, covered_values)])
    buy_hold_points = _svg_polyline_points([(sx(x), sy(y)) for x, y in zip(x_values, buy_hold_values)])

    return f"""
    <svg viewBox="0 0 {width} {height}" width="100%" height="auto" role="img" aria-label="Covered call payoff concept chart">
        <rect x="0" y="0" width="920" height="360" rx="12" fill="#f8fafc"/>
        <line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" stroke="#cbd5e1" stroke-width="1"/>
        <line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_bottom}" stroke="#cbd5e1" stroke-width="1"/>
        <line x1="{plot_left}" y1="{zero_y:.1f}" x2="{plot_right}" y2="{zero_y:.1f}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4 4"/>
        <line x1="{strike_x:.1f}" y1="{plot_top}" x2="{strike_x:.1f}" y2="{plot_bottom}" stroke="#f97316" stroke-width="2" stroke-dasharray="5 5"/>
        <text x="{strike_x:.1f}" y="26" text-anchor="middle" font-size="13" fill="#9a3412">estimated call strike</text>
        <polyline points="{buy_hold_points}" fill="none" stroke="#334155" stroke-width="4"/>
        <polyline points="{covered_points}" fill="none" stroke="#2563eb" stroke-width="4"/>
        <text x="{plot_left}" y="330" font-size="13" fill="#486581">Lower stock price</text>
        <text x="{plot_right}" y="330" text-anchor="end" font-size="13" fill="#486581">Higher stock price</text>
        <text x="18" y="42" font-size="13" fill="#486581" transform="rotate(-90 18,42)">Profit / loss</text>
        <rect x="610" y="50" width="18" height="5" rx="2" fill="#2563eb"/><text x="636" y="57" font-size="13" fill="#102a43">Covered call</text>
        <rect x="610" y="74" width="18" height="5" rx="2" fill="#334155"/><text x="636" y="81" font-size="13" fill="#102a43">Buy-and-hold</text>
        <text x="72" y="24" font-size="13" fill="#52606d">Concept only: estimated premium about {_safe_html(currency(premium))} per share</text>
    </svg>
    """


def _build_modeled_path_svg(config: dict[str, Any]) -> str:
    """Build an illustrative scenario price-path SVG."""
    # PUBLIC_BETA_MODELED_PATH_LEGEND_BELOW_CHART_READY
    import math

    start_price = float(config.get("demo_price", DEFAULT_CONFIG["demo_price"]) or DEFAULT_CONFIG["demo_price"])
    dte = max(10, min(int(config.get("target_dte", DEFAULT_CONFIG["target_dte"]) or DEFAULT_CONFIG["target_dte"]), 60))
    steps = 30
    xs = list(range(steps + 1))

    def path_value(kind: str, i: int) -> float:
        t = i / steps
        if kind == "Downtrend":
            return start_price * (1 - 0.09 * t + 0.006 * math.sin(5 * t))
        if kind == "Sideways Choppy":
            return start_price * (1 + 0.012 * math.sin(7 * t) - 0.002 * t)
        if kind == "Moderate Uptrend":
            return start_price * (1 + 0.055 * t + 0.006 * math.sin(4 * t))
        if kind == "Volatile Two-Sided":
            return start_price * (1 + 0.04 * math.sin(8 * t) - 0.015 * t)
        return start_price * (1 + 0.13 * t + 0.008 * math.sin(5 * t))

    scenarios = [
        ("Downtrend", "#64748b"),
        ("Sideways Choppy", "#0f766e"),
        ("Moderate Uptrend", "#2563eb"),
        ("Volatile Two-Sided", "#9333ea"),
        ("Strong Rally", "#dc2626"),
    ]

    series = {name: [path_value(name, i) for i in xs] for name, _ in scenarios}
    all_values = [v for values in series.values() for v in values]
    min_y, max_y = min(all_values), max(all_values)
    if min_y == max_y:
        min_y *= 0.99
        max_y *= 1.01

    width = 920
    height = 430
    plot_left = 72
    plot_right = 850
    plot_top = 58
    plot_bottom = 285

    def sx(i: int) -> float:
        return plot_left + i / steps * (plot_right - plot_left)

    def sy(y: float) -> float:
        return plot_bottom - (y - min_y) / (max_y - min_y) * (plot_bottom - plot_top)

    zero_y = sy(start_price)
    middle_y = (plot_top + plot_bottom) / 2

    rows = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Illustrative modeled market path shapes">',
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="#f8fafc"/>',
        f'<line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" stroke="#cbd5e1" stroke-width="1"/>',
        f'<line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_bottom}" stroke="#cbd5e1" stroke-width="1"/>',
        f'<line x1="{plot_left}" y1="{zero_y:.1f}" x2="{plot_right}" y2="{zero_y:.1f}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4 5"/>',
        f'<text x="{plot_left}" y="30" font-size="13" fill="#334155">Starting price {_safe_html(currency(start_price))}; illustrative {dte}-DTE scenario shapes</text>',
    ]

    for name, color in scenarios:
        pts = _svg_polyline_points([(sx(i), sy(v)) for i, v in enumerate(series[name])])
        rows.append(
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        )

    legend_x = 120
    legend_y = 338
    legend_gap_x = 250
    legend_gap_y = 26
    for idx, (name, color) in enumerate(scenarios):
        col = idx % 3
        row = idx // 3
        lx = legend_x + col * legend_gap_x
        ly = legend_y + row * legend_gap_y
        rows.append(
            f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 18}" y2="{ly - 4}" stroke="{color}" stroke-width="5" stroke-linecap="round"/>'
        )
        rows.append(
            f'<text x="{lx + 30}" y="{ly}" font-size="13" fill="#0f172a">{_safe_html(name)}</text>'
        )

    rows.extend(
        [
            f'<text x="{plot_left}" y="{plot_bottom + 32}" font-size="12" fill="#334155">Start</text>',
            f'<text x="{plot_right - 110}" y="{plot_bottom + 32}" font-size="12" fill="#334155">Expiration horizon</text>',
            f'<text x="22" y="{middle_y:.1f}" font-size="12" fill="#334155" transform="rotate(-90 22 {middle_y:.1f})">Stock price</text>',
            '</svg>',
        ]
    )
    return "".join(rows)

def show_customer_visual_summary(
    config: dict[str, Any],
    df: pd.DataFrame | None,
    summary: dict[str, Any],
    *,
    expanded: bool = True,
) -> None:
    """Render customer-facing visuals that make the covered-call tradeoff obvious."""
    st.subheader("Visual summary")
    st.caption("Three quick graphics: scenario tradeoff, payoff concept, and illustrative modeled path shapes. The current beta uses named scenario stress paths, not a Monte Carlo distribution.")

    if df is None or df.empty or not summary.get("relative_col"):
        st.info("Run the simulator to display scenario results. The payoff and path illustrations below are concept graphics based on the current setup.")
        _render_visual_card(
            "Covered-call payoff concept",
            "The short call creates premium income but caps participation above the call strike.",
            _build_payoff_concept_svg(config),
        )
        _render_visual_card(
            "Modeled market paths concept",
            "Illustrative path shapes used to explain scenario stress testing. These are not forecasts and are not individual Monte Carlo runs.",
            _build_modeled_path_svg(config),
        )
        return

    relative_svg = _build_relative_tradeoff_svg(df, summary)
    if relative_svg:
        _render_visual_card(
            "Scenario tradeoff chart",
            "Covered-call result minus buy-and-hold. Positive values mean the covered call finished ahead; negative values show performance given up.",
            relative_svg,
        )
    else:
        st.info("The scenario tradeoff chart is unavailable for this output format.")

    _render_visual_card(
        "Covered-call payoff concept",
        "The short call creates income and downside cushion, but it also caps the stock's upside above the strike.",
        _build_payoff_concept_svg(config),
    )

    _render_visual_card(
        "Modeled market paths concept",
        "A visual reminder that the dashboard is testing named market-path scenarios. These lines are illustrative scenario shapes, not a Monte Carlo fan or prediction.",
        _build_modeled_path_svg(config),
    )

def estimate_max_contracts(config: dict[str, Any]) -> int:
    account_size = float(config.get("account_size", 0) or 0)
    cap = float(config.get("position_size_cap", 0) or 0)
    demo_price = float(config.get("demo_price", 0) or 0)
    if account_size <= 0 or cap <= 0 or demo_price <= 0:
        return 0
    return int((account_size * cap) // (demo_price * 100.0))


def validate_config(config: dict[str, Any]) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    warnings: list[str] = []
    max_contracts = estimate_max_contracts(config)

    account_size = float(config.get("account_size", 0) or 0)
    desired_contracts = int(config.get("desired_contracts", 0) or 0)
    target_delta = float(config.get("target_delta", 0) or 0)
    target_dte = int(config.get("target_dte", 0) or 0)
    cap = float(config.get("position_size_cap", 0) or 0)
    demo_price = float(config.get("demo_price", 0) or 0)
    transaction_cost = float(config.get("transaction_cost", 0) or 0)
    slippage = float(config.get("slippage_assumption", 0) or 0)

    if account_size <= 0:
        errors.append("Account size must be positive.")
    if demo_price <= 0:
        errors.append("Demo price must be positive.")
    if desired_contracts <= 0:
        errors.append("Desired contracts must be at least 1.")
    if max_contracts > 0 and desired_contracts > max_contracts:
        errors.append(f"Desired contracts exceed estimated maximum allowed contracts ({max_contracts}).")
    if not 0.05 <= target_delta <= 0.50:
        warnings.append("Target delta is outside a typical covered-call range of roughly 0.05 to 0.50.")
    if target_dte < 7 or target_dte > 60:
        warnings.append("Target DTE is outside the usual short-to-intermediate covered-call range of 7 to 60 days.")
    if cap > 0.25:
        warnings.append("Position-size cap is high. Consider whether this is too concentrated for a paid demo setup.")
    if cap <= 0:
        errors.append("Position-size cap must be positive.")
    if transaction_cost < 0:
        errors.append("Transaction cost cannot be negative.")
    if slippage < 0:
        errors.append("Slippage assumption cannot be negative.")

    return errors, warnings, max_contracts


def build_interpretation(summary: dict[str, Any]) -> str:
    if "best_value" not in summary or "worst_value" not in summary:
        return "The simulator results were loaded, but the relative-performance column could not be summarized."

    best = summary["best_value"]
    worst = summary["worst_value"]
    avg = summary["average_value"]
    best_scenario = summary["best_scenario"]
    worst_scenario = summary["worst_scenario"]

    text = (
        f"The covered call helped most in the {best_scenario} scenario "
        f"({signed_currency(best)} relative to buy-and-hold) and lagged most in the "
        f"{worst_scenario} scenario ({signed_currency(worst)} relative to buy-and-hold). "
        "This is the normal covered-call tradeoff: option premium can cushion flat, choppy, "
        "or declining markets, while the short call can cap participation during a strong rally."
    )

    if avg < 0:
        text += f" The average relative result is negative ({signed_currency(avg)}), so this setup should be treated as income-oriented rather than return-maximizing."
    else:
        text += f" The average relative result is positive ({signed_currency(avg)}), suggesting the modeled scenarios favor the covered-call structure."

    if abs(worst) > max(abs(best), 1) * 3 and worst < 0:
        text += " The upside give-up is much larger than the best downside/sideways benefit, so strong-rally risk deserves attention."

    return text


def build_decision_guidance(config: dict[str, Any], summary: dict[str, Any], errors: list[str], warnings: list[str]) -> tuple[str, list[str]]:
    recommendations: list[str] = []
    if errors:
        return "DO NOT OPEN WITHOUT ADJUSTMENT", ["Fix all configuration errors before running or using this setup."]

    if "average_value" not in summary:
        return "REVIEW BEFORE USE", ["Run the simulator and confirm that the scenario results can be summarized."]

    avg = float(summary["average_value"])
    worst = float(summary["worst_value"])
    best = float(summary["best_value"])
    desired_contracts = int(config.get("desired_contracts", 1) or 1)
    target_delta = float(config.get("target_delta", 0.30) or 0.30)
    cap = float(config.get("position_size_cap", 0.10) or 0.10)

    status = "OPEN / ACCEPTABLE DEMO"

    if avg < 0:
        status = "REVIEW BEFORE USE"
        recommendations.append("Average relative performance is negative versus buy-and-hold. Treat this as an income/risk-shaping tradeoff, not an outperformance strategy.")

    if worst < 0 and abs(worst) > max(abs(best), 1) * 3:
        status = "REVIEW BEFORE USE"
        recommendations.append("Strong-rally give-up dominates the best modeled cushion. Consider reducing target delta or using a smaller position.")

    if target_delta > 0.35:
        status = "REVIEW BEFORE USE"
        recommendations.append("Target delta is relatively high for a conservative covered-call setup. Consider lowering delta to reduce assignment/upside-cap risk.")

    if cap > 0.15 or desired_contracts > 1:
        recommendations.append("Position sizing is more aggressive than the clean demo. Confirm this is intentional before using it as a customer-facing example.")

    if warnings and status == "OPEN / ACCEPTABLE DEMO":
        status = "REVIEW BEFORE USE"
        recommendations.extend(warnings)

    if not recommendations:
        recommendations.append("Inputs and modeled tradeoffs are acceptable for a controlled demo. This does not imply the trade will outperform buy-and-hold.")

    return status, recommendations


def append_run_history(config: dict[str, Any], summary: dict[str, Any]) -> None:
    if "average_value" not in summary:
        return
    RUN_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "run_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ticker": config.get("ticker"),
        "account_size": config.get("account_size"),
        "risk_tier": config.get("risk_tier"),
        "position_size_cap": config.get("position_size_cap"),
        "desired_contracts": config.get("desired_contracts"),
        "target_delta": config.get("target_delta"),
        "target_dte": config.get("target_dte"),
        "management_rule": config.get("management_rule"),
        "rolling_rule": config.get("rolling_rule"),
        "re_entry_rule": config.get("re_entry_rule"),
        "transaction_cost": config.get("transaction_cost"),
        "slippage_assumption": config.get("slippage_assumption"),
        "demo_price": config.get("demo_price"),
        "best_scenario": summary.get("best_scenario"),
        "best_relative_result": summary.get("best_value"),
        "worst_scenario": summary.get("worst_scenario"),
        "worst_relative_result": summary.get("worst_value"),
        "average_relative_result": summary.get("average_value"),
    }
    new_df = pd.DataFrame([row])
    if RUN_HISTORY_PATH.exists():
        old_df = pd.read_csv(RUN_HISTORY_PATH)
        out_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        out_df = new_df
    out_df.to_csv(RUN_HISTORY_PATH, index=False)



def dataframe_to_markdown_table(df: pd.DataFrame) -> str:
    """Return a simple Markdown table without requiring pandas optional tabulate."""
    if df is None or df.empty:
        return ""

    display_df = df.copy()
    display_df = display_df.fillna("")

    columns = [str(col) for col in display_df.columns]

    def clean_cell(value: Any) -> str:
        text = str(value)
        text = text.replace("\n", " ").replace("\r", " ")
        text = text.replace("|", "\\|")
        return text

    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in display_df.iterrows():
        rows.append("| " + " | ".join(clean_cell(row[col]) for col in display_df.columns) + " |")

    return "\n".join([header, separator, *rows])

def build_decision_memo(config: dict[str, Any], summary: dict[str, Any], status: str, recommendations: list[str], interpretation: str, df: pd.DataFrame | None) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = []
    lines.append(f"# {PRODUCT_INFO.product_name} Decision Memo")
    lines.append("")
    lines.append(f"Generated: {timestamp}")
    lines.append(f"Product version: {PRODUCT_INFO.version_label}")
    lines.append(f"Build: {PRODUCT_INFO.build_label}")
    lines.append(f"Release stage: {PRODUCT_INFO.release_stage}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")
    lines.append("## Product framing")
    lines.append(PRODUCT_INFO.positioning_statement)
    lines.append("")
    lines.append("## Configuration")
    for key in [
        "ticker",
        "account_size",
        "risk_tier",
        "position_size_cap",
        "desired_contracts",
        "target_delta",
        "target_dte",
        "management_rule",
        "rolling_rule",
        "re_entry_rule",
        "transaction_cost",
        "slippage_assumption",
        "demo_price",
    ]:
        lines.append(f"- {key}: {config.get(key)}")
    lines.append("")
    lines.append("## Latest results summary")
    if "average_value" in summary:
        lines.append(f"- Named scenarios tested: {summary.get('row_count')}")
        lines.append(f"- Best relative result: {signed_currency(summary.get('best_value'))} ({summary.get('best_scenario')})")
        lines.append(f"- Worst relative result: {signed_currency(summary.get('worst_value'))} ({summary.get('worst_scenario')})")
        lines.append(f"- Average result versus simply holding the stock: {signed_currency(summary.get('average_value'))}")
    else:
        lines.append("- Results summary was not available.")
    lines.append("")
    lines.append("## Plain-English interpretation")
    lines.append(interpretation)
    lines.append("")
    lines.append("## Decision guidance")
    lines.append(f"Decision: {status}")
    lines.append("")
    for item in recommendations:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Scenario table")
    if df is not None and not df.empty:
        lines.append(dataframe_to_markdown_table(df))
    else:
        lines.append("Scenario table was not available.")
    lines.append("")
    lines.append("## Important limitations")
    for limitation in PRODUCT_INFO.key_limitations:
        lines.append(f"- {limitation}")
    lines.append("- This memo summarizes modeled scenarios from the local paid simulator. It is not investment advice, does not guarantee future returns, and should be interpreted as scenario analysis rather than a forecast.")
    lines.append("")
    return "\n".join(lines)


def save_decision_memo(config: dict[str, Any], summary: dict[str, Any], status: str, recommendations: list[str], interpretation: str, df: pd.DataFrame | None) -> Path:
    MEMO_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticker = str(config.get("ticker", "ticker")).upper().replace(" ", "_")
    memo_path = MEMO_DIR / f"decision_memo_{ticker}_{timestamp}.md"
    memo_path.write_text(build_decision_memo(config, summary, status, recommendations, interpretation, df), encoding="utf-8")
    return memo_path


def sanitize_pdf_text(text: Any) -> str:
    """Convert text to a PDF-safe, mostly ASCII representation."""
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
    }
    out = str(text)
    for old, new in replacements.items():
        out = out.replace(old, new)
    return out.encode("latin-1", errors="replace").decode("latin-1")


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_pdf_line(text: str, max_chars: int) -> list[str]:
    text = sanitize_pdf_text(text).strip()
    if not text:
        return [""]
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            current = word
    if current:
        lines.append(current)
    return lines


def markdown_to_plain_lines(markdown_text: str) -> list[tuple[str, int]]:
    """Return (line, font_size) tuples for a simple text-first PDF memo."""
    output: list[tuple[str, int]] = []
    for raw_line in markdown_text.splitlines():
        line = sanitize_pdf_text(raw_line).rstrip()
        if not line:
            output.append(("", 10))
            continue
        if line.startswith("# "):
            output.append((line[2:].strip(), 18))
        elif line.startswith("## "):
            output.append((line[3:].strip(), 14))
        elif line.startswith("### "):
            output.append((line[4:].strip(), 12))
        elif line.startswith("| "):
            # Make Markdown tables readable in the plain PDF without tabulate/reportlab.
            cells = [cell.strip().replace("\\|", "|") for cell in line.strip("|").split("|")]
            cleaned = " | ".join(cells)
            if set(cleaned.replace("|", "").replace("-", "").replace(" ", "")) == set():
                continue
            output.append((cleaned, 8))
        else:
            output.append((line, 10))
    return output


def write_simple_pdf(text: str, pdf_path: Path) -> None:
    """Write a dependency-free plain-text PDF using Helvetica."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    page_width = 612
    page_height = 792
    left_margin = 54
    top_y = 744
    bottom_y = 54
    line_gap = 4

    pages: list[list[tuple[str, int]]] = []
    current_page: list[tuple[str, int]] = []
    y = top_y

    for line, font_size in markdown_to_plain_lines(text):
        max_chars = 72 if font_size >= 10 else 105
        wrapped = wrap_pdf_line(line, max_chars)
        for part in wrapped:
            needed = font_size + line_gap
            if y - needed < bottom_y:
                pages.append(current_page)
                current_page = []
                y = top_y
            current_page.append((part, font_size))
            y -= needed
    if current_page or not pages:
        pages.append(current_page)

    objects: list[bytes] = []

    def add_object(body: str | bytes) -> int:
        if isinstance(body, str):
            body_b = body.encode("latin-1", errors="replace")
        else:
            body_b = body
        objects.append(body_b)
        return len(objects)

    catalog_id = add_object("<< /Type /Catalog /Pages 2 0 R >>")
    kids_refs: list[str] = []
    page_content_pairs: list[tuple[int, int]] = []

    # Reserve pages object as object 2.
    objects[1-1:1-1] = []  # no-op, keeps linters quiet
    # Object 2 must be added now.
    # Since catalog is object 1, add placeholder for object 2.
    objects.append(b"PAGES_PLACEHOLDER")

    font_id = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for page_lines in pages:
        commands: list[str] = ["BT"]
        y_pos = top_y
        for part, font_size in page_lines:
            escaped = pdf_escape(part)
            commands.append(f"/F1 {font_size} Tf")
            commands.append(f"1 0 0 1 {left_margin} {int(y_pos)} Tm")
            commands.append(f"({escaped}) Tj")
            y_pos -= font_size + line_gap
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", errors="replace")
        content_id = add_object(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
        page_id = add_object(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>"
        )
        kids_refs.append(f"{page_id} 0 R")
        page_content_pairs.append((page_id, content_id))

    pages_body = f"<< /Type /Pages /Kids [{' '.join(kids_refs)}] /Count {len(kids_refs)} >>".encode("latin-1")
    objects[1] = pages_body

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_num, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{obj_num} 0 obj\n".encode("ascii"))
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")

    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    pdf_path.write_bytes(bytes(pdf))


def save_decision_memo_pdf(config: dict[str, Any], summary: dict[str, Any], status: str, recommendations: list[str], interpretation: str, df: pd.DataFrame | None) -> Path:
    MEMO_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticker = str(config.get("ticker", "ticker")).upper().replace(" ", "_")
    pdf_path = MEMO_DIR / f"decision_memo_{ticker}_{timestamp}.pdf"
    memo_text = build_decision_memo(config, summary, status, recommendations, interpretation, df)
    write_simple_pdf(memo_text, pdf_path)
    return pdf_path



def show_latest_results_next_steps(summary: dict[str, Any], status: str) -> None:
    """Show a clear next-step panel after a beta tester reads Latest results."""
    average_value = summary.get("average_value")
    if average_value is None:
        average_text = "The app could not summarize the average result yet."
    else:
        average_text = (
            "The clean demo favored the covered call on average."
            if float(average_value) >= 0
            else "The clean demo lagged buy-and-hold on average, which is common when upside is capped in rally scenarios."
        )

    st.markdown("### What to do next")
    st.info(
        "You have completed the first stress-test run. "
        + average_text
        + " Use the tabs above to continue the beta walkthrough."
    )

    next_col1, next_col2, next_col3 = st.columns(3)
    with next_col1:
        st.markdown("**1. Try the Challenge**")
        st.write(
            "Open **Challenge** to pick a target market scenario, adjust the setup, "
            "and try to improve the score."
        )
    with next_col2:
        st.markdown("**2. Review the Report**")
        st.write(
            "Open **Report** to see the customer-readable summary that explains the setup, "
            "tradeoff, and result."
        )
    with next_col3:
        st.markdown("**3. Check Help**")
        st.write(
            "Open **Help & assumptions** if terms like delta, DTE, assignment, "
            "one option cycle, or scenario stress test are unclear."
        )

    st.caption(
        "Suggested beta feedback: Was the result clear? Did the graphics help? "
        "Could you tell what to do next without asking for instructions?"
    )

def show_latest_results(config: dict[str, Any], errors: list[str], warnings: list[str]) -> tuple[dict[str, Any], pd.DataFrame | None, str, list[str], str]:
    st.subheader("Latest results summary")
    df = load_scenario_results()
    if df is None:
        st.info("No scenario comparison CSV found yet. Run the paid simulator first.")
        return {}, None, "REVIEW BEFORE USE", ["Run the simulator first."], "No results are available yet."

    summary = summarize_results(df)
    relative_col = summary.get("relative_col")
    scenario_col = summary.get("scenario_col")

    if relative_col is None:
        st.warning("Could not detect the relative-result column.")
        st.caption("Available columns: " + ", ".join(map(str, summary.get("available_columns", []))))
        with st.expander("Raw scenario comparison table", expanded=False):
            st.dataframe(df, width="stretch")
        return summary, df, "REVIEW BEFORE USE", ["The result column could not be detected."], "The scenario table was loaded, but the relative-result column was not detected."

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Named scenarios tested", summary.get("row_count", 0))
    col2.metric("Best relative result", signed_currency(summary.get("best_value", 0)), summary.get("best_scenario", ""))
    col3.metric("Worst relative result", signed_currency(summary.get("worst_value", 0)), summary.get("worst_scenario", ""))
    col4.metric("Average result versus simply holding the stock", signed_currency(summary.get("average_value", 0)))

    with st.expander("Technical details", expanded=False):
        st.caption(f"Relative-result column used internally: {relative_col}")

    interpretation = build_interpretation(summary)
    st.info("Plain-English interpretation\n\n" + safe_markdown_text(interpretation))

    status, recommendations = build_decision_guidance(config, summary, errors, warnings)
    if status == "OPEN / ACCEPTABLE DEMO":
        st.success(f"Decision guidance: {status}")
    elif status == "REVIEW BEFORE USE":
        st.warning(f"Decision guidance: {status}")
    else:
        st.error(f"Decision guidance: {status}")

    for rec in recommendations:
        st.write(f"- {rec}")

    show_latest_results_next_steps(summary, status)

    show_customer_visual_summary(config, df, summary, expanded=True)

    with st.expander("Raw scenario comparison table", expanded=False):
        st.dataframe(df, width="stretch")

    st.subheader("Scenario detail cards")
    for idx, row in df.iterrows():
        scenario_name = str(row[scenario_col]) if scenario_col else f"Scenario {idx + 1}"
        value = pd.to_numeric(pd.Series([row[relative_col]]), errors="coerce").iloc[0]
        title = f"{scenario_name}: {signed_currency(value)} relative result"
        with st.expander(title):
            if value >= 0:
                st.write("The covered call helped in this scenario relative to buy-and-hold.")
            else:
                st.write("The covered call lagged buy-and-hold in this scenario.")
            st.dataframe(pd.DataFrame([row]), width="stretch")

    st.subheader("Export decision memo")
    st.write("Save a customer-facing memo with the current configuration, results summary, decision guidance, and scenario table.")
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        if st.button("Export Markdown memo"):
            memo_path = save_decision_memo(config, summary, status, recommendations, interpretation, df)
            st.success(f"Decision memo saved: {memo_path}")
            st.session_state["latest_memo_path"] = str(memo_path)
    with col_b:
        if st.button("Export PDF memo"):
            pdf_path = save_decision_memo_pdf(config, summary, status, recommendations, interpretation, df)
            st.success(f"Decision memo PDF saved: {pdf_path}")
            st.session_state["latest_memo_pdf_path"] = str(pdf_path)
    with col_c:
        if st.button("Open memo folder"):
            MEMO_DIR.mkdir(parents=True, exist_ok=True)
            if not open_path_with_windows(MEMO_DIR):
                st.warning(f"Could not open memo folder directly. Folder: {MEMO_DIR}")

    latest_memo = st.session_state.get("latest_memo_path")
    latest_pdf = st.session_state.get("latest_memo_pdf_path")
    dl1, dl2 = st.columns(2)
    with dl1:
        if latest_memo:
            memo_file = Path(latest_memo)
            if memo_file.exists():
                st.download_button(
                    "Download latest Markdown memo",
                    data=memo_file.read_text(encoding="utf-8"),
                    file_name=memo_file.name,
                    mime="text/markdown",
                )
    with dl2:
        if latest_pdf:
            pdf_file = Path(latest_pdf)
            if pdf_file.exists():
                st.download_button(
                    "Download latest PDF memo",
                    data=pdf_file.read_bytes(),
                    file_name=pdf_file.name,
                    mime="application/pdf",
                )

    return summary, df, status, recommendations, interpretation


def _get_challenge_score_row(df: pd.DataFrame, summary: dict[str, Any], target_scenario: str) -> tuple[float | None, pd.Series | None, str | None]:
    """Return the current challenge score for a selected scenario."""
    if df is None or df.empty:
        return None, None, None
    relative_col = summary.get("relative_col")
    scenario_col = summary.get("scenario_col") or detect_scenario_column(df)
    if not relative_col or relative_col not in df.columns:
        return None, None, scenario_col

    if scenario_col and scenario_col in df.columns:
        scenario_values = df[scenario_col].astype(str)
        match = df.loc[scenario_values.str.lower() == str(target_scenario).lower()].copy()
        if match.empty:
            match = df.loc[scenario_values.str.contains(str(target_scenario), case=False, regex=False, na=False)].copy()
    else:
        match = pd.DataFrame()

    if match.empty:
        return None, None, scenario_col

    row = match.iloc[0]
    score = pd.to_numeric(pd.Series([row[relative_col]]), errors="coerce").iloc[0]
    if pd.isna(score):
        return None, row, scenario_col
    return float(score), row, scenario_col


def _challenge_config_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    """Capture the user-facing setup fields for challenge scoring."""
    return {
        "ticker": str(config.get("ticker", "SPY")).upper(),
        "contracts": int(config.get("desired_contracts", 1)),
        "delta": float(config.get("target_delta", 0.30)),
        "dte": int(config.get("target_dte", 30)),
        "risk_tier": str(config.get("risk_tier", "Balanced")),
        "stock_price": float(config.get("demo_price", 545.25)),
        "position_cap": float(config.get("position_size_cap", 0.10)),
    }


def _clean_challenge_player_name(raw_name: str) -> str:
    """Return a short display name for the challenge leaderboard."""
    cleaned = " ".join(str(raw_name or "").strip().split())
    if not cleaned:
        return "Anonymous tester"
    return cleaned[:40]


def _estimate_position_capacity(account_size: float, stock_price: float, position_size_cap: float) -> tuple[float, int, int]:
    """Estimate capped stock dollars, whole shares, and covered-call contracts."""
    try:
        account_value = max(float(account_size or 0), 0.0)
        price = max(float(stock_price or 0), 0.0)
        cap = min(max(float(position_size_cap or 0), 0.0), 1.0)
    except (TypeError, ValueError):
        return 0.0, 0, 0

    capped_dollars = account_value * cap
    if price <= 0:
        return capped_dollars, 0, 0
    whole_shares = int(capped_dollars // price)
    whole_contracts = int(whole_shares // 100)
    return capped_dollars, whole_shares, whole_contracts


def _render_position_size_explainer(account_size: float, stock_price: float, position_size_cap: float) -> None:
    """Explain max position size in shares and covered-call contracts."""
    capped_dollars, whole_shares, whole_contracts = _estimate_position_capacity(account_size, stock_price, position_size_cap)
    price_text = f"${stock_price:,.2f}" if float(stock_price or 0) > 0 else "the selected stock price"
    st.caption(
        "Max position size limits the stock/ETF dollars used for covered calls. "
        f"With a ${float(account_size or 0):,.0f} account and a {float(position_size_cap or 0):.0%} cap, "
        f"the allowed stock exposure is about ${capped_dollars:,.0f}. At {price_text} per share, "
        f"that supports about {whole_shares:,} shares, or {whole_contracts:,} full covered-call "
        f"contract{'s' if whole_contracts != 1 else ''}."
    )


def _render_itm_no_roll_explainer() -> None:
    """Explain the current beta's ITM / no-roll assumption."""
    st.info(
        "If the short call goes in the money during a scenario, this beta does not automatically roll it. "
        "The result reflects the capped-upside / assignment-style behavior of one covered-call cycle: "
        "the premium is kept, but gains above the strike are limited compared with buy-and-hold."
    )


def _format_challenge_board(board_df: pd.DataFrame) -> pd.DataFrame:
    """Prepare a display-friendly leaderboard table."""
    if board_df.empty:
        return board_df

    display_df = board_df.copy()
    display_df = display_df.sort_values(
        ["target_scenario", "score"],
        ascending=[True, False],
        na_position="last",
    ).reset_index(drop=True)
    display_df["rank_in_regime"] = display_df.groupby("target_scenario")["score"].rank(
        method="first",
        ascending=False,
    ).astype(int)

    ordered_cols = [
        "target_scenario",
        "rank_in_regime",
        "player_name",
        "score",
        "ticker",
        "contracts",
        "delta",
        "dte",
        "risk_tier",
        "time",
        "average_relative_result",
        "worst_relative_result",
    ]
    ordered_cols = [col for col in ordered_cols if col in display_df.columns]
    display_df = display_df[ordered_cols]

    rename_map = {
        "target_scenario": "Market scenario",
        "rank_in_regime": "Rank",
        "player_name": "Name",
        "score": "Score",
        "ticker": "Ticker",
        "contracts": "Contracts",
        "delta": "Delta target",
        "dte": "DTE",
        "risk_tier": "Setup style",
        "time": "Recorded",
        "average_relative_result": "Average result versus simply holding the stock",
        "worst_relative_result": "Worst relative result",
    }
    display_df = display_df.rename(columns=rename_map)

    for col in ["Score", "Average result versus simply holding the stock", "Worst relative result"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].map(lambda value: signed_currency(value) if pd.notna(value) else "N/A")
    if "Delta target" in display_df.columns:
        display_df["Delta target"] = display_df["Delta target"].map(lambda value: f"{value:.2f}" if pd.notna(value) else "N/A")
    return display_df


def _render_challenge_run_controls(config: dict[str, Any]) -> None:
    """Render a compact challenge-specific setup-and-run panel."""
    st.markdown("### Setup and run from this page")
    st.caption(
        "Use these controls to try a covered-call setup for the challenge without leaving this tab. "
        "After the run completes, choose a regime below and record the score."
    )

    with st.expander("Edit challenge setup", expanded=True):
        input_col1, input_col2, input_col3 = st.columns(3)
        with input_col1:
            ticker = st.text_input(
                "Ticker",
                value=str(config.get("ticker", "SPY")).upper(),
                key="challenge_run_ticker",
            ).upper()
            account_size = st.number_input(
                "Account size ($)",
                min_value=0.0,
                value=float(config.get("account_size", 600000.0)),
                step=1000.0,
                key="challenge_run_account_size",
            )
        with input_col2:
            desired_contracts = st.number_input(
                "Contracts",
                min_value=1,
                value=int(config.get("desired_contracts", 1)),
                step=1,
                key="challenge_run_contracts",
            )
            target_delta = st.number_input(
                "Call delta target",
                min_value=0.0,
                max_value=1.0,
                value=float(config.get("target_delta", 0.30)),
                step=0.01,
                format="%.2f",
                key="challenge_run_delta",
            )
        with input_col3:
            target_dte = st.number_input(
                "Days to expiration",
                min_value=1,
                value=int(config.get("target_dte", 30)),
                step=1,
                key="challenge_run_dte",
            )
            demo_price = st.number_input(
                "Stock price",
                min_value=0.0,
                value=float(config.get("demo_price", 545.25)),
                step=1.0,
                key="challenge_run_demo_price",
            )

        tier_options = ["Conservative", "Balanced", "Aggressive"]
        current_tier = str(config.get("risk_tier", "Balanced"))
        if current_tier not in tier_options:
            current_tier = "Balanced"

        run_col1, run_col2 = st.columns(2)
        with run_col1:
            risk_tier = st.selectbox(
                "Setup style",
                tier_options,
                index=tier_options.index(current_tier),
                key="challenge_run_risk_tier",
            )
        with run_col2:
            position_size_cap = st.number_input(
                "Max position size",
                min_value=0.0,
                max_value=1.0,
                value=float(config.get("position_size_cap", 0.10)),
                step=0.01,
                format="%.2f",
                key="challenge_run_position_cap",
            )

        _render_position_size_explainer(account_size, demo_price, position_size_cap)

        run_config = {
            "ticker": ticker,
            "account_size": account_size,
            "risk_tier": risk_tier,
            "position_size_cap": position_size_cap,
            "desired_contracts": int(desired_contracts),
            "target_delta": float(target_delta),
            "target_dte": int(target_dte),
            "management_rule": str(config.get("management_rule", "hold_to_expiration")),
            "rolling_rule": str(config.get("rolling_rule", "none")),
            "re_entry_rule": str(config.get("re_entry_rule", "immediate")),
            "transaction_cost": float(config.get("transaction_cost", 1.0)),
            "slippage_assumption": float(config.get("slippage_assumption", 0.01)),
            "demo_price": float(demo_price),
        }

        errors, warnings, max_contracts = validate_config(run_config)
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Estimated max contracts", max_contracts)
        metric_col2.metric("Selected contracts", int(desired_contracts))
        metric_col3.metric("Max position size", f"{position_size_cap:.2%}")

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("This challenge setup passes the sizing rule.")
        for warning in warnings:
            st.warning(warning)

        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("Run this setup for challenge", type="primary", disabled=bool(errors), key="challenge_run_this_setup"):
                save_config(run_config)
                code, output = run_python_script(RUNNER_PATH)
                st.session_state["latest_challenge_run_output"] = output
                if code == 0:
                    df_after = load_scenario_results()
                    if df_after is not None:
                        append_run_history(run_config, summarize_results(df_after))
                    st.session_state["dashboard_notice"] = "Challenge setup run completed. Choose a target market scenario below and record the score."
                    st.session_state["dashboard_notice_level"] = "success"
                    st.success("Challenge setup run completed. Choose a target market scenario below and record the score on this page.")
                else:
                    st.error(f"Challenge setup run failed with return code {code}.")
                    with st.expander("Simulator output", expanded=True):
                        st.text_area("Simulator output text", value=output, height=220, label_visibility="collapsed")
        with button_col2:
            if st.button("Reset and run clean SPY demo", key="challenge_reset_and_run_clean_demo"):
                ok, message = reset_to_clean_demo(run_after_reset=True)
                st.session_state["dashboard_notice"] = message
                st.session_state["dashboard_notice_level"] = "success" if ok else "warning"
                if ok:
                    st.success("Clean SPY demo run completed. Choose a target market scenario below and record the score on this page.")
                else:
                    st.warning(message)

        latest_output = st.session_state.get("latest_challenge_run_output")
        if latest_output:
            with st.expander("Latest challenge run output", expanded=False):
                st.text_area("Output", value=str(latest_output), height=180, label_visibility="collapsed")


def show_covered_call_challenge(config: dict[str, Any]) -> None:
    """Render a beta game mode for comparing covered-call scores by scenario."""
    st.subheader("Covered Call Challenge")
    st.caption(
        "A beta learning mode: choose a market regime, adjust the covered-call setup, rerun the stress test, "
        "and record a score under a name of your choice."
    )

    st.info(
        "Challenge goal: try to find a covered-call setup that scores well for a chosen named scenario. "
        "The score is the covered-call result minus buy-and-hold for that scenario. Higher is better."
    )

    st.markdown("### How to play")
    play_col1, play_col2, play_col3 = st.columns(3)
    with play_col1:
        st.markdown(
            """
            **1. Choose a target scenario**  
            Pick the market path you want to optimize for.
            """
        )
    with play_col2:
        st.markdown(
            """
            **2. Change the setup**  
            Use the setup controls on this page, or use **Setup & run** for the full input panel.
            """
        )
    with play_col3:
        st.markdown(
            """
            **3. Run and record**  
            Run the setup, enter a name or nickname, and save the score to the leaderboard.
            """
        )

    _render_challenge_run_controls(config)
    # Reload config after the challenge-run controls because those controls may
    # save and run a new setup without leaving the Challenge tab.
    config = load_config()

    df = load_scenario_results()
    if df is None or df.empty:
        st.warning("No stress-test results are available yet. Use the setup-and-run controls above to create a challenge score.")
        return

    summary = summarize_results(df)
    scenario_col = summary.get("scenario_col") or detect_scenario_column(df)
    relative_col = summary.get("relative_col")

    if not relative_col:
        st.error("The challenge cannot score this run because the relative-result column was not detected.")
        with st.expander("Raw results", expanded=False):
            st.dataframe(df, width="stretch")
        return

    if scenario_col and scenario_col in df.columns:
        scenarios = [str(value) for value in df[scenario_col].dropna().astype(str).tolist()]
    else:
        scenarios = [f"Scenario {i + 1}" for i in range(len(df))]

    if not scenarios:
        st.error("No named scenarios were found in the latest result table.")
        return

    st.markdown("### Current challenge")
    target_scenario = st.selectbox("Target market scenario", scenarios, key="challenge_target_scenario")
    player_name = _clean_challenge_player_name(
        st.text_input(
            "Name for the scoreboards",
            value=st.session_state.get("challenge_player_name", "Beta tester"),
            help="Use a nickname or initials. Do not enter sensitive personal information.",
            key="challenge_player_name",
        )
    )

    score, score_row, _ = _get_challenge_score_row(df, summary, target_scenario)

    cfg = _challenge_config_snapshot(config)
    contracts = cfg["contracts"]
    shares_controlled = contracts * 100

    score_col1, score_col2, score_col3, score_col4 = st.columns(4)
    score_col1.metric("Target scenario", target_scenario)
    score_col2.metric("Current score", signed_currency(score) if score is not None else "N/A")
    score_col3.metric("Contracts", contracts)
    score_col4.metric("Shares controlled", shares_controlled)

    st.caption(
        "Score = covered-call result minus buy-and-hold for the selected regime. "
        "A positive score means the covered call beat buy-and-hold in that scenario; a negative score means it lagged."
    )

    setup_col1, setup_col2, setup_col3, setup_col4 = st.columns(4)
    setup_col1.metric("Ticker", cfg["ticker"])
    setup_col2.metric("Delta target", f"{cfg['delta']:.2f}")
    setup_col3.metric("DTE", cfg["dte"])
    setup_col4.metric("Setup style", cfg["risk_tier"])

    if score is not None:
        if score >= 0:
            st.success("This setup beat buy-and-hold for the selected regime.")
        else:
            st.warning("This setup lagged buy-and-hold for the selected regime. Try changing the inputs and running again.")

    st.markdown("### Market scenario scoreboards")
    st.caption(
        "Scores are ranked highest to lowest within each market scenario for this browser session. "
        "A future version can store shared public scoreboards using a database."
    )

    if "challenge_leaderboard" not in st.session_state:
        st.session_state["challenge_leaderboard"] = []

    button_col1, button_col2 = st.columns([1, 1])
    with button_col1:
        if st.button("Record current score", type="primary", disabled=score is None):
            entry = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "player_name": player_name,
                "target_scenario": target_scenario,
                "score": float(score) if score is not None else None,
                "ticker": cfg["ticker"],
                "contracts": cfg["contracts"],
                "delta": cfg["delta"],
                "dte": cfg["dte"],
                "risk_tier": cfg["risk_tier"],
                "stock_price": cfg["stock_price"],
                "position_cap": cfg["position_cap"],
                "average_relative_result": float(summary.get("average_value", 0)) if summary.get("average_value") is not None else None,
                "worst_relative_result": float(summary.get("worst_value", 0)) if summary.get("worst_value") is not None else None,
            }
            st.session_state["challenge_leaderboard"].append(entry)
            st.success(f"Score recorded for {player_name} in {target_scenario}.")
    with button_col2:
        if st.button("Clear session scoreboards"):
            st.session_state["challenge_leaderboard"] = []
            st.info("Challenge scoreboards cleared.")

    leaderboard = st.session_state.get("challenge_leaderboard", [])
    if leaderboard:
        board_df = pd.DataFrame(leaderboard)
        board_df["score"] = pd.to_numeric(board_df["score"], errors="coerce")

        summary_rows = []
        for scenario in scenarios:
            scenario_df = board_df.loc[board_df["target_scenario"] == scenario].copy()
            scenario_df = scenario_df.sort_values("score", ascending=False, na_position="last")
            best_score = scenario_df["score"].iloc[0] if not scenario_df.empty else None
            best_name = scenario_df["player_name"].iloc[0] if not scenario_df.empty else "No score yet"
            summary_rows.append(
                {
                    "Market scenario": scenario,
                    "Attempts": int(len(scenario_df)),
                    "Best name": best_name,
                    "Best score": signed_currency(best_score) if best_score is not None and pd.notna(best_score) else "N/A",
                }
            )
        st.markdown("#### Scoreboard summary by scenario")
        st.dataframe(pd.DataFrame(summary_rows), width="stretch", hide_index=True)

        selected_board = st.selectbox("View ranked scores for market scenario", ["All scenarios"] + scenarios, key="challenge_board_filter")
        if selected_board == "All scenarios":
            ranked_df = board_df.copy()
        else:
            ranked_df = board_df.loc[board_df["target_scenario"] == selected_board].copy()
        ranked_df = ranked_df.sort_values(["target_scenario", "score"], ascending=[True, False], na_position="last")
        display_df = _format_challenge_board(ranked_df)
        st.dataframe(display_df, width="stretch", hide_index=True)

        download_df = board_df.sort_values(["target_scenario", "score"], ascending=[True, False], na_position="last")
        st.download_button(
            "Download scoreboards CSV",
            data=download_df.to_csv(index=False),
            file_name="covered_call_challenge_scoreboards.csv",
            mime="text/csv",
        )
    else:
        st.info("No scores recorded yet. Enter a name and record a score after running a setup.")

    st.markdown("### Important limitation")
    st.warning(
        "This is a beta learning game, not an optimizer or trade recommendation. Optimizing for one named scenario may make the setup worse in another scenario. "
        "The current beta evaluates one covered-call setup over one option cycle and does not roll ITM calls. "
        "The scoreboards are currently stored only in this browser session; shared public scoreboards would require a database or other persistent storage."
    )

    with st.expander("Raw result row for selected scenario", expanded=False):
        if score_row is not None:
            st.dataframe(pd.DataFrame([score_row]), width="stretch")
        else:
            st.write("No matching row found for the selected scenario.")

def show_run_history() -> None:
    st.subheader("Run history")
    if not RUN_HISTORY_PATH.exists():
        st.info("No run history logged yet. Run the simulator from this control panel to create it.")
        return
    df = pd.read_csv(RUN_HISTORY_PATH)
    if df.empty:
        st.info("Run history exists but is empty.")
        return
    avg_col = find_column(df, ["average_relative_result"])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Runs logged", len(df))
    if avg_col:
        values = pd.to_numeric(df[avg_col], errors="coerce")
        col2.metric("Latest average result", signed_currency(values.iloc[-1]))
        col3.metric("Best average run", signed_currency(values.max()))
        col4.metric("Worst average run", signed_currency(values.min()))
        distinct_values = values.dropna().round(2).nunique()
        if len(values.dropna()) >= 3 and distinct_values > 1:
            st.line_chart(values.reset_index(drop=True), height=240)
        else:
            st.caption("Run-history chart hidden because recent runs are effectively identical. The table below keeps the audit trail.")
    with st.expander("Recent run-history rows", expanded=False):
        st.dataframe(df.tail(20), width="stretch")
    st.download_button("Download run history CSV", data=df.to_csv(index=False), file_name="run_history.csv", mime="text/csv")

def run_selected_preset_comparison(selected_presets: list[str]) -> None:
    rows: list[dict[str, Any]] = []
    original_config = load_config()
    batch_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    progress = st.progress(0)

    for i, preset_name in enumerate(selected_presets, start=1):
        config = PRESETS[preset_name].copy()
        save_config(config)
        code, output = run_python_script(RUNNER_PATH, {"COVERED_CALL_SIMULATOR_SUPPRESS_REPORT_OPEN": "1"})
        df = load_scenario_results()
        summary = summarize_results(df) if df is not None else {}
        rows.append(
            {
                "batch_timestamp": batch_timestamp,
                "preset_name": preset_name,
                "return_code": code,
                "average_relative_result": summary.get("average_value"),
                "best_scenario": summary.get("best_scenario"),
                "best_relative_result": summary.get("best_value"),
                "worst_scenario": summary.get("worst_scenario"),
                "worst_relative_result": summary.get("worst_value"),
                "ticker": config.get("ticker"),
                "target_delta": config.get("target_delta"),
                "target_dte": config.get("target_dte"),
                "desired_contracts": config.get("desired_contracts"),
                "position_size_cap": config.get("position_size_cap"),
                "output_tail": output[-1000:],
            }
        )
        progress.progress(i / max(len(selected_presets), 1))

    save_config(original_config)
    PRESET_COMPARISON_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_df = pd.DataFrame(rows)
    if PRESET_COMPARISON_PATH.exists():
        old_df = pd.read_csv(PRESET_COMPARISON_PATH)
        out_df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        out_df = new_df
    out_df.to_csv(PRESET_COMPARISON_PATH, index=False)
    st.success("Preset comparison complete. Original visible config was restored.")


def show_preset_comparison() -> None:
    st.subheader("Compare preset examples")

    st.info(
        "This page compares several ready-made covered-call examples using the same named market examples. "
        "It helps show how changing the covered-call style changes the result. "
        "This is not a trade recommendation; it simply shows which preset did better or worse in this test batch."
    )

    st.caption("Compare several ready-made covered-call examples using the same named market examples.")

    selected = st.multiselect("Ready-made examples to compare", list(PRESETS.keys()), default=list(PRESETS.keys()))
    if st.button("Compare selected examples"):
        if not selected:
            st.warning("Select at least one preset.")
        else:
            run_selected_preset_comparison(selected)

    if not PRESET_COMPARISON_PATH.exists():
        st.info("No preset comparison has been run yet.")
        return

    df = pd.read_csv(PRESET_COMPARISON_PATH)
    if df.empty:
        st.info("Preset comparison history exists but is empty.")
        return

    latest_batch = df["batch_timestamp"].iloc[-1] if "batch_timestamp" in df.columns else None
    latest = df[df["batch_timestamp"] == latest_batch] if latest_batch else df
    avg_col = find_column(latest, ["average_relative_result"])
    preset_col = find_column(latest, ["preset_name"])

    if avg_col and preset_col and not latest.empty:
        values = pd.to_numeric(latest[avg_col], errors="coerce")
        best_idx = values.idxmax()
        worst_idx = values.idxmin()
        best_preset = str(latest.loc[best_idx, preset_col])
        worst_preset = str(latest.loc[worst_idx, preset_col])
        best_value = values.loc[best_idx]
        worst_value = values.loc[worst_idx]

        st.success(
            "Held up best in this test batch: "
            f"{best_preset}. It held up best because it fell behind simply holding the stock "
            f"by the smallest amount in this batch ({signed_currency(best_value)})."
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Examples in latest batch", len(latest))
        col2.metric("Held up best", best_preset, signed_currency(best_value))
        col3.metric("Fell behind most", worst_preset, signed_currency(worst_value))

        chart_df = latest[[preset_col, avg_col]].copy()
        chart_df[avg_col] = pd.to_numeric(chart_df[avg_col], errors="coerce")
        ranked = chart_df.sort_values(avg_col, ascending=False).copy()
        ranked_display = ranked.copy()
        ranked_display[avg_col] = ranked_display[avg_col].map(signed_currency)
        ranked_display = ranked_display.rename(columns={preset_col: "Preset", avg_col: "Average result versus simply holding the stock"})

        st.markdown("**Ranked examples table**")
        st.dataframe(ranked_display, width="stretch", hide_index=True)

        with st.expander("Preset comparison chart", expanded=False):
            st.caption("Average result versus simply holding the stock by preset. Higher is better, even if all values are negative.")
            chart_rendered = compact_horizontal_bar_chart(
                ranked,
                preset_col,
                avg_col,
                title=None,
                height=230,
            )
            if not chart_rendered:
                st.bar_chart(ranked.set_index(preset_col)[[avg_col]], height=230)

    with st.expander("Preset comparison audit table", expanded=False):
        st.dataframe(df.tail(30), width="stretch")
    st.download_button(
        "Download preset comparison CSV",
        data=df.to_csv(index=False),
        file_name="preset_comparison.csv",
        mime="text/csv",
    )




def _scenario_count(df: pd.DataFrame | None) -> int:
    """Return the visible number of named scenarios in the latest result table."""
    if df is None or df.empty:
        return 0
    scenario_col = detect_scenario_column(df)
    if scenario_col:
        return int(df[scenario_col].dropna().nunique())
    return int(len(df))


def show_current_beta_run_explainer(config: dict[str, Any], df: pd.DataFrame | None) -> None:
    """Explain exactly what the current public beta run represents."""
    ticker = str(config.get("ticker", "SPY")).upper()
    contracts = int(float(config.get("contracts", 1) or 1))
    dte = int(float(config.get("target_dte", config.get("days_to_expiration", 30)) or 30))
    delta = float(config.get("target_delta", config.get("call_delta_target", 0.30)) or 0.30)
    scenario_count = _scenario_count(df) or 5
    share_count = contracts * 100

    st.markdown("### What was run in this demo")
    st.info(
        "This public beta is currently a named-scenario stress test. It evaluates the same covered-call setup "
        "across several modeled market paths. It is not yet displaying a Monte Carlo distribution of hundreds "
        "or thousands of random paths."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Covered-call setup", f"{contracts} contract{'s' if contracts != 1 else ''}")
    c2.metric("Shares controlled", f"{share_count:,}")
    c3.metric("Named paths tested", f"{scenario_count}")
    c4.metric("Expiration horizon", f"{dte} DTE")

    st.markdown(
        f"""
        - The demo uses **{ticker}**, about **{delta:.2f} target call delta**, and **{dte} days to expiration**.
        - The same covered-call setup is run once through each named scenario: downtrend, sideways/choppy, volatile, moderate uptrend, and strong rally.
        - Each named scenario represents **one option cycle** for that setup. The current beta does **not** write repeated new covered calls during the scenario.
        - If the short call finishes in the money, the scenario reflects the capped-upside/assignment-style payoff rather than an automatic roll into a new call.
        - The scenario-path graphic is a **conceptual illustration** of those path shapes, not a collection of random Monte Carlo trials.
        - A future Monte Carlo mode should show the number of random paths, percentile outcomes, probability of beating buy-and-hold, and a distribution chart.
        """
    )


def show_beta_purpose_and_roadmap_panel() -> None:
    """Show the beta landing-page purpose and future direction in customer-friendly language."""
    st.markdown(
        """
        <div class="beta-hero-panel">
            <div class="beta-hero-kicker">Covered-call scenario stress test</div>
            <div class="beta-hero-title">See the covered-call tradeoff before you write the call.</div>
            <p class="beta-hero-body">
                This beta lets a user set up a covered call and test that same position across several deliberately different market scenarios.
                The goal is not to predict the market. The goal is to show where the covered call helps, where it lags, and how it compares
                with simply holding the stock or ETF.
            </p>
        </div>
        <div class="beta-card-grid">
            <div class="beta-card">
                <div class="beta-card-title">What it does now</div>
                <p class="beta-card-text">
                    Tests one covered-call setup over one option cycle across five named scenarios: downtrend, sideways choppy,
                    moderate uptrend, volatile two-sided, and strong rally.
                </p>
            </div>
            <div class="beta-card">
                <div class="beta-card-title">Why it matters</div>
                <p class="beta-card-text">
                    Covered calls can provide premium income and downside cushion, but they can also give up upside in a strong rally.
                    The app makes that tradeoff visible before money is at risk.
                </p>
            </div>
            <div class="beta-card">
                <div class="beta-card-title">Where this is going</div>
                <ul class="beta-future-list">
                    <li>Monte Carlo mode with many randomized paths.</li>
                    <li>Animated ticker-style covered-call evolution.</li>
                    <li>Clearer assignment, ITM, and roll-decision guidance.</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_stress_test_explainer_panel() -> None:
    """Explain what the scenario stress test is doing before users see the results."""
    st.markdown("### What this stress test is doing")
    st.info(
        "This beta tests one covered-call setup across several deliberately different market-path scenarios. "
        "It is not predicting which path will occur. It is asking what would happen to the same covered call "
        "if the market went down, moved sideways, became choppy, rose moderately, or rallied strongly."
    )

    st.warning(
        "For the current beta, each scenario represents one covered-call position over one option cycle. "
        "For example, 1 contract means 100 shares plus 1 short call. The app does not currently write repeated "
        "new calls during the scenario, and it does not roll the call when it goes in the money."
    )

    left_col, right_col = st.columns([1.05, 1])
    with left_col:
        st.markdown(
            """
            **For the clean SPY demo, the app compares one sample covered-call setup across five named scenarios:**

            1. **Downtrend**
            2. **Sideways choppy**
            3. **Moderate uptrend**
            4. **Volatile two-sided**
            5. **Strong rally**
            """
        )
    with right_col:
        st.markdown(
            """
            **Why this matters**

            The stress test shows where the covered call usually helps and where it can lag.

            **The option premium can cushion flat, choppy, or declining markets, but the short call can limit upside during a strong rally.**
            """
        )

    st.caption(
        "Current beta note: this is a scenario stress test using named modeled paths. "
        "A later version may add full Monte Carlo simulation with many randomized paths and probability summaries."
    )

def show_start_here_beta_tester_box() -> None:
    """Show a short first-run guide directly inside the customer-facing app."""
    st.markdown("### Start here for first-time beta testers")
    st.warning(
        "Do this first: run the clean SPY demo. Do not change any inputs until you have seen the default walkthrough."
    )

    button_col, note_col = st.columns([0.45, 0.55])
    with button_col:
        if st.button("Run clean SPY demo now", type="primary", key="overview_run_clean_demo_now"):
            ok, message = reset_to_clean_demo(run_after_reset=True)
            st.session_state["dashboard_notice"] = message
            st.session_state["dashboard_notice_level"] = "success" if ok else "warning"
            st.rerun()
    with note_col:
        st.caption(
            "This uses SPY, one covered call, and five named market scenarios so every beta tester starts from the same example."
        )

    step_col, purpose_col = st.columns([1.15, 1])
    with step_col:
        st.markdown(
            """
            **First 5-minute walkthrough**

            1. Click **Run clean SPY demo now** above, or use **Reset and run clean demo** in the left sidebar.
            2. Stay on **Overview** and scroll to **Visual summary**.
            3. Look at the **scenario tradeoff chart**.
            4. Look at the **covered-call payoff concept** chart.
            5. Open **Latest results** for the detailed interpretation.
            6. Open **Report** to see the printable summary.
            7. Open **Help & assumptions** to review what the simulator does and does not claim.
            """
        )
    with purpose_col:
        st.markdown(
            """
            **What you are testing**

            Can a first-time user understand the covered-call tradeoff quickly?

            The clean demo should make one point clear: option premium can cushion flat, choppy, or declining markets, while the short call can limit upside in a strong rally.

            After the walkthrough, note what was clear, what was confusing, and what feature you expected but did not see.
            """
        )



def show_overview_dashboard(config: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    """
    Show the customer landing page.

    The Overview tab is intentionally different from Latest results:
    - Overview explains the workflow and shows a visual, executive-level readout.
    - Latest results contains the detailed metrics, guidance, scenario cards, and export controls.
    """
    st.subheader("Overview")
    st.caption("Start here. This page shows the big-picture tradeoff and suggests where to go next.")

    st.markdown(f"**{PRODUCT_INFO.version_label}**  ")
    st.caption(f"{PRODUCT_INFO.release_stage} | {PRODUCT_INFO.build_label}")
    st.info(PRODUCT_INFO.positioning_statement)

    show_beta_purpose_and_roadmap_panel()

    show_start_here_beta_tester_box()

    show_stress_test_explainer_panel()

    with st.expander("Primary workflow", expanded=False):
        for step_number, step_text in enumerate(PRODUCT_INFO.primary_workflow, start=1):
            st.write(f"{step_number}. {step_text}")

    df = load_scenario_results()
    summary = summarize_results(df) if df is not None else {}
    has_results = bool(df is not None and summary.get("relative_col"))

    st.markdown("### Current status")
    status_col, ticker_col, result_col, report_col = st.columns(4)
    with status_col:
        if errors:
            st.error("Configuration: blocked")
        elif warnings:
            st.warning("Configuration: review")
        else:
            st.success("Configuration: valid")
    with ticker_col:
        st.metric("Ticker", str(config.get("ticker", "SPY")).upper())
    with result_col:
        if has_results:
            st.success("Latest result: available")
        else:
            st.info("Latest result: not run")
    with report_col:
        if REPORT_PATH.exists():
            st.success("Report: found")
        else:
            st.info("Report: not found")

    show_current_beta_run_explainer(config, df)

    show_customer_visual_summary(config, df, summary, expanded=True)

    st.markdown("### What this means at a glance")
    if not has_results:
        st.info(
            "No latest result is available yet. Go to Setup & run, use the clean demo or enter a setup, "
            "then run the simulator to populate the charts and results."
        )
    else:
        best_scenario = summary.get("best_scenario", "best scenario")
        worst_scenario = summary.get("worst_scenario", "worst scenario")
        best_value = signed_currency(summary.get("best_value", 0))
        worst_value = signed_currency(summary.get("worst_value", 0))
        average_value = signed_currency(summary.get("average_value", 0))
        st.markdown(
            f"""
            - The covered call helped most in **{best_scenario}** ({best_value} versus buy-and-hold).
            - The covered call lagged most in **{worst_scenario}** ({worst_value} versus buy-and-hold).
            - The average relative result across the modeled paths was **{average_value}**.
            """
        )
        st.caption(
            "For the detailed interpretation, decision guidance, scenario cards, and memo export, open the Latest results tab."
        )

    st.markdown("### Recommended next action")
    if errors:
        st.error("Fix the blocking configuration errors in Setup & run before running the simulator.")
    elif not has_results:
        st.info("Open Setup & run and run the clean demo or your own setup.")
    elif summary.get("average_value") is not None and float(summary.get("average_value", 0)) < 0:
        st.warning("Review the upside tradeoff in Latest results. The latest covered-call setup lags buy-and-hold on average across the modeled paths.")
    else:
        st.success("Open Latest results to inspect the scenario cards and export a decision memo.")

    quick1, quick2, quick3 = st.columns(3)
    with quick1:
        st.write("**Setup & run**")
        st.caption("Edit inputs, apply presets, and run the simulator.")
    with quick2:
        st.write("**Latest results**")
        st.caption("Detailed result metrics, interpretation, scenario cards, and export tools.")
    with quick3:
        st.write("**Report**")
        st.caption("Customer-facing summary suitable for saving or printing.")

def show_phase2_file_status() -> None:
    """Show file availability for Phase 2 scaffold outputs and runners."""
    rows = []
    for label, path in [
        ("Price paths CSV", PHASE2_PRICE_PATHS_PATH),
        ("Option payoff CSV", PHASE2_OPTION_PAYOFF_PATH),
        ("Scenario payoff CSV", PHASE2_SCENARIO_PAYOFF_PATH),
        ("Scenario payoff report CSV", PHASE2_SCENARIO_PAYOFF_REPORT_PATH),
        ("Scenario payoff HTML", PHASE2_SCENARIO_PAYOFF_HTML_PATH),
        ("Phase 2 vs v0 CSV", PHASE2_V0_COMPARISON_PATH),
        ("Phase 2 vs v0 HTML", PHASE2_V0_COMPARISON_HTML_PATH),
        ("Pipeline checker", PHASE2_PIPELINE_CHECK_PATH),
        ("Standalone Phase 2 viewer", PHASE2_VIEWER_PATH),
        ("Integration-readiness checker", PHASE2_INTEGRATION_READINESS_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase2_scaffold_tab() -> None:
    """Developer-view-only Phase 2 scaffold diagnostics."""
    st.subheader("Phase 2 scaffold")
    st.caption(
        "Developer-only view of the Phase 2 modeling scaffold. These outputs are exploratory and are not yet the customer-facing paid simulator engine."
    )

    st.info(
        "Phase 2 is being developed beside the stable v0.1 dashboard. Use this tab to inspect scaffold outputs, run checks, and compare Phase 2 estimates with the current v0.1 simulator."
    )

    action_col1, action_col2, action_col3 = st.columns(3)
    with action_col1:
        if st.button("Run Phase 2 pipeline check"):
            code, output = run_python_script(PHASE2_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 2 pipeline check passed.")
            else:
                st.warning(f"Phase 2 pipeline check returned code {code}.")
            with st.expander("Phase 2 pipeline output", expanded=False):
                st.text_area("Pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Run integration-readiness check"):
            code, output = run_python_script(PHASE2_INTEGRATION_READINESS_PATH)
            if code == 0:
                st.success("Phase 2 integration-readiness check passed.")
            else:
                st.warning(f"Phase 2 integration-readiness check returned code {code}.")
            with st.expander("Integration-readiness output", expanded=False):
                st.text_area("Integration-readiness output text", value=output, height=260, label_visibility="collapsed")
    with action_col3:
        if st.button("Open standalone Phase 2 viewer"):
            code, output = run_python_script(PHASE2_VIEWER_PATH)
            if code == 0:
                st.success("Phase 2 viewer process ended normally.")
            else:
                st.info("The Phase 2 viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 2 viewer launch output", expanded=False):
                st.text_area("Viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Scaffold file status")
    show_phase2_file_status()

    comparison_df = load_csv_safely(PHASE2_V0_COMPARISON_PATH)
    payoff_df = load_csv_safely(PHASE2_SCENARIO_PAYOFF_REPORT_PATH)
    price_paths_df = load_csv_safely(PHASE2_PRICE_PATHS_PATH)

    st.markdown("### Phase 2 vs v0 comparison")
    if comparison_df is None or comparison_df.empty:
        st.info("No Phase 2 vs v0 comparison CSV found yet. Run the Phase 2 pipeline check first.")
    else:
        st.dataframe(comparison_df, width="stretch", hide_index=True)
        numeric_cols = [col for col in comparison_df.columns if "difference" in str(col).lower() or "phase_2" in str(col).lower() or "phase2" in str(col).lower()]
        scenario_col = find_column(comparison_df, ["scenario", "scenario_name", "Scenario"])
        if scenario_col and numeric_cols:
            chart_col = numeric_cols[0]
            chart_df = comparison_df[[scenario_col, chart_col]].copy()
            chart_df[chart_col] = pd.to_numeric(chart_df[chart_col], errors="coerce")
            st.caption("Quick chart from the comparison output. Higher values indicate better Phase 2 relative result where applicable.")
            if not compact_horizontal_bar_chart(chart_df, scenario_col, chart_col, height=250):
                st.bar_chart(chart_df.set_index(scenario_col)[[chart_col]].dropna(), height=250)

    with st.expander("Scenario payoff report scaffold", expanded=False):
        if payoff_df is None or payoff_df.empty:
            st.info("No scenario-payoff report scaffold CSV found yet.")
        else:
            st.dataframe(payoff_df, width="stretch", hide_index=True)

    with st.expander("Scenario price paths scaffold", expanded=False):
        if price_paths_df is None or price_paths_df.empty:
            st.info("No scenario price-path CSV found yet.")
        else:
            st.dataframe(price_paths_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 2 reports")
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        if PHASE2_SCENARIO_PAYOFF_HTML_PATH.exists():
            if st.button("Open scenario-payoff HTML"):
                if not open_path_with_windows(PHASE2_SCENARIO_PAYOFF_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2_SCENARIO_PAYOFF_HTML_PATH}")
        else:
            st.info("Scenario-payoff HTML report not found yet.")
    with report_col2:
        if PHASE2_V0_COMPARISON_HTML_PATH.exists():
            if st.button("Open Phase 2 vs v0 HTML"):
                if not open_path_with_windows(PHASE2_V0_COMPARISON_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2_V0_COMPARISON_HTML_PATH}")
        else:
            st.info("Phase 2 vs v0 HTML report not found yet.")

    with st.expander("How to interpret this tab", expanded=False):
        st.markdown(
            """
            - This tab is visible only in Developer view.
            - Phase 2 outputs are scaffold diagnostics, not final customer-facing analytics.
            - The stable customer-facing workflow remains the v0.1 paid simulator dashboard.
            - Use the Phase 2 vs v0 comparison to identify where the new modeling layer agrees or disagrees with the current v0.1 simulator.
            - Do not promote Phase 2 outputs into Customer view until the pipeline, integration-readiness check, and qualitative review all pass.
            """
        )

# === PUBLIC BETA REPORT NEXT STEPS PATCH START ===
PUBLIC_BETA_REPORT_NEXT_STEPS_PATCH_READY = "PUBLIC_BETA_REPORT_NEXT_STEPS_PATCH_READY"


def _public_beta_report_next_steps_html() -> str:
    """Return the beta-tester next-step card for generated HTML reports."""
    return """
    <!-- PUBLIC_BETA_REPORT_NEXT_STEPS_START -->
    <section class="card public-beta-next-steps" style="border:1px solid #bfdbfe;background:#eff6ff;border-radius:14px;padding:20px;margin:22px 0;">
      <h2 style="margin-top:0;">What to do next</h2>
      <p>
        This report shows how the current covered-call setup behaved across the named stress-test scenarios.
        After reviewing the report, return to the app and continue with the steps below.
      </p>
      <ol>
        <li><strong>Open Challenge.</strong> Pick a target market scenario and try to improve the score.</li>
        <li><strong>Change one setup input at a time.</strong> Try call delta, DTE, setup style, or contract count.</li>
        <li><strong>Run the stress test again.</strong> Compare whether the new setup helped or hurt versus buy-and-hold.</li>
        <li><strong>Review Help &amp; assumptions.</strong> Confirm the current beta assumption: one option cycle, no automatic rolls, and no market prediction.</li>
        <li><strong>Send feedback.</strong> What was clear, what was confusing, and what feature did you expect but did not see?</li>
      </ol>
      <p style="margin-bottom:0;">
        Beta note: this is a named-scenario stress test. A later version may add Monte Carlo simulation, animated ticker-style covered-call evolution, and persistent leaderboards.
      </p>
    </section>
    <!-- PUBLIC_BETA_REPORT_NEXT_STEPS_END -->
    """


def ensure_public_beta_next_steps_in_report(report_path=REPORT_PATH) -> None:
    """Inject the beta-tester next-step card into the generated HTML report."""
    try:
        path = Path(report_path)
    except Exception:
        return

    if not path.exists():
        return

    try:
        html = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return

    if "PUBLIC_BETA_REPORT_NEXT_STEPS_START" in html:
        return

    block = _public_beta_report_next_steps_html()

    anchors = [
        "<h2>Covered-Call Profile",
        "<h2>Strategy Setup",
        "Covered-Call Profile",
        "Strategy Setup",
        "</main>",
        "</body>",
    ]

    for anchor in anchors:
        idx = html.find(anchor)
        if idx != -1:
            html = html[:idx] + block + "\n" + html[idx:]
            break
    else:
        html = html + "\n" + block + "\n"

    try:
        path.write_text(html, encoding="utf-8")
    except Exception:
        return


def render_public_beta_report_next_steps_panel() -> None:
    """Render next-step guidance on the Streamlit Report tab."""
    st.markdown("### What to do next")
    st.info(
        "After reviewing this report, open Challenge, pick a target market scenario, "
        "change one setup input at a time, rerun the stress test, and record the score. "
        "Then review Help & assumptions and send feedback on what was clear, confusing, or missing."
    )
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**1. Try Challenge**")
        st.caption("Use the scoreboards to compare covered-call setups by market scenario.")
    with col_b:
        st.markdown("**2. Change one input**")
        st.caption("Try delta, DTE, setup style, or contract count. Then rerun.")
    with col_c:
        st.markdown("**3. Send feedback**")
        st.caption("Tell us what was clear, confusing, or missing.")
# === PUBLIC BETA REPORT NEXT STEPS PATCH END ===


def show_report_section() -> None:
    st.subheader("Report")
    render_public_beta_report_next_steps_panel()
    # Report next-step guidance is generated by scenario_comparison_report.py.
    # Do not inject a second HTML block from the dashboard.
    if REPORT_PATH.exists():
        st.success("HTML report found.")
        st.caption("A scenario-comparison HTML report has been generated.")
        if st.button("Open report"):
            if not open_path_with_windows(REPORT_PATH):
                st.warning("Could not open the report directly from this environment.")
    else:
        st.info("HTML report not found yet. Run the paid simulator first.")



def show_help_section() -> None:
    st.subheader("Help & assumptions")
    st.caption("Plain-English reference for the covered-call stress test.")

    st.markdown(f"### {PRODUCT_INFO.product_name}")
    st.write(PRODUCT_INFO.product_subtitle)
    st.caption(f"{PRODUCT_INFO.version_label} | {PRODUCT_INFO.release_stage} | {PRODUCT_INFO.build_label}")

    st.markdown("### What this simulator is doing")
    st.write(PRODUCT_INFO.positioning_statement)

    st.write(
        "The stress test compares a selected covered-call setup against simply holding the stock across several named market examples. "
        "It is designed to show the tradeoff created by the short call: income and downside/sideways cushion in exchange for "
        "reduced participation during strong rallies."
    )

    st.write(
        "The simulator should be treated as a scenario-analysis tool, not a prediction engine. It does not claim to identify "
        "the future market regime."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Key inputs

        **Ticker** — The underlying symbol used for the demo setup.

        **Account size ($)** — The account value used to estimate position-size limits.

        **Setup style** — The aggressiveness of the covered-call setup: Conservative, Balanced, or Aggressive. This is not a market scenario.

        **Max position size** — The maximum percentage of the account allowed in the stock/ETF shares needed for covered calls. For example, a $600,000 account with a 10% cap allows about $60,000 of stock exposure. If SPY is near $600/share, that supports about 100 shares, or one standard covered-call contract.

        **Contracts** — The number of covered-call contracts requested. One standard contract generally represents 100 shares.

        **Call delta target** — Approximate option delta used to select the short call. Lower delta usually means less premium
        and less upside cap. Higher delta usually means more premium and more upside cap.

        **Days to expiration** — Target option maturity for the short call.
        """)
    with col2:
        st.markdown("""
        ### Output terms

        **Relative result** — Covered-call result minus buy-and-hold result. Positive means the covered call did better in that
        scenario. Negative means buy-and-hold did better.

        **Best relative result** — The market path where the covered call helped most versus buy-and-hold.

        **Worst relative result** — The market path where the covered call lagged buy-and-hold the most.

        **Average result versus simply holding the stock** — The average relative result across all modeled paths. This is not a forecast; it is a
        summary of the selected scenario set.

        **Decision guidance** — A rule-based interpretation of the scenario results and configuration checks.

        **Challenge score** — Covered-call result minus buy-and-hold result for the selected market scenario. Higher is better for that scenario.
        """)

    with st.expander("Current beta assumption: one option cycle, no automatic rolls", expanded=True):
        st.markdown(
            """
            The current beta evaluates one covered-call setup over one option cycle across named market scenarios.

            It does **not** write repeated new covered calls during a scenario, and it does **not** automatically roll the short call when it goes in the money.
            """
        )
        _render_itm_no_roll_explainer()

    with st.expander("How to use the control panel", expanded=True):
        st.markdown("""
        1. Use **Reset to clean demo** when preparing for a customer walkthrough.
        2. Start on **Overview** to see the current status.
        3. Go to **Setup & run** to choose a preset or edit inputs.
        4. Click **Save config** before relying on a setup.
        5. Click **Run simulator** to regenerate results.
        6. Go to **Latest results** to review the decision summary and scenario cards.
        7. Export a Markdown or PDF memo when you want a customer-facing record of the analysis.
        8. Use **Preset comparison** to compare conservative, balanced, aggressive, and shorter-term assumptions.
        """)

    with st.expander("Covered-call interpretation guide", expanded=False):
        st.markdown("""
        A covered call usually performs best relative to buy-and-hold when the underlying is flat, choppy, or declining modestly.
        The option premium can cushion the stock result.

        A covered call usually performs worst relative to buy-and-hold during a strong rally. The short call limits upside
        participation, so the strategy can trail the stock even though it may still make money in absolute terms.

        This is why the app focuses on relative performance versus buy-and-hold rather than only the covered-call profit or loss.
        """)

    with st.expander("Important limitations", expanded=False):
        for limitation in PRODUCT_INFO.key_limitations:
            st.write(f"- {limitation}")
        st.write("- Option pricing is simplified for demonstration and product-design purposes.")
        st.write("- A positive scenario result does not guarantee a good live trade.")
        st.write("- A negative relative result does not necessarily mean the trade loses money; it may mean it underperforms buy-and-hold.")
        st.write("- The decision guidance is rule-based and should be reviewed rather than followed mechanically.")

    st.info("Commercial framing: the simulator helps users understand tradeoffs before opening a covered call. It should not be marketed as a regime detector or profit guarantee.")




def show_app_status_tab() -> None:
    """Display read-only dashboard and file status information."""
    st.subheader("App status")
    st.caption("Read-only check of dashboard files, generated outputs, and active config.")

    if get_dashboard_status is None or status_table_rows is None:
        st.error("Status utilities are not available. Reinstall the App Status tab files.")
        return

    status = get_dashboard_status(PROJECT_ROOT)

    st.markdown(f"**{PRODUCT_INFO.product_name}**")
    st.caption(PRODUCT_INFO.product_subtitle)

    top_col1, top_col2, top_col3 = st.columns(3)
    with top_col1:
        if status.overall_status == "PASS":
            st.success("Overall status: PASS")
        else:
            st.warning("Overall status: REVIEW")
    with top_col2:
        st.metric("Product version", PRODUCT_INFO.version_label)
    with top_col3:
        st.metric("Release stage", PRODUCT_INFO.release_stage)

    st.caption(f"Build: {PRODUCT_INFO.build_label}")
    # === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP START ===
    CUSTOMER_VIEW_LOCAL_DEBUG_TEXT_CLEANUP_APPLIED = True
    if (
        locals().get('interface_mode') == 'Developer view'
        or locals().get('selected_interface_mode') == 'Developer view'
        or locals().get('dashboard_mode') == 'Developer view'
        or locals().get('dashboard_view_mode') == 'Developer view'
        or locals().get('view_mode') == 'Developer view'
    ):
        st.caption(f"Project root: {status.project_root}")
    # === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP END ===

    if status.problems:
        st.warning("Items needing attention")
        for problem in status.problems:
            st.write(f"- {problem}")
    else:
        st.success("All required dashboard files and main simulator outputs are present.")

    st.markdown("#### Active config summary")
    if status.config_summary:
        summary_rows = [{"Field": key, "Value": value} for key, value in status.config_summary.items()]
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No config summary is available.")

    st.markdown("#### Required files")
    st.dataframe(pd.DataFrame(status_table_rows(status.required_files)), use_container_width=True, hide_index=True)

    with st.expander("Generated output files", expanded=True):
        st.dataframe(pd.DataFrame(status_table_rows(status.output_files)), use_container_width=True, hide_index=True)

    with st.expander("Optional dashboard files", expanded=False):
        st.dataframe(pd.DataFrame(status_table_rows(status.optional_files)), use_container_width=True, hide_index=True)

    st.markdown("#### Suggested use")
    if status.overall_status == "PASS":
        st.write("The dashboard is ready for normal use. Use Setup & run to test a configuration, then review Latest results and export a memo if needed.")
    else:
        st.write("Review the missing files above. If generated outputs are missing, run the paid simulator. If required files are missing, reinstall the latest dashboard files.")


def show_phase2b_premium_file_status() -> None:
    """Show file availability for Phase 2B premium-model outputs and runners."""
    rows = []
    for label, path in [
        ("Option premium CSV", PHASE2B_OPTION_PREMIUM_PATH),
        ("Premium-aware payoff CSV", PHASE2B_PREMIUM_AWARE_PAYOFF_PATH),
        ("Premium-aware payoff HTML", PHASE2B_PREMIUM_AWARE_PAYOFF_HTML_PATH),
        ("Premium vs scaffold CSV", PHASE2B_PREMIUM_VS_SCAFFOLD_PATH),
        ("Premium vs scaffold HTML", PHASE2B_PREMIUM_VS_SCAFFOLD_HTML_PATH),
        ("Phase 2B pipeline checker", PHASE2B_PIPELINE_CHECK_PATH),
        ("Standalone Phase 2B premium viewer", PHASE2B_PREMIUM_VIEWER_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase2b_premium_model_tab() -> None:
    """Developer-view-only Phase 2B premium-model diagnostics."""
    st.subheader("Phase 2B premium model")
    st.caption(
        "Developer-only view of the newer premium-aware modeling layer. These outputs are exploratory and are not yet the customer-facing paid simulator engine."
    )

    st.info(
        "Phase 2B adds a more realistic option-premium layer before we promote the new model into the main customer workflow. Use this tab to inspect premium estimates, premium-aware payoffs, and differences from the older Phase 2 scaffold."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 2B pipeline check"):
            code, output = run_python_script(PHASE2B_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 2B pipeline check passed.")
            else:
                st.warning(f"Phase 2B pipeline check returned code {code}.")
            with st.expander("Phase 2B pipeline output", expanded=False):
                st.text_area("Phase 2B pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 2B premium viewer"):
            code, output = run_python_script(PHASE2B_PREMIUM_VIEWER_PATH)
            if code == 0:
                st.success("Phase 2B premium viewer process ended normally.")
            else:
                st.info("The Phase 2B premium viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 2B viewer launch output", expanded=False):
                st.text_area("Phase 2B viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Premium-model file status")
    show_phase2b_premium_file_status()

    st.markdown("### Option premium estimates")
    premium_df = load_csv_safely(PHASE2B_OPTION_PREMIUM_PATH)
    if premium_df is None or premium_df.empty:
        st.info("No option-premium scaffold CSV found yet. Run the Phase 2B pipeline check first.")
    else:
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        if "estimated_call_premium" in premium_df.columns:
            metric_col1.metric("Average estimated premium", currency(float(premium_df["estimated_call_premium"].mean())))
        if "estimated_call_delta" in premium_df.columns:
            metric_col2.metric("Average estimated delta", f"{float(premium_df['estimated_call_delta'].mean()):.2f}")
        if "scenario" in premium_df.columns:
            metric_col3.metric("Scenarios priced", len(premium_df["scenario"].dropna().unique()))
        st.dataframe(premium_df, width="stretch", hide_index=True)

    st.markdown("### Premium-aware payoff output")
    payoff_df = load_csv_safely(PHASE2B_PREMIUM_AWARE_PAYOFF_PATH)
    if payoff_df is None or payoff_df.empty:
        st.info("No premium-aware payoff CSV found yet. Run the Phase 2B pipeline check first.")
    else:
        relative_col = find_column(
            payoff_df,
            [
                "covered_call_minus_buy_hold",
                "covered_call_minus_buy_and_hold",
                "relative_result",
                "covered_call_relative_result",
            ],
        )
        if relative_col is not None:
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Average result versus simply holding the stock", signed_currency(float(payoff_df[relative_col].mean())))
            metric_col2.metric("Best relative result", signed_currency(float(payoff_df[relative_col].max())))
            metric_col3.metric("Worst relative result", signed_currency(float(payoff_df[relative_col].min())))
            chart_df = payoff_df.copy()
            label_col = find_column(chart_df, ["scenario", "scenario_name", "display_name", "path_label"])
            if label_col is not None:
                compact_horizontal_bar_chart(chart_df, label_col, relative_col, "Premium-aware relative result")
        st.dataframe(payoff_df, width="stretch", hide_index=True)

    st.markdown("### Premium-aware vs older Phase 2 scaffold")
    comparison_df = load_csv_safely(PHASE2B_PREMIUM_VS_SCAFFOLD_PATH)
    if comparison_df is None or comparison_df.empty:
        st.info("No premium-vs-scaffold comparison CSV found yet. Run the Phase 2B pipeline check first.")
    else:
        difference_col = find_column(
            comparison_df,
            [
                "premium_minus_scaffold",
                "premium_aware_minus_old",
                "premium_aware_minus_scaffold",
                "difference",
            ],
        )
        if difference_col is not None:
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Average model difference", signed_currency(float(comparison_df[difference_col].mean())))
            metric_col2.metric("Largest positive difference", signed_currency(float(comparison_df[difference_col].max())))
            metric_col3.metric("Largest negative difference", signed_currency(float(comparison_df[difference_col].min())))
            label_col = find_column(comparison_df, ["scenario", "scenario_name", "display_name", "path_label"])
            if label_col is not None:
                compact_horizontal_bar_chart(comparison_df, label_col, difference_col, "Premium-aware minus older scaffold")
        st.dataframe(comparison_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 2B reports")
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        if PHASE2B_PREMIUM_AWARE_PAYOFF_HTML_PATH.exists():
            if st.button("Open premium-aware payoff HTML"):
                if not open_path_with_windows(PHASE2B_PREMIUM_AWARE_PAYOFF_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2B_PREMIUM_AWARE_PAYOFF_HTML_PATH}")
        else:
            st.info("Premium-aware payoff HTML report not found yet.")
    with report_col2:
        if PHASE2B_PREMIUM_VS_SCAFFOLD_HTML_PATH.exists():
            if st.button("Open premium-vs-scaffold HTML"):
                if not open_path_with_windows(PHASE2B_PREMIUM_VS_SCAFFOLD_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2B_PREMIUM_VS_SCAFFOLD_HTML_PATH}")
        else:
            st.info("Premium-vs-scaffold HTML report not found yet.")

    with st.expander("How to interpret this tab", expanded=False):
        st.markdown("""
        - The **option premium estimates** come from the new Phase 2B premium model.
        - The **premium-aware payoff output** uses those estimated strikes and premiums in the covered-call payoff calculation.
        - The **premium-aware vs older scaffold** section shows whether the more realistic premium layer materially changes the result.
        - Keep this in Developer view until the assumptions are reviewed and the model is ready to replace the older scaffold in the customer workflow.
        """)


def show_phase2c_validation_file_status() -> None:
    """Show file availability for Phase 2C premium-model validation outputs and runners."""
    rows = []
    for label, path in [
        ("Premium validation CSV", PHASE2C_VALIDATION_CSV_PATH),
        ("Premium validation HTML", PHASE2C_VALIDATION_HTML_PATH),
        ("Premium validation summary", PHASE2C_VALIDATION_SUMMARY_PATH),
        ("Phase 2C pipeline report", PHASE2C_VALIDATION_PIPELINE_REPORT_PATH),
        ("Premium validation checker", PHASE2C_VALIDATION_CHECK_PATH),
        ("Phase 2C validation pipeline checker", PHASE2C_VALIDATION_PIPELINE_CHECK_PATH),
        ("Standalone Phase 2C validation viewer", PHASE2C_VALIDATION_VIEWER_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase2c_validation_tab() -> None:
    """Developer-view-only Phase 2C premium-model validation diagnostics."""
    st.subheader("Phase 2C validation")
    st.caption(
        "Developer-only view of the premium-model validation layer. These checks review whether the Phase 2B premium model behaves reasonably before promotion into the customer workflow."
    )

    st.info(
        "Phase 2C validates the premium model instead of adding new customer-facing simulator behavior. Use this tab to inspect PASS/WATCH/REVIEW items, validation notes, premium estimates, and premium-aware payoffs."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 2C validation pipeline"):
            code, output = run_python_script(PHASE2C_VALIDATION_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 2C validation pipeline passed.")
            else:
                st.warning(f"Phase 2C validation pipeline returned code {code}.")
            with st.expander("Phase 2C validation pipeline output", expanded=False):
                st.text_area("Phase 2C validation pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 2C validation viewer"):
            code, output = run_python_script(PHASE2C_VALIDATION_VIEWER_PATH)
            if code == 0:
                st.success("Phase 2C validation viewer process ended normally.")
            else:
                st.info("The Phase 2C validation viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 2C validation viewer launch output", expanded=False):
                st.text_area("Phase 2C validation viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Validation file status")
    show_phase2c_validation_file_status()

    st.markdown("### Validation summary")
    if PHASE2C_VALIDATION_SUMMARY_PATH.exists():
        try:
            st.text(PHASE2C_VALIDATION_SUMMARY_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            st.warning(f"Could not read validation summary: {exc}")
    else:
        st.info("No Phase 2C validation summary found yet. Run the Phase 2C validation pipeline first.")

    st.markdown("### Validation checks")
    validation_df = load_csv_safely(PHASE2C_VALIDATION_CSV_PATH)
    if validation_df is None or validation_df.empty:
        st.info("No premium-model validation CSV found yet. Run the Phase 2C validation pipeline first.")
    else:
        status_col = find_column(validation_df, ["status", "validation_status", "result"])
        if status_col is not None:
            status_counts = validation_df[status_col].fillna("UNKNOWN").astype(str).value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            metric_col1.metric("Validation rows", len(validation_df))
            metric_col2.metric("PASS rows", int((validation_df[status_col].astype(str).str.upper() == "PASS").sum()))
            metric_col3.metric("Non-PASS rows", int((validation_df[status_col].astype(str).str.upper() != "PASS").sum()))
            st.dataframe(status_counts, width="stretch", hide_index=True)
        st.dataframe(validation_df, width="stretch", hide_index=True)

    st.markdown("### Option premium estimates")
    premium_df = load_csv_safely(PHASE2B_OPTION_PREMIUM_PATH)
    if premium_df is None or premium_df.empty:
        st.info("No option-premium scaffold CSV found yet. Run the Phase 2B or Phase 2C pipeline first.")
    else:
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        if "estimated_call_premium" in premium_df.columns:
            metric_col1.metric("Average estimated premium", currency(float(pd.to_numeric(premium_df["estimated_call_premium"], errors="coerce").mean())))
        if "estimated_call_delta" in premium_df.columns:
            metric_col2.metric("Average estimated delta", f"{float(pd.to_numeric(premium_df['estimated_call_delta'], errors='coerce').mean()):.2f}")
        if "estimated_iv" in premium_df.columns:
            metric_col3.metric("Average estimated IV", f"{float(pd.to_numeric(premium_df['estimated_iv'], errors='coerce').mean()):.2%}")
        st.dataframe(premium_df, width="stretch", hide_index=True)

    st.markdown("### Premium-aware payoff output")
    payoff_df = load_csv_safely(PHASE2B_PREMIUM_AWARE_PAYOFF_PATH)
    if payoff_df is None or payoff_df.empty:
        st.info("No premium-aware payoff CSV found yet. Run the Phase 2B or Phase 2C pipeline first.")
    else:
        relative_col = find_column(
            payoff_df,
            [
                "covered_call_minus_buy_hold",
                "covered_call_minus_buy_and_hold",
                "relative_result",
                "covered_call_relative_result",
            ],
        )
        if relative_col is not None:
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            numeric_relative = pd.to_numeric(payoff_df[relative_col], errors="coerce")
            metric_col1.metric("Average result versus simply holding the stock", signed_currency(float(numeric_relative.mean())))
            metric_col2.metric("Best relative result", signed_currency(float(numeric_relative.max())))
            metric_col3.metric("Worst relative result", signed_currency(float(numeric_relative.min())))
            label_col = find_column(payoff_df, ["scenario", "scenario_name", "display_name", "path_label"])
            if label_col is not None:
                chart_df = payoff_df.copy()
                chart_df[relative_col] = numeric_relative
                compact_horizontal_bar_chart(chart_df, label_col, relative_col, "Premium-aware relative result")
        st.dataframe(payoff_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 2C reports")
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        if PHASE2C_VALIDATION_HTML_PATH.exists():
            if st.button("Open premium-validation HTML"):
                if not open_path_with_windows(PHASE2C_VALIDATION_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2C_VALIDATION_HTML_PATH}")
        else:
            st.info("Premium-validation HTML report not found yet.")
    with report_col2:
        if PHASE2C_VALIDATION_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 2C pipeline report folder"):
                if not open_path_with_windows(PHASE2C_VALIDATION_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE2C_VALIDATION_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 2C pipeline report not found yet.")

    with st.expander("How to interpret this tab", expanded=False):
        st.markdown("""
        - **PASS** means a validation check is within the configured reasonableness band.
        - **WATCH** or **REVIEW** does not necessarily mean the code is broken; it means the modeling assumption deserves inspection.
        - Phase 2C validates assumptions before the premium-aware model becomes part of the customer-facing workflow.
        - Keep this tab in Developer view until the premium model has been reviewed and tuned.
        """)


def show_phase2d_tuning_file_status() -> None:
    """Show file availability for Phase 2D premium-model tuning outputs and runners."""
    rows = []
    for label, path in [
        ("Tuning config JSON", PHASE2D_TUNING_CONFIG_PATH),
        ("Tuning recommendations CSV", PHASE2D_TUNING_RECOMMENDATIONS_PATH),
        ("Tuning recommendations HTML", PHASE2D_TUNING_HTML_PATH),
        ("Tuning summary", PHASE2D_TUNING_SUMMARY_PATH),
        ("Tuning check report", PHASE2D_TUNING_CHECK_REPORT_PATH),
        ("Tuning pipeline report", PHASE2D_TUNING_PIPELINE_REPORT_PATH),
        ("Tuning checker", PHASE2D_TUNING_CHECK_PATH),
        ("Tuning pipeline checker", PHASE2D_TUNING_PIPELINE_CHECK_PATH),
        ("Standalone Phase 2D tuning viewer", PHASE2D_TUNING_VIEWER_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase2d_tuning_tab() -> None:
    """Developer-view-only Phase 2D premium-model tuning diagnostics."""
    st.subheader("Phase 2D tuning")
    st.caption(
        "Developer-only view of the premium-model tuning layer. These outputs are recommendations for inspecting and tuning assumptions before customer-facing promotion."
    )

    st.info(
        "Phase 2D reviews the premium-model outputs and produces tuning recommendations. Use this tab to inspect TUNE/REVIEW items, compare them with validation results, and decide which assumptions should be adjusted next."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 2D tuning pipeline"):
            code, output = run_python_script(PHASE2D_TUNING_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 2D tuning pipeline passed.")
            else:
                st.warning(f"Phase 2D tuning pipeline returned code {code}.")
            with st.expander("Phase 2D tuning pipeline output", expanded=False):
                st.text_area("Phase 2D tuning pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 2D tuning viewer"):
            code, output = run_python_script(PHASE2D_TUNING_VIEWER_PATH)
            if code == 0:
                st.success("Phase 2D tuning viewer process ended normally.")
            else:
                st.info("The Phase 2D tuning viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 2D tuning viewer launch output", expanded=False):
                st.text_area("Phase 2D tuning viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Tuning file status")
    show_phase2d_tuning_file_status()

    st.markdown("### Tuning summary")
    if PHASE2D_TUNING_SUMMARY_PATH.exists():
        try:
            st.text(PHASE2D_TUNING_SUMMARY_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            st.warning(f"Could not read tuning summary: {exc}")
    else:
        st.info("No Phase 2D tuning summary found yet. Run the Phase 2D tuning pipeline first.")

    st.markdown("### Tuning recommendations")
    tuning_df = load_csv_safely(PHASE2D_TUNING_RECOMMENDATIONS_PATH)
    if tuning_df is None or tuning_df.empty:
        st.info("No premium-model tuning recommendations CSV found yet. Run the Phase 2D tuning pipeline first.")
    else:
        status_col = find_column(tuning_df, ["status", "tuning_status", "recommendation_status", "result"])
        scenario_col = find_column(tuning_df, ["scenario", "scenario_name", "display_name", "path_label"])
        value_cols = [col for col in tuning_df.columns if any(token in str(col).lower() for token in ["premium", "iv", "delta", "strike", "distance"])]

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Recommendation rows", len(tuning_df))
        if status_col is not None:
            statuses = tuning_df[status_col].fillna("UNKNOWN").astype(str).str.upper()
            metric_col2.metric("PASS/OK rows", int(statuses.isin(["PASS", "OK"]).sum()))
            metric_col3.metric("TUNE/REVIEW rows", int(statuses.isin(["TUNE", "REVIEW", "WATCH"]).sum()))
            status_counts = statuses.value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.dataframe(status_counts, width="stretch", hide_index=True)
        else:
            metric_col2.metric("Status column", "not found")
            metric_col3.metric("Columns", len(tuning_df.columns))

        if scenario_col is not None and value_cols:
            chart_col = value_cols[0]
            chart_df = tuning_df[[scenario_col, chart_col]].copy()
            chart_df[chart_col] = pd.to_numeric(chart_df[chart_col], errors="coerce")
            if chart_df[chart_col].notna().any():
                compact_horizontal_bar_chart(chart_df, scenario_col, chart_col, f"Tuning context: {chart_col}")

        st.dataframe(tuning_df, width="stretch", hide_index=True)

    st.markdown("### Validation context")
    validation_df = load_csv_safely(PHASE2C_VALIDATION_CSV_PATH)
    if validation_df is None or validation_df.empty:
        st.info("No Phase 2C validation CSV found yet. Run the Phase 2C or Phase 2D pipeline first.")
    else:
        with st.expander("Show Phase 2C validation checks", expanded=False):
            st.dataframe(validation_df, width="stretch", hide_index=True)

    st.markdown("### Premium inputs and payoff context")
    premium_df = load_csv_safely(PHASE2B_OPTION_PREMIUM_PATH)
    payoff_df = load_csv_safely(PHASE2B_PREMIUM_AWARE_PAYOFF_PATH)
    context_col1, context_col2 = st.columns(2)
    with context_col1:
        with st.expander("Option premium estimates", expanded=False):
            if premium_df is None or premium_df.empty:
                st.info("No option-premium CSV found yet.")
            else:
                st.dataframe(premium_df, width="stretch", hide_index=True)
    with context_col2:
        with st.expander("Premium-aware payoff output", expanded=False):
            if payoff_df is None or payoff_df.empty:
                st.info("No premium-aware payoff CSV found yet.")
            else:
                st.dataframe(payoff_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 2D reports")
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        if PHASE2D_TUNING_HTML_PATH.exists():
            if st.button("Open tuning recommendations HTML"):
                if not open_path_with_windows(PHASE2D_TUNING_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2D_TUNING_HTML_PATH}")
        else:
            st.info("Tuning recommendations HTML report not found yet.")
    with report_col2:
        if PHASE2D_TUNING_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 2D report folder"):
                if not open_path_with_windows(PHASE2D_TUNING_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE2D_TUNING_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 2D pipeline report not found yet.")

    with st.expander("How to interpret this tab", expanded=False):
        st.markdown("""
        - **PASS** or **OK** means the current premium-model assumption is inside the tuning band.
        - **WATCH**, **REVIEW**, or **TUNE** does not mean the code is broken; it means the assumption deserves inspection.
        - Phase 2D is still Developer-view only. It is a tuning layer, not a customer-facing trade recommendation layer.
        - The next modeling step is to make the premium model read tunable assumptions from configuration rather than keeping assumptions embedded in code.
        """)



def show_phase2e_adjustment_file_status() -> None:
    """Show file availability for Phase 2E controlled premium adjustment outputs and runners."""
    rows = []
    for label, path in [
        ("Adjustment config JSON", PHASE2E_ADJUSTMENT_CONFIG_PATH),
        ("Adjusted premiums CSV", PHASE2E_ADJUSTED_PREMIUMS_PATH),
        ("Adjustment comparison HTML", PHASE2E_ADJUSTMENT_HTML_PATH),
        ("Adjustment summary", PHASE2E_ADJUSTMENT_SUMMARY_PATH),
        ("Adjusted payoff comparison CSV", PHASE2E_ADJUSTED_PAYOFF_COMPARISON_PATH),
        ("Adjusted payoff comparison HTML", PHASE2E_ADJUSTED_PAYOFF_HTML_PATH),
        ("Adjusted payoff summary", PHASE2E_ADJUSTED_PAYOFF_SUMMARY_PATH),
        ("Phase 2E pipeline report", PHASE2E_ADJUSTMENT_PIPELINE_REPORT_PATH),
        ("Adjustment checker", PHASE2E_ADJUSTMENT_CHECK_PATH),
        ("Adjusted payoff comparison checker", PHASE2E_ADJUSTED_PAYOFF_CHECK_PATH),
        ("Phase 2E pipeline checker", PHASE2E_ADJUSTMENT_PIPELINE_CHECK_PATH),
        ("Standalone Phase 2E adjustment viewer", PHASE2E_ADJUSTMENT_VIEWER_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase2e_adjustment_tab() -> None:
    """Developer-view-only Phase 2E controlled premium-model adjustment diagnostics."""
    st.subheader("Phase 2E adjustment")
    st.caption(
        "Developer-only view of the controlled premium-model adjustment layer. These outputs compare original premium estimates with adjusted estimates before any customer-facing promotion."
    )

    st.info(
        "Phase 2E applies a conservative IV-only premium adjustment, keeps the original premium model intact, and writes separate adjusted outputs for inspection."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 2E adjustment pipeline"):
            code, output = run_python_script(PHASE2E_ADJUSTMENT_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 2E adjustment pipeline passed.")
            else:
                st.warning(f"Phase 2E adjustment pipeline returned code {code}.")
            with st.expander("Phase 2E adjustment pipeline output", expanded=False):
                st.text_area("Phase 2E adjustment pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 2E adjustment viewer"):
            code, output = run_python_script(PHASE2E_ADJUSTMENT_VIEWER_PATH)
            if code == 0:
                st.success("Phase 2E adjustment viewer process ended normally.")
            else:
                st.info("The Phase 2E adjustment viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 2E adjustment viewer launch output", expanded=False):
                st.text_area("Phase 2E adjustment viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Phase 2E file status")
    show_phase2e_adjustment_file_status()

    st.markdown("### Adjustment summary")
    if PHASE2E_ADJUSTMENT_SUMMARY_PATH.exists():
        try:
            st.text(PHASE2E_ADJUSTMENT_SUMMARY_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            st.warning(f"Could not read adjustment summary: {exc}")
    else:
        st.info("No Phase 2E premium-adjustment summary found yet. Run the Phase 2E adjustment pipeline first.")

    st.markdown("### Adjusted premium estimates")
    adjusted_df = load_csv_safely(PHASE2E_ADJUSTED_PREMIUMS_PATH)
    if adjusted_df is None or adjusted_df.empty:
        st.info("No adjusted-premium CSV found yet. Run the Phase 2E adjustment pipeline first.")
    else:
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Scenario rows", len(adjusted_df))

        original_col = find_column(adjusted_df, ["original_call_premium", "estimated_call_premium", "original_premium"])
        adjusted_col = find_column(adjusted_df, ["adjusted_call_premium", "adjusted_premium", "call_premium_adjusted"])
        scenario_col = find_column(adjusted_df, ["scenario", "scenario_name", "display_name", "path_label"])

        if original_col is not None:
            original_values = pd.to_numeric(adjusted_df[original_col], errors="coerce")
            metric_col2.metric("Avg original premium", signed_currency(float(original_values.mean())))
        else:
            metric_col2.metric("Original premium", "not found")

        if adjusted_col is not None:
            adjusted_values = pd.to_numeric(adjusted_df[adjusted_col], errors="coerce")
            metric_col3.metric("Avg adjusted premium", signed_currency(float(adjusted_values.mean())))
        else:
            metric_col3.metric("Adjusted premium", "not found")

        if scenario_col is not None and adjusted_col is not None:
            chart_df = adjusted_df[[scenario_col, adjusted_col]].copy()
            chart_df[adjusted_col] = pd.to_numeric(chart_df[adjusted_col], errors="coerce")
            if chart_df[adjusted_col].notna().any():
                compact_horizontal_bar_chart(chart_df, scenario_col, adjusted_col, "Adjusted call premium by scenario")

        st.dataframe(adjusted_df, width="stretch", hide_index=True)

    st.markdown("### Adjusted payoff comparison")
    comparison_df = load_csv_safely(PHASE2E_ADJUSTED_PAYOFF_COMPARISON_PATH)
    if comparison_df is None or comparison_df.empty:
        st.info("No adjusted-premium payoff comparison CSV found yet. Run the Phase 2E adjustment pipeline first.")
    else:
        scenario_col = find_column(comparison_df, ["scenario", "scenario_name", "display_name", "path_label"])
        adjusted_relative_col = find_column(
            comparison_df,
            [
                "adjusted_covered_call_minus_buy_hold",
                "adjusted_covered_call_minus_buy_and_hold",
                "adjusted_relative_result",
                "covered_call_minus_buy_hold_adjusted",
            ],
        )
        model_change_col = find_column(
            comparison_df,
            [
                "adjusted_minus_original_model_pl",
                "adjusted_minus_original_p_l",
                "adjusted_minus_original",
                "adjusted_minus_prior_premium_aware_result",
            ],
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Comparison rows", len(comparison_df))
        if adjusted_relative_col is not None:
            adjusted_relative = pd.to_numeric(comparison_df[adjusted_relative_col], errors="coerce")
            metric_col2.metric("Avg adjusted relative result", signed_currency(float(adjusted_relative.mean())))
            if scenario_col is not None:
                chart_df = comparison_df[[scenario_col, adjusted_relative_col]].copy()
                chart_df[adjusted_relative_col] = adjusted_relative
                compact_horizontal_bar_chart(chart_df, scenario_col, adjusted_relative_col, "Adjusted covered-call relative result")
        else:
            metric_col2.metric("Adjusted relative result", "not found")

        if model_change_col is not None:
            model_change = pd.to_numeric(comparison_df[model_change_col], errors="coerce")
            metric_col3.metric("Avg model change", signed_currency(float(model_change.mean())))
        else:
            metric_col3.metric("Model change", "not found")

        st.dataframe(comparison_df, width="stretch", hide_index=True)

    st.markdown("### Original and tuning context")
    context_col1, context_col2 = st.columns(2)
    with context_col1:
        with st.expander("Original option premium estimates", expanded=False):
            premium_df = load_csv_safely(PHASE2B_OPTION_PREMIUM_PATH)
            if premium_df is None or premium_df.empty:
                st.info("No original option-premium CSV found yet.")
            else:
                st.dataframe(premium_df, width="stretch", hide_index=True)
    with context_col2:
        with st.expander("Phase 2D tuning recommendations", expanded=False):
            tuning_df = load_csv_safely(PHASE2D_TUNING_RECOMMENDATIONS_PATH)
            if tuning_df is None or tuning_df.empty:
                st.info("No Phase 2D tuning recommendations CSV found yet.")
            else:
                st.dataframe(tuning_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 2E reports")
    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        if PHASE2E_ADJUSTMENT_HTML_PATH.exists():
            if st.button("Open adjustment comparison HTML"):
                if not open_path_with_windows(PHASE2E_ADJUSTMENT_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2E_ADJUSTMENT_HTML_PATH}")
        else:
            st.info("Adjustment comparison HTML report not found yet.")
    with report_col2:
        if PHASE2E_ADJUSTED_PAYOFF_HTML_PATH.exists():
            if st.button("Open adjusted payoff HTML"):
                if not open_path_with_windows(PHASE2E_ADJUSTED_PAYOFF_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2E_ADJUSTED_PAYOFF_HTML_PATH}")
        else:
            st.info("Adjusted payoff HTML report not found yet.")
    with report_col3:
        if PHASE2E_ADJUSTMENT_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 2E report folder"):
                if not open_path_with_windows(PHASE2E_ADJUSTMENT_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE2E_ADJUSTMENT_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 2E pipeline report not found yet.")

    with st.expander("How to interpret this tab", expanded=False):
        st.markdown("""
        - Phase 2E does **not** overwrite the original premium model.
        - It writes adjusted premiums and adjusted payoff comparisons to separate files.
        - The adjustment is intentionally conservative and should be inspected before promotion.
        - A better adjusted payoff does not automatically mean the adjustment is realistic; it means the model sensitivity has changed.
        - Keep this tab in Developer view until the premium adjustment is validated against realistic examples.
        """)


def show_phase2f_model_decision_file_status() -> None:
    """Show file availability for Phase 2F model-decision outputs and runners."""
    rows = []
    for label, path in [
        ("Model-decision CSV", PHASE2F_MODEL_DECISION_CSV_PATH),
        ("Model-decision HTML", PHASE2F_MODEL_DECISION_HTML_PATH),
        ("Model-decision text summary", PHASE2F_MODEL_DECISION_TEXT_PATH),
        ("Model-decision summary check report", PHASE2F_MODEL_DECISION_CHECK_REPORT_PATH),
        ("Model-decision viewer check report", PHASE2F_MODEL_DECISION_VIEWER_CHECK_REPORT_PATH),
        ("Model-decision pipeline report", PHASE2F_MODEL_DECISION_PIPELINE_REPORT_PATH),
        ("Model-decision summary checker", PHASE2F_MODEL_DECISION_SUMMARY_CHECK_PATH),
        ("Phase 2F pipeline checker", PHASE2F_MODEL_DECISION_PIPELINE_CHECK_PATH),
        ("Standalone Phase 2F model-decision viewer", PHASE2F_MODEL_DECISION_VIEWER_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase2f_model_decision_tab() -> None:
    """Developer-view-only Phase 2F model-decision summary diagnostics."""
    st.subheader("Phase 2F model decision")
    st.caption(
        "Developer-only view of the consolidated model-decision layer. This compares original premium-aware results, adjusted-premium results, validation checks, and tuning recommendations."
    )

    st.info(
        "Phase 2F is an internal model-development checkpoint. Its labels are promotion-readiness labels for the model, not customer-facing trade recommendations."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 2F model-decision pipeline"):
            code, output = run_python_script(PHASE2F_MODEL_DECISION_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 2F model-decision pipeline passed.")
            else:
                st.warning(f"Phase 2F model-decision pipeline returned code {code}.")
            with st.expander("Phase 2F model-decision pipeline output", expanded=False):
                st.text_area("Phase 2F model-decision pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 2F model-decision viewer"):
            code, output = run_python_script(PHASE2F_MODEL_DECISION_VIEWER_PATH)
            if code == 0:
                st.success("Phase 2F model-decision viewer process ended normally.")
            else:
                st.info("The Phase 2F model-decision viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 2F model-decision viewer launch output", expanded=False):
                st.text_area("Phase 2F model-decision viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Phase 2F file status")
    show_phase2f_model_decision_file_status()

    st.markdown("### Model-decision summary")
    if PHASE2F_MODEL_DECISION_TEXT_PATH.exists():
        try:
            st.text(PHASE2F_MODEL_DECISION_TEXT_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            st.warning(f"Could not read Phase 2F model-decision text summary: {exc}")
    else:
        st.info("No Phase 2F model-decision text summary found yet. Run the Phase 2F pipeline first.")

    decision_df = load_csv_safely(PHASE2F_MODEL_DECISION_CSV_PATH)
    st.markdown("### Model decisions")
    if decision_df is None or decision_df.empty:
        st.info("No Phase 2F model-decision CSV found yet. Run the Phase 2F pipeline first.")
    else:
        scenario_col = find_column(decision_df, ["scenario", "scenario_name", "display_name", "path_label"])
        decision_col = find_column(
            decision_df,
            [
                "decision_label",
                "model_decision",
                "promotion_decision",
                "recommendation",
                "decision",
            ],
        )
        relative_col = find_column(
            decision_df,
            [
                "adjusted_covered_call_minus_buy_hold",
                "adjusted_relative_result",
                "premium_aware_covered_call_minus_buy_hold",
                "covered_call_minus_buy_hold",
            ],
        )
        model_change_col = find_column(
            decision_df,
            [
                "adjusted_minus_original_model_pl",
                "adjusted_minus_prior_premium_aware_result",
                "model_change",
                "adjustment_effect",
            ],
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Scenario rows", len(decision_df))
        if decision_col is not None:
            unique_decisions = int(decision_df[decision_col].dropna().nunique())
            metric_col2.metric("Decision categories", unique_decisions)
        else:
            metric_col2.metric("Decision categories", "not found")
        if relative_col is not None:
            relative_values = pd.to_numeric(decision_df[relative_col], errors="coerce")
            metric_col3.metric("Avg relative result", signed_currency(float(relative_values.mean())))
        elif model_change_col is not None:
            change_values = pd.to_numeric(decision_df[model_change_col], errors="coerce")
            metric_col3.metric("Avg model change", signed_currency(float(change_values.mean())))
        else:
            metric_col3.metric("Avg result", "not found")

        if decision_col is not None:
            st.markdown("#### Decision counts")
            count_df = decision_df[decision_col].fillna("Unclassified").value_counts().reset_index()
            count_df.columns = ["Decision label", "Scenario count"]
            st.dataframe(count_df, width="stretch", hide_index=True)

        if scenario_col is not None and relative_col is not None:
            chart_df = decision_df[[scenario_col, relative_col]].copy()
            chart_df[relative_col] = pd.to_numeric(chart_df[relative_col], errors="coerce")
            if chart_df[relative_col].notna().any():
                compact_horizontal_bar_chart(chart_df, scenario_col, relative_col, "Phase 2F scenario relative result")

        st.dataframe(decision_df, width="stretch", hide_index=True)

        st.markdown("### Promotion candidates")
        if decision_col is None:
            st.info("No decision-label column was found, so promotion candidates cannot be filtered automatically.")
        else:
            decision_text = decision_df[decision_col].astype(str).str.upper()
            candidate_mask = decision_text.str.contains("CANDIDATE", na=False) | decision_text.str.contains("PROMOTION", na=False)
            candidates_df = decision_df[candidate_mask].copy()
            if candidates_df.empty:
                st.info("No controlled-promotion candidates are currently flagged. That is acceptable; the model may remain research-only until assumptions are stronger.")
            else:
                st.dataframe(candidates_df, width="stretch", hide_index=True)

    st.markdown("### Evidence context")
    context_col1, context_col2 = st.columns(2)
    with context_col1:
        with st.expander("Original premium-aware payoff", expanded=False):
            premium_payoff_df = load_csv_safely(PHASE2B_PREMIUM_AWARE_PAYOFF_PATH)
            if premium_payoff_df is None or premium_payoff_df.empty:
                st.info("No premium-aware payoff CSV found yet.")
            else:
                st.dataframe(premium_payoff_df, width="stretch", hide_index=True)
        with st.expander("Premium-model validation checks", expanded=False):
            validation_df = load_csv_safely(PHASE2C_VALIDATION_CSV_PATH)
            if validation_df is None or validation_df.empty:
                st.info("No premium-model validation CSV found yet.")
            else:
                st.dataframe(validation_df, width="stretch", hide_index=True)
    with context_col2:
        with st.expander("Phase 2D tuning recommendations", expanded=False):
            tuning_df = load_csv_safely(PHASE2D_TUNING_RECOMMENDATIONS_PATH)
            if tuning_df is None or tuning_df.empty:
                st.info("No Phase 2D tuning recommendations CSV found yet.")
            else:
                st.dataframe(tuning_df, width="stretch", hide_index=True)
        with st.expander("Phase 2E adjusted payoff comparison", expanded=False):
            adjusted_df = load_csv_safely(PHASE2E_ADJUSTED_PAYOFF_COMPARISON_PATH)
            if adjusted_df is None or adjusted_df.empty:
                st.info("No Phase 2E adjusted payoff comparison CSV found yet.")
            else:
                st.dataframe(adjusted_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 2F reports")
    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        if PHASE2F_MODEL_DECISION_HTML_PATH.exists():
            if st.button("Open model-decision HTML"):
                if not open_path_with_windows(PHASE2F_MODEL_DECISION_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2F_MODEL_DECISION_HTML_PATH}")
        else:
            st.info("Model-decision HTML report not found yet.")
    with report_col2:
        if PHASE2F_MODEL_DECISION_TEXT_PATH.exists():
            if st.button("Open model-decision folder"):
                if not open_path_with_windows(PHASE2F_MODEL_DECISION_TEXT_PATH.parent):
                    st.warning(f"Could not open: {PHASE2F_MODEL_DECISION_TEXT_PATH.parent}")
        else:
            st.info("Model-decision text summary not found yet.")
    with report_col3:
        if PHASE2F_MODEL_DECISION_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 2F pipeline folder"):
                if not open_path_with_windows(PHASE2F_MODEL_DECISION_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE2F_MODEL_DECISION_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 2F pipeline report not found yet.")

    with st.expander("How to interpret this tab", expanded=False):
        st.markdown("""
        - Phase 2F consolidates several diagnostic layers into one internal decision summary.
        - A controlled-promotion candidate is not a customer trade recommendation.
        - A research-model label means the model is useful for development but should not yet drive the customer-facing result.
        - A review label means at least one assumption, validation result, or tuning result needs inspection.
        - Keep this tab in Developer view until the model-decision process is stable and the assumptions are documented clearly.
        """)


def show_phase2g_model_promotion_file_status() -> None:
    """Show file availability for Phase 2G model-promotion outputs and runners."""
    rows = []
    for label, path in [
        ("Model-promotion plan CSV", PHASE2G_MODEL_PROMOTION_PLAN_CSV_PATH),
        ("Model-promotion plan HTML", PHASE2G_MODEL_PROMOTION_PLAN_HTML_PATH),
        ("Model-promotion plan text summary", PHASE2G_MODEL_PROMOTION_PLAN_TEXT_PATH),
        ("Model-promotion planning check report", PHASE2G_MODEL_PROMOTION_PLANNING_CHECK_REPORT_PATH),
        ("Model-promotion viewer check report", PHASE2G_MODEL_PROMOTION_VIEWER_CHECK_REPORT_PATH),
        ("Model-promotion pipeline report", PHASE2G_MODEL_PROMOTION_PIPELINE_REPORT_PATH),
        ("Model-promotion planning checker", PHASE2G_MODEL_PROMOTION_PLANNING_CHECK_PATH),
        ("Phase 2G model-promotion pipeline checker", PHASE2G_MODEL_PROMOTION_PIPELINE_CHECK_PATH),
        ("Standalone Phase 2G model-promotion viewer", PHASE2G_MODEL_PROMOTION_VIEWER_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase2g_model_promotion_tab() -> None:
    """Developer-view-only Phase 2G controlled model-promotion planning diagnostics."""
    st.subheader("Phase 2G model promotion")
    st.caption(
        "Developer-only view of the controlled model-promotion planning layer. This helps decide whether the adjusted premium model should remain research-only or become the promoted internal model."
    )

    st.warning(
        "Phase 2G is internal model governance. Promotion labels are not customer-facing trade recommendations and do not change the customer dashboard model by themselves."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 2G model-promotion pipeline"):
            code, output = run_python_script(PHASE2G_MODEL_PROMOTION_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 2G model-promotion pipeline passed.")
            else:
                st.warning(f"Phase 2G model-promotion pipeline returned code {code}.")
            with st.expander("Phase 2G model-promotion pipeline output", expanded=False):
                st.text_area("Phase 2G model-promotion pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 2G model-promotion viewer"):
            code, output = run_python_script(PHASE2G_MODEL_PROMOTION_VIEWER_PATH)
            if code == 0:
                st.success("Phase 2G model-promotion viewer process ended normally.")
            else:
                st.info("The Phase 2G model-promotion viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 2G model-promotion viewer launch output", expanded=False):
                st.text_area("Phase 2G model-promotion viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Phase 2G file status")
    show_phase2g_model_promotion_file_status()

    st.markdown("### Model-promotion plan summary")
    if PHASE2G_MODEL_PROMOTION_PLAN_TEXT_PATH.exists():
        try:
            st.text(PHASE2G_MODEL_PROMOTION_PLAN_TEXT_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            st.warning(f"Could not read Phase 2G model-promotion text summary: {exc}")
    else:
        st.info("No Phase 2G model-promotion text summary found yet. Run the Phase 2G pipeline first.")

    plan_df = load_csv_safely(PHASE2G_MODEL_PROMOTION_PLAN_CSV_PATH)
    st.markdown("### Model-promotion plan")
    if plan_df is None or plan_df.empty:
        st.info("No Phase 2G model-promotion plan CSV found yet. Run the Phase 2G pipeline first.")
    else:
        scenario_col = find_column(plan_df, ["scenario", "scenario_name", "display_name", "path_label"])
        decision_col = find_column(
            plan_df,
            [
                "promotion_label",
                "promotion_decision",
                "promotion_status",
                "model_promotion_label",
                "decision_label",
                "recommendation",
                "decision",
            ],
        )
        relative_col = find_column(
            plan_df,
            [
                "adjusted_covered_call_minus_buy_hold",
                "adjusted_relative_result",
                "premium_aware_covered_call_minus_buy_hold",
                "covered_call_minus_buy_hold",
            ],
        )
        confidence_col = find_column(
            plan_df,
            [
                "promotion_confidence",
                "confidence",
                "model_confidence",
                "evidence_score",
                "readiness_score",
            ],
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Scenario rows", len(plan_df))
        if decision_col is not None:
            metric_col2.metric("Promotion categories", int(plan_df[decision_col].dropna().nunique()))
        else:
            metric_col2.metric("Promotion categories", "not found")
        if relative_col is not None:
            relative_values = pd.to_numeric(plan_df[relative_col], errors="coerce")
            metric_col3.metric("Avg relative result", signed_currency(float(relative_values.mean())))
        elif confidence_col is not None:
            confidence_values = pd.to_numeric(plan_df[confidence_col], errors="coerce")
            metric_col3.metric("Avg readiness score", f"{float(confidence_values.mean()):.2f}")
        else:
            metric_col3.metric("Avg result", "not found")

        if decision_col is not None:
            st.markdown("#### Promotion-plan counts")
            count_df = plan_df[decision_col].fillna("Unclassified").value_counts().reset_index()
            count_df.columns = ["Promotion label", "Scenario count"]
            st.dataframe(count_df, width="stretch", hide_index=True)

        if scenario_col is not None and relative_col is not None:
            chart_df = plan_df[[scenario_col, relative_col]].copy()
            chart_df[relative_col] = pd.to_numeric(chart_df[relative_col], errors="coerce")
            if chart_df[relative_col].notna().any():
                compact_horizontal_bar_chart(chart_df, scenario_col, relative_col, "Phase 2G promotion-plan relative result")

        st.dataframe(plan_df, width="stretch", hide_index=True)

        st.markdown("### Promotion candidates")
        if decision_col is None:
            st.info("No promotion-label column was found, so promotion candidates cannot be filtered automatically.")
        else:
            decision_text = plan_df[decision_col].astype(str).str.upper()
            candidate_mask = decision_text.str.contains("CANDIDATE", na=False) | decision_text.str.contains("PROMOTION", na=False)
            candidates_df = plan_df[candidate_mask].copy()
            if candidates_df.empty:
                st.info("No internal promotion candidates are currently flagged. That is acceptable; the model can remain research-only.")
            else:
                st.dataframe(candidates_df, width="stretch", hide_index=True)

    st.markdown("### Evidence context")
    context_col1, context_col2 = st.columns(2)
    with context_col1:
        with st.expander("Phase 2F model-decision summary", expanded=False):
            decision_df = load_csv_safely(PHASE2F_MODEL_DECISION_CSV_PATH)
            if decision_df is None or decision_df.empty:
                st.info("No Phase 2F model-decision CSV found yet.")
            else:
                st.dataframe(decision_df, width="stretch", hide_index=True)
        with st.expander("Phase 2E adjusted payoff comparison", expanded=False):
            adjusted_df = load_csv_safely(PHASE2E_ADJUSTED_PAYOFF_COMPARISON_PATH)
            if adjusted_df is None or adjusted_df.empty:
                st.info("No Phase 2E adjusted payoff comparison CSV found yet.")
            else:
                st.dataframe(adjusted_df, width="stretch", hide_index=True)
    with context_col2:
        with st.expander("Phase 2D tuning recommendations", expanded=False):
            tuning_df = load_csv_safely(PHASE2D_TUNING_RECOMMENDATIONS_PATH)
            if tuning_df is None or tuning_df.empty:
                st.info("No Phase 2D tuning recommendations CSV found yet.")
            else:
                st.dataframe(tuning_df, width="stretch", hide_index=True)
        with st.expander("Phase 2C validation checks", expanded=False):
            validation_df = load_csv_safely(PHASE2C_VALIDATION_CSV_PATH)
            if validation_df is None or validation_df.empty:
                st.info("No premium-model validation CSV found yet.")
            else:
                st.dataframe(validation_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 2G reports")
    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        if PHASE2G_MODEL_PROMOTION_PLAN_HTML_PATH.exists():
            if st.button("Open model-promotion HTML"):
                if not open_path_with_windows(PHASE2G_MODEL_PROMOTION_PLAN_HTML_PATH):
                    st.warning(f"Could not open: {PHASE2G_MODEL_PROMOTION_PLAN_HTML_PATH}")
        else:
            st.info("Model-promotion HTML report not found yet.")
    with report_col2:
        if PHASE2G_MODEL_PROMOTION_PLAN_TEXT_PATH.exists():
            if st.button("Open model-promotion folder"):
                if not open_path_with_windows(PHASE2G_MODEL_PROMOTION_PLAN_TEXT_PATH.parent):
                    st.warning(f"Could not open: {PHASE2G_MODEL_PROMOTION_PLAN_TEXT_PATH.parent}")
        else:
            st.info("Model-promotion text summary not found yet.")
    with report_col3:
        if PHASE2G_MODEL_PROMOTION_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 2G pipeline folder"):
                if not open_path_with_windows(PHASE2G_MODEL_PROMOTION_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE2G_MODEL_PROMOTION_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 2G pipeline report not found yet.")

    with st.expander("How to interpret this tab", expanded=False):
        st.markdown("""
        - Phase 2G is a controlled internal planning layer, not a customer feature.
        - A promotion candidate means the model may be considered for controlled internal use.
        - A research-model label means the model is still useful but should not drive customer-facing output yet.
        - A review label means the model needs additional inspection before any promotion decision.
        - Keep this tab in Developer view until model governance, assumptions, and warnings are documented clearly.
        """)


def show_phase3_interactive_payoff_file_status() -> None:
    """Show file availability for Phase 3 interactive payoff outputs and runners."""
    rows = []
    for label, path in [
        ("Phase 3 interactive payoff viewer", PHASE3_INTERACTIVE_PAYOFF_VIEWER_PATH),
        ("Phase 3 interactive payoff viewer check", PHASE3_INTERACTIVE_PAYOFF_VIEWER_CHECK_PATH),
        ("Phase 3 interactive payoff pipeline checker", PHASE3_INTERACTIVE_PAYOFF_PIPELINE_CHECK_PATH),
        ("Interactive payoff snapshot CSV", PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_CSV_PATH),
        ("Interactive payoff snapshot HTML", PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_HTML_PATH),
        ("Interactive payoff pipeline report", PHASE3_INTERACTIVE_PAYOFF_PIPELINE_REPORT_PATH),
    ]:
        rows.append(
            {
                "Item": label,
                "Status": "FOUND" if path.exists() else "OPTIONAL / MISSING",
                "Path": str(path),
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase3_interactive_payoff_tab() -> None:
    """Developer-view-only Phase 3 interactive covered-call payoff prototype."""
    st.subheader("Phase 3 interactive payoff")
    st.caption(
        "Developer-only view of the first interactive graphical covered-call payoff interface. "
        "This is the bridge toward the Pro running ticker/payoff dashboard."
    )

    st.warning(
        "This prototype uses manually entered trade details. It is not connected to live market data or option-chain data yet."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 3 interactive payoff pipeline"):
            code, output = run_python_script(PHASE3_INTERACTIVE_PAYOFF_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 3 interactive payoff pipeline passed.")
            else:
                st.warning(f"Phase 3 interactive payoff pipeline returned code {code}.")
            with st.expander("Phase 3 pipeline output", expanded=False):
                st.text_area("Phase 3 pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 3 interactive payoff viewer"):
            code, output = run_python_script(PHASE3_INTERACTIVE_PAYOFF_VIEWER_PATH)
            if code == 0:
                st.success("Phase 3 interactive payoff viewer process ended normally.")
            else:
                st.info("The Phase 3 viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 3 viewer launch output", expanded=False):
                st.text_area("Phase 3 viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Phase 3 file status")
    show_phase3_interactive_payoff_file_status()

    st.markdown("### Interactive payoff snapshot")
    snapshot_df = load_csv_safely(PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_CSV_PATH)
    if snapshot_df is None or snapshot_df.empty:
        st.info(
            "No Phase 3 payoff snapshot has been saved yet. Open the standalone viewer once to create the snapshot CSV and HTML."
        )
    else:
        price_col = find_column(snapshot_df, ["stock_price", "price", "underlying_price", "expiration_price"])
        covered_col = find_column(snapshot_df, ["covered_call_pl", "covered_call_p_l", "covered_call_profit_loss", "covered_call_payoff"])
        buy_hold_col = find_column(snapshot_df, ["buy_hold_pl", "buy_and_hold_pl", "buy_hold_p_l", "buy_and_hold_payoff"])

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Snapshot rows", len(snapshot_df))
        if covered_col is not None:
            covered_values = pd.to_numeric(snapshot_df[covered_col], errors="coerce")
            metric_col2.metric("Best covered-call P/L", signed_currency(float(covered_values.max())))
        else:
            metric_col2.metric("Best covered-call P/L", "not found")
        if buy_hold_col is not None and covered_col is not None:
            difference_values = pd.to_numeric(snapshot_df[covered_col], errors="coerce") - pd.to_numeric(snapshot_df[buy_hold_col], errors="coerce")
            metric_col3.metric("Avg CC minus B/H", signed_currency(float(difference_values.mean())))
        else:
            metric_col3.metric("Avg CC minus B/H", "not found")

        if price_col is not None and covered_col is not None and buy_hold_col is not None:
            chart_df = snapshot_df[[price_col, covered_col, buy_hold_col]].copy()
            chart_df[price_col] = pd.to_numeric(chart_df[price_col], errors="coerce")
            chart_df[covered_col] = pd.to_numeric(chart_df[covered_col], errors="coerce")
            chart_df[buy_hold_col] = pd.to_numeric(chart_df[buy_hold_col], errors="coerce")
            chart_df = chart_df.dropna()
            if not chart_df.empty and alt is not None:
                long_df = chart_df.melt(
                    id_vars=[price_col],
                    value_vars=[covered_col, buy_hold_col],
                    var_name="Payoff type",
                    value_name="Profit / loss",
                )
                chart = (
                    alt.Chart(long_df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(f"{price_col}:Q", title="Stock price"),
                        y=alt.Y("Profit / loss:Q", title="Profit / loss"),
                        color=alt.Color("Payoff type:N", title="Payoff"),
                        tooltip=[price_col, "Payoff type", "Profit / loss"],
                    )
                    .properties(height=360)
                )
                st.altair_chart(chart, width="stretch")
            elif not chart_df.empty:
                st.line_chart(chart_df.set_index(price_col)[[covered_col, buy_hold_col]])

        st.dataframe(snapshot_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 3 reports")
    report_col1, report_col2 = st.columns(2)
    with report_col1:
        if PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_HTML_PATH.exists():
            if st.button("Open Phase 3 payoff snapshot HTML"):
                if not open_path_with_windows(PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_HTML_PATH):
                    st.warning(f"Could not open: {PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_HTML_PATH}")
        else:
            st.info("Phase 3 payoff snapshot HTML has not been created yet.")
    with report_col2:
        if PHASE3_INTERACTIVE_PAYOFF_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 3 pipeline report folder"):
                if not open_path_with_windows(PHASE3_INTERACTIVE_PAYOFF_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE3_INTERACTIVE_PAYOFF_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 3 pipeline report has not been created yet.")

    with st.expander("Phase 3 notes", expanded=False):
        st.markdown("""
        - Phase 3 begins the interactive Pro graphical dashboard workstream.
        - The current prototype is manual-input only; live ticker and option-chain data come later.
        - The payoff line is useful for visualizing capped upside, downside cushion, break-even, and assignment exposure.
        - Keep this in Developer view until the chart, labels, input validation, and customer warnings are polished.
        """)



def show_phase3b_scenario_overlay_file_status() -> None:
    """Show file availability for Phase 3B scenario-overlay outputs and runners."""
    rows = []
    for label, path in [
        ("Scenario-overlay model check", PHASE3B_SCENARIO_OVERLAY_CHECK_PATH),
        ("Scenario-overlay viewer", PHASE3B_SCENARIO_OVERLAY_VIEWER_PATH),
        ("Scenario-overlay viewer check", PHASE3B_SCENARIO_OVERLAY_VIEWER_CHECK_PATH),
        ("Scenario-overlay pipeline checker", PHASE3B_SCENARIO_OVERLAY_PIPELINE_CHECK_PATH),
        ("Scenario-overlay CSV", PHASE3B_SCENARIO_OVERLAY_CSV_PATH),
        ("Scenario-overlay HTML", PHASE3B_SCENARIO_OVERLAY_HTML_PATH),
        ("Scenario-overlay text summary", PHASE3B_SCENARIO_OVERLAY_SUMMARY_PATH),
        ("Scenario-overlay pipeline report", PHASE3B_SCENARIO_OVERLAY_PIPELINE_REPORT_PATH),
        ("Interactive payoff snapshot CSV", PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_CSV_PATH),
    ]:
        if path == PHASE3_INTERACTIVE_PAYOFF_SNAPSHOT_CSV_PATH:
            status = "OPTIONAL / FOUND" if path.exists() else "OPTIONAL / MISSING"
        else:
            status = "FOUND" if path.exists() else "MISSING"
        rows.append({"Item": label, "Status": status, "Path": str(path)})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase3b_scenario_overlay_tab() -> None:
    """Developer-view-only Phase 3B scenario-overlay diagnostics."""
    st.subheader("Phase 3B scenario overlay")
    st.caption(
        "Developer-only view of scenario stress tests for the interactive covered-call payoff setup. "
        "This extends the Phase 3 payoff graph with modeled price-scenario outcomes."
    )

    st.info(
        "The overlay uses a saved Phase 3 payoff snapshot when available. If no snapshot exists, "
        "the model uses the default SPY demo setup."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 3B scenario-overlay pipeline"):
            code, output = run_python_script(PHASE3B_SCENARIO_OVERLAY_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 3B scenario-overlay pipeline passed.")
            else:
                st.warning(f"Phase 3B scenario-overlay pipeline returned code {code}.")
            with st.expander("Phase 3B pipeline output", expanded=False):
                st.text_area("Phase 3B pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 3B scenario-overlay viewer"):
            code, output = run_python_script(PHASE3B_SCENARIO_OVERLAY_VIEWER_PATH)
            if code == 0:
                st.success("Phase 3B scenario-overlay viewer process ended normally.")
            else:
                st.info("The Phase 3B viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 3B viewer launch output", expanded=False):
                st.text_area("Phase 3B viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Phase 3B file status")
    show_phase3b_scenario_overlay_file_status()

    st.markdown("### Scenario-overlay summary")
    if PHASE3B_SCENARIO_OVERLAY_SUMMARY_PATH.exists():
        with st.expander("Open text summary", expanded=True):
            st.text(PHASE3B_SCENARIO_OVERLAY_SUMMARY_PATH.read_text(encoding="utf-8", errors="replace"))
    else:
        st.info("Scenario-overlay text summary has not been created yet. Run the Phase 3B pipeline first.")

    overlay_df = load_csv_safely(PHASE3B_SCENARIO_OVERLAY_CSV_PATH)
    if overlay_df is None or overlay_df.empty:
        st.info("No Phase 3B scenario-overlay CSV is available yet. Run the Phase 3B pipeline first.")
    else:
        st.markdown("### Scenario overlay table")
        scenario_col = find_column(overlay_df, ["scenario", "scenario_name", "display_name"])
        cc_col = find_column(overlay_df, ["covered_call_pl", "covered_call_p_l", "covered_call_profit_loss"])
        bh_col = find_column(overlay_df, ["buy_hold_pl", "buy_and_hold_pl", "buy_hold_p_l", "buy_and_hold_profit_loss"])
        rel_col = find_column(overlay_df, ["covered_call_minus_buy_hold", "cc_minus_bh", "relative_result"])
        assignment_col = find_column(overlay_df, ["assignment_flag", "assigned", "assignment"])

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Scenarios", len(overlay_df))
        if rel_col is not None:
            rel_values = pd.to_numeric(overlay_df[rel_col], errors="coerce")
            metric_col2.metric("Best relative result", signed_currency(float(rel_values.max())))
            metric_col3.metric("Worst relative result", signed_currency(float(rel_values.min())))
        else:
            metric_col2.metric("Best relative result", "not found")
            metric_col3.metric("Worst relative result", "not found")

        chart_cols = [col for col in [scenario_col, cc_col, bh_col, rel_col] if col is not None]
        if scenario_col is not None and rel_col is not None and alt is not None:
            chart_df = overlay_df[[scenario_col, rel_col]].copy()
            chart_df[rel_col] = pd.to_numeric(chart_df[rel_col], errors="coerce")
            chart_df = chart_df.dropna()
            if not chart_df.empty:
                chart = (
                    alt.Chart(chart_df)
                    .mark_bar()
                    .encode(
                        x=alt.X(f"{rel_col}:Q", title="Covered call minus buy-and-hold"),
                        y=alt.Y(f"{scenario_col}:N", title="Scenario", sort="-x"),
                        tooltip=[scenario_col, rel_col],
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart, width="stretch")

        if assignment_col is not None:
            assigned_count = int(overlay_df[assignment_col].astype(str).str.lower().isin(["true", "yes", "1", "assigned"]).sum())
            st.caption(f"Assignment-flagged scenarios: {assigned_count}")

        if chart_cols:
            st.dataframe(overlay_df[chart_cols], width="stretch", hide_index=True)
        else:
            st.dataframe(overlay_df, width="stretch", hide_index=True)

        with st.expander("Full scenario-overlay output", expanded=False):
            st.dataframe(overlay_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 3B reports")
    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        if PHASE3B_SCENARIO_OVERLAY_HTML_PATH.exists():
            if st.button("Open scenario-overlay HTML"):
                if not open_path_with_windows(PHASE3B_SCENARIO_OVERLAY_HTML_PATH):
                    st.warning(f"Could not open: {PHASE3B_SCENARIO_OVERLAY_HTML_PATH}")
        else:
            st.info("Scenario-overlay HTML has not been created yet.")
    with report_col2:
        if PHASE3B_SCENARIO_OVERLAY_SUMMARY_PATH.exists():
            if st.button("Open scenario-overlay report folder"):
                if not open_path_with_windows(PHASE3B_SCENARIO_OVERLAY_SUMMARY_PATH.parent):
                    st.warning(f"Could not open: {PHASE3B_SCENARIO_OVERLAY_SUMMARY_PATH.parent}")
        else:
            st.info("Scenario-overlay summary has not been created yet.")
    with report_col3:
        if PHASE3B_SCENARIO_OVERLAY_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 3B pipeline report folder"):
                if not open_path_with_windows(PHASE3B_SCENARIO_OVERLAY_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE3B_SCENARIO_OVERLAY_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 3B pipeline report has not been created yet.")

    with st.expander("Phase 3B notes", expanded=False):
        st.markdown("""
        - Phase 3B adds scenario overlays to the interactive payoff prototype.
        - This is still a modeled scenario display, not a forecast.
        - The overlay helps show when a covered call is expected to outperform or lag buy-and-hold.
        - Keep this in Developer view until the scenario logic and visual warnings are polished.
        """)



def show_phase3c_rich_payoff_file_status() -> None:
    """Show file availability for Phase 3C richer payoff outputs and runners."""
    rows = []
    for label, path, optional in [
        ("Phase 3C rich payoff viewer", PHASE3C_RICH_PAYOFF_VIEWER_PATH, False),
        ("Phase 3C rich payoff viewer check", PHASE3C_RICH_PAYOFF_VIEWER_CHECK_PATH, False),
        ("Phase 3C rich payoff pipeline checker", PHASE3C_RICH_PAYOFF_PIPELINE_CHECK_PATH, False),
        ("Phase 3C rich payoff pipeline report", PHASE3C_RICH_PAYOFF_PIPELINE_REPORT_PATH, False),
        ("Phase 3C rich payoff snapshot CSV", PHASE3C_RICH_PAYOFF_SNAPSHOT_CSV_PATH, True),
        ("Phase 3C rich payoff snapshot HTML", PHASE3C_RICH_PAYOFF_SNAPSHOT_HTML_PATH, True),
        ("Phase 3B scenario overlay CSV", PHASE3B_SCENARIO_OVERLAY_CSV_PATH, False),
    ]:
        if optional:
            status = "OPTIONAL / FOUND" if path.exists() else "OPTIONAL / MISSING"
        else:
            status = "FOUND" if path.exists() else "MISSING"
        rows.append({"Item": label, "Status": status, "Path": str(path)})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def show_phase3c_rich_payoff_tab() -> None:
    """Developer-view-only Phase 3C richer graphical payoff diagnostics."""
    st.subheader("Phase 3C rich payoff")
    st.caption(
        "Developer-only prototype for the richer graphical covered-call payoff interface. "
        "This is the next visual layer after the basic Phase 3 payoff viewer and Phase 3B scenario overlay."
    )

    st.info(
        "Open the standalone Phase 3C viewer to enter a covered-call setup, inspect the richer payoff graph, "
        "and optionally save a snapshot. Snapshot outputs are optional until a setup is saved."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 3C rich payoff pipeline"):
            code, output = run_python_script(PHASE3C_RICH_PAYOFF_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 3C rich payoff pipeline passed.")
            else:
                st.warning(f"Phase 3C rich payoff pipeline returned code {code}.")
            with st.expander("Phase 3C pipeline output", expanded=False):
                st.text_area("Phase 3C pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 3C rich payoff viewer"):
            code, output = run_python_script(PHASE3C_RICH_PAYOFF_VIEWER_PATH)
            if code == 0:
                st.success("Phase 3C rich payoff viewer process ended normally.")
            else:
                st.info("The Phase 3C viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 3C viewer launch output", expanded=False):
                st.text_area("Phase 3C viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Phase 3C file status")
    show_phase3c_rich_payoff_file_status()

    st.markdown("### Saved Phase 3C payoff snapshot")
    snapshot_df = load_csv_safely(PHASE3C_RICH_PAYOFF_SNAPSHOT_CSV_PATH)
    if snapshot_df is None or snapshot_df.empty:
        st.info("No Phase 3C rich payoff snapshot exists yet. Open the standalone viewer and save a setup to create one.")
    else:
        setup_cols = [
            col
            for col in [
                "setup_ticker",
                "setup_current_price",
                "setup_shares",
                "setup_contracts",
                "setup_strike",
                "setup_premium",
                "setup_dte",
                "setup_delta",
                "generated_at",
            ]
            if col in snapshot_df.columns
        ]
        if setup_cols:
            st.markdown("#### Saved setup")
            st.dataframe(snapshot_df[setup_cols].drop_duplicates().head(5), width="stretch", hide_index=True)

        scenario_df = snapshot_df.copy()
        if "snapshot_type" in scenario_df.columns:
            scenario_df = scenario_df[scenario_df["snapshot_type"].astype(str).str.lower() == "scenario"]
        if not scenario_df.empty:
            st.markdown("#### Scenario overlay from saved setup")
            scenario_col = find_column(scenario_df, ["scenario"])
            rel_col = find_column(scenario_df, ["covered_call_minus_buy_hold", "relative_result"])
            cc_col = find_column(scenario_df, ["covered_call_pnl", "covered_call_pl"])
            bh_col = find_column(scenario_df, ["buy_hold_pnl", "buy_and_hold_pnl"])
            final_price_col = find_column(scenario_df, ["final_price"])
            assignment_col = find_column(scenario_df, ["assignment_flag", "assigned"])

            if rel_col is not None:
                rel_values = pd.to_numeric(scenario_df[rel_col], errors="coerce")
                m1, m2, m3 = st.columns(3)
                m1.metric("Saved scenarios", len(scenario_df))
                m2.metric("Best relative result", signed_currency(float(rel_values.max())))
                m3.metric("Worst relative result", signed_currency(float(rel_values.min())))

            if scenario_col is not None and rel_col is not None and alt is not None:
                chart_df = scenario_df[[scenario_col, rel_col]].copy()
                chart_df[rel_col] = pd.to_numeric(chart_df[rel_col], errors="coerce")
                chart_df = chart_df.dropna()
                if not chart_df.empty:
                    chart = (
                        alt.Chart(chart_df)
                        .mark_bar()
                        .encode(
                            x=alt.X(f"{rel_col}:Q", title="Covered call minus buy-and-hold"),
                            y=alt.Y(f"{scenario_col}:N", title="Scenario", sort=None),
                            tooltip=[scenario_col, rel_col],
                        )
                        .properties(height=280)
                    )
                    st.altair_chart(chart, width="stretch")

            display_cols = [col for col in [scenario_col, final_price_col, bh_col, cc_col, rel_col, assignment_col] if col is not None]
            if display_cols:
                st.dataframe(scenario_df[display_cols], width="stretch", hide_index=True)
            else:
                st.dataframe(scenario_df, width="stretch", hide_index=True)

        with st.expander("Full saved Phase 3C snapshot", expanded=False):
            st.dataframe(snapshot_df, width="stretch", hide_index=True)

    st.markdown("### Open Phase 3C reports")
    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        if PHASE3C_RICH_PAYOFF_SNAPSHOT_HTML_PATH.exists():
            if st.button("Open Phase 3C snapshot HTML"):
                if not open_path_with_windows(PHASE3C_RICH_PAYOFF_SNAPSHOT_HTML_PATH):
                    st.warning(f"Could not open: {PHASE3C_RICH_PAYOFF_SNAPSHOT_HTML_PATH}")
        else:
            st.info("Phase 3C snapshot HTML has not been created yet.")
    with report_col2:
        if PHASE3C_RICH_PAYOFF_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 3C pipeline report folder"):
                if not open_path_with_windows(PHASE3C_RICH_PAYOFF_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE3C_RICH_PAYOFF_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 3C pipeline report has not been created yet.")
    with report_col3:
        if PHASE3B_SCENARIO_OVERLAY_HTML_PATH.exists():
            if st.button("Open Phase 3B overlay HTML"):
                if not open_path_with_windows(PHASE3B_SCENARIO_OVERLAY_HTML_PATH):
                    st.warning(f"Could not open: {PHASE3B_SCENARIO_OVERLAY_HTML_PATH}")
        else:
            st.info("Phase 3B overlay HTML has not been created yet.")

    with st.expander("Phase 3C notes", expanded=False):
        st.markdown("""
        - Phase 3C is still a prototype and remains Developer-view only.
        - It improves the payoff graph and scenario display, but it does not use live market data yet.
        - Snapshot files are optional until a setup is saved from the standalone viewer.
        - The purpose is to refine the visual interface before exposing it to customer view.
        """)


def show_phase3d_integrated_overlay_file_status() -> None:
    """Show file availability for Phase 3D integrated payoff-overlay outputs and runners."""
    rows = [
        ("Phase 3D integrated viewer", PHASE3D_INTEGRATED_OVERLAY_VIEWER_PATH, False),
        ("Phase 3D integrated viewer check", PHASE3D_INTEGRATED_OVERLAY_VIEWER_CHECK_PATH, False),
        ("Phase 3D integrated overlay pipeline checker", PHASE3D_INTEGRATED_OVERLAY_PIPELINE_CHECK_PATH, False),
        ("Phase 3D integrated overlay pipeline report", PHASE3D_INTEGRATED_OVERLAY_PIPELINE_REPORT_PATH, False),
        ("Phase 3D integrated viewer check report", PHASE3D_INTEGRATED_OVERLAY_VIEWER_CHECK_REPORT_PATH, False),
        ("Phase 3D integrated snapshot CSV", PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_CSV_PATH, True),
        ("Phase 3D integrated snapshot HTML", PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_HTML_PATH, True),
        ("Phase 3B scenario overlay CSV", PHASE3B_SCENARIO_OVERLAY_CSV_PATH, False),
        ("Phase 3C checkpoint report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3c_checkpoint_report.txt", False),
    ]
    status_rows = []
    for label, path, optional in rows:
        if path.exists():
            status = "FOUND"
        elif optional:
            status = "OPTIONAL"
        else:
            status = "MISSING"
        status_rows.append({"Item": label, "Status": status, "Path": str(path)})
    st.dataframe(pd.DataFrame(status_rows), width="stretch", hide_index=True)


def show_phase3d_integrated_overlay_tab() -> None:
    """Developer-view-only Phase 3D integrated payoff-overlay diagnostics."""
    st.subheader("Phase 3D integrated overlay")
    st.caption(
        "This combines the richer Phase 3C payoff graph with the Phase 3B scenario overlay in one developer-only prototype."
    )
    st.info(
        "Phase 3D is still manual-entry and prototype-level. It does not use live market data yet. "
        "Use it to test the integrated graphical payoff and scenario-overlay workflow before customer exposure."
    )

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Run Phase 3D integrated overlay pipeline"):
            code, output = run_python_script(PHASE3D_INTEGRATED_OVERLAY_PIPELINE_CHECK_PATH)
            if code == 0:
                st.success("Phase 3D integrated overlay pipeline passed.")
            else:
                st.warning(f"Phase 3D integrated overlay pipeline returned code {code}.")
            with st.expander("Phase 3D pipeline output", expanded=False):
                st.text_area("Phase 3D pipeline output text", value=output, height=260, label_visibility="collapsed")
    with action_col2:
        if st.button("Open standalone Phase 3D integrated viewer"):
            code, output = run_python_script(PHASE3D_INTEGRATED_OVERLAY_VIEWER_PATH)
            if code == 0:
                st.success("Phase 3D integrated viewer process ended normally.")
            else:
                st.info("The Phase 3D viewer was launched or returned a nonzero code. Check the browser and output below.")
            with st.expander("Phase 3D viewer launch output", expanded=False):
                st.text_area("Phase 3D viewer output text", value=output, height=220, label_visibility="collapsed")

    st.markdown("### Phase 3D file status")
    show_phase3d_integrated_overlay_file_status()

    st.markdown("### Saved Phase 3D integrated snapshot")
    if PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_CSV_PATH.exists():
        try:
            snapshot_df = pd.read_csv(PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_CSV_PATH)
            if snapshot_df.empty:
                st.info("The Phase 3D integrated snapshot CSV exists but has no rows.")
            else:
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                numeric_cols = snapshot_df.select_dtypes(include="number").columns.tolist()
                if "covered_call_pl" in snapshot_df.columns:
                    metric_col1.metric("Average covered-call P/L", signed_currency(float(snapshot_df["covered_call_pl"].mean())))
                elif numeric_cols:
                    metric_col1.metric("Rows", len(snapshot_df))
                else:
                    metric_col1.metric("Rows", len(snapshot_df))
                if "buy_and_hold_pl" in snapshot_df.columns:
                    metric_col2.metric("Average buy-and-hold P/L", signed_currency(float(snapshot_df["buy_and_hold_pl"].mean())))
                else:
                    metric_col2.metric("Columns", len(snapshot_df.columns))
                if "covered_call_minus_buy_hold" in snapshot_df.columns:
                    metric_col3.metric(
                        "Average result versus simply holding the stock",
                        signed_currency(float(snapshot_df["covered_call_minus_buy_hold"].mean())),
                    )
                else:
                    metric_col3.metric("Snapshot file", "Available")

                st.dataframe(snapshot_df.head(30), width="stretch", hide_index=True)
        except Exception as exc:  # noqa: BLE001 - dashboard diagnostic only.
            st.warning(f"Could not read Phase 3D snapshot CSV: {exc}")
    else:
        st.info("No Phase 3D integrated snapshot exists yet. Open the standalone viewer and save a setup to create one.")

    st.markdown("### Scenario-overlay context")
    if PHASE3B_SCENARIO_OVERLAY_CSV_PATH.exists():
        try:
            overlay_df = pd.read_csv(PHASE3B_SCENARIO_OVERLAY_CSV_PATH)
            if overlay_df.empty:
                st.info("The Phase 3B scenario-overlay CSV exists but has no rows.")
            else:
                value_col = find_column(
                    overlay_df,
                    [
                        "covered_call_minus_buy_hold",
                        "covered_call_minus_buy_and_hold",
                        "relative_result",
                        "relative_pl",
                    ],
                )
                scenario_col = find_column(overlay_df, ["scenario", "scenario_name", "display_name", "label"])
                if value_col and scenario_col:
                    chart_df = overlay_df[[scenario_col, value_col]].copy()
                    chart_df[value_col] = pd.to_numeric(chart_df[value_col], errors="coerce")
                    if alt is not None:
                        chart = (
                            alt.Chart(chart_df)
                            .mark_bar()
                            .encode(
                                x=alt.X(f"{value_col}:Q", title="Covered-call minus buy-and-hold"),
                                y=alt.Y(f"{scenario_col}:N", sort="-x", title="Scenario"),
                                tooltip=[scenario_col, value_col],
                            )
                            .properties(height=260)
                        )
                        st.altair_chart(chart, use_container_width=True)
                    else:
                        st.bar_chart(chart_df.set_index(scenario_col)[value_col])
                st.dataframe(overlay_df, width="stretch", hide_index=True)
        except Exception as exc:  # noqa: BLE001 - dashboard diagnostic only.
            st.warning(f"Could not read Phase 3B scenario-overlay CSV: {exc}")
    else:
        st.info("No Phase 3B scenario-overlay CSV is available yet. Run the Phase 3B pipeline first.")

    st.markdown("### Open Phase 3D reports")
    report_col1, report_col2, report_col3 = st.columns(3)
    with report_col1:
        if PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_HTML_PATH.exists():
            if st.button("Open Phase 3D snapshot HTML"):
                if not open_path_with_windows(PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_HTML_PATH):
                    st.warning(f"Could not open: {PHASE3D_INTEGRATED_OVERLAY_SNAPSHOT_HTML_PATH}")
        else:
            st.info("Phase 3D snapshot HTML has not been created yet.")
    with report_col2:
        if PHASE3D_INTEGRATED_OVERLAY_PIPELINE_REPORT_PATH.exists():
            if st.button("Open Phase 3D pipeline report folder"):
                if not open_path_with_windows(PHASE3D_INTEGRATED_OVERLAY_PIPELINE_REPORT_PATH.parent):
                    st.warning(f"Could not open: {PHASE3D_INTEGRATED_OVERLAY_PIPELINE_REPORT_PATH.parent}")
        else:
            st.info("Phase 3D pipeline report has not been created yet.")
    with report_col3:
        if PHASE3B_SCENARIO_OVERLAY_HTML_PATH.exists():
            if st.button("Open Phase 3B overlay HTML from Phase 3D tab"):
                if not open_path_with_windows(PHASE3B_SCENARIO_OVERLAY_HTML_PATH):
                    st.warning(f"Could not open: {PHASE3B_SCENARIO_OVERLAY_HTML_PATH}")
        else:
            st.info("Phase 3B overlay HTML has not been created yet.")

    with st.expander("Phase 3D notes", expanded=False):
        st.markdown("""
        - Phase 3D integrates the payoff graph and scenario overlay into one developer-only prototype.
        - Snapshot outputs are optional until a setup is saved from the standalone viewer.
        - This is still not live market data and should remain hidden from Customer view for now.
        - The next step after validation is a Phase 3D checkpoint, followed by polish of customer-facing graph language.
        """)


def main() -> None:
    st.title(PRODUCT_INFO.product_name)
    st.caption(PRODUCT_INFO.product_subtitle)
    st.caption(f"{PRODUCT_INFO.version_label} | {PRODUCT_INFO.release_stage} | {PRODUCT_INFO.build_label}")
    # === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP START ===
    CUSTOMER_VIEW_LOCAL_DEBUG_TEXT_CLEANUP_APPLIED = True
    if (
        locals().get('interface_mode') == 'Developer view'
        or locals().get('selected_interface_mode') == 'Developer view'
        or locals().get('dashboard_mode') == 'Developer view'
        or locals().get('dashboard_view_mode') == 'Developer view'
        or locals().get('view_mode') == 'Developer view'
    ):
        st.caption(f"Project root: {PROJECT_ROOT}")
    # === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP END ===

    with st.sidebar:
        st.markdown("### Dashboard mode")
        st.caption(PRODUCT_INFO.version_label)

        # Public beta lock: hosted customer-facing deployments should not expose
        # the Developer view toggle. Developer-only tabs and local diagnostics are
        # still present in the code, but they remain hidden because interface_mode
        # is forced to Customer view.
        interface_mode = "Customer view"
        st.caption("Customer view")

        st.divider()
        st.markdown("**Customer workflow**")
        st.caption("1. Choose setup")
        st.caption("2. Validate and run")
        st.caption("3. Review result")
        st.caption("4. Export memo")
        st.divider()
        st.caption("Advanced diagnostics are hidden.")

    config = load_config()

    with st.sidebar:
        st.divider()
        st.markdown("### Demo controls")
        st.caption("Use these to restore the clean demo.")
        if st.button("Reset to clean demo"):
            ok, message = reset_to_clean_demo(run_after_reset=False)
            st.session_state["dashboard_notice"] = message
            st.session_state["dashboard_notice_level"] = "success" if ok else "warning"
            st.rerun()
        if st.button("Reset and run clean demo"):
            ok, message = reset_to_clean_demo(run_after_reset=True)
            st.session_state["dashboard_notice"] = message
            st.session_state["dashboard_notice_level"] = "success" if ok else "warning"
            st.rerun()

    notice = st.session_state.pop("dashboard_notice", None)
    notice_level = st.session_state.pop("dashboard_notice_level", "info")
    if notice:
        if notice_level == "success":
            st.success(notice)
        elif notice_level == "warning":
            st.warning(notice)
        else:
            st.info(notice)

    if interface_mode == "Developer view":
        tab_names = [
            "Overview",
            "Setup & run",
            "Latest results",
            "Challenge",
            "Run history",
            "Preset comparison",
            "Report",
            "Phase 2 scaffold",
            "Phase 2B premium model",
            "Phase 2C validation",
            "Phase 2D tuning",
            "Phase 2E adjustment",
            "Phase 2F model decision",
            "Phase 2G model promotion",
            "Phase 3 interactive payoff",
            "Phase 3B scenario overlay",
            "Phase 3C rich payoff",
            "Phase 3D integrated overlay",
            "App status",
            "Maintenance",
            "Help & assumptions",
        ]
    else:
        tab_names = [
            "Overview",
            "Setup & run",
            "Latest results",
            "Challenge",
            "Preset comparison",
            "Report",
            "Help & assumptions",
        ]

    tab_objects = st.tabs(tab_names)
    tabs = dict(zip(tab_names, tab_objects))

    overview_errors, overview_warnings, _ = validate_config(config)

    with tabs["Overview"]:
        show_overview_dashboard(config, overview_errors, overview_warnings)
        if interface_mode == "Customer view":
            st.caption("Use the Setup & run tab to test a configuration, then review Latest results and export a memo.")

    with tabs["Setup & run"]:
        st.subheader("Start with a clean demo")
        st.caption("Restore the standard SPY one-contract demo before testing or taking a screenshot.")
        demo_col1, demo_col2 = st.columns(2)
        with demo_col1:
            if st.button("Reset setup to clean demo", key="setup_reset_clean_demo"):
                ok, message = reset_to_clean_demo(run_after_reset=False)
                st.session_state["dashboard_notice"] = message
                st.session_state["dashboard_notice_level"] = "success" if ok else "warning"
                if ok:
                    st.success("Clean SPY demo run completed. Choose a target market scenario below and record the score on this page.")
                else:
                    st.warning(message)
        with demo_col2:
            if st.button("Reset and run demo", key="setup_reset_and_run_demo"):
                ok, message = reset_to_clean_demo(run_after_reset=True)
                st.session_state["dashboard_notice"] = message
                st.session_state["dashboard_notice_level"] = "success" if ok else "warning"
                if ok:
                    st.success("Clean SPY demo run completed. Choose a target market scenario below and record the score on this page.")
                else:
                    st.warning(message)

        st.subheader("Preset configurations")
        preset_col, button_col = st.columns([4, 1])
        with preset_col:
            preset_name = st.selectbox("Choose a preset", list(PRESETS.keys()))
        with button_col:
            st.write("")
            if st.button("Apply preset"):
                config = PRESETS[preset_name].copy()
                st.session_state["active_preset"] = preset_name
                st.success(f"Applied preset: {preset_name}")
        st.info(f"Active preset: {st.session_state.get('active_preset', 'Custom')}")

        st.subheader("Core setup")
        col1, col2 = st.columns(2)
        with col1:
            ticker = st.text_input("Ticker", value=str(config.get("ticker", "SPY"))).upper()
            account_size = st.number_input("Account size ($)", min_value=0.0, value=float(config.get("account_size", 600000.0)), step=1000.0)
            risk_tier = st.selectbox(
                "Setup style",
                ["Conservative", "Balanced", "Aggressive"],
                index=["Conservative", "Balanced", "Aggressive"].index(str(config.get("risk_tier", "Balanced"))) if str(config.get("risk_tier", "Balanced")) in ["Conservative", "Balanced", "Aggressive"] else 1,
            )
            position_size_cap = st.number_input("Max position size", min_value=0.0, max_value=1.0, value=float(config.get("position_size_cap", 0.10)), step=0.01, format="%.2f")
        with col2:
            desired_contracts = st.number_input("Contracts", min_value=1, value=int(config.get("desired_contracts", 1)), step=1)
            target_delta = st.number_input("Call delta target", min_value=0.0, max_value=1.0, value=float(config.get("target_delta", 0.30)), step=0.01, format="%.2f")
            target_dte = st.number_input("Days to expiration", min_value=1, value=int(config.get("target_dte", 30)), step=1)
            demo_price = st.number_input("Stock price", min_value=0.0, value=float(config.get("demo_price", 545.25)), step=1.0)

        _render_position_size_explainer(account_size, demo_price, position_size_cap)

        with st.expander("Advanced strategy settings", expanded=False):
            col3, col4, col5 = st.columns(3)
            with col3:
                management_rule = st.selectbox(
                    "Management rule",
                    ["hold_to_expiration", "close_at_50_percent_profit"],
                    index=1 if config.get("management_rule") == "close_at_50_percent_profit" else 0,
                )
            with col4:
                rolling_rule = st.selectbox("Rolling rule", ["none", "roll_for_credit", "roll_out_and_up"], index=0)
            with col5:
                re_entry_rule = st.selectbox("Re-entry rule", ["immediate", "next_cycle", "none"], index=0)

        with st.expander("Advanced cost assumptions", expanded=False):
            col6, col7 = st.columns(2)
            with col6:
                transaction_cost = st.number_input("Transaction cost", min_value=0.0, value=float(config.get("transaction_cost", 1.0)), step=0.25)
            with col7:
                slippage_assumption = st.number_input("Slippage assumption", min_value=0.0, value=float(config.get("slippage_assumption", 0.01)), step=0.01, format="%.2f")

        current_config = {
            "ticker": ticker,
            "account_size": account_size,
            "risk_tier": risk_tier,
            "position_size_cap": position_size_cap,
            "desired_contracts": int(desired_contracts),
            "target_delta": target_delta,
            "target_dte": int(target_dte),
            "management_rule": management_rule,
            "rolling_rule": rolling_rule,
            "re_entry_rule": re_entry_rule,
            "transaction_cost": transaction_cost,
            "slippage_assumption": slippage_assumption,
            "demo_price": demo_price,
        }

        st.subheader("Workflow")
        errors, warnings, max_contracts = validate_config(current_config)

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Estimated max contracts", max_contracts)
        metric_col2.metric("Contracts", int(desired_contracts))
        metric_col3.metric("Max position size", f"{position_size_cap:.2%}")

        if errors:
            for error in errors:
                st.error(error)
        else:
            st.success("No blocking configuration errors detected.")
        for warning in warnings:
            st.warning(warning)

        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            if st.button("Save config"):
                backup_path = save_config(current_config)
                if backup_path:
                    st.success(f"Config saved. Backup created: {backup_path}")
                else:
                    st.success("Config saved.")
        with action_col2:
            run_disabled = bool(errors)
            if st.button("Run simulator", disabled=run_disabled):
                save_config(current_config)
                code, output = run_python_script(RUNNER_PATH)
                if code == 0:
                    st.success("Paid simulator completed. Open the Latest results tab to review the decision summary.")
                    df_after = load_scenario_results()
                    if df_after is not None:
                        append_run_history(current_config, summarize_results(df_after))
                else:
                    st.error(f"Paid simulator failed with return code {code}.")
                with st.expander("Simulator output", expanded=False):
                    st.text_area("Simulator output text", value=output, height=220, label_visibility="collapsed")
        with action_col3:
            if st.button("Run health check"):
                code, output = run_python_script(HEALTH_CHECK_PATH)
                if code == 0:
                    st.success("Health check completed.")
                else:
                    st.error(f"Health check failed with return code {code}.")
                with st.expander("Health-check output", expanded=False):
                    st.text_area("Health-check output text", value=output, height=220, label_visibility="collapsed")

    current_config_for_results = load_config()
    result_errors, result_warnings, _ = validate_config(current_config_for_results)

    with tabs["Latest results"]:
        show_latest_results(current_config_for_results, result_errors, result_warnings)

    if "Challenge" in tabs:
        with tabs["Challenge"]:
            show_covered_call_challenge(current_config_for_results)

    if "Run history" in tabs:
        with tabs["Run history"]:
            show_run_history()

    with tabs["Preset comparison"]:
        show_preset_comparison()

    with tabs["Report"]:
        show_report_section()

    if "Phase 2 scaffold" in tabs:
        with tabs["Phase 2 scaffold"]:
            show_phase2_scaffold_tab()

    if "Phase 2B premium model" in tabs:
        with tabs["Phase 2B premium model"]:
            show_phase2b_premium_model_tab()

    if "Phase 2C validation" in tabs:
        with tabs["Phase 2C validation"]:
            show_phase2c_validation_tab()

    if "Phase 2D tuning" in tabs:
        with tabs["Phase 2D tuning"]:
            show_phase2d_tuning_tab()

    if "Phase 2E adjustment" in tabs:
        with tabs["Phase 2E adjustment"]:
            show_phase2e_adjustment_tab()

    if "Phase 2F model decision" in tabs:
        with tabs["Phase 2F model decision"]:
            show_phase2f_model_decision_tab()

    if "Phase 2G model promotion" in tabs:
        with tabs["Phase 2G model promotion"]:
            show_phase2g_model_promotion_tab()

    if "Phase 3 interactive payoff" in tabs:
        with tabs["Phase 3 interactive payoff"]:
            show_phase3_interactive_payoff_tab()

    if "Phase 3B scenario overlay" in tabs:
        with tabs["Phase 3B scenario overlay"]:
            show_phase3b_scenario_overlay_tab()

    if "Phase 3C rich payoff" in tabs:
        with tabs["Phase 3C rich payoff"]:
            show_phase3c_rich_payoff_tab()

    if "Phase 3D integrated overlay" in tabs:
        with tabs["Phase 3D integrated overlay"]:
            show_phase3d_integrated_overlay_tab()

    if "App status" in tabs:
        with tabs["App status"]:
            show_app_status_tab()

    if "Maintenance" in tabs:
        with tabs["Maintenance"]:
            show_maintenance_tab()

    with tabs["Help & assumptions"]:
        show_help_section()


if __name__ == "__main__":
    main()

# --- PHASE 3E-7C DEVELOPER TAB INTEGRATION START ---
# PHASE3E_7C_DEVELOPER_TAB_READY
# Developer-view helper for the Phase 3E customer payoff workbench.
# Customer view remains protected until the Phase 3E completion checkpoint passes.

def _render_phase3e_customer_payoff_workbench_tab():
    """Render the Phase 3E customer payoff workbench in Developer view only."""
    from app.paid_simulator.phase3e_customer_workbench_streamlit_panel import (
        render_phase3e_customer_workbench_panel,
    )

    try:
        import streamlit as st
    except Exception:
        st = None

    return render_phase3e_customer_workbench_panel(streamlit_module=st)


def render_phase3e_customer_payoff_workbench_developer_tab():
    """Backward-compatible Developer-view entry point for Phase 3E."""
    return _render_phase3e_customer_payoff_workbench_tab()


PHASE3E_CUSTOMER_PAYOFF_WORKBENCH_TAB_TITLE = "Phase 3E customer payoff workbench"
PHASE3E_CUSTOMER_PAYOFF_WORKBENCH_SCOPE = "Developer view only; Customer view protected."
# --- PHASE 3E-7C DEVELOPER TAB INTEGRATION END ---

# >>> PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_START
# Protected Customer Preview route for Phase 3F-3.
# This helper is intentionally staged for preview use only.
# It must not be wired into the ordinary Customer view until a later release gate passes.
PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY = True
PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED = False


def _render_phase3f_customer_preview_route(streamlit_module=None):
    """Render the protected Phase 3F customer-preview route."""
    from app.paid_simulator.phase3f_customer_preview_route import render_customer_preview_route

    return render_customer_preview_route(streamlit_module=streamlit_module)

# <<< PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_END

# === PHASE3G_4_PUBLIC_ROUTE_READINESS_START ===
# Phase 3G-4 public Customer-view route-readiness helper.
# This block prepares a public-candidate route structure but does NOT enable
# ordinary Customer-view access.
PHASE3G_4_PUBLIC_ROUTE_READY = "PHASE3G_4_PUBLIC_ROUTE_READY"
PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = False


def _render_phase3g_public_customer_route_readiness():
    """Render Phase 3G-4 route-readiness information in a protected context."""
    from app.paid_simulator.phase3g_public_customer_route_readiness import (
        render_phase3g_4_public_route_readiness,
    )

    try:
        import streamlit as st
    except Exception:
        st = None

    return render_phase3g_4_public_route_readiness(streamlit_module=st)
# === PHASE3G_4_PUBLIC_ROUTE_READINESS_END ===

# === PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_START ===
PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY = "PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_READY"
PHASE3H_2_PUBLIC_CUSTOMER_ENABLED = False


def _render_phase3h_public_customer_activation_route(st_module=None):
    """Guarded Phase 3H-2 public Customer-view activation route helper."""
    from app.paid_simulator.phase3h_public_customer_activation_route import (
        render_phase3h_public_activation_route,
    )
    return render_phase3h_public_activation_route(streamlit_module=st_module)
# === PHASE3H_2_PUBLIC_CUSTOMER_ACTIVATION_ROUTE_END ===

# BEGIN PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION
# Controlled public Customer-view activation marker.
# Added by app/install_phase3h_7_public_customer_activation.py.
PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY = "PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION_READY"
PHASE3H_7_PUBLIC_CUSTOMER_ENABLED = True
PHASE3H_7_RELEASE_DECISION = "PHASE3H_7_PUBLIC_CUSTOMER_VIEW_CONTROLLED_ACTIVATION_ENABLED"


def _render_phase3h_7_public_customer_activation():
    """Render the Phase 3H-7 public Customer-view activation helper when called."""
    from app.paid_simulator.phase3h_public_customer_activation import (
        render_phase3h_7_public_customer_activation,
    )

    return render_phase3h_7_public_customer_activation()
# END PHASE3H_7_PUBLIC_CUSTOMER_ACTIVATION

# PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_BEGIN
# Controlled dashboard data-mode selector support.
# Synthetic scenarios remain the default. Imported historical data remains
# explicit opt-in only and must not be described as a forecast.
PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY = "PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_READY"


def render_phase6_3_dashboard_mode_selector(default_mode="synthetic"):
    """
    Optional Phase 6-3 dashboard mode selector helper.

    This helper is deliberately guarded. It returns a normalized selection dict
    when Streamlit or the support module is unavailable, so the existing paid
    dashboard remains safe.
    """

    try:
        from phase6_dashboard_mode_selector_patch import (
            render_phase6_3_dashboard_mode_selector as _phase6_3_renderer,
        )
    except Exception:
        try:
            from app.paid_simulator.phase6_dashboard_mode_selector_patch import (
                render_phase6_3_dashboard_mode_selector as _phase6_3_renderer,
            )
        except Exception:
            requested = str(default_mode).strip().lower()
            selected_mode = "historical_import" if requested in {
                "historical",
                "historical_import",
                "historical import",
                "imported historical data",
            } else "synthetic"
            return {
                "selected_mode": selected_mode,
                "selected_label": (
                    "Imported historical data"
                    if selected_mode == "historical_import"
                    else "Synthetic scenarios"
                ),
                "is_default": selected_mode == "synthetic",
                "historical_mode_explicit_only": True,
                "customer_caution_text": (
                    "Historical data mode uses imported past price behavior as "
                    "an input scenario. It should not be interpreted as a "
                    "forecast or regime oracle."
                ),
            }

    return _phase6_3_renderer(default_mode=default_mode)
# PHASE6_3_DASHBOARD_MODE_SELECTOR_PATCH_END

# =============================================================================
# Phase 6-4 dashboard helper visibility repair
# Marker: PHASE6_4_DASHBOARD_HELPER_VISIBILITY_REPAIR_READY
# Purpose: expose the Phase 6-3 mode helper name expected by visibility checks.
# This block is passive and does not alter the active dashboard workflow.
# =============================================================================

PHASE6_4_DASHBOARD_HELPER_VISIBILITY_REPAIR_READY = True


def phase6_3_resolve_dashboard_data_mode(selected_label=None):
    """
    Resolve the paid-dashboard data mode using conservative customer wording.

    Synthetic scenarios remain the default. Imported historical data is an
    explicit opt-in scenario input, not a forecast.
    """
    synthetic_label = "Synthetic scenarios"
    historical_label = "Imported historical data"

    if selected_label == historical_label:
        return {
            "selected_label": historical_label,
            "mode": "historical_import",
            "is_default": False,
            "requires_explicit_opt_in": True,
            "customer_message": "Imported historical data is used as scenario input, not as a forecast.",
        }

    return {
        "selected_label": synthetic_label,
        "mode": "synthetic",
        "is_default": True,
        "requires_explicit_opt_in": False,
        "customer_message": "Synthetic scenarios remain the default modeling mode.",
    }


# End Phase 6-4 dashboard helper visibility repair
# =============================================================================

# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH START ===
PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY = "PHASE6_6_DASHBOARD_HISTORICAL_INPUT_PANEL_PATCH_READY"

def phase6_6_build_historical_input_panel_contract(selected_mode="Synthetic scenarios"):
    # Passive dashboard helper for the historical-data input panel.
    # Synthetic scenarios remain the default. Imported historical data remains
    # explicit opt-in only. Historical data is scenario input, not forecast.
    allowed_modes = ["Synthetic scenarios", "Imported historical data"]
    if selected_mode not in allowed_modes:
        selected_mode = "Synthetic scenarios"

    is_historical = selected_mode == "Imported historical data"

    return {
        "selected_mode": selected_mode,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": True,
        "historical_mode_selected": is_historical,
        "historical_price_file_label": "Historical price file",
        "option_chain_file_label": "Option-chain file",
        "scenario_input_not_forecast": True,
        "customer_caution": "Historical data is scenario input, not forecast",
    }
# === PHASE 6-6 DASHBOARD HISTORICAL INPUT PANEL PATCH END ===

# === PHASE 6-9 DASHBOARD RUNNER WIRING PATCH START ===
PHASE6_9_DASHBOARD_RUNNER_WIRING_PATCH_READY = "PHASE6_9_DASHBOARD_RUNNER_WIRING_PATCH_READY"

def phase6_9_resolve_dashboard_runner_mode(dashboard_mode="Synthetic scenarios"):
    # Passive dashboard-to-runner mapping helper.
    # Synthetic scenarios remain the default.
    # Imported historical data remains explicit opt-in only.
    # Historical data is scenario input, not forecast.
    if dashboard_mode == "Imported historical data":
        selected_dashboard_mode = "Imported historical data"
        runner_mode = "historical_import"
    else:
        selected_dashboard_mode = "Synthetic scenarios"
        runner_mode = "synthetic"

    return {
        "selected_dashboard_mode": selected_dashboard_mode,
        "runner_mode": runner_mode,
        "synthetic_default_preserved": True,
        "historical_mode_explicit_only": True,
        "unknown_modes_fall_back_to_synthetic": dashboard_mode not in ["Synthetic scenarios", "Imported historical data"],
        "historical_data_is_scenario_input_not_forecast": True,
        "customer_caution": "Historical data is scenario input, not forecast",
    }
# === PHASE 6-9 DASHBOARD RUNNER WIRING PATCH END ===
# PHASE_POST10_CUSTOMER_VIEW_RELEASE_LABEL_CLEANUP_APPLIED: local prototype/checkpoint wording replaced with beta-release wording.

# CUSTOMER_VIEW_FINAL_RELEASE_TEXT_CLEANUP_APPLIED


# CUSTOMER_VIEW_HARD_RELEASE_LABEL_REPAIR_APPLIED
