# Code Style Enforcement

This document describes the code style enforcement tools and configuration implemented in this project.

## Overview

We've implemented a comprehensive code style enforcement system using the following tools:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For style checking
- **mypy**: For type checking
- **ruff**: For additional linting

## Configuration Files

The following configuration files have been created or updated:

- `.flake8`: Configuration for flake8
- `pyproject.toml`: Configuration for black, isort, and ruff
- `.pre-commit-config.yaml`: Configuration for pre-commit hooks

## Helper Scripts

Several helper scripts have been created to assist with style enforcement:

### `scripts/fix_all.py`

This script runs all style fixers in sequence:

```bash
python scripts/fix_all.py
```

### `scripts/fix_style.py`

This script runs all style tools on the codebase and fixes issues where possible:

```bash
# Check style without fixing
python scripts/fix_style.py --check

# Fix style issues
python scripts/fix_style.py

# Check/fix style for specific files
python scripts/fix_style.py path/to/file1.py path/to/file2.py
```

### `scripts/lint_changed.py`

This script runs style checks only on files that have been changed in the current Git branch:

```bash
# Check style without fixing
python scripts/lint_changed.py

# Fix style issues
python scripts/lint_changed.py --fix
```

### `scripts/fix_common_issues.py`

This script fixes the most common style issues in the codebase:

- Adding missing module docstrings
- Fixing docstring formatting
- Fixing unnecessary else/elif after return

```bash
python scripts/fix_common_issues.py
```

### `scripts/fix_long_lines.py`

This script fixes long lines by breaking them into multiple lines:

```bash
python scripts/fix_long_lines.py
```

### `scripts/fix_import_order.py`

This script fixes import order issues:

```bash
python scripts/fix_import_order.py
```

## Pre-commit Hooks

Pre-commit hooks have been configured to automatically check code style before committing. To set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Style Guidelines

### Line Length

Maximum line length is 88 characters, matching Black's default.

### Imports

Imports should be grouped and sorted as follows:

1. Standard library imports
2. Third-party imports
3. First-party imports
4. Local imports

Each group should be separated by a blank line.

### Docstrings

We use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description if needed, explaining what the function does
    in more detail.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of the return value

    Raises:
        ValueError: When param1 is empty
    """
```

### Type Annotations

Use type annotations for function parameters and return values:

```python
def get_match_data(match_id: int) -> Dict[str, Any]:
    """Get data for a specific match."""
```

## Common Style Issues

The most common style issues in the codebase are:

1. **Line Length (E501)**: Lines exceeding 88 characters
2. **Import Order (I100, I101, I201, I202)**: Incorrect import ordering
3. **Docstring Issues (D100, D200, D202, D205, D212, D415)**: Missing or incorrectly formatted docstrings
4. **Unnecessary else/elif after return (R505, R508)**: Redundant control flow

## Iterative Approach

We recommend an iterative approach to fixing style issues:

1. Start with the most critical files
2. Fix one category of issues at a time
3. Run tests after each set of changes
4. Commit changes frequently

## CI/CD Integration

We've added a GitHub Actions workflow to enforce code style checks on pull requests and pushes to the main branch. The workflow is defined in `.github/workflows/code-style.yml` and runs the following checks:

- black: Checks code formatting
- isort: Checks import sorting
- flake8: Checks style rules
- ruff: Checks for additional issues
- mypy: Checks type annotations

This ensures that all code merged into the main branch follows the project's style guidelines.

## Future Improvements

Future improvements to the code style enforcement system could include:

1. More comprehensive documentation of style guidelines
2. Custom plugins for project-specific style rules
3. Integration with code review tools
