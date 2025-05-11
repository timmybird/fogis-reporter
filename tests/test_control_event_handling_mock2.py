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


# Test for finding existing events
def test_find_existing_event():
    """Test that the _find_existing_event function correctly identifies existing events."""
    # Create mock objects
    match_context_mock = MagicMock()

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

    # Set up the match_events_json to include the existing events
    match_context_mock.match_events_json = [existing_period_start, existing_period_end]

    # Create a control event
    control_event = {
        "matchhandelseid": 0,
        "matchid": 123,
        "period": 2,
        "matchminut": 90,
        "sekund": 0,
        "matchhandelsetypid": 32,  # Period End
        "matchlagid": 0,
        "hemmamal": 1,
        "bortamal": 1,
    }

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock = MagicMock()
    api_client_mock.report_match_event.return_value = {"success": True}
    match_context_mock.api_client = api_client_mock

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that api_client.report_match_event was called with the correct event ID
    # for the existing Period End event
    for call in api_client_mock.report_match_event.call_args_list:
        args = call[0][0]
        if args["matchhandelsetypid"] == 32:  # Period End
            assert args["matchhandelseid"] == 457
            return

    # If we get here, the test failed
    assert False, "No call to update the existing Period End event was made"


# Test for creating new events when none exist
def test_create_new_events():
    """Test that new events are created when none exist."""
    # Create mock objects
    match_context_mock = MagicMock()

    # Set up the match_events_json to be empty (no existing events)
    match_context_mock.match_events_json = []

    # Set up other required properties
    match_context_mock.period_length = 45
    match_context_mock.match_id = 123

    # Create a control event
    control_event = {
        "matchhandelseid": 0,
        "matchid": 123,
        "period": 2,
        "matchminut": 90,
        "sekund": 0,
        "matchhandelsetypid": 32,  # Period End
        "matchlagid": 0,
        "hemmamal": 1,
        "bortamal": 1,
    }

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock = MagicMock()
    # Return a list of events as the response
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 123, "matchhandelsetypid": 31, "period": 2}
    ]
    match_context_mock.api_client = api_client_mock

    # Mock the match_events_json update after API call
    def side_effect(event_json):
        # Update match_context_mock.match_events_json with the new event
        match_context_mock.match_events_json.append(event_json)
        return [
            {
                "matchhandelseid": 123,
                "matchhandelsetypid": event_json["matchhandelsetypid"],
                "period": event_json["period"],
            }
        ]

    api_client_mock.report_match_event.side_effect = side_effect

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that api_client.report_match_event was called at least twice
    # (once for Period Start and once for Period End)
    assert api_client_mock.report_match_event.call_count >= 2

    # Check that all calls to api_client.report_match_event had matchhandelseid=0
    # (indicating new events)
    for call in api_client_mock.report_match_event.call_args_list:
        args = call[0][0]
        assert args["matchhandelseid"] == 0
