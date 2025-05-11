"""Tests for event reporting in the CLI application.

This module tests the event reporting functionality of the CLI application.
"""

import pytest
from tests.ui.helpers import (
    assert_output_contains,
    assert_success,
    create_test_match,
    create_test_team_players,
)

# Mark all tests in this module as UI tests
pytestmark = pytest.mark.ui


def test_report_goal(mock_server, cli_runner):
    """Test reporting a goal."""
    # Set up mock server with a test match and players
    match = create_test_match(match_id=101, team1_name="Team A", team2_name="Team B")

    team1_players = create_test_team_players(
        team_id=1, num_starters=11, num_substitutes=5, start_player_id=100
    )

    team2_players = create_test_team_players(
        team_id=2, num_starters=11, num_substitutes=5, start_player_id=200
    )

    mock_server.add_valid_credentials("test_user", "test_pass")
    mock_server.add_match(match)
    mock_server.add_team_players(1, team1_players)
    mock_server.add_team_players(2, team2_players)

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "test_pass",  # Password
            "1",  # Select "List matches"
            "1",  # Select the first match
            "1",  # Select "Report events"
            "1",  # Select "Team A events"
            "1",  # Select "Goal"
            "9",  # Player jersey number
            "10",  # Minute
            "",  # Return to match events menu
            "q",  # Quit
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Goal reported successfully")
    assert_output_contains(result, "Starter Player9")  # Player name
    assert_output_contains(result, "10'")  # Minute


def test_report_card(mock_server, cli_runner):
    """Test reporting a card."""
    # Set up mock server with a test match and players
    match = create_test_match(match_id=101, team1_name="Team A", team2_name="Team B")

    team1_players = create_test_team_players(
        team_id=1, num_starters=11, num_substitutes=5, start_player_id=100
    )

    team2_players = create_test_team_players(
        team_id=2, num_starters=11, num_substitutes=5, start_player_id=200
    )

    mock_server.add_valid_credentials("test_user", "test_pass")
    mock_server.add_match(match)
    mock_server.add_team_players(1, team1_players)
    mock_server.add_team_players(2, team2_players)

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "test_pass",  # Password
            "1",  # Select "List matches"
            "1",  # Select the first match
            "1",  # Select "Report events"
            "2",  # Select "Team B events"
            "2",  # Select "Card"
            "1",  # Select "Yellow card"
            "5",  # Player jersey number
            "25",  # Minute
            "",  # Return to match events menu
            "q",  # Quit
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Card reported successfully")
    assert_output_contains(result, "Starter Player5")  # Player name
    assert_output_contains(result, "Yellow card")
    assert_output_contains(result, "25'")  # Minute


def test_report_substitution(mock_server, cli_runner):
    """Test reporting a substitution."""
    # Set up mock server with a test match and players
    match = create_test_match(match_id=101, team1_name="Team A", team2_name="Team B")

    team1_players = create_test_team_players(
        team_id=1, num_starters=11, num_substitutes=5, start_player_id=100
    )

    team2_players = create_test_team_players(
        team_id=2, num_starters=11, num_substitutes=5, start_player_id=200
    )

    mock_server.add_valid_credentials("test_user", "test_pass")
    mock_server.add_match(match)
    mock_server.add_team_players(1, team1_players)
    mock_server.add_team_players(2, team2_players)

    # Run the CLI with simulated input
    result = cli_runner.run_with_input(
        [
            "test_user",  # Username
            "test_pass",  # Password
            "1",  # Select "List matches"
            "1",  # Select the first match
            "1",  # Select "Report events"
            "1",  # Select "Team A events"
            "3",  # Select "Substitution"
            "12",  # Player coming on (jersey number)
            "7",  # Player going off (jersey number)
            "60",  # Minute
            "",  # Return to match events menu
            "q",  # Quit
        ]
    )

    # Assert expected output
    assert_success(result)
    assert_output_contains(result, "Substitution reported successfully")
    assert_output_contains(result, "Sub Player12")  # Player coming on
    assert_output_contains(result, "Starter Player7")  # Player going off
    assert_output_contains(result, "60'")  # Minute
