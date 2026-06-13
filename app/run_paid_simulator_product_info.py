"""
run_paid_simulator_product_info.py

Small PyCharm-friendly runner that prints the paid simulator product metadata.

Run this file directly from PyCharm to confirm that the product branding/version
module is installed correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.product_info import get_product_info, get_status_lines


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 88)


def main() -> None:
    info = get_product_info()

    print("=" * 88)
    print("Paid simulator product information")
    print("=" * 88)

    print_section("Product metadata")
    for line in get_status_lines():
        print(line)

    print_section("Positioning statement")
    print(info.positioning_statement)

    print_section("Primary workflow")
    for index, item in enumerate(info.primary_workflow, start=1):
        print(f"{index}. {item}")

    print_section("Key limitations")
    for index, item in enumerate(info.key_limitations, start=1):
        print(f"{index}. {item}")

    print("\n" + "=" * 88)
    print("Overall product-info status: PASS")
    print("The paid simulator product metadata module is installed and importable.")
    print("=" * 88)


if __name__ == "__main__":
    main()
