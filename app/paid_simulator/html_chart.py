"""
html_chart.py

Lightweight SVG chart utilities for the paid Covered Call Simulator HTML report.

This module creates an embedded SVG equity-curve chart from saved CSV rows.

No external charting library is required.
"""

from __future__ import annotations

from html import escape
from typing import Any


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

    return f"${number:,.0f}"


def get_numeric_series(
    rows: list[dict[str, Any]],
    column: str,
) -> list[float]:
    """
    Extract a numeric series from row dictionaries.
    """
    values: list[float] = []

    for row in rows:
        value = parse_float(row.get(column))

        if value is not None:
            values.append(value)

    return values


def scale_value(
    value: float,
    data_min: float,
    data_max: float,
    output_min: float,
    output_max: float,
) -> float:
    """
    Scale a numeric value from data coordinates to SVG coordinates.
    """
    if data_max == data_min:
        return (output_min + output_max) / 2.0

    fraction = (value - data_min) / (data_max - data_min)
    return output_min + fraction * (output_max - output_min)


def build_path_from_points(
    points: list[tuple[float, float]],
) -> str:
    """
    Build an SVG path from chart points.
    """
    if not points:
        return ""

    commands = [f"M {points[0][0]:.2f} {points[0][1]:.2f}"]

    for x_value, y_value in points[1:]:
        commands.append(f"L {x_value:.2f} {y_value:.2f}")

    return " ".join(commands)


