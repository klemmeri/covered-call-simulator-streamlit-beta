"""
session_config.py

Session-configuration helpers for the paid Covered Call Simulator.

This module centralizes simulator assumptions and reads optional user-editable
settings from:

    config/paid_simulator_config.json

If that file is missing or incomplete, built-in defaults are used.

Purpose:
    Let the paid simulator move from hard-coded demo assumptions toward
    user-selected inputs without requiring changes to runner.py.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from models import (
    SimulationInput,
    TickerSnapshot,
)


DEFAULT_SESSION_ID = "demo_session_001"
DEFAULT_TICKER = "SPY"
DEFAULT_ACCOUNT_SIZE = 100000.0
DEFAULT_RISK_TIER = "Balanced"
DEFAULT_POSITION_SIZE_CAP = 0.10
DEFAULT_DESIRED_CONTRACTS = 1
DEFAULT_TARGET_DELTA = 0.30
DEFAULT_TARGET_DTE = 30
DEFAULT_STRIKE_SELECTION_METHOD = "Closest to target delta"
DEFAULT_MANAGEMENT_RULE = "Close at 50% profit"
DEFAULT_PROFIT_TAKE_PERCENT = 0.50
DEFAULT_ROLLING_RULE = "Roll only for net credit"
DEFAULT_REENTRY_RULE = "Wait 10 days"
DEFAULT_TRANSACTION_COST_PER_CONTRACT = 1.00
DEFAULT_SLIPPAGE_ASSUMPTION = 0.01
DEFAULT_DATA_SOURCE = "illustrative"
DEFAULT_MODE = "historical_active_replay"

DEFAULT_DEMO_PRICE = 545.25
DEFAULT_DEMO_PREVIOUS_CLOSE = 543.80
DEFAULT_DEMO_DAILY_RETURN = 0.0027


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.

    This file lives in:

        app/paid_simulator/session_config.py

    Therefore, parents[2] is the project root.
    """
    return Path(__file__).resolve().parents[2]


def get_default_config_path() -> Path:
    """
    Return the default paid-simulator config path.
    """
    return get_project_root() / "config" / "paid_simulator_config.json"


def load_paid_simulator_config(
    config_path: Path | None = None,
) -> dict[str, Any]:
    """
    Load the optional paid simulator JSON config file.

    Missing files are allowed. In that case, an empty dictionary is returned
    and defaults are used.
    """
    if config_path is None:
        config_path = get_default_config_path()

    if not config_path.exists():
        return {}

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config_data = json.load(config_file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Could not parse paid simulator config file: {config_path}"
        ) from exc

    if not isinstance(config_data, dict):
        raise ValueError(
            f"Paid simulator config must be a JSON object: {config_path}"
        )

    return config_data


def get_config_value(
    config: dict[str, Any],
    key: str,
    default: Any,
) -> Any:
    """
    Return a config value with a default fallback.
    """
    value = config.get(key, default)

    if value is None:
        return default

    return value


def get_config_float(
    config: dict[str, Any],
    key: str,
    default: float,
) -> float:
    """
    Return a float config value with validation.
    """
    value = get_config_value(config, key, default)

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Config value '{key}' must be numeric.") from exc


def get_config_int(
    config: dict[str, Any],
    key: str,
    default: int,
) -> int:
    """
    Return an integer config value with validation.
    """
    value = get_config_value(config, key, default)

    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Config value '{key}' must be an integer.") from exc


def get_config_string(
    config: dict[str, Any],
    key: str,
    default: str,
) -> str:
    """
    Return a stripped string config value.
    """
    value = get_config_value(config, key, default)

    return str(value).strip()


def get_desired_contracts() -> int:
    """
    Return the desired covered-call contract count from config.

    This is used for position-sizing diagnostics. The current path engine still
    simulates one contract; multi-contract path scaling will be added later.
    """
    config = load_paid_simulator_config()

    desired_contracts = get_config_int(
        config,
        "desired_contracts",
        DEFAULT_DESIRED_CONTRACTS,
    )

    if desired_contracts < 0:
        raise ValueError("Config value 'desired_contracts' cannot be negative.")

    return desired_contracts


