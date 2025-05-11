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
from fogis_reporter import report_match_events_menu


# Test for the clear events confirmation functionality
def test_clear_events_confirmation():
    """Test that the clear events confirmation works correctly."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock the input function to simulate user selecting option 3, typing "clear", and then exiting
    with patch("builtins.input", side_effect=["3", "clear", ""]):
        # Mock the _handle_clear_events function
        with patch(
            "fogis_reporter._handle_clear_events", return_value={}
        ) as mock_handle_clear:
            # Mock the _display_current_events_table function
            with patch("fogis_reporter._display_current_events_table") as mock_display:
                # Call the function with our mock context
                report_match_events_menu(match_context_mock)

                # Assert that _handle_clear_events was called
                mock_handle_clear.assert_called_once_with(match_context_mock)
                # Assert that _display_current_events_table was called
                mock_display.assert_called_once()


# Test for the case when user cancels the clear operation
def test_clear_events_confirmation_cancel():
    """Test that the clear events confirmation can be cancelled."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock the input function to simulate user selecting option 3, typing something other than "clear", and then exiting
    with patch("builtins.input", side_effect=["3", "no", ""]):
        # Mock the _handle_clear_events function
        with patch("fogis_reporter._handle_clear_events") as mock_handle_clear:
            # Mock the _display_current_events_table function
            with patch("fogis_reporter._display_current_events_table") as mock_display:
                # Call the function with our mock context
                report_match_events_menu(match_context_mock)

                # Assert that _handle_clear_events was NOT called
                mock_handle_clear.assert_not_called()
                # Assert that _display_current_events_table was NOT called
                mock_display.assert_not_called()
