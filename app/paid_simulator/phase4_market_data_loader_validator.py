"""
phase4_market_data_loader_validator.py

Phase 4-3 market-data loader and schema validator for the Covered Call Simulator.

This module is intentionally scaffolded and conservative. It loads the Phase 4-2
sample market-data CSV files, validates the required schema and basic data-quality
rules, and writes customer/developer-readable validation outputs.

No dashboard changes are made in this phase.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import json

import pandas as pd


READY_MARKER = "PHASE4_3_MARKET_DATA_LOADER_VALIDATOR_READY"
RELEASE_DECISION = "PHASE4_3_MARKET_DATA_LOADER_VALIDATOR_CREATED_NO_DASHBOARD_CHANGE"
DASHBOARD_CHANGE_REQUIRED = False


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "inputs" / "market_data"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

UNDERLYING_PRICE_FILE = INPUT_DIR / "sample_underlying_prices.csv"
OPTION_CHAIN_FILE = INPUT_DIR / "sample_option_chain.csv"


UNDERLYING_REQUIRED_COLUMNS = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "volume",
]

OPTION_CHAIN_REQUIRED_COLUMNS = [
    "quote_date",
    "ticker",
    "expiration_date",
    "option_type",
    "strike",
    "bid",
    "ask",
    "mid",
    "delta",
    "iv",
    "volume",
    "open_interest",
]


@dataclass
class ValidationIssue:
    dataset: str
    severity: str
    rule: str
    column: str
    message: str
    row_count: int = 0


@dataclass
class DatasetValidationResult:
    dataset: str
    file_path: str
    file_exists: bool
    row_count: int
    column_count: int
    required_column_count: int
    missing_required_columns: list[str]
    issue_count: int
    error_count: int
    warning_count: int
    status: str


@dataclass
class Phase43ValidationResult:
    ready_marker: str
    release_decision: str
    dashboard_change_required: bool
    overall_status: str
    underlying: DatasetValidationResult
    option_chain: DatasetValidationResult
    issues: list[ValidationIssue]
    output_files: dict[str, str]


def _ensure_output_dirs() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)


def _read_csv_if_exists(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _append_issue(
    issues: list[ValidationIssue],
    dataset: str,
    severity: str,
    rule: str,
    column: str,
    message: str,
    row_count: int = 0,
) -> None:
    issues.append(
        ValidationIssue(
            dataset=dataset,
            severity=severity,
            rule=rule,
            column=column,
            message=message,
            row_count=int(row_count),
        )
    )


def _validate_required_columns(
    df: pd.DataFrame,
    dataset: str,
    required_columns: list[str],
    issues: list[ValidationIssue],
) -> list[str]:
    missing = [column for column in required_columns if column not in df.columns]
    for column in missing:
        _append_issue(
            issues=issues,
            dataset=dataset,
            severity="ERROR",
            rule="required_column",
            column=column,
            message=f"Missing required column: {column}",
            row_count=0,
        )
    return missing


def _validate_parseable_dates(
    df: pd.DataFrame,
    dataset: str,
    date_columns: list[str],
    issues: list[ValidationIssue],
) -> None:
    for column in date_columns:
        if column not in df.columns:
            continue
        parsed = pd.to_datetime(df[column], errors="coerce")
        invalid_count = int(parsed.isna().sum())
        if invalid_count > 0:
            _append_issue(
                issues=issues,
                dataset=dataset,
                severity="ERROR",
                rule="parseable_date",
                column=column,
                message=f"Column {column} contains {invalid_count} unparseable date value(s).",
                row_count=invalid_count,
            )


def _validate_numeric_columns(
    df: pd.DataFrame,
    dataset: str,
    numeric_columns: list[str],
    issues: list[ValidationIssue],
) -> None:
    for column in numeric_columns:
        if column not in df.columns:
            continue
        numeric = pd.to_numeric(df[column], errors="coerce")
        invalid_count = int(numeric.isna().sum())
        if invalid_count > 0:
            _append_issue(
                issues=issues,
                dataset=dataset,
                severity="ERROR",
                rule="numeric",
                column=column,
                message=f"Column {column} contains {invalid_count} non-numeric value(s).",
                row_count=invalid_count,
            )


def _validate_non_negative(
    df: pd.DataFrame,
    dataset: str,
    columns: list[str],
    issues: list[ValidationIssue],
) -> None:
    for column in columns:
        if column not in df.columns:
            continue
        numeric = pd.to_numeric(df[column], errors="coerce")
        negative_count = int((numeric < 0).sum())
        if negative_count > 0:
            _append_issue(
                issues=issues,
                dataset=dataset,
                severity="ERROR",
                rule="non_negative",
                column=column,
                message=f"Column {column} contains {negative_count} negative value(s).",
                row_count=negative_count,
            )


def _validate_underlying_ohlc(df: pd.DataFrame, issues: list[ValidationIssue]) -> None:
    required = ["open", "high", "low", "close"]
    if any(column not in df.columns for column in required):
        return

    open_ = pd.to_numeric(df["open"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    close = pd.to_numeric(df["close"], errors="coerce")

    high_too_low = int(((high < open_) | (high < close) | (high < low)).sum())
    low_too_high = int(((low > open_) | (low > close) | (low > high)).sum())

    if high_too_low > 0:
        _append_issue(
            issues,
            "underlying_prices",
            "ERROR",
            "ohlc_consistency",
            "high",
            "High is below open, close, or low for one or more rows.",
            high_too_low,
        )

    if low_too_high > 0:
        _append_issue(
            issues,
            "underlying_prices",
            "ERROR",
            "ohlc_consistency",
            "low",
            "Low is above open, close, or high for one or more rows.",
            low_too_high,
        )


def _validate_option_chain_specific_rules(df: pd.DataFrame, issues: list[ValidationIssue]) -> None:
    if "option_type" in df.columns:
        values = df["option_type"].astype(str).str.upper().str.strip()
        invalid_count = int((~values.isin(["C", "P", "CALL", "PUT"])).sum())
        if invalid_count > 0:
            _append_issue(
                issues,
                "option_chain",
                "ERROR",
                "option_type",
                "option_type",
                "Option type must be C, P, CALL, or PUT.",
                invalid_count,
            )

    if "bid" in df.columns and "ask" in df.columns:
        bid = pd.to_numeric(df["bid"], errors="coerce")
        ask = pd.to_numeric(df["ask"], errors="coerce")
        crossed_count = int((bid > ask).sum())
        if crossed_count > 0:
            _append_issue(
                issues,
                "option_chain",
                "ERROR",
                "bid_ask_order",
                "bid/ask",
                "Bid exceeds ask for one or more rows.",
                crossed_count,
            )

    if "mid" in df.columns and "bid" in df.columns and "ask" in df.columns:
        bid = pd.to_numeric(df["bid"], errors="coerce")
        ask = pd.to_numeric(df["ask"], errors="coerce")
        mid = pd.to_numeric(df["mid"], errors="coerce")
        outside_mid_count = int(((mid < bid) | (mid > ask)).sum())
        if outside_mid_count > 0:
            _append_issue(
                issues,
                "option_chain",
                "WARNING",
                "mid_inside_market",
                "mid",
                "Mid price is outside the bid/ask range for one or more rows.",
                outside_mid_count,
            )

    if "delta" in df.columns:
        delta = pd.to_numeric(df["delta"], errors="coerce")
        outside_delta_count = int(((delta < -1) | (delta > 1)).sum())
        if outside_delta_count > 0:
            _append_issue(
                issues,
                "option_chain",
                "ERROR",
                "delta_range",
                "delta",
                "Delta must be between -1 and +1.",
                outside_delta_count,
            )

    if "iv" in df.columns:
        iv = pd.to_numeric(df["iv"], errors="coerce")
        negative_iv_count = int((iv < 0).sum())
        if negative_iv_count > 0:
            _append_issue(
                issues,
                "option_chain",
                "ERROR",
                "iv_non_negative",
                "iv",
                "Implied volatility must be non-negative.",
                negative_iv_count,
            )


def _summarize_dataset(
    dataset: str,
    file_path: Path,
    df: pd.DataFrame,
    required_columns: list[str],
    missing_required_columns: list[str],
    issues: list[ValidationIssue],
) -> DatasetValidationResult:
    dataset_issues = [issue for issue in issues if issue.dataset == dataset]
    error_count = sum(1 for issue in dataset_issues if issue.severity == "ERROR")
    warning_count = sum(1 for issue in dataset_issues if issue.severity == "WARNING")

    if not file_path.exists():
        status = "FAIL_FILE_MISSING"
    elif missing_required_columns or error_count > 0:
        status = "FAIL_SCHEMA_OR_DATA_QUALITY"
    elif warning_count > 0:
        status = "PASS_WITH_WARNINGS"
    else:
        status = "PASS"

    return DatasetValidationResult(
        dataset=dataset,
        file_path=str(file_path),
        file_exists=file_path.exists(),
        row_count=int(len(df.index)),
        column_count=int(len(df.columns)),
        required_column_count=len(required_columns),
        missing_required_columns=missing_required_columns,
        issue_count=len(dataset_issues),
        error_count=error_count,
        warning_count=warning_count,
        status=status,
    )


def validate_market_data(
    underlying_price_file: Path = UNDERLYING_PRICE_FILE,
    option_chain_file: Path = OPTION_CHAIN_FILE,
) -> Phase43ValidationResult:
    """
    Load and validate the Phase 4 market-data CSV inputs.

    Returns a structured validation result and writes report/table artifacts.
    """
    _ensure_output_dirs()

    issues: list[ValidationIssue] = []

    underlying_df = _read_csv_if_exists(underlying_price_file)
    option_chain_df = _read_csv_if_exists(option_chain_file)

    if not underlying_price_file.exists():
        _append_issue(
            issues,
            "underlying_prices",
            "ERROR",
            "file_exists",
            "file",
            f"Missing input file: {underlying_price_file}",
            0,
        )

    if not option_chain_file.exists():
        _append_issue(
            issues,
            "option_chain",
            "ERROR",
            "file_exists",
            "file",
            f"Missing input file: {option_chain_file}",
            0,
        )

    underlying_missing = _validate_required_columns(
        underlying_df,
        "underlying_prices",
        UNDERLYING_REQUIRED_COLUMNS,
        issues,
    )
    option_chain_missing = _validate_required_columns(
        option_chain_df,
        "option_chain",
        OPTION_CHAIN_REQUIRED_COLUMNS,
        issues,
    )

    _validate_parseable_dates(underlying_df, "underlying_prices", ["date"], issues)
    _validate_numeric_columns(
        underlying_df,
        "underlying_prices",
        ["open", "high", "low", "close", "volume"],
        issues,
    )
    _validate_non_negative(
        underlying_df,
        "underlying_prices",
        ["open", "high", "low", "close", "volume"],
        issues,
    )
    _validate_underlying_ohlc(underlying_df, issues)

    _validate_parseable_dates(option_chain_df, "option_chain", ["quote_date", "expiration_date"], issues)
    _validate_numeric_columns(
        option_chain_df,
        "option_chain",
        ["strike", "bid", "ask", "mid", "delta", "iv", "volume", "open_interest"],
        issues,
    )
    _validate_non_negative(
        option_chain_df,
        "option_chain",
        ["strike", "bid", "ask", "mid", "iv", "volume", "open_interest"],
        issues,
    )
    _validate_option_chain_specific_rules(option_chain_df, issues)

    underlying_summary = _summarize_dataset(
        dataset="underlying_prices",
        file_path=underlying_price_file,
        df=underlying_df,
        required_columns=UNDERLYING_REQUIRED_COLUMNS,
        missing_required_columns=underlying_missing,
        issues=issues,
    )
    option_chain_summary = _summarize_dataset(
        dataset="option_chain",
        file_path=option_chain_file,
        df=option_chain_df,
        required_columns=OPTION_CHAIN_REQUIRED_COLUMNS,
        missing_required_columns=option_chain_missing,
        issues=issues,
    )

    error_count = sum(1 for issue in issues if issue.severity == "ERROR")
    warning_count = sum(1 for issue in issues if issue.severity == "WARNING")
    if error_count > 0:
        overall_status = "FAIL"
    elif warning_count > 0:
        overall_status = "PASS_WITH_WARNINGS"
    else:
        overall_status = "PASS"

    issues_csv = TABLE_DIR / "phase4_3_market_data_validation_issues.csv"
    summary_csv = TABLE_DIR / "phase4_3_market_data_validation_summary.csv"
    json_path = REPORT_DIR / "phase4_3_market_data_validation.json"
    report_path = REPORT_DIR / "phase4_3_market_data_validation_report.txt"

    issue_rows = [asdict(issue) for issue in issues]
    if issue_rows:
        pd.DataFrame(issue_rows).to_csv(issues_csv, index=False)
    else:
        pd.DataFrame(
            columns=["dataset", "severity", "rule", "column", "message", "row_count"]
        ).to_csv(issues_csv, index=False)

    summary_rows = [asdict(underlying_summary), asdict(option_chain_summary)]
    pd.DataFrame(summary_rows).to_csv(summary_csv, index=False)

    output_files = {
        "json": str(json_path),
        "report": str(report_path),
        "summary_csv": str(summary_csv),
        "issues_csv": str(issues_csv),
    }

    result = Phase43ValidationResult(
        ready_marker=READY_MARKER,
        release_decision=RELEASE_DECISION,
        dashboard_change_required=DASHBOARD_CHANGE_REQUIRED,
        overall_status=overall_status,
        underlying=underlying_summary,
        option_chain=option_chain_summary,
        issues=issues,
        output_files=output_files,
    )

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(_to_jsonable(result), f, indent=2)

    report_path.write_text(_build_text_report(result), encoding="utf-8")

    return result


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _to_jsonable(val) for key, val in asdict(value).items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_jsonable(val) for key, val in value.items()}
    return value


def _build_text_report(result: Phase43ValidationResult) -> str:
    lines: list[str] = []
    lines.append("Phase 4-3 Market-Data Loader and Schema Validator")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Ready marker:              {result.ready_marker}")
    lines.append(f"Release decision:          {result.release_decision}")
    lines.append(f"Dashboard change required: {result.dashboard_change_required}")
    lines.append(f"Overall status:            {result.overall_status}")
    lines.append("")
    lines.append("Dataset summary")
    lines.append("-" * 72)
    for dataset in [result.underlying, result.option_chain]:
        lines.append(f"Dataset:             {dataset.dataset}")
        lines.append(f"File:                {dataset.file_path}")
        lines.append(f"File exists:         {dataset.file_exists}")
        lines.append(f"Rows:                {dataset.row_count}")
        lines.append(f"Columns:             {dataset.column_count}")
        lines.append(f"Required columns:    {dataset.required_column_count}")
        lines.append(f"Missing required:    {dataset.missing_required_columns}")
        lines.append(f"Issues:              {dataset.issue_count}")
        lines.append(f"Errors:              {dataset.error_count}")
        lines.append(f"Warnings:            {dataset.warning_count}")
        lines.append(f"Status:              {dataset.status}")
        lines.append("")

    lines.append("Validation issues")
    lines.append("-" * 72)
    if not result.issues:
        lines.append("No validation issues found.")
    else:
        for issue in result.issues:
            lines.append(
                f"{issue.severity:7s} | {issue.dataset:18s} | {issue.rule:22s} | "
                f"{issue.column:12s} | rows={issue.row_count} | {issue.message}"
            )

    lines.append("")
    lines.append("Output files")
    lines.append("-" * 72)
    for label, path in result.output_files.items():
        lines.append(f"{label:12s}: {path}")

    lines.append("")
    lines.append("Interpretation")
    lines.append("-" * 72)
    lines.append(
        "This checkpoint confirms that the project can load the market-data CSV "
        "inputs created in Phase 4-2 and validate their schema before any future "
        "historical-path or option-chain premium logic consumes them."
    )
    lines.append(
        "This is intentionally not a regime detector and should not be treated as "
        "market guidance. It is a data-quality gate."
    )

    return "\n".join(lines) + "\n"


def build_phase4_3_summary() -> dict[str, Any]:
    """
    Small helper used by checkpoint scripts and future dashboard integration tests.
    """
    result = validate_market_data()
    return _to_jsonable(result)


if __name__ == "__main__":
    validation_result = validate_market_data()
    print(_build_text_report(validation_result))
