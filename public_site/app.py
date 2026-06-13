"""
public_site/app.py

Public-facing Streamlit prototype for the Covered Call Simulator.

Version 45
----------
This version keeps the public website shell, reads existing simulator output
files when available, keeps the organized sidebar navigation, FAQ, waitlist,
and Product Roadmap pages, and improves navigation by moving Product Roadmap,
Pricing, and Contact / Waitlist Preview into a Product section while separating
Disclaimers and About into a Legal section.

The app remains separate from the internal development dashboard located at:

    dashboard/app.py

Purpose
-------
This public-site prototype introduces the product, explains the simulator,
shows a free simulator preview, describes paid features, and displays public
disclaimer language.

Important
---------
This app does not:
    - run the full simulator
    - modify app/main.py
    - modify dashboard/app.py
    - rewrite output files
    - place trades
    - provide financial advice

Run from PyCharm using:

    app/run_public_site.py

Recommended local URL:

    http://localhost:8502
"""

from datetime import datetime
from pathlib import Path
import re
import time

import altair as alt
import pandas as pd
import streamlit as st


# =============================================================================
# Path setup
# =============================================================================

PUBLIC_SITE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PUBLIC_SITE_DIR.parent
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
COMPARISON_DIR = OUTPUTS_DIR / "tables" / "comparison"


WEBSITE_PLAN_PATH = DOCS_DIR / "website_plan.md"
LANDING_PAGE_COPY_PATH = DOCS_DIR / "landing_page_copy.md"
FREE_VS_PAID_PATH = DOCS_DIR / "free_vs_paid_features.md"
PUBLIC_DISCLAIMER_PATH = DOCS_DIR / "public_disclaimer.md"
DEVELOPMENT_ROADMAP_PATH = DOCS_DIR / "development_roadmap.md"
SIMULATOR_WORKFLOW_PATH = DOCS_DIR / "simulator_user_workflow.md"


STRATEGY_DASHBOARD_REPORT_PATH = (
    COMPARISON_DIR / "strategy_dashboard_report.txt"
)

CURRENT_PRICE_SNAPSHOT_PATH = (
    COMPARISON_DIR / "current_price_snapshot.csv"
)

CURRENT_REGIME_SNAPSHOT_PATH = (
    COMPARISON_DIR / "current_regime_snapshot.csv"
)


# =============================================================================
# Streamlit page configuration
# =============================================================================

st.set_page_config(
    page_title="Covered Call Simulator",
    page_icon="📈",
    layout="wide",
)


# =============================================================================
# Style helpers
# =============================================================================

