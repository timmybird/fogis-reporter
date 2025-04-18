#!/usr/bin/env python3
"""Script to set up pre-commit hooks.

This script installs pre-commit and sets up the hooks for the repository.
"""

import subprocess
import sys


def run_command(cmd, description):
    """Run a shell command and print its output."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False


def install_pre_commit():
    """Install pre-commit if not already installed."""
    try:
        # Check if pre-commit is already installed
        subprocess.run(["pre-commit", "--version"], check=True, capture_output=True)
        print("pre-commit is already installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Install pre-commit
        print("pre-commit not found. Installing...")
        return run_command(
            [sys.executable, "-m", "pip", "install", "pre-commit"],
            "Installing pre-commit"
        )


def setup_pre_commit_hooks():
    """Set up pre-commit hooks for the repository."""
    return run_command(
        ["pre-commit", "install"],
        "Setting up pre-commit hooks"
    )


def update_pre_commit_hooks():
    """Update pre-commit hooks to the latest versions."""
    return run_command(
        ["pre-commit", "autoupdate"],
        "Updating pre-commit hooks to the latest versions"
    )


def main():
    """Main function to set up pre-commit hooks."""
    print("Setting up pre-commit hooks...")

    # Install pre-commit
    if not install_pre_commit():
        print("Failed to install pre-commit.")
        return 1

    # Set up pre-commit hooks
    if not setup_pre_commit_hooks():
        print("Failed to set up pre-commit hooks.")
        return 1

    # Update pre-commit hooks
    if not update_pre_commit_hooks():
        print("Failed to update pre-commit hooks.")
        print("This is not critical, continuing...")

    print("\nPre-commit hooks setup complete!")
    print("\nYou can run pre-commit manually with:")
    print("  pre-commit run --all-files")
    print("\nOr run it on specific files:")
    print("  pre-commit run --files path/to/file.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
