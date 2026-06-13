"""
scenario_comparison_report.py

HTML report for the paid simulator scenario comparison.

This module turns the scenario-comparison rows into a user-facing HTML report.
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.
    """
    return Path(__file__).resolve().parents[2]


def get_default_report_dir() -> Path:
    """
    Return the default paid-simulator report directory.
    """
    return get_project_root() / "outputs" / "reports" / "paid_simulator"


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Convert a value to float safely.
    """
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Convert a value to int safely.
    """
    if value is None:
        return default

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_bool(value: Any, default: bool = False) -> bool:
    """
    Convert common boolean-like values safely.
    """
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "y", "1"}:
            return True
        if normalized in {"false", "no", "n", "0"}:
            return False

    try:
        return bool(value)
    except (TypeError, ValueError):
        return default


def format_money(value: Any) -> str:
    """
    Format a value as dollars.
    """
    return f"${safe_float(value):,.2f}"


def format_signed_money(value: Any) -> str:
    """
    Format a value as signed dollars.
    """
    number = safe_float(value)

    if number >= 0:
        return f"+${number:,.2f}"

    return f"-${abs(number):,.2f}"


def format_percent(value: Any) -> str:
    """
    Format a value as percent.
    """
    return f"{safe_float(value):,.2f}%"


def format_decimal_percent(value: Any) -> str:
    """
    Format a decimal as a percent.
    """
    return f"{safe_float(value):.2%}"


def format_number(value: Any, decimals: int = 2) -> str:
    """
    Format a numeric value with a fixed number of decimals.
    """
    return f"{safe_float(value):,.{decimals}f}"


def format_config_text(value: Any, default: str = "N/A") -> str:
    """
    Format a configuration value for display.
    """
    if value is None:
        return default

    text = str(value).strip()
    if not text:
        return default

    return text


def classify_result(value: Any) -> str:
    """
    Classify covered-call result versus buy-and-hold.
    """
    number = safe_float(value)

    if number > 0:
        return "Outperformed"

    if number < 0:
        return "Underperformed"

    return "Matched"


def get_result_label(
    row: dict[str, object],
    best_row: dict[str, object] | None,
    worst_row: dict[str, object] | None,
    near_break_even_threshold: float = 25.0,
) -> str:
    """
    Return a plain-English label for a scenario result.
    """
    if best_row is not None and row is best_row:
        return "Best environment"

    if worst_row is not None and row is worst_row:
        return "Worst environment"

    difference = safe_float(row.get("covered_call_minus_buy_hold"))

    if abs(difference) <= near_break_even_threshold:
        return "Near break-even"

    if difference > 0:
        return "Helpful environment"

    return "Lagging environment"


def get_result_label_class(label: str) -> str:
    """
    Return the CSS class name for a result label.
    """
    normalized_label = label.strip().lower()

    if normalized_label == "best environment":
        return "badge-best"

    if normalized_label == "worst environment":
        return "badge-worst"

    if normalized_label == "near break-even":
        return "badge-neutral"

    if normalized_label == "helpful environment":
        return "badge-helpful"

    if normalized_label == "lagging environment":
        return "badge-lagging"

    return "badge-neutral"


def build_result_badge(label: str) -> str:
    """
    Build an HTML badge for a scenario result label.
    """
    class_name = get_result_label_class(label)

    return (
        f"<span class=\"result-badge {escape(class_name)}\">"
        f"{escape(label)}"
        "</span>"
    )