def inject_public_site_css() -> None:
    """
    Add light custom styling for the public prototype.

    Streamlit remains the rendering engine. These styles only improve spacing
    and make the prototype feel more like a public-facing website.
    """
    st.markdown(
        """
        <style>
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 4rem;
                max-width: 1180px;
            }

            .public-hero {
                padding: 2.2rem 2.4rem;
                border: 1px solid rgba(128, 128, 128, 0.25);
                border-radius: 18px;
                margin-bottom: 1.5rem;
                background: linear-gradient(
                    135deg,
                    rgba(120, 120, 120, 0.10),
                    rgba(120, 120, 120, 0.03)
                );
            }

            .public-hero h1 {
                font-size: 3rem;
                line-height: 1.05;
                margin-bottom: 0.8rem;
            }

            .public-hero p {
                font-size: 1.15rem;
                line-height: 1.55;
                margin-bottom: 0.2rem;
            }

            .small-muted {
                color: rgba(120, 120, 120, 0.95);
                font-size: 0.92rem;
                line-height: 1.45;
            }

            .feature-card {
                padding: 1.05rem 1.15rem;
                border: 1px solid rgba(128, 128, 128, 0.25);
                border-radius: 14px;
                min-height: 155px;
                margin-bottom: 0.85rem;
            }

            .feature-card h3 {
                margin-top: 0;
                margin-bottom: 0.45rem;
                font-size: 1.08rem;
            }

            .feature-card p {
                margin-bottom: 0;
                line-height: 1.45;
            }

            .callout-box {
                padding: 1.0rem 1.1rem;
                border: 1px solid rgba(128, 128, 128, 0.25);
                border-radius: 14px;
                margin-top: 0.8rem;
                margin-bottom: 0.8rem;
            }

            .badge-row span {
                display: inline-block;
                padding: 0.25rem 0.55rem;
                border: 1px solid rgba(128, 128, 128, 0.28);
                border-radius: 999px;
                margin: 0.15rem 0.15rem 0.15rem 0;
                font-size: 0.88rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_feature_card(title: str, body: str) -> None:
    """
    Display a simple card for public-site feature descriptions.
    """
    st.markdown(
        f"""
        <div class="feature-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_badges(labels: list[str]) -> None:
    """
    Display a row of small pill-style labels.
    """
    badge_html = " ".join(
        f"<span>{label}</span>" for label in labels
    )

    st.markdown(
        f"""
        <div class="badge-row">
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# File helpers
# =============================================================================

def load_markdown_file(path: Path) -> str:
    """
    Load a markdown document if it exists.
    """
    if not path.exists():
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        try:
            return path.read_text()
        except Exception:
            return ""


def load_text_file(path: Path) -> str:
    """
    Load a text file if it exists.
    """
    return load_markdown_file(path)


@st.cache_data(show_spinner=False)
def load_csv_cached(path_text: str, modified_token: int) -> pd.DataFrame:
    """
    Load a CSV file with cache invalidation based on modified timestamp.
    """
    path = Path(path_text)

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def get_file_modified_token(path: Path) -> int:
    """
    Return a file modified token for Streamlit cache invalidation.
    """
    if not path.exists():
        return 0

    try:
        return path.stat().st_mtime_ns
    except Exception:
        return 0


def load_csv(path: Path) -> pd.DataFrame:
    """
    Load a CSV file with cache invalidation.
    """
    return load_csv_cached(
        str(path),
        get_file_modified_token(path),
    )


def clean_column_name(column: str) -> str:
    """
    Convert a source column name into a public-facing display name.
    """
    text = str(column).strip()
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text.title()


def clean_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a display-friendly copy of a dataframe.
    """
    if df.empty:
        return df

    display_df = df.copy()
    display_df.columns = [
        clean_column_name(column)
        for column in display_df.columns
    ]

    return display_df


def find_first_column_containing(
    df: pd.DataFrame,
    required_terms: list[str],
    excluded_terms: list[str] | None = None,
) -> str | None:
    """
    Find the first column whose normalized name contains all required terms
    and none of the excluded terms.
    """
    if excluded_terms is None:
        excluded_terms = []

    if df.empty:
        return None

    for column in df.columns:
        normalized = (
            str(column)
            .lower()
            .replace("_", " ")
            .replace("-", " ")
        )

        has_required_terms = all(
            term.lower() in normalized
            for term in required_terms
        )

        has_excluded_terms = any(
            term.lower() in normalized
            for term in excluded_terms
        )

        if has_required_terms and not has_excluded_terms:
            return column

    return None


def get_numeric_value(row: pd.Series, column: str | None) -> float | None:
    """
    Extract a numeric value from a dataframe row.
    """
    if column is None:
        return None

    try:
        value = pd.to_numeric(row[column], errors="coerce")
    except Exception:
        return None

    if pd.isna(value):
        return None

    return float(value)


def format_percent_value(value: float | None) -> str:
    """
    Format a decimal value as a percentage when appropriate.

    Many simulator output columns store outperformance as decimal returns,
    such as 0.0449 for 4.49%.
    """
    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


def format_money_value(value: float | None) -> str:
    """
    Format a numeric value as a dollar amount.
    """
    if value is None:
        return "N/A"

    return f"${value:,.0f}"


def format_number_value(value: float | None) -> str:
    """
    Format a numeric value with one decimal place when useful.
    """
    if value is None:
        return "N/A"

    return f"{value:.1f}"


def build_public_rule_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a compact public-facing rule summary from a wide simulator table.

    The raw management_rule_comparison.csv can contain many diagnostic columns.
    This function extracts a small set of columns that are easier for a public
    user to understand.
    """
    if df.empty:
        return pd.DataFrame()

    regime_col = find_column(
        df,
        [
            "Regime",
            "Market Regime",
            "Scenario",
        ],
    )

    hold_out_col = find_first_column_containing(
        df,
        required_terms=["hold", "outperformance"],
    )

    close_out_col = find_first_column_containing(
        df,
        required_terms=["close", "outperformance"],
    )

    hold_net_col = find_first_column_containing(
        df,
        required_terms=["hold", "net", "option"],
    )

    close_net_col = find_first_column_containing(
        df,
        required_terms=["close", "net", "option"],
    )

    hold_premium_col = find_first_column_containing(
        df,
        required_terms=["hold", "total", "premium"],
        excluded_terms=["gross"],
    )

    close_premium_col = find_first_column_containing(
        df,
        required_terms=["close", "total", "premium"],
        excluded_terms=["gross"],
    )

    hold_assignment_col = find_first_column_containing(
        df,
        required_terms=["hold", "assignment"],
    )

    close_assignment_col = find_first_column_containing(
        df,
        required_terms=["close", "assignment"],
    )

    rows = []

    for _, row in df.iterrows():
        regime = "All scenarios"

        if regime_col is not None:
            regime = str(row[regime_col])

        hold_out = get_numeric_value(row, hold_out_col)
        close_out = get_numeric_value(row, close_out_col)
        hold_net = get_numeric_value(row, hold_net_col)
        close_net = get_numeric_value(row, close_net_col)
        hold_premium = get_numeric_value(row, hold_premium_col)
        close_premium = get_numeric_value(row, close_premium_col)
        hold_assignments = get_numeric_value(row, hold_assignment_col)
        close_assignments = get_numeric_value(row, close_assignment_col)

        better_rule = "N/A"

        if hold_out is not None and close_out is not None:
            if close_out > hold_out:
                better_rule = "Close at 50%"
            elif hold_out > close_out:
                better_rule = "Hold to expiration"
            else:
                better_rule = "Tie"

        rows.append(
            {
                "Regime": regime,
                "Better Rule": better_rule,
                "Hold Outperformance": format_percent_value(hold_out),
                "Close 50% Outperformance": format_percent_value(close_out),
                "Hold Net Option Effect": format_money_value(hold_net),
                "Close 50% Net Option Effect": format_money_value(close_net),
                "Hold Premium": format_money_value(hold_premium),
                "Close 50% Premium": format_money_value(close_premium),
                "Hold Assignments": format_number_value(hold_assignments),
                "Close 50% Assignments": format_number_value(close_assignments),
            }
        )

    return pd.DataFrame(rows)


def display_rule_summary_interpretation(public_summary_df: pd.DataFrame) -> None:
    """
    Display a plain-English interpretation of the compact public rule summary.
    """
    if public_summary_df.empty:
        return

    if "Better Rule" not in public_summary_df.columns:
        return

    better_rule_counts = (
        public_summary_df["Better Rule"]
        .astype(str)
        .value_counts()
        .to_dict()
    )

    hold_count = int(better_rule_counts.get("Hold to expiration", 0))
    close_count = int(better_rule_counts.get("Close at 50%", 0))
    tie_count = int(better_rule_counts.get("Tie", 0))

    total_count = len(public_summary_df)

    st.markdown("### Rule Summary Interpretation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Hold wins", hold_count)

    with col2:
        st.metric("Close 50% wins", close_count)

    with col3:
        st.metric("Ties", tie_count)

    with st.container(border=True):
        if hold_count > close_count:
            st.write(
                "In this preview output, holding to expiration performs better "
                f"in {hold_count} of {total_count} displayed regimes."
            )
        elif close_count > hold_count:
            st.write(
                "In this preview output, closing at 50% profit performs better "
                f"in {close_count} of {total_count} displayed regimes."
            )
        else:
            st.write(
                "In this preview output, the displayed regimes are split "
                "between holding to expiration and closing at 50% profit."
            )

        st.write(
            "This does not mean one rule is universally superior. The better "
            "rule changes with market regime, price path, option premium, and "
            "account-size constraints."
        )

        st.caption(
            "Interpretation is based on the compact public summary table. "
            "It is for education only and is not a trade recommendation."
        )


def display_rule_comparison_results(rule_df: pd.DataFrame) -> pd.DataFrame:
    """
    Display a public-facing summary table, with the raw table in an expander.

    Returns the dataframe that should be used in downloadable reports.
    """
    public_summary_df = build_public_rule_summary_table(rule_df)

    if not public_summary_df.empty:
        st.markdown("### Public Rule Summary")
        st.dataframe(
            public_summary_df,
            width="stretch",
            hide_index=True,
        )

        st.caption(
            "This compact table is derived from the wider simulator output. "
            "It is intended for public display."
        )

        display_rule_summary_interpretation(public_summary_df)

        with st.expander("Show raw simulator output", expanded=False):
            st.dataframe(
                clean_dataframe_for_display(rule_df),
                width="stretch",
                hide_index=True,
            )

        return public_summary_df

    st.dataframe(
        clean_dataframe_for_display(rule_df),
        width="stretch",
        hide_index=True,
    )

    return rule_df.copy()


def find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """
    Find the first dataframe column matching one of the candidate names.

    Matching ignores case, spaces, hyphens, and underscores.
    """
    if df.empty:
        return None

    normalized_map = {}

    for column in df.columns:
        normalized = (
            str(column)
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )
        normalized_map[normalized] = column

    for candidate in candidates:
        normalized_candidate = (
            candidate
            .lower()
            .replace("_", "")
            .replace("-", "")
            .replace(" ", "")
        )

        if normalized_candidate in normalized_map:
            return normalized_map[normalized_candidate]

    return None


def filter_dataframe_by_ticker(
    df: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """
    Filter a dataframe by ticker if it has a recognizable ticker column.
    """
    if df.empty:
        return df

    ticker_column = find_column(
        df,
        [
            "Ticker",
            "Symbol",
            "Underlying",
            "ETF",
        ],
    )

    if ticker_column is None:
        return df

    ticker_text = str(ticker).upper().strip()

    filtered_df = df[
        df[ticker_column].astype(str).str.upper().str.strip() == ticker_text
    ].copy()

    if filtered_df.empty:
        return df

    return filtered_df


# =============================================================================
# Output discovery helpers
# =============================================================================

def discover_comparison_csv_files() -> list[Path]:
    """
    Return available CSV files in the comparison output directory.
    """
    if not COMPARISON_DIR.exists():
        return []

    return sorted(COMPARISON_DIR.glob("*.csv"))


def score_rule_comparison_file(path: Path) -> int:
    """
    Score a CSV file by how likely it is to contain rule-comparison results.
    """
    name = path.name.lower()
    score = 0

    preferred_terms = [
        "management_rule",
        "rule_comparison",
        "strategy_comparison",
        "experiment_comparison",
        "dashboard",
        "comparison",
    ]

    lower_priority_terms = [
        "current_price",
        "current_regime",
        "position_sizing",
        "account_size",
        "tiers",
        "snapshot",
        "strategy_map",
    ]

    for term in preferred_terms:
        if term in name:
            score += 10

    for term in lower_priority_terms:
        if term in name:
            score -= 8

    return score


def select_best_rule_comparison_file() -> Path | None:
    """
    Select the most likely rule-comparison CSV file from existing outputs.
    """
    csv_files = discover_comparison_csv_files()

    if not csv_files:
        return None

    scored_files = [
        (score_rule_comparison_file(path), path)
        for path in csv_files
    ]

    scored_files.sort(
        key=lambda item: (item[0], item[1].name),
        reverse=True,
    )

    best_score, best_path = scored_files[0]

    if best_score <= 0:
        return None

    return best_path


def load_best_rule_comparison(ticker: str) -> tuple[pd.DataFrame, str]:
    """
    Load the best available rule-comparison table.

    Returns
    -------
    tuple[pd.DataFrame, str]
        Dataframe and source label.
    """
    selected_path = select_best_rule_comparison_file()

    if selected_path is None:
        return pd.DataFrame(), ""

    df = load_csv(selected_path)

    if df.empty:
        return pd.DataFrame(), ""

    df = filter_dataframe_by_ticker(df, ticker)

    return df, str(selected_path.relative_to(PROJECT_ROOT))


def build_free_preview_placeholder_results() -> pd.DataFrame:
    """
    Build illustrative placeholder results for the free simulator preview.

    These values are intentionally marked as illustrative. They are not
    produced by the production simulator.
    """
    rows = [
        {
            "Rule": "Hold to expiration",
            "Illustrative Total Return": "8.4%",
            "Premium Collected": "$2,450",
            "Missed Upside": "$1,850",
            "Max Drawdown": "-13.2%",
            "Interpretation": "Simple, lower maintenance, but may cap upside.",
        },
        {
            "Rule": "Close at 50% profit",
            "Illustrative Total Return": "9.1%",
            "Premium Collected": "$2,180",
            "Missed Upside": "$1,420",
            "Max Drawdown": "-12.5%",
            "Interpretation": "More active; captures premium earlier.",
        },
        {
            "Rule": "Wait 10 days",
            "Illustrative Total Return": "8.8%",
            "Premium Collected": "$1,950",
            "Missed Upside": "$1,200",
            "Max Drawdown": "-12.9%",
            "Interpretation": "Reduces overtrading but may miss premium.",
        },
    ]

    return pd.DataFrame(rows)


def build_illustrative_equity_curve() -> pd.DataFrame:
    """
    Build an illustrative total-equity curve for the public preview.

    This is not production simulator output. It is a visual placeholder that
    shows the type of equity-curve comparison the public product should
    eventually display.
    """
    rows = [
        {
            "Step": "Start",
            "Buy and Hold": 100000,
            "Hold to Expiration": 100000,
            "Close at 50%": 100000,
            "Wait 10 Days": 100000,
        },
        {
            "Step": "Month 1",
            "Buy and Hold": 101500,
            "Hold to Expiration": 101100,
            "Close at 50%": 101300,
            "Wait 10 Days": 101000,
        },
        {
            "Step": "Month 2",
            "Buy and Hold": 99000,
            "Hold to Expiration": 99600,
            "Close at 50%": 100000,
            "Wait 10 Days": 99750,
        },
        {
            "Step": "Month 3",
            "Buy and Hold": 103800,
            "Hold to Expiration": 102900,
            "Close at 50%": 103200,
            "Wait 10 Days": 103000,
        },
        {
            "Step": "Month 4",
            "Buy and Hold": 106500,
            "Hold to Expiration": 104700,
            "Close at 50%": 105100,
            "Wait 10 Days": 105000,
        },
        {
            "Step": "Month 5",
            "Buy and Hold": 104200,
            "Hold to Expiration": 104000,
            "Close at 50%": 104400,
            "Wait 10 Days": 104100,
        },
        {
            "Step": "Month 6",
            "Buy and Hold": 109500,
            "Hold to Expiration": 108400,
            "Close at 50%": 109100,
            "Wait 10 Days": 108800,
        },
    ]

    return pd.DataFrame(rows)


def display_total_equity_preview() -> None:
    """
    Display an illustrative Total Equity Over Time section.

    This section is intentionally framed as a placeholder until the public site
    is connected to production path-level simulation output.
    """
    st.markdown("### Total Equity Over Time")

    st.caption(
        "Illustrative placeholder chart. Later this section should use real "
        "path-level simulator output or replay-simulator equity history."
    )

    equity_df = build_illustrative_equity_curve()

    chart_df = equity_df.set_index("Step")

    st.line_chart(chart_df, height=360)

    with st.container(border=True):
        st.write(
            "The equity curve is the right visual anchor for the public "
            "simulator because it combines stock value, option value, realized "
            "P/L, and cash. It helps prevent users from focusing only on "
            "premium collected."
        )

        st.warning(
            "Premium collected is not the same as profit. Watch total equity, "
            "not just income."
        )

    with st.expander("Show illustrative equity data", expanded=False):
        st.dataframe(
            equity_df,
            width="stretch",
            hide_index=True,
        )


def build_current_snapshot_table(ticker: str) -> pd.DataFrame:
    """
    Build a compact table from current price and regime snapshots.
    """
    price_df = filter_dataframe_by_ticker(
        load_csv(CURRENT_PRICE_SNAPSHOT_PATH),
        ticker,
    )

    regime_df = filter_dataframe_by_ticker(
        load_csv(CURRENT_REGIME_SNAPSHOT_PATH),
        ticker,
    )

    rows = []

    if not price_df.empty:
        first_price_row = price_df.iloc[0].to_dict()

        rows.append(
            {
                "Item": "Current price source",
                "Value": first_price_row.get(
                    "Source",
                    first_price_row.get("source", "Available"),
                ),
            }
        )

        for source_column, label in [
            ("Current_Price", "Current price"),
            ("Previous_Close", "Previous close"),
            ("Quote_Status", "Quote status"),
            ("Quote_Date_ET", "Quote date ET"),
            ("Quote_Time_ET", "Quote time ET"),
        ]:
            if source_column in first_price_row:
                rows.append(
                    {
                        "Item": label,
                        "Value": first_price_row[source_column],
                    }
                )

    if not regime_df.empty:
        first_regime_row = regime_df.iloc[0].to_dict()

        for possible_column, label in [
            ("Detected_Regime", "Detected regime"),
            ("Detected_Market_Regime", "Detected regime"),
            ("Market_Regime", "Detected regime"),
            ("Current_Regime", "Detected regime"),
            ("Current_Market_Regime", "Detected regime"),
            ("Regime_Label", "Detected regime"),
            ("Latest_Regime", "Detected regime"),
            ("Scenario", "Detected regime"),
            ("Scenario_Name", "Detected regime"),
            ("Regime", "Detected regime"),
            ("Practical_Rule", "Practical rule"),
            ("Suggested_Rule", "Practical rule"),
            ("Recommended_Rule", "Practical rule"),
            ("Rule_Name", "Practical rule"),
            ("Rule", "Practical rule"),
            ("Date", "Regime date"),
            ("Market_Date", "Regime market date"),
            ("Regime_Date", "Regime date"),
            ("Last_Daily_Close_Date", "Regime market date"),
        ]:
            if possible_column in first_regime_row:
                rows.append(
                    {
                        "Item": label,
                        "Value": first_regime_row[possible_column],
                    }
                )

    return pd.DataFrame(rows)


def get_snapshot_value(snapshot_df: pd.DataFrame, item_name: str) -> str:
    """
    Extract a value from the compact current snapshot table.
    """
    if snapshot_df.empty:
        return "N/A"

    if "Item" not in snapshot_df.columns or "Value" not in snapshot_df.columns:
        return "N/A"

    match = snapshot_df[
        snapshot_df["Item"].astype(str).str.lower().str.strip()
        == item_name.lower().strip()
    ]

    if match.empty:
        return "N/A"

    value = match.iloc[0]["Value"]

    try:
        if pd.isna(value):
            return "N/A"
    except Exception:
        pass

    return str(value)


def format_snapshot_price_text(value: str) -> str:
    """
    Format a snapshot price value for display.
    """
    try:
        numeric_value = pd.to_numeric(value, errors="coerce")
    except Exception:
        return value

    if pd.isna(numeric_value):
        return "N/A"

    return f"${float(numeric_value):,.2f}"


def format_public_label(value: str) -> str:
    """
    Convert internal labels into more readable public-facing labels.
    """
    if value is None:
        return "N/A"

    text_value = str(value).strip()

    if not text_value or text_value.lower() in {"nan", "none", "n/a"}:
        return "N/A"

    label_map = {
        "Wait10d": "Wait 10 days",
        "wait10d": "Wait 10 days",
        "wait_10_days": "Wait 10 days",
        "HoldToExpiration": "Hold to expiration",
        "hold_to_expiration": "Hold to expiration",
        "CloseAt50": "Close at 50%",
        "CloseAt50Percent": "Close at 50%",
        "close_at_50_percent_profit": "Close at 50%",
        "bullish_market": "Bullish market",
        "bearish_market": "Bearish market",
        "sideways_market": "Sideways market",
        "high_volatility": "High volatility",
        "low_volatility": "Low volatility",
        "baseline": "Baseline",
    }

    if text_value in label_map:
        return label_map[text_value]

    cleaned = text_value.replace("_", " ").replace("-", " ")
    cleaned = " ".join(cleaned.split())

    if cleaned.lower() == "wait10d":
        return "Wait 10 days"

    return cleaned[:1].upper() + cleaned[1:]


def display_current_snapshot_results(ticker: str) -> None:
    """
    Display the current price/regime snapshot as public-facing cards.
    """
    st.markdown("### Current Snapshot")

    snapshot_df = build_current_snapshot_table(ticker)

    if snapshot_df.empty:
        st.warning(
            "No current price or regime snapshot was available for this "
            "ticker."
        )
        return

    current_price = format_snapshot_price_text(
        get_snapshot_value(snapshot_df, "Current price")
    )

    if get_snapshot_value(snapshot_df, "Detected regime") == "N/A":
        raw_regime_df = filter_dataframe_by_ticker(
            load_csv(CURRENT_REGIME_SNAPSHOT_PATH),
            ticker,
        )

        if not raw_regime_df.empty:
            fallback_regime_column = find_first_column_containing(
                raw_regime_df,
                required_terms=["regime"],
            )

            if fallback_regime_column is not None:
                fallback_value = raw_regime_df.iloc[0][fallback_regime_column]
                snapshot_df = pd.concat(
                    [
                        snapshot_df,
                        pd.DataFrame(
                            [
                                {
                                    "Item": "Detected regime",
                                    "Value": fallback_value,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

    quote_status = format_public_label(
        get_snapshot_value(snapshot_df, "Quote status")
    )
    detected_regime = format_public_label(
        get_snapshot_value(snapshot_df, "Detected regime")
    )
    practical_rule = format_public_label(
        get_snapshot_value(snapshot_df, "Practical rule")
    )

    snapshot_col1, snapshot_col2, snapshot_col3, snapshot_col4 = st.columns(4)

    with snapshot_col1:
        with st.container(border=True):
            st.subheader("Current price")
            st.metric("Price used", current_price)

    with snapshot_col2:
        with st.container(border=True):
            st.subheader("Quote status")
            st.metric("Status", quote_status)

    with snapshot_col3:
        with st.container(border=True):
            st.subheader("Regime")
            st.metric("Detected regime", detected_regime)

    with snapshot_col4:
        with st.container(border=True):
            st.subheader("Rule")
            st.metric("Practical rule", practical_rule)

    with st.container(border=True):
        st.write(
            "The snapshot separates current-price tradability from completed-bar "
            "regime guidance. Current price is used for account-size screening; "
            "the practical rule comes from the regime snapshot."
        )

        st.caption(
            "Regime detection is probabilistic guidance, not an oracle. "
            "Tradability is not a trade recommendation."
        )

    with st.expander("Show current snapshot details", expanded=False):
        st.dataframe(
            snapshot_df,
            width="stretch",
            hide_index=True,
        )

        raw_regime_df = filter_dataframe_by_ticker(
            load_csv(CURRENT_REGIME_SNAPSHOT_PATH),
            ticker,
        )

        if not raw_regime_df.empty:
            st.caption("Raw regime snapshot columns available:")
            st.code(", ".join([str(column) for column in raw_regime_df.columns]))


def get_current_price_for_ticker(ticker: str) -> float | None:
    """
    Return the current price for a ticker from current_price_snapshot.csv.
    """
    price_df = filter_dataframe_by_ticker(
        load_csv(CURRENT_PRICE_SNAPSHOT_PATH),
        ticker,
    )

    if price_df.empty:
        return None

    price_column = find_column(
        price_df,
        [
            "Current_Price",
            "Current Price",
            "Price",
            "Last",
            "Last Price",
        ],
    )

    if price_column is None:
        return None

    try:
        value = pd.to_numeric(price_df.iloc[0][price_column], errors="coerce")
    except Exception:
        return None

    if pd.isna(value):
        return None

    return float(value)


def format_currency(value: float | None) -> str:
    """
    Format a number as a US dollar amount for metrics and tables.
    """
    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"
    except Exception:
        pass

    return f"${value:,.0f}"


def format_currency_text(value: float | None) -> str:
    """
    Format a number as currency for Markdown text.

    Streamlit Markdown can interpret dollar signs as math delimiters, so this
    text formatter uses USD instead of a dollar sign inside warning messages.
    """
    if value is None:
        return "N/A"

    try:
        if pd.isna(value):
            return "N/A"
    except Exception:
        pass

    return f"USD {value:,.0f}"


def estimate_minimum_equity_for_one_contract(
    current_price: float | None,
    position_cap: float,
) -> float | None:
    """
    Estimate minimum equity required for one covered-call contract.

    Formula:
        100 shares * current price / per-position cap
    """
    if current_price is None:
        return None

    if position_cap <= 0:
        return None

    return 100.0 * current_price / position_cap


def display_account_size_tradability_preview(ticker: str) -> None:
    """
    Display the free-version account-size tradability preview.
    """
    st.markdown("### Account-Size Tradability Preview")

    account_size = 100000.0
    risk_tier = "Balanced"
    position_cap = 0.10

    current_price = get_current_price_for_ticker(ticker)
    minimum_equity = estimate_minimum_equity_for_one_contract(
        current_price=current_price,
        position_cap=position_cap,
    )

    is_tradable = (
        minimum_equity is not None
        and minimum_equity <= account_size
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("Free account size", format_currency(account_size))

    with metric_col2:
        st.metric("Risk tier", risk_tier)

    with metric_col3:
        st.metric("Per-position cap", "10%")

    with metric_col4:
        st.metric("Estimated min equity", format_currency(minimum_equity))

    if minimum_equity is None:
        st.warning(
            "Current price was not available, so the account-size estimate "
            "could not be calculated."
        )
    elif is_tradable:
        st.success(
            f"{ticker} passes the free-version account-size screen under "
            f"the fixed {format_currency_text(account_size)} Balanced "
            "assumption."
        )
    else:
        st.warning(
            f"{ticker} does not pass the free-version account-size screen. "
            f"Estimated minimum equity is "
            f"{format_currency_text(minimum_equity)}, which is above the "
            f"fixed {format_currency_text(account_size)} free-version "
            "account assumption."
        )

    with st.container(border=True):
        st.write(
            "This is a position-size screen only. It estimates whether one "
            "covered-call contract is practical for the selected account size."
        )

        st.caption(
            "Formula: estimated minimum equity = 100 shares * current price / "
            "selected per-position cap."
        )

        st.caption(
            "Example: if the ticker trades at USD 700 and the cap is 10%, "
            "one covered-call contract requires about USD 700,000 of account "
            "equity under that sizing rule."
        )

        st.caption(
            "Tradable means the ticker passes this account-size screen. It is "
            "not a trade recommendation."
        )


def display_free_vs_paid_interpretation(ticker: str) -> None:
    """
    Display a public-facing explanation of what is locked in the free version
    and what becomes configurable in the paid version.
    """
    st.markdown("### Free vs Paid Interpretation")

    current_price = get_current_price_for_ticker(ticker)
    free_account_size = 100000.0
    free_position_cap = 0.10

    minimum_equity = estimate_minimum_equity_for_one_contract(
        current_price=current_price,
        position_cap=free_position_cap,
    )

    free_passes = (
        minimum_equity is not None
        and minimum_equity <= free_account_size
    )

    free_col, paid_col = st.columns(2)

    with free_col:
        with st.container(border=True):
            st.subheader("Free preview")
            st.write(
                "The free version intentionally uses fixed assumptions so the "
                "basic idea is easy to understand."
            )
            st.markdown(
                """
                - Preset tickers only
                - Fixed USD 100,000 account
                - Balanced risk tier
                - Fixed 0.30 delta
                - Fixed 30 DTE
                - Limited rule comparison
                """
            )

            if free_passes:
                st.success(
                    f"{ticker} passes the fixed free-version account-size "
                    "screen."
                )
            else:
                st.warning(
                    f"{ticker} may be too large for the fixed free-version "
                    "account assumption."
                )

    with paid_col:
        with st.container(border=True):
            st.subheader("Paid configurable version")
            st.write(
                "The paid version should allow the user to adjust the "
                "assumptions to match their own account and covered-call "
                "process."
            )
            st.markdown(
                """
                - Custom account size
                - Conservative / Balanced / Aggressive risk tiers
                - Custom stock or ETF ticker
                - User-selected delta and DTE
                - Optionability and liquidity checks
                - Exportable reports
                - Replay simulator with total-equity plot
                """
            )

            if minimum_equity is not None:
                st.info(
                    "With a custom account size of at least "
                    f"{format_currency_text(minimum_equity)}, this ticker "
                    "would pass the same 10% one-contract sizing screen."
                )
            else:
                st.info(
                    "The paid version should also help diagnose missing price, "
                    "optionability, or liquidity data."
                )

    with st.container(border=True):
        st.write(
            "This distinction is useful commercially: the free version teaches "
            "the concept, while the paid version unlocks realistic account "
            "sizing, custom tickers, option parameters, reports, and replay."
        )


def display_preview_summary(ticker: str, source_label: str) -> None:
    """
    Display a concise summary at the top of the preview result area.
    """
    st.markdown("### Preview Summary")

    free_account_size = 100000.0
    free_position_cap = 0.10

    current_price = get_current_price_for_ticker(ticker)
    minimum_equity = estimate_minimum_equity_for_one_contract(
        current_price=current_price,
        position_cap=free_position_cap,
    )

    free_passes = (
        minimum_equity is not None
        and minimum_equity <= free_account_size
    )

    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        with st.container(border=True):
            st.subheader("Ticker")
            st.metric("Selected ticker", ticker)
            if current_price is not None:
                st.caption(f"Current price used: {format_currency(current_price)}")
            else:
                st.caption("Current price not available.")

    with summary_col2:
        with st.container(border=True):
            st.subheader("Free account screen")
            if minimum_equity is None:
                st.warning("Cannot calculate")
                st.caption("Missing current price.")
            elif free_passes:
                st.success("Passes")
                st.caption(
                    "The ticker fits the fixed free-version account-size "
                    "assumption."
                )
            else:
                st.warning("Too large")
                st.caption(
                    "The ticker does not fit the fixed USD 100,000 free "
                    "account assumption."
                )

    with summary_col3:
        with st.container(border=True):
            st.subheader("Data source")
            if source_label:
                st.success("Simulator output")
                st.caption(source_label)
            else:
                st.warning("Illustrative fallback")
                st.caption(
                    "No suitable rule-comparison CSV was found, so the page "
                    "used placeholder values."
                )

    if minimum_equity is not None and not free_passes:
        st.info(
            f"{ticker} is useful as an example because it shows why account "
            "sizing matters. One covered-call contract requires 100 shares, "
            f"and under the free 10% cap the estimated minimum account size is "
            f"{format_currency_text(minimum_equity)}."
        )
    elif free_passes:
        st.info(
            f"{ticker} passes the free account-size screen, so the preview can "
            "focus on rule comparison rather than account-size constraint."
        )
    else:
        st.info(
            "The preview can still show rule behavior, but the current-price "
            "data needed for account-size screening were not available."
        )


def dataframe_to_report_csv_block(df: pd.DataFrame, max_rows: int = 25) -> str:
    """
    Convert a dataframe to a compact CSV block for a Markdown report.
    """
    if df.empty:
        return "No table data available."

    display_df = clean_dataframe_for_display(df).head(max_rows)

    return display_df.to_csv(index=False)


def build_preview_report_markdown(
    ticker: str,
    source_label: str,
    used_placeholder_results: bool,
    results_df: pd.DataFrame,
) -> str:
    """
    Build a downloadable Markdown report for the public preview.
    """
    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_price = get_current_price_for_ticker(ticker)

    free_account_size = 100000.0
    free_position_cap = 0.10
    minimum_equity = estimate_minimum_equity_for_one_contract(
        current_price=current_price,
        position_cap=free_position_cap,
    )

    if minimum_equity is None:
        free_screen_status = "Cannot calculate because current price is missing."
    elif minimum_equity <= free_account_size:
        free_screen_status = "Passes the fixed free-version account-size screen."
    else:
        free_screen_status = (
            "Does not pass the fixed free-version account-size screen."
        )

    if used_placeholder_results:
        data_source_text = (
            "Illustrative fallback values. No suitable rule-comparison CSV "
            "was found."
        )
    else:
        data_source_text = f"Simulator output file: {source_label}"

    table_text = dataframe_to_report_csv_block(results_df)

    report = f"""# Covered Call Simulator — Free Preview Report

Generated: {generated_time}

## Summary

Ticker: {ticker}

Current price used: {format_currency_text(current_price)}

Free account size: {format_currency_text(free_account_size)}

Risk tier: Balanced

Per-position cap: 10%

Estimated minimum equity for one covered-call contract: {format_currency_text(minimum_equity)}

Free account screen: {free_screen_status}

Data source: {data_source_text}

## Fixed Free-Version Assumptions

- Preset ticker list only.
- Account size fixed at USD 100,000.
- Risk tier fixed at Balanced.
- Target delta fixed at 0.30.
- DTE fixed at 30 days.
- Transaction-cost assumption uses the default estimate.
- Results are for education and preview purposes.

## Preview Results Table

```csv
{table_text}
```

## Equity Curve Note

The public preview includes an illustrative Total Equity Over Time chart.

The equity curve is the correct visual anchor for covered-call analysis because it combines stock value, option value, realized profit or loss, and cash.

Premium collected is not the same as profit. Watch total equity, not just income.

## Free vs Paid Interpretation

The free version is intended to teach the basic concept with fixed assumptions.

The paid version should allow users to configure:

- Custom account size.
- Conservative, Balanced, or Aggressive risk tiers.
- Custom stock or ETF ticker.
- Target delta.
- DTE.
- Strike-selection method.
- Rolling assumptions.
- Optionability and liquidity checks.
- Exportable reports.
- Replay simulator with a moving total-equity plot.

## Disclaimers

This report is for educational and analytical use only.

It is not financial advice, investment advice, tax advice, legal advice, or a trade recommendation.

Options involve risk and are not suitable for all investors.

Simulated results are hypothetical and may not reflect actual trading outcomes.

Tradable means the ticker passes the selected account-size and position-size screen. It does not mean the ticker is recommended.

Regime detection is probabilistic guidance, not an oracle.

Premium collected is not the same as profit.
"""

    return report


def display_download_preview_report(
    ticker: str,
    source_label: str,
    used_placeholder_results: bool,
    results_df: pd.DataFrame,
) -> None:
    """
    Display a download button for the public preview report.
    """
    st.markdown("### Download Preview Report")

    report_markdown = build_preview_report_markdown(
        ticker=ticker,
        source_label=source_label,
        used_placeholder_results=used_placeholder_results,
        results_df=results_df,
    )

    file_name = f"covered_call_preview_{ticker.lower()}.md"

    st.download_button(
        label="Download Markdown report",
        data=report_markdown,
        file_name=file_name,
        mime="text/markdown",
    )

    st.caption(
        "The report is a simple Markdown file. It is intended for education "
        "and preview use only."
    )


def get_report_summary_lines(limit: int = 24) -> list[str]:
    """
    Return a compact set of non-empty lines from the dashboard report.
    """
    report_text = load_text_file(STRATEGY_DASHBOARD_REPORT_PATH)

    if not report_text:
        return []

    lines = [
        line.strip()
        for line in report_text.splitlines()
        if line.strip()
    ]

    return lines[:limit]


# =============================================================================
# Status helpers
# =============================================================================

def display_document_status() -> None:
    """
    Display a compact status list of available planning documents.
    """
    docs = [
        ("Website plan", WEBSITE_PLAN_PATH),
        ("Landing page copy", LANDING_PAGE_COPY_PATH),
        ("Free vs paid features", FREE_VS_PAID_PATH),
        ("Public disclaimer", PUBLIC_DISCLAIMER_PATH),
        ("Development roadmap", DEVELOPMENT_ROADMAP_PATH),
        ("Simulator workflow", SIMULATOR_WORKFLOW_PATH),
    ]

    rows = []

    for label, path in docs:
        rows.append(
            {
                "Document": label,
                "Status": "Found" if path.exists() else "Missing",
                "Path": str(path.relative_to(PROJECT_ROOT)),
            }
        )

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def display_output_status() -> None:
    """
    Display a compact status list of simulator output files.
    """
    files = [
        ("Strategy dashboard report", STRATEGY_DASHBOARD_REPORT_PATH),
        ("Current price snapshot", CURRENT_PRICE_SNAPSHOT_PATH),
        ("Current regime snapshot", CURRENT_REGIME_SNAPSHOT_PATH),
    ]

    rows = []

    for label, path in files:
        rows.append(
            {
                "Output": label,
                "Status": "Found" if path.exists() else "Missing",
                "Path": str(path.relative_to(PROJECT_ROOT)),
            }
        )

    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


# =============================================================================
# Page components
# =============================================================================

def display_public_disclaimer_short() -> None:
    """
    Display the short public disclaimer used throughout the site.
    """
    st.caption(
        "Educational use only. Not financial advice. Not a trade "
        "recommendation. Options involve risk. Simulated results are "
        "hypothetical."
    )


def page_home() -> None:
    """
    Home page for the public prototype.
    """
    st.markdown(
        """
        <div class="public-hero">
            <h1>Test covered-call decisions before risking capital.</h1>
            <p>
                Compare covered-call management rules, account-size constraints,
                option assumptions, market-regime scenarios, and active covered-call
                decisions using a practical simulator built for income-focused investors.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "The Covered Call Simulator is not a trade signal service. It is an "
        "educational simulator, decision-practice environment, and covered-call "
        "training tool."
    )

    st.markdown("### Main product idea")

    hero_col1, hero_col2 = st.columns(2)

    with hero_col1:
        with st.container(border=True):
            st.subheader("Compare covered-call rules")
            st.write(
                "Use simulation output to compare management rules such as "
                "holding to expiration, closing at a profit target, waiting "
                "before re-entry, or adapting behavior to market-regime "
                "conditions."
            )

    with hero_col2:
        with st.container(border=True):
            st.subheader("Practice active CC decisions")
            st.write(
                "Use active covered-call simulation to practice selling, "
                "closing, rolling, waiting, and reviewing decisions while "
                "watching total equity change over time."
            )

    st.markdown("### Active covered-call simulation")

    with st.container(border=True):
        st.write(
            "The most distinctive future feature is active participation. "
            "Instead of only reading a backtest table, the user should be able "
            "to step through a market path, inspect candidate calls, choose a "
            "strike and expiration, place a simulated covered call, and manage "
            "the position as price changes."
        )

        st.success(
            "The key feedback loop is total equity, not premium collected. "
            "The simulator should show whether the user's decisions improved "
            "wealth relative to buy-and-hold and rule-based benchmarks."
        )

    workflow_col1, workflow_col2, workflow_col3 = st.columns(3)

    with workflow_col1:
        with st.container(border=True):
            st.subheader("1. Select")
            st.write(
                "Choose ticker, account size, risk tier, target delta, DTE, "
                "and strike-selection method."
            )

    with workflow_col2:
        with st.container(border=True):
            st.subheader("2. Place")
            st.write(
                "Review candidate calls, compare premium versus upside room, "
                "then place a simulated covered call."
            )

    with workflow_col3:
        with st.container(border=True):
            st.subheader("3. Manage")
            st.write(
                "Hold, close, roll, wait, or accept assignment in the "
                "simulation, then review total-equity results."
            )

    st.markdown("### Free preview versus paid simulator")

    tier_col1, tier_col2 = st.columns(2)

    with tier_col1:
        with st.container(border=True):
            st.subheader("Free preview")
            st.markdown(
                """
                - Fixed assumptions.
                - Preset ticker examples.
                - Basic rule comparison.
                - Account-size explanation.
                - Educational interpretation.
                """
            )

    with tier_col2:
        with st.container(border=True):
            st.subheader("Individual / Pro and Future Professional")
            st.markdown(
                """
                - Custom ticker and account assumptions.
                - Historical active replay.
                - Simulated CC placement and management.
                - Total-equity benchmark comparison.
                - Future real-time active simulation.
                """
            )

    st.markdown("### Why this is a training tool")

    training_col1, training_col2, training_col3 = st.columns(3)

    with training_col1:
        with st.container(border=True):
            st.subheader("Practice without capital at risk")
            st.write(
                "Users can practice covered-call decisions before risking real "
                "money. The simulator can show what happens after selling, "
                "closing, rolling, waiting, or accepting assignment."
            )

    with training_col2:
        with st.container(border=True):
            st.subheader("Learn from feedback")
            st.write(
                "Each decision should update total equity, option value, cash, "
                "missed upside, and benchmark comparisons so users learn from "
                "the full position, not just the premium received."
            )

    with training_col3:
        with st.container(border=True):
            st.subheader("Build process discipline")
            st.write(
                "Repeated practice can help users develop rules for entry, "
                "strike selection, profit taking, rolling, and re-entry."
            )

    st.markdown("### Why this matters")

    reason_df = pd.DataFrame(
        [
            {
                "Problem": "Premium feels like profit",
                "Simulator response": "Track total equity, option liability, cash, and benchmark comparison.",
            },
            {
                "Problem": "Rules behave differently by market path",
                "Simulator response": "Compare rules across bullish, bearish, sideways, high-vol, and low-vol conditions.",
            },
            {
                "Problem": "Covered calls are path-dependent",
                "Simulator response": "Let users practice decisions as the market unfolds rather than only seeing final results.",
            },
            {
                "Problem": "Account size limits practical tickers",
                "Simulator response": "Estimate whether one covered-call contract fits the selected account and position-size cap.",
            },
        ]
    )

    st.dataframe(
        reason_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Where to look next")

    next_col1, next_col2, next_col3 = st.columns(3)

    with next_col1:
        with st.container(border=True):
            st.subheader("Free Simulator Preview")
            st.write(
                "Shows the basic simulator output and current tradability "
                "logic using existing generated files."
            )

    with next_col2:
        with st.container(border=True):
            st.subheader("Active CC Simulation Preview")
            st.write(
                "Shows the interactive concept: moving market demo, option "
                "selection, pre-trade impact, post-trade state, and scorecard."
            )

    with next_col3:
        with st.container(border=True):
            st.subheader("Pricing")
            st.write(
                "Shows how Free, Individual / Pro, and Future Professional "
                "features are separated."
            )

    display_public_disclaimer_short()


def page_how_it_works() -> None:
    """
    How It Works page.
    """
    st.header("How It Works")

    st.write(
        "The Covered Call Simulator is designed to help users move from "
        "simple rule comparison to active decision practice. The finished "
        "product should let users configure assumptions, inspect possible "
        "covered calls, place simulated trades, manage the open position, and "
        "review the result through total equity and benchmark comparison."
    )

    st.info(
        "The simulator is a training and analysis environment. It should help "
        "users understand tradeoffs, not issue trade commands."
    )

    st.markdown("### Workflow overview")

    workflow_df = pd.DataFrame(
        [
            {
                "Step": "1. Choose mode",
                "User action": "Select Free Preview, Paid Simulator, Training Mode, Historical Replay, or future Real-Time Simulation.",
                "Simulator output": "Loads the appropriate level of assumptions, controls, and data requirements.",
            },
            {
                "Step": "2. Configure assumptions",
                "User action": "Choose ticker, account size, risk tier, target delta, DTE, and strike-selection method.",
                "Simulator output": "Checks account-size feasibility and defines the covered-call setup.",
            },
            {
                "Step": "3. Inspect candidate calls",
                "User action": "Compare strikes, expirations, delta, bid/ask, premium, and tradeoff notes.",
                "Simulator output": "Shows premium, upside cap, downside buffer, and possible assignment outcome.",
            },
            {
                "Step": "4. Place simulated CC",
                "User action": "Sell a selected covered call in the simulation.",
                "Simulator output": "Adds cash premium, opens a short-call liability, and updates the account state.",
            },
            {
                "Step": "5. Manage the position",
                "User action": "Hold, close, roll, wait, or accept assignment in the simulation.",
                "Simulator output": "Updates option value, cash, total equity, moneyness, and decision log.",
            },
            {
                "Step": "6. Review results",
                "User action": "Compare ending equity with buy-and-hold and mechanical rule benchmarks.",
                "Simulator output": "Shows scorecard, decision-quality notes, missed upside, and downloadable report.",
            },
        ]
    )

    st.dataframe(
        workflow_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Three product layers")

    layer_col1, layer_col2, layer_col3 = st.columns(3)

    with layer_col1:
        with st.container(border=True):
            st.subheader("Free preview")
            st.write(
                "A simplified educational version with fixed assumptions and "
                "limited rule comparison."
            )
            st.markdown(
                """
                - Preset tickers.
                - Basic account-size screen.
                - Basic rule comparison.
                - Educational interpretation.
                """
            )

    with layer_col2:
        with st.container(border=True):
            st.subheader("Individual / Pro")
            st.write(
                "A configurable paid simulator with historical active replay "
                "and training reports."
            )
            st.markdown(
                """
                - Custom ticker and account size.
                - Delta and DTE controls.
                - Simulated CC placement.
                - Historical active replay.
                - Training scorecard.
                - Downloadable report.
                """
            )

    with layer_col3:
        with st.container(border=True):
            st.subheader("Future Professional")
            st.write(
                "A future advanced tier for real-time or near-real-time "
                "interactive simulation."
            )
            st.markdown(
                """
                - Intraday market updates.
                - Option-chain updates.
                - Advanced liquidity checks.
                - Saved sessions.
                - Client or classroom demos.
                - Client-ready reports.
                """
            )

    st.markdown("### What the user learns")

    learning_col1, learning_col2 = st.columns(2)

    with learning_col1:
        with st.container(border=True):
            st.subheader("Tradeoff awareness")
            st.write(
                "The user sees that higher premium usually comes with less "
                "upside room, more assignment pressure, or a longer obligation."
            )

            st.write(
                "The simulator should make the premium-versus-upside tradeoff "
                "visible before the user places the simulated trade."
            )

    with learning_col2:
        with st.container(border=True):
            st.subheader("Total-equity discipline")
            st.write(
                "The simulator should constantly show total equity, because "
                "premium collected is not the same as profit."
            )

            st.write(
                "The user learns whether decisions improved total wealth "
                "relative to buy-and-hold and rule-based benchmarks."
            )

    st.markdown("### Active simulation feedback loop")

    feedback_df = pd.DataFrame(
        [
            {
                "User decision": "Sell a call",
                "Immediate effect": "Cash increases and short-call liability opens.",
                "Feedback shown": "Premium, upside cap, downside buffer, total equity.",
            },
            {
                "User decision": "Hold",
                "Immediate effect": "Position remains open while stock and option value change.",
                "Feedback shown": "Moneyness, option mark, unrealized P/L, assignment pressure.",
            },
            {
                "User decision": "Close",
                "Immediate effect": "Cash decreases by buyback cost and option risk is removed.",
                "Feedback shown": "Realized option P/L, updated cash, restored flexibility.",
            },
            {
                "User decision": "Roll",
                "Immediate effect": "Old call is closed and new call is opened.",
                "Feedback shown": "Net credit/debit, new strike, new cap, extended obligation.",
            },
            {
                "User decision": "Wait",
                "Immediate effect": "No trade is placed.",
                "Feedback shown": "Opportunity cost, changed premium, changed strike availability.",
            },
            {
                "User decision": "Accept assignment",
                "Immediate effect": "Shares are called away in the simulation.",
                "Feedback shown": "Final stock result, option result, cash, total equity.",
            },
        ]
    )

    st.dataframe(
        feedback_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Why this is different from a static backtest")

    difference_col1, difference_col2 = st.columns(2)

    with difference_col1:
        with st.container(border=True):
            st.subheader("Static backtest")
            st.markdown(
                """
                - User sees final results.
                - Rule decisions are already made.
                - Little sense of decision pressure.
                - Easy to overlook path dependence.
                """
            )

    with difference_col2:
        with st.container(border=True):
            st.subheader("Active training simulator")
            st.markdown(
                """
                - User makes decisions as the path unfolds.
                - Consequences appear immediately.
                - Total equity updates after each action.
                - Repeated practice builds process discipline.
                """
            )

    st.markdown("### Final output")

    with st.container(border=True):
        st.write(
            "A completed simulation should produce a session review: ending "
            "equity, benchmark comparison, premium collected, missed upside, "
            "roll impact, decision-quality notes, and a downloadable report."
        )

        st.success(
            "The end product is not only a simulator. It is a covered-call "
            "training system."
        )

    display_public_disclaimer_short()


def page_faq() -> None:
    """
    Frequently asked questions page.
    """
    st.header("Frequently Asked Questions")

    st.write(
        "This page answers the questions a first-time visitor is likely to ask "
        "after seeing the simulator, active covered-call training concept, "
        "pricing tiers, and report preview."
    )

    st.markdown("### Product basics")

    with st.expander("Is this a trade signal service?", expanded=True):
        st.write(
            "No. The Covered Call Simulator is intended to be an educational, "
            "analytical, and training-oriented simulation tool. It should help "
            "users compare rules, understand tradeoffs, and practice decisions. "
            "It should not tell users what to trade."
        )

    with st.expander("Does the simulator place real trades?"):
        st.write(
            "No. The public prototype is paper simulation only. Buttons such "
            "as Sell covered call, Close, Roll, or Wait are simulation controls. "
            "They do not submit orders to a broker."
        )

    with st.expander("Why call it a training tool?"):
        st.write(
            "Covered-call management is path-dependent. Users need practice "
            "choosing strikes, deciding when to close, deciding whether to roll, "
            "and judging results by total equity. Training Mode lets users "
            "practice those decisions without capital at risk."
        )

    st.markdown("### Active simulation")

    with st.expander("What does active covered-call simulation mean?", expanded=True):
        st.write(
            "It means the user actively participates in the simulated position. "
            "The user can inspect candidate calls, choose a strike and "
            "expiration, place a simulated covered call, and then decide whether "
            "to hold, close, roll, wait, or accept assignment in the simulation."
        )

    with st.expander("What is the difference between historical replay and real-time simulation?"):
        st.write(
            "Historical replay uses past market paths while hiding future "
            "information from the user. It belongs naturally in the Individual / "
            "Pro tier. Real-time or near-real-time active simulation would use "
            "intraday price and option-chain updates. That is more complex and "
            "belongs in the Future Professional tier."
        )

    with st.expander("Why is there a moving stock-price demo?"):
        st.write(
            "The moving demo quickly illustrates the core idea: the stock moves, "
            "the short call moves closer to or farther from being ITM, and total "
            "equity changes. It is a demonstration, not a forecast."
        )

    with st.expander("What does the dashed ITM line mean?"):
        st.write(
            "The dashed line is a hypothetical threshold showing where the "
            "illustrative short call would be in or near the money. It helps "
            "users see when covered-call management pressure increases."
        )

    st.markdown("### Results and reports")

    with st.expander("Why emphasize total equity instead of premium collected?", expanded=True):
        st.write(
            "Because premium collected is not the same as profit. A covered-call "
            "position can collect premium while still underperforming buy-and-hold "
            "because of missed upside, stock losses, option buyback costs, or "
            "rolling decisions. Total equity gives the fuller picture."
        )

    with st.expander("What should a session report include?"):
        st.write(
            "A useful report should include setup assumptions, trade log, total "
            "equity curve, premium collected, missed upside, buy-and-hold "
            "comparison, rule benchmark comparison, roll impact, and "
            "decision-quality notes."
        )

    with st.expander("Are simulated results expected to match real trading?"):
        st.write(
            "No. Simulated results are hypothetical. Real trading includes "
            "bid/ask spreads, slippage, commissions, liquidity constraints, "
            "tax effects, assignment behavior, emotional pressure, and changing "
            "volatility."
        )

    st.markdown("### Tickers, options, and account size")

    with st.expander("Why does account size matter?"):
        st.write(
            "A standard covered call requires 100 shares. A high-priced ticker "
            "may require too much capital relative to the user's account or "
            "position-size cap. The simulator should help users see which "
            "tickers are practical under their assumptions."
        )

    with st.expander("What does 'tradable' mean in this product?"):
        st.write(
            "Tradable means the ticker passes a practical account-size and "
            "position-size screen under the selected assumptions. It does not "
            "mean the ticker is recommended or expected to outperform."
        )

    with st.expander("Will custom tickers be available?"):
        st.write(
            "Custom stock or ETF tickers are planned for the paid simulator. "
            "A robust version should verify that the ticker exists, has listed "
            "options, has usable expirations near the selected DTE, and has "
            "adequate liquidity."
        )

    st.markdown("### Market regimes and data")

    with st.expander("Are market-regime labels predictions?"):
        st.write(
            "No. Regime labels are scenario inputs and probabilistic guidance. "
            "They are used to compare how covered-call rules behave under "
            "different conditions. They should not be treated as trading signals."
        )

    with st.expander("Does high volatility mean bearish?"):
        st.write(
            "Not inherently. High volatility often appears during downside "
            "stress, but volatility itself does not determine direction. Low "
            "volatility often appears during calm uptrends or sideways markets, "
            "but it is not inherently bullish."
        )

    with st.expander("Will data be live?"):
        st.write(
            "The current public prototype reads existing generated output files. "
            "Future versions may use current or near-real-time data, but the site "
            "should always clearly show whether data is historical, delayed, "
            "near-real-time, or illustrative."
        )

    st.markdown("### Pricing tiers")

    tier_faq_df = pd.DataFrame(
        [
            {
                "Tier": "Free",
                "Likely role": "Educational preview with fixed assumptions and limited rule comparison.",
            },
            {
                "Tier": "Individual / Pro",
                "Likely role": "Configurable simulator with custom assumptions, historical active replay, training mode, and reports.",
            },
            {
                "Tier": "Future Professional",
                "Likely role": "Advanced real-time or near-real-time active simulation, saved sessions, client-ready reports, and richer analytics.",
            },
        ]
    )

    st.dataframe(
        tier_faq_df,
        width="stretch",
        hide_index=True,
    )

    display_public_disclaimer_short()


def page_free_simulator_preview() -> None:
    """
    Free Simulator Preview page.
    """
    st.header("Free Simulator Preview")

    st.info(
        "This page now tries to read existing simulator output files. If no "
        "suitable rule-comparison output is found, it falls back to an "
        "illustrative placeholder table."
    )

    st.subheader("Fixed assumptions")

    input_col1, input_col2, input_col3 = st.columns(3)

    with input_col1:
        ticker = st.selectbox(
            "Ticker",
            options=["SPY", "QQQ", "IWM"],
            index=0,
        )

    with input_col2:
        st.text_input(
            "Account size",
            value="$100,000",
            disabled=True,
        )

    with input_col3:
        st.text_input(
            "Risk tier",
            value="Balanced",
            disabled=True,
        )

    assumptions_col1, assumptions_col2, assumptions_col3 = st.columns(3)

    with assumptions_col1:
        st.text_input(
            "Target delta",
            value="0.30",
            disabled=True,
        )

    with assumptions_col2:
        st.text_input(
            "DTE",
            value="30 days",
            disabled=True,
        )

    with assumptions_col3:
        st.text_input(
            "Transaction cost",
            value="Default estimate",
            disabled=True,
        )

    st.caption(
        "The free version uses fixed assumptions. Paid functionality should "
        "allow custom tickers, account size, delta, DTE, strike method, and "
        "rolling rules."
    )

    st.markdown("---")

    if st.button("Run preview comparison", type="primary"):
        st.session_state["show_free_preview_results"] = True

    if st.session_state.get("show_free_preview_results", False):
        st.subheader(f"Preview results for {ticker}")

        rule_df, source_label = load_best_rule_comparison(ticker)

        display_preview_summary(ticker, source_label)

        used_placeholder_results = False

        if not rule_df.empty:
            st.success(
                f"Loaded available simulator output: {source_label}"
            )
            results_for_report_df = display_rule_comparison_results(rule_df)
        else:
            used_placeholder_results = True
            st.warning(
                "No suitable rule-comparison CSV was found in "
                "outputs/tables/comparison. Showing illustrative placeholder "
                "results instead."
            )

            placeholder_df = build_free_preview_placeholder_results()
            results_for_report_df = placeholder_df.copy()

            st.dataframe(
                placeholder_df,
                width="stretch",
                hide_index=True,
            )

        display_current_snapshot_results(ticker)

        display_total_equity_preview()

        display_account_size_tradability_preview(ticker)

        display_free_vs_paid_interpretation(ticker)

        display_download_preview_report(
            ticker=ticker,
            source_label=source_label,
            used_placeholder_results=used_placeholder_results,
            results_df=results_for_report_df,
        )

        st.markdown("### Plain-English interpretation")

        with st.container(border=True):
            st.write(
                "The preview is intended to demonstrate how a public user "
                "would compare covered-call management rules under fixed "
                "assumptions. In the paid version, the user should be able to "
                "change ticker, account size, target delta, DTE, strike "
                "selection, rolling behavior, and transaction-cost assumptions."
            )

            st.warning(
                "This preview is not a trade recommendation. Results depend "
                "on assumptions, data quality, and market behavior."
            )

        with st.expander("Show strategy dashboard report summary", expanded=False):
            report_lines = get_report_summary_lines(limit=30)

            if report_lines:
                st.code("\n".join(report_lines))
            else:
                st.warning(
                    "strategy_dashboard_report.txt was not found or could not "
                    "be read."
                )

        with st.expander("Show output file status", expanded=False):
            display_output_status()

        st.markdown("### Upgrade direction")

        paid_col1, paid_col2 = st.columns(2)

        with paid_col1:
            with st.container(border=True):
                st.subheader("Paid configurable simulator")
                st.write(
                    "Use your own ticker, account size, risk tier, delta, "
                    "DTE, strike-selection method, and rolling assumptions."
                )

        with paid_col2:
            with st.container(border=True):
                st.subheader("Replay simulator")
                st.write(
                    "Practice covered-call decisions on historical price "
                    "paths without seeing the future, with a moving total "
                    "equity curve."
                )

    display_public_disclaimer_short()


def page_strategies_compared() -> None:
    """
    Public-facing page explaining the covered-call management rules.
    """
    st.header("Strategies Compared")

    st.write(
        "Covered-call results depend not only on the ticker, but also on how "
        "the short call is managed. This page explains the main rules used in "
        "the simulator."
    )

    st.info(
        "These rules are comparison frameworks, not recommendations. The best "
        "historical rule can change by ticker, regime, option premium, and "
        "price path."
    )

    st.markdown("### Rule overview")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Hold to expiration")
            st.write(
                "The investor sells a covered call and generally holds it "
                "until expiration."
            )
            st.markdown(
                """
                **Advantages**

                - Simple.
                - Low maintenance.
                - Easy to understand.

                **Tradeoffs**

                - May leave money on the table.
                - May be slow to adapt.
                - Can create missed-upside or assignment issues.
                """
            )

    with col2:
        with st.container(border=True):
            st.subheader("Close at 50% profit")
            st.write(
                "The investor buys back the short call after capturing 50% "
                "of the original credit."
            )
            st.markdown(
                """
                **Advantages**

                - Captures time decay earlier.
                - Reduces exposure after much of the premium has been earned.
                - Can free the position for another trade.

                **Tradeoffs**

                - More active.
                - May increase transaction frequency.
                - May not outperform in every market regime.
                """
            )

    col3, col4 = st.columns(2)

    with col3:
        with st.container(border=True):
            st.subheader("Wait 10 days")
            st.write(
                "The investor waits before selling another covered call after "
                "a prior option cycle ends or is closed."
            )
            st.markdown(
                """
                **Advantages**

                - Can reduce overtrading.
                - May allow the underlying to recover or trend.
                - Helps avoid immediately selling calls after unfavorable moves.

                **Tradeoffs**

                - May miss premium collection opportunities.
                - Depends strongly on market environment.
                - Requires patience and discipline.
                """
            )

    with col4:
        with st.container(border=True):
            st.subheader("Adaptive regime rule")
            st.write(
                "The simulator maps completed-bar market conditions to a "
                "practical rule."
            )
            st.markdown(
                """
                **Advantages**

                - More flexible.
                - Can respond to broad market behavior.
                - Helps compare rule behavior across regimes.

                **Tradeoffs**

                - Regime detection is imperfect.
                - It should not be treated as a forecast.
                - It adds complexity.
                """
            )

    st.markdown("### Compact comparison")

    comparison_df = pd.DataFrame(
        [
            {
                "Rule": "Hold to expiration",
                "Activity level": "Low",
                "Main strength": "Simple and disciplined",
                "Main risk": "Can cap upside or be slow to adapt",
                "Best use case": "Users who prefer low-maintenance rules",
            },
            {
                "Rule": "Close at 50%",
                "Activity level": "Medium",
                "Main strength": "Captures time decay earlier",
                "Main risk": "More transactions and possible re-entry risk",
                "Best use case": "Users who actively manage premium capture",
            },
            {
                "Rule": "Wait 10 days",
                "Activity level": "Low to medium",
                "Main strength": "Reduces overtrading",
                "Main risk": "May miss premium opportunities",
                "Best use case": "Users who want a cooling-off rule",
            },
            {
                "Rule": "Adaptive regime rule",
                "Activity level": "Medium",
                "Main strength": "Scenario-aware comparison",
                "Main risk": "Regime labels are uncertain",
                "Best use case": "Users comparing rule behavior by regime",
            },
        ]
    )

    st.dataframe(
        comparison_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Important interpretation")

    with st.container(border=True):
        st.write(
            "The simulator should not ask which rule generates the most "
            "premium. It should ask which rule produces the best total-equity "
            "behavior after accounting for stock movement, option value, cash, "
            "missed upside, assignment, and drawdown."
        )

        st.warning(
            "Premium collected is not the same as profit. A rule can collect "
            "premium and still underperform if the underlying rises strongly "
            "or falls sharply."
        )

    st.markdown("### How this connects to the simulator")

    st.write(
        "The Free Simulator Preview compares a limited set of rules under "
        "fixed assumptions. The paid version should allow users to test rules "
        "with their own ticker, account size, target delta, DTE, strike "
        "selection, rolling assumptions, and transaction-cost assumptions."
    )

    display_public_disclaimer_short()



def page_market_regimes() -> None:
    """
    Public-facing page explaining market regimes.
    """
    st.header("Market Regimes")

    st.write(
        "The simulator uses market-regime labels to help compare how "
        "covered-call rules may behave under different market conditions."
    )

    st.warning(
        "Regime detection is probabilistic guidance, not an oracle. Regime "
        "labels are scenario inputs, not predictions."
    )

    st.markdown("### Two-axis regime framework")

    st.write(
        "Market direction and market volatility are different dimensions. "
        "Bullish, bearish, and sideways describe direction. High volatility "
        "and low volatility describe the size or instability of price "
        "movement. They are not the same thing."
    )

    axis_col1, axis_col2 = st.columns(2)

    with axis_col1:
        with st.container(border=True):
            st.subheader("Direction axis")
            st.write(
                "Direction describes whether the underlying has been rising, "
                "falling, or moving mostly sideways."
            )
            st.markdown(
                """
                - Bullish
                - Bearish
                - Sideways
                """
            )

    with axis_col2:
        with st.container(border=True):
            st.subheader("Volatility axis")
            st.write(
                "Volatility describes how large or unstable the price movement "
                "has been. It is not inherently bullish or bearish."
            )
            st.markdown(
                """
                - High volatility
                - Low volatility
                """
            )

    st.markdown("### Combined regimes")

    combined_df = pd.DataFrame(
        [
            {
                "Combined Regime": "Bullish + low volatility",
                "Covered-call issue": "Missed upside with relatively small premium",
                "Interpretation": "The stock may drift upward through the strike while premium is modest.",
            },
            {
                "Combined Regime": "Bullish + high volatility",
                "Covered-call issue": "Larger premium but faster strike pressure",
                "Interpretation": "Premium is larger, but the call can move ITM quickly.",
            },
            {
                "Combined Regime": "Bearish + high volatility",
                "Covered-call issue": "Underlying loss may overwhelm premium",
                "Interpretation": "Premium helps, but stock losses can dominate total equity.",
            },
            {
                "Combined Regime": "Bearish + low volatility",
                "Covered-call issue": "Slow decline with limited premium offset",
                "Interpretation": "Losses may be smaller per step, but premium may also be smaller.",
            },
            {
                "Combined Regime": "Sideways + low/moderate volatility",
                "Covered-call issue": "Overtrading or low premium",
                "Interpretation": "Often a cleaner covered-call environment if the range persists.",
            },
            {
                "Combined Regime": "Sideways + high volatility",
                "Covered-call issue": "Large swings inside a range",
                "Interpretation": "Premium can be attractive, but management can still be difficult.",
            },
        ]
    )

    st.dataframe(
        combined_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Direction categories")

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        with st.container(border=True):
            st.subheader("Bullish")
            st.write(
                "The underlying has been rising or showing positive trend "
                "behavior. Covered calls may collect premium but can also cap "
                "upside if the price continues higher."
            )

    with row1_col2:
        with st.container(border=True):
            st.subheader("Bearish")
            st.write(
                "The underlying has been falling or showing negative trend "
                "behavior. Covered-call premium may provide partial offset, "
                "but the stock position can still lose money."
            )

    with row1_col3:
        with st.container(border=True):
            st.subheader("Sideways")
            st.write(
                "The underlying is moving within a range. This may be a more "
                "favorable environment for time-decay strategies, but only if "
                "the range persists."
            )

    st.markdown("### Volatility categories")

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        with st.container(border=True):
            st.subheader("High volatility")
            st.write(
                "Option premiums may be larger, but price movement and "
                "assignment risk may also be larger. Higher premium does not "
                "automatically mean better risk-adjusted return."
            )
            st.caption(
                "High volatility is not inherently bearish, but it is often "
                "seen during downside stress because markets frequently fall "
                "faster than they rise."
            )

    with row2_col2:
        with st.container(border=True):
            st.subheader("Low volatility")
            st.write(
                "Option premiums may be smaller, and price movement may be "
                "more contained. The tradeoff is that less premium is "
                "collected for the same notional exposure."
            )
            st.caption(
                "Low volatility is not inherently bullish, but it often "
                "appears during steady uptrends or quiet sideways markets."
            )

    st.markdown("### Does volatility imply direction?")

    with st.container(border=True):
        st.write(
            "Volatility by itself does not tell us whether the market is "
            "bullish, bearish, or sideways. It tells us how large or unstable "
            "the price movement is."
        )

        st.write(
            "There can still be a practical association. High volatility is "
            "often associated with selloffs or market stress, because declines "
            "can be abrupt and investors may bid up option protection. Low "
            "volatility is often associated with calm uptrends or range-bound "
            "markets. These are tendencies, not rules."
        )

        st.write(
            "For covered calls, this distinction matters: direction determines "
            "stock P/L and missed upside, while volatility affects option "
            "premium, option buyback cost, and rolling difficulty."
        )

    volatility_trend_df = pd.DataFrame(
        [
            {
                "Volatility condition": "High volatility",
                "Inherent direction": "None",
                "Common association": "Often appears during downside stress or unstable markets",
                "Covered-call implication": "Higher premium, but more strike pressure and larger stock risk",
            },
            {
                "Volatility condition": "Low volatility",
                "Inherent direction": "None",
                "Common association": "Often appears during calm uptrends or sideways markets",
                "Covered-call implication": "Lower premium, but usually less violent option mark-to-market movement",
            },
        ]
    )

    st.dataframe(
        volatility_trend_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### How the simulator uses regimes")

    with st.container(border=True):
        st.write(
            "The simulator uses completed daily-bar information to classify "
            "recent market behavior. It then compares how different "
            "covered-call rules behaved across those regime categories."
        )

        st.write(
            "The purpose is not to forecast tomorrow. The purpose is to show "
            "that a rule that works well in one regime may not work as well "
            "in another."
        )

    st.markdown("### Why regimes matter for covered calls")

    regime_df = pd.DataFrame(
        [
            {
                "Dimension": "Direction",
                "Example": "Bullish",
                "Covered-call issue": "Missed upside",
                "Common lesson": "Premium may not compensate for capped gains.",
            },
            {
                "Dimension": "Direction",
                "Example": "Bearish",
                "Covered-call issue": "Underlying loss",
                "Common lesson": "Premium provides only partial downside offset.",
            },
            {
                "Dimension": "Direction",
                "Example": "Sideways",
                "Covered-call issue": "Overtrading",
                "Common lesson": "Theta collection may help if the range persists.",
            },
            {
                "Dimension": "Volatility",
                "Example": "High volatility",
                "Covered-call issue": "Large price movement",
                "Common lesson": "Higher premium comes with higher uncertainty.",
            },
            {
                "Dimension": "Volatility",
                "Example": "Low volatility",
                "Covered-call issue": "Low premium",
                "Common lesson": "Risk may not be adequately compensated.",
            },
        ]
    )

    st.dataframe(
        regime_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Current regime snapshot")

    ticker_options = get_available_public_tickers()

    selected_ticker = st.selectbox(
        "Ticker",
        options=ticker_options,
        index=0,
        key="market_regimes_ticker",
    )

    display_current_snapshot_results(selected_ticker)

    st.markdown("### Important limitation")

    with st.container(border=True):
        st.write(
            "A regime label is a summary of recent market behavior. It is not "
            "a promise that the next trading period will behave the same way."
        )

        st.write(
            "For the public product, this distinction is important: the "
            "simulator should help users compare scenarios, not tell users "
            "what the market will do next."
        )

    display_public_disclaimer_short()



def get_available_public_tickers() -> list[str]:
    """
    Return a public-facing ticker list from current_price_snapshot.csv when
    available, otherwise fall back to the default free ticker list.
    """
    default_tickers = ["SPY", "QQQ", "IWM"]

    price_df = load_csv(CURRENT_PRICE_SNAPSHOT_PATH)

    if price_df.empty:
        return default_tickers

    ticker_column = find_column(
        price_df,
        [
            "Ticker",
            "Symbol",
            "Underlying",
            "ETF",
        ],
    )

    if ticker_column is None:
        return default_tickers

    tickers = (
        price_df[ticker_column]
        .dropna()
        .astype(str)
        .str.upper()
        .str.strip()
        .unique()
        .tolist()
    )

    tickers = sorted([ticker for ticker in tickers if ticker])

    if not tickers:
        return default_tickers

    return tickers


def get_position_cap_for_risk_tier(
    risk_tier: str,
    ticker: str,
) -> float:
    """
    Return a simple public-facing per-position cap.

    Leveraged ETF examples use smaller caps because they are more volatile.
    """
    leveraged_tickers = {
        "TQQQ",
        "SQQQ",
        "SOXL",
        "SOXS",
        "UPRO",
        "SPXU",
        "LABU",
        "LABD",
    }

    is_leveraged = ticker.upper().strip() in leveraged_tickers

    if risk_tier == "Conservative":
        return 0.05 if is_leveraged else 0.08

    if risk_tier == "Aggressive":
        return 0.10 if is_leveraged else 0.15

    return 0.075 if is_leveraged else 0.10


def page_account_sizing() -> None:
    """
    Public-facing account sizing page.
    """
    st.header("Account Sizing")

    st.write(
        "Covered calls require 100 shares per option contract. That means "
        "account size matters. A ticker can be useful for analysis but still "
        "too large for a small account under a disciplined position-size rule."
    )

    st.info(
        "Tradable means the ticker passes the selected account-size and "
        "position-size screen. It is not a trade recommendation."
    )

    st.markdown("### Minimum equity calculator")

    ticker_options = get_available_public_tickers()

    input_col1, input_col2, input_col3 = st.columns(3)

    with input_col1:
        selected_ticker = st.selectbox(
            "Ticker",
            options=ticker_options,
            index=0,
            key="account_sizing_ticker",
        )

    with input_col2:
        account_size = st.number_input(
            "Account size",
            min_value=1000,
            max_value=10000000,
            value=100000,
            step=5000,
            format="%d",
            key="account_sizing_account_size",
        )

    with input_col3:
        risk_tier = st.selectbox(
            "Risk tier",
            options=["Conservative", "Balanced", "Aggressive"],
            index=1,
            key="account_sizing_risk_tier",
        )

    current_price = get_current_price_for_ticker(selected_ticker)
    position_cap = get_position_cap_for_risk_tier(
        risk_tier=risk_tier,
        ticker=selected_ticker,
    )

    minimum_equity = estimate_minimum_equity_for_one_contract(
        current_price=current_price,
        position_cap=position_cap,
    )

    passes_screen = (
        minimum_equity is not None
        and minimum_equity <= float(account_size)
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            "Current price",
            format_currency(current_price),
        )

    with metric_col2:
        st.metric(
            "Per-position cap",
            f"{position_cap * 100:.1f}%",
        )

    with metric_col3:
        st.metric(
            "Estimated min equity",
            format_currency(minimum_equity),
        )

    with metric_col4:
        if minimum_equity is None:
            st.metric("Screen result", "N/A")
        elif passes_screen:
            st.metric("Screen result", "Passes")
        else:
            st.metric("Screen result", "Too large")

    if minimum_equity is None:
        st.warning(
            "Current price was not available, so the minimum-equity estimate "
            "could not be calculated."
        )
    elif passes_screen:
        st.success(
            f"{selected_ticker} passes the selected account-size screen. "
            f"The estimated minimum equity is "
            f"{format_currency_text(minimum_equity)}, compared with the "
            f"selected account size of {format_currency_text(float(account_size))}."
        )
    else:
        st.warning(
            f"{selected_ticker} does not pass the selected account-size screen. "
            f"The estimated minimum equity is "
            f"{format_currency_text(minimum_equity)}, compared with the "
            f"selected account size of {format_currency_text(float(account_size))}."
        )

    st.markdown("### Formula")

    with st.container(border=True):
        st.markdown(
            """
            Estimated minimum equity:

            **100 shares × current price ÷ per-position cap**
            """
        )

        st.write(
            "For example, if a ticker trades at USD 700 and the selected "
            "per-position cap is 10%, then one covered-call contract requires "
            "approximately USD 700,000 of account equity under that sizing rule."
        )

    st.markdown("### Why this matters")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("High-priced ETFs")
            st.write(
                "High-priced ETFs such as SPY or QQQ may require much larger "
                "accounts than users expect because one option contract "
                "controls 100 shares."
            )

    with col2:
        with st.container(border=True):
            st.subheader("Leveraged ETFs")
            st.write(
                "Leveraged ETFs should generally use smaller position-size "
                "caps because their daily price movement can be much larger."
            )

    with st.expander("Show current price snapshot details", expanded=False):
        snapshot_df = build_current_snapshot_table(selected_ticker)

        if snapshot_df.empty:
            st.warning("No current snapshot details were available.")
        else:
            st.dataframe(
                snapshot_df,
                width="stretch",
                hide_index=True,
            )

    display_public_disclaimer_short()


def build_replay_preview_equity_curve() -> pd.DataFrame:
    """
    Build an illustrative replay-equity curve for the public replay preview.
    """
    rows = [
        {
            "Replay Step": "Start",
            "User Replay Equity": 100000,
            "Buy and Hold": 100000,
            "Rule Benchmark": 100000,
        },
        {
            "Replay Step": "Day 5",
            "User Replay Equity": 100600,
            "Buy and Hold": 101200,
            "Rule Benchmark": 100800,
        },
        {
            "Replay Step": "Day 10",
            "User Replay Equity": 101100,
            "Buy and Hold": 102400,
            "Rule Benchmark": 101300,
        },
        {
            "Replay Step": "Day 15",
            "User Replay Equity": 100300,
            "Buy and Hold": 100900,
            "Rule Benchmark": 100600,
        },
        {
            "Replay Step": "Day 20",
            "User Replay Equity": 102000,
            "Buy and Hold": 103600,
            "Rule Benchmark": 102100,
        },
        {
            "Replay Step": "Day 25",
            "User Replay Equity": 102700,
            "Buy and Hold": 105000,
            "Rule Benchmark": 102900,
        },
        {
            "Replay Step": "Day 30",
            "User Replay Equity": 103300,
            "Buy and Hold": 104200,
            "Rule Benchmark": 103100,
        },
    ]

    return pd.DataFrame(rows)


def build_replay_preview_event_log() -> pd.DataFrame:
    """
    Build an illustrative event log for replay mode.
    """
    rows = [
        {
            "Replay Date": "Day 1",
            "Action": "Start",
            "Stock Price": "$100.00",
            "Short Call": "None",
            "Cash Event": "$0",
            "Total Equity": "$100,000",
            "Note": "Starting account.",
        },
        {
            "Replay Date": "Day 5",
            "Action": "Sell covered call",
            "Stock Price": "$101.20",
            "Short Call": "105C, 30 DTE",
            "Cash Event": "+$180",
            "Total Equity": "$100,600",
            "Note": "Collected premium.",
        },
        {
            "Replay Date": "Day 12",
            "Action": "Wait",
            "Stock Price": "$103.40",
            "Short Call": "105C, 23 DTE",
            "Cash Event": "$0",
            "Total Equity": "$101,300",
            "Note": "Call remains OTM.",
        },
        {
            "Replay Date": "Day 20",
            "Action": "Roll up and out",
            "Stock Price": "$105.60",
            "Short Call": "108C, 35 DTE",
            "Cash Event": "+$40 net credit",
            "Total Equity": "$102,000",
            "Note": "Prior call moved near ITM.",
        },
        {
            "Replay Date": "Day 30",
            "Action": "End preview",
            "Stock Price": "$104.20",
            "Short Call": "108C, 25 DTE",
            "Cash Event": "$0",
            "Total Equity": "$103,300",
            "Note": "Replay preview complete.",
        },
    ]

    return pd.DataFrame(rows)


def page_replay_simulator_preview() -> None:
    """
    Public-facing preview page for the future replay simulator.
    """
    st.header("Replay Simulator Preview")

    st.write(
        "The Replay Simulator is planned as a paid workflow tool. It would let "
        "users practice covered-call decisions on historical price paths "
        "without seeing the future."
    )

    st.warning(
        "This page is a public prototype. It does not yet run a real replay "
        "engine. The chart and event log below are illustrative placeholders."
    )

    st.markdown("### Replay concept")

    concept_col1, concept_col2 = st.columns(2)

    with concept_col1:
        with st.container(border=True):
            st.subheader("What the user does")
            st.markdown(
                """
                - Select a ticker.
                - Select a historical start period.
                - Watch price move forward one step at a time.
                - Decide when to sell a covered call.
                - Choose delta, DTE, strike, and expiration.
                - Decide whether to hold, close, roll, or wait.
                """
            )

    with concept_col2:
        with st.container(border=True):
            st.subheader("What the simulator tracks")
            st.markdown(
                """
                - Stock value.
                - Cash.
                - Premium collected.
                - Open short-call value.
                - Realized option P/L.
                - Missed upside.
                - Total account equity.
                """
            )

    st.markdown("### Replay controls preview")

    control_col1, control_col2, control_col3 = st.columns(3)

    with control_col1:
        selected_ticker = st.selectbox(
            "Ticker",
            options=get_available_public_tickers(),
            index=0,
            key="replay_preview_ticker",
        )

    with control_col2:
        st.selectbox(
            "Replay speed",
            options=["Step one day", "Step one week", "Auto-play"],
            index=0,
            key="replay_preview_speed",
            disabled=True,
        )

    with control_col3:
        st.selectbox(
            "Default action set",
            options=["Sell / close / roll / wait", "Sell / wait only"],
            index=0,
            key="replay_preview_action_set",
            disabled=True,
        )

    st.caption(
        "Controls are shown for layout only. The replay engine will be added "
        "later."
    )

    st.markdown("### Total Equity Over Time")

    equity_df = build_replay_preview_equity_curve()
    st.line_chart(
        equity_df.set_index("Replay Step"),
        height=360,
    )

    with st.container(border=True):
        st.write(
            "The total-equity curve should be the central visual in replay "
            "mode. It shows whether the user's decisions improved total "
            "wealth compared with buy-and-hold and rule-based benchmarks."
        )

        st.warning(
            "Premium collected is not the same as profit. A replay user may "
            "collect premium while still underperforming because of missed "
            "upside, stock losses, or expensive rolls."
        )

    st.markdown("### Replay event log")

    event_log_df = build_replay_preview_event_log()

    st.dataframe(
        event_log_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Why replay matters")

    why_col1, why_col2 = st.columns(2)

    with why_col1:
        with st.container(border=True):
            st.subheader("Path dependence")
            st.write(
                "Covered-call management is path-dependent. A rule that looks "
                "simple in a final table can feel difficult when the user must "
                "make decisions without knowing the future."
            )

    with why_col2:
        with st.container(border=True):
            st.subheader("Decision practice")
            st.write(
                "Replay mode helps users see the consequences of holding, "
                "closing, rolling, or waiting as the trade evolves."
            )

    st.markdown("### Planned paid functionality")

    st.markdown(
        """
        The paid replay simulator should eventually include:

        - Real historical price paths.
        - Hidden future data.
        - Option selection by delta and DTE.
        - Realistic rolling choices.
        - Assignment handling.
        - Benchmark overlays.
        - Downloadable decision log.
        - Total-equity performance summary.
        """
    )

    display_public_disclaimer_short()


def page_paid_simulator_preview() -> None:
    """
    Public-facing preview of the future paid configurable simulator.
    """
    st.header("Paid Simulator Preview")

    st.write(
        "The paid simulator should let users move beyond fixed assumptions. "
        "Instead of using only preset tickers, fixed account size, fixed delta, "
        "and fixed DTE, users should be able to model covered-call decisions "
        "using assumptions closer to their own trading process."
    )

    st.warning(
        "This page is a prototype layout. It does not yet run the full paid "
        "simulator. The controls show the intended workflow."
    )

    st.markdown("### Paid setup workflow")

    setup_col1, setup_col2, setup_col3 = st.columns(3)

    with setup_col1:
        paid_ticker = st.text_input(
            "Custom stock or ETF ticker",
            value="SPY",
            key="paid_preview_ticker",
        ).upper().strip()

    with setup_col2:
        paid_account_size = st.number_input(
            "Account size",
            min_value=10000,
            max_value=10000000,
            value=250000,
            step=10000,
            format="%d",
            key="paid_preview_account_size",
        )

    with setup_col3:
        paid_risk_tier = st.selectbox(
            "Risk tier",
            options=["Conservative", "Balanced", "Aggressive"],
            index=1,
            key="paid_preview_risk_tier",
        )

    option_col1, option_col2, option_col3 = st.columns(3)

    with option_col1:
        target_delta = st.selectbox(
            "Target short-call delta",
            options=["0.15", "0.20", "0.25", "0.30", "0.35", "0.40"],
            index=3,
            key="paid_preview_delta",
        )

    with option_col2:
        target_dte = st.selectbox(
            "Target DTE",
            options=["7", "14", "21", "30", "45", "60"],
            index=3,
            key="paid_preview_dte",
        )

    with option_col3:
        strike_method = st.selectbox(
            "Strike-selection method",
            options=[
                "Closest to target delta",
                "Fixed percent OTM",
                "Fixed dollar OTM",
                "Highest annualized premium subject to delta limit",
                "Liquidity-filtered best match",
            ],
            index=0,
            key="paid_preview_strike_method",
        )

    rule_col1, rule_col2, rule_col3 = st.columns(3)

    with rule_col1:
        profit_rule = st.selectbox(
            "Profit-taking rule",
            options=[
                "Hold to expiration",
                "Close at 25% profit",
                "Close at 50% profit",
                "Close at 75% profit",
                "Close by DTE threshold",
            ],
            index=2,
            key="paid_preview_profit_rule",
        )

    with rule_col2:
        rolling_rule = st.selectbox(
            "Rolling rule",
            options=[
                "Never roll",
                "Roll when ITM",
                "Roll when delta exceeds threshold",
                "Roll out and up",
                "Roll only for a net credit",
            ],
            index=4,
            key="paid_preview_rolling_rule",
        )

    with rule_col3:
        reentry_rule = st.selectbox(
            "Re-entry rule",
            options=[
                "Sell new call immediately",
                "Wait fixed number of days",
                "Wait for price recovery",
                "Wait for volatility condition",
                "Wait for regime condition",
            ],
            index=1,
            key="paid_preview_reentry_rule",
        )

    st.markdown("### Account-size screen")

    position_cap = get_position_cap_for_risk_tier(
        risk_tier=paid_risk_tier,
        ticker=paid_ticker,
    )

    current_price = get_current_price_for_ticker(paid_ticker)
    minimum_equity = estimate_minimum_equity_for_one_contract(
        current_price=current_price,
        position_cap=position_cap,
    )

    passes_screen = (
        minimum_equity is not None
        and minimum_equity <= float(paid_account_size)
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("Current price", format_currency(current_price))

    with metric_col2:
        st.metric("Position cap", f"{position_cap * 100:.1f}%")

    with metric_col3:
        st.metric("Estimated min equity", format_currency(minimum_equity))

    with metric_col4:
        if minimum_equity is None:
            st.metric("Screen result", "N/A")
        elif passes_screen:
            st.metric("Screen result", "Passes")
        else:
            st.metric("Screen result", "Too large")

    if minimum_equity is None:
        st.warning(
            "Current price was not available for this ticker. The paid "
            "version should diagnose whether the issue is missing price data, "
            "invalid ticker, missing option data, or liquidity failure."
        )
    elif passes_screen:
        st.success(
            f"{paid_ticker} passes the selected paid-preview account-size "
            f"screen. Estimated minimum equity is "
            f"{format_currency_text(minimum_equity)}."
        )
    else:
        st.warning(
            f"{paid_ticker} does not pass the selected paid-preview "
            f"account-size screen. Estimated minimum equity is "
            f"{format_currency_text(minimum_equity)}, compared with selected "
            f"account size {format_currency_text(float(paid_account_size))}."
        )

    st.markdown("### Optionability and liquidity screen")

    liquidity_df = pd.DataFrame(
        [
            {
                "Check": "Ticker exists",
                "Purpose": "Confirm that the ticker is valid.",
                "Paid version behavior": "Required before simulation.",
            },
            {
                "Check": "Has listed options",
                "Purpose": "Covered calls require listed call options.",
                "Paid version behavior": "Reject or warn if unavailable.",
            },
            {
                "Check": "DTE availability",
                "Purpose": "Find expirations near the selected DTE.",
                "Paid version behavior": "Select closest available expiration.",
            },
            {
                "Check": "Target-delta strike available",
                "Purpose": "Find a usable strike near the selected delta.",
                "Paid version behavior": "Select closest liquid strike.",
            },
            {
                "Check": "Bid/ask spread",
                "Purpose": "Avoid unrealistic fills on illiquid options.",
                "Paid version behavior": "Warn or reject wide-spread chains.",
            },
            {
                "Check": "Open interest and volume",
                "Purpose": "Estimate whether the option chain is usable.",
                "Paid version behavior": "Classify as liquid or illiquid.",
            },
        ]
    )

    st.dataframe(
        liquidity_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Paid preview summary")

    with st.container(border=True):
        st.write(
            f"This paid-preview setup would test {paid_ticker} using a "
            f"{format_currency_text(float(paid_account_size))} account, "
            f"{paid_risk_tier} risk tier, target delta {target_delta}, "
            f"{target_dte} DTE, and the strike method: {strike_method}."
        )

        st.write(
            f"The selected management logic is: {profit_rule}, "
            f"{rolling_rule}, and {reentry_rule}."
        )

        st.caption(
            "In the finished paid version, this setup should produce a rule "
            "comparison, account-size analysis, option-chain liquidity status, "
            "equity curve, benchmark comparison, and exportable report."
        )

    st.markdown("### Why this is paid functionality")

    paid_col1, paid_col2 = st.columns(2)

    with paid_col1:
        with st.container(border=True):
            st.subheader("More realistic")
            st.write(
                "Covered-call traders usually choose strikes using delta, DTE, "
                "liquidity, account size, and personal management rules. The "
                "paid version should let users model those choices."
            )

    with paid_col2:
        with st.container(border=True):
            st.subheader("More data-intensive")
            st.write(
                "Custom tickers and option-chain liquidity screens require "
                "more data access and validation than the fixed free preview."
            )

    display_public_disclaimer_short()


def build_active_session_review_scorecard() -> pd.DataFrame:
    """
    Build an illustrative end-of-session scorecard for active covered-call
    simulation.
    """
    rows = [
        {
            "Measure": "Starting equity",
            "Illustrative result": "$100,000",
            "What it means": "Baseline account value before the active session.",
        },
        {
            "Measure": "Ending active-simulation equity",
            "Illustrative result": "$102,950",
            "What it means": "Total account value after stock movement, option premium, and simulated management decisions.",
        },
        {
            "Measure": "Active-simulation return",
            "Illustrative result": "+2.95%",
            "What it means": "Return based on total equity, not just premium collected.",
        },
        {
            "Measure": "Buy-and-hold benchmark",
            "Illustrative result": "$104,600",
            "What it means": "What 100 shares alone would have been worth in this simplified path.",
        },
        {
            "Measure": "Rule benchmark",
            "Illustrative result": "$102,300",
            "What it means": "Illustrative result from a mechanical covered-call rule.",
        },
        {
            "Measure": "Premium collected",
            "Illustrative result": "$345",
            "What it means": "Visible option income collected during the session; not the same as total profit.",
        },
        {
            "Measure": "Estimated missed upside",
            "Illustrative result": "$1,650",
            "What it means": "Approximate amount by which active covered-call management lagged buy-and-hold in this rising path.",
        },
        {
            "Measure": "Decision takeaway",
            "Illustrative result": "Useful but capped",
            "What it means": "The user generated income and managed the call, but gave up some upside in a strong upward move.",
        },
    ]

    return pd.DataFrame(rows)


def build_active_session_decision_notes() -> pd.DataFrame:
    """
    Build illustrative qualitative feedback for active-simulation decisions.
    """
    rows = [
        {
            "Decision area": "Entry timing",
            "Illustrative feedback": "Selling the first call after a modest rise generated premium, but also capped upside early.",
            "Possible lesson": "Compare immediate call-writing with waiting for a stronger move or higher implied volatility.",
        },
        {
            "Decision area": "Strike choice",
            "Illustrative feedback": "The selected call balanced premium and upside room, but the market moved toward the strike quickly.",
            "Possible lesson": "Farther OTM calls may reduce assignment pressure but collect less premium.",
        },
        {
            "Decision area": "Roll decision",
            "Illustrative feedback": "Rolling up and out restored upside room but extended the obligation.",
            "Possible lesson": "A roll should be evaluated by total equity and future risk, not only whether it creates a credit.",
        },
        {
            "Decision area": "Closing decision",
            "Illustrative feedback": "Closing the short call reduced risk and reset the position.",
            "Possible lesson": "Closing can be useful when much of the premium has been captured or when the user wants flexibility.",
        },
        {
            "Decision area": "Benchmark comparison",
            "Illustrative feedback": "The active strategy outperformed the rule benchmark but lagged buy-and-hold in this rising path.",
            "Possible lesson": "Covered calls often trade some upside for premium income and smoother decision structure.",
        },
    ]

    return pd.DataFrame(rows)


def build_active_simulation_action_log() -> pd.DataFrame:
    """
    Build an illustrative action log for active covered-call simulation.
    """
    rows = [
        {
            "Time": "09:35",
            "User Action": "Start session",
            "Stock Price": "$100.00",
            "Position": "100 shares",
            "Short Call": "None",
            "Cash Event": "$0",
            "Total Equity": "$100,000",
        },
        {
            "Time": "09:42",
            "User Action": "Sell covered call",
            "Stock Price": "$100.80",
            "Position": "100 shares",
            "Short Call": "105C, 30 DTE",
            "Cash Event": "+$185 premium",
            "Total Equity": "$100,265",
        },
        {
            "Time": "10:18",
            "User Action": "Wait",
            "Stock Price": "$101.40",
            "Position": "100 shares",
            "Short Call": "105C, 30 DTE",
            "Cash Event": "$0",
            "Total Equity": "$100,710",
        },
        {
            "Time": "11:05",
            "User Action": "Roll up and out",
            "Stock Price": "$104.90",
            "Position": "100 shares",
            "Short Call": "108C, 45 DTE",
            "Cash Event": "+$35 net credit",
            "Total Equity": "$102,160",
        },
        {
            "Time": "12:30",
            "User Action": "Close short call",
            "Stock Price": "$103.20",
            "Position": "100 shares",
            "Short Call": "None",
            "Cash Event": "-$90 buyback",
            "Total Equity": "$102,540",
        },
    ]

    return pd.DataFrame(rows)


def build_active_simulation_equity_curve() -> pd.DataFrame:
    """
    Build an illustrative equity curve for active covered-call simulation.
    """
    rows = [
        {
            "Time": "09:35",
            "Active CC Simulation": 100000,
            "Buy and Hold": 100000,
            "Rule Benchmark": 100000,
        },
        {
            "Time": "09:42",
            "Active CC Simulation": 100265,
            "Buy and Hold": 100800,
            "Rule Benchmark": 100180,
        },
        {
            "Time": "10:18",
            "Active CC Simulation": 100710,
            "Buy and Hold": 101400,
            "Rule Benchmark": 100620,
        },
        {
            "Time": "11:05",
            "Active CC Simulation": 102160,
            "Buy and Hold": 104900,
            "Rule Benchmark": 101850,
        },
        {
            "Time": "12:30",
            "Active CC Simulation": 102540,
            "Buy and Hold": 103200,
            "Rule Benchmark": 102300,
        },
    ]

    return pd.DataFrame(rows)


def build_passive_market_animation_frames() -> pd.DataFrame:
    """
    Build an illustrative passive market-animation sequence for the active
    covered-call preview page.
    """
    rows = [
        {
            "Time": "09:30",
            "Stock Price": 100.00,
            "Short Call": "None",
            "Short Call Mark": 0.00,
            "Call Status": "No call open",
            "Total Equity": 100000,
            "Typical User Focus": "Observe the market",
            "Narrative": "The user begins with 100 shares and no short call. The first decision is whether to sell a covered call now or wait.",
        },
        {
            "Time": "09:40",
            "Stock Price": 100.60,
            "Short Call": "None",
            "Short Call Mark": 0.00,
            "Call Status": "No call open",
            "Total Equity": 100600,
            "Typical User Focus": "Check available calls",
            "Narrative": "The stock is moving modestly higher. A user might inspect the option chain and compare 0.25 to 0.35 delta calls.",
        },
        {
            "Time": "09:50",
            "Stock Price": 100.80,
            "Short Call": "105C, 30 DTE",
            "Short Call Mark": 1.85,
            "Call Status": "OTM by 4.20",
            "Total Equity": 100615,
            "Typical User Focus": "Sell covered call",
            "Narrative": "The user sells a 105 covered call for illustrative premium. Cash rises, but the short call is now a liability that must be tracked.",
        },
        {
            "Time": "10:05",
            "Stock Price": 101.70,
            "Short Call": "105C, 30 DTE",
            "Short Call Mark": 2.20,
            "Call Status": "OTM by 3.30",
            "Total Equity": 101165,
            "Typical User Focus": "Monitor moneyness",
            "Narrative": "The stock rises. The user is still profitable overall, but the short call has become more expensive to buy back.",
        },
        {
            "Time": "10:25",
            "Stock Price": 103.20,
            "Short Call": "105C, 30 DTE",
            "Short Call Mark": 3.05,
            "Call Status": "OTM by 1.80",
            "Total Equity": 101995,
            "Typical User Focus": "Prepare decision",
            "Narrative": "The stock is approaching the strike. A user might plan whether to hold, close early, or prepare to roll if the call moves ITM.",
        },
        {
            "Time": "10:45",
            "Stock Price": 105.40,
            "Short Call": "105C, 30 DTE",
            "Short Call Mark": 4.70,
            "Call Status": "ITM by 0.40",
            "Total Equity": 102215,
            "Typical User Focus": "Choose hold / close / roll",
            "Narrative": "The call is now slightly ITM. This is the central active decision point: hold the position, close the call, or roll to a higher strike.",
        },
        {
            "Time": "11:05",
            "Stock Price": 106.20,
            "Short Call": "108C, 45 DTE",
            "Short Call Mark": 4.95,
            "Call Status": "Rolled; OTM by 1.80",
            "Total Equity": 102685,
            "Typical User Focus": "Roll up and out",
            "Narrative": "In this illustrative path, the user rolls up and out. The new call gives the stock more room, but the position remains capped.",
        },
        {
            "Time": "11:30",
            "Stock Price": 104.70,
            "Short Call": "108C, 45 DTE",
            "Short Call Mark": 3.85,
            "Call Status": "OTM by 3.30",
            "Total Equity": 102335,
            "Typical User Focus": "Evaluate roll result",
            "Narrative": "The stock pulls back. The roll looks better now because the new short call has lost value and the position has more breathing room.",
        },
        {
            "Time": "12:05",
            "Stock Price": 103.80,
            "Short Call": "108C, 45 DTE",
            "Short Call Mark": 3.20,
            "Call Status": "OTM by 4.20",
            "Total Equity": 102080,
            "Typical User Focus": "Consider closing",
            "Narrative": "The short call has become cheaper. A user might close it to lock in option profit, or hold for more time decay.",
        },
        {
            "Time": "12:30",
            "Stock Price": 104.30,
            "Short Call": "None",
            "Short Call Mark": 0.00,
            "Call Status": "Call closed",
            "Total Equity": 102510,
            "Typical User Focus": "Close short call",
            "Narrative": "The user closes the short call in the simulation. The position returns to long shares plus cash, ready for a new decision.",
        },
        {
            "Time": "13:00",
            "Stock Price": 105.10,
            "Short Call": "110C, 30 DTE",
            "Short Call Mark": 1.60,
            "Call Status": "New call; OTM by 4.90",
            "Total Equity": 103025,
            "Typical User Focus": "Sell new call",
            "Narrative": "The user sells a new call after the stock stabilizes. The simulator would track whether re-entry improved total equity.",
        },
        {
            "Time": "13:30",
            "Stock Price": 104.60,
            "Short Call": "110C, 30 DTE",
            "Short Call Mark": 1.35,
            "Call Status": "OTM by 5.40",
            "Total Equity": 102950,
            "Typical User Focus": "End / review session",
            "Narrative": "The session ends with the call comfortably OTM. The user reviews total equity, premium, missed upside, roll results, and decision quality.",
        },
    ]

    return pd.DataFrame(rows)


def build_pre_trade_impact_preview(
    stock_price: float,
    strike_price: float,
    option_mid_price: float,
    contract_multiplier: int = 100,
) -> dict[str, float]:
    """
    Calculate simple illustrative covered-call impact metrics before placement.
    """
    stock_value = stock_price * contract_multiplier
    premium_cash = option_mid_price * contract_multiplier
    upside_to_strike = max(strike_price - stock_price, 0.0) * contract_multiplier
    gross_if_assigned = upside_to_strike + premium_cash

    premium_yield = premium_cash / stock_value if stock_value > 0 else 0.0
    assignment_return = gross_if_assigned / stock_value if stock_value > 0 else 0.0
    downside_buffer = option_mid_price / stock_price if stock_price > 0 else 0.0

    return {
        "stock_value": stock_value,
        "premium_cash": premium_cash,
        "upside_to_strike": upside_to_strike,
        "gross_if_assigned": gross_if_assigned,
        "premium_yield": premium_yield,
        "assignment_return": assignment_return,
        "downside_buffer": downside_buffer,
    }


def build_simulated_option_chain_preview() -> pd.DataFrame:
    """
    Build an illustrative option-chain table for active covered-call placement.
    """
    rows = [
        {
            "Expiration": "30 DTE",
            "Strike": 103,
            "Delta": 0.43,
            "Bid": 3.15,
            "Ask": 3.35,
            "Mid": 3.25,
            "Moneyness": "Near the money",
            "Tradeoff": "Higher premium, more assignment pressure",
        },
        {
            "Expiration": "30 DTE",
            "Strike": 105,
            "Delta": 0.31,
            "Bid": 1.78,
            "Ask": 1.92,
            "Mid": 1.85,
            "Moneyness": "Moderately OTM",
            "Tradeoff": "Balanced premium and upside room",
        },
        {
            "Expiration": "30 DTE",
            "Strike": 108,
            "Delta": 0.21,
            "Bid": 0.92,
            "Ask": 1.04,
            "Mid": 0.98,
            "Moneyness": "Farther OTM",
            "Tradeoff": "Lower premium, more upside room",
        },
        {
            "Expiration": "45 DTE",
            "Strike": 108,
            "Delta": 0.29,
            "Bid": 1.62,
            "Ask": 1.80,
            "Mid": 1.71,
            "Moneyness": "Farther OTM, longer DTE",
            "Tradeoff": "More premium, longer obligation",
        },
        {
            "Expiration": "45 DTE",
            "Strike": 110,
            "Delta": 0.22,
            "Bid": 1.05,
            "Ask": 1.19,
            "Mid": 1.12,
            "Moneyness": "Farther OTM, longer DTE",
            "Tradeoff": "Lower delta, still meaningful premium",
        },
    ]

    return pd.DataFrame(rows)


def calculate_axis_domain(
    values: pd.Series,
    padding_fraction: float = 0.08,
) -> list[float]:
    """
    Calculate a stable y-axis domain with padding.

    This prevents an animated chart from clipping or disappearing when the
    latest value exceeds the initial chart range.
    """
    numeric_values = pd.to_numeric(values, errors="coerce").dropna()

    if numeric_values.empty:
        return [0.0, 1.0]

    minimum_value = float(numeric_values.min())
    maximum_value = float(numeric_values.max())

    if minimum_value == maximum_value:
        padding = max(abs(minimum_value) * padding_fraction, 1.0)
    else:
        padding = (maximum_value - minimum_value) * padding_fraction

    return [
        minimum_value - padding,
        maximum_value + padding,
    ]


def build_fixed_domain_line_chart(
    chart_df: pd.DataFrame,
    x_column: str,
    y_column: str,
    y_domain: list[float],
    title: str,
    reference_line_value: float | None = None,
    reference_line_label: str | None = None,
) -> alt.Chart:
    """
    Build an Altair line chart with a fixed y-axis domain.

    Optionally add a horizontal reference line, useful for illustrative
    thresholds such as a hypothetical ITM level.
    """
    base_chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X(
                f"{x_column}:N",
                title=None,
                sort=None,
            ),
            y=alt.Y(
                f"{y_column}:Q",
                title=title,
                scale=alt.Scale(domain=y_domain),
            ),
            tooltip=[
                alt.Tooltip(f"{x_column}:N", title=x_column),
                alt.Tooltip(f"{y_column}:Q", title=title, format=",.2f"),
            ],
        )
        .properties(height=220)
    )

    if reference_line_value is None:
        return base_chart

    reference_df = pd.DataFrame(
        [
            {
                x_column: chart_df[x_column].iloc[0],
                y_column: reference_line_value,
                "Reference_Label": reference_line_label or "Reference line",
            },
            {
                x_column: chart_df[x_column].iloc[-1],
                y_column: reference_line_value,
                "Reference_Label": reference_line_label or "Reference line",
            },
        ]
    )

    reference_line = (
        alt.Chart(reference_df)
        .mark_rule(strokeDash=[6, 6], size=2)
        .encode(
            y=alt.Y(
                f"{y_column}:Q",
                scale=alt.Scale(domain=y_domain),
            ),
            tooltip=[
                alt.Tooltip("Reference_Label:N", title="Guide"),
                alt.Tooltip(f"{y_column}:Q", title="Level", format=",.2f"),
            ],
        )
    )

    return base_chart + reference_line


def page_active_cc_simulation_preview() -> None:
    """
    Public-facing preview for active real-time covered-call simulation.
    """
    st.header("Active Covered-Call Simulation Preview")

    st.write(
        "This is the most interactive future version of the product: a "
        "paper-trading style covered-call simulator where the user actively "
        "places, closes, rolls, or waits as market data updates."
    )

    st.warning(
        "This page is a prototype layout. It does not yet use live option "
        "chains or place real trades. The purpose is to show the intended "
        "active user workflow."
    )

    st.markdown("### Core idea")

    with st.container(border=True):
        st.write(
            "The user should not only read a table. The user should participate "
            "in the simulated market. They should own shares, choose when to "
            "sell a covered call, select the strike and expiration, watch the "
            "call move OTM or ITM, and decide whether to hold, close, roll, "
            "wait, or accept assignment in the simulation."
        )

        st.success(
            "This turns the simulator into an active decision-training tool, "
            "not just a static backtest."
        )

    st.markdown("### Training-tool value")

    training_value_df = pd.DataFrame(
        [
            {
                "Training benefit": "Decision repetition",
                "How the simulator helps": "The user can practice selling, closing, rolling, waiting, and reviewing many times without risking capital.",
            },
            {
                "Training benefit": "Immediate feedback",
                "How the simulator helps": "Each simulated action can update cash, option liability, total equity, missed upside, and benchmark comparison.",
            },
            {
                "Training benefit": "Mistake discovery",
                "How the simulator helps": "The user can see when collecting premium still leads to underperformance or poor risk/reward.",
            },
            {
                "Training benefit": "Rule development",
                "How the simulator helps": "Repeated sessions can help the user refine personal rules for delta, DTE, rolling, and re-entry.",
            },
        ]
    )

    st.dataframe(
        training_value_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### How the user participates")

    st.write(
        "The active simulator should walk the user through the same decisions "
        "a covered-call trader normally faces. The purpose is not to predict "
        "the market. The purpose is to let the user practice decision-making "
        "as the position changes."
    )

    participation_df = pd.DataFrame(
        [
            {
                "Stage": "1. Observe",
                "User decision": "Watch the stock move before selling a call.",
                "Simulator feedback": "Shows stock price, available calls, and current account equity.",
            },
            {
                "Stage": "2. Sell CC",
                "User decision": "Choose strike, expiration, delta, and premium.",
                "Simulator feedback": "Adds cash premium and opens a short-call liability.",
            },
            {
                "Stage": "3. Monitor",
                "User decision": "Watch whether the call stays OTM or moves ITM.",
                "Simulator feedback": "Updates moneyness, option value, unrealized P/L, and total equity.",
            },
            {
                "Stage": "4. Manage",
                "User decision": "Hold, close, roll, wait, or accept assignment.",
                "Simulator feedback": "Shows how the decision changes cash, capped upside, and future risk.",
            },
            {
                "Stage": "5. Review",
                "User decision": "Compare decision results against benchmarks.",
                "Simulator feedback": "Shows total equity, buy-and-hold comparison, rule benchmark, and event log.",
            },
        ]
    )

    st.dataframe(
        participation_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Passive Market Animation Preview")

    st.write(
        "Before asking the user to click anything, the site can illustrate the "
        "idea with an auto-play demo. The stock moves, the short call moves "
        "closer to or farther from the strike, and total equity changes over "
        "time."
    )

    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #e8f1ff 0%, #f4f8ff 100%);
            border: 1px solid #b8d4ff;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin: 0.5rem 0 1rem 0;
        ">
            <strong>Preview action:</strong>
            Run the mini market demo to watch the stock price, short-call
            status, and total equity update together.
        </div>
        """,
        unsafe_allow_html=True,
    )

    demo_control_col1, demo_control_col2 = st.columns([1, 1])

    with demo_control_col1:
        demo_speed = st.selectbox(
            "Demo speed",
            options=["Slow", "Medium", "Fast"],
            index=1,
            key="active_cc_demo_speed",
        )

    with demo_control_col2:
        st.write("")
        run_passive_demo = st.button(
            "Run illustrative market demo",
            key="active_cc_run_demo",
            type="primary",
            use_container_width=True,
        )

    st.caption(
        "This is an illustrative mini-demo, not a live engine. It is meant to "
        "show what an active covered-call environment feels like even before "
        "the user begins interacting."
    )

    passive_demo_frames = build_passive_market_animation_frames()

    metric_placeholder = st.empty()
    chart_placeholder = st.empty()
    note_placeholder = st.empty()

    speed_map = {
        "Slow": 1.0,
        "Medium": 0.55,
        "Fast": 0.25,
    }

    def render_passive_demo_frame(frame_df: pd.DataFrame) -> None:
        current_row = frame_df.iloc[-1]

        with metric_placeholder.container():
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

            with metric_col1:
                st.metric("Time", str(current_row["Time"]))

            with metric_col2:
                st.metric("Stock price", format_currency(float(current_row["Stock Price"])))

            with metric_col3:
                st.metric("Call status", str(current_row["Call Status"]))

            with metric_col4:
                st.metric(
                    "Total equity",
                    format_currency(float(current_row["Total Equity"])),
                )

            detail_col1, detail_col2, detail_col3 = st.columns(3)

            with detail_col1:
                st.metric("Short call", str(current_row["Short Call"]))

            with detail_col2:
                st.metric(
                    "Short call mark",
                    format_currency(float(current_row["Short Call Mark"])),
                )

            with detail_col3:
                st.metric("Typical user focus", str(current_row["Typical User Focus"]))

        with chart_placeholder.container():
            chart_col1, chart_col2 = st.columns(2)

            stock_price_domain = calculate_axis_domain(
                passive_demo_frames["Stock Price"]
            )

            total_equity_domain = calculate_axis_domain(
                passive_demo_frames["Total Equity"]
            )

            with chart_col1:
                st.write("**Stock price path**")
                st.altair_chart(
                    build_fixed_domain_line_chart(
                        chart_df=frame_df,
                        x_column="Time",
                        y_column="Stock Price",
                        y_domain=stock_price_domain,
                        title="Stock price",
                        reference_line_value=105.0,
                        reference_line_label="Hypothetical ITM threshold",
                    ),
                    use_container_width=True,
                )
                st.markdown(
                    """
                    <div style="
                        display: inline-block;
                        background: #fff8e8;
                        border: 1px solid #f1d48a;
                        border-radius: 10px;
                        padding: 0.45rem 0.7rem;
                        margin-top: 0.35rem;
                        font-size: 0.92rem;
                    ">
                        <strong>ITM legend:</strong>
                        <span style="
                            display: inline-block;
                            width: 34px;
                            border-top: 3px dashed #666;
                            margin: 0 0.45rem 0 0.55rem;
                            vertical-align: middle;
                        "></span>
                        Hypothetical ITM threshold
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption(
                    "Above the dashed line, the illustrative short call would be "
                    "in or near the money."
                )

            with chart_col2:
                st.write("**Total equity path**")
                st.altair_chart(
                    build_fixed_domain_line_chart(
                        chart_df=frame_df,
                        x_column="Time",
                        y_column="Total Equity",
                        y_domain=total_equity_domain,
                        title="Total equity",
                    ),
                    use_container_width=True,
                )

        with note_placeholder.container():
            with st.container(border=True):
                st.write(current_row["Narrative"])

    if run_passive_demo:
        for frame_index in range(1, len(passive_demo_frames) + 1):
            render_passive_demo_frame(passive_demo_frames.iloc[:frame_index].copy())
            time.sleep(speed_map.get(demo_speed, 0.55))
    else:
        render_passive_demo_frame(passive_demo_frames.iloc[:1].copy())

    with st.expander("Show passive demo frame table", expanded=False):
        st.dataframe(
            passive_demo_frames,
            width="stretch",
            hide_index=True,
        )

    st.markdown("### Active session controls")

    setup_col1, setup_col2, setup_col3 = st.columns(3)

    with setup_col1:
        active_ticker = st.text_input(
            "Ticker",
            value="SPY",
            key="active_cc_ticker",
        ).upper().strip()

    with setup_col2:
        st.number_input(
            "Starting account equity",
            min_value=10000,
            max_value=10000000,
            value=250000,
            step=10000,
            format="%d",
            key="active_cc_account_equity",
        )

    with setup_col3:
        st.selectbox(
            "Simulation mode",
            options=[
                "Historical replay",
                "Near-real-time paper simulation",
                "Live market training mode",
            ],
            index=1,
            key="active_cc_mode",
        )

    option_col1, option_col2, option_col3 = st.columns(3)

    with option_col1:
        st.selectbox(
            "Target delta",
            options=["0.15", "0.20", "0.25", "0.30", "0.35", "0.40"],
            index=3,
            key="active_cc_delta",
        )

    with option_col2:
        st.selectbox(
            "Target DTE",
            options=["7", "14", "21", "30", "45", "60"],
            index=3,
            key="active_cc_dte",
        )

    with option_col3:
        st.selectbox(
            "Strike method",
            options=[
                "Closest to target delta",
                "Fixed percent OTM",
                "Liquidity-filtered best match",
            ],
            index=0,
            key="active_cc_strike_method",
        )

    st.markdown("### Simulated option-chain placement panel")

    st.write(
        "In the active simulator, the user would not merely press a generic "
        "button. The user would inspect available calls, choose a strike and "
        "expiration, and then place the simulated covered call."
    )

    option_chain_df = build_simulated_option_chain_preview()

    display_chain_df = option_chain_df.copy()
    display_chain_df["Bid"] = display_chain_df["Bid"].map(lambda value: f"${value:.2f}")
    display_chain_df["Ask"] = display_chain_df["Ask"].map(lambda value: f"${value:.2f}")
    display_chain_df["Mid"] = display_chain_df["Mid"].map(lambda value: f"${value:.2f}")
    display_chain_df["Delta"] = display_chain_df["Delta"].map(lambda value: f"{value:.2f}")

    st.dataframe(
        display_chain_df,
        width="stretch",
        hide_index=True,
    )

    option_labels = [
        (
            f"{row['Expiration']} | {int(row['Strike'])}C | "
            f"Delta {row['Delta']:.2f} | Mid ${row['Mid']:.2f}"
        )
        for _, row in option_chain_df.iterrows()
    ]

    selected_option_label = st.selectbox(
        "Select a simulated covered call candidate",
        options=option_labels,
        index=1,
        key="active_cc_selected_option_candidate",
    )

    selected_option_index = option_labels.index(selected_option_label)
    selected_option = option_chain_df.iloc[selected_option_index]

    st.markdown("### Simulated order ticket")

    ticket_col1, ticket_col2, ticket_col3, ticket_col4 = st.columns(4)

    with ticket_col1:
        st.metric("Selected call", f"{int(selected_option['Strike'])}C")

    with ticket_col2:
        st.metric("Expiration", str(selected_option["Expiration"]))

    with ticket_col3:
        st.metric("Delta", f"{float(selected_option['Delta']):.2f}")

    with ticket_col4:
        st.metric("Estimated premium", f"${float(selected_option['Mid']) * 100:,.0f}")

    with st.container(border=True):
        st.write(
            f"The selected candidate is the {int(selected_option['Strike'])}C "
            f"with {selected_option['Expiration']}, approximate delta "
            f"{float(selected_option['Delta']):.2f}, and illustrative mid-price "
            f"${float(selected_option['Mid']):.2f}. For one covered-call "
            f"contract, that represents about "
            f"${float(selected_option['Mid']) * 100:,.0f} in premium before "
            f"transaction costs and slippage."
        )

        st.caption(
            "A real paid version should also show bid/ask spread, liquidity, "
            "open interest, expected assignment pressure, capped upside, and "
            "estimated total-equity impact before the user places the "
            "simulated trade."
        )

    st.markdown("### Pre-trade impact preview")

    simulated_stock_price = 100.80

    impact_metrics = build_pre_trade_impact_preview(
        stock_price=simulated_stock_price,
        strike_price=float(selected_option["Strike"]),
        option_mid_price=float(selected_option["Mid"]),
    )

    impact_col1, impact_col2, impact_col3, impact_col4 = st.columns(4)

    with impact_col1:
        st.metric(
            "Premium received",
            format_currency(impact_metrics["premium_cash"]),
        )

    with impact_col2:
        st.metric(
            "Upside to strike",
            format_currency(impact_metrics["upside_to_strike"]),
        )

    with impact_col3:
        st.metric(
            "Gross if assigned",
            format_currency(impact_metrics["gross_if_assigned"]),
        )

    with impact_col4:
        st.metric(
            "Premium yield",
            f"{impact_metrics['premium_yield'] * 100:.2f}%",
        )

    impact_summary_df = pd.DataFrame(
        [
            {
                "Metric": "Current stock value",
                "Illustrative value": format_currency_text(
                    impact_metrics["stock_value"]
                ),
                "Interpretation": "Approximate value of 100 shares before selling the call.",
            },
            {
                "Metric": "Premium received",
                "Illustrative value": format_currency_text(
                    impact_metrics["premium_cash"]
                ),
                "Interpretation": "Cash collected from selling one call contract.",
            },
            {
                "Metric": "Upside to strike",
                "Illustrative value": format_currency_text(
                    impact_metrics["upside_to_strike"]
                ),
                "Interpretation": "Additional stock gain available before the covered call reaches the strike.",
            },
            {
                "Metric": "Gross if assigned",
                "Illustrative value": format_currency_text(
                    impact_metrics["gross_if_assigned"]
                ),
                "Interpretation": "Premium plus stock gain up to the strike, before taxes, fees, and slippage.",
            },
            {
                "Metric": "Downside buffer",
                "Illustrative value": f"{impact_metrics['downside_buffer'] * 100:.2f}%",
                "Interpretation": "Approximate stock decline offset by the option premium.",
            },
            {
                "Metric": "If-assigned return",
                "Illustrative value": f"{impact_metrics['assignment_return'] * 100:.2f}%",
                "Interpretation": "Approximate return if the stock finishes above the strike and shares are called away.",
            },
        ]
    )

    st.dataframe(
        impact_summary_df,
        width="stretch",
        hide_index=True,
    )

    with st.container(border=True):
        st.write(
            "This is the kind of preview a user should see before placing a "
            "simulated covered call. It makes the tradeoff explicit: more "
            "premium usually means less upside room, while farther OTM calls "
            "usually leave more upside but collect less income."
        )

        st.warning(
            "This is still a simplified estimate. A real simulator should "
            "include bid/ask spread, liquidity, transaction costs, tax lots, "
            "early assignment risk, and changing option value over time."
        )

    st.markdown("### Post-trade position preview")

    post_trade_col1, post_trade_col2, post_trade_col3, post_trade_col4 = st.columns(4)

    with post_trade_col1:
        st.metric("Shares held", "100")

    with post_trade_col2:
        st.metric("Short call", f"-1 {int(selected_option['Strike'])}C")

    with post_trade_col3:
        st.metric("Cash added", format_currency(impact_metrics["premium_cash"]))

    with post_trade_col4:
        st.metric(
            "Initial call liability",
            f"-{format_currency(impact_metrics['premium_cash'])}",
        )

    post_trade_df = pd.DataFrame(
        [
            {
                "Position component": "Long shares",
                "Quantity": "100 shares",
                "Initial effect": "User owns the underlying required for one covered call.",
                "What changes later": "Stock value moves with the market.",
            },
            {
                "Position component": "Short call",
                "Quantity": f"-1 {int(selected_option['Strike'])}C",
                "Initial effect": "Option premium is collected, but a short-call liability is opened.",
                "What changes later": "Liability rises if the stock moves toward or above the strike.",
            },
            {
                "Position component": "Cash",
                "Quantity": format_currency_text(impact_metrics["premium_cash"]),
                "Initial effect": "Premium is credited to the simulated account.",
                "What changes later": "Cash decreases if the call is bought back or rolled for a debit.",
            },
            {
                "Position component": "Upside cap",
                "Quantity": f"{int(selected_option['Strike'])} strike",
                "Initial effect": "Stock upside is limited beyond the selected strike.",
                "What changes later": "A roll may move the cap higher, usually at a cost or smaller credit.",
            },
            {
                "Position component": "Assignment condition",
                "Quantity": "Possible above strike",
                "Initial effect": "Shares may be called away if the option finishes ITM.",
                "What changes later": "Assignment risk depends on moneyness, expiration, dividends, and exercise behavior.",
            },
        ]
    )

    st.dataframe(
        post_trade_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Management trigger preview")

    trigger_df = pd.DataFrame(
        [
            {
                "Trigger": "Stock remains far below strike",
                "Likely user choice": "Hold or close after profit target",
                "Simulator should show": "Time decay, option profit, and remaining premium.",
            },
            {
                "Trigger": "Short call reaches 50% profit",
                "Likely user choice": "Close call or continue holding",
                "Simulator should show": "Realized option P/L and new total equity.",
            },
            {
                "Trigger": "Stock approaches strike",
                "Likely user choice": "Hold, close, or prepare to roll",
                "Simulator should show": "Moneyness, buyback cost, and capped-upside risk.",
            },
            {
                "Trigger": "Short call moves ITM",
                "Likely user choice": "Roll up/out, close, or accept assignment risk",
                "Simulator should show": "Net roll credit/debit and new upside cap.",
            },
            {
                "Trigger": "Expiration nears",
                "Likely user choice": "Let expire, close, roll, or handle assignment",
                "Simulator should show": "Final option value, assignment status, and total account result.",
            },
        ]
    )

    st.dataframe(
        trigger_df,
        width="stretch",
        hide_index=True,
    )

    with st.container(border=True):
        st.write(
            "This section turns the selected option into a position. The user "
            "can see that selling a covered call is not just collecting "
            "premium; it creates a managed position with a short-call liability, "
            "a capped upside, and future decision points."
        )

    st.markdown("### Simulated action panel")

    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    with action_col1:
        st.button("Sell selected CC", disabled=True, type="primary")

    with action_col2:
        st.button("Close short call", disabled=True)

    with action_col3:
        st.button("Roll call", disabled=True)

    with action_col4:
        st.button("Wait / update market", disabled=True)

    st.caption(
        "Buttons are disabled in this prototype. In the finished simulator, "
        "these would update the simulated position, cash, option value, event "
        "log, and total-equity curve."
    )

    st.markdown("### What active placement means")

    placement_col1, placement_col2 = st.columns(2)

    with placement_col1:
        with st.container(border=True):
            st.subheader("User places simulated CCs")
            st.markdown(
                """
                The user actively chooses:

                - When to sell the call.
                - Which expiration to use.
                - Which strike to select.
                - Whether to prioritize delta, premium, or liquidity.
                - Whether to accept a lower premium for a safer strike.
                """
            )

    with placement_col2:
        with st.container(border=True):
            st.subheader("User manages the open call")
            st.markdown(
                """
                As the market moves, the user decides whether to:

                - Hold the call.
                - Close the call.
                - Roll out.
                - Roll up.
                - Roll out and up.
                - Wait.
                - Accept assignment in the simulation.
                """
            )

    st.markdown("### Total Equity Over Time")

    equity_df = build_active_simulation_equity_curve()

    st.line_chart(
        equity_df.set_index("Time"),
        height=360,
    )

    with st.container(border=True):
        st.write(
            "The equity curve should update after every active decision. This "
            "is the main feedback mechanism. It shows whether the user's "
            "covered-call decisions improved total wealth or merely generated "
            "visible premium."
        )

        st.warning(
            "Premium collected is not the same as profit. Active simulation "
            "should always track total equity."
        )

    st.markdown("### Simulated decision log")

    action_log_df = build_active_simulation_action_log()

    st.dataframe(
        action_log_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Session review scorecard")

    scorecard_col1, scorecard_col2, scorecard_col3, scorecard_col4 = st.columns(4)

    with scorecard_col1:
        st.metric("Ending equity", "$102,950")

    with scorecard_col2:
        st.metric("Active return", "+2.95%")

    with scorecard_col3:
        st.metric("Premium collected", "$345")

    with scorecard_col4:
        st.metric("Missed upside", "$1,650")

    session_review_df = build_active_session_review_scorecard()

    st.dataframe(
        session_review_df,
        width="stretch",
        hide_index=True,
    )

    with st.container(border=True):
        st.write(
            "The session review is where the active simulator teaches the main "
            "lesson: the user should judge the strategy by total equity and "
            "benchmark comparison, not by premium collected alone."
        )

        st.warning(
            "A covered-call session can show positive premium income while "
            "still underperforming buy-and-hold if the stock rises strongly."
        )

    st.markdown("### Decision-quality notes")

    decision_notes_df = build_active_session_decision_notes()

    st.dataframe(
        decision_notes_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Product positioning")

    positioning_col1, positioning_col2 = st.columns(2)

    with positioning_col1:
        with st.container(border=True):
            st.subheader("Individual / Pro tier")
            st.write(
                "Historical replay with active decisions belongs in the "
                "Individual / Pro tier. The user practices selling, closing, "
                "rolling, and waiting on past market paths without seeing the "
                "future."
            )

    with positioning_col2:
        with st.container(border=True):
            st.subheader("Future Professional tier")
            st.write(
                "Near-real-time active simulation belongs in the Future "
                "Professional tier because it requires live or near-live price "
                "data, option-chain updates, liquidity checks, intraday state, "
                "saved sessions, and more careful infrastructure."
            )

    st.markdown("### Required safeguards")

    safeguards_df = pd.DataFrame(
        [
            {
                "Safeguard": "Paper simulation only",
                "Reason": "The product should not accidentally imply that it places real trades.",
            },
            {
                "Safeguard": "Clear data timestamps",
                "Reason": "Users need to know whether prices and option chains are live, delayed, or historical.",
            },
            {
                "Safeguard": "Liquidity warnings",
                "Reason": "Simulated fills should not imply that real fills are guaranteed.",
            },
            {
                "Safeguard": "Total-equity tracking",
                "Reason": "Premium income alone can be misleading.",
            },
            {
                "Safeguard": "No trade recommendation wording",
                "Reason": "The simulator is for education and decision practice.",
            },
        ]
    )

    st.dataframe(
        safeguards_df,
        width="stretch",
        hide_index=True,
    )

    display_public_disclaimer_short()


def build_training_mode_lesson_path() -> pd.DataFrame:
    """
    Build a structured lesson path for the Training Mode Preview page.
    """
    rows = [
        {
            "Level": "Beginner",
            "Training focus": "Understand the basic covered-call tradeoff",
            "User practices": "Sell one covered call, watch premium, upside cap, and assignment condition.",
            "Main lesson": "Premium reduces some downside but caps upside.",
        },
        {
            "Level": "Beginner",
            "Training focus": "Premium is not profit",
            "User practices": "Compare option income with total account equity.",
            "Main lesson": "A position can collect premium and still underperform.",
        },
        {
            "Level": "Intermediate",
            "Training focus": "Strike and delta selection",
            "User practices": "Compare lower-delta and higher-delta calls.",
            "Main lesson": "Higher premium usually means less upside room and more assignment pressure.",
        },
        {
            "Level": "Intermediate",
            "Training focus": "Profit-taking discipline",
            "User practices": "Close calls at 25%, 50%, or 75% of max profit.",
            "Main lesson": "Early closing can reduce risk but may leave premium uncollected.",
        },
        {
            "Level": "Advanced",
            "Training focus": "Rolling decisions",
            "User practices": "Roll out, roll up, roll out and up, or accept assignment risk.",
            "Main lesson": "A roll should be judged by total equity and future exposure, not just net credit.",
        },
        {
            "Level": "Advanced",
            "Training focus": "Market-regime awareness",
            "User practices": "Run the same rule in bullish, bearish, sideways, high-vol, and low-vol paths.",
            "Main lesson": "Covered-call rules are path-dependent and regime-sensitive.",
        },
        {
            "Level": "Future Professional",
            "Training focus": "Real-time active simulation",
            "User practices": "Manage simulated calls using intraday price and option-chain updates.",
            "Main lesson": "Real-time decision pressure requires liquidity, fill-quality, and risk controls.",
        },
    ]

    return pd.DataFrame(rows)


def build_training_mode_score_categories() -> pd.DataFrame:
    """
    Build illustrative training score categories.
    """
    rows = [
        {
            "Score category": "Total-equity awareness",
            "What is measured": "Whether the user evaluates the full account rather than premium alone.",
            "Example feedback": "Good: you compared ending equity with buy-and-hold and rule benchmarks.",
        },
        {
            "Score category": "Strike discipline",
            "What is measured": "Whether the selected strike fits the user's risk and upside objective.",
            "Example feedback": "Watchlist: the high-premium strike left very little upside room.",
        },
        {
            "Score category": "Exit discipline",
            "What is measured": "Whether the user closes or holds based on a defined rule.",
            "Example feedback": "Good: you closed after most of the premium was captured.",
        },
        {
            "Score category": "Rolling discipline",
            "What is measured": "Whether rolls are judged by future risk and total equity.",
            "Example feedback": "Watchlist: the roll created a credit but extended assignment pressure.",
        },
        {
            "Score category": "Benchmark comparison",
            "What is measured": "Whether the user compares active decisions with buy-and-hold and mechanical rules.",
            "Example feedback": "Good: you recognized that covered calls lagged in a strong upward path.",
        },
    ]

    return pd.DataFrame(rows)


def page_training_mode_preview() -> None:
    """
    Public-facing preview of the covered-call training mode.
    """
    st.header("Training Mode Preview")

    st.write(
        "Training Mode positions the simulator as a structured practice "
        "environment. Users can learn covered-call management by making "
        "decisions, seeing consequences, reviewing total equity, and comparing "
        "their choices with benchmarks."
    )

    st.info(
        "The goal is not to tell users what trade to make. The goal is to help "
        "users practice the decision process before risking real capital."
    )

    st.markdown("### Training path")

    lesson_path_df = build_training_mode_lesson_path()

    st.dataframe(
        lesson_path_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Practice modules")

    module_col1, module_col2, module_col3 = st.columns(3)

    with module_col1:
        with st.container(border=True):
            st.subheader("Beginner module")
            st.markdown(
                """
                - What is a covered call?
                - How premium works.
                - Why upside is capped.
                - What assignment means.
                - Why total equity matters.
                """
            )

    with module_col2:
        with st.container(border=True):
            st.subheader("Intermediate module")
            st.markdown(
                """
                - Strike selection.
                - Delta and DTE choices.
                - Closing at profit targets.
                - Waiting before re-entry.
                - Comparing rule outcomes.
                """
            )

    with module_col3:
        with st.container(border=True):
            st.subheader("Advanced module")
            st.markdown(
                """
                - Rolling up and out.
                - Rolling only for credit.
                - Managing ITM calls.
                - Regime-sensitive behavior.
                - Benchmark-aware review.
                """
            )

    st.markdown("### How a training session would work")

    session_col1, session_col2 = st.columns(2)

    with session_col1:
        with st.container(border=True):
            st.subheader("During the session")
            st.markdown(
                """
                1. User selects a lesson or scenario.
                2. Simulator shows stock path and candidate calls.
                3. User chooses a covered-call action.
                4. Simulator updates cash, option value, and total equity.
                5. User keeps managing the position as conditions change.
                """
            )

    with session_col2:
        with st.container(border=True):
            st.subheader("After the session")
            st.markdown(
                """
                1. Review ending total equity.
                2. Compare with buy-and-hold.
                3. Compare with a mechanical rule.
                4. Review premium versus missed upside.
                5. Receive decision-quality feedback.
                """
            )

    st.markdown("### Training scorecard categories")

    score_categories_df = build_training_mode_score_categories()

    st.dataframe(
        score_categories_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Why this may be commercially useful")

    commercial_col1, commercial_col2 = st.columns(2)

    with commercial_col1:
        with st.container(border=True):
            st.subheader("Reduces intimidation")
            st.write(
                "Many investors understand the definition of a covered call but "
                "are unsure how to manage one after price starts moving. "
                "Training Mode lets them practice in a controlled environment."
            )

    with commercial_col2:
        with st.container(border=True):
            st.subheader("Creates repeat use")
            st.write(
                "A static calculator may be used once. A training simulator can "
                "be used repeatedly because each scenario teaches a different "
                "decision pattern."
            )

    st.markdown("### Tier placement")

    tier_df = pd.DataFrame(
        [
            {
                "Feature": "Basic lesson explanations",
                "Free": "Yes",
                "Individual / Pro": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Historical training scenarios",
                "Free": "Limited preview",
                "Individual / Pro": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Active simulated covered-call placement",
                "Free": "Preview only",
                "Individual / Pro": "Yes, historical",
                "Future Professional": "Yes, real-time / intraday",
            },
            {
                "Feature": "Training scorecard",
                "Free": "Preview only",
                "Individual / Pro": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Saved sessions",
                "Free": "No",
                "Individual / Pro": "Possible",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Client or classroom demonstrations",
                "Free": "No",
                "Individual / Pro": "No",
                "Future Professional": "Yes",
            },
        ]
    )

    st.dataframe(
        tier_df,
        width="stretch",
        hide_index=True,
    )

    display_public_disclaimer_short()


def build_report_preview_summary() -> pd.DataFrame:
    """
    Build an illustrative downloadable report summary table.
    """
    rows = [
        {
            "Report item": "Ticker",
            "Illustrative value": "SPY",
            "Purpose": "Identifies the simulated underlying.",
        },
        {
            "Report item": "Training mode",
            "Illustrative value": "Historical active replay",
            "Purpose": "Shows whether the session was training, replay, or future real-time simulation.",
        },
        {
            "Report item": "Starting equity",
            "Illustrative value": "$100,000",
            "Purpose": "Establishes the account baseline.",
        },
        {
            "Report item": "Ending equity",
            "Illustrative value": "$102,950",
            "Purpose": "Shows final total account value.",
        },
        {
            "Report item": "Buy-and-hold benchmark",
            "Illustrative value": "$104,600",
            "Purpose": "Compares active covered-call decisions with simply holding shares.",
        },
        {
            "Report item": "Rule benchmark",
            "Illustrative value": "$102,300",
            "Purpose": "Compares user decisions with a mechanical covered-call rule.",
        },
        {
            "Report item": "Premium collected",
            "Illustrative value": "$345",
            "Purpose": "Shows option income, while making clear it is not the same as total profit.",
        },
        {
            "Report item": "Missed upside",
            "Illustrative value": "$1,650",
            "Purpose": "Shows opportunity cost in a rising path.",
        },
        {
            "Report item": "Decision takeaway",
            "Illustrative value": "Useful income, but capped upside",
            "Purpose": "Summarizes the main lesson from the session.",
        },
    ]

    return pd.DataFrame(rows)


def build_report_preview_sections() -> pd.DataFrame:
    """
    Build a table of report sections for the paid report preview.
    """
    rows = [
        {
            "Section": "Session setup",
            "Contents": "Ticker, account size, risk tier, delta, DTE, rule settings, and data timestamp.",
            "Why it matters": "Makes the report reproducible.",
        },
        {
            "Section": "Trade log",
            "Contents": "Every simulated sell, close, roll, wait, and assignment event.",
            "Why it matters": "Shows the actual decisions that produced the result.",
        },
        {
            "Section": "Equity curve",
            "Contents": "Total equity over time, compared with benchmarks.",
            "Why it matters": "Prevents premium-only interpretation.",
        },
        {
            "Section": "Option impact",
            "Contents": "Premium collected, buyback costs, roll credits/debits, and open liability.",
            "Why it matters": "Shows whether option management helped or hurt.",
        },
        {
            "Section": "Benchmark comparison",
            "Contents": "Active simulation versus buy-and-hold and mechanical covered-call rules.",
            "Why it matters": "Shows whether active decisions added value.",
        },
        {
            "Section": "Training feedback",
            "Contents": "Decision-quality notes and possible lessons.",
            "Why it matters": "Turns the simulator into a learning tool.",
        },
    ]

    return pd.DataFrame(rows)


def build_sample_html_report() -> str:
    """
    Build an illustrative professional HTML report for download.
    """
    report = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Covered Call Simulator — Sample Session Report</title>
<style>
    :root {
        --ink: #1f2937;
        --muted: #5b6472;
        --line: #d9dee8;
        --soft: #f6f8fb;
        --accent: #244a7f;
        --accent-soft: #e8f1ff;
        --warn-soft: #fff8e8;
        --warn-line: #f1d48a;
    }

    body {
        margin: 0;
        padding: 0;
        background: #f2f4f8;
        color: var(--ink);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
        line-height: 1.55;
    }

    .page {
        max-width: 980px;
        margin: 36px auto;
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 18px;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        overflow: hidden;
    }

    .header {
        padding: 34px 42px;
        background: linear-gradient(135deg, #18345c 0%, #2d5f9f 100%);
        color: #ffffff;
    }

    .eyebrow {
        font-size: 13px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.82;
        margin-bottom: 10px;
    }

    h1 {
        margin: 0;
        font-size: 32px;
        line-height: 1.15;
        font-weight: 750;
    }

    .subtitle {
        margin-top: 12px;
        max-width: 760px;
        font-size: 16px;
        opacity: 0.92;
    }

    .content {
        padding: 34px 42px 42px 42px;
    }

    h2 {
        margin: 32px 0 12px 0;
        font-size: 21px;
        color: var(--accent);
        border-bottom: 1px solid var(--line);
        padding-bottom: 8px;
    }

    h2:first-child {
        margin-top: 0;
    }

    p {
        margin: 10px 0;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 18px 0 8px 0;
    }

    .card {
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--soft);
        padding: 16px;
    }

    .label {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 5px;
    }

    .value {
        font-size: 22px;
        font-weight: 760;
        color: var(--ink);
    }

    .note-box {
        border: 1px solid #b8d4ff;
        background: var(--accent-soft);
        border-radius: 14px;
        padding: 16px 18px;
        margin: 18px 0;
    }

    .warning-box {
        border: 1px solid var(--warn-line);
        background: var(--warn-soft);
        border-radius: 14px;
        padding: 16px 18px;
        margin: 18px 0;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0 22px 0;
        font-size: 14px;
    }

    th {
        text-align: left;
        background: #eef2f7;
        color: #263244;
        border: 1px solid var(--line);
        padding: 10px 12px;
    }

    td {
        border: 1px solid var(--line);
        padding: 10px 12px;
        vertical-align: top;
    }

    tr:nth-child(even) td {
        background: #fafbfe;
    }

    .footer {
        padding: 22px 42px;
        border-top: 1px solid var(--line);
        color: var(--muted);
        font-size: 13px;
        background: #fbfcfe;
    }

    @media print {
        body {
            background: #ffffff;
        }
        .page {
            margin: 0;
            border: none;
            box-shadow: none;
        }
    }
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <div class="eyebrow">Covered Call Simulator</div>
        <h1>Sample Session Report</h1>
        <div class="subtitle">
            Historical active replay training session for an illustrative covered-call simulation.
            This report is designed to summarize decisions, total-equity results, and training feedback.
        </div>
    </div>

    <div class="content">
        <h2>Session Setup</h2>
        <table>
            <tr><th>Field</th><th>Illustrative value</th></tr>
            <tr><td>Ticker</td><td>SPY</td></tr>
            <tr><td>Starting equity</td><td>$100,000</td></tr>
            <tr><td>Initial position</td><td>100 shares</td></tr>
            <tr><td>Target delta</td><td>0.30</td></tr>
            <tr><td>Target DTE</td><td>30</td></tr>
            <tr><td>Strategy mode</td><td>Active covered-call simulation</td></tr>
            <tr><td>Benchmarks</td><td>Buy and hold; mechanical covered-call rule</td></tr>
        </table>

        <h2>Session Summary</h2>
        <div class="summary-grid">
            <div class="card">
                <div class="label">Ending equity</div>
                <div class="value">$102,950</div>
            </div>
            <div class="card">
                <div class="label">Active return</div>
                <div class="value">+2.95%</div>
            </div>
            <div class="card">
                <div class="label">Premium collected</div>
                <div class="value">$345</div>
            </div>
            <div class="card">
                <div class="label">Missed upside</div>
                <div class="value">$1,650</div>
            </div>
        </div>

        <table>
            <tr><th>Comparison item</th><th>Illustrative value</th><th>Interpretation</th></tr>
            <tr>
                <td>Active simulation</td>
                <td>$102,950</td>
                <td>Total account value after simulated covered-call decisions.</td>
            </tr>
            <tr>
                <td>Buy-and-hold benchmark</td>
                <td>$104,600</td>
                <td>What the share position alone would have produced in this simplified path.</td>
            </tr>
            <tr>
                <td>Mechanical rule benchmark</td>
                <td>$102,300</td>
                <td>Illustrative result from a rule-based covered-call process.</td>
            </tr>
        </table>

        <div class="note-box">
            <strong>Main lesson:</strong>
            The active covered-call session generated income and outperformed the mechanical rule benchmark
            in this illustrative path, but it lagged buy-and-hold because the underlying rose strongly.
            This is the core covered-call tradeoff: income and structure in exchange for capped upside.
        </div>

        <h2>Decision Review</h2>
        <table>
            <tr><th>Decision</th><th>Result</th><th>Training note</th></tr>
            <tr>
                <td>Sold initial covered call</td>
                <td>Collected premium, but capped upside early.</td>
                <td>Entry timing matters when the underlying begins moving quickly.</td>
            </tr>
            <tr>
                <td>Rolled up and out</td>
                <td>Restored some upside room, but extended the obligation.</td>
                <td>A roll should be evaluated by total equity and future exposure, not only by net credit.</td>
            </tr>
            <tr>
                <td>Closed the short call</td>
                <td>Reduced short-call risk and restored flexibility.</td>
                <td>Closing can be useful when the remaining premium is small relative to future risk.</td>
            </tr>
            <tr>
                <td>Reviewed benchmarks</td>
                <td>Active simulation beat the mechanical rule but lagged buy-and-hold.</td>
                <td>Benchmark comparison prevents premium-only interpretation.</td>
            </tr>
        </table>

        <h2>Training Takeaway</h2>
        <p>
            Covered-call management is path-dependent. The same rule can feel very different when the user
            must make decisions without knowing the future. Repeated training sessions can help develop
            better discipline around strike choice, rolling, closing, and re-entry.
        </p>

        <div class="warning-box">
            <strong>Important:</strong>
            Premium collected is not the same as profit. A covered-call session should be judged by total
            equity, benchmark comparison, option liability, missed upside, and risk exposure.
        </div>
    </div>

    <div class="footer">
        This report is an illustrative simulation report. It is not financial advice, investment advice,
        or a trade recommendation. Simulated results are hypothetical and may not reflect real trading
        outcomes. Options involve risk and are not suitable for all investors.
    </div>
</div>
</body>
</html>
"""
    return report


def page_report_preview() -> None:
    """
    Public-facing preview of paid downloadable reports.
    """
    st.header("Report Preview")

    st.write(
        "A paid simulator should not end with only a chart on the screen. It "
        "should produce a clear session report that the user can save, review, "
        "and compare across repeated covered-call training sessions."
    )

    st.info(
        "The report should reinforce the main training principle: judge the "
        "session by total equity and benchmark comparison, not by premium "
        "collected alone."
    )

    st.markdown("### Sample report summary")

    report_summary_df = build_report_preview_summary()

    st.dataframe(
        report_summary_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Report sections")

    report_sections_df = build_report_preview_sections()

    st.dataframe(
        report_sections_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Example report interpretation")

    interpretation_col1, interpretation_col2 = st.columns(2)

    with interpretation_col1:
        with st.container(border=True):
            st.subheader("What the report should show")
            st.markdown(
                """
                - Ending total equity.
                - Buy-and-hold comparison.
                - Mechanical rule comparison.
                - Premium collected.
                - Missed upside.
                - Roll impact.
                - Decision-quality notes.
                """
            )

    with interpretation_col2:
        with st.container(border=True):
            st.subheader("What the report should prevent")
            st.markdown(
                """
                - Confusing premium with profit.
                - Ignoring buy-and-hold performance.
                - Ignoring option buyback costs.
                - Ignoring missed upside.
                - Treating a net-credit roll as automatically good.
                - Forgetting account-size constraints.
                """
            )

    st.markdown("### Download professional sample report")

    sample_report = build_sample_html_report()

    st.download_button(
        label="Download styled HTML session report",
        data=sample_report,
        file_name="covered_call_sample_session_report.html",
        mime="text/html",
        type="primary",
        use_container_width=True,
    )

    st.caption(
        "The HTML report uses browser-safe professional typography and spacing. "
        "A future paid version could also export PDF, CSV, or client-ready reports."
    )

    st.markdown("### Tier placement")

    tier_df = pd.DataFrame(
        [
            {
                "Report feature": "Styled HTML summary",
                "Free": "Preview only",
                "Individual / Pro": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Report feature": "Trade log export",
                "Free": "No",
                "Individual / Pro": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Report feature": "Equity curve export",
                "Free": "No",
                "Individual / Pro": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Report feature": "Training scorecard",
                "Free": "Preview only",
                "Individual / Pro": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Report feature": "Client-ready report",
                "Free": "No",
                "Individual / Pro": "No",
                "Future Professional": "Yes",
            },
        ]
    )

    st.dataframe(
        tier_df,
        width="stretch",
        hide_index=True,
    )

    display_public_disclaimer_short()


def page_contact_waitlist_preview() -> None:
    """
    Contact / Waitlist Preview page.
    """
    st.header("Contact / Waitlist Preview")

    st.write(
        "A commercial version of the site should include a simple way for "
        "interested users to signal what they care about most. This prototype "
        "page shows the intended layout without storing or sending any data."
    )

    st.warning(
        "Prototype only: this form does not submit, store, email, or transmit "
        "information. It is included to plan the public product workflow."
    )

    st.markdown("### What kind of user are you?")

    user_col1, user_col2 = st.columns(2)

    with user_col1:
        with st.container(border=True):
            st.subheader("Individual investor")
            st.write(
                "Likely interested in covered-call education, account-size "
                "screening, active training mode, and downloadable reports."
            )

    with user_col2:
        with st.container(border=True):
            st.subheader("Professional or educator")
            st.write(
                "Likely interested in training scenarios, client or classroom "
                "demonstrations, richer reports, and future real-time simulation."
            )

    st.markdown("### Prototype interest form")

    with st.form("contact_waitlist_preview_form"):
        name = st.text_input("Name", value="", placeholder="Optional")
        email = st.text_input("Email", value="", placeholder="Optional in this prototype")

        user_type = st.selectbox(
            "User type",
            options=[
                "Individual investor",
                "Retired or semi-retired investor",
                "Advisor",
                "Educator",
                "Research / newsletter provider",
                "Asset manager / professional user",
                "Other",
            ],
            index=0,
        )

        interests = st.multiselect(
            "Most interesting features",
            options=[
                "Free simulator preview",
                "Configurable paid simulator",
                "Active covered-call training",
                "Historical replay",
                "Downloadable reports",
                "Account-size tradability screening",
                "Market-regime comparison",
                "Future real-time active simulation",
                "Professional / client-ready reports",
            ],
            default=[
                "Active covered-call training",
                "Downloadable reports",
            ],
        )

        preferred_tier = st.selectbox(
            "Likely tier of interest",
            options=[
                "Free preview",
                "Individual / Pro",
                "Future Professional",
                "Not sure yet",
            ],
            index=1,
        )

        comments = st.text_area(
            "What problem would you want this tool to solve?",
            value="",
            placeholder=(
                "Example: I want to practice rolling covered calls without "
                "risking capital, or compare 0.30 delta versus 0.20 delta "
                "covered-call rules."
            ),
            height=130,
        )

        submitted = st.form_submit_button(
            "Preview waitlist submission",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        st.success(
            "Prototype submission generated. In a deployed version, this would "
            "be sent to a secure waitlist or CRM system after proper privacy "
            "and consent handling."
        )

        summary_df = pd.DataFrame(
            [
                {
                    "Field": "Name",
                    "Preview value": name if name else "(not provided)",
                },
                {
                    "Field": "Email",
                    "Preview value": email if email else "(not provided)",
                },
                {
                    "Field": "User type",
                    "Preview value": user_type,
                },
                {
                    "Field": "Likely tier",
                    "Preview value": preferred_tier,
                },
                {
                    "Field": "Selected interests",
                    "Preview value": ", ".join(interests) if interests else "(none selected)",
                },
                {
                    "Field": "Problem statement",
                    "Preview value": comments if comments else "(not provided)",
                },
            ]
        )

        st.dataframe(
            summary_df,
            width="stretch",
            hide_index=True,
        )

    st.markdown("### What this page would help validate")

    validation_df = pd.DataFrame(
        [
            {
                "Question": "Do users care more about education or simulation?",
                "Why it matters": "Determines whether the product should lead with training mode or rule comparison.",
            },
            {
                "Question": "Do users want historical replay?",
                "Why it matters": "Historical replay may be the strongest Individual / Pro feature.",
            },
            {
                "Question": "Do users want real-time active simulation?",
                "Why it matters": "Real-time simulation is more expensive to build and likely belongs in Future Professional.",
            },
            {
                "Question": "Do users value downloadable reports?",
                "Why it matters": "Reports can make the product feel more professional and repeat-use.",
            },
            {
                "Question": "Are professional users interested?",
                "Why it matters": "Advisor, educator, and asset-manager interest would affect the future roadmap.",
            },
        ]
    )

    st.dataframe(
        validation_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Privacy note for future deployment")

    with st.container(border=True):
        st.write(
            "A real waitlist page should include privacy language, consent "
            "handling, spam protection, secure storage, unsubscribe options, "
            "and a clear statement about how contact information will be used."
        )

    display_public_disclaimer_short()


def page_product_roadmap() -> None:
    """
    Product Roadmap page.
    """
    st.header("Product Roadmap")

    st.write(
        "The roadmap separates what the public prototype already demonstrates "
        "from what should be built for the first real product and what should "
        "wait for a future professional version."
    )

    st.info(
        "The recommended build order is: prove the public product story first, "
        "then connect the configurable simulator, then add active training and "
        "reports, and only later consider real-time professional simulation."
    )

    st.markdown("### Roadmap phases")

    roadmap_df = pd.DataFrame(
        [
            {
                "Phase": "1. Public prototype",
                "Status": "Current",
                "Primary goal": "Explain the product story and validate user interest.",
                "Main features": "Home, How It Works, FAQ, previews, pricing, disclaimers, waitlist.",
            },
            {
                "Phase": "2. Free simulator preview",
                "Status": "Near-term",
                "Primary goal": "Offer a useful educational preview with fixed assumptions.",
                "Main features": "Preset tickers, fixed account size, basic rule comparison, account-size screen.",
            },
            {
                "Phase": "3. Individual / Pro simulator",
                "Status": "Core paid build",
                "Primary goal": "Let users configure their own covered-call assumptions.",
                "Main features": "Custom ticker, account size, risk tier, delta, DTE, strike method, rule comparison.",
            },
            {
                "Phase": "4. Active historical training",
                "Status": "Core paid differentiator",
                "Primary goal": "Turn the simulator into a repeat-use training tool.",
                "Main features": "Historical replay, simulated CC placement, close, roll, wait, assignment handling.",
            },
            {
                "Phase": "5. Reports and saved sessions",
                "Status": "Paid retention feature",
                "Primary goal": "Give users reviewable outputs and encourage repeat practice.",
                "Main features": "Styled reports, scorecards, trade logs, equity curves, benchmark comparison.",
            },
            {
                "Phase": "6. Future Professional",
                "Status": "Later",
                "Primary goal": "Support professional demonstrations and richer analytics.",
                "Main features": "Real-time active simulation, option-chain updates, saved client sessions, client-ready reports.",
            },
            {
                "Phase": "7. Institutional research engine",
                "Status": "Possible long-term",
                "Primary goal": "Support deeper rule testing and overlay-strategy research.",
                "Main features": "Historical option-chain replay, parameter sweeps, regime analytics, portfolio overlays.",
            },
        ]
    )

    st.dataframe(
        roadmap_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### What should be built first")

    first_col1, first_col2 = st.columns(2)

    with first_col1:
        with st.container(border=True):
            st.subheader("Build before launch")
            st.markdown(
                """
                - Stable public site structure.
                - Clear product positioning.
                - Fixed-assumption free preview.
                - Account-size tradability logic.
                - Basic rule comparison.
                - Strong disclaimers.
                - Contact / waitlist capture.
                """
            )

    with first_col2:
        with st.container(border=True):
            st.subheader("Do not overbuild yet")
            st.markdown(
                """
                - Real-time trading engine.
                - Broker integration.
                - Institutional analytics.
                - Complex portfolio optimizer.
                - Live option-chain infrastructure.
                - Client-ready professional portal.
                """
            )

    st.markdown("### First paid product requirements")

    paid_requirements_df = pd.DataFrame(
        [
            {
                "Requirement": "Custom ticker support",
                "Why it matters": "Users need to test the stocks or ETFs they actually trade.",
                "Build note": "Must verify ticker validity, optionability, and data availability.",
            },
            {
                "Requirement": "Account-aware sizing",
                "Why it matters": "A ticker can be too large for a user's account even if it is optionable.",
                "Build note": "Use 100-share contract requirement and selected position-size cap.",
            },
            {
                "Requirement": "Option assumptions",
                "Why it matters": "Delta, DTE, and strike-selection method strongly affect results.",
                "Build note": "Expose these as paid controls.",
            },
            {
                "Requirement": "Rule comparison",
                "Why it matters": "Users need to compare hold, close, wait, and adaptive logic.",
                "Build note": "Keep results benchmarked and scenario-based.",
            },
            {
                "Requirement": "Historical active replay",
                "Why it matters": "This is the main training differentiator.",
                "Build note": "User should make decisions without seeing future data.",
            },
            {
                "Requirement": "Downloadable reports",
                "Why it matters": "Reports make the product feel professional and repeat-use.",
                "Build note": "Start with styled HTML, later add PDF and CSV.",
            },
        ]
    )

    st.dataframe(
        paid_requirements_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Future Professional criteria")

    pro_col1, pro_col2 = st.columns(2)

    with pro_col1:
        with st.container(border=True):
            st.subheader("Only build after paid core works")
            st.write(
                "Real-time active simulation should wait until the historical "
                "training product is stable. It requires more data, more state "
                "management, and more careful user expectations."
            )

    with pro_col2:
        with st.container(border=True):
            st.subheader("Why it may justify a higher tier")
            st.write(
                "Near-real-time price and option-chain updates, saved sessions, "
                "client demonstrations, and richer reports are more valuable to "
                "advisors, educators, and professional users than to casual "
                "visitors."
            )

    st.markdown("### Launch-readiness checklist")

    checklist_df = pd.DataFrame(
        [
            {
                "Area": "Product clarity",
                "Launch question": "Can a first-time visitor understand the product in under one minute?",
                "Readiness target": "Home, How It Works, FAQ, and tour are clear.",
            },
            {
                "Area": "Simulation correctness",
                "Launch question": "Do rule comparisons and account-size screens produce consistent results?",
                "Readiness target": "Tested against known examples and edge cases.",
            },
            {
                "Area": "Data reliability",
                "Launch question": "Are timestamps, missing data, stale data, and quote status handled clearly?",
                "Readiness target": "Every data-driven result shows source/timing status.",
            },
            {
                "Area": "Disclaimers",
                "Launch question": "Is it clear this is education and paper simulation only?",
                "Readiness target": "Disclaimers appear on key pages and reports.",
            },
            {
                "Area": "User feedback",
                "Launch question": "Do early users understand and want the product?",
                "Readiness target": "Waitlist responses show interest in paid features.",
            },
            {
                "Area": "Payment readiness",
                "Launch question": "Are tiers and feature boundaries clear enough to charge?",
                "Readiness target": "Free versus Individual / Pro versus Future Professional are distinct.",
            },
        ]
    )

    st.dataframe(
        checklist_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Recommended next business step")

    with st.container(border=True):
        st.write(
            "Before building the real-time professional version, validate the "
            "individual paid product: configurable assumptions, historical "
            "active replay, total-equity feedback, and professional reports."
        )

        st.success(
            "The near-term commercial thesis is not prediction. It is covered-call "
            "training, decision practice, and account-aware simulation."
        )

    display_public_disclaimer_short()


def page_pricing() -> None:
    """
    Pricing page.
    """
    st.header("Pricing")

    st.write(
        "The first public version should keep pricing simple. The free version "
        "teaches the concept with fixed assumptions. The individual paid "
        "version unlocks configurability, account-aware analysis, custom "
        "tickers, option-selection controls, reports, and replay practice."
    )

    st.warning(
        "Pricing is not implemented in this prototype. This page defines the "
        "planned product tiers and feature boundaries."
    )

    st.markdown("### Product tiers")

    free_col, paid_col, pro_col = st.columns(3)

    with free_col:
        with st.container(border=True):
            st.subheader("Free")
            st.write("Educational preview with fixed assumptions.")
            st.markdown(
                """
                **Best for**

                - Learning the simulator concept.
                - Comparing basic covered-call rules.
                - Understanding account-size constraints.

                **Includes**

                - Preset tickers.
                - Fixed USD 100,000 account.
                - Fixed Balanced risk tier.
                - Fixed 0.30 delta.
                - Fixed 30 DTE.
                - Basic rule comparison.
                - Simple Markdown report.
                """
            )

    with paid_col:
        with st.container(border=True):
            st.subheader("Individual / Pro")
            st.write("Configurable covered-call simulator with historical active replay.")
            st.markdown(
                """
                **Best for**

                - Investors who already trade or study covered calls.
                - Users who want to test their own assumptions.
                - Users who want account-aware ticker screening.

                **Includes**

                - Custom stock or ETF ticker.
                - Optionability and liquidity screen.
                - Custom account size.
                - Risk-tier selection.
                - User-selected delta and DTE.
                - Strike-selection method.
                - Rolling and re-entry rules.
                - Exportable reports.
                - Historical replay simulator.
                - Active simulated CC decisions on past paths.
                - Moving total-equity plot.
                """
            )

    with pro_col:
        with st.container(border=True):
            st.subheader("Future Professional")
            st.write("Advanced tools for advisors, educators, or researchers.")
            st.markdown(
                """
                **Possible future features**

                - Portfolio-level simulations.
                - Batch ticker screening.
                - Saved scenarios.
                - Client-ready reports.
                - Custom rule design.
                - Historical option-chain analysis.
                - Real-time active CC simulation.
                - Intraday price and option-chain updates.
                - More export formats.
                """
            )

    st.markdown("### Feature comparison")

    feature_df = pd.DataFrame(
        [
            {
                "Feature": "Basic covered-call education",
                "Free": "Yes",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Preset ticker list",
                "Free": "Yes",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Custom stock or ETF ticker",
                "Free": "No",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Custom account size",
                "Free": "No",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "User-selected delta and DTE",
                "Free": "No",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Optionability and liquidity checks",
                "Free": "No",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Account-size tradability screen",
                "Free": "Limited",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Rule comparison",
                "Free": "Limited",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Historical replay simulator",
                "Free": "Preview only",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Active simulated CC placement",
                "Free": "Preview only",
                "Individual": "Historical replay",
                "Future Professional": "Real-time / intraday",
            },
            {
                "Feature": "Real-time price and option-chain simulation",
                "Free": "No",
                "Individual": "No",
                "Future Professional": "Possible",
            },
            {
                "Feature": "Moving total-equity plot",
                "Free": "Illustrative",
                "Individual": "Yes",
                "Future Professional": "Yes",
            },
            {
                "Feature": "Downloadable reports",
                "Free": "Simple Markdown",
                "Individual": "Yes",
                "Future Professional": "Client-ready",
            },
            {
                "Feature": "Batch ticker screening",
                "Free": "No",
                "Individual": "No",
                "Future Professional": "Possible",
            },
        ]
    )

    st.dataframe(
        feature_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Why users would pay")

    reason_col1, reason_col2 = st.columns(2)

    with reason_col1:
        with st.container(border=True):
            st.subheader("Configurability")
            st.write(
                "Covered-call users do not all trade the same way. The paid "
                "version should let them test their own ticker, account size, "
                "risk tier, delta, DTE, strike-selection method, and rolling "
                "rules."
            )

    with reason_col2:
        with st.container(border=True):
            st.subheader("Realism")
            st.write(
                "Custom tickers, liquidity checks, total-equity curves, "
                "active CC placement, rolling decisions, and replay practice "
                "make the paid version feel like a workflow tool rather than "
                "a static educational page."
            )

    st.markdown("### Paid-version principle")

    st.success(
        "Free version = educational preview with fixed assumptions. "
        "Paid version = configurable simulator with account-aware, "
        "option-aware, and replay-based analysis."
    )

    st.info(
        "The product should not charge for predictions. It should charge for "
        "configurability, workflow depth, reports, and decision practice."
    )

    display_public_disclaimer_short()


def page_disclaimers() -> None:
    """
    Disclaimers page.
    """
    st.header("Disclaimers")

    st.warning(
        "The Covered Call Simulator is an educational, analytical, and "
        "training-oriented simulation tool. It is not financial advice, "
        "investment advice, tax advice, legal advice, or a trade recommendation."
    )

    st.markdown("### Core disclaimer")

    with st.container(border=True):
        st.write(
            "The simulator is designed to help users study covered-call "
            "tradeoffs, compare rules, practice decisions, and review "
            "hypothetical outcomes. It does not determine whether a user should "
            "buy, sell, hold, write, close, roll, or exercise any security or "
            "option contract."
        )

    st.markdown("### Paper simulation only")

    paper_df = pd.DataFrame(
        [
            {
                "Topic": "No real trade placement",
                "Explanation": "Buttons such as Sell covered call, Close, Roll, or Wait are simulation controls only. They do not place orders with a broker.",
            },
            {
                "Topic": "No brokerage connection",
                "Explanation": "The public prototype does not connect to a brokerage account, submit trades, manage orders, or alter real positions.",
            },
            {
                "Topic": "Training environment",
                "Explanation": "Training Mode is intended to help users practice decision-making without capital at risk.",
            },
            {
                "Topic": "Future real-time mode",
                "Explanation": "Any future real-time or near-real-time mode should still be presented as paper simulation unless explicitly built and licensed as something else.",
            },
        ]
    )

    st.dataframe(
        paper_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Hypothetical and simulated results")

    result_col1, result_col2 = st.columns(2)

    with result_col1:
        with st.container(border=True):
            st.subheader("What simulated results can show")
            st.markdown(
                """
                - Rule behavior under selected assumptions.
                - Covered-call tradeoffs.
                - Premium versus capped upside.
                - Benchmark comparison.
                - Path dependence.
                - Decision-quality feedback.
                """
            )

    with result_col2:
        with st.container(border=True):
            st.subheader("What simulated results cannot prove")
            st.markdown(
                """
                - Future profitability.
                - Future market direction.
                - Actual fill prices.
                - Actual tax treatment.
                - Actual assignment behavior.
                - Guaranteed income.
                """
            )

    st.info(
        "Simulated results are hypothetical. They may differ materially from "
        "real trading results because real markets include bid/ask spreads, "
        "slippage, commissions, liquidity constraints, assignment behavior, "
        "tax effects, emotional decision pressure, and changing volatility."
    )

    st.markdown("### Options risk")

    options_risk_df = pd.DataFrame(
        [
            {
                "Risk": "Underlying loss",
                "Explanation": "A covered call still owns the underlying. If the stock or ETF falls, the position can lose money.",
            },
            {
                "Risk": "Capped upside",
                "Explanation": "If the underlying rises strongly, the short call can limit gains or cause shares to be called away.",
            },
            {
                "Risk": "Assignment",
                "Explanation": "Short calls can be assigned. Assignment timing may depend on moneyness, dividends, expiration, and market behavior.",
            },
            {
                "Risk": "Rolling risk",
                "Explanation": "Rolling may extend risk, increase exposure, reduce future flexibility, or create misleading comfort if judged only by net credit.",
            },
            {
                "Risk": "Liquidity and fills",
                "Explanation": "A displayed mid-price or simulated price may not be achievable in live trading.",
            },
            {
                "Risk": "Tax consequences",
                "Explanation": "Option trades, assignment, and share sales may have tax effects that depend on the user's situation.",
            },
        ]
    )

    st.dataframe(
        options_risk_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Data timing and market-regime limitations")

    data_col1, data_col2 = st.columns(2)

    with data_col1:
        with st.container(border=True):
            st.subheader("Data timing")
            st.write(
                "Current-price, option-chain, and market-regime information may "
                "be delayed, incomplete, stale, or unavailable. Any data "
                "timestamp should be shown clearly wherever possible."
            )

    with data_col2:
        with st.container(border=True):
            st.subheader("Regime detection")
            st.write(
                "Market-regime labels are scenario inputs and probabilistic "
                "guides, not predictions. Regime detection is not an oracle and "
                "should not be treated as a trading signal."
            )

    st.markdown("### Training-mode limitations")

    training_limit_df = pd.DataFrame(
        [
            {
                "Training feature": "Moving price demo",
                "Limitation": "Illustrative animation only. It is not a forecast and not necessarily based on live market data.",
            },
            {
                "Training feature": "Option-chain placement panel",
                "Limitation": "Illustrative candidates may not represent real available options or executable prices.",
            },
            {
                "Training feature": "Pre-trade impact preview",
                "Limitation": "Simplified estimates may omit slippage, fees, taxes, volatility changes, and liquidity constraints.",
            },
            {
                "Training feature": "Scorecard and decision notes",
                "Limitation": "Feedback is educational and should not be interpreted as personalized investment advice.",
            },
            {
                "Training feature": "Downloadable reports",
                "Limitation": "Reports summarize hypothetical simulation output and should not be treated as verified investment performance.",
            },
        ]
    )

    st.dataframe(
        training_limit_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Plain-English summary")

    with st.container(border=True):
        st.write(
            "Use the simulator to learn, compare, practice, and ask better "
            "questions. Do not use it as a substitute for your own judgment, "
            "professional advice, broker-provided risk disclosures, or a "
            "complete understanding of options risk."
        )

    st.markdown("### Short disclaimer text")

    st.code(
        "The Covered Call Simulator is an educational and analytical tool. "
        "It is not financial advice, investment advice, tax advice, legal "
        "advice, or a trade recommendation. Simulated results are hypothetical "
        "and may not reflect actual trading outcomes. Options involve risk and "
        "are not suitable for all investors. Training-mode actions are paper "
        "simulation only and do not place real trades.",
        language="text",
    )


def page_about() -> None:
    """
    About page.
    """
    st.header("About the Covered Call Simulator")

    st.write(
        "The Covered Call Simulator is being built to answer a practical "
        "question: how do covered-call decisions behave when account size, "
        "option assumptions, market path, volatility, and trade-management "
        "rules are all made explicit?"
    )

    st.info(
        "The project is not designed to predict tomorrow's market. It is "
        "designed to help users understand covered-call tradeoffs and practice "
        "better decision processes."
    )

    st.markdown("### Product philosophy")

    philosophy_df = pd.DataFrame(
        [
            {
                "Principle": "Training before trading",
                "Meaning": "Users should be able to practice covered-call decisions before risking capital.",
            },
            {
                "Principle": "Total equity over premium",
                "Meaning": "Premium collected is visible, but total account equity determines whether the decision helped.",
            },
            {
                "Principle": "Scenario comparison, not prediction",
                "Meaning": "Market regimes and replay paths are used to compare behavior, not to forecast outcomes.",
            },
            {
                "Principle": "Account-aware analysis",
                "Meaning": "A ticker may be technically optionable but still impractical for a given account size.",
            },
            {
                "Principle": "Decision transparency",
                "Meaning": "The simulator should show why a rule or action helped, hurt, capped upside, or changed risk.",
            },
        ]
    )

    st.dataframe(
        philosophy_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### What makes the product different")

    diff_col1, diff_col2 = st.columns(2)

    with diff_col1:
        with st.container(border=True):
            st.subheader("Not just a static backtest")
            st.write(
                "A static backtest shows what happened after the fact. The "
                "training simulator should let users make decisions as the path "
                "unfolds, without knowing the future."
            )

    with diff_col2:
        with st.container(border=True):
            st.subheader("Not a trade signal service")
            st.write(
                "The product should not say 'buy this' or 'sell that.' It "
                "should help users compare assumptions, understand tradeoffs, "
                "and practice covered-call management."
            )

    st.markdown("### Core product components")

    component_df = pd.DataFrame(
        [
            {
                "Component": "Free simulator preview",
                "Purpose": "Demonstrates basic rule comparison and account-size logic using fixed assumptions.",
            },
            {
                "Component": "Paid configurable simulator",
                "Purpose": "Lets users choose ticker, account size, risk tier, delta, DTE, and management rules.",
            },
            {
                "Component": "Active CC simulation",
                "Purpose": "Lets users practice selecting calls, placing simulated covered calls, rolling, closing, waiting, and reviewing results.",
            },
            {
                "Component": "Training mode",
                "Purpose": "Organizes covered-call learning into beginner, intermediate, advanced, and future professional practice scenarios.",
            },
            {
                "Component": "Report output",
                "Purpose": "Summarizes setup, decisions, total equity, benchmark comparison, premium collected, missed upside, and lessons learned.",
            },
        ]
    )

    st.dataframe(
        component_df,
        width="stretch",
        hide_index=True,
    )

    st.markdown("### Intended users")

    user_col1, user_col2 = st.columns(2)

    with user_col1:
        with st.container(border=True):
            st.subheader("Individual investors")
            st.markdown(
                """
                - Covered-call learners.
                - Income-focused ETF investors.
                - Retired or semi-retired investors.
                - Users who want to practice before trading.
                - Users who want to compare rules and assumptions.
                """
            )

    with user_col2:
        with st.container(border=True):
            st.subheader("Potential professional users")
            st.markdown(
                """
                - Advisors explaining option overlays.
                - Educators teaching covered-call tradeoffs.
                - Newsletter or research providers.
                - Small asset managers testing overlay logic.
                - Future institutional users of a deeper research engine.
                """
            )

    st.markdown("### Current development direction")

    direction_col1, direction_col2, direction_col3 = st.columns(3)

    with direction_col1:
        with st.container(border=True):
            st.subheader("Now")
            st.write(
                "Build a clear public prototype that explains the value of the "
                "simulator, training mode, and report workflow."
            )

    with direction_col2:
        with st.container(border=True):
            st.subheader("Next")
            st.write(
                "Connect the public interface to a stronger configurable "
                "simulation engine with account-aware and option-aware inputs."
            )

    with direction_col3:
        with st.container(border=True):
            st.subheader("Later")
            st.write(
                "Develop historical replay, real-time paper simulation, saved "
                "sessions, richer reports, and possibly professional analytics."
            )

    st.markdown("### Important boundaries")

    boundary_df = pd.DataFrame(
        [
            {
                "Boundary": "No guarantee",
                "Explanation": "The simulator cannot guarantee income, outperformance, or future results.",
            },
            {
                "Boundary": "No market oracle",
                "Explanation": "Regime labels are probabilistic scenario inputs, not predictive signals.",
            },
            {
                "Boundary": "No real order placement",
                "Explanation": "Training-mode actions are paper simulation only.",
            },
            {
                "Boundary": "No premium-only scoring",
                "Explanation": "Results should be judged by total equity, benchmark comparison, and risk exposure.",
            },
        ]
    )

    st.dataframe(
        boundary_df,
        width="stretch",
        hide_index=True,
    )

    with st.container(border=True):
        st.write(
            "In short: the Covered Call Simulator is being shaped into a "
            "covered-call training system. It is meant to help users learn how "
            "covered-call decisions behave before those decisions involve real "
            "capital."
        )

    display_public_disclaimer_short()


def page_docs_preview() -> None:
    """
    Optional page that previews planning documents if they exist.
    """
    st.header("Planning Documents Preview")

    selected_doc = st.selectbox(
        "Document",
        options=[
            "Website plan",
            "Landing page copy",
            "Free vs paid features",
            "Public disclaimer",
            "Development roadmap",
            "Simulator workflow",
        ],
    )

    path_map = {
        "Website plan": WEBSITE_PLAN_PATH,
        "Landing page copy": LANDING_PAGE_COPY_PATH,
        "Free vs paid features": FREE_VS_PAID_PATH,
        "Public disclaimer": PUBLIC_DISCLAIMER_PATH,
        "Development roadmap": DEVELOPMENT_ROADMAP_PATH,
        "Simulator workflow": SIMULATOR_WORKFLOW_PATH,
    }

    selected_path = path_map[selected_doc]
    markdown_text = load_markdown_file(selected_path)

    if markdown_text:
        st.markdown(markdown_text)
    else:
        st.warning(
            f"{selected_path.relative_to(PROJECT_ROOT)} was not found."
        )


# =============================================================================
# Main app
# =============================================================================

def main() -> None:
    """
    Run the public site prototype.
    """
    inject_public_site_css()

    st.sidebar.title("Covered Call Simulator")
    st.sidebar.caption("Public website prototype")

    navigation_sections = {
        "Start Here": [
            "Home",
            "How It Works",
            "FAQ",
        ],
        "Product": [
            "Product Roadmap",
            "Pricing",
            "Contact / Waitlist Preview",
        ],
        "Simulator Previews": [
            "Free Simulator Preview",
            "Paid Simulator Preview",
            "Active CC Simulation Preview",
            "Replay Simulator Preview",
        ],
        "Training / Reports": [
            "Training Mode Preview",
            "Report Preview",
        ],
        "Education": [
            "Strategies Compared",
            "Account Sizing",
            "Market Regimes",
        ],
        "Legal": [
            "Disclaimers",
            "About",
        ],
        "Developer Docs": [
            "Planning Docs Preview",
        ],
    }

    selected_section = st.sidebar.radio(
        "Section",
        options=list(navigation_sections.keys()),
        index=0,
    )

    selected_page = st.sidebar.radio(
        "Page",
        options=navigation_sections[selected_section],
        index=0,
    )

    st.sidebar.markdown("---")

    st.sidebar.markdown("### Recommended Tour")
    st.sidebar.markdown(
        """
        1. **How It Works**  
           Understand the full workflow.

        2. **Active CC Simulation Preview**  
           See the interactive training concept.

        3. **Training Mode Preview**  
           See the learning path.

        4. **Report Preview**  
           See the paid-user report output.

        5. **Product Roadmap**  
           See the recommended build sequence.

        6. **Pricing**  
           Review Free, Individual / Pro, and Future Professional tiers.

        7. **Contact / Waitlist Preview**  
           Show how user interest could be captured.
        """
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "Select a section first, then choose a page. This public-site "
        "prototype is separate from the internal dashboard."
    )

    if selected_page == "Home":
        page_home()
    elif selected_page == "How It Works":
        page_how_it_works()
    elif selected_page == "FAQ":
        page_faq()
    elif selected_page == "Free Simulator Preview":
        page_free_simulator_preview()
    elif selected_page == "Paid Simulator Preview":
        page_paid_simulator_preview()
    elif selected_page == "Active CC Simulation Preview":
        page_active_cc_simulation_preview()
    elif selected_page == "Training Mode Preview":
        page_training_mode_preview()
    elif selected_page == "Report Preview":
        page_report_preview()
    elif selected_page == "Strategies Compared":
        page_strategies_compared()
    elif selected_page == "Account Sizing":
        page_account_sizing()
    elif selected_page == "Market Regimes":
        page_market_regimes()
    elif selected_page == "Replay Simulator Preview":
        page_replay_simulator_preview()
    elif selected_page == "Pricing":
        page_pricing()
    elif selected_page == "Product Roadmap":
        page_product_roadmap()
    elif selected_page == "Contact / Waitlist Preview":
        page_contact_waitlist_preview()
    elif selected_page == "Disclaimers":
        page_disclaimers()
    elif selected_page == "About":
        page_about()
    elif selected_page == "Planning Docs Preview":
        page_docs_preview()

    st.markdown("---")
    display_public_disclaimer_short()


if __name__ == "__main__":
    main()
