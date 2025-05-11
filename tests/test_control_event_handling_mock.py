import sys
from unittest.mock import MagicMock

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
from fogis_reporter import _add_control_event_with_implicit_events


# Test for updating existing Period End events
def test_update_existing_period_end():
    """Test that existing Period End events are updated instead of creating new ones."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45

    # Create a mock existing Period End event
    existing_event = {
        "matchhandelseid": 456,
        "matchhandelsetypid": 32,  # Period End
        "period": 2,
    }

    # Set up the match_events_json to include the existing event
    match_context_mock.match_events_json = [existing_event]

    # Create a control event for Period End
    control_event = {
        "matchhandelseid": 0,  # New event
        "matchid": 123,
        "period": 2,
        "matchminut": 90,
        "sekund": 0,
        "matchhandelsetypid": 32,  # Period End
        "matchlagid": 0,
        "hemmamal": 1,
        "bortamal": 1,
    }

    # Configure the API client mock
    api_client_mock.report_match_event.return_value = [{"success": True}]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that the function tried to update the existing event
    # The call to the mock should include an event that has the existing event ID
    for call in api_client_mock.report_match_event.call_args_list:
        args = call[0][0]
        if args["matchhandelsetypid"] == 32:  # Period End
            assert args["matchhandelseid"] == 456
            assert args["period"] == 2
            return

        # If we get here, the test failed
        assert False, "No call to update the existing Period End event was made"


# Test for creating new Period End events when none exist
def test_create_new_period_end():
    """Test that new Period End events are created when none exist."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45

    # Set up the match_events_json to be empty (no existing events)
    match_context_mock.match_events_json = []

    # Create a control event for Period End
    control_event = {
        "matchhandelseid": 0,  # New event
        "matchid": 123,
        "period": 2,
        "matchminut": 90,
        "sekund": 0,
        "matchhandelsetypid": 32,  # Period End
        "matchlagid": 0,
        "hemmamal": 1,
        "bortamal": 1,
    }

    # Configure the API client mock
    api_client_mock.report_match_event.return_value = [{"success": True}]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that the function tried to create a new Period End event
    # There should be at least one call with matchhandelseid=0 and matchhandelsetypid=32
    period_end_calls = [
        call
        for call in api_client_mock.report_match_event.call_args_list
        if call[0][0]["matchhandelsetypid"] == 32 and call[0][0]["matchhandelseid"] == 0
    ]

    assert (
        len(period_end_calls) > 0
    ), "No call to create a new Period End event was made"


# Test for updating existing Game End events
def test_update_existing_game_end():
    """Test that existing Game End events are updated instead of creating new ones."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45

    # Create mock existing events
    existing_period_start = {
        "matchhandelseid": 456,
        "matchhandelsetypid": 31,  # Period Start
        "period": 2,
    }
    existing_period_end = {
        "matchhandelseid": 457,
        "matchhandelsetypid": 32,  # Period End
        "period": 2,
    }
    existing_game_end = {
        "matchhandelseid": 458,
        "matchhandelsetypid": 23,  # Game End
        "period": 2,
    }

    # Set up the match_events_json to include the existing events
    match_context_mock.match_events_json = [
        existing_period_start,
        existing_period_end,
        existing_game_end,
    ]

    # Create a control event for Game End
    control_event = {
        "matchhandelseid": 0,  # New event
        "matchid": 123,
        "period": 2,
        "matchminut": 90,
        "sekund": 0,
        "matchhandelsetypid": 23,  # Game End
        "matchlagid": 0,
        "hemmamal": 1,
        "bortamal": 1,
    }

    # Configure the API client mock
    api_client_mock.report_match_event.return_value = [{"success": True}]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that the function tried to update the existing Game End event
    # The call to the mock should include an event that has the existing event ID
    for call in api_client_mock.report_match_event.call_args_list:
        args = call[0][0]
        if args["matchhandelsetypid"] == 23:  # Game End
            assert args["matchhandelseid"] == 458
            assert args["period"] == 2
            return

        # If we get here, the test failed
        assert False, "No call to update the existing Game End event was made"
