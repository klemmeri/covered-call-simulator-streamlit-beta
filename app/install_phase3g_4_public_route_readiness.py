"""
install_phase3g_4_public_route_readiness.py

Guarded Phase 3G-4 dashboard readiness installer.

This installer appends a protected helper block to config_form_app.py. It does
not enable public Customer-view access. It creates a timestamped backup before
writing and validates Python syntax before and after the append.
"""

from __future__ import annotations

import ast
import shutil
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
BACKUP_DIR = PROJECT_ROOT / "outputs" / "backups" / "paid_simulator"

START_MARKER = "# === PHASE3G_4_PUBLIC_ROUTE_READINESS_START ==="
END_MARKER = "# === PHASE3G_4_PUBLIC_ROUTE_READINESS_END ==="

HELPER_BLOCK = f'''
{START_MARKER}
# Phase 3G-4 public Customer-view route-readiness helper.
# This block prepares a public-candidate route structure but does NOT enable
# ordinary Customer-view access.
PHASE3G_4_PUBLIC_ROUTE_READY = "PHASE3G_4_PUBLIC_ROUTE_READY"
PHASE3G_4_PUBLIC_CUSTOMER_ENABLED = False


def _render_phase3g_public_customer_route_readiness():
    """Render Phase 3G-4 route-readiness information in a protected context."""
    from app.paid_simulator.phase3g_public_customer_route_readiness import (
        render_phase3g_4_public_route_readiness,
    )

    try:
        import streamlit as st
    except Exception:
        st = None

    return render_phase3g_4_public_route_readiness(streamlit_module=st)
{END_MARKER}
'''


def validate_syntax(text: str, label: str) -> None:
    try:
        ast.parse(text)
    except SyntaxError as exc:
        raise RuntimeError(f"Syntax validation failed for {label}: {exc}") from exc


def remove_existing_block(text: str) -> str:
    start = text.find(START_MARKER)
    end = text.find(END_MARKER)
    if start == -1 or end == -1:
        return text
    end += len(END_MARKER)
    while end < len(text) and text[end] in "\r\n":
        end += 1
    return text[:start].rstrip() + "\n\n" + text[end:].lstrip()


def main() -> int:
    print("=" * 100)
    print("Installing Phase 3G-4 public route-readiness helper")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dashboard:    {DASHBOARD_PATH}")

    if not DASHBOARD_PATH.exists():
        raise FileNotFoundError(DASHBOARD_PATH)

    original = DASHBOARD_PATH.read_text(encoding="utf-8")
    validate_syntax(original, "original dashboard")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"config_form_app_before_phase3g_4_{stamp}.py"
    shutil.copy2(DASHBOARD_PATH, backup_path)

    cleaned = remove_existing_block(original)
    updated = cleaned.rstrip() + "\n\n" + HELPER_BLOCK.lstrip()
    validate_syntax(updated, "updated dashboard")

    DASHBOARD_PATH.write_text(updated, encoding="utf-8")

    print(f"Backup written: {backup_path}")
    print("Phase 3G-4 helper appended safely.")
    print("Public Customer view remains disabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
