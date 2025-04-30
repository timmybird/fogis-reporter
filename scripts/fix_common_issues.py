#!/usr/bin/env python3
"""Script to fix the most common style issues in the codebase.

This script focuses on:
1. Adding missing module docstrings
2. Fixing docstring formatting
3. Fixing unnecessary else/elif after return
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


def add_missing_module_docstring(file_path):
    """Add a missing module docstring to a Python file.

    Args:
        file_path: Path to the Python file.

    Returns:
        True if changes were made, False otherwise.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Check if the file already has a module docstring
    if re.search(r'^""".*?"""', content, re.DOTALL) or re.search(
        r'^#!.*?\n""".*?"""', content, re.DOTALL
    ):
        return False

    # Get the module name from the file path
    module_name = os.path.basename(file_path).replace(".py", "")

    # Create a simple module docstring
    title = module_name.replace("_", " ").title()
    desc = module_name.replace("_", " ")
    module_docstring = (
        f'"""{title} module.\n\nThis module provides functionality for {desc}.\n"""\n\n'
    )

    # Check if the file starts with a shebang line
    if content.startswith("#!"):
        shebang_end = content.find("\n") + 1
        shebang = content[:shebang_end]
        rest = content[shebang_end:]
        # Add the docstring after the shebang line
        with open(file_path, "w") as f:
            f.write(shebang + module_docstring + rest)
    else:
        # Add the docstring at the beginning of the file
        with open(file_path, "w") as f:
            f.write(module_docstring + content)

    print(f"Added module docstring to {file_path}")
    return True


def fix_docstring_formatting(file_path):
    """Fix common docstring formatting issues.

    Args:
        file_path: Path to the Python file.

    Returns:
        True if changes were made, False otherwise.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    changes_made = False
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Look for docstring start
        if '"""' in line and not line.strip().endswith('"""'):
            # This might be a multi-line docstring
            docstring_start = i
            docstring_lines = [line]
            i += 1

            # Collect all docstring lines
            while i < len(lines) and '"""' not in lines[i]:
                docstring_lines.append(lines[i])
                i += 1

            if i < len(lines):
                docstring_lines.append(lines[i])

                # Check for D200: One-line docstring should fit on one line
                if (
                    len(docstring_lines) == 3
                    and docstring_lines[1].strip()
                    and not docstring_lines[2].strip().startswith('"""')
                ):
                    # Convert to one-line docstring
                    one_line_docstring = (
                        docstring_lines[0].rstrip().replace('"""', '"""')
                        + " "
                        + docstring_lines[1].strip()
                        + ' """'
                    )
                    new_lines.append(one_line_docstring + "\n")
                    changes_made = True
                    print(f"Fixed D200 in {file_path} at line {docstring_start+1}")
                    i += 1
                    continue

                # Check for D205: 1 blank line required between summary and description
                if (
                    len(docstring_lines) > 3
                    and docstring_lines[1].strip()
                    and docstring_lines[2].strip()
                ):
                    # Add blank line after summary
                    fixed_docstring = [docstring_lines[0], docstring_lines[1], "\n"]
                    fixed_docstring.extend(docstring_lines[2:])
                    new_lines.extend(fixed_docstring)
                    changes_made = True
                    print(f"Fixed D205 in {file_path} at line {docstring_start+1}")
                    i += 1
                    continue

                # Check for D415: First line should end with a period
                if (
                    docstring_lines[0].strip()
                    and not docstring_lines[0].strip().endswith(".")
                    and not docstring_lines[0].strip().endswith("?")
                    and not docstring_lines[0].strip().endswith("!")
                ):
                    # Add period to first line
                    docstring_lines[0] = docstring_lines[0].rstrip() + ".\n"
                    new_lines.extend(docstring_lines)
                    changes_made = True
                    print(f"Fixed D415 in {file_path} at line {docstring_start+1}")
                    i += 1
                    continue

            # If no fixes were applied, keep the original lines
            new_lines.extend(docstring_lines)
            i += 1
            continue

        new_lines.append(line)
        i += 1

    if changes_made:
        with open(file_path, "w") as f:
            f.writelines(new_lines)

    return changes_made


def fix_unnecessary_else_after_return(file_path):
    """Fix unnecessary else/elif after return (R505, R508).

    Args:
        file_path: Path to the Python file.

    Returns:
        True if changes were made, False otherwise.
    """
    with open(file_path, "r") as f:
        content = f.read()

    # Pattern for unnecessary else after return
    pattern_else = r"(\s+)return.*?\n\1else:"
    fixed_content = re.sub(pattern_else, r"\1return\n", content)

    # Pattern for unnecessary elif after return
    pattern_elif = r"(\s+)return.*?\n\1elif\s+(.*):"
    fixed_content = re.sub(pattern_elif, r"\1return\n\1if \2:", fixed_content)

    changes_made = content != fixed_content

    if changes_made:
        with open(file_path, "w") as f:
            f.write(fixed_content)
        print(f"Fixed unnecessary else/elif after return in {file_path}")

    return changes_made


def main():
    """Run the script.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Get Python files
    python_files = find_python_files()

    # Count of files with changes
    files_changed = 0

    # Fix issues in each file
    for file_path in python_files:
        changes = False

        # Add missing module docstrings
        changes |= add_missing_module_docstring(file_path)

        # Fix docstring formatting
        changes |= fix_docstring_formatting(file_path)

        # Fix unnecessary else/elif after return
        changes |= fix_unnecessary_else_after_return(file_path)

        if changes:
            files_changed += 1

    print(f"\nFixed issues in {files_changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
