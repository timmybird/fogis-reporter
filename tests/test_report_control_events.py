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
from fogis_reporter import _report_control_event_interactively


# Test for reporting Period Start (31) events
def test_report_period_start():
    """Test reporting a Period Start event."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"
    match_context_mock.match_events_json = []

    # Mock the API response
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 123, "matchhandelsetypid": 31, "period": 1}
    ]

    # Mock _display_current_events_table
    with patch("fogis_reporter._display_current_events_table"):
        # Mock input for period and minute
        with patch("builtins.input", side_effect=["1", "1"]):
            # Call the function
            # We need to mock EVENT_TYPES to test Period Start
            with patch("fogis_reporter.EVENT_TYPES", {31: {"name": "Period Start"}}):
                # We need to patch _add_control_event_with_implicit_events to avoid API calls
                with patch(
                    "fogis_reporter._add_control_event_with_implicit_events"
                ) as mock_add_control:
                    _report_control_event_interactively(
                        match_context_mock, "3"
                    )  # 3 = Period Start (custom)

    # Check that _add_control_event_with_implicit_events was called
    mock_add_control.assert_called_once()

    # Check that the call had the correct parameters
    call_args = mock_add_control.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 31  # Period Start
    assert call_args["period"] == 1
    assert call_args["matchminut"] == 1


# Test for reporting Period End (32) events
def test_report_period_end():
    """Test reporting a Period End event."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Create a mock existing Period Start event
    period_start_event = {
        "matchhandelseid": 456,
        "matchhandelsetypid": 31,  # Period Start
        "period": 1,
    }
    match_context_mock.match_events_json = [period_start_event]

    # Mock the API response
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 456, "matchhandelsetypid": 31, "period": 1},
        {"matchhandelseid": 457, "matchhandelsetypid": 32, "period": 1},
    ]

    # Mock _display_current_events_table
    with patch("fogis_reporter._display_current_events_table"):
        # Mock input for period and minute
        with patch("builtins.input", side_effect=["1", "45"]):
            # Call the function
            # We need to patch _add_control_event_with_implicit_events to avoid API calls
            with patch(
                "fogis_reporter._add_control_event_with_implicit_events"
            ) as mock_add_control:
                _report_control_event_interactively(
                    match_context_mock, "1"
                )  # 1 = Period End

    # Check that _add_control_event_with_implicit_events was called
    mock_add_control.assert_called_once()

    # Check that the call had the correct parameters
    call_args = mock_add_control.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 32  # Period End
    assert call_args["period"] == 1
    assert call_args["matchminut"] == 45


# Test for reporting Game End (23) events
def test_report_game_end():
    """Test reporting a Game End event."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Create mock existing Period Start and Period End events
    period_start_event = {
        "matchhandelseid": 456,
        "matchhandelsetypid": 31,  # Period Start
        "period": 2,
    }
    period_end_event = {
        "matchhandelseid": 457,
        "matchhandelsetypid": 32,  # Period End
        "period": 2,
    }
    match_context_mock.match_events_json = [period_start_event, period_end_event]

    # Mock the API response
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 456, "matchhandelsetypid": 31, "period": 2},
        {"matchhandelseid": 457, "matchhandelsetypid": 32, "period": 2},
        {"matchhandelseid": 458, "matchhandelsetypid": 23, "period": 2},
    ]

    # Mock _display_current_events_table
    with patch("fogis_reporter._display_current_events_table"):
        # Mock input for period and minute
        with patch("builtins.input", side_effect=["2", "90"]):
            # Call the function
            # We need to patch _add_control_event_with_implicit_events to avoid API calls
            with patch(
                "fogis_reporter._add_control_event_with_implicit_events"
            ) as mock_add_control:
                _report_control_event_interactively(
                    match_context_mock, "2"
                )  # 2 = Game End

    # Check that _add_control_event_with_implicit_events was called
    mock_add_control.assert_called_once()

    # Check that the call had the correct parameters
    call_args = mock_add_control.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 23  # Game End
    assert call_args["period"] == 2
    assert call_args["matchminut"] == 90
