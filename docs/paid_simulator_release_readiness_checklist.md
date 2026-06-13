# Paid Simulator Release Readiness Checklist

## Purpose

This checklist preserves the next development checkpoint for the Covered Call Simulator paid browser dashboard. The current app is working locally and has passed the App status check. The next phase is to move from "working development dashboard" toward "paid-product release candidate."

## Current verified state

Project root:

```text
C:\Users\ctran\OneDrive\Documents\Coveredcallsimulator
```

Current browser dashboard launcher:

```text
app\run_paid_simulator_form.py
```

Current dashboard app:

```text
app\paid_simulator\config_form_app.py
```

Current status:

```text
App status: PASS
```

## Current dashboard tabs

The Streamlit browser dashboard currently includes:

1. Overview
2. Setup & run
3. Latest results
4. Run history
5. Preset comparison
6. Report
7. Maintenance
8. Help & assumptions
9. App status

## Current core capabilities

The paid simulator dashboard can now:

- Choose and apply preset configurations.
- Edit the paid simulator JSON config.
- Validate the setup before running.
- Run the paid simulator from the browser.
- Run the health check from the browser.
- Show latest results summary.
- Show plain-English interpretation.
- Show decision guidance.
- Show scenario detail cards.
- Export Markdown decision memos.
- Export PDF decision memos.
- Track run history.
- Compare presets.
- Open the generated HTML report and report folder.
- Reset or clean generated dashboard files from the Maintenance tab.
- Show App status with required-file and generated-output checks.

## Release-readiness goals

Before treating the paid simulator as a release candidate, verify these areas.

### 1. Workflow reliability

- [ ] Apply each preset and confirm fields update correctly.
- [ ] Save config after each preset.
- [ ] Run simulator after each preset.
- [ ] Run health check after each simulator run.
- [ ] Confirm latest results update after each run.
- [ ] Confirm App status remains PASS.

### 2. User-interface clarity

- [ ] Confirm tab order is logical.
- [ ] Confirm the Overview tab gives the main result without scrolling.
- [ ] Confirm advanced settings are not visually overwhelming.
- [ ] Confirm raw tables are hidden behind expanders.
- [ ] Confirm charts are compact and readable.
- [ ] Confirm buttons are grouped by task.
- [ ] Confirm labels are customer-facing rather than code-facing where possible.

### 3. Output quality

- [ ] Open the HTML report after a simulator run.
- [ ] Export a Markdown decision memo.
- [ ] Export a PDF decision memo.
- [ ] Confirm memo files appear in the decision memo folder.
- [ ] Confirm the PDF opens correctly.
- [ ] Confirm the memo wording is suitable for a paying user.
- [ ] Confirm limitations are clearly stated.

### 4. Preset comparison

- [ ] Run all presets.
- [ ] Confirm best and worst presets are identified.
- [ ] Confirm the recommended preset panel is understandable.
- [ ] Confirm the preset comparison CSV is generated.
- [ ] Confirm the chart and table agree.

### 5. Maintenance and recovery

- [ ] Confirm config backups are created when saving.
- [ ] Confirm Maintenance tab can open output folders.
- [ ] Confirm reset-to-clean-demo works.
- [ ] Confirm clearing run history only removes generated history, not simulator files.
- [ ] Confirm clearing preset comparison only removes generated comparison rows.

## Suggested next development phase

The next useful phase is a controlled **Release Candidate Smoke Test**.

Instead of adding more dashboard features immediately, run a repeatable scripted check that verifies:

- Required files exist.
- Dashboard files exist.
- Config file is valid JSON.
- Scenario comparison CSV exists and has rows.
- HTML report exists.
- Decision memo folder exists.
- Run history and preset comparison files are present or safely optional.
- App status script runs.

The companion script for this checkpoint is:

```text
app\run_paid_simulator_release_check.py
```

## Development rule going forward

For the next phase, prefer:

```text
Stabilize -> verify -> document -> then add features
```

rather than continuing to add features without a release checkpoint.

