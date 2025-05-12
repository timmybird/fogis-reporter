"""Tests for authentication in the CLI application.

This module tests the authentication functionality of the CLI application.
"""

import pytest
from tests.ui.helpers import assert_output_contains, assert_success

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


def test_login_success(mock_server, cli_runner):
    """Test successful login."""
    # Set up mock server to accept specific credentials
    mock_server.add_valid_credentials("test_user", "test_pass")

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        ["test_user", "test_pass", "q"]  # Username  # Password  # Quit after login
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Login successful")
    assert_output_contains(result, "Main Menu")


def test_login_failure(mock_server, cli_runner):
    """Test failed login."""
    # Set up mock server to reject specific credentials
    mock_server.add_valid_credentials("test_user", "test_pass")

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "wrong_password",  # Wrong password
            "test_user",  # Try again with correct username
            "test_pass",  # Correct password
            "q",  # Quit after login
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Login failed")
    assert_output_contains(result, "Login successful")  # Eventually succeeds
    assert_output_contains(result, "Main Menu")
