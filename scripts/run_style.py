#!/usr/bin/env python3
"""Script to run the fix_style.py script.

This script simply runs the fix_style.py script to fix style issues.
"""

import os
import subprocess
import sys


def main():
    """Run the fix_style.py script.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    print("\nRunning fix_style.py...\n")

    script_path = os.path.join("scripts", "fix_style.py")
    result = subprocess.run([sys.executable, script_path])

    if result.returncode != 0:
        print(f"\nError: fix_style.py failed with exit code {result.returncode}.")
        return result.returncode

    print("\nStyle fixes completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
