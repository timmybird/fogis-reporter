#!/usr/bin/env python3
"""Script to fix long lines in Python files.

This script identifies lines that exceed the maximum line length (88 characters)
and attempts to fix them by:
1. Breaking long string literals
2. Breaking long function calls
3. Breaking long list/dict/set literals
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


def fix_long_lines(file_path, max_length=88):
    """Fix lines that exceed the maximum length.

    Args:
        file_path: Path to the Python file.
        max_length: Maximum line length.

    Returns:
        True if changes were made, False otherwise.
    """
    with open(file_path, "r") as f:
        lines = f.readlines()

    changes_made = False
    new_lines = []

    for i, line in enumerate(lines):
        if len(line.rstrip()) <= max_length:
            new_lines.append(line)
            continue

        # Skip comment lines - these need manual fixing
        if line.strip().startswith("#"):
            new_lines.append(line)
            continue

        # Try to fix long string literals
        if '"' in line or "'" in line:
            fixed_line = fix_long_string(line, max_length)
            if fixed_line != line:
                new_lines.extend(fixed_line.splitlines(True))
                changes_made = True
                print(f"Fixed long string in {file_path} at line {i+1}")
                continue

        # Try to fix long function calls
        if "(" in line and ")" in line:
            fixed_line = fix_long_function_call(line, max_length)
            if fixed_line != line:
                new_lines.extend(fixed_line.splitlines(True))
                changes_made = True
                print(f"Fixed long function call in {file_path} at line {i+1}")
                continue

        # Try to fix long list/dict/set literals
        if "[" in line or "{" in line:
            fixed_line = fix_long_collection(line, max_length)
            if fixed_line != line:
                new_lines.extend(fixed_line.splitlines(True))
                changes_made = True
                print(f"Fixed long collection in {file_path} at line {i+1}")
                continue

        # If we couldn't fix it, keep the original line
        new_lines.append(line)

    if changes_made:
        with open(file_path, "w") as f:
            f.writelines(new_lines)

    return changes_made


def fix_long_string(line, max_length):
    """Fix a long string literal by breaking it into multiple lines.

    Args:
        line: The line containing a long string.
        max_length: Maximum line length.

    Returns:
        The fixed line or the original line if it couldn't be fixed.
    """
    # Find string literals in the line
    string_matches = list(re.finditer(r'(["\'])(.*?)\1', line))

    if not string_matches:
        return line

    # Try to break the longest string
    longest_match = max(string_matches, key=lambda m: len(m.group(2)))
    quote = longest_match.group(1)
    string_content = longest_match.group(2)

    if len(string_content) < 20:  # Don't break short strings
        return line

    # Calculate indentation for continuation lines
    indent = len(line) - len(line.lstrip())
    continuation_indent = indent + 4

    # Break the string
    prefix = line[: longest_match.start()]
    suffix = line[longest_match.end() :]

    # Split the string content into chunks
    max_chunk_length = max_length - continuation_indent - 2  # Account for quotes
    chunks = []
    current_chunk = ""

    for word in string_content.split():
        if not current_chunk:
            current_chunk = word
        elif len(current_chunk) + len(word) + 1 <= max_chunk_length:
            current_chunk += " " + word
        else:
            chunks.append(current_chunk)
            current_chunk = word

    if current_chunk:
        chunks.append(current_chunk)

    # Format the broken string
    result = prefix + quote + chunks[0] + quote + " \\\n"
    for i, chunk in enumerate(chunks[1:], 1):
        result += " " * continuation_indent + quote + chunk + quote
        if i < len(chunks) - 1:
            result += " \\\n"
        else:
            result += suffix

    return result


def fix_long_function_call(line, max_length):
    """Fix a long function call by breaking it into multiple lines.

    Args:
        line: The line containing a long function call.
        max_length: Maximum line length.

    Returns:
        The fixed line or the original line if it couldn't be fixed.
    """
    # Find the function call
    match = re.search(r"(\w+)\((.*)\)", line)
    if not match:
        return line

    function_name = match.group(1)
    args = match.group(2)

    # Split the arguments
    arg_list = []
    current_arg = ""
    paren_level = 0
    bracket_level = 0
    brace_level = 0

    for char in args:
        if char == "," and paren_level == 0 and bracket_level == 0 and brace_level == 0:
            arg_list.append(current_arg.strip())
            current_arg = ""
        else:
            current_arg += char
            if char == "(":
                paren_level += 1
            elif char == ")":
                paren_level -= 1
            elif char == "[":
                bracket_level += 1
            elif char == "]":
                bracket_level -= 1
            elif char == "{":
                brace_level += 1
            elif char == "}":
                brace_level -= 1

    if current_arg:
        arg_list.append(current_arg.strip())

    if len(arg_list) <= 1:  # Don't break if there's only one argument
        return line

    # Calculate indentation
    indent = len(line) - len(line.lstrip())
    continuation_indent = indent + 4

    # Format the broken function call
    prefix = line[: match.start()]
    suffix = line[match.end() :]

    result = prefix + function_name + "(\n"
    for i, arg in enumerate(arg_list):
        result += " " * continuation_indent + arg
        if i < len(arg_list) - 1:
            result += ",\n"
        else:
            result += "\n" + " " * indent + ")" + suffix

    return result


def fix_long_collection(line, max_length):
    """Fix a long list/dict/set literal by breaking it into multiple lines.

    Args:
        line: The line containing a long collection literal.
        max_length: Maximum line length.

    Returns:
        The fixed line or the original line if it couldn't be fixed.
    """
    # Find the collection literal
    match = re.search(r"(\[|\{)(.*?)(\]|\})", line)
    if not match:
        return line

    open_char = match.group(1)
    content = match.group(2)
    close_char = match.group(3)

    # Split the items
    item_list = []
    current_item = ""
    paren_level = 0
    bracket_level = 0
    brace_level = 0

    for char in content:
        if char == "," and paren_level == 0 and bracket_level == 0 and brace_level == 0:
            item_list.append(current_item.strip())
            current_item = ""
        else:
            current_item += char
            if char == "(":
                paren_level += 1
            elif char == ")":
                paren_level -= 1
            elif char == "[":
                bracket_level += 1
            elif char == "]":
                bracket_level -= 1
            elif char == "{":
                brace_level += 1
            elif char == "}":
                brace_level -= 1

    if current_item:
        item_list.append(current_item.strip())

    if len(item_list) <= 1:  # Don't break if there's only one item
        return line

    # Calculate indentation
    indent = len(line) - len(line.lstrip())
    continuation_indent = indent + 4

    # Format the broken collection
    prefix = line[: match.start()]
    suffix = line[match.end() :]

    result = prefix + open_char + "\n"
    for i, item in enumerate(item_list):
        result += " " * continuation_indent + item
        if i < len(item_list) - 1:
            result += ",\n"
        else:
            result += "\n" + " " * indent + close_char + suffix

    return result


def main():
    """Run the script.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    # Get Python files
    python_files = find_python_files()

    # Count of files with changes
    files_changed = 0

    # Fix long lines in each file
    for file_path in python_files:
        changes = fix_long_lines(file_path)
        if changes:
            files_changed += 1

    print(f"\nFixed long lines in {files_changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
