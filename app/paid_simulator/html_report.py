"""
html_report.py

HTML report output for the paid Covered Call Simulator.

This module turns saved paid-simulator CSV outputs into a readable HTML report.

Default output folder:

    outputs/reports/paid_simulator

Expected input files:

    outputs/tables/paid_simulator/<session_id>_equity_curve.csv
    outputs/tables/paid_simulator/<session_id>_path_summary.csv

Output file:

    outputs/reports/paid_simulator/<session_id>_paid_simulator_report.html
"""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from html_chart import build_equity_curve_svg_chart
from report_reader import (
    build_compact_readback_summary,
    path_summary_rows_to_dict,
    read_path_report,
)


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.
    """
    return Path(__file__).resolve().parents[2]


def get_default_html_output_dir() -> Path:
    """
    Return the default paid-simulator HTML report directory.
    """
    return get_project_root() / "outputs" / "reports" / "paid_simulator"


def parse_float(value: Any) -> float | None:
    """
    Convert a value to float if possible.
    """
    if value is None:
        return None

    text = str(value).strip()

    if text == "":
        return None

    try:
        return float(text)
    except ValueError:
        return None


def format_money(value: Any) -> str:
    """
    Format a numeric value as dollars.
    """
    number = parse_float(value)

    if number is None:
        return "N/A"

    return f"${number:,.2f}"


def format_number(value: Any) -> str:
    """
    Format a numeric value cleanly.
    """
    number = parse_float(value)

    if number is None:
        return "N/A"

    return f"{number:,.2f}"


def format_integer(value: Any) -> str:
    """
    Format a numeric value as an integer-like string.
    """
    number = parse_float(value)

    if number is None:
        return "N/A"

    return f"{number:,.0f}"


def format_percent(value: Any) -> str:
    """
    Format a numeric value as a percent.
    """
    number = parse_float(value)

    if number is None:
        return "N/A"

    return f"{number:,.2f}%"


def html_table_from_rows(
    rows: list[dict[str, Any]],
    columns: list[str],
    money_columns: set[str] | None = None,
    number_columns: set[str] | None = None,
) -> str:
    """
    Build a simple HTML table from row dictionaries.
    """
    if money_columns is None:
        money_columns = set()

    if number_columns is None:
        number_columns = set()

    if not rows:
        return "<p>No rows available.</p>"

    header_html = "".join(
        f"<th>{escape(column.replace('_', ' ').title())}</th>"
        for column in columns
    )

    body_rows: list[str] = []

    for row in rows:
        cells: list[str] = []

        for column in columns:
            raw_value = row.get(column, "")

            if column in money_columns:
                display_value = format_money(raw_value)
                css_class = "numeric"
            elif column in number_columns:
                display_value = format_number(raw_value)
                css_class = "numeric"
            else:
                display_value = str(raw_value)
                css_class = ""

            cells.append(
                f"<td class=\"{css_class}\">{escape(display_value)}</td>"
            )

        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        "<table>"
        "<thead><tr>"
        f"{header_html}"
        "</tr></thead>"
        "<tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def build_metric_card(
    label: str,
    value: str,
    note: str = "",
) -> str:
    """
    Build a metric card.
    """
    note_html = f"<div class=\"metric-note\">{escape(note)}</div>" if note else ""

    return (
        "<div class=\"metric-card\">"
        f"<div class=\"metric-label\">{escape(label)}</div>"
        f"<div class=\"metric-value\">{escape(value)}</div>"
        f"{note_html}"
        "</div>"
    )


def build_scenario_section(
    summary_dict: dict[str, str],
) -> str:
    """
    Build an HTML section describing the selected scenario.
    """
    scenario_display_name = summary_dict.get(
        "scenario_display_name",
        "Not specified",
    )

    scenario_name = summary_dict.get(
        "scenario_name",
        "not_specified",
    )

    scenario_description = summary_dict.get(
        "scenario_description",
        "No scenario description was saved.",
    )

    scenario_total_simple_return_percent = summary_dict.get(
        "scenario_total_simple_return_percent",
        "",
    )

    scenario_return_text = ""
    if scenario_total_simple_return_percent != "":
        scenario_return_text = (
            "<div class=\"scenario-detail\">"
            "<strong>Total simple scenario return:</strong> "
            f"{escape(format_percent(scenario_total_simple_return_percent))}"
            "</div>"
        )

    return f"""
    <div class="section">
        <h2>Scenario</h2>
        <div class="scenario-box">
            <div class="scenario-title">{escape(str(scenario_display_name))}</div>
            <div class="scenario-code">Scenario key: {escape(str(scenario_name))}</div>
            <p class="note">{escape(str(scenario_description))}</p>
            {scenario_return_text}
        </div>
    </div>
