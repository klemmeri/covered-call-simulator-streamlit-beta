# Phase 3F-3 Customer Preview Route Repair 3

This repair replaces only:

```text
app\paid_simulator\phase3f_customer_preview_route.py
```

The previous repair still failed because the dynamically loaded validation module encountered a `NoneType.__dict__` issue. This is consistent with Python `dataclass` behavior when a module is loaded through `importlib` without being registered in `sys.modules` first.

This repair removes dataclasses entirely and uses a plain Python class with:

- a stable `.to_dict()` method
- dictionary-style `.get()` support
- dictionary-style `model[key]` support
- compatibility builder and render function names

It does not modify:

```text
app\paid_simulator\config_form_app.py
```

The ordinary Customer view remains protected.
