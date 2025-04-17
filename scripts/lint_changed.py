#!/usr/bin/env python3
"""Script to run linting tools only on changed files.

This script identifies Python files that have been changed in the current Git branch
compared to the main branch, and runs flake8 and mypy only on those files.
"""

import os
from pathlib import Path
import subprocess
import sys


def get_changed_files():
    """Get a list of Python files that have been changed in the current branch."""
    try:
        # Get the list of changed files compared to main branch
        result = subprocess.run(
            ["git", "diff", "--name-only", "main", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Filter for Python files only
        changed_files = [
            file for file in result.stdout.splitlines()
            if file.endswith(".py") and os.path.exists(file)
        ]

        return changed_files
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        return []


def run_flake8(files):
    """Run flake8 on the specified files."""
    if not files:
        print("No files to lint with flake8.")
        return 0

    print(f"Running flake8 on {len(files)} files:")
    for file in files:
        print(f"  - {file}")

    # Run flake8 with the specified files
    cmd = ["flake8"] + files
    result = subprocess.run(cmd)

    return result.returncode


def run_mypy(files):
    """Run mypy on the specified files."""
    if not files:
        print("No files to type check with mypy.")
        return 0

    print(f"Running mypy on {len(files)} files:")
    for file in files:
        print(f"  - {file}")

    # Run mypy with the specified files
    cmd = ["mypy"] + files
    result = subprocess.run(cmd)

    return result.returncode


def main():
    """Main function to run linting tools on changed files."""
    # Create scripts directory if it doesn't exist
    scripts_dir = Path(__file__).parent
    if not scripts_dir.exists():
        scripts_dir.mkdir(parents=True)

    # Get changed files
    changed_files = get_changed_files()
    if not changed_files:
        print("No Python files have been changed.")
        return 0

    print(f"Found {len(changed_files)} changed Python files:")
    for file in changed_files:
        print(f"  - {file}")

    # Run flake8
    flake8_result = run_flake8(changed_files)

    # Run mypy
    mypy_result = run_mypy(changed_files)

    # Return non-zero if any tool failed
    return flake8_result or mypy_result


if __name__ == "__main__":
    sys.exit(main())
