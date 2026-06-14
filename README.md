# Covered Call Simulator

The Covered Call Simulator is a public beta web app for testing how a covered-call setup behaves across several named market examples.

The current beta is a **covered-call strategy stress test**, not yet a full Monte Carlo simulator.

Hosted beta app:

```text
https://configformapppy-nkcdrgmmzxvzlz89ck9m63.streamlit.app
```

## What the beta app does

The app lets a user enter a simple covered-call setup and compare the result against simply holding the stock or ETF.

The current beta tests one covered-call example across several named market examples, such as:

```text
Downtrend
Sideways choppy
Moderate uptrend
Volatile two-sided
Strong rally
```

The purpose is to answer a practical question:

```text
If the market behaved in different ways, would this covered call help or hurt compared with simply holding the stock or ETF?
```

## Current beta scope

The current public beta includes:

```text
Overview page
Setup & run page
Latest results page
Challenge page
Preset comparison page
Generated report page
Help & assumptions page
Beta tester documentation
```

It is designed for plain-English testing and feedback.

## What it does not do yet

The current beta does not yet:

```text
Run full Monte Carlo simulations
Automatically roll covered calls
Use live market option chains
Predict the market
Maintain a persistent public leaderboard
```

Those features may be added later.

## Local run command

From the project root:

```bash
streamlit run app/paid_simulator/config_form_app.py
```

Or, using the local Python installation:

```bash
C:\Users\ctran\AppData\Local\Programs\Python\Python313\python.exe -m streamlit run app/paid_simulator/config_form_app.py
```

## Main project files

Current main app file:

```text
app/paid_simulator/config_form_app.py
```

Main scenario report generator:

```text
app/paid_simulator/scenario_comparison_report.py
```

Main runner:

```text
app/run_paid_simulator.py
```

Beta tester docs:

```text
docs/beta_tester_readme.md
docs/beta_feedback_checklist.md
docs/beta_email_invitation.md
```

## Current product framing

This app should be described as:

```text
A covered-call strategy stress test
A way to compare a covered call against simply holding the stock
A beta tool for exploring covered-call behavior across named market examples
```

Avoid presenting it as:

```text
A market prediction tool
A guaranteed trading system
A complete options backtester
A full Monte Carlo simulator
```

## Development workflow

Use exact-file Git commands. Do not use:

```bash
git add .
```

Instead, add only the files intended for a commit, for example:

```bash
git add app/paid_simulator/config_form_app.py
git commit -m "Describe the specific change"
git push
```

## Repository status

The current public beta has been polished for initial tester review. Recent improvements include:

```text
Clearer public beta workflow
Improved preset comparison wording
Suppressed duplicate report tabs during preset comparison
Only one generated-report “What to do next” box
Overview chart legend moved below the chart
Beta tester documentation added
```

## Notes for beta testers

The beta app is meant to be tested for clarity, usability, and basic covered-call reasoning.

Useful feedback includes:

```text
Was the wording clear?
Did the pages open correctly?
Did any button behave strangely?
Did the report make sense?
Did the app explain covered-call risk clearly enough?
Was anything too technical?
```

The main beta tester checklist is here:

```text
docs/beta_feedback_checklist.md
```
