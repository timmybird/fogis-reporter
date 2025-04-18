import pytest
from unittest.mock import MagicMock, patch

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
        'matchhandelseid': 456,
        'matchhandelsetypid': 32,  # Period End
        'period': 2
    }

    # Set up the match_events_json to include the existing event
    match_context_mock.match_events_json = [existing_event]

    # Create a control event for Period End
    control_event = {
        'matchhandelseid': 0,  # New event
        'matchid': 123,
        'period': 2,
        'matchminut': 90,
        'sekund': 0,
        'matchhandelsetypid': 32,  # Period End
        'matchlagid': 0,
        'hemmamal': 1,
        'bortamal': 1
    }

    # Import the function we want to test
    from fogis_reporter import _add_control_event_with_implicit_events

    # Call the function with our mock context and control event
    # Configure the mock to return a successful response
    api_client_mock.report_match_event.return_value = [{'success': True}]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that the function tried to update the existing event
    # The first call to the mock should be with an event that has the existing event ID
    call_args = api_client_mock.report_match_event.call_args[0][0]
    assert call_args['matchhandelseid'] == 456
    assert call_args['matchhandelsetypid'] == 32
    assert call_args['period'] == 2

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
        'matchhandelseid': 0,  # New event
        'matchid': 123,
        'period': 2,
        'matchminut': 90,
        'sekund': 0,
        'matchhandelsetypid': 32,  # Period End
        'matchlagid': 0,
        'hemmamal': 1,
        'bortamal': 1
    }

    # Import the function we want to test
    from fogis_reporter import _add_control_event_with_implicit_events

    # Call the function with our mock context and control event
    # Configure the mock to return a successful response
    api_client_mock.report_match_event.return_value = [{'success': True}]

    # Call the function
    _add_control_event_with_implicit_events(control_event, match_context_mock)

    # Check that the function tried to create a new Period Start event first
    # and then a new Period End event
    assert api_client_mock.report_match_event.call_count >= 2

    # The first call should be for Period Start
    first_call_args = api_client_mock.report_match_event.call_args_list[0][0][0]
    assert first_call_args['matchhandelseid'] == 0  # New event
    assert first_call_args['matchhandelsetypid'] == 31  # Period Start
    assert first_call_args['period'] == 2

    # The second call should be for Period End
    second_call_args = api_client_mock.report_match_event.call_args_list[1][0][0]
    assert second_call_args['matchhandelseid'] == 0  # New event
    assert second_call_args['matchhandelsetypid'] == 32  # Period End
    assert second_call_args['period'] == 2