def build_simulation_input(
    created_timestamp: datetime,
    session_id: str = DEFAULT_SESSION_ID,
    ticker: str = DEFAULT_TICKER,
    account_size: float = DEFAULT_ACCOUNT_SIZE,
    risk_tier: str = DEFAULT_RISK_TIER,
    position_size_cap: float = DEFAULT_POSITION_SIZE_CAP,
    target_delta: float = DEFAULT_TARGET_DELTA,
    target_dte: int = DEFAULT_TARGET_DTE,
    strike_selection_method: str = DEFAULT_STRIKE_SELECTION_METHOD,
    management_rule: str = DEFAULT_MANAGEMENT_RULE,
    profit_take_percent: float = DEFAULT_PROFIT_TAKE_PERCENT,
    rolling_rule: str = DEFAULT_ROLLING_RULE,
    reentry_rule: str = DEFAULT_REENTRY_RULE,
    transaction_cost_per_contract: float = DEFAULT_TRANSACTION_COST_PER_CONTRACT,
    slippage_assumption: float = DEFAULT_SLIPPAGE_ASSUMPTION,
    data_source: str = DEFAULT_DATA_SOURCE,
    mode: str = DEFAULT_MODE,
) -> SimulationInput:
    """
    Build a SimulationInput object from explicit parameters.
    """
    return SimulationInput(
        session_id=session_id,
        created_timestamp=created_timestamp,
        mode=mode,
        ticker=ticker.upper().strip(),
        account_size=account_size,
        risk_tier=risk_tier,
        position_size_cap=position_size_cap,
        target_delta=target_delta,
        target_dte=target_dte,
        strike_selection_method=strike_selection_method,
        management_rule=management_rule,
        profit_take_percent=profit_take_percent,
        rolling_rule=rolling_rule,
        reentry_rule=reentry_rule,
        transaction_cost_per_contract=transaction_cost_per_contract,
        slippage_assumption=slippage_assumption,
        data_source=data_source,
    )


def build_ticker_snapshot(
    timestamp: datetime,
    ticker: str = DEFAULT_TICKER,
    price: float = DEFAULT_DEMO_PRICE,
    previous_close: float = DEFAULT_DEMO_PREVIOUS_CLOSE,
    daily_return: float = DEFAULT_DEMO_DAILY_RETURN,
    data_status: str = "illustrative",
    quote_type: str = "demo",
    is_price_available: bool = True,
    is_optionable: bool = True,
    has_sufficient_liquidity: bool = True,
    note: str = "Demo ticker snapshot.",
) -> TickerSnapshot:
    """
    Build a TickerSnapshot object from explicit parameters.
    """
    return TickerSnapshot(
        ticker=ticker.upper().strip(),
        timestamp=timestamp,
        price=price,
        previous_close=previous_close,
        daily_return=daily_return,
        data_status=data_status,
        quote_type=quote_type,
        is_price_available=is_price_available,
        is_optionable=is_optionable,
        has_sufficient_liquidity=has_sufficient_liquidity,
        note=note,
    )


