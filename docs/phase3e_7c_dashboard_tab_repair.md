# Phase 3E-7C Dashboard Tab Repair

This repair fixes two issues from the first Phase 3E-7C dashboard-tab integration attempt.

## Problem corrected

The prior installer inserted a Phase 3E import into the middle of an open `try:` block in:

```text
app\paid_simulator\config_form_app.py
```

That produced this syntax failure:

```text
SyntaxError("expected 'except' or 'finally' block")
```

The panel also did not expose the function name expected by the 7C checkpoint:

```text
build_panel_render_model
```

## Repair behavior

The replacement installer:

1. Checks whether `config_form_app.py` is valid Python.
2. If invalid, restores the newest Phase 3E-7C backup from:

```text
outputs\backups\paid_simulator
```

3. Creates a new repair backup.
4. Removes any prior Phase 3E-7C injected block.
5. Appends a lazy Developer-view helper at the end of `config_form_app.py`.
6. Validates the patched file before writing.

## Customer-view protection

This repair does not expose Phase 3E to the Customer view.  It only stages a Developer-view helper and marker for the 7C checkpoint.
