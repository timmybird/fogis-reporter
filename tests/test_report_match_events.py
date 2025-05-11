"""Tests for the match events reporting functionality."""

from unittest.mock import MagicMock

import pytest

# Create a mock for FogisApiClient instead of importing it
FogisApiClient = MagicMock

# Import after mocks are set up
from fogis_data_parser import FogisDataParser  # noqa: E402
from fogis_reporter import MatchContext, report_match_events_menu  # noqa: E402


@pytest.fixture
def base_match_context():
    """Fixture to create a base MatchContext object for testing."""
    api_client_mock = MagicMock(spec=FogisApiClient)
    selected_match_data = {
        "matchid": 123,
        "lag1namn": "Team 1 Test",
        "lag2namn": "Team 2 Test",
        "matchlag1id": 1,
        "matchlag2id": 2,
        "label": "Test Match",
        "antalhalvlekar": 2,
        "tidperhalvlek": 45,
        "antalforlangningsperioder": 0,
        "tidperforlangningsperiod": 0,
    }
    team1_players_data = [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}]
    team2_players_data = [{"spelareid": 200, "trojnummer": 2, "matchdeltagareid": 2000}]
    match_events_data = []

    return MatchContext(
        api_client=api_client_mock,
        selected_match=selected_match_data,
        team1_players_json=team1_players_data,
        team2_players_json=team2_players_data,
        match_events_json=match_events_data,
        num_periods=selected_match_data["antalhalvlekar"],
        period_length=selected_match_data["tidperhalvlek"],
        num_extra_periods=selected_match_data["antalforlangningsperioder"],
        extra_period_length=selected_match_data["tidperforlangningsperiod"],
        team1_name=selected_match_data["lag1namn"],
        team2_name=selected_match_data["lag2namn"],
        team1_id=selected_match_data["matchlag1id"],
        team2_id=selected_match_data["matchlag2id"],
        match_id=selected_match_data["matchid"],
    )


def test_report_match_events_done_input(mocker, capsys, base_match_context):
    """Test report_match_events_menu with 'done' input using MatchContext."""
    # 1.  Use the fixture for the base MatchContext
    match_context = base_match_context
    match_context.team1_name = "Team 1"
    match_context.team2_name = "Team 2"

    # 2. Mock Dependencies (we only need input here; the api client is in the fixture)
    mocker.patch("builtins.input", side_effect=["", ""])

    # 3. Call report_match_events_menu with the MatchContext
    report_match_events_menu(match_context)

    # 4. Assertions
    captured = capsys.readouterr()
    print(f"Captured: {captured.out}")  # Debugging print
    assert "Match Events Menu" in captured.out

    # Access api_client_mock from the fixture
    api_client_mock = match_context.api_client  # Get api_client_mock from the context
    api_client_mock.clear_match_events.assert_not_called()  # Access from context


def test_report_match_events_clear_input(mocker, capsys, base_match_context):
    """Test report_match_events_menu with 'clear' input using MatchContext."""
    # 1. Use the fixture to get a base context:
    match_context = base_match_context
    match_context.team1_name = "Team 1"
    match_context.team2_name = "Team 2"

    # 2. Mock Dependencies
    mocker.patch("builtins.input", side_effect=["3", "clear", ""])
    mocker.patch("fogis_reporter._display_current_events_table")

    # 3. Call report_match_events_menu with the MatchContext
    report_match_events_menu(match_context)

    # 4. Assertions
    api_client_mock = match_context.api_client  # Get api_client_mock from the context
    # Check clear_match_events was called
    api_client_mock.clear_match_events.assert_called_once_with(123)
    # Check that fetch_match_events_json was called with the right match ID
    api_client_mock.fetch_match_events_json.assert_called_once_with(123)
    api_client_mock.report_match_event.assert_not_called()


def test_report_team_event(mocker, capsys, base_match_context):
    """Test for report_team_event function - basic goal reporting using MatchContext."""
    # 1. Use the fixture for the base MatchContext
    match_context = base_match_context
    match_context.team1_name = "Team 1"
    match_context.team2_name = "Team 2"

    # 2. Mock Dependencies
    api_client_mock = match_context.api_client

    # Mock FogisDataParser methods
    mocker.patch.object(FogisDataParser, "calculate_scores")
    # Mock player ID lookup
    # Get player ID by jersey number
    method_name = "get_player_id_by_team_jersey"
    player_id_mock = mocker.patch.object(FogisDataParser, method_name)
    player_id_mock.return_value = 100
    # Mock match participant ID lookup
    # Get match participant ID by jersey number
    method_name = "get_matchdeltagareid_by_team_jersey"
    participant_id_mock = mocker.patch.object(FogisDataParser, method_name)
    participant_id_mock.return_value = 1000

    # Mock input for jersey number and minute
    mocker.patch("builtins.input", side_effect=["1", "1"])

    # Mock event types
    event_types_mock = {6: {"name": "Goal", "goal": True}}
    mocker.patch("fogis_reporter.EVENT_TYPES", event_types_mock)

    # Mock the API response
    api_client_mock.report_match_event.return_value = {"status": "ok"}
    api_client_mock.fetch_match_events_json.return_value = [{"matchhandelseid": 123}]

    # Mock _display_current_events_table
    mocker.patch("fogis_reporter._display_current_events_table")

    # Mock _get_event_details_from_input
    player_data = [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}]
    event_details = (1, {"name": "Goal", "goal": True}, 6, "Goal", True, player_data)
    # Mock the event details input function
    event_details_mock = mocker.patch("fogis_reporter._get_event_details_from_input")
    event_details_mock.return_value = event_details

    # 3. Import and call report_team_event
    # Import the function we're testing
    from fogis_reporter import report_team_event  # noqa: E402

    report_team_event(match_context, 1)

    # 4. Assertions
    # Get the API client mock from the context
    api_client_mock = match_context.api_client
    api_client_mock.report_match_event.assert_called_once()
