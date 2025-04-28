#!/usr/bin/env python3
"""Script to fix import order issues in Python files.

This script identifies import order issues and fixes them by:
1. Grouping imports correctly
2. Sorting imports within each group
3. Adding blank lines between import groups
"""

import os
import re
import sys


def find_python_files(directory="."):
    """Find all Python files in the given directory and its subdirectories.

    Args:
        directory: The directory to search in.

    Returns:
        A list of paths to Python files.
    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def fix_import_order(file_path):
    """Fix import order issues in a Python file.

    Args:
        file_path: Path to the Python file.

    Returns:
        True if changes were made, False otherwise.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Find the import section
    import_section_match = re.search(
        (
            r"((?:from\s+[\w.]+\s+import\s+[\w,\s*]+|import\s+[\w,\s.]+)"
            r"(?:\n(?:from\s+[\w.]+\s+import\s+[\w,\s*]+|import\s+[\w,\s.]+))*)"
        ),
        content,
    )

    if not import_section_match:
        return False

    import_section = import_section_match.group(1)
    import_lines = import_section.strip().split("\n")

    # Categorize imports
    stdlib_imports = []
    third_party_imports = []
    first_party_imports = []
    local_imports = []

    # Define known first-party modules
    first_party_modules = {
        "api_utils",
        "emoji_config",
        "fogis_data_parser",
        "fogis_reporter",
    }

    # Define known third-party modules
    third_party_modules = {"fogis_api_client", "tabulate", "bs4", "requests", "pytest"}

    for line in import_lines:
        line = line.strip()
        if not line:
            continue

        # Extract the module name
        try:
            if line.startswith("from "):
                module = line.split("from ")[1].split(" import")[0]
            else:  # line.startswith("import ")
                module = line.split("import ")[1].split(" as")[0].split(",")[0].strip()
        except IndexError:
            # Skip lines that don't match the expected format
            continue

        # Determine the category
        if module in first_party_modules:
            first_party_imports.append(line)
        elif module in third_party_modules:
            third_party_imports.append(line)
        elif "." in module and not module.startswith("."):
            # Third-party module if it has a dot and doesn't start with a dot
            third_party_imports.append(line)
        elif module.startswith("."):
            # Relative import
            local_imports.append(line)
        else:
            # Check if it's a standard library module
            try:
                __import__(module)
                stdlib_imports.append(line)
            except ImportError:
                # If we can't import it, assume it's a third-party module
                third_party_imports.append(line)

    # Sort imports within each category
    stdlib_imports.sort()
    third_party_imports.sort()
    first_party_imports.sort()
    local_imports.sort()

    # Combine the categories with blank lines between them
    new_import_section = ""
    if stdlib_imports:
        new_import_section += "\n".join(stdlib_imports) + "\n"
    if third_party_imports:
        if new_import_section:
            new_import_section += "\n"
        new_import_section += "\n".join(third_party_imports) + "\n"
    if first_party_imports:
        if new_import_section:
            new_import_section += "\n"
        new_import_section += "\n".join(first_party_imports) + "\n"
    if local_imports:
        if new_import_section:
            new_import_section += "\n"
        new_import_section += "\n".join(local_imports) + "\n"

    # Replace the old import section with the new one
    new_content = content.replace(import_section, new_import_section)

    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"Fixed import order in {file_path}")
        return True

    return False


def main():
    """Run the script.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Get Python files
    python_files = find_python_files()

    # Count of files with changes
    files_changed = 0

    # Fix import order in each file
    for file_path in python_files:
        changes = fix_import_order(file_path)
        if changes:
            files_changed += 1

    print(f"\nFixed import order in {files_changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
