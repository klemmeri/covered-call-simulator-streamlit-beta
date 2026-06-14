# Covered Call Simulator — Beta Tester Guide

Thank you for helping test the Covered Call Simulator public beta.

This beta is a **covered-call stress test**. It lets you set up one covered-call example and compare it against simply holding the stock or ETF across several named market examples.

The goal is not to predict the market. The goal is to help users understand when a covered call may help, when it may hurt, and how much upside can be given away when the stock rises above the call strike.

## Beta app URL

```text
https://configformapppy-nkcdrgmmzxvzlz89ck9m63.streamlit.app
```

## What to test first

Please try the app in this order:

1. Open the **Overview** page.
2. Read the explanation and inspect the chart.
3. Open **Setup & run**.
4. Run the default SPY example without changing anything.
5. Open **Latest results** and review the comparison.
6. Open **Challenge** and try to improve the result.
7. Open **Preset comparison** and compare the example setups.
8. Open **Report** and review the generated report.
9. Open **Help & assumptions** and read the assumptions.

## What this beta does

The beta compares one covered-call setup against simply holding the stock or ETF across named market examples such as:

- Downtrend
- Sideways choppy
- Moderate uptrend
- Volatile two-sided
- Strong rally

The app currently uses one option cycle for the setup. If the stock rises above the call strike, the covered call is treated as limiting gains above that strike.

## What this beta does not do yet

This beta does not yet:

- Automatically roll covered calls
- Run full Monte Carlo simulations
- Predict future market behavior
- Store public leaderboard results permanently
- Replace trading judgment or financial advice

## Things to watch for

Please tell us if:

- A page does not open.
- A button behaves unexpectedly.
- A chart is hard to read.
- Text overlaps other text.
- Wording is confusing or too technical.
- You are unsure what to do next.
- The report says something that seems inconsistent with the app result.
- The app opens extra browser tabs unexpectedly.

## Best kind of feedback

The most useful feedback is specific.

For example:

```text
On the Overview page, the chart legend overlaps the lines.
```

or:

```text
On Preset comparison, I did not understand why the best result was still negative.
```

A screenshot is helpful whenever possible.
