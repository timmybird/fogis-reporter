"""Tests for match results reporting in the CLI application.

This module tests the match results reporting functionality of the CLI application.
"""

import pytest
from tests.ui.helpers import assert_output_contains, assert_success, create_test_match

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


def test_report_match_results(mock_server, cli_runner):
    """Test reporting match results."""
    # Set up mock server with a test match
    match = create_test_match(match_id=101, team1_name="Team A", team2_name="Team B")

    mock_server.add_valid_credentials("test_user", "test_pass")
    mock_server.add_match(match)

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "test_pass",  # Password
            "1",  # Select "List matches"
            "1",  # Select the first match
            "2",  # Select "Report results"
            "n",  # Don't accept calculated scores
            "1",  # Halftime score team 1
            "0",  # Halftime score team 2
            "2",  # Fulltime score team 1
            "1",  # Fulltime score team 2
            "y",  # Confirm scores
            "",  # Return to match menu
            "q",  # Quit
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Match results reported successfully")
    assert_output_contains(result, "Team A 2 - 1 Team B")
    assert_output_contains(result, "Halftime: 1 - 0")


def test_report_match_results_with_verification(mock_server, cli_runner):
    """Test reporting match results with verification."""
    # Set up mock server with a test match
    match = create_test_match(match_id=101, team1_name="Team A", team2_name="Team B")

    # This would set up the mock server to return the match result for verification
    # In a real implementation, this would be handled by the mock server
    mock_server.add_valid_credentials("test_user", "test_pass")
    mock_server.add_match(match)

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "test_pass",  # Password
            "1",  # Select "List matches"
            "1",  # Select the first match
            "2",  # Select "Report results"
            "n",  # Don't accept calculated scores
            "1",  # Halftime score team 1
            "0",  # Halftime score team 2
            "2",  # Fulltime score team 1
            "1",  # Fulltime score team 2
            "y",  # Confirm scores
            "",  # Return to match menu
            "q",  # Quit
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Match results reported successfully")
    assert_output_contains(result, "Team A 2 - 1 Team B")
    assert_output_contains(result, "Halftime: 1 - 0")
