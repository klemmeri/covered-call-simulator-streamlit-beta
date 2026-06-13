"""
report_reader.py

Read-back utilities for paid Covered Call Simulator CSV reports.

This module verifies that saved paid-simulator outputs can be reused by a
dashboard, public site, report page, or later analysis script.

Default input folder:

    outputs/tables/paid_simulator

Expected files:
    - <session_id>_equity_curve.csv
    - <session_id>_path_summary.csv
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.

    This file lives in:

        app/paid_simulator/report_reader.py

    Therefore, parents[2] is the project root.
    """
    return Path(__file__).resolve().parents[2]


def get_default_output_dir() -> Path:
    """
    Return the default paid-simulator table output directory.
    """
    return get_project_root() / "outputs" / "tables" / "paid_simulator"


def read_csv_rows(input_path: Path) -> list[dict[str, str]]:
    """
    Read a CSV file into a list of dictionaries.

    Parameters
    ----------
    input_path:
        CSV file path.

    Returns
    -------
    list[dict[str, str]]
        CSV rows as dictionaries.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"CSV file not found: {input_path}")

    with input_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)


def parse_number(value: Any) -> float | None:
    """
    Convert a value to float when possible.

    Returns None if the value is missing or not numeric.
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


def read_path_report(
    session_id: str,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Read saved equity-curve and path-summary CSV files.

    Parameters
    ----------
    session_id:
        Session id used when the report files were saved.

    output_dir:
        Optional report directory. If None, the default paid-simulator output
        directory is used.

    Returns
    -------
    dict[str, Any]
        Report file paths and loaded rows.
    """
    if output_dir is None:
        output_dir = get_default_output_dir()

    safe_session_id = (
        session_id
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    equity_curve_path = output_dir / f"{safe_session_id}_equity_curve.csv"
    path_summary_path = output_dir / f"{safe_session_id}_path_summary.csv"

    equity_curve_rows = read_csv_rows(equity_curve_path)
    path_summary_rows = read_csv_rows(path_summary_path)

    return {
        "session_id": session_id,
        "equity_curve_csv": str(equity_curve_path),
        "path_summary_csv": str(path_summary_path),
        "equity_curve_rows": equity_curve_rows,
        "path_summary_rows": path_summary_rows,
    }


def path_summary_rows_to_dict(
    path_summary_rows: list[dict[str, str]],
) -> dict[str, str]:
    """
    Convert name/value summary rows into a dictionary.
    """
    summary: dict[str, str] = {}

    for row in path_summary_rows:
        metric = row.get("metric", "")
        value = row.get("value", "")

        if metric:
            summary[metric] = value

    return summary


def get_last_equity_row(
    equity_curve_rows: list[dict[str, str]],
) -> dict[str, str] | None:
    """
    Return the final equity-curve row.
    """
    if not equity_curve_rows:
        return None

    return equity_curve_rows[-1]


def build_compact_readback_summary(
    report_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a compact summary from a loaded path report.

    This is meant for quick console checks and later dashboard display.
    """
    equity_curve_rows = report_data.get("equity_curve_rows", [])
    path_summary_rows = report_data.get("path_summary_rows", [])

    summary_dict = path_summary_rows_to_dict(path_summary_rows)
    final_row = get_last_equity_row(equity_curve_rows)

    compact_summary: dict[str, Any] = {
        "session_id": report_data.get("session_id"),
        "equity_curve_rows": len(equity_curve_rows),
        "path_summary_rows": len(path_summary_rows),
        "equity_curve_csv": report_data.get("equity_curve_csv"),
        "path_summary_csv": report_data.get("path_summary_csv"),
        "final_covered_call_equity": parse_number(
            summary_dict.get("final_covered_call_equity")
        ),
        "final_buy_hold_equity": parse_number(
            summary_dict.get("final_buy_hold_equity")
        ),
        "covered_call_minus_buy_hold": parse_number(
            summary_dict.get("covered_call_minus_buy_hold")
        ),
        "covered_call_pl_after_entry": parse_number(
            summary_dict.get("covered_call_pl_after_entry")
        ),
        "final_stock_price": parse_number(
            summary_dict.get("final_stock_price")
        ),
    }

    if final_row is not None:
        compact_summary["final_row_step_number"] = parse_number(
            final_row.get("step_number")
        )
        compact_summary["final_row_total_equity"] = parse_number(
            final_row.get("total_equity")
        )
        compact_summary["final_row_benchmark_buy_hold_equity"] = parse_number(
            final_row.get("benchmark_buy_hold_equity")
        )

    return compact_summary


def format_optional_money(value: Any) -> str:
    """
    Format a numeric value as dollars, or return N/A if unavailable.
    """
    number = parse_number(value)

    if number is None:
        return "N/A"

    return f"${number:,.2f}"


def print_readback_check(
    compact_summary: dict[str, Any],
) -> None:
    """
    Print a simple report-readback check.
    """
    print()
    print("Read-back report check")
    print(f"Session id: {compact_summary.get('session_id')}")
    print(f"Equity curve rows: {compact_summary.get('equity_curve_rows')}")
    print(f"Path summary rows: {compact_summary.get('path_summary_rows')}")
    print(
        "Final covered-call equity: "
        f"{format_optional_money(compact_summary.get('final_covered_call_equity'))}"
    )
    print(
        "Final buy-and-hold equity: "
        f"{format_optional_money(compact_summary.get('final_buy_hold_equity'))}"
    )
    print(
        "Covered-call minus buy-and-hold: "
        f"{format_optional_money(compact_summary.get('covered_call_minus_buy_hold'))}"
    )
