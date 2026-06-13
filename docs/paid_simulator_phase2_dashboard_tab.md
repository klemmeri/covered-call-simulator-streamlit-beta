# Paid Simulator Phase 2 Dashboard Tab

This package adds a **Developer-view-only** tab named **Phase 2 scaffold** to the main Streamlit dashboard.

The tab is intentionally hidden from Customer view. It is designed to inspect Phase 2 scaffold outputs beside the stable v0.1 dashboard without promoting those outputs to the customer-facing workflow.

## Tab contents

The Phase 2 scaffold tab displays:

- Phase 2 pipeline check button
- Phase 2 integration-readiness check button
- Standalone Phase 2 viewer launcher
- Scaffold file-status table
- Phase 2 vs v0 comparison table
- Scenario payoff report scaffold table
- Scenario price-path scaffold table
- Links/buttons for Phase 2 HTML scaffold reports

## Important limitation

Phase 2 outputs are exploratory scaffold diagnostics. They are not yet the official paid simulator engine and should not be shown in Customer view until the modeling layer has been reviewed and stabilized.