def get_best_row(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """
    Return the row with the highest covered-call minus buy-and-hold value.
    """
    if not rows:
        return None

    return max(
        rows,
        key=lambda row: safe_float(row.get("covered_call_minus_buy_hold")),
    )


def get_worst_row(rows: list[dict[str, object]]) -> dict[str, object] | None:
    """
    Return the row with the lowest covered-call minus buy-and-hold value.
    """
    if not rows:
        return None

    return min(
        rows,
        key=lambda row: safe_float(row.get("covered_call_minus_buy_hold")),
    )


def build_metric_card(
    label: str,
    value: str,
    note: str = "",
) -> str:
    """
    Build a metric card.
    """
    note_html = ""
    if note:
        note_html = f"<div class=\"metric-note\">{escape(note)}</div>"

    return (
        "<div class=\"metric-card\">"
        f"<div class=\"metric-label\">{escape(label)}</div>"
        f"<div class=\"metric-value\">{escape(value)}</div>"
        f"{note_html}"
        "</div>"
    )


def build_setup_item(
    label: str,
    value: str,
) -> str:
    """
    Build one compact setup item.
    """
    return (
        "<div class=\"setup-item\">"
        f"<div class=\"setup-label\">{escape(label)}</div>"
        f"<div class=\"setup-value\">{escape(value)}</div>"
        "</div>"
    )


def build_plain_english_takeaway_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a plain-English takeaway from the best and worst scenario results.
    """
    if not rows:
        return ""

    best_row = get_best_row(rows)
    worst_row = get_worst_row(rows)

    if best_row is None or worst_row is None:
        return ""

    best_scenario = str(best_row.get("scenario_display_name", "N/A"))
    worst_scenario = str(worst_row.get("scenario_display_name", "N/A"))
    best_value = format_signed_money(best_row.get("covered_call_minus_buy_hold"))
    worst_value = format_signed_money(worst_row.get("covered_call_minus_buy_hold"))

    return f"""
    <div class="takeaway-section">
        <h2>Plain-English Takeaway</h2>
        <p>
            In this setup, the covered call helps most in the
            <strong>{escape(best_scenario)}</strong> path
            ({escape(best_value)} versus buy-and-hold) and lags most in the
            <strong>{escape(worst_scenario)}</strong> path
            ({escape(worst_value)} versus buy-and-hold).
        </p>
        <p>
            This is consistent with a covered-call profile: option premium can
            cushion sideways or declining markets, while the short call can limit
            upside participation during a strong rally.
        </p>
    </div>
"""


def build_decision_box_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a user-facing decision signal box.

    The signal is not a recommendation. It summarizes whether the modeled
    setup passes the simulator's sizing rules.
    """
    if not rows:
        return ""

    row = rows[0]

    desired_contracts_pass = safe_bool(
        row.get("desired_contracts_pass_screen"),
        default=True,
    )

    desired_contracts = safe_int(row.get("desired_contracts"))
    max_contracts_allowed = safe_int(row.get("max_contracts_allowed"))
    position_size_cap = format_decimal_percent(row.get("position_size_cap"))

    if desired_contracts_pass:
        signal = "Decision signal: Sizing rule passed"
        reason = (
            "The requested contract count fits within the selected "
            "position-size cap. The stress-test results can be interpreted "
            "without a sizing-rule violation."
        )
        css_class = "decision-box-pass"
    else:
        signal = "Decision signal: Analyze with caution"
        reason = (
            "The requested contract count exceeds the selected position-size "
            "cap. The strategy behavior is useful for analysis, but this "
            "contract count is not tradable under the current sizing rule."
        )
        css_class = "decision-box-warning"

    detail = (
        f"Requested contracts: {desired_contracts} | "
        f"Maximum contracts allowed: {max_contracts_allowed} | "
        f"Position-size cap: {position_size_cap}"
    )

    return f"""
    <div class="decision-box {escape(css_class)}">
        <div class="decision-title">{escape(signal)}</div>
        <p>{escape(reason)}</p>
        <div class="decision-detail">{escape(detail)}</div>
    </div>
"""


def build_next_action_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a practical next-action section for the report user.
    """
    if not rows:
        return ""

    row = rows[0]

    desired_contracts_pass = safe_bool(
        row.get("desired_contracts_pass_screen"),
        default=True,
    )

    best_row = get_best_row(rows)
    worst_row = get_worst_row(rows)

    best_scenario = "N/A"
    worst_scenario = "N/A"
    worst_value = "N/A"

    if best_row is not None:
        best_scenario = str(best_row.get("scenario_display_name", "N/A"))

    if worst_row is not None:
        worst_scenario = str(worst_row.get("scenario_display_name", "N/A"))
        worst_value = format_signed_money(worst_row.get("covered_call_minus_buy_hold"))

    if desired_contracts_pass:
        title = "Next action: Review upside tradeoff"
        action = (
            "The setup passes the current sizing rule. Before treating it as a "
            "candidate setup, review whether the worst-case relative lag is "
            "acceptable."
        )
        detail = (
            f"In this run, the covered call helped most in {best_scenario} "
            f"and lagged most in {worst_scenario} ({worst_value} versus "
            "buy-and-hold)."
        )
        css_class = "next-action-pass"
    else:
        desired_contracts = safe_int(row.get("desired_contracts"))
        max_contracts_allowed = safe_int(row.get("max_contracts_allowed"))
        title = "Next action: Reduce contract count or adjust sizing"
        action = (
            "The requested setup fails the current sizing rule. Use the results "
            "as a what-if analysis, but do not treat this contract count as "
            "tradable under the selected cap."
        )
        detail = (
            f"Requested contracts: {desired_contracts}. "
            f"Maximum contracts allowed: {max_contracts_allowed}."
        )
        css_class = "next-action-warning"

    return f"""
    <div class="next-action-box {escape(css_class)}">
        <div class="next-action-title">{escape(title)}</div>
        <p>{escape(action)}</p>
        <div class="next-action-detail">{escape(detail)}</div>
    </div>
"""


def build_covered_call_profile_section() -> str:
    """
    Build a concise profile of the covered-call payoff behavior.
    """
    return """
    <div class="section">
        <h2>Covered-Call Profile</h2>
        <div class="profile-grid">
            <div class="profile-item">
                <div class="profile-title">Primary benefit</div>
                <p>Generates option premium that can help in sideways, mildly rising, or declining paths.</p>
            </div>
            <div class="profile-item">
                <div class="profile-title">Main tradeoff</div>
                <p>Upside is limited once the stock rises above the short-call strike.</p>
            </div>
            <div class="profile-item">
                <div class="profile-title">Downside behavior</div>
                <p>Premium cushions losses, but the stock position can still decline substantially.</p>
            </div>
            <div class="profile-item">
                <div class="profile-title">Best fit</div>
                <p>Usually works best when the stock is flat, modestly bullish, or moderately weak.</p>
            </div>
            <div class="profile-item">
                <div class="profile-title">Weakest fit</div>
                <p>Usually lags buy-and-hold when the stock rallies strongly above the call strike.</p>
            </div>
            <div class="profile-item">
                <div class="profile-title">Sizing focus</div>
                <p>Contract count should stay inside the selected position-size cap before considering execution.</p>
            </div>
        </div>
    </div>
"""


def build_strategy_setup_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a user-facing section showing the active strategy setup.
    """
    if not rows:
        return ""

    row = rows[0]

    ticker = format_config_text(row.get("ticker"))
    management_rule = format_config_text(row.get("management_rule"))
    rolling_rule = format_config_text(row.get("rolling_rule"))
    reentry_rule = format_config_text(row.get("reentry_rule"))
    strike_selection_method = format_config_text(row.get("strike_selection_method"))
    data_source = format_config_text(row.get("data_source"))
    mode = format_config_text(row.get("mode"))

    target_delta = format_number(row.get("target_delta"), decimals=2)
    target_dte = str(safe_int(row.get("target_dte")))
    transaction_cost = format_money(row.get("transaction_cost_per_contract"))
    slippage = format_money(row.get("slippage_assumption"))

    setup_items = "".join(
        [
            build_setup_item("Ticker", ticker),
            build_setup_item("Management rule", management_rule),
            build_setup_item("Target delta", target_delta),
            build_setup_item("Target DTE", target_dte),
            build_setup_item("Strike selection", strike_selection_method),
            build_setup_item("Rolling rule", rolling_rule),
            build_setup_item("Re-entry rule", reentry_rule),
            build_setup_item("Transaction cost", f"{transaction_cost} per contract"),
            build_setup_item("Slippage assumption", slippage),
            build_setup_item("Data source", data_source),
            build_setup_item("Simulation mode", mode),
        ]
    )

    return f"""
    <div class="section">
        <h2>Strategy Setup</h2>
        <div class="setup-grid">
            {setup_items}
        </div>
        <p class="note">
            These are the active paid-simulator inputs used to generate this
            stress test. Changing any of these values may change the relative
            covered-call result versus buy-and-hold.
        </p>
    </div>
"""


def build_methodology_assumptions_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a concise methodology and assumptions section.
    """
    if not rows:
        return ""

    row = rows[0]

    data_source = format_config_text(row.get("data_source"))
    mode = format_config_text(row.get("mode"))
    transaction_cost = format_money(row.get("transaction_cost_per_contract"))
    slippage = format_money(row.get("slippage_assumption"))
    management_rule = format_config_text(row.get("management_rule"))

    assumption_items = "".join(
        [
            build_setup_item("Path type", "Modeled market paths"),
            build_setup_item("Data source", data_source),
            build_setup_item("Simulation mode", mode),
            build_setup_item("Management rule", management_rule),
            build_setup_item("Transaction cost", f"{transaction_cost} per contract"),
            build_setup_item("Slippage assumption", slippage),
        ]
    )

    return f"""
    <div class="section">
        <h2>Methodology and Assumptions</h2>
        <div class="setup-grid">
            {assumption_items}
        </div>
        <p class="note">
            This stress test applies the same covered-call setup to several
            modeled market paths. The goal is to isolate the strategy behavior
            across different price environments, not to forecast which path will
            occur.
        </p>
        <p class="note">
            Results are sensitive to option-pricing assumptions, transaction
            costs, slippage, path shape, and management rules. Treat the output
            as a structured what-if analysis rather than a prediction.
        </p>
    </div>
"""


def build_selected_option_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a section showing the modeled short-call option selected by the simulator.
    """
    if not rows:
        return ""

    row = rows[0]

    selected_strike = format_money(row.get("selected_strike"))
    selected_delta = format_number(row.get("selected_delta"), decimals=2)
    premium_per_contract = format_money(row.get("selected_premium_per_contract"))
    total_premium = format_money(row.get("selected_total_premium"))

    premium_yield = format_percent(row.get("pre_trade_premium_yield_percent"))
    if_assigned_return = format_percent(
        row.get("pre_trade_if_assigned_return_percent")
    )

    desired_contracts = str(row.get("desired_contracts", "N/A"))

    selected_option_items = "".join(
        [
            build_setup_item("Selected short-call strike", selected_strike),
            build_setup_item("Selected short-call delta", selected_delta),
            build_setup_item("Premium per contract", premium_per_contract),
            build_setup_item("Total premium", total_premium),
            build_setup_item("Premium yield", premium_yield),
            build_setup_item("If-assigned return", if_assigned_return),
            build_setup_item("Modeled contracts", desired_contracts),
        ]
    )

    return f"""
    <div class="section">
        <h2>Selected Option</h2>
        <div class="setup-grid">
            {selected_option_items}
        </div>
        <p class="note">
            This is the modeled short call selected from the active strategy
            inputs. Premium and return figures are simplified simulator
            estimates and are shown before the path stress test is applied.
        </p>
    </div>
"""


def build_sizing_warning(row: dict[str, object]) -> str:
    """
    Build a warning banner if the requested contract count fails the sizing screen.
    """
    desired_contracts_pass = safe_bool(
        row.get("desired_contracts_pass_screen"),
        default=True,
    )

    if desired_contracts_pass:
        return ""

    requested_contracts = safe_int(row.get("desired_contracts"))
    max_contracts_allowed = safe_int(row.get("max_contracts_allowed"))
    position_size_cap = format_decimal_percent(row.get("position_size_cap"))

    return f"""
        <div class="warning-box">
            <div class="warning-title">Sizing warning</div>
            <p>
                The requested number of contracts exceeds the selected
                position-size cap. The simulation is shown for analysis, but
                this contract count is not tradable under the current sizing rule.
            </p>
            <div class="warning-detail">
                Requested contracts: {escape(str(requested_contracts))}
                &nbsp;|&nbsp;
                Maximum contracts allowed: {escape(str(max_contracts_allowed))}
                &nbsp;|&nbsp;
                Position-size cap: {escape(position_size_cap)}
            </div>
        </div>
"""


def build_position_sizing_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build the position-sizing section from the first comparison row.
    """
    if not rows:
        return ""

    row = rows[0]
    sizing_warning = build_sizing_warning(row)

    metric_cards = "".join(
        [
            build_metric_card(
                "Account size",
                format_money(row.get("account_size")),
                f"Risk tier: {row.get('risk_tier', 'N/A')}",
            ),
            build_metric_card(
                "Desired contracts",
                str(row.get("desired_contracts", "N/A")),
                f"Passes screen: {row.get('desired_contracts_pass_screen', 'N/A')}",
            ),
            build_metric_card(
                "Maximum contracts allowed",
                str(row.get("max_contracts_allowed", "N/A")),
                "Based on account size and position-size cap.",
            ),
            build_metric_card(
                "Position-size cap",
                format_decimal_percent(row.get("position_size_cap")),
                "Maximum target allocation to one covered-call position.",
            ),
            build_metric_card(
                "Desired position value",
                format_money(row.get("desired_position_value")),
                f"Desired allocation: {format_decimal_percent(row.get('desired_position_percent'))}",
            ),
            build_metric_card(
                "Allowed position value",
                format_money(row.get("allowed_position_value")),
                "Account size multiplied by the position-size cap.",
            ),
            build_metric_card(
                "Stock value per contract",
                format_money(row.get("stock_value_per_contract")),
                "One standard contract controls 100 shares.",
            ),
            build_metric_card(
                "Equity needed for desired",
                format_money(row.get("required_equity_for_desired_contracts")),
                "Equity required to trade the desired contract count under the cap.",
            ),
            build_metric_card(
                "Extra equity needed",
                format_money(row.get("required_extra_equity_for_desired_contracts")),
                "Zero means the desired contract count passes the screen.",
            ),
        ]
    )

    return f"""
    <div class="section">
        <h2>Position Sizing</h2>
        {sizing_warning}
        <div class="metrics">
            {metric_cards}
        </div>
        <p class="note">
            Position sizing is based on the selected account size, ticker price,
            desired contracts, and per-position cap. A result of "passes screen"
            means the requested contract count fits inside the selected cap.
            It does not mean the trade is recommended.
        </p>
        <p class="note">
            Path P/L is scaled to the desired contract count from the active
            paid-simulator configuration. If the requested contract count fails
            the sizing screen, the results are still shown as a what-if analysis.
        </p>
    </div>
"""


def explain_relative_difference(row: dict[str, object]) -> str:
    """
    Explain why the covered-call result differed from buy-and-hold.
    """
    difference = safe_float(row.get("covered_call_minus_buy_hold"))

    if abs(difference) <= 25.0:
        return "Nearly matched buy-and-hold"

    if difference > 0:
        return "Premium helped more than upside was limited"

    return "Upside limitation outweighed premium collected"


def build_buy_hold_difference_section(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a user-facing section explaining what changed versus buy-and-hold.
    """
    if not rows:
        return ""

    body_rows: list[str] = []

    for row in rows:
        scenario_name = str(row.get("scenario_display_name", ""))
        total_premium = format_money(row.get("selected_total_premium"))
        missed_upside = format_money(row.get("total_missed_upside"))
        difference = format_signed_money(row.get("covered_call_minus_buy_hold"))
        explanation = explain_relative_difference(row)

        body_rows.append(
            "<tr>"
            f"<td>{escape(scenario_name)}</td>"
            f"<td class=\"numeric\">{escape(total_premium)}</td>"
            f"<td class=\"numeric\">{escape(missed_upside)}</td>"
            f"<td class=\"numeric\">{escape(difference)}</td>"
            f"<td>{escape(explanation)}</td>"
            "</tr>"
        )

    table_html = (
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Market path</th>"
        "<th>Premium collected</th>"
        "<th>Missed upside</th>"
        "<th>Net difference</th>"
        "<th>Plain-English explanation</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        + "".join(body_rows)
        + "</tbody>"
        "</table>"
    )

    return f"""
    <div class="section">
        <h2>What Changed Versus Buy-and-Hold?</h2>
        <p class="note">
            A covered call changes the stock-only result mainly by adding option
            premium while giving up some upside above the short-call strike.
            This table summarizes that tradeoff for each modeled market path.
        </p>
        {table_html}
    </div>
"""


def build_bar_chart_svg(
    rows: list[dict[str, object]],
) -> str:
    """
    Build an embedded SVG horizontal bar chart for scenario differences.
    """
    if not rows:
        return "<p>No scenario rows available.</p>"

    values = [
        safe_float(row.get("covered_call_minus_buy_hold"))
        for row in rows
    ]

    max_abs_value = max(abs(value) for value in values)

    if max_abs_value == 0:
        max_abs_value = 1.0

    chart_width = 960
    row_height = 48
    top_margin = 36
    bottom_margin = 28
    label_width = 190
    value_width = 130
    plot_width = chart_width - label_width - value_width - 40
    zero_x = label_width + plot_width / 2
    chart_height = top_margin + bottom_margin + row_height * len(rows)

    scale = (plot_width / 2) / max_abs_value

    elements: list[str] = []

    elements.append(
        f'<svg viewBox="0 0 {chart_width} {chart_height}" '
        'role="img" aria-label="Covered-call stress-test chart" '
        'xmlns="http://www.w3.org/2000/svg">'
    )

    elements.append(
        '<rect x="0" y="0" width="100%" height="100%" rx="10" fill="#ffffff"/>'
    )

    elements.append(
        f'<line x1="{zero_x:.1f}" y1="{top_margin - 14}" '
        f'x2="{zero_x:.1f}" y2="{chart_height - bottom_margin + 8}" '
        'stroke="#94a3b8" stroke-width="1"/>'
    )

    elements.append(
        f'<text x="{zero_x:.1f}" y="20" text-anchor="middle" '
        'font-size="12" fill="#64748b">Buy-and-hold parity</text>'
    )

    for index, row in enumerate(rows):
        y = top_margin + index * row_height + 12
        bar_y = y + 7
        bar_height = 18

        scenario = str(row.get("scenario_display_name", "Scenario"))
        value = safe_float(row.get("covered_call_minus_buy_hold"))

        if value >= 0:
            x = zero_x
            width = value * scale
            fill = "#2563eb"
        else:
            width = abs(value) * scale
            x = zero_x - width
            fill = "#64748b"

        elements.append(
            f'<text x="12" y="{y + 20}" font-size="13" '
            'fill="#102a43" font-weight="600">'
            f'{escape(scenario)}</text>'
        )

        elements.append(
            f'<rect x="{x:.1f}" y="{bar_y:.1f}" '
            f'width="{width:.1f}" height="{bar_height}" '
            f'rx="4" fill="{fill}"/>'
        )

        elements.append(
            f'<text x="{chart_width - 18}" y="{y + 20}" '
            'font-size="13" text-anchor="end" fill="#102a43" '
            'font-weight="600">'
            f'{escape(format_signed_money(value))}</text>'
        )

    elements.append("</svg>")

    return (
        '<div class="chart-card">'
        '<div class="chart-title">Covered-call result versus buy-and-hold</div>'
        '<div class="chart-subtitle">'
        'Positive values mean the covered-call strategy finished ahead of buy-and-hold.'
        '</div>'
        + "".join(elements)
        + "</div>"
    )


def build_result_label_guide_section() -> str:
    """
    Build a short guide explaining the scenario result labels.
    """
    return """
    <div class="section">
        <h2>How to Interpret the Scenario Labels</h2>
        <p class="note">
            The labels summarize how the covered-call setup performed relative
            to buy-and-hold in each modeled market path. They are descriptive
            labels for this stress test, not trade recommendations.
        </p>
        <div class="label-guide-grid">
            <div class="label-guide-item">
                <span class="result-badge badge-best">Best environment</span>
                <p>The path where the covered call helped most versus buy-and-hold.</p>
            </div>
            <div class="label-guide-item">
                <span class="result-badge badge-worst">Worst environment</span>
                <p>The path where the covered call lagged buy-and-hold by the most.</p>
            </div>
            <div class="label-guide-item">
                <span class="result-badge badge-neutral">Near break-even</span>
                <p>The covered call and buy-and-hold finished very close together.</p>
            </div>
            <div class="label-guide-item">
                <span class="result-badge badge-helpful">Helpful environment</span>
                <p>The covered call finished ahead of buy-and-hold, but was not the best path.</p>
            </div>
            <div class="label-guide-item">
                <span class="result-badge badge-lagging">Lagging environment</span>
                <p>The covered call trailed buy-and-hold, usually because upside was capped.</p>
            </div>
        </div>
    </div>
"""


def build_comparison_table(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a comparison table from scenario rows.
    """
    if not rows:
        return "<p>No scenario rows available.</p>"

    best_row = get_best_row(rows)
    worst_row = get_worst_row(rows)

    body_rows: list[str] = []

    for row in rows:
        scenario_name = str(row.get("scenario_display_name", ""))
        scenario_return = format_percent(
            row.get("scenario_total_simple_return_percent")
        )
        covered_call_equity = format_money(row.get("final_covered_call_equity"))
        buy_hold_equity = format_money(row.get("final_buy_hold_equity"))
        difference = format_signed_money(row.get("covered_call_minus_buy_hold"))
        covered_call_pl = format_signed_money(row.get("covered_call_pl_after_entry"))
        buy_hold_pl = format_signed_money(row.get("buy_hold_pl_from_initial_account"))
        final_stock_price = format_money(row.get("final_stock_price"))
        result = classify_result(row.get("covered_call_minus_buy_hold"))
        result_label = get_result_label(
            row=row,
            best_row=best_row,
            worst_row=worst_row,
        )
        result_badge = build_result_badge(result_label)

        body_rows.append(
            "<tr>"
            f"<td>{escape(scenario_name)}</td>"
            f"<td>{result_badge}</td>"
            f"<td class=\"numeric\">{escape(scenario_return)}</td>"
            f"<td class=\"numeric\">{escape(final_stock_price)}</td>"
            f"<td class=\"numeric\">{escape(covered_call_equity)}</td>"
            f"<td class=\"numeric\">{escape(buy_hold_equity)}</td>"
            f"<td class=\"numeric\">{escape(difference)}</td>"
            f"<td class=\"numeric\">{escape(covered_call_pl)}</td>"
            f"<td class=\"numeric\">{escape(buy_hold_pl)}</td>"
            f"<td>{escape(result)}</td>"
            "</tr>"
        )

    return (
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Market path</th>"
        "<th>Label</th>"
        "<th>Path return</th>"
        "<th>Final stock price</th>"
        "<th>Covered-call equity</th>"
        "<th>Buy-and-hold equity</th>"
        "<th>Difference</th>"
        "<th>Covered-call P/L</th>"
        "<th>Buy-and-hold P/L</th>"
        "<th>Result</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        + "".join(body_rows)
        + "</tbody>"
        "</table>"
    )


def build_scenario_report_link_table(
    rows: list[dict[str, object]],
) -> str:
    """
    Build a table linking to per-scenario HTML reports.
    """
    if not rows:
        return "<p>No path reports available.</p>"

    body_rows: list[str] = []

    for row in rows:
        scenario_name = str(row.get("scenario_display_name", ""))
        html_path = str(row.get("saved_html_report", ""))
        session_id = str(row.get("session_id", ""))

        if html_path:
            normalized_path = html_path.replace("\\", "/")
            link_html = (
                f'<a href="file:///{escape(normalized_path)}">'
                "Open report"
                "</a>"
            )
        else:
            link_html = "Not saved"

        body_rows.append(
            "<tr>"
            f"<td>{escape(scenario_name)}</td>"
            f"<td>{escape(session_id)}</td>"
            f"<td>{link_html}</td>"
            "</tr>"
        )

    return (
        "<table>"
        "<thead>"
        "<tr>"
        "<th>Market path</th>"
        "<th>Session ID</th>"
        "<th>Detailed path report</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        + "".join(body_rows)
        + "</tbody>"
        "</table>"
    )


def build_scenario_comparison_html_report(
    rows: list[dict[str, object]],
) -> str:
    """
    Build the complete strategy stress-test HTML report.
    """
    generated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    best_row = get_best_row(rows)
    worst_row = get_worst_row(rows)

    best_scenario = "N/A"
    best_value = "N/A"
    worst_scenario = "N/A"
    worst_value = "N/A"

    if best_row is not None:
        best_scenario = str(best_row.get("scenario_display_name", "N/A"))
        best_value = format_signed_money(best_row.get("covered_call_minus_buy_hold"))

    if worst_row is not None:
        worst_scenario = str(worst_row.get("scenario_display_name", "N/A"))
        worst_value = format_signed_money(worst_row.get("covered_call_minus_buy_hold"))

    metric_cards = "".join(
        [
            build_metric_card(
                "Market paths tested",
                str(len(rows)),
                "Number of modeled paths in this stress test.",
            ),
            build_metric_card(
                "Best covered-call relative result",
                best_value,
                best_scenario,
            ),
            build_metric_card(
                "Worst covered-call relative result",
                worst_value,
                worst_scenario,
            ),
        ]
    )

    plain_english_takeaway_section = build_plain_english_takeaway_section(rows)
    decision_box_section = build_decision_box_section(rows)
    next_action_section = build_next_action_section(rows)
    covered_call_profile_section = build_covered_call_profile_section()
    strategy_setup_section = build_strategy_setup_section(rows)
    methodology_assumptions_section = build_methodology_assumptions_section(rows)
    selected_option_section = build_selected_option_section(rows)
    position_sizing_section = build_position_sizing_section(rows)
    buy_hold_difference_section = build_buy_hold_difference_section(rows)
    result_label_guide_section = build_result_label_guide_section()
    chart_html = build_bar_chart_svg(rows)
    comparison_table = build_comparison_table(rows)
    report_link_table = build_scenario_report_link_table(rows)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Covered Call Strategy Stress Test</title>
<style>
    body {{
        margin: 0;
        padding: 0;
        font-family: Arial, Helvetica, sans-serif;
        background: #f5f7fa;
        color: #1f2933;
    }}

    .page {{
        max-width: 1120px;
        margin: 0 auto;
        padding: 32px 24px 48px 24px;
    }}

    .report-actions {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
    }}

    .print-button {{
        border: 1px solid #2563eb;
        background: #2563eb;
        color: #ffffff;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.12);
    }}

    .print-button:hover {{
        background: #1d4ed8;
        border-color: #1d4ed8;
    }}

    .header {{
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 14px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
    }}

    .eyebrow {{
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #52616b;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 8px;
    }}

    h1 {{
        margin: 0 0 8px 0;
        font-size: 30px;
        line-height: 1.2;
    }}

    h2 {{
        margin: 0 0 16px 0;
        font-size: 22px;
    }}

    .subtitle {{
        color: #52616b;
        font-size: 15px;
        line-height: 1.5;
        margin: 0;
    }}

    .section {{
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }}

    .takeaway-section {{
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }}

    .takeaway-section p {{
        color: #1e3a8a;
        line-height: 1.55;
        font-size: 15px;
        margin: 0 0 10px 0;
    }}

    .takeaway-section p:last-child {{
        margin-bottom: 0;
    }}

    .decision-box {{
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }}

    .decision-box-warning {{
        background: #fffbeb;
        border: 1px solid #f59e0b;
        color: #92400e;
    }}

    .decision-box-pass {{
        background: #ecfdf5;
        border: 1px solid #10b981;
        color: #065f46;
    }}

    .decision-title {{
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 8px;
    }}

    .decision-box p {{
        line-height: 1.55;
        font-size: 15px;
        margin: 0 0 8px 0;
    }}

    .decision-detail {{
        font-size: 13px;
        font-weight: 700;
    }}

    .metrics {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
    }}

    .metric-card {{
        border: 1px solid #d9e2ec;
        background: #f8fafc;
        border-radius: 12px;
        padding: 16px;
    }}

    .metric-label {{
        color: #52616b;
        font-size: 13px;
        margin-bottom: 6px;
    }}

    .metric-value {{
        font-size: 24px;
        font-weight: 700;
        color: #102a43;
    }}

    .metric-note {{
        color: #697b8c;
        font-size: 12px;
        margin-top: 6px;
        line-height: 1.35;
    }}

    .setup-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin-bottom: 16px;
    }}

    .setup-item {{
        border: 1px solid #d9e2ec;
        background: #f8fafc;
        border-radius: 10px;
        padding: 12px 14px;
    }}

    .setup-label {{
        color: #52616b;
        font-size: 12px;
        margin-bottom: 5px;
    }}

    .setup-value {{
        color: #102a43;
        font-size: 15px;
        font-weight: 700;
        line-height: 1.25;
    }}

    .result-badge {{
        display: inline-block;
        border-radius: 999px;
        padding: 4px 9px;
        font-size: 12px;
        font-weight: 700;
        white-space: nowrap;
    }}

    .badge-best {{
        color: #166534;
        background: #dcfce7;
        border: 1px solid #86efac;
    }}

    .badge-worst {{
        color: #991b1b;
        background: #fee2e2;
        border: 1px solid #fca5a5;
    }}

    .badge-neutral {{
        color: #334155;
        background: #e2e8f0;
        border: 1px solid #cbd5e1;
    }}

    .badge-helpful {{
        color: #1d4ed8;
        background: #dbeafe;
        border: 1px solid #93c5fd;
    }}

    .badge-lagging {{
        color: #92400e;
        background: #fffbeb;
        border: 1px solid #fcd34d;
    }}

    .label-guide-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin-top: 14px;
    }}

    .label-guide-item {{
        border: 1px solid #d9e2ec;
        background: #f8fafc;
        border-radius: 10px;
        padding: 12px 14px;
    }}

    .label-guide-item p {{
        color: #52616b;
        font-size: 13px;
        line-height: 1.45;
        margin: 8px 0 0 0;
    }}

    .next-action-box {{
        border-radius: 14px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }}

    .next-action-pass {{
        background: #f8fafc;
        border: 1px solid #94a3b8;
        color: #102a43;
    }}

    .next-action-warning {{
        background: #fff7ed;
        border: 1px solid #fb923c;
        color: #9a3412;
    }}

    .next-action-title {{
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 8px;
    }}

    .next-action-box p {{
        line-height: 1.55;
        font-size: 15px;
        margin: 0 0 8px 0;
    }}

    .next-action-detail {{
        font-size: 13px;
        font-weight: 700;
    }}

    .profile-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 4px;
    }}

    .profile-item {{
        border: 1px solid #d9e2ec;
        background: #f8fafc;
        border-radius: 10px;
        padding: 14px 16px;
    }}

    .profile-title {{
        color: #102a43;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 6px;
    }}

    .profile-item p {{
        color: #52616b;
        font-size: 13px;
        line-height: 1.45;
        margin: 0;
    }}

    .warning-box {{
        border: 1px solid #f59e0b;
        background: #fffbeb;
        color: #92400e;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 18px;
    }}

    .warning-title {{
        font-weight: 700;
        margin-bottom: 8px;
    }}

    .warning-box p {{
        margin: 0 0 8px 0;
        line-height: 1.5;
        font-size: 14px;
    }}

    .warning-detail {{
        font-size: 13px;
        font-weight: 700;
    }}

    .chart-card {{
        border: 1px solid #d9e2ec;
        background: #f8fafc;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }}

    .chart-title {{
        font-weight: 700;
        color: #102a43;
        font-size: 16px;
        margin-bottom: 4px;
    }}

    .chart-subtitle {{
        color: #52616b;
        font-size: 13px;
        margin-bottom: 12px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }}

    th {{
        text-align: left;
        background: #f1f5f9;
        border-bottom: 1px solid #cbd5e1;
        padding: 10px 8px;
        color: #334e68;
    }}

    td {{
        border-bottom: 1px solid #e2e8f0;
        padding: 9px 8px;
        vertical-align: top;
    }}

    td.numeric {{
        text-align: right;
        font-variant-numeric: tabular-nums;
    }}

    .note {{
        color: #52616b;
        line-height: 1.55;
        font-size: 14px;
    }}

    .disclaimer {{
        color: #697b8c;
        font-size: 12px;
        line-height: 1.5;
    }}

    a {{
        color: #2563eb;
        text-decoration: none;
        font-weight: 600;
    }}

    a:hover {{
        text-decoration: underline;
    }}

    @media (max-width: 1000px) {{
        .setup-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}

        .profile-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
    }}

    @media (max-width: 800px) {{
        .metrics {{
            grid-template-columns: 1fr;
        }}

        .setup-grid {{
            grid-template-columns: 1fr;
        }}

        .label-guide-grid {{
            grid-template-columns: 1fr;
        }}

        .profile-grid {{
            grid-template-columns: 1fr;
        }}

        .page {{
            padding: 20px 12px;
        }}
    }}
    @media print {{
        body {{
            background: #ffffff;
        }}

        .page {{
            max-width: none;
            padding: 0;
        }}

        .report-actions {{
            display: none;
        }}

        .header,
        .section,
        .takeaway-section,
        .decision-box,
        .chart-card {{
            box-shadow: none;
            break-inside: avoid;
        }}

        .section,
        .takeaway-section,
        .decision-box {{
            margin-bottom: 14px;
        }}

        a {{
            color: #102a43;
            text-decoration: none;
        }}

        table {{
            font-size: 11px;
        }}

        th,
        td {{
            padding: 6px 5px;
        }}
    }}

</style>
</head>
<body>
<div class="page">
    <div class="report-actions">
        <button class="print-button" onclick="window.print()">Print / Save PDF</button>
    </div>
    <div class="header">
        <div class="eyebrow">Covered Call Simulator</div>
        <h1>Covered Call Strategy Stress Test</h1>
        <p class="subtitle">
            Generated: {escape(generated_timestamp)}<br>
            This report compares the same covered-call setup across several
            modeled market-path scenarios.
        </p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <div class="metrics">
            {metric_cards}
        </div>
    </div>

    {plain_english_takeaway_section}

    {decision_box_section}

    {next_action_section}

    {covered_call_profile_section}

    {strategy_setup_section}

    {methodology_assumptions_section}

    {selected_option_section}

    {position_sizing_section}

    {buy_hold_difference_section}

    <div class="section">
        <h2>Comparison Chart</h2>
        {chart_html}
    </div>

    {result_label_guide_section}

    <div class="section">
        <h2>Market Path Comparison Table</h2>
        {comparison_table}
    </div>

    <div class="section">
        <h2>Detailed Path Reports</h2>
        <p class="note">
            Each modeled market path also has its own detailed report with an
            equity curve and path summary.
        </p>
        {report_link_table}
    </div>

    <div class="section">
        <h2>How to Read This Stress Test</h2>
        <p class="note">
            This report isolates how the selected covered-call configuration
            behaves across different market paths. Covered calls tend to help
            when the stock falls or remains contained, and tend to lag when the
            stock rallies strongly above the short-call strike.
        </p>
    </div>

    <div class="section">
        <h2>Important Limitations</h2>
        <p class="disclaimer">
            This is an illustrative simulator report, not financial advice,
            investment advice, or a trade recommendation. The option marks are
            simplified estimates and do not reflect a full option-pricing model,
            real bid/ask dynamics, taxes, early assignment, dividends, market
            impact, or changing implied volatility. Simulated results are
            hypothetical and may not reflect actual trading outcomes.
        </p>
    </div>
</div>
</body>
</html>
"""


def save_scenario_comparison_html_report(
    rows: list[dict[str, object]],
    output_path: Path | None = None,
) -> str:
    """
    Save the scenario-comparison HTML report.
    """
    if output_path is None:
        output_path = get_default_report_dir() / "scenario_comparison_report.html"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    html_content = build_scenario_comparison_html_report(
        rows=rows,
    )

    output_path.write_text(html_content, encoding="utf-8")

    return str(output_path)
