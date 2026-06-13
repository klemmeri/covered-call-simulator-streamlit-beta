# Customer-view final release text cleanup

This cleanup removes local/pre-release wording from the Streamlit dashboard source.

It replaces customer-visible labels such as:

- `Local prototype / pre-release dashboard`
- `2026-06-11 local checkpoint`
- `local checkpoint`

with clean beta wording:

- `Beta release`

It does not change simulator calculations, engine files, or option logic.

Run:

`app\run_customer_view_final_release_text_cleanup.py`

Then run:

`app\run_customer_view_final_release_text_cleanup_check.py`
