#!/usr/bin/env python3
"""Script to run style checks on changed files.

This script identifies Python files that have been changed in the current Git branch
compared to the main branch, and runs black, isort, flake8, ruff, and mypy only on
those files.
"""

import argparse
import subprocess
import sys


def get_changed_files():
    """Get a list of Python files that have been changed in the current branch."""
    try:
        # Get the list of changed files compared to main branch
        result = subprocess.run(
            ["git", "diff", "--name-only", "main"],
            capture_output=True,
            text=True,
            check=True,
        )
        changed_files = result.stdout.strip().split("\n")

        # Filter for Python files and return them
        return [f for f in changed_files if f.endswith(".py")]
    except subprocess.CalledProcessError:
        print("Error: Failed to get changed files.")
        return []


def run_black(files, fix=False):
    """Run black on the specified files.

    Args:
        files: List of files to check
        fix: If True, automatically fix issues

    Returns:
        Return code from black
    """
    if not files:
        print("No files to check with black.")
        return 0

    print(f"Running black on {len(files)} files:")
    for file in files:
        print(f"  - {file}")

    # Run black with the specified files
    cmd = ["python3", "-m", "black"]
    if not fix:
        cmd.append("--check")
    cmd.extend(files)
    result = subprocess.run(cmd)

    return result.returncode


def run_isort(files, fix=False):
    """Run isort on the specified files.

    Args:
        files: List of files to check
        fix: If True, automatically fix issues

    Returns:
        Return code from isort
    """
    if not files:
        print("No files to check with isort.")
        return 0

    print(f"Running isort on {len(files)} files:")
    for file in files:
        print(f"  - {file}")

    # Run isort with the specified files
    cmd = ["python3", "-m", "isort"]
    if not fix:
        cmd.append("--check")
    cmd.extend(files)
    result = subprocess.run(cmd)

    return result.returncode


def run_flake8(files):
    """Run flake8 on the specified files.

    Args:
        files: List of files to check

    Returns:
        Return code from flake8
    """
    if not files:
        print("No files to check with flake8.")
        return 0

    print(f"Running flake8 on {len(files)} files:")
    for file in files:
        print(f"  - {file}")

    # Run flake8 with the specified files
    cmd = ["python3", "-m", "flake8"]
    cmd.extend(files)
    result = subprocess.run(cmd)

    return result.returncode


def run_ruff(files, fix=False):
    """Run ruff on the specified files.

    Args:
        files: List of files to check
        fix: If True, automatically fix issues

    Returns:
        Return code from ruff
    """
    if not files:
        print("No files to lint with ruff.")
        return 0

    print(f"Running ruff on {len(files)} files:")
    for file in files:
        print(f"  - {file}")

    # Run ruff with the specified files
    cmd = ["python3", "-m", "ruff", "check"]
    if fix:
        cmd.append("--fix")
    cmd.extend(files)
    result = subprocess.run(cmd)

    return result.returncode


def run_mypy(files):
    """Run mypy on the specified files.

    Args:
        files: List of files to check

    Returns:
        Return code from mypy
    """
    if not files:
        print("No files to check with mypy.")
        return 0

    print(f"Running mypy on {len(files)} files:")
    for file in files:
        print(f"  - {file}")

    # Run mypy with the specified files
    cmd = ["python3", "-m", "mypy"]
    cmd.extend(files)
    result = subprocess.run(cmd)

    return result.returncode


def main():
    """Run the script.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = argparse.ArgumentParser(
        description="Run style checks on files changed in the current branch."
    )
    parser.add_argument(
        "--fix", action="store_true", help="Fix issues instead of just checking"
    )
    args = parser.parse_args()

    # Get the list of changed files
    changed_files = get_changed_files()
    if not changed_files:
        print("No Python files have been changed.")
        return 0

    # Run style checks
    black_result = run_black(changed_files, args.fix)
    isort_result = run_isort(changed_files, args.fix)
    flake8_result = run_flake8(changed_files)
    ruff_result = run_ruff(changed_files, args.fix)
    mypy_result = run_mypy(changed_files)

    # Return non-zero if any check failed
    if (
        black_result != 0
        or isort_result != 0
        or flake8_result != 0
        or ruff_result != 0
        or mypy_result != 0
    ):
        print("\nSome style checks failed.")
        return 1

    print("\nAll style checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
