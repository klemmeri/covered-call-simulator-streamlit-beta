# Phase 2 price-path scaffold attribute fix

This update fixes a scaffold compatibility issue where `scenario_price_paths.py` expected each scenario object to expose `.name`, while the installed `scenario_model.py` uses a different field name.

The replacement price-path scaffold now tolerates several field-name conventions, including:

- `name`
- `scenario_name`
- `display_name`
- `scenario_display_name`
- `total_return`
- `total_return_percent`
- `modeled_return_percent`
- `path_shape`
- `volatility_label`
- `interpretation`

It also replaces the PyCharm check script with a more robust scenario-loader that supports several possible scenario-factory function names.

Expected output:

```text
outputs\tables\paid_simulator\scenario_price_paths_scaffold.csv
```
