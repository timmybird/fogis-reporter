#!/usr/bin/env python3
"""Script to fix existing code style issues in the codebase.

This script runs all the style fixers on the entire codebase to bring it up to
the project's coding standards. It should be run once to establish a baseline
of code style compliance.
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


def fix_existing_code():
    """Fix existing code style issues in the codebase.

    Returns:
        True if all fixes were applied successfully, False otherwise.
    """
    # Find the repository root
    repo_root = os.getcwd()

    # Run each fixer in sequence
    print("\n=== Running fix_common_issues.py ===")
    common_issues_result = run_command(
        [sys.executable, "scripts/fix_common_issues.py"], cwd=repo_root
    )

    print("\n=== Running fix_long_lines.py ===")
    long_lines_result = run_command(
        [sys.executable, "scripts/fix_long_lines.py"], cwd=repo_root
    )

    print("\n=== Running fix_import_order.py ===")
    import_order_result = run_command(
        [sys.executable, "scripts/fix_import_order.py"], cwd=repo_root
    )

    print("\n=== Running black ===")
    black_result = run_command([sys.executable, "-m", "black", "."], cwd=repo_root)

    print("\n=== Running isort ===")
    isort_result = run_command([sys.executable, "-m", "isort", "."], cwd=repo_root)

    print("\n=== Running ruff --fix ===")
    ruff_result = run_command(
        [sys.executable, "-m", "ruff", "check", "--fix", "."], cwd=repo_root
    )

    # Return True if all fixers succeeded
    return (
        common_issues_result == 0
        and long_lines_result == 0
        and import_order_result == 0
        and black_result == 0
        and isort_result == 0
        and ruff_result == 0
    )


def main():
    """Run the script.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Fix existing code style issues in the codebase."
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Run in non-interactive mode (no confirmation)",
    )
    args = parser.parse_args()

    print("This script will fix existing code style issues in the codebase.")
    print("It should be run once to establish a baseline of code style compliance.")
    print("WARNING: This will modify files in the codebase.")

    # Ask for confirmation if not in non-interactive mode
    if not args.yes:
        response = input("Do you want to continue? (y/n): ")
        if response.lower() not in ["y", "yes"]:
            print("Aborted.")
            return 1

    # Fix existing code
    success = fix_existing_code()

    if success:
        print("\nAll code style issues have been fixed successfully!")
        print("Please review the changes and commit them.")
    else:
        print("\nSome code style issues could not be fixed automatically.")
        print("Please fix the remaining issues manually.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
