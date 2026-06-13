# Paid Simulator Branding Integration

This update integrates the product metadata module into the Streamlit dashboard while preserving the current working tabbed dashboard.

## Updated files

- `app/paid_simulator/config_form_app.py`
- `app/run_paid_simulator_form.py`

## Included product metadata files

- `app/paid_simulator/product_info.py`
- `app/run_paid_simulator_product_info.py`
- `docs/paid_simulator_product_branding.md`
- `docs/paid_simulator_release_notes_v0_1.md`

## Dashboard changes

- The main Streamlit header now uses the product name from `product_info.py`.
- The Overview tab now displays the version label, release stage, positioning statement, and primary workflow.
- The App status tab now displays product version/release-stage metadata.
- Markdown and PDF decision memos now include product version, build label, release stage, product framing, and key limitations.
- Help & assumptions now uses the centralized product framing and limitations.

## Product name

Covered Call Strategy Stress Test

## Version

Paid Simulator Dashboard v0.1
