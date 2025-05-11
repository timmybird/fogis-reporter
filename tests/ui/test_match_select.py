"""Tests for match selection in the CLI application.

This module tests the match selection functionality of the CLI application.
"""

import pytest
from tests.ui.helpers import (
    assert_menu_contains,
    assert_output_contains,
    assert_success,
    create_test_match,
)

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


def test_list_matches(mock_server, cli_runner):
    """Test listing available matches."""
    # Set up mock server with test matches
    match1 = create_test_match(
        match_id=101, team1_name="Team A", team2_name="Team B", match_date="2025-05-15"
    )
    match2 = create_test_match(
        match_id=102, team1_name="Team C", team2_name="Team D", match_date="2025-05-16"
    )

    mock_server.add_valid_credentials("test_user", "test_pass")
    mock_server.add_match(match1)
    mock_server.add_match(match2)

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "test_pass",  # Password
            "1",  # Select "List matches"
            "q",  # Quit
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Team A vs Team B")
    assert_output_contains(result, "Team C vs Team D")
    assert_output_contains(result, "2025-05-15")
    assert_output_contains(result, "2025-05-16")


def test_select_match(mock_server, cli_runner):
    """Test selecting a match."""
    # Set up mock server with a test match
    match = create_test_match(
        match_id=101, team1_name="Team A", team2_name="Team B", match_date="2025-05-15"
    )

    mock_server.add_valid_credentials("test_user", "test_pass")
    mock_server.add_match(match)

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "test_pass",  # Password
            "1",  # Select "List matches"
            "1",  # Select the first match
            "q",  # Quit
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Team A vs Team B")
    assert_output_contains(result, "Match selected")
    assert_menu_contains(result, "Match Menu", ["Report events", "Report results"])
