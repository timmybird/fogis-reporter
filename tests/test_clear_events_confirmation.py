from unittest.mock import MagicMock, patch


# Test for the clear events confirmation functionality
def test_clear_events_confirmation():
    """Test that the clear events confirmation works correctly."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Import the function we want to test
    from fogis_reporter import report_match_events_menu

    # Call the function with our mock context
    with patch("fogis_reporter._handle_clear_events") as mock_handle_clear:
        with patch("fogis_reporter._display_current_events_table"):
            # Simulate the user selecting option 3, typing "clear" for confirmation, and then returning to the menu
            with patch("builtins.input", side_effect=["3", "clear", ""]):
                report_match_events_menu(match_context_mock)

            # Assert that _handle_clear_events was called
            mock_handle_clear.assert_called_once_with(match_context_mock)


# Test for the case when user cancels the clear operation
def test_clear_events_confirmation_cancel():
    """Test that the clear events confirmation can be cancelled."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Import the function we want to test
    from fogis_reporter import report_match_events_menu

    # Call the function with our mock context
    with patch("fogis_reporter._handle_clear_events") as mock_handle_clear:
        with patch("fogis_reporter._display_current_events_table"):
            # Simulate the user selecting option 3, typing "no" for confirmation, and then returning to the menu
            with patch("builtins.input", side_effect=["3", "no", ""]):
                report_match_events_menu(match_context_mock)

            # Assert that _handle_clear_events was NOT called
            mock_handle_clear.assert_not_called()