def build_equity_curve_svg_chart(
    equity_curve_rows: list[dict[str, Any]],
    title: str = "Equity curve",
) -> str:
    """
    Build an embedded SVG line chart for covered-call equity versus buy-and-hold.

    Parameters
    ----------
    equity_curve_rows:
        Rows loaded from the paid simulator equity-curve CSV file.

    title:
        Chart title.

    Returns
    -------
    str
        HTML/SVG string.
    """
    if len(equity_curve_rows) < 2:
        return "<p>Not enough equity-curve rows to draw a chart.</p>"

    covered_call_values = get_numeric_series(
        rows=equity_curve_rows,
        column="total_equity",
    )

    buy_hold_values = get_numeric_series(
        rows=equity_curve_rows,
        column="benchmark_buy_hold_equity",
    )

    if not covered_call_values or not buy_hold_values:
        return "<p>Equity-curve values are unavailable.</p>"

    all_values = covered_call_values + buy_hold_values
    data_min = min(all_values)
    data_max = max(all_values)

    data_range = data_max - data_min

    if data_range <= 0:
        data_padding = max(data_max * 0.005, 100.0)
    else:
        data_padding = data_range * 0.10

    y_min = data_min - data_padding
    y_max = data_max + data_padding

    width = 960
    height = 360

    margin_left = 78
    margin_right = 28
    margin_top = 42
    margin_bottom = 56

    plot_left = margin_left
    plot_right = width - margin_right
    plot_top = margin_top
    plot_bottom = height - margin_bottom

    step_count = len(equity_curve_rows)

    covered_call_points: list[tuple[float, float]] = []
    buy_hold_points: list[tuple[float, float]] = []

    for index, row in enumerate(equity_curve_rows):
        x_value = scale_value(
            value=index,
            data_min=0,
            data_max=max(step_count - 1, 1),
            output_min=plot_left,
            output_max=plot_right,
        )

        covered_call_equity = parse_float(row.get("total_equity"))
        buy_hold_equity = parse_float(row.get("benchmark_buy_hold_equity"))

        if covered_call_equity is not None:
            y_value = scale_value(
                value=covered_call_equity,
                data_min=y_min,
                data_max=y_max,
                output_min=plot_bottom,
                output_max=plot_top,
            )
            covered_call_points.append((x_value, y_value))

        if buy_hold_equity is not None:
            y_value = scale_value(
                value=buy_hold_equity,
                data_min=y_min,
                data_max=y_max,
                output_min=plot_bottom,
                output_max=plot_top,
            )
            buy_hold_points.append((x_value, y_value))

    covered_call_path = build_path_from_points(covered_call_points)
    buy_hold_path = build_path_from_points(buy_hold_points)

    grid_lines: list[str] = []
    y_labels: list[str] = []

    grid_count = 5

    for grid_index in range(grid_count + 1):
        fraction = grid_index / grid_count
        y_position = plot_bottom - fraction * (plot_bottom - plot_top)
        value = y_min + fraction * (y_max - y_min)

        grid_lines.append(
            f'<line x1="{plot_left}" y1="{y_position:.2f}" '
            f'x2="{plot_right}" y2="{y_position:.2f}" '
            f'class="chart-grid-line" />'
        )

        y_labels.append(
            f'<text x="{plot_left - 10}" y="{y_position + 4:.2f}" '
            f'class="chart-axis-label" text-anchor="end">{escape(format_money(value))}</text>'
        )

    x_labels: list[str] = []

    for index, row in enumerate(equity_curve_rows):
        step_number = row.get("step_number", index + 1)

        x_position = scale_value(
            value=index,
            data_min=0,
            data_max=max(step_count - 1, 1),
            output_min=plot_left,
            output_max=plot_right,
        )

        x_labels.append(
            f'<text x="{x_position:.2f}" y="{plot_bottom + 28}" '
            f'class="chart-axis-label" text-anchor="middle">{escape(str(step_number))}</text>'
        )

    final_covered_call = covered_call_values[-1]
    final_buy_hold = buy_hold_values[-1]

    svg = f"""
<div class="chart-card">
    <div class="chart-title">{escape(title)}</div>
    <div class="chart-subtitle">
        Covered-call equity versus buy-and-hold benchmark across the simulated path.
    </div>

    <svg viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">
        <style>
            .chart-bg {{
                fill: #ffffff;
            }}

            .chart-grid-line {{
                stroke: #e2e8f0;
                stroke-width: 1;
            }}

            .chart-axis {{
                stroke: #94a3b8;
                stroke-width: 1.2;
            }}

            .chart-axis-label {{
                fill: #475569;
                font-size: 12px;
                font-family: Arial, Helvetica, sans-serif;
            }}

            .chart-covered-line {{
                fill: none;
                stroke: #0f172a;
                stroke-width: 3;
                stroke-linecap: round;
                stroke-linejoin: round;
            }}

            .chart-benchmark-line {{
                fill: none;
                stroke: #64748b;
                stroke-width: 3;
                stroke-dasharray: 7 5;
                stroke-linecap: round;
                stroke-linejoin: round;
            }}

            .chart-point-covered {{
                fill: #0f172a;
            }}

            .chart-point-benchmark {{
                fill: #64748b;
            }}

            .chart-legend-text {{
                fill: #334155;
                font-size: 13px;
                font-family: Arial, Helvetica, sans-serif;
            }}
        </style>

        <rect class="chart-bg" x="0" y="0" width="{width}" height="{height}" rx="12" />

        {''.join(grid_lines)}
        {''.join(y_labels)}

        <line x1="{plot_left}" y1="{plot_bottom}" x2="{plot_right}" y2="{plot_bottom}" class="chart-axis" />
        <line x1="{plot_left}" y1="{plot_top}" x2="{plot_left}" y2="{plot_bottom}" class="chart-axis" />

        {''.join(x_labels)}

        <path d="{covered_call_path}" class="chart-covered-line" />
        <path d="{buy_hold_path}" class="chart-benchmark-line" />

        {''.join(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" class="chart-point-covered" />'
            for x, y in covered_call_points
        )}

        {''.join(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" class="chart-point-benchmark" />'
            for x, y in buy_hold_points
        )}

        <line x1="{plot_left}" y1="18" x2="{plot_left + 36}" y2="18" class="chart-covered-line" />
        <text x="{plot_left + 46}" y="22" class="chart-legend-text">
            Covered call ({escape(format_money(final_covered_call))})
        </text>

        <line x1="{plot_left + 260}" y1="18" x2="{plot_left + 296}" y2="18" class="chart-benchmark-line" />
        <text x="{plot_left + 306}" y="22" class="chart-legend-text">
            Buy-and-hold ({escape(format_money(final_buy_hold))})
        </text>

        <text x="{(plot_left + plot_right) / 2:.2f}" y="{height - 12}" class="chart-axis-label" text-anchor="middle">
            Simulated path step
        </text>
    </svg>
</div>
"""

    return svg
