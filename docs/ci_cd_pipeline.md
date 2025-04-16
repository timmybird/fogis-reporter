# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline set up for the FOGIS Reporter project.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and consists of automated testing, linting, and type checking to ensure code quality and prevent regressions.

## Workflow Configuration

The pipeline is defined in `.github/workflows/python-ci.yml` and includes the following jobs:

### Test Job

This job runs on multiple Python versions (3.8, 3.9, 3.10) and performs:

1. **Critical Linting with Flake8**: Enforces critical errors (syntax errors, undefined names) while reporting style issues as informational only
2. **Type Checking with MyPy**: Verifies type annotations according to the configuration in `mypy.ini`
3. **Testing with Pytest (Informational)**: Runs tests but doesn't fail the build if tests fail
4. **Coverage Upload**: Uploads the coverage report to Codecov for visualization

### Pre-commit Job (Informational)

This job runs all pre-commit hooks defined in `.pre-commit-config.yaml` on all files but doesn't fail the build if hooks fail. It checks for:

1. No trailing whitespace
2. Files end with a newline
3. Valid YAML and JSON files
4. No debug statements in code
5. No large files added to the repository

## When the Pipeline Runs

The pipeline runs automatically on:

1. Every push to the `main` branch
2. Every pull request targeting the `main` branch

## Badges

The README includes a badge showing the current status of the CI pipeline:

[![Python CI](https://github.com/timmybird/fogis-reporter/actions/workflows/python-ci.yml/badge.svg)](https://github.com/timmybird/fogis-reporter/actions/workflows/python-ci.yml)

## Local Development

Developers can run the same checks locally before pushing code:

```bash
# Run flake8
flake8

# Run mypy
mypy .

# Run tests with coverage
pytest --cov=.

# Run pre-commit hooks on all files
pre-commit run --all-files
```

## Future Enhancements

Potential future enhancements to the CI/CD pipeline:

1. Automated deployment to PyPI for releases
2. Integration with code quality platforms like SonarQube
3. Automated dependency updates with Dependabot
4. Performance benchmarking
5. Security scanning
