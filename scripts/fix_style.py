#!/usr/bin/env python3
"""Script to automatically fix common style issues in the codebase.

This script runs black, isort, and ruff to automatically fix style issues.
It can be run on the entire codebase or on specific files.
"""

import argparse
import os
import subprocess
import sys


def run_command(command, cwd=None):
    """Run a command and return the exit code.

    Args:
        command: The command to run as a list of strings.
        cwd: The working directory to run the command in.

    Returns:
        The exit code of the command.
    """
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd)
    return result.returncode


def find_repo_root():
    """Find the root of the repository.

    Returns:
        The path to the root of the repository.
    """
    # Start from the current directory
    current_dir = os.getcwd()

    # Keep going up until we find a .git directory or reach the root
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, ".git")):
            return current_dir
        current_dir = os.path.dirname(current_dir)

    # If we didn't find a .git directory, return the current directory
    return os.getcwd()


def fix_style(files=None, check_only=False):
    """Fix style issues in the specified files.

    Args:
        files: List of files to fix. If None, fix all Python files.
        check_only: If True, only check for issues, don't fix them.

    Returns:
        True if all style checks passed, False otherwise.
    """
    # Find the repository root
    repo_root = find_repo_root()

    # If no files are specified, find all Python files
    if not files:
        files = []
        for root, _, filenames in os.walk(repo_root):
            for filename in filenames:
                if filename.endswith(".py"):
                    files.append(os.path.join(root, filename))

    # Make sure all files exist
    for file in files:
        if not os.path.exists(file):
            print(f"Error: File {file} does not exist.")
            return False

    # Initialize success flag
    success = True

    # Run black
    black_args = ["python3", "-m", "black"]
    if check_only:
        black_args.append("--check")
    black_args.extend(files)
    black_result = run_command(black_args, cwd=repo_root)
    success = success and (black_result == 0)

    # Run isort
    isort_args = ["python3", "-m", "isort"]
    if check_only:
        isort_args.append("--check")
    isort_args.extend(files)
    isort_result = run_command(isort_args, cwd=repo_root)
    success = success and (isort_result == 0)

    # Run ruff
    ruff_args = ["python3", "-m", "ruff", "check"]
    if not check_only:
        ruff_args.append("--fix")
    ruff_args.extend(files)
    ruff_result = run_command(ruff_args, cwd=repo_root)
    success = success and (ruff_result == 0)

    return black_result == 0 and isort_result == 0 and ruff_result == 0


def main():
    """Run the script.

    Returns:
        0 if all style checks passed, 1 otherwise.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Fix style issues in the codebase.")
    parser.add_argument(
        "--check", action="store_true", help="Only check for issues, don't fix them."
    )
    parser.add_argument(
        "files", nargs="*", help="Files to fix. If not specified, fix all Python files."
    )
    args = parser.parse_args()

    # Fix style issues
    success = fix_style(args.files, args.check)

    # Return exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