def build_demo_simulation_input(
    created_timestamp: datetime,
) -> SimulationInput:
    """
    Build the SimulationInput used by runner.py.

    Values are read from config/paid_simulator_config.json when available.
    """
    config = load_paid_simulator_config()

    return build_simulation_input(
        created_timestamp=created_timestamp,
        session_id=get_config_string(config, "session_id", DEFAULT_SESSION_ID),
        ticker=get_config_string(config, "ticker", DEFAULT_TICKER),
        account_size=get_config_float(
            config,
            "account_size",
            DEFAULT_ACCOUNT_SIZE,
        ),
        risk_tier=get_config_string(config, "risk_tier", DEFAULT_RISK_TIER),
        position_size_cap=get_config_float(
            config,
            "position_size_cap",
            DEFAULT_POSITION_SIZE_CAP,
        ),
        target_delta=get_config_float(
            config,
            "target_delta",
            DEFAULT_TARGET_DELTA,
        ),
        target_dte=get_config_int(config, "target_dte", DEFAULT_TARGET_DTE),
        strike_selection_method=get_config_string(
            config,
            "strike_selection_method",
            DEFAULT_STRIKE_SELECTION_METHOD,
        ),
        management_rule=get_config_string(
            config,
            "management_rule",
            DEFAULT_MANAGEMENT_RULE,
        ),
        profit_take_percent=get_config_float(
            config,
            "profit_take_percent",
            DEFAULT_PROFIT_TAKE_PERCENT,
        ),
        rolling_rule=get_config_string(config, "rolling_rule", DEFAULT_ROLLING_RULE),
        reentry_rule=get_config_string(config, "reentry_rule", DEFAULT_REENTRY_RULE),
        transaction_cost_per_contract=get_config_float(
            config,
            "transaction_cost_per_contract",
            DEFAULT_TRANSACTION_COST_PER_CONTRACT,
        ),
        slippage_assumption=get_config_float(
            config,
            "slippage_assumption",
            DEFAULT_SLIPPAGE_ASSUMPTION,
        ),
        data_source=get_config_string(config, "data_source", DEFAULT_DATA_SOURCE),
        mode=get_config_string(config, "mode", DEFAULT_MODE),
    )


def build_demo_ticker_snapshot(
    timestamp: datetime,
) -> TickerSnapshot:
    """
    Build the TickerSnapshot used by runner.py.

    Values are read from config/paid_simulator_config.json when available.
    """
    config = load_paid_simulator_config()

    return build_ticker_snapshot(
        timestamp=timestamp,
        ticker=get_config_string(config, "ticker", DEFAULT_TICKER),
        price=get_config_float(config, "demo_price", DEFAULT_DEMO_PRICE),
        previous_close=get_config_float(
            config,
            "demo_previous_close",
            DEFAULT_DEMO_PREVIOUS_CLOSE,
        ),
        daily_return=get_config_float(
            config,
            "demo_daily_return",
            DEFAULT_DEMO_DAILY_RETURN,
        ),
        data_status=get_config_string(config, "data_source", DEFAULT_DATA_SOURCE),
        quote_type="demo",
        is_price_available=True,
        is_optionable=True,
        has_sufficient_liquidity=True,
        note="Demo ticker snapshot from paid_simulator_config.json.",
    )


def describe_session_config(
    simulation_input: SimulationInput,
    ticker_snapshot: TickerSnapshot,
) -> dict[str, object]:
    """
    Create a compact dictionary describing the active session configuration.
    """
    config_path = get_default_config_path()

    return {
        "config_path": str(config_path),
        "config_file_exists": config_path.exists(),
        "session_id": simulation_input.session_id,
        "mode": simulation_input.mode,
        "ticker": simulation_input.ticker,
        "account_size": simulation_input.account_size,
        "risk_tier": simulation_input.risk_tier,
        "position_size_cap": simulation_input.position_size_cap,
        "desired_contracts": get_desired_contracts(),
        "target_delta": simulation_input.target_delta,
        "target_dte": simulation_input.target_dte,
        "strike_selection_method": simulation_input.strike_selection_method,
        "management_rule": simulation_input.management_rule,
        "rolling_rule": simulation_input.rolling_rule,
        "reentry_rule": simulation_input.reentry_rule,
        "data_source": simulation_input.data_source,
        "ticker_price": ticker_snapshot.price,
        "ticker_data_status": ticker_snapshot.data_status,
        "ticker_quote_type": ticker_snapshot.quote_type,
    }
