# Customer-view local debug text cleanup

This post-Phase-10 polish patch hides local/debugging text from Customer view while preserving it in Developer view.

It targets dashboard display lines containing:

- `Project root:`
- `Local prototype`
- `pre-release dashboard`
- `local checkpoint`

The patch is intentionally narrow. It does not change the simulator engine, customer workflow, historical-mode logic, or Streamlit entry point.

## Run

First run the patch:

`app\run_customer_view_local_debug_text_cleanup.py`

Then run the check:

`app\run_customer_view_local_debug_text_cleanup_check.py`

Expected final line:

`Overall customer-view cleanup check status: PASS`
