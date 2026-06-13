# Paid Simulator Customer View Acceptance Test

Use this checklist after installing each dashboard update.

## Startup

- [ ] Run `app/run_paid_simulator_form.py` from PyCharm.
- [ ] Browser opens to the Streamlit dashboard.
- [ ] Product title displays as **Covered Call Strategy Stress Test**.
- [ ] Version line displays **Paid Simulator Dashboard v0.1**.
- [ ] Sidebar mode selector is visible.

## Customer view

Select **Customer view**.

Expected visible tabs:

- [ ] Overview
- [ ] Setup & run
- [ ] Latest results
- [ ] Preset comparison
- [ ] Report
- [ ] Help & assumptions

Expected hidden tabs:

- [ ] Run history
- [ ] App status
- [ ] Maintenance

## Setup & run

- [ ] Preset selector appears.
- [ ] Clean demo preset can be applied.
- [ ] Core setup fields appear.
- [ ] Advanced strategy settings are collapsed by default.
- [ ] Advanced cost assumptions are collapsed by default.
- [ ] Validation shows estimated max contracts.
- [ ] Save config button works.
- [ ] Run simulator button works.
- [ ] Health check button works.

## Latest results

- [ ] Latest results summary appears.
- [ ] Best, worst, and average relative results display.
- [ ] Plain-English interpretation displays without broken dollar-sign formatting.
- [ ] Decision guidance displays.
- [ ] Compact scenario chart displays.
- [ ] Raw scenario table is hidden behind an expander.
- [ ] Scenario detail cards appear.
- [ ] Markdown memo export works.
- [ ] PDF memo export works.

## Preset comparison

- [ ] Preset comparison section opens.
- [ ] Selected preset comparison can run.
- [ ] Recommended preset appears.
- [ ] Ranked preset table appears.
- [ ] Preset comparison chart is hidden behind an expander.
- [ ] Preset comparison CSV download works.

## Report

- [ ] HTML report found message appears after simulator run.
- [ ] Open report button works.
- [ ] Open report folder button works.

## Help & assumptions

- [ ] What the simulator does is explained.
- [ ] Key inputs are defined.
- [ ] Output terms are defined.
- [ ] Limitations are stated clearly.
- [ ] It does not describe the app as a forecast engine or guaranteed trading system.

## Developer view

Switch to **Developer view**.

Expected additional tabs:

- [ ] Run history
- [ ] App status
- [ ] Maintenance

## Final release check

Run:

```text
app/run_paid_simulator_release_check.py
```

Expected result:

```text
Overall release-check status: PASS
```
