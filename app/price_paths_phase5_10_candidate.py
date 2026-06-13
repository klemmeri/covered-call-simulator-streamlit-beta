"""
price_paths_phase5_10_candidate.py

Candidate replacement for app/price_paths.py.

Purpose
-------
This file is a guarded Phase 5-10 integration candidate. It is intentionally
not installed over app/price_paths.py by the package. The companion check script
validates that this candidate can support both:

1. the existing synthetic-default workflow, and
2. an explicit historical_import workflow using Phase 5 historical-path artifacts.

Design rules
------------
- Synthetic mode remains the default.
- Historical-import mode must be explicitly requested.
- Unknown modes fall back to synthetic.
- The public function name generate_price_paths(config) is preserved.
- The return format is a pandas DataFrame with normalized columns:
      path_id, step, price

The next checkpoint can decide whether to promote this candidate into the live
app/price_paths.py file after reviewing compatibility with the rest of the engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import math
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
INPUT_MARKET_DATA_DIR = PROJECT_ROOT / "inputs" / "market_data"

DEFAULT_HISTORICAL_PATH = OUTPUT_TABLES_DIR / "phase5_2_engine_ready_historical_path.csv"
FALLBACK_HISTORICAL_PATH = OUTPUT_TABLES_DIR / "phase4_4_historical_price_path.csv"
FALLBACK_UNDERLYING_PRICE_INPUT = INPUT_MARKET_DATA_DIR / "sample_underlying_prices.csv"

SYNTHETIC_DEFAULT_MODE = "synthetic"
HISTORICAL_IMPORT_MODE = "historical_import"


_PRICE_COLUMN_CANDIDATES = [
    "price",
    "close",
    "Close",
    "last",
    "Last",
    "underlying_price",
    "Underlying Price",
    "mark",
    "mid",
]


def _get_config_value(config: Any, names: list[str], default: Any) -> Any:
    """Read a value from either a dict-like config or an attribute config."""
    for name in names:
        if isinstance(config, dict) and name in config:
            value = config.get(name)
            if value is not None:
                return value
        if hasattr(config, name):
            value = getattr(config, name)
            if value is not None:
                return value
    return default


def _coerce_float(value: Any, default: float) -> float:
    try:
        numeric = float(value)
        if math.isfinite(numeric):
            return numeric
    except Exception:
        pass
    return default


def _coerce_int(value: Any, default: int, minimum: int = 1) -> int:
    try:
        numeric = int(value)
        return max(minimum, numeric)
    except Exception:
        return max(minimum, default)


def resolve_price_path_mode(config: Any) -> str:
    """
    Resolve the requested price-path mode.

    Supported modes:
    - synthetic
    - historical_import

    Any missing or unknown mode falls back to synthetic.
    """
    requested = _get_config_value(
        config,
        [
            "price_path_mode",
            "path_mode",
            "market_data_mode",
            "data_source_mode",
            "source_mode",
        ],
        SYNTHETIC_DEFAULT_MODE,
    )
    requested_text = str(requested).strip().lower()
    if requested_text == HISTORICAL_IMPORT_MODE:
        return HISTORICAL_IMPORT_MODE
    return SYNTHETIC_DEFAULT_MODE


def _find_price_column(df: pd.DataFrame) -> str | None:
    for column in _PRICE_COLUMN_CANDIDATES:
        if column in df.columns:
            return column
    return None


def _read_historical_source(config: Any) -> pd.DataFrame:
    """Read the best available explicit historical price source."""
    configured_path = _get_config_value(
        config,
        ["historical_path_file", "historical_price_path_file", "market_data_price_file"],
        None,
    )

    candidate_paths: list[Path] = []
    if configured_path:
        candidate_paths.append(Path(str(configured_path)))
    candidate_paths.extend([
        DEFAULT_HISTORICAL_PATH,
        FALLBACK_HISTORICAL_PATH,
        FALLBACK_UNDERLYING_PRICE_INPUT,
    ])

    for path in candidate_paths:
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.exists():
            try:
                df = pd.read_csv(path)
                if not df.empty:
                    return df
            except Exception:
                continue

    return pd.DataFrame()


def generate_historical_price_paths(config: Any) -> pd.DataFrame:
    """
    Generate an engine-ready price-path DataFrame from imported historical data.
    """
    source_df = _read_historical_source(config)
    if source_df.empty:
        return generate_synthetic_price_paths(config)

    price_column = _find_price_column(source_df)
    if price_column is None:
        return generate_synthetic_price_paths(config)

    prices = pd.to_numeric(source_df[price_column], errors="coerce").dropna()
    prices = prices[prices > 0]
    if prices.empty:
        return generate_synthetic_price_paths(config)

    out = pd.DataFrame()
    out["path_id"] = source_df.get("path_id", "historical_path_001")
    if isinstance(out["path_id"], pd.Series):
        out["path_id"] = out["path_id"].fillna("historical_path_001").astype(str)
    else:
        out["path_id"] = "historical_path_001"

    out["step"] = range(1, len(source_df) + 1)
    if "step" in source_df.columns:
        step_series = pd.to_numeric(source_df["step"], errors="coerce")
        fallback = pd.Series(range(1, len(source_df) + 1), index=source_df.index)
        out["step"] = step_series.fillna(fallback).astype(int)

    out["price"] = pd.to_numeric(source_df[price_column], errors="coerce")
    out = out.dropna(subset=["price"])
    out = out[out["price"] > 0]
    if out.empty:
        return generate_synthetic_price_paths(config)

    out["path_id"] = out["path_id"].replace({"": "historical_path_001", "nan": "historical_path_001"})
    out["path_id"] = out["path_id"].fillna("historical_path_001")
    out["source_mode"] = HISTORICAL_IMPORT_MODE
    return out[["path_id", "step", "price", "source_mode"]].reset_index(drop=True)


def generate_synthetic_price_paths(config: Any) -> pd.DataFrame:
    """
    Generate deterministic synthetic price paths.

    This candidate uses a deterministic drift path rather than a random Monte
    Carlo path so that regression checks remain stable.
    """
    num_paths = _coerce_int(
        _get_config_value(config, ["num_paths", "number_of_paths", "paths"], 1),
        1,
    )
    steps = _coerce_int(
        _get_config_value(config, ["steps", "num_steps", "trading_days", "days", "target_dte"], 30),
        30,
    )
    initial_price = _coerce_float(
        _get_config_value(
            config,
            ["initial_price", "demo_price", "stock_price", "underlying_price", "start_price"],
            545.25,
        ),
        545.25,
    )
    annual_drift = _coerce_float(
        _get_config_value(config, ["annual_drift", "expected_return", "drift"], 0.06),
        0.06,
    )
    trading_days = _coerce_float(
        _get_config_value(config, ["trading_days_per_year"], 252),
        252,
    )
    daily_drift = annual_drift / trading_days

    rows: list[dict[str, Any]] = []
    for path_number in range(1, num_paths + 1):
        price = initial_price
        for step in range(1, steps + 1):
            if step > 1:
                price *= 1.0 + daily_drift
            rows.append(
                {
                    "path_id": f"synthetic_path_{path_number:03d}",
                    "step": step,
                    "price": round(float(price), 6),
                    "source_mode": SYNTHETIC_DEFAULT_MODE,
                }
            )
    return pd.DataFrame(rows)


def generate_price_paths(config: Any) -> pd.DataFrame:
    """
    Public engine function preserved for backward compatibility.

    Synthetic mode is the default. Historical mode is explicit only.
    """
    mode = resolve_price_path_mode(config)
    if mode == HISTORICAL_IMPORT_MODE:
        return generate_historical_price_paths(config)
    return generate_synthetic_price_paths(config)


if __name__ == "__main__":
    demo = generate_price_paths({"price_path_mode": "synthetic", "num_paths": 1, "steps": 5})
    print(demo)
