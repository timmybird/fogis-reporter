import sys
from unittest.mock import MagicMock, patch

# Mock the fogis_api_client module
sys.modules["fogis_api_client"] = MagicMock()
sys.modules["fogis_api_client.fogis_api_client"] = MagicMock()
sys.modules["fogis_api_client.fogis_api_client"].FogisApiClient = MagicMock
sys.modules["fogis_api_client.fogis_api_client"].EVENT_TYPES = {}
sys.modules["fogis_api_client.fogis_api_client"].FogisLoginError = Exception

# Mock other dependencies
sys.modules["fogis_data_parser"] = MagicMock()
sys.modules["match_context"] = MagicMock()
sys.modules["match_event_table_formatter"] = MagicMock()

# Now we can import from fogis_reporter
from fogis_reporter import _get_event_details_from_input, report_team_event


# Test for getting event details from input
def test_get_event_details_from_input_valid():
    """Test getting event details from valid input."""
    # Mock event_types
    event_types_mock = {
        6: {"name": "Goal", "goal": True},
        7: {"name": "Yellow Card"},
        8: {"name": "Red Card"},
        9: {"name": "Substitution"},
        10: {"name": "Team Official Action"},
        23: {"name": "Game End", "control_event": True},  # This should be skipped
    }

    # Mock team players
    team1_players_mock = [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}]
    team2_players_mock = [{"spelareid": 200, "trojnummer": 1, "matchdeltagareid": 2000}]

    # Test with team 1 and goal event
    with patch("fogis_reporter.EVENT_TYPES", event_types_mock):
        with patch("builtins.input", return_value="6"):  # Select Goal event
            (
                team_number,
                selected_event_type,
                event_type_id,
                event_type_name,
                is_goal_event,
                current_team_players_json,
            ) = _get_event_details_from_input(
                "1", team1_players_mock, team2_players_mock
            )

            # Check the returned values
            assert team_number == 1
            assert selected_event_type == {"name": "Goal", "goal": True}
            assert event_type_id == 6
            assert event_type_name == "Goal"
            assert is_goal_event == True
            assert current_team_players_json == team1_players_mock


# Test for getting event details with invalid team number
def test_get_event_details_from_input_invalid_team():
    """Test getting event details with invalid team number."""
    # Mock team players
    team1_players_mock = [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}]
    team2_players_mock = [{"spelareid": 200, "trojnummer": 1, "matchdeltagareid": 2000}]

    # Test with invalid team number
    (
        team_number,
        selected_event_type,
        event_type_id,
        event_type_name,
        is_goal_event,
        current_team_players_json,
    ) = _get_event_details_from_input("3", team1_players_mock, team2_players_mock)

    # Check that all returned values are None
    assert team_number is None
    assert selected_event_type is None
    assert event_type_id is None
    assert event_type_name is None
    assert is_goal_event is None
    assert current_team_players_json is None


# Test for getting event details with 'done' input
def test_get_event_details_from_input_done():
    """Test getting event details with 'done' input."""
    # Mock team players
    team1_players_mock = [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}]
    team2_players_mock = [{"spelareid": 200, "trojnummer": 1, "matchdeltagareid": 2000}]

    # Test with 'done' input
    (
        team_number,
        selected_event_type,
        event_type_id,
        event_type_name,
        is_goal_event,
        current_team_players_json,
    ) = _get_event_details_from_input("done", team1_players_mock, team2_players_mock)

    # Check that all returned values are None
    assert team_number is None
    assert selected_event_type is None
    assert event_type_id is None
    assert event_type_name is None
    assert is_goal_event is None
    assert current_team_players_json is None


# Test for getting event details with invalid event type
def test_get_event_details_from_input_invalid_event():
    """Test getting event details with invalid event type."""
    # Mock event_types
    event_types_mock = {6: {"name": "Goal", "goal": True}, 7: {"name": "Yellow Card"}}

    # Mock team players
    team1_players_mock = [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}]
    team2_players_mock = [{"spelareid": 200, "trojnummer": 1, "matchdeltagareid": 2000}]

    # Test with valid team but invalid event type
    with patch("fogis_reporter.EVENT_TYPES", event_types_mock):
        with patch("builtins.input", return_value="99"):  # Select invalid event
            (
                team_number,
                selected_event_type,
                event_type_id,
                event_type_name,
                is_goal_event,
                current_team_players_json,
            ) = _get_event_details_from_input(
                "1", team1_players_mock, team2_players_mock
            )

            # Check that all returned values are None
            assert team_number is None
            assert selected_event_type is None
            assert event_type_id is None
            assert event_type_name is None
            assert is_goal_event is None
            assert current_team_players_json is None


