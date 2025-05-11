# Contributing to FOGIS Reporter

Thank you for your interest in contributing to FOGIS Reporter! This document provides guidelines and instructions for contributing to this project.

## Organization-Wide Guidelines

**Important:** This repository follows the PitchConnect organization-wide contribution guidelines. Please refer to the [organization-wide CONTRIBUTING document](https://github.com/PitchConnect/.github/blob/main/CONTRIBUTING.md) for essential information that applies to all PitchConnect repositories.

The organization-wide guidelines should be followed in addition to the repository-specific guidelines outlined in this document.

## Table of Contents

- [Organization-Wide Guidelines](#organization-wide-guidelines)
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [GitFlow Pattern](#gitflow-pattern)
  - [GitHub Issue Closing and GitFlow](#github-issue-closing-and-gitflow)
- [GitHub CLI Best Practices](#github-cli-best-practices)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting Guidelines](#issue-reporting-guidelines)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Working with AI Agents](#working-with-ai-agents)

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

This project follows the GitFlow workflow pattern. Please read the [GitFlow Pattern](#gitflow-pattern) section for details.

1. Create a new branch for your feature or bugfix following the GitFlow naming conventions:
   ```
   # For features (branch from develop)
   git checkout develop
   git checkout -b feature/your-feature-name
   ```
   or
   ```
   # For bugfixes (branch from develop)
   git checkout develop
   git checkout -b fix/your-bugfix-name
   ```
   or
   ```
   # For hotfixes (branch from main)
   git checkout main
   git checkout -b hotfix/critical-issue-fix
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

## GitFlow Pattern

This project follows the GitFlow branching model. Here's an overview of the branch structure:

- **main**: Production-ready code. Only merge from release branches or hotfix branches.
- **develop**: Main development branch. Features are merged into this branch.
- **feature/\***: Feature branches for new functionality. Branch off from develop.
- **fix/\***: Bug fix branches for non-critical issues. Branch off from develop.
- **release/\***: Release preparation branches. Branch off from develop.
- **hotfix/\***: Hotfix branches for critical production issues. Branch off from main.

Workflow:

1. Create feature branches from develop
2. When a feature is complete, merge it into develop
3. When ready for release, create a release branch from develop
4. After testing the release branch, merge it into main and back into develop
5. If issues are found in production, create a hotfix branch from main
6. After fixing, merge the hotfix into both main and develop

### GitHub Issue Closing and GitFlow

**Important:** GitHub only automatically closes issues when PRs with keywords like "Fixes #123" or "Closes #123" are merged into the **default branch** (main). When following GitFlow, most PRs are merged into the `develop` branch, not directly to `main`.

To handle this limitation, you have two options:

1. **Manual closure**: After merging a PR into `develop` that implements an issue, manually close the issue with a comment explaining it's implemented in `develop` and will be in `main` with the next release.

   ```bash
   gh issue close 123 --comment "This issue has been implemented in PR #456, which has been merged into the develop branch following our GitFlow workflow."
   ```

2. **Alternative wording**: Use "Addresses #123" or "Implements #123" instead of "Fixes #123" in PR descriptions for PRs targeting `develop`. This creates a reference without promising automatic closure.

This approach ensures accurate issue tracking while following GitFlow best practices.

## GitHub CLI Best Practices

When using GitHub CLI (`gh`), be aware of the following limitations and best practices:

### Markdown Handling

GitHub CLI has limitations when handling complex markdown content directly in command arguments. For complex markdown content (issues, pull requests, comments), use files instead.

**Example: Creating an issue with complex markdown**

```bash
# Instead of this (which may not render markdown correctly):
# gh issue create --title "Complex Issue" --body "## Heading\n- List item 1\n- List item 2"

# Do this instead:
# 1. Create a markdown file with your content
cat > issue_description.md << 'EOL'
## Problem Description

- List item 1
- List item 2

## Steps to Reproduce

1. Step one
2. Step two

```code example```
EOL

# 2. Create the issue using the file
gh issue create --title "Complex Issue" --body-file issue_description.md
```

**Example: Creating a pull request with complex markdown**

```bash
cat > pr_description.md << 'EOL'
## Changes Made

- Implemented feature X
- Fixed bug Y

## Testing Done

- Added unit tests
- Manually tested scenarios

## Screenshots

![Description](url-to-image)
EOL

gh pr create --title "Add new feature" --body-file pr_description.md
```

### Cleaning Up Temporary Markdown Files

After creating issues or PRs using markdown files, remember to clean up these temporary files to avoid cluttering the repository:

```bash
# After your PR or issue is created, remove the temporary file
rm issue_description.md
rm pr_description.md
```

Alternatively, you can create these files in a temporary directory:

```bash
# Create files in /tmp directory (they will be automatically cleaned up eventually)
cat > /tmp/issue_description.md << 'EOL'
...
EOL

gh issue create --title "Issue Title" --body-file /tmp/issue_description.md
```

**Important:** Always clean up temporary markdown files before merging a PR. These files should not be committed to the repository.

## Pull Request Process

1. **Always reference the issue** your PR addresses using the GitHub issue number
   - For PRs targeting `main`: Use "Fixes #123" or "Closes #123" for automatic closure
   - For PRs targeting `develop`: Use "Addresses #123" or "Implements #123" (see [GitHub Issue Closing and GitFlow](#github-issue-closing-and-gitflow))
2. **Reference CONTRIBUTING.md**: Include a link to CONTRIBUTING.md in your PR description as a reminder for reviewers
3. Follow the GitFlow pattern when targeting branches (usually target develop for features, main for hotfixes)
4. For complex PR descriptions, use the GitHub CLI with markdown files as described in the [GitHub CLI Best Practices](#github-cli-best-practices) section
5. Ensure your code passes all tests
6. Update documentation if necessary
7. Add tests for new features
8. Make sure your code follows the project's coding standards
9. **Clean up temporary files**: Remove any temporary markdown files or other temporary files before merging
10. Request a review from a maintainer

## Issue Reporting Guidelines

When reporting issues, please include:

1. **Clear title and description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** and what actually happened
4. **Environment details**:
   - Python version
   - Operating system
   - Any relevant configuration
5. **Reference CONTRIBUTING.md**: Include a link to CONTRIBUTING.md in your issue description

Use the provided issue templates when available. For complex issues, consider using a markdown file with the GitHub CLI as described in the [GitHub CLI Best Practices](#github-cli-best-practices) section.

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

### Pre-commit Hooks and CI/CD Pipeline

We use pre-commit to automatically run checks before each commit. The same checks are also run in the CI/CD pipeline to ensure consistency between local development and CI/CD:

```bash
# Set up pre-commit hooks with the dedicated script
python scripts/setup_pre_commit.py

# Run pre-commit on specific files (faster)
pre-commit run --files path/to/file.py

# Run pre-commit on all files
pre-commit run --all-files
```

### CI/CD Pipeline

The CI/CD pipeline runs the following checks:

1. **Code Quality Checks**: Runs pre-commit hooks on all files
2. **Python CI**: Runs tests, linting, and type checking

The CI/CD pipeline is configured to fail if any of these checks fail. This ensures that all code merged into the repository meets our quality standards.

If you encounter CI/CD failures, you can run the same checks locally to debug the issues:

```bash
# Run pre-commit hooks on all files
pre-commit run --all-files

# Run tests
pytest

# Run linting
flake8 .

# Run type checking
mypy --config-file=mypy.ini
```

The setup script will:
- Install pre-commit if not already installed
- Set up the hooks for the repository
- Update the hooks to the latest versions

## Working with AI Agents

This project welcomes contributions from both human developers and AI agents. Here are guidelines for working with AI agents:

### For Humans Working with AI Agents

1. **Provide clear instructions**: Be specific about what you want the AI to do

2. **Review AI-generated code carefully**: Always review code generated by AI before committing

3. **Provide feedback**: Let the AI know what it did well and what could be improved

4. **Set boundaries**: Be clear about what the AI should and shouldn't modify

5. **Reference this document**: Always remind the AI to follow the guidelines in CONTRIBUTING.md

6. **Maintain responsibility**: You are responsible for all code submitted under your name, even if generated by AI

### For AI Agents Contributing to the Project

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

9. **Reference CONTRIBUTING.md**: Always mention and link to CONTRIBUTING.md in PRs and issues

10. **Clean up temporary files**: Remove any temporary markdown files created for PRs or issues before merging

Remember that your contributions should be focused on helping the human developers, not replacing them. Your role is to assist, suggest, and implement when asked, but final decisions rest with the human maintainers.
