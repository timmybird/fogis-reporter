#!/usr/bin/env python3
"""Development environment setup script.

This script sets up the development environment by:
1. Creating a virtual environment if it doesn't exist
2. Installing dependencies
3. Setting up pre-commit hooks
4. Creating necessary directories
"""

import os
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


def create_virtual_env():
    """Create a virtual environment if it doesn't exist."""
    if os.path.exists(".venv"):
        print("Virtual environment already exists.")
        return True

    return run_command(
        [sys.executable, "-m", "venv", ".venv"],
        "Creating virtual environment"
    )


def install_dependencies():
    """Install dependencies from requirements.txt."""
    # Determine the pip executable based on the platform
    venv_dir = ".venv"
    pip_dir = "bin" if os.name != "nt" else "Scripts"
    pip_cmd = os.path.join(venv_dir, pip_dir, "pip")

    # Install dependencies
    return run_command(
        [pip_cmd, "install", "-r", "requirements.txt"],
        "Installing dependencies"
    )


def install_dev_dependencies():
    """Install development dependencies."""
    # Determine the pip executable based on the platform
    venv_dir = ".venv"
    pip_dir = "bin" if os.name != "nt" else "Scripts"
    pip_cmd = os.path.join(venv_dir, pip_dir, "pip")

    # Install pre-commit
    return run_command(
        [pip_cmd, "install", "pre-commit"],
        "Installing pre-commit"
    )


def setup_pre_commit():
    """Set up pre-commit hooks."""
    return run_command(
        ["pre-commit", "install"],
        "Setting up pre-commit hooks"
    )


def create_directories():
    """Create necessary directories."""
    directories = [
        ".mypy_cache",
        "scripts",
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    return True


def main():
    """Main function to set up the development environment."""
    print("Setting up development environment...")

    # Create virtual environment
    if not create_virtual_env():
        print("Failed to create virtual environment.")
        return 1

    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies.")
        return 1

    # Install development dependencies
    if not install_dev_dependencies():
        print("Failed to install development dependencies.")
        return 1

    # Set up pre-commit hooks
    if not setup_pre_commit():
        print("Failed to set up pre-commit hooks.")
        return 1

    # Create necessary directories
    if not create_directories():
        print("Failed to create necessary directories.")
        return 1

    print("\nDevelopment environment setup complete!")
    print("\nActivate the virtual environment with:")
    if os.name != "nt":
        print("  source .venv/bin/activate")
    else:
        print("  .venv\\Scripts\\activate")

    return 0


if __name__ == "__main__":
    sys.exit(main())
