#!/usr/bin/env python3
"""Script to run tests only on changed files.

This script identifies Python files that have been changed in the current Git branch
compared to the main branch, and runs pytest only on the corresponding test files.
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


def find_test_files(changed_files):
    """Find test files corresponding to the changed files."""
    test_files = []

    for file in changed_files:
        # If it's already a test file, include it
        if file.startswith("tests/") or "test_" in file:
            test_files.append(file)
            continue

        # For non-test files, look for corresponding test files
        filename = os.path.basename(file)
        module_name = os.path.splitext(filename)[0]

        # Check for test files with common naming patterns
        possible_test_files = [
            f"tests/test_{module_name}.py",
            f"tests/{module_name}_test.py",
        ]

        for test_file in possible_test_files:
            if os.path.exists(test_file):
                test_files.append(test_file)

    return test_files


def run_tests(test_files):
    """Run pytest on the specified test files."""
    if not test_files:
        print("No test files to run.")
        return 0

    print(f"Running tests for {len(test_files)} files:")
    for file in test_files:
        print(f"  - {file}")

    # Run pytest with the specified test files
    cmd = ["pytest"] + test_files + ["-v"]
    result = subprocess.run(cmd)

    return result.returncode


def main():
    """Main function to run tests on changed files."""
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

    # Find corresponding test files
    test_files = find_test_files(changed_files)

    # Run tests
    return run_tests(test_files)


if __name__ == "__main__":
    sys.exit(main())
