"""
models.py

Core data models for the paid Covered Call Simulator engine.

This module intentionally contains data containers only.

It should not:
    - import Streamlit
    - call external data services
    - connect to a broker
    - run simulations directly
    - write output files

The paid simulator should be testable outside the public website.

Central design rule:
    Premium collected is not the same as profit.
    Total equity is the main scorecard.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


# =============================================================================
# Utility base class
# =============================================================================


@dataclass
class ModelBase:
    """
    Base class that gives all simulator dataclasses a simple dictionary export.
    """

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the dataclass to a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the model.
        """
        return asdict(self)


# =============================================================================
# User input and market snapshot models
# =============================================================================


@dataclass
class SimulationInput(ModelBase):
    """
    User-selected assumptions for one simulator session.
    """

    session_id: str
    created_timestamp: datetime

    mode: str
    ticker: str

    account_size: float
    risk_tier: str
    position_size_cap: float

    target_delta: float
    target_dte: int
    strike_selection_method: str

    management_rule: str
    profit_take_percent: float | None = None
    rolling_rule: str | None = None
    reentry_rule: str | None = None

    transaction_cost_per_contract: float = 0.0
    slippage_assumption: float = 0.0
    data_source: str = "illustrative"


@dataclass
class TickerSnapshot(ModelBase):
    """
    Ticker-level price and availability snapshot.
    """

    ticker: str
    timestamp: datetime

    price: float | None
    previous_close: float | None = None
    daily_return: float | None = None

    data_status: str = "unknown"
    quote_type: str = "unknown"

    is_price_available: bool = False
    is_optionable: bool = False
    has_sufficient_liquidity: bool = False

    note: str = ""


@dataclass
class AccountFeasibility(ModelBase):
    """
    Account-size and position-size feasibility result.
    """

    ticker: str
    price: float | None

    shares_required: int = 100
    contract_multiplier: int = 100

    stock_value_required: float | None = None
    account_size: float = 0.0
    position_size_cap: float = 0.0
    minimum_equity_required: float | None = None

    passes_account_screen: bool = False
    reason: str = ""


# =============================================================================
# Option candidate and trade-selection models
# =============================================================================


@dataclass
class OptionCandidate(ModelBase):
    """
    One possible covered-call candidate.
    """

    candidate_id: str
    ticker: str

    expiration_date: datetime
    dte: int
    strike: float
    option_type: str = "call"

    bid: float | None = None
    ask: float | None = None
    mid: float | None = None
    last: float | None = None

    volume: int | None = None
    open_interest: int | None = None

    implied_volatility: float | None = None
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None

    spread_width: float | None = None
    spread_percent: float | None = None

    moneyness: str = "unknown"
    liquidity_score: str = "unknown"

    is_candidate: bool = True
    candidate_reason: str = ""


@dataclass
class SelectedOption(ModelBase):
    """
    The option candidate selected for simulated covered-call placement.
    """

    option_candidate_id: str
    ticker: str

    expiration_date: datetime
    dte: int
    strike: float
    delta: float | None

    bid: float | None
    ask: float | None
    mid: float | None

    selected_price: float
    selected_price_source: str

    estimated_premium: float
    estimated_transaction_cost: float
    estimated_net_credit: float

    selection_timestamp: datetime
    selection_reason: str = ""


@dataclass
class PreTradeImpact(ModelBase):
    """
    Simplified pre-trade impact estimate for a selected covered call.
    """

    stock_price: float
    strike: float
    premium_per_share: float

    contract_multiplier: int = 100

    stock_value: float = 0.0
    premium_cash: float = 0.0
    upside_to_strike: float = 0.0
    gross_if_assigned: float = 0.0

    premium_yield: float = 0.0
    if_assigned_return: float = 0.0
    downside_buffer: float = 0.0

    assignment_pressure: str = "unknown"
    notes: str = ""


# =============================================================================
# Event, position, and equity models
# =============================================================================


@dataclass
class TradeEvent(ModelBase):
    """
    One user action, rule action, or simulation event.
    """

    event_id: str
    session_id: str
    timestamp: datetime
    event_type: str

    ticker: str
    stock_price: float | None = None

    shares_delta: int = 0
    cash_delta: float = 0.0

    option_symbol: str | None = None
    option_quantity_delta: int = 0
    option_price: float | None = None
    option_cash_delta: float = 0.0

    transaction_cost: float = 0.0

    realized_option_pl: float = 0.0
    realized_stock_pl: float = 0.0

    event_note: str = ""
    user_decision: str | None = None
    rule_trigger: str | None = None


