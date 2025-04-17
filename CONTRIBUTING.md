# Contributing to FOGIS Reporter

Thank you for your interest in contributing to FOGIS Reporter! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Special Guidelines for AI Assistants](#special-guidelines-for-ai-assistants)

## Code of Conduct

Please be respectful and considerate of others when contributing to this project. We aim to foster an inclusive and welcoming community.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/fogis-reporter.git`
3. Run the setup script to quickly set up your development environment:
   ```bash
   python scripts/setup_dev.py
   ```
4. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`

The setup script will:
- Create a virtual environment
- Install dependencies from requirements.txt
- Set up pre-commit hooks
- Create necessary directories

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```
   git checkout -b feature/your-feature-name
   ```
   or
   ```
   git checkout -b fix/your-bugfix-name
   ```

2. Make your changes and commit them with clear, descriptive commit messages:
   ```
   git commit -m "Add feature: your feature description"
   ```

3. Push your branch to your fork:
   ```
   git push origin feature/your-feature-name
   ```

4. Create a pull request from your branch to the main repository

## Pull Request Process

1. **Always reference the issue** your PR addresses using the GitHub issue number (e.g., "Fixes #123")
2. Ensure your code passes all tests
3. Update documentation if necessary
4. Add tests for new features
5. Make sure your code follows the project's coding standards
6. Request a review from a maintainer

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all functions, classes, and modules
- Keep lines under 100 characters
- Use meaningful variable and function names

## Testing

- Write tests for all new features and bug fixes
- Run the test suite before submitting a PR:
  ```bash
  # Run all tests
  python -m pytest

  # Run tests with coverage
  pytest --cov=.

  # Run tests only on changed files (faster)
  python scripts/run_tests_changed.py
  ```
- Aim for high test coverage

## Optimized Development Workflow

We've optimized the development workflow to make it faster and more efficient:

### Helper Scripts

The project includes several helper scripts to streamline development:

```bash
# Run tests only on changed files
python scripts/run_tests_changed.py

# Run linting only on changed files
python scripts/lint_changed.py
```

### Linting and Type Checking

```bash
# Run flake8 on specific files (faster than running on the entire codebase)
flake8 path/to/file.py

# Run mypy with incremental mode for faster type checking
mypy path/to/file.py
```

### Pre-commit Hooks

We use pre-commit to automatically run checks before each commit:

```bash
# Set up pre-commit hooks with the dedicated script
python scripts/setup_pre_commit.py

# Run pre-commit on specific files (faster)
pre-commit run --files path/to/file.py

# Run pre-commit on all files
pre-commit run --all-files
```

The setup script will:
- Install pre-commit if not already installed
- Set up the hooks for the repository
- Update the hooks to the latest versions

## Special Guidelines for AI Assistants

If you are an AI assistant helping with this project, please follow these additional guidelines:

1. **Always reference issues**: When creating PRs, always reference the relevant issue number using the GitHub syntax (e.g., "Fixes #123" or "Addresses #456")

2. **Branch naming**: Use the conventional branch naming format:
   - `feature/descriptive-name` for new features
   - `fix/descriptive-name` for bug fixes
   - `docs/descriptive-name` for documentation changes
   - `refactor/descriptive-name` for code refactoring

3. **Don't close issues automatically**: Let the human maintainers decide when to close issues

4. **Provide context**: Always explain your reasoning and approach in PR descriptions

5. **Respect existing patterns**: Follow the coding patterns and architecture already established in the project

6. **Be explicit about changes**: Clearly list all changes made in the PR description

7. **Test coverage**: Ensure that any code changes are covered by tests

8. **Documentation**: Update documentation to reflect any changes made

Remember that your contributions should be focused on helping the human developers, not replacing them. Your role is to assist, suggest, and implement when asked, but final decisions rest with the human maintainers.
