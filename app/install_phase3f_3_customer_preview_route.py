"""
install_phase3f_3_customer_preview_route.py

Guarded installer for Phase 3F-3 Customer Preview Dashboard Route.

The installer appends a small, protected helper block to config_form_app.py.
It creates a timestamped backup before writing and validates Python syntax before
and after the change.
"""

from __future__ import annotations

import ast
from datetime import datetime
from pathlib import Path
import shutil
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase3f_3_customer_preview_route_install_report.txt"

START_MARKER = "# >>> PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_START"
END_MARKER = "# <<< PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_END"
READY_MARKER = "PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_READY"
HELPER_NAME = "_render_phase3f_customer_preview_route"


APPEND_BLOCK = f'''

{START_MARKER}
# Protected Customer Preview route for Phase 3F-3.
# This helper is intentionally staged for preview use only.
# It must not be wired into the ordinary Customer view until a later release gate passes.
{READY_MARKER} = True
PHASE3F_3_CUSTOMER_PREVIEW_ROUTE_CUSTOMER_ENABLED = False


def {HELPER_NAME}(streamlit_module=None):
    """Render the protected Phase 3F customer-preview route."""
    from app.paid_simulator.phase3f_customer_preview_route import render_customer_preview_route

    return render_customer_preview_route(streamlit_module=streamlit_module)

{END_MARKER}
'''


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _validate_python(text: str, label: str) -> None:
    try:
        ast.parse(text)
    except SyntaxError as exc:
        raise RuntimeError(f"Python syntax validation failed for {label}: {exc}") from exc


def _remove_existing_block(text: str) -> str:
    if START_MARKER not in text:
        return text
    start = text.index(START_MARKER)
    end = text.find(END_MARKER, start)
    if end == -1:
        raise RuntimeError("Found Phase 3F-3 start marker without end marker.")
    end += len(END_MARKER)
    return text[:start].rstrip() + "\n" + text[end:].lstrip("\n")


def install() -> list[str]:
    messages: list[str] = []
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if not DASHBOARD_PATH.exists():
        raise FileNotFoundError(f"Dashboard file not found: {DASHBOARD_PATH}")

    original_text = _read_text(DASHBOARD_PATH)
    _validate_python(original_text, "current config_form_app.py")
    messages.append(f"PASS Current dashboard syntax is valid: {DASHBOARD_PATH}")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"config_form_app_before_phase3f_3_{timestamp}.py"
    shutil.copy2(DASHBOARD_PATH, backup_path)
    messages.append(f"PASS Backup written: {backup_path}")

    cleaned_text = _remove_existing_block(original_text)
    new_text = cleaned_text.rstrip() + APPEND_BLOCK
    _validate_python(new_text, "patched config_form_app.py")

    _write_text(DASHBOARD_PATH, new_text)
    messages.append("PASS Phase 3F-3 protected preview route block appended safely")
    messages.append(f"PASS Ready marker present: {READY_MARKER}")
    messages.append(f"PASS Helper function present: {HELPER_NAME}")
    messages.append("PASS Ordinary Customer view remains disabled for Phase 3F-3")

    REPORT_PATH.write_text("\n".join(messages) + "\n", encoding="utf-8")
    messages.append(f"PASS Install report written: {REPORT_PATH}")
    return messages


def main() -> int:
    print("=" * 100)
    print("Phase 3F-3 guarded customer preview route installer")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    try:
        messages = install()
    except Exception as exc:
        print(f"FAIL {exc}")
        return 1

    for message in messages:
        print(message)
    print()
    print("Installer status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
