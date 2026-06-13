# Paid Simulator Restore Checkpoint — 2026-06-11

This checkpoint preserves the current working local Streamlit paid-simulator dashboard for the Covered Call Simulator project.

## Project root

`C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator`

## Restore purpose

Use this package to restore the branded paid simulator dashboard after future experiments, UI changes, or accidental file edits.

## Included files

- `app\paid_simulator\config_form_app.py`
- `app\run_paid_simulator_form.py`
- `app\paid_simulator\product_info.py`
- `app\run_paid_simulator_product_info.py`
- `app\paid_simulator\dashboard_status.py`
- `app\run_paid_simulator_status.py`
- `app\run_paid_simulator_release_check.py`
- Supporting documentation in `docs\`

## Verified dashboard state at checkpoint

- Product branding integrated.
- Overview tab present and working.
- Setup & run tab present and working.
- Latest results tab present and working.
- Run history tab present and working.
- Preset comparison tab present and working.
- Report tab present and working.
- App status tab present and passing.
- Maintenance tab present and working.
- Help & assumptions tab present and working.
- Markdown decision memo export working.
- PDF decision memo export working.
- Release check passing.

## Restore instructions

1. Extract this zip directly into:

   `C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator`

2. Allow Windows to merge folders and replace files.

3. In PyCharm, run:

   `C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_form.py`

4. If PyCharm says the process is already running, choose **Stop and Rerun**.

5. Open the **App status** tab and confirm status is `PASS`.

6. Optionally run:

   `C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator\app\run_paid_simulator_release_check.py`

   Expected result: `Overall release-check status: PASS`.

## Notes

This package is intended to restore the dashboard/control-panel layer. It does not include the entire simulator engine or historical output data.
