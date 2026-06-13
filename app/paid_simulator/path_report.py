"""
path_report.py

CSV report output for the paid Covered Call Simulator.

This module saves the multi-step path results so the paid simulator produces
usable output files instead of only printing to the PyCharm console.

Default output folder:

    outputs/tables/paid_simulator

Files created:
    - <session_id>_equity_curve.csv
    - <session_id>_path_summary.csv

This is intentionally lightweight and uses only the Python standard library.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from models import EquitySnapshot


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.

    This file lives in:

        app/paid_simulator/path_report.py

    Therefore, parents[2] is the project root.
    """
    return Path(__file__).resolve().parents[2]


def get_default_output_dir() -> Path:
    """
    Return the default paid-simulator table output directory.
    """
    return get_project_root() / "outputs" / "tables" / "paid_simulator"


def serialize_value(value: Any) -> Any:
    """
    Convert values into CSV-friendly representations.

    Datetime values are converted to ISO strings. Other values are left alone.
    """
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")

    return value


def write_csv_rows(
    output_path: Path,
    rows: list[dict[str, Any]],
) -> None:
    """
    Write a list of dictionaries to a CSV file.

    Parameters
    ----------
    output_path:
        Destination CSV path.

    rows:
        Rows to write. If rows is empty, an empty file with no header is created.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    key: serialize_value(value)
                    for key, value in row.items()
                }
            )


def equity_snapshots_to_rows(
    equity_snapshots: list[EquitySnapshot],
) -> list[dict[str, Any]]:
    """
    Convert equity snapshots into CSV rows.
    """
    rows: list[dict[str, Any]] = []

    for snapshot in equity_snapshots:
        rows.append(
            {
                "session_id": snapshot.session_id,
                "timestamp": snapshot.timestamp,
                "step_number": snapshot.step_number,
                "stock_price": snapshot.stock_price,
                "cash": snapshot.cash,
                "stock_value": snapshot.stock_value,
                "short_call_value": snapshot.short_call_value,
                "total_equity": snapshot.total_equity,
                "premium_collected_to_date": snapshot.premium_collected_to_date,
                "realized_option_pl": snapshot.realized_option_pl,
                "unrealized_option_pl": snapshot.unrealized_option_pl,
                "missed_upside": snapshot.missed_upside,
                "benchmark_buy_hold_equity": snapshot.benchmark_buy_hold_equity,
                "benchmark_rule_equity": snapshot.benchmark_rule_equity,
            }
        )

    return rows


def path_summary_to_rows(
    path_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Convert a path-summary dictionary into name/value CSV rows.
    """
    rows: list[dict[str, Any]] = []

    for key, value in path_summary.items():
        rows.append(
            {
                "metric": key,
                "value": value,
            }
        )

    return rows


def save_path_report(
    equity_snapshots: list[EquitySnapshot],
    path_summary: dict[str, Any],
    output_dir: Path | None = None,
    session_id: str | None = None,
) -> dict[str, str]:
    """
    Save the equity curve and path summary to CSV files.

    Parameters
    ----------
    equity_snapshots:
        Multi-step equity snapshots.

    path_summary:
        Summary dictionary from path_runner.summarize_path_result().

    output_dir:
        Optional output directory. If None, the default paid-simulator output
        directory is used.

    session_id:
        Optional session id for file naming. If None, the session id is taken
        from path_summary or from the first equity snapshot.

    Returns
    -------
    dict[str, str]
        Paths to the saved CSV files as strings.
    """
    if output_dir is None:
        output_dir = get_default_output_dir()

    if session_id is None:
        session_id = str(path_summary.get("session_id", "")).strip()

    if not session_id and equity_snapshots:
        session_id = equity_snapshots[0].session_id

    if not session_id:
        session_id = "paid_simulator_session"

    safe_session_id = (
        session_id
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    equity_curve_path = output_dir / f"{safe_session_id}_equity_curve.csv"
    path_summary_path = output_dir / f"{safe_session_id}_path_summary.csv"

    write_csv_rows(
        output_path=equity_curve_path,
        rows=equity_snapshots_to_rows(equity_snapshots),
    )

    write_csv_rows(
        output_path=path_summary_path,
        rows=path_summary_to_rows(path_summary),
    )

    return {
        "equity_curve_csv": str(equity_curve_path),
        "path_summary_csv": str(path_summary_path),
    }
