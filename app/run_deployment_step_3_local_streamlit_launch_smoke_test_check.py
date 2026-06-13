"""
run_deployment_step_3_local_streamlit_launch_smoke_test_check.py

Deployment Step 3 - local Streamlit launch smoke-test preparation.

This check does not start a long-running Streamlit server. It verifies that the
local project has the files needed to launch the paid simulator with Streamlit,
that the dashboard file compiles, and that a launch command/documentation file
has been prepared.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILE = PROJECT_ROOT / 'app' / 'paid_simulator' / 'config_form_app.py'
REQUIREMENTS_FILE = PROJECT_ROOT / 'requirements.txt'
STREAMLIT_CONFIG_FILE = PROJECT_ROOT / '.streamlit' / 'config.toml'
DOC_FILE = PROJECT_ROOT / 'docs' / 'deployment_step_3_local_streamlit_launch_smoke_test.md'
LAUNCH_CMD_FILE = PROJECT_ROOT / 'deployment_streamlit_local_launch_command.txt'

OUTPUT_REPORT_DIR = PROJECT_ROOT / 'outputs' / 'reports' / 'paid_simulator'
CHECKPOINT_REPORT = OUTPUT_REPORT_DIR / 'deployment_step_3_local_streamlit_launch_smoke_test_report.txt'
CHECKPOINT_JSON = OUTPUT_REPORT_DIR / 'deployment_step_3_local_streamlit_launch_smoke_test.json'

EXPECTED_COMMAND = 'streamlit run app/paid_simulator/config_form_app.py'


class Recorder:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, passed: bool, label: str, detail: Any = '') -> None:
        status = 'PASS' if passed else 'FAIL'
        detail_text = '' if detail is None else str(detail)
        self.rows.append({'status': status, 'label': label, 'detail': detail_text})
        print(f'{status:<10} {label:<76} {detail_text}')

    @property
    def passed(self) -> bool:
        return all(row['status'] == 'PASS' for row in self.rows)


def _compile_file(path: Path) -> tuple[bool, str]:
    try:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
        return True, 'syntax valid'
    except Exception as exc:
        return False, str(exc)


def _module_available(module_name: str) -> tuple[bool, str]:
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None, 'available' if spec is not None else 'not found'
    except Exception as exc:
        return False, str(exc)


def _streamlit_version() -> str:
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'streamlit', 'version'],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        text = (result.stdout or result.stderr or '').strip()
        if result.returncode == 0 and text:
            return text.splitlines()[0]
        return f'streamlit command returned {result.returncode}'
    except Exception as exc:
        return str(exc)


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print('=' * 100)
    print('Deployment Step 3 local Streamlit launch smoke-test preparation check')
    print('=' * 100)
    print(f'Project root: {PROJECT_ROOT}')
    print()

    rec = Recorder()

    rec.add(DASHBOARD_FILE.exists(), 'Dashboard entry point exists', DASHBOARD_FILE)
    rec.add(REQUIREMENTS_FILE.exists(), 'requirements.txt exists', REQUIREMENTS_FILE)
    rec.add(STREAMLIT_CONFIG_FILE.exists(), 'Streamlit config file exists', STREAMLIT_CONFIG_FILE)
    rec.add(DOC_FILE.exists(), 'Deployment Step 3 documentation exists', DOC_FILE)

    ok, detail = _compile_file(DASHBOARD_FILE)
    rec.add(ok, 'Dashboard entry point syntax remains valid', detail)

    text = DASHBOARD_FILE.read_text(encoding='utf-8') if DASHBOARD_FILE.exists() else ''
    rec.add('Synthetic scenarios' in text, 'Dashboard retains synthetic scenario label', 'present' if 'Synthetic scenarios' in text else None)
    rec.add('Imported historical data' in text, 'Dashboard retains historical opt-in label', 'present' if 'Imported historical data' in text else None)
    rec.add('Historical data is scenario input, not forecast' in text, 'Dashboard retains historical-data caution', 'present' if 'Historical data is scenario input, not forecast' in text else None)

    for module_name in ['streamlit', 'pandas', 'numpy', 'matplotlib']:
        available, module_detail = _module_available(module_name)
        rec.add(available, f'Python package available: {module_name}', module_detail)

    req_text = REQUIREMENTS_FILE.read_text(encoding='utf-8') if REQUIREMENTS_FILE.exists() else ''
    rec.add('streamlit' in req_text.lower(), 'requirements.txt includes streamlit', 'present' if 'streamlit' in req_text.lower() else None)
    rec.add('pandas' in req_text.lower(), 'requirements.txt includes pandas', 'present' if 'pandas' in req_text.lower() else None)
    rec.add('numpy' in req_text.lower(), 'requirements.txt includes numpy', 'present' if 'numpy' in req_text.lower() else None)
    rec.add('matplotlib' in req_text.lower(), 'requirements.txt includes matplotlib', 'present' if 'matplotlib' in req_text.lower() else None)

    LAUNCH_CMD_FILE.write_text(EXPECTED_COMMAND + '\n', encoding='utf-8')
    rec.add(LAUNCH_CMD_FILE.exists(), 'Local Streamlit launch command file written', LAUNCH_CMD_FILE)
    rec.add(LAUNCH_CMD_FILE.read_text(encoding='utf-8').strip() == EXPECTED_COMMAND, 'Launch command is expected Streamlit command', EXPECTED_COMMAND)

    streamlit_version_text = _streamlit_version()
    rec.add('streamlit' in streamlit_version_text.lower() or 'version' in streamlit_version_text.lower(), 'Streamlit command responds', streamlit_version_text)

    print()
    print('=' * 100)
    final_status = 'PASS' if rec.passed else 'FAIL'
    print(f'Overall deployment Step 3 status: {final_status}')
    print('=' * 100)

    CHECKPOINT_REPORT.write_text(
        '\n'.join([f"{r['status']:<10} {r['label']:<76} {r['detail']}" for r in rec.rows] + ['', f'Overall deployment Step 3 status: {final_status}']) + '\n',
        encoding='utf-8',
    )
    CHECKPOINT_JSON.write_text(json.dumps({'overall_status': final_status, 'checks': rec.rows}, indent=2), encoding='utf-8')
    print(f'Saved checkpoint report: {CHECKPOINT_REPORT}')
    print(f'Saved checkpoint JSON:   {CHECKPOINT_JSON}')

    return 0 if rec.passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