# Test for reporting a goal event
def test_report_team_event_goal():
    """Test reporting a goal event."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock FogisDataParser.calculate_scores
    scores_mock = MagicMock()
    scores_mock.regular_time.home = 1
    scores_mock.regular_time.away = 0

    # Mock _get_event_details_from_input
    event_details_mock = (
        1,
        {"name": "Goal", "goal": True},
        6,
        "Goal",
        True,
        [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}],
    )

    # Mock _report_player_event
    report_player_event_mock = MagicMock(return_value=[{"matchhandelseid": 123}])

    # Patch the necessary functions
    with patch(
        "fogis_reporter.FogisDataParser.calculate_scores", return_value=scores_mock
    ):
        with patch(
            "fogis_reporter._get_event_details_from_input",
            return_value=event_details_mock,
        ):
            with patch("fogis_reporter._report_player_event", report_player_event_mock):
                with patch("fogis_reporter._display_current_events_table"):
                    # Call the function
                    report_team_event(match_context_mock, 1)

                    # Check that _report_player_event was called with the correct parameters
                    report_player_event_mock.assert_called_once_with(
                        match_context_mock,
                        1,
                        {"name": "Goal", "goal": True},
                        [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}],
                        1,
                        0,
                    )

                    # Check that match_context.match_events_json was updated
                    assert match_context_mock.match_events_json == [
                        {"matchhandelseid": 123}
                    ]


# Test for reporting a substitution event
def test_report_team_event_substitution():
    """Test reporting a substitution event."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock FogisDataParser.calculate_scores
    scores_mock = MagicMock()
    scores_mock.regular_time.home = 1
    scores_mock.regular_time.away = 0

    # Mock _get_event_details_from_input
    event_details_mock = (
        1,
        {"name": "Substitution"},
        9,
        "Substitution",
        False,
        [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}],
    )

    # Mock _report_substitution_event
    report_substitution_event_mock = MagicMock(return_value=[{"matchhandelseid": 123}])

    # Patch the necessary functions
    with patch(
        "fogis_reporter.FogisDataParser.calculate_scores", return_value=scores_mock
    ):
        with patch(
            "fogis_reporter._get_event_details_from_input",
            return_value=event_details_mock,
        ):
            with patch(
                "fogis_reporter._report_substitution_event",
                report_substitution_event_mock,
            ):
                with patch("fogis_reporter._display_current_events_table"):
                    # Call the function
                    report_team_event(match_context_mock, 1)

                    # Check that _report_substitution_event was called with the correct parameters
                    report_substitution_event_mock.assert_called_once_with(
                        match_context_mock,
                        1,
                        [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}],
                        1,
                        0,
                    )

                    # Check that match_context.match_events_json was updated
                    assert match_context_mock.match_events_json == [
                        {"matchhandelseid": 123}
                    ]


# Test for reporting a team official action event
def test_report_team_event_official_action():
    """Test reporting a team official action event."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock FogisDataParser.calculate_scores
    scores_mock = MagicMock()
    scores_mock.regular_time.home = 1
    scores_mock.regular_time.away = 0

    # Mock _get_event_details_from_input
    event_details_mock = (
        1,
        {"name": "Team Official Action"},
        10,
        "Team Official Action",
        False,
        [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}],
    )

    # Mock _report_team_official_action_event
    report_team_official_action_event_mock = MagicMock(
        return_value=[{"matchhandelseid": 123}]
    )

    # Patch the necessary functions
    with patch(
        "fogis_reporter.FogisDataParser.calculate_scores", return_value=scores_mock
    ):
        with patch(
            "fogis_reporter._get_event_details_from_input",
            return_value=event_details_mock,
        ):
            with patch(
                "fogis_reporter._report_team_official_action_event",
                report_team_official_action_event_mock,
            ):
                with patch("fogis_reporter._display_current_events_table"):
                    # Call the function
                    report_team_event(match_context_mock, 1)

                    # Check that _report_team_official_action_event was called with the correct parameters
                    report_team_official_action_event_mock.assert_called_once_with(
                        match_context_mock
                    )

                    # Check that match_context.match_events_json was updated
                    assert match_context_mock.match_events_json == [
                        {"matchhandelseid": 123}
                    ]


# Test for reporting with invalid input
def test_report_team_event_invalid_input():
    """Test reporting with invalid input."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock FogisDataParser.calculate_scores
    scores_mock = MagicMock()
    scores_mock.regular_time.home = 1
    scores_mock.regular_time.away = 0

    # Mock _get_event_details_from_input to return None values (invalid input)
    event_details_mock = (None, None, None, None, None, None)

    # Patch the necessary functions
    with patch(
        "fogis_reporter.FogisDataParser.calculate_scores", return_value=scores_mock
    ):
        with patch(
            "fogis_reporter._get_event_details_from_input",
            return_value=event_details_mock,
        ):
            with patch(
                "fogis_reporter._report_player_event"
            ) as report_player_event_mock:
                with patch(
                    "fogis_reporter._report_substitution_event"
                ) as report_substitution_event_mock:
                    with patch(
                        "fogis_reporter._report_team_official_action_event"
                    ) as report_team_official_action_event_mock:
                        with patch(
                            "fogis_reporter._display_current_events_table"
                        ) as display_table_mock:
                            # Call the function
                            report_team_event(match_context_mock, 1)

                            # Check that none of the reporting functions were called
                            report_player_event_mock.assert_not_called()
                            report_substitution_event_mock.assert_not_called()
                            report_team_official_action_event_mock.assert_not_called()
                            display_table_mock.assert_not_called()


# Test for reporting with error in event reporting
def test_report_team_event_error():
    """Test reporting with error in event reporting."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock FogisDataParser.calculate_scores
    scores_mock = MagicMock()
    scores_mock.regular_time.home = 1
    scores_mock.regular_time.away = 0

    # Mock _get_event_details_from_input
    event_details_mock = (
        1,
        {"name": "Goal", "goal": True},
        6,
        "Goal",
        True,
        [{"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}],
    )

    # Mock _report_player_event to raise ValueError
    def report_player_event_mock_func(*args, **kwargs):
        raise ValueError("Test error")

    # Patch the necessary functions
    with patch(
        "fogis_reporter.FogisDataParser.calculate_scores", return_value=scores_mock
    ):
        with patch(
            "fogis_reporter._get_event_details_from_input",
            return_value=event_details_mock,
        ):
            with patch(
                "fogis_reporter._report_player_event",
                side_effect=report_player_event_mock_func,
            ):
                with patch(
                    "fogis_reporter._display_current_events_table"
                ) as display_table_mock:
                    # Call the function
                    report_team_event(match_context_mock, 1)

                    # Check that _display_current_events_table was not called
                    display_table_mock.assert_not_called()
