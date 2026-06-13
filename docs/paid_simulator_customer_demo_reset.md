# Paid Simulator Customer Demo Reset

This update adds one-click demo reset controls to the Streamlit paid simulator dashboard.

## Purpose

Before a customer walkthrough, screenshot, or video, the dashboard can be returned to the standard clean demo configuration.

## Clean demo configuration

- Ticker: SPY
- Account size: 600000
- Risk tier: Balanced
- Position-size cap: 0.10
- Desired contracts: 1
- Target delta: 0.30
- Target DTE: 30
- Management rule: close_at_50_percent_profit
- Rolling rule: none
- Re-entry rule: immediate
- Transaction cost: 1.00
- Slippage assumption: 0.01
- Demo price: 545.25

## New controls

The dashboard sidebar now includes Demo controls:

- Reset to clean demo
- Reset and run clean demo

The Setup & run tab also includes a Customer demo reset section with the same actions.

## Notes

The reset action writes to config/paid_simulator_config.json and creates the normal config backup.

The reset-and-run action also runs the paid simulator and appends the result to run history when scenario results are available.