@dataclass
class PositionState(ModelBase):
    """
    Account and position state after an event or market step.
    """

    session_id: str
    timestamp: datetime
    ticker: str

    shares: int
    stock_price: float
    stock_value: float

    cash: float

    short_call_symbol: str | None = None
    short_call_quantity: int = 0
    short_call_strike: float | None = None
    short_call_expiration: datetime | None = None
    short_call_mark: float = 0.0
    short_call_market_value: float = 0.0

    realized_option_pl: float = 0.0
    unrealized_option_pl: float = 0.0
    realized_stock_pl: float = 0.0
    total_realized_pl: float = 0.0

    total_equity: float = 0.0

    capped_upside: float | None = None
    assignment_status: str = "not_applicable"
    days_to_expiration: int | None = None
    moneyness: str = "unknown"

    note: str = ""


@dataclass
class EquitySnapshot(ModelBase):
    """
    One point on the simulator equity curve.
    """

    session_id: str
    timestamp: datetime
    step_number: int

    stock_price: float
    cash: float
    stock_value: float
    short_call_value: float
    total_equity: float

    premium_collected_to_date: float = 0.0
    realized_option_pl: float = 0.0
    unrealized_option_pl: float = 0.0
    missed_upside: float = 0.0

    benchmark_buy_hold_equity: float | None = None
    benchmark_rule_equity: float | None = None


@dataclass
class BenchmarkSnapshot(ModelBase):
    """
    Benchmark value at one point in the simulation.
    """

    session_id: str
    timestamp: datetime
    benchmark_name: str

    equity: float
    cash: float = 0.0
    stock_value: float = 0.0
    option_value: float = 0.0

    realized_pl: float = 0.0
    unrealized_pl: float = 0.0

    notes: str = ""


# =============================================================================
# Training and report models
# =============================================================================


@dataclass
class TrainingFeedback(ModelBase):
    """
    One piece of training feedback generated by the simulator.
    """

    feedback_id: str
    session_id: str
    timestamp: datetime

    decision_area: str
    feedback_type: str
    message: str

    severity: str = "info"
    related_event_id: str | None = None
    related_metric: str | None = None
    suggested_lesson: str = ""


@dataclass
class SessionReport(ModelBase):
    """
    Summary values for a completed simulation or training session.
    """

    session_id: str
    created_timestamp: datetime
    session_type: str
    ticker: str

    starting_equity: float
    ending_equity: float
    active_return: float

    buy_hold_ending_equity: float | None = None
    rule_benchmark_ending_equity: float | None = None

    premium_collected: float = 0.0
    option_buyback_costs: float = 0.0
    net_option_pl: float = 0.0
    missed_upside: float = 0.0
    max_drawdown: float | None = None

    number_of_calls_sold: int = 0
    number_of_rolls: int = 0
    number_of_closes: int = 0
    number_of_assignments: int = 0

    decision_summary: str = ""
    training_takeaway: str = ""

    disclaimer_text: str = (
        "This report is an illustrative simulation report. It is not financial "
        "advice, investment advice, tax advice, legal advice, or a trade "
        "recommendation. Simulated results are hypothetical and may not reflect "
        "real trading outcomes. Options involve risk and are not suitable for "
        "all investors."
    )


@dataclass
class SimulatorRunOutput(ModelBase):
    """
    Container for all major outputs from one simulator run.

    DataFrame outputs can be created later from the lists stored here.
    """

    session_id: str

    simulation_input: SimulationInput
    ticker_snapshot: TickerSnapshot
    account_feasibility: AccountFeasibility

    option_candidates: list[OptionCandidate] = field(default_factory=list)
    selected_option: SelectedOption | None = None
    pre_trade_impact: PreTradeImpact | None = None

    trade_events: list[TradeEvent] = field(default_factory=list)
    position_states: list[PositionState] = field(default_factory=list)
    equity_curve: list[EquitySnapshot] = field(default_factory=list)
    benchmarks: list[BenchmarkSnapshot] = field(default_factory=list)
    training_feedback: list[TrainingFeedback] = field(default_factory=list)

    session_report: SessionReport | None = None
