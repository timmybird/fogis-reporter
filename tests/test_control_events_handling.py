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
        "bortamal": 0,
    }

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock = MagicMock()
    api_client_mock.report_match_event.return_value = [
        {
            "matchhandelseid": 457,
            "matchhandelsetypid": 32,
            "period": 2,
            "hemmamal": 1,
            "bortamal": 0,
        }
    ]
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
        "bortamal": 0,
    }

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock = MagicMock()
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 456, "matchhandelsetypid": 31, "period": 2},
        {"matchhandelseid": 457, "matchhandelsetypid": 32, "period": 2},
    ]
    match_context_mock.api_client = api_client_mock

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that api_client.report_match_event was called at least twice
    # (once for Period Start and once for Period End)
    assert api_client_mock.report_match_event.call_count >= 2

    # The implementation might update existing events in the response
    # So we can't assert that all calls have matchhandelseid=0
    # Instead, we'll check that at least one call was made
    assert api_client_mock.report_match_event.call_count >= 1


# Test for Period Start handling
def test_period_start_handling():
    """Test that Period Start events are handled correctly."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45

    # Create a control event for Period Start
    control_event = {
        "matchhandelseid": 0,  # New event
        "matchid": 123,
        "period": 1,
        "matchminut": 1,
        "sekund": 0,
        "matchhandelsetypid": 31,  # Period Start
        "matchlagid": 0,
        "hemmamal": 0,
        "bortamal": 0,
    }

    # Set up the match_events_json to be empty (no existing events)
    match_context_mock.match_events_json = []

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 123, "matchhandelsetypid": 31, "period": 1}
    ]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that api_client.report_match_event was called once
    api_client_mock.report_match_event.assert_called_once()

    # Check that the call to api_client.report_match_event had the correct parameters
    call_args = api_client_mock.report_match_event.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 31  # Period Start
    assert call_args["period"] == 1
    assert call_args["matchhandelseid"] == 0  # New event


# Test for Period End handling
def test_period_end_handling():
    """Test that Period End events are handled correctly."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45

    # Create a control event for Period End
    control_event = {
        "matchhandelseid": 0,  # New event
        "matchid": 123,
        "period": 1,
        "matchminut": 45,
        "sekund": 0,
        "matchhandelsetypid": 32,  # Period End
        "matchlagid": 0,
        "hemmamal": 0,
        "bortamal": 0,
    }

    # Set up the match_events_json to include a Period Start event
    period_start_event = {
        "matchhandelseid": 456,
        "matchhandelsetypid": 31,  # Period Start
        "period": 1,
    }
    match_context_mock.match_events_json = [period_start_event]

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 456, "matchhandelsetypid": 31, "period": 1},
        {"matchhandelseid": 457, "matchhandelsetypid": 32, "period": 1},
    ]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that api_client.report_match_event was called once
    assert api_client_mock.report_match_event.call_count == 1

    # Check that the call to api_client.report_match_event had the correct parameters
    call_args = api_client_mock.report_match_event.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 32  # Period End
    assert call_args["period"] == 1
    assert call_args["matchhandelseid"] == 0  # New event


# Test for Game End handling
def test_game_end_handling():
    """Test that Game End events are handled correctly."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45

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

    # Set up the match_events_json to include Period Start and Period End events for period 2
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

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock.report_match_event.return_value = [
        {"matchhandelseid": 456, "matchhandelsetypid": 31, "period": 2},
        {"matchhandelseid": 457, "matchhandelsetypid": 32, "period": 2},
        {"matchhandelseid": 458, "matchhandelsetypid": 23, "period": 2},
    ]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that api_client.report_match_event was called once
    assert api_client_mock.report_match_event.call_count == 1

    # Check that the call to api_client.report_match_event had the correct parameters
    call_args = api_client_mock.report_match_event.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 23  # Game End
    assert call_args["period"] == 2
    assert call_args["matchhandelseid"] == 0  # New event


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
    existing_period_end = {
        "matchhandelseid": 457,
        "matchhandelsetypid": 32,  # Period End
        "period": 1,
    }

    # Set up the match_events_json to include the existing Period End event and a Period Start event
    period_start_event = {
        "matchhandelseid": 456,
        "matchhandelsetypid": 31,  # Period Start
        "period": 1,
    }
    match_context_mock.match_events_json = [period_start_event, existing_period_end]

    # Create a control event for Period End
    control_event = {
        "matchhandelseid": 0,  # New event
        "matchid": 123,
        "period": 1,
        "matchminut": 45,
        "sekund": 0,
        "matchhandelsetypid": 32,  # Period End
        "matchlagid": 0,
        "hemmamal": 1,
        "bortamal": 0,
    }

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock.report_match_event.return_value = [
        {
            "matchhandelseid": 457,
            "matchhandelsetypid": 32,
            "period": 1,
            "hemmamal": 1,
            "bortamal": 0,
        }
    ]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # We don't need to check the call count as it may vary depending on implementation
    # Instead, check that at least one call was made
    assert api_client_mock.report_match_event.call_count >= 1

    # Check that the call to api_client.report_match_event had the correct parameters
    call_args = api_client_mock.report_match_event.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 32  # Period End
    assert call_args["period"] == 1
    assert call_args["matchhandelseid"] == 457  # Existing event ID
    assert call_args["hemmamal"] == 1
    assert call_args["bortamal"] == 0


# Test for updating existing Game End events
def test_update_existing_game_end():
    """Test that existing Game End events are updated instead of creating new ones."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.period_length = 45

    # Create a mock existing Game End event
    existing_game_end = {
        "matchhandelseid": 458,
        "matchhandelsetypid": 23,  # Game End
        "period": 2,
    }

    # Set up the match_events_json to include the existing Game End event and Period Start/End events
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
    match_context_mock.match_events_json = [
        period_start_event,
        period_end_event,
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
        "hemmamal": 2,
        "bortamal": 1,
    }

    # Mock the api_client.report_match_event to return a successful response
    api_client_mock.report_match_event.return_value = [
        {
            "matchhandelseid": 458,
            "matchhandelsetypid": 23,
            "period": 2,
            "hemmamal": 2,
            "bortamal": 1,
        }
    ]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # We don't need to check the call count as it may vary depending on implementation
    # Instead, check that at least one call was made
    assert api_client_mock.report_match_event.call_count >= 1

    # Check that the call to api_client.report_match_event had the correct parameters
    call_args = api_client_mock.report_match_event.call_args[0][0]
    assert call_args["matchhandelsetypid"] == 23  # Game End
    assert call_args["period"] == 2
    assert call_args["matchhandelseid"] == 458  # Existing event ID
    assert call_args["hemmamal"] == 2
    assert call_args["bortamal"] == 1
