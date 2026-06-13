"""
run_customer_view_local_debug_text_cleanup.py

Post-Phase-10 customer-view polish patch.

Purpose
-------
Hide local debugging/build text from Customer view while preserving it in
Developer view. Specifically targets dashboard lines that expose:

1. the local Windows project root, and
2. local prototype / pre-release / checkpoint wording.

The script modifies app/paid_simulator/config_form_app.py in place and writes a
backup next to it before patching.
"""

from __future__ import annotations

import ast
import json
import shutil
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_TXT = OUTPUT_REPORT_DIR / "customer_view_local_debug_text_cleanup_report.txt"
REPORT_JSON = OUTPUT_REPORT_DIR / "customer_view_local_debug_text_cleanup_report.json"

PATCH_MARKER = "CUSTOMER_VIEW_LOCAL_DEBUG_TEXT_CLEANUP_APPLIED"
START_MARKER = "# === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP START ==="
END_MARKER = "# === CUSTOMER VIEW LOCAL DEBUG TEXT CLEANUP END ==="

TARGET_PATTERNS = [
    "Project root:",
    "Local prototype",
    "pre-release dashboard",
    "local checkpoint",
]

DISPLAY_TOKENS = [
    "st.caption",
    "st.write",
    "st.markdown",
    "st.text",
]


DEV_GUARD_LINES = [
    "if (",
    "    locals().get('interface_mode') == 'Developer view'",
    "    or locals().get('selected_interface_mode') == 'Developer view'",
    "    or locals().get('dashboard_mode') == 'Developer view'",
    "    or locals().get('dashboard_view_mode') == 'Developer view'",
    "    or locals().get('view_mode') == 'Developer view'",
    "):",
]


def compile_ok(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return True, "syntax valid"
    except Exception as exc:
        return False, str(exc)


def should_wrap_line(line: str) -> bool:
    if PATCH_MARKER in line or START_MARKER in line or END_MARKER in line:
        return False
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    has_display_token = any(token in stripped for token in DISPLAY_TOKENS)
    has_target_pattern = any(pattern in stripped for pattern in TARGET_PATTERNS)
    return has_display_token and has_target_pattern


def wrap_for_developer_view(line: str) -> list[str]:
    indent = line[: len(line) - len(line.lstrip())]
    original = line.rstrip("\n")
    wrapped: list[str] = []
    wrapped.append(f"{indent}{START_MARKER}\n")
    wrapped.append(f"{indent}{PATCH_MARKER} = True\n")
    for guard_line in DEV_GUARD_LINES:
        wrapped.append(f"{indent}{guard_line}\n")
    wrapped.append(f"{indent}    {original.lstrip()}\n")
    wrapped.append(f"{indent}{END_MARKER}\n")
    return wrapped


def apply_patch() -> dict:
    if not DASHBOARD_FILE.exists():
        return {
            "overall_status": "FAIL",
            "reason": "dashboard file missing",
            "dashboard_file": str(DASHBOARD_FILE),
        }

    before_ok, before_detail = compile_ok(DASHBOARD_FILE)
    if not before_ok:
        return {
            "overall_status": "FAIL",
            "reason": "dashboard syntax invalid before patch",
            "syntax_detail": before_detail,
        }

    text = DASHBOARD_FILE.read_text(encoding="utf-8")
    if PATCH_MARKER in text:
        after_ok, after_detail = compile_ok(DASHBOARD_FILE)
        return {
            "overall_status": "PASS" if after_ok else "FAIL",
            "patch_status": "already_applied",
            "wrapped_lines": 0,
            "dashboard_syntax_valid": after_ok,
            "syntax_detail": after_detail,
        }

    backup_path = DASHBOARD_FILE.with_suffix(
        DASHBOARD_FILE.suffix + f".customer_view_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    shutil.copy2(DASHBOARD_FILE, backup_path)

    lines = text.splitlines(keepends=True)
    new_lines: list[str] = []
    wrapped_count = 0

    for line in lines:
        if should_wrap_line(line):
            new_lines.extend(wrap_for_developer_view(line))
            wrapped_count += 1
        else:
            new_lines.append(line)

    if wrapped_count == 0:
        return {
            "overall_status": "FAIL",
            "reason": "no matching local debug display lines found",
            "backup_path": str(backup_path),
            "target_patterns": TARGET_PATTERNS,
        }

    patched_text = "".join(new_lines)
    DASHBOARD_FILE.write_text(patched_text, encoding="utf-8")

    after_ok, after_detail = compile_ok(DASHBOARD_FILE)
    if not after_ok:
        shutil.copy2(backup_path, DASHBOARD_FILE)
        return {
            "overall_status": "FAIL",
            "reason": "dashboard syntax invalid after patch; restored backup",
            "backup_path": str(backup_path),
            "syntax_detail": after_detail,
            "wrapped_lines": wrapped_count,
        }

    return {
        "overall_status": "PASS",
        "patch_status": "applied",
        "backup_path": str(backup_path),
        "wrapped_lines": wrapped_count,
        "dashboard_syntax_valid": after_ok,
        "syntax_detail": after_detail,
        "customer_view_effect": "local project root and local prototype/checkpoint display lines are now Developer-view only",
        "developer_view_preserved": True,
    }


def main() -> int:
    print("=" * 100)
    print("Customer-view local debug text cleanup")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dashboard:    {DASHBOARD_FILE}")
    print()

    result = apply_patch()

    for key, value in result.items():
        print(f"{key}: {value}")

    REPORT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    REPORT_TXT.write_text("\n".join(f"{k}: {v}" for k, v in result.items()) + "\n", encoding="utf-8")

    print()
    print(f"Saved report: {REPORT_TXT}")
    print(f"Saved JSON:   {REPORT_JSON}")
    print()
    print(f"Overall customer-view cleanup status: {result.get('overall_status')}")

    return 0 if result.get("overall_status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
