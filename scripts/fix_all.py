#!/usr/bin/env python3
"""Script to run all style fixers in sequence.

This script runs the following fixers in order:
1. fix_common_issues.py - Fixes docstrings, unnecessary else/elif after return
2. fix_style.py - Runs black, isort, and ruff to fix remaining issues
"""

import os
import subprocess
import sys


def run_script(script_name):
    """Run a Python script and return its exit code.

    Args:
        script_name: Name of the script to run.

    Returns:
        Exit code of the script.
    """
    print(f"\n{'=' * 80}")
    print(f"Running {script_name}...")
    print(f"{'=' * 80}\n")

    script_path = os.path.join("scripts", script_name)
    result = subprocess.run([sys.executable, script_path])
    return result.returncode


def main():
    """Run all style fixers in sequence.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Make sure we're in the project root
    if not os.path.exists("scripts"):
        print("Error: This script must be run from the project root.")
        return 1

    # Run each fixer in sequence
    fixers = ["fix_common_issues.py", "fix_style.py"]

    for fixer in fixers:
        exit_code = run_script(fixer)
        if exit_code != 0:
            print(f"\nError: {fixer} failed with exit code {exit_code}.")
            return exit_code

    print("\nAll style fixers completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
