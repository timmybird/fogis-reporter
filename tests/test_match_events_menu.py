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


# Test for the match events menu - team 1 events
def test_match_events_menu_team1():
    """Test selecting team 1 events from the match events menu."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock the input function to simulate user selecting option 1 (Team 1 events) and then exiting
    with patch("builtins.input", side_effect=["1", ""]):
        # Mock the report_team_event function
        with patch("fogis_reporter.report_team_event") as mock_report_team:
            # Mock the _display_current_events_table function
            with patch("fogis_reporter._display_current_events_table"):
                # Call the function with our mock context
                report_match_events_menu(match_context_mock)

                # Assert that report_team_event was called with the correct parameters
                mock_report_team.assert_called_once_with(match_context_mock, 1)


# Test for the match events menu - team 2 events
def test_match_events_menu_team2():
    """Test selecting team 2 events from the match events menu."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock the input function to simulate user selecting option 2 (Team 2 events) and then exiting
    with patch("builtins.input", side_effect=["2", ""]):
        # Mock the report_team_event function
        with patch("fogis_reporter.report_team_event") as mock_report_team:
            # Mock the _display_current_events_table function
            with patch("fogis_reporter._display_current_events_table"):
                # Call the function with our mock context
                report_match_events_menu(match_context_mock)

                # Assert that report_team_event was called with the correct parameters
                mock_report_team.assert_called_once_with(match_context_mock, 2)


# Test for the match events menu - clear events with confirmation
def test_match_events_menu_clear_confirm():
    """Test clearing events with confirmation from the match events menu."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock the input function to simulate user selecting option 3 (Clear events),
    # typing "clear" to confirm, and then exiting
    with patch("builtins.input", side_effect=["3", "clear", ""]):
        # Mock the _handle_clear_events function
        with patch(
            "fogis_reporter._handle_clear_events", return_value={}
        ) as mock_handle_clear:
            # Mock the _display_current_events_table function
            with patch("fogis_reporter._display_current_events_table"):
                # Call the function with our mock context
                report_match_events_menu(match_context_mock)

                # Assert that _handle_clear_events was called
                mock_handle_clear.assert_called_once_with(match_context_mock)


# Test for the match events menu - clear events with cancellation
def test_match_events_menu_clear_cancel():
    """Test cancelling clear events from the match events menu."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock the input function to simulate user selecting option 3 (Clear events),
    # typing something other than "clear", and then exiting
    with patch("builtins.input", side_effect=["3", "no", ""]):
        # Mock the _handle_clear_events function
        with patch("fogis_reporter._handle_clear_events") as mock_handle_clear:
            # Mock the _display_current_events_table function
            with patch("fogis_reporter._display_current_events_table"):
                # Call the function with our mock context
                report_match_events_menu(match_context_mock)

                # Assert that _handle_clear_events was NOT called
                mock_handle_clear.assert_not_called()


# Test for the match events menu - control events
# Note: This test is commented out because the current menu doesn't have a control events option
# def test_match_events_menu_control_events():
#     """Test selecting control events from the match events menu."""
#     # Create mock objects
#     match_context_mock = MagicMock()
#     api_client_mock = MagicMock()
#     match_context_mock.api_client = api_client_mock
#     match_context_mock.match_id = 123
#     match_context_mock.team1_name = "Team 1"
#     match_context_mock.team2_name = "Team 2"
#
#     # Mock the input function to simulate user selecting option 4 (Control events) and then exiting
#     with patch('builtins.input', side_effect=['4', '']):
#         # Mock the report_control_events_menu function
#         with patch('fogis_reporter.report_control_events_menu') as mock_report_control:
#             # Mock the _display_current_events_table function
#             with patch('fogis_reporter._display_current_events_table'):
#                 # Call the function with our mock context
#                 report_match_events_menu(match_context_mock)
#
#                 # Assert that report_control_events_menu was called with the correct parameters
#                 mock_report_control.assert_called_once_with(match_context_mock)

# Test for the match events menu - staff events
# Note: This test is commented out because the current menu doesn't have a staff events option
# def test_match_events_menu_staff_events():
#     """Test selecting staff events from the match events menu."""
#     # Create mock objects
#     match_context_mock = MagicMock()
#     api_client_mock = MagicMock()
#     match_context_mock.api_client = api_client_mock
#     match_context_mock.match_id = 123
#     match_context_mock.team1_name = "Team 1"
#     match_context_mock.team2_name = "Team 2"
#
#     # Mock the input function to simulate user selecting option 5 (Staff events) and then exiting
#     with patch('builtins.input', side_effect=['5', '']):
#         # Mock the report_staff_events_menu function
#         with patch('fogis_reporter.report_staff_events_menu') as mock_report_staff:
#             # Mock the _display_current_events_table function
#             with patch('fogis_reporter._display_current_events_table'):
#                 # Call the function with our mock context
#                 report_match_events_menu(match_context_mock)
#
#                 # Assert that report_staff_events_menu was called with the correct parameters
#                 mock_report_staff.assert_called_once_with(match_context_mock)


# Test for the match events menu - invalid input
def test_match_events_menu_invalid_input():
    """Test entering invalid input in the match events menu."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123
    match_context_mock.team1_name = "Team 1"
    match_context_mock.team2_name = "Team 2"

    # Mock the input function to simulate user entering invalid input and then exiting
    with patch("builtins.input", side_effect=["invalid", ""]):
        # Mock various functions to ensure they are not called
        with patch("fogis_reporter.report_team_event") as mock_report_team:
            with patch("fogis_reporter._handle_clear_events") as mock_handle_clear:
                with patch(
                    "fogis_reporter.report_control_events_menu"
                ) as mock_report_control:
                    with patch(
                        "fogis_reporter.report_staff_events_menu"
                    ) as mock_report_staff:
                        # Mock the _display_current_events_table function
                        with patch("fogis_reporter._display_current_events_table"):
                            # Call the function with our mock context
                            report_match_events_menu(match_context_mock)

                            # Assert that none of the functions were called
                            mock_report_team.assert_not_called()
                            mock_handle_clear.assert_not_called()
                            mock_report_control.assert_not_called()
                            mock_report_staff.assert_not_called()
