# Phase 3I-4 — Customer Risk-Warning and Disclosure Verification

This checkpoint verifies that the activated customer-facing covered-call workflow contains clear risk and disclosure language.

It checks for customer labels such as current price, strike, premium, breakeven, max profit, downside cushion, assignment zone, and warning language.

It also verifies key disclosure concepts:

- covered calls cap upside above the strike;
- assignment can occur when the stock is in the assignment zone;
- premium lowers breakeven but does not eliminate downside risk;
- large stock declines can still create losses;
- scenario results are estimates, not guarantees.

This package does not modify `app\paid_simulator\config_form_app.py`.
