"""
simulator_phase5_13_candidate.py

Phase 5-13 simulator-engine integration candidate for the Covered Call Simulator.

This is a candidate file only. It does not replace app/simulator.py.

Purpose
-------
Preserve the existing synthetic-default simulator behavior while documenting and
exercising the future hook where imported historical paths can be passed into the
simulation engine explicitly.

Design rules
------------
1. Synthetic mode remains the default.
2. Historical-import mode must be explicit.
3. Unknown modes fall back to synthetic.
4. The candidate exposes a SimulationEngine class with a run() method.
5. The candidate is deliberately simple and conservative for checkpointing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENGINE_READY_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase5_2_engine_ready_historical_path.csv"


VALID_MODES = {"synthetic", "historical_import"}
DEFAULT_MODE = "synthetic"


@dataclass
class CandidateSimulationConfig:
    ticker: str = "SPY"
    account_size: float = 100000.0
    data_mode: str = DEFAULT_MODE
    number_of_paths: int = 1
    starting_price: float = 545.25
    drift_per_step: float = 0.0
    steps: int = 1


def _get_config_value(config: Any, name: str, default: Any) -> Any:
    if isinstance(config, dict):
        return config.get(name, default)
    return getattr(config, name, default)


def normalize_data_mode(requested_mode: str | None) -> str:
    if requested_mode in VALID_MODES:
        return requested_mode
    return DEFAULT_MODE


def _build_synthetic_path(config: Any) -> pd.DataFrame:
    starting_price = float(_get_config_value(config, "starting_price", 545.25))
    steps = int(_get_config_value(config, "steps", 1) or 1)
    drift_per_step = float(_get_config_value(config, "drift_per_step", 0.0))
    rows = []
    for step in range(1, steps + 1):
        price = starting_price + (step - 1) * drift_per_step
        rows.append(
            {
                "path_id": "synthetic_path_001",
                "step": step,
                "price": price,
                "close": price,
                "source_mode": "synthetic",
            }
        )
    return pd.DataFrame(rows)


def _build_historical_path() -> pd.DataFrame:
    if not ENGINE_READY_PATH.exists():
        return _build_synthetic_path(CandidateSimulationConfig())

    df = pd.read_csv(ENGINE_READY_PATH)
    if df.empty:
        return _build_synthetic_path(CandidateSimulationConfig())

    price_col = None
    for candidate in ["price", "close", "underlying_price", "last_price"]:
        if candidate in df.columns:
            price_col = candidate
            break

    if price_col is None:
        return _build_synthetic_path(CandidateSimulationConfig())

    out = pd.DataFrame()
    out["path_id"] = df["path_id"] if "path_id" in df.columns else "historical_path_001"
    out["step"] = pd.to_numeric(df["step"], errors="coerce") if "step" in df.columns else range(1, len(df) + 1)
    fallback_steps = pd.Series(range(1, len(out) + 1), index=out.index)
    out["step"] = pd.to_numeric(out["step"], errors="coerce").fillna(fallback_steps).astype(int)
    out["price"] = pd.to_numeric(df[price_col], errors="coerce").ffill().bfill().fillna(0.0)
    out["close"] = out["price"]
    out["source_mode"] = "historical_import"
    return out


class SimulationEngine:
    """Minimal candidate engine preserving the public run() shape."""

    def __init__(self, config: Any):
        self.config = config
        self.selected_mode = normalize_data_mode(_get_config_value(config, "data_mode", DEFAULT_MODE))
        self.path_results_df = pd.DataFrame()
        self.cycle_results_df = pd.DataFrame()

    def run(self) -> pd.DataFrame:
        if self.selected_mode == "historical_import":
            path_df = _build_historical_path()
        else:
            path_df = _build_synthetic_path(self.config)

        if path_df.empty:
            path_df = _build_synthetic_path(self.config)

        first_price = float(path_df["price"].iloc[0])
        last_price = float(path_df["price"].iloc[-1])
        total_return = (last_price - first_price) / first_price if first_price else 0.0

        self.path_results_df = pd.DataFrame(
            [
                {
                    "path_id": str(path_df["path_id"].iloc[0]),
                    "source_mode": str(path_df["source_mode"].iloc[0]),
                    "selected_mode": self.selected_mode,
                    "start_price": first_price,
                    "end_price": last_price,
                    "total_return": total_return,
                    "row_count": int(len(path_df)),
                }
            ]
        )
        self.cycle_results_df = pd.DataFrame(
            [
                {
                    "path_id": str(path_df["path_id"].iloc[0]),
                    "cycle": 1,
                    "source_mode": str(path_df["source_mode"].iloc[0]),
                    "start_price": first_price,
                    "end_price": last_price,
                }
            ]
        )
        return self.path_results_df


def run_candidate_simulation(config: Any | None = None, requested_mode: str | None = None) -> dict[str, Any]:
    if config is None:
        config = CandidateSimulationConfig()
    if requested_mode is not None:
        if isinstance(config, dict):
            config = dict(config)
            config["data_mode"] = requested_mode
        else:
            setattr(config, "data_mode", requested_mode)

    engine = SimulationEngine(config)
    results = engine.run()
    return {
        "selected_mode": engine.selected_mode,
        "path_results_rows": int(len(engine.path_results_df)),
        "cycle_results_rows": int(len(engine.cycle_results_df)),
        "start_price": float(results["start_price"].iloc[0]) if not results.empty else 0.0,
        "end_price": float(results["end_price"].iloc[0]) if not results.empty else 0.0,
        "result_source_mode": str(results["source_mode"].iloc[0]) if not results.empty else "",
    }