"""


def build_html_report(
    report_data: dict[str, Any],
) -> str:
    """
    Build the paid-simulator HTML report content.
    """
    compact_summary = build_compact_readback_summary(report_data)
    path_summary_rows = report_data.get("path_summary_rows", [])
    equity_curve_rows = report_data.get("equity_curve_rows", [])

    summary_dict = path_summary_rows_to_dict(path_summary_rows)

    session_id = str(report_data.get("session_id", "paid_simulator_session"))
    generated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    final_covered_call_equity = compact_summary.get("final_covered_call_equity")
    final_buy_hold_equity = compact_summary.get("final_buy_hold_equity")
    covered_call_minus_buy_hold = compact_summary.get("covered_call_minus_buy_hold")
    covered_call_pl_after_entry = compact_summary.get("covered_call_pl_after_entry")
    final_stock_price = compact_summary.get("final_stock_price")

    metric_cards = "".join(
        [
            build_metric_card(
                "Final covered-call equity",
                format_money(final_covered_call_equity),
                "Total equity after the simulated path.",
            ),
            build_metric_card(
                "Final buy-and-hold equity",
                format_money(final_buy_hold_equity),
                "Benchmark using the same initial share allocation.",
            ),
            build_metric_card(
                "Covered-call minus buy-and-hold",
                format_money(covered_call_minus_buy_hold),
                "Positive means the covered-call path finished ahead.",
            ),
            build_metric_card(
                "Covered-call P/L after entry",
                format_money(covered_call_pl_after_entry),
                "Change from opening covered-call equity.",
            ),
            build_metric_card(
                "Final stock price",
                format_money(final_stock_price),
                "Last simulated underlying price.",
            ),
            build_metric_card(
                "Path steps",
                format_integer(summary_dict.get("steps")),
                "Number of simulated market steps.",
            ),
        ]
    )

    scenario_section = build_scenario_section(
        summary_dict=summary_dict,
    )

    equity_chart = build_equity_curve_svg_chart(
        equity_curve_rows=equity_curve_rows,
        title="Covered-call equity versus buy-and-hold",
    )

    equity_table_columns = [
        "step_number",
        "stock_price",
        "cash",
        "stock_value",
        "short_call_value",
        "total_equity",
        "unrealized_option_pl",
        "missed_upside",
        "benchmark_buy_hold_equity",
    ]

    equity_table = html_table_from_rows(
        rows=equity_curve_rows,
        columns=equity_table_columns,
        money_columns={
            "stock_price",
            "cash",
            "stock_value",
            "short_call_value",
            "total_equity",
            "unrealized_option_pl",
            "missed_upside",
            "benchmark_buy_hold_equity",
        },
    )

    summary_table = html_table_from_rows(
        rows=path_summary_rows,
        columns=["metric", "value"],
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Paid Simulator Report - {escape(session_id)}</title>
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

    h2 {{
        margin: 0 0 16px 0;
        font-size: 22px;
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

    .scenario-box {{
        border: 1px solid #d9e2ec;
        background: #f8fafc;
        border-radius: 12px;
        padding: 18px;
    }}

    .scenario-title {{
        font-size: 20px;
        font-weight: 700;
        color: #102a43;
        margin-bottom: 4px;
    }}

    .scenario-code {{
        color: #697b8c;
        font-size: 13px;
        margin-bottom: 12px;
    }}

    .scenario-detail {{
        color: #334e68;
        font-size: 14px;
        margin-top: 10px;
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

    @media (max-width: 800px) {{
        .metrics {{
            grid-template-columns: 1fr;
        }}

        .page {{
            padding: 20px 12px;
        }}
    }}
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <div class="eyebrow">Covered Call Simulator</div>
        <h1>Paid Simulator Path Report</h1>
        <p class="subtitle">
            Session: <strong>{escape(session_id)}</strong><br>
            Generated: {escape(generated_timestamp)}
        </p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <div class="metrics">
            {metric_cards}
        </div>
    </div>

    {scenario_section}

    <div class="section">
        <h2>Interpretation</h2>
        <p class="note">
            This report compares the simulated covered-call account equity
            against a simple buy-and-hold benchmark over the same illustrative
            stock path. Premium collected is not treated as immediate profit;
            the short call is marked as a liability after sale.
        </p>
    </div>

    <div class="section">
        <h2>Equity Curve</h2>
        {equity_chart}
        {equity_table}
    </div>

    <div class="section">
        <h2>Path Summary Data</h2>
        {summary_table}
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

    return html


def save_html_report(
    session_id: str,
    output_dir: Path | None = None,
) -> str:
    """
    Read saved CSV report files and write a readable HTML report.
    """
    if output_dir is None:
        output_dir = get_default_html_output_dir()

    output_dir.mkdir(parents=True, exist_ok=True)

    report_data = read_path_report(session_id=session_id)
    html_content = build_html_report(report_data=report_data)

    safe_session_id = (
        session_id
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    output_path = output_dir / f"{safe_session_id}_paid_simulator_report.html"
    output_path.write_text(html_content, encoding="utf-8")

    return str(output_path)
