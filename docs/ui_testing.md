# UI Testing Guide

This guide explains how to write and run UI tests for the FOGIS Reporter CLI application.

## Overview

UI tests simulate user interaction with the CLI application. They use a mock server to simulate the FOGIS API, allowing tests to run without real FOGIS credentials.

## Prerequisites

- Python 3.8 or higher
- fogis-reporter installed in development mode
- fogis-api-client with mock server support

## Installation

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

## Running UI Tests

```bash
# Run all UI tests
pytest tests/ui -v -m ui

# Run a specific UI test file
pytest tests/ui/test_auth.py -v

# Run a specific UI test
pytest tests/ui/test_auth.py::test_login_success -v
```

## Writing UI Tests

UI tests are located in the `tests/ui` directory. Each test file focuses on a specific area of functionality:

- `test_auth.py`: Authentication tests
- `test_match_select.py`: Match selection tests
- `test_event_report.py`: Event reporting tests
- `test_results.py`: Match results reporting tests

### Test Structure

A typical UI test follows this structure:

1. Set up the mock server with test data
2. Run the CLI with simulated user input
3. Assert that the output contains expected content

Example:

```python
def test_login_success(mock_server, cli_runner):
    """Test successful login."""
    # Set up mock server to accept specific credentials
    mock_server.add_valid_credentials("test_user", "test_pass")

    # Run the CLI with simulated input
    result = cli_runner.run_with_input([
        "test_user",  # Username
        "test_pass",  # Password
        "q"           # Quit after login
    ])

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Login successful")
    assert_output_contains(result, "Main Menu")
```

### Fixtures

The UI tests use the following fixtures:

- `mock_server`: A fixture that provides a mock server for testing
- `cli_runner`: A fixture that provides a CLI runner for testing

These fixtures are defined in `tests/ui/conftest.py`.

### Helpers

The UI tests use the following helpers:

- `CLIRunner`: A class for running the CLI and interacting with it
- `assert_output_contains`: Assert that the output contains the expected string
- `assert_success`: Assert that the command succeeded
- `create_test_match`: Create a test match
- `create_test_team_players`: Create test players for a team

These helpers are defined in the `tests/ui/helpers` directory.

## Mock Server

The mock server simulates the FOGIS API, allowing tests to run without real FOGIS credentials. It provides the following functionality:

- Authentication
- Match listing
- Player listing
- Event reporting
- Match results reporting

The mock server is configured to run on a random available port for each test, ensuring that tests don't interfere with each other.

## Test Data

Test data is generated using helper functions in the `tests/ui/helpers/test_data.py` module. These functions create realistic test data for matches, players, events, and results.

## Debugging

If a UI test fails, you can see the full output by running the test with the `-v` flag:

```bash
pytest tests/ui/test_auth.py::test_login_success -v
```

You can also add print statements to the test to see what's happening:

```python
def test_login_success(mock_server, cli_runner):
    # ...
    result = cli_runner.run_with_input([...])
    print(f"Output: {result.stdout}")
    # ...
```

## CI/CD Integration

UI tests are run as part of the CI/CD pipeline. The workflow is defined in `.github/workflows/ui-tests.yml`.
