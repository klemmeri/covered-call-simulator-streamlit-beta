"""
public_site/app.py

Public-facing Streamlit prototype for the Covered Call Simulator.

Version 2
---------
This version keeps the public website shell, but improves the Free Simulator
Preview page so it can read existing simulator output files when available.

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

from pathlib import Path
import re

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
            ("Regime", "Detected regime"),
            ("Practical_Rule", "Practical rule"),
            ("Rule", "Practical rule"),
            ("Date", "Regime date"),
            ("Market_Date", "Regime market date"),
        ]:
            if possible_column in first_regime_row:
                rows.append(
                    {
                        "Item": label,
                        "Value": first_regime_row[possible_column],
                    }
                )

    return pd.DataFrame(rows)


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
            <h1>Test covered-call rules before risking capital.</h1>
            <p>
                Compare covered-call management rules across account sizes,
                ETFs, option-selection assumptions, and market-regime scenarios
                using a practical simulator built for income-focused investors.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hero_col1, hero_col2 = st.columns([1.15, 0.85])

    with hero_col1:
        st.subheader("What this simulator is for")
        st.write(
            "The Covered Call Simulator helps investors compare covered-call "
            "rules before committing real capital. It is designed to show how "
            "management choices such as holding to expiration, closing early, "
            "waiting before re-entry, or rolling can affect total equity."
        )

        st.write(
            "The key idea is simple: option premium matters, but total equity "
            "matters more. A covered-call strategy should be judged by the "
            "combined effect of stock value, option value, cash, realized P/L, "
            "missed upside, and drawdown."
        )

        display_badges(
            [
                "Rule comparison",
                "Account sizing",
                "Delta and DTE",
                "Market regimes",
                "Replay practice",
                "Total equity curve",
            ]
        )

    with hero_col2:
        with st.container(border=True):
            st.subheader("Core product message")
            st.success(
                "Compare covered-call decisions before risking capital."
            )
            st.markdown(
                "**Not a signal service.** The simulator is a research and "
                "education tool, not a black-box recommendation engine."
            )
            st.markdown(
                "**Not just income.** Premium collected is not the same as "
                "profit. Watch total equity."
            )

    st.markdown("---")

    st.subheader("What users can compare")

    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        display_feature_card(
            "Management rules",
            "Compare hold-to-expiration, close-at-50%, wait-before-reentry, "
            "and adaptive regime-based covered-call rules.",
        )

    with feature_col2:
        display_feature_card(
            "Account-aware tradability",
            "Estimate whether one covered-call contract is practical under "
            "the selected account size and position-size limits.",
        )

    with feature_col3:
        display_feature_card(
            "Option-selection assumptions",
            "Paid users should be able to test target delta, DTE, strike "
            "selection, rolling rules, and transaction-cost assumptions.",
        )

    feature_col4, feature_col5, feature_col6 = st.columns(3)

    with feature_col4:
        display_feature_card(
            "Custom tickers",
            "Paid users should be able to test any stock or ETF with listed, "
            "liquid options, subject to optionability and liquidity checks.",
        )

    with feature_col5:
        display_feature_card(
            "Market regimes",
            "Use regime labels as scenario inputs. Regime detection is "
            "probabilistic guidance, not an oracle.",
        )

    with feature_col6:
        display_feature_card(
            "Replay simulator",
            "Practice covered-call decisions on a historical price path "
            "without seeing the future.",
        )

    st.markdown("---")

    cta_col1, cta_col2 = st.columns(2)

    with cta_col1:
        with st.container(border=True):
            st.subheader("Try the free simulator preview")
            st.write(
                "Start with preset tickers and fixed assumptions to see how "
                "basic covered-call rules compare."
            )
            st.info(
                "Use the sidebar to open the Free Simulator Preview page."
            )

    with cta_col2:
        with st.container(border=True):
            st.subheader("Paid version direction")
            st.write(
                "The paid version should unlock custom tickers, custom account "
                "size, delta, DTE, rolling assumptions, exportable reports, "
                "and historical replay."
            )
            st.warning(
                "Paid features are planned. This prototype is only a public "
                "website shell."
            )

    display_public_disclaimer_short()


def page_how_it_works() -> None:
    """
    How It Works page.
    """
    st.header("How It Works")

    st.write(
        "The simulator is designed to compare covered-call decisions in a "
        "structured way. It separates account-size practicality, option "
        "selection, management rules, market-regime scenarios, and total "
        "equity behavior."
    )

    steps = [
        (
            "1. Choose a ticker",
            "Start with a preset ticker in the free version, or enter any "
            "optionable and liquid stock or ETF in the paid version.",
        ),
        (
            "2. Choose account assumptions",
            "Select account size and risk tier. The simulator estimates "
            "whether one covered-call contract is practical.",
        ),
        (
            "3. Choose option parameters",
            "Paid users should be able to select target delta, DTE, strike "
            "method, transaction costs, and liquidity constraints.",
        ),
        (
            "4. Choose management rules",
            "Compare rules such as hold to expiration, close at 50%, wait "
            "before re-entry, roll when ITM, or adaptive regime rules.",
        ),
        (
            "5. Compare outcomes",
            "Review total return, premium collected, missed upside, drawdown, "
            "assignment events, roll events, and total equity.",
        ),
        (
            "6. Interpret cautiously",
            "The simulator provides scenario analysis and decision practice, "
            "not a trade recommendation.",
        ),
    ]

    for title, body in steps:
        with st.container(border=True):
            st.subheader(title)
            st.write(body)

    st.markdown("---")

    st.subheader("Important concepts")

    concept_col1, concept_col2 = st.columns(2)

    with concept_col1:
        st.markdown("### Tradability")
        st.write(
            "Tradable means the ticker passes the selected account-size and "
            "position-size screen. It does not mean the ticker is recommended."
        )

        st.markdown("### Regime labels")
        st.write(
            "Regime labels are scenario inputs based on completed data. They "
            "are not market predictions."
        )

    with concept_col2:
        st.markdown("### Total equity")
        st.write(
            "A covered-call strategy should be evaluated using total equity, "
            "not premium collected alone."
        )

        st.markdown("### Replay practice")
        st.write(
            "Replay mode should eventually let users practice decisions on "
            "historical price paths without seeing the future."
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

        if not rule_df.empty:
            st.success(
                f"Loaded available simulator output: {source_label}"
            )
            st.dataframe(
                clean_dataframe_for_display(rule_df),
                width="stretch",
                hide_index=True,
            )
        else:
            st.warning(
                "No suitable rule-comparison CSV was found in "
                "outputs/tables/comparison. Showing illustrative placeholder "
                "results instead."
            )

            placeholder_df = build_free_preview_placeholder_results()

            st.dataframe(
                placeholder_df,
                width="stretch",
                hide_index=True,
            )

        st.markdown("### Current snapshot")

        snapshot_df = build_current_snapshot_table(ticker)

        if not snapshot_df.empty:
            st.dataframe(
                snapshot_df,
                width="stretch",
                hide_index=True,
            )
        else:
            st.warning(
                "No current price or regime snapshot was available for this "
                "ticker."
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


def page_pricing() -> None:
    """
    Pricing page.
    """
    st.header("Pricing Direction")

    st.write(
        "Pricing is not implemented in this prototype. This page defines the "
        "planned free-versus-paid product structure."
    )

    free_col, paid_col, pro_col = st.columns(3)

    with free_col:
        with st.container(border=True):
            st.subheader("Free")
            st.write("Educational preview with fixed assumptions.")
            st.markdown(
                """
                - Preset tickers
                - Fixed account size
                - Fixed risk tier
                - Basic rule comparison
                - Simple interpretation
                """
            )

    with paid_col:
        with st.container(border=True):
            st.subheader("Individual")
            st.write("Configurable covered-call simulator.")
            st.markdown(
                """
                - Custom stock or ETF
                - Optionability and liquidity screen
                - Custom account size
                - User-selected delta and DTE
                - Rule comparison
                - Exportable reports
                - Replay simulator
                - Moving total-equity plot
                """
            )

    with pro_col:
        with st.container(border=True):
            st.subheader("Future Professional")
            st.write("Advanced tools for advisors or researchers.")
            st.markdown(
                """
                - Portfolio-level analysis
                - Batch ticker screening
                - Saved scenarios
                - Client-ready reports
                - Custom rule design
                """
            )

    st.markdown("---")

    st.subheader("Paid-version principle")

    st.success(
        "Free version = educational preview with fixed assumptions. "
        "Paid version = configurable simulator with account-aware, "
        "option-aware, and replay-based analysis."
    )

    display_public_disclaimer_short()


def page_disclaimers() -> None:
    """
    Disclaimers page.
    """
    st.header("Disclaimers")

    public_disclaimer = load_markdown_file(PUBLIC_DISCLAIMER_PATH)

    if public_disclaimer:
        st.markdown(public_disclaimer)
    else:
        st.warning(
            "docs/public_disclaimer.md was not found. Showing fallback "
            "disclaimer text."
        )
        st.markdown(
            """
            The Covered Call Simulator is an educational and analytical tool.
            It is not financial advice, investment advice, tax advice, legal
            advice, or a trade recommendation.

            Simulated results are hypothetical. Options involve risk and are
            not suitable for all investors. Regime detection is probabilistic
            guidance, not an oracle. Tradable does not mean recommended.
            Premium collected is not the same as profit.
            """
        )


def page_about() -> None:
    """
    About page.
    """
    st.header("About the Covered Call Simulator")

    st.write(
        "The Covered Call Simulator was built to answer a practical question: "
        "how do covered-call management rules behave under different market "
        "conditions and account-size constraints?"
    )

    st.write(
        "The project focuses on simulation, practical tradability, account "
        "sizing, option-selection assumptions, and total equity behavior."
    )

    st.markdown("---")

    about_col1, about_col2 = st.columns(2)

    with about_col1:
        st.subheader("What the project emphasizes")
        st.markdown(
            """
            - Scenario comparison
            - Rule comparison
            - Account sizing
            - Option assumptions
            - Total equity
            - Plain-English interpretation
            """
        )

    with about_col2:
        st.subheader("What the project avoids")
        st.markdown(
            """
            - Guaranteed income claims
            - Trade recommendations
            - Black-box signals
            - Claims of market prediction
            - Treating premium as profit
            - Treating regime detection as an oracle
            """
        )

    st.markdown("---")

    st.subheader("Planning documents")

    with st.expander("Show planning document status", expanded=False):
        display_document_status()

    st.subheader("Simulator outputs")

    with st.expander("Show output file status", expanded=False):
        display_output_status()

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

    selected_page = st.sidebar.radio(
        "Navigation",
        options=[
            "Home",
            "How It Works",
            "Free Simulator Preview",
            "Pricing",
            "Disclaimers",
            "About",
            "Planning Docs Preview",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "This public-site prototype is separate from the internal dashboard."
    )

    if selected_page == "Home":
        page_home()
    elif selected_page == "How It Works":
        page_how_it_works()
    elif selected_page == "Free Simulator Preview":
        page_free_simulator_preview()
    elif selected_page == "Pricing":
        page_pricing()
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
