"""Test Mark Reporting Finished module.

This module provides functionality for test mark reporting finished.
"""

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
from fogis_reporter import _mark_reporting_finished_with_error_handling  # noqa: E402


# Test for marking reporting as finished with user confirmation
def test_mark_reporting_finished_with_confirmation():
    """Test marking reporting as finished with user confirmation."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Add the mark_reporting_finished method to the API client
    api_client_mock.mark_reporting_finished = MagicMock(
        return_value={"status": "success"}
    )

    # Mock the input function to simulate user confirming
    with patch("builtins.input", return_value="yes"):
        # Call the function
        _mark_reporting_finished_with_error_handling(match_context_mock)

        # Check that mark_reporting_finished was called with the correct parameters
        api_client_mock.mark_reporting_finished.assert_called_once_with(123)


# Test for marking reporting as finished with matchrapportgodkandavdomare property
def test_mark_reporting_finished_with_referee_confirmation():
    """Test marking reporting as finished with matchrapportgodkandavdomare property."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Add the mark_reporting_finished method to the API client with matchrapportgodkandavdomare property
    api_client_mock.mark_reporting_finished = MagicMock(
        return_value={"matchrapportgodkandavdomare": True, "status": "success"}
    )

    # Mock the input function to simulate user confirming and print to check output
    with patch("builtins.input", return_value="yes"), patch(
        "builtins.print"
    ) as mock_print:
        # Call the function
        _mark_reporting_finished_with_error_handling(match_context_mock)

        # Check that mark_reporting_finished was called with the correct parameters
        api_client_mock.mark_reporting_finished.assert_called_once_with(123)

        # Check that the referee confirmation status was printed
        mock_print.assert_any_call("\nMatch Reporting Marked as Finished Successfully!")
        mock_print.assert_any_call("Referee confirmation status: True")


# Test for marking reporting as finished without matchrapportgodkandavdomare property
def test_mark_reporting_finished_without_referee_confirmation():
    """Test marking reporting as finished without matchrapportgodkandavdomare property."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Add the mark_reporting_finished method to the API client without matchrapportgodkandavdomare property
    api_client_mock.mark_reporting_finished = MagicMock(
        return_value={"status": "success"}
    )

    # Mock the input function to simulate user confirming and print to check output
    with patch("builtins.input", return_value="yes"), patch(
        "builtins.print"
    ) as mock_print:
        # Call the function
        _mark_reporting_finished_with_error_handling(match_context_mock)

        # Check that mark_reporting_finished was called with the correct parameters
        api_client_mock.mark_reporting_finished.assert_called_once_with(123)

        # Check that the appropriate message was printed
        mock_print.assert_any_call("\nMatch Reporting Marked as Finished Successfully!")
        mock_print.assert_any_call(
            "(No referee confirmation status available in the response)"
        )


# Test for marking reporting as finished with user cancellation
def test_mark_reporting_finished_with_cancellation():
    """Test marking reporting as finished with user cancellation."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Add the mark_reporting_finished method to the API client
    api_client_mock.mark_reporting_finished = MagicMock()

    # Mock the input function to simulate user cancelling
    with patch("builtins.input", return_value="no"):
        # Call the function
        _mark_reporting_finished_with_error_handling(match_context_mock)

        # Check that mark_reporting_finished was NOT called
        api_client_mock.mark_reporting_finished.assert_not_called()


# Test for marking reporting as finished with API error
def test_mark_reporting_finished_with_api_error():
    """Test marking reporting as finished with API error."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Add the mark_reporting_finished method to the API client
    api_client_mock.mark_reporting_finished = MagicMock(
        side_effect=Exception("API Error")
    )

    # Mock the input function to simulate user confirming
    with patch("builtins.input", return_value="yes"):
        # Call the function - should not raise an exception
        _mark_reporting_finished_with_error_handling(match_context_mock)

        # Check that mark_reporting_finished was called with the correct parameters
        api_client_mock.mark_reporting_finished.assert_called_once_with(123)


# Test for marking reporting as finished with invalid user input
def test_mark_reporting_finished_with_invalid_input():
    """Test marking reporting as finished with invalid user input."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Add the mark_reporting_finished method to the API client
    api_client_mock.mark_reporting_finished = MagicMock()

    # Mock the input function to simulate invalid input followed by cancellation
    with patch("builtins.input", side_effect=["invalid", "no"]):
        # Call the function
        _mark_reporting_finished_with_error_handling(match_context_mock)

        # Check that mark_reporting_finished was NOT called
        api_client_mock.mark_reporting_finished.assert_not_called()


# Test for marking reporting as finished with empty input (treated as invalid)
def test_mark_reporting_finished_with_empty_input():
    """Test marking reporting as finished with empty input (treated as invalid)."""
    # Create mock objects
    match_context_mock = MagicMock()
    api_client_mock = MagicMock()
    match_context_mock.api_client = api_client_mock
    match_context_mock.match_id = 123

    # Add the mark_reporting_finished method to the API client
    api_client_mock.mark_reporting_finished = MagicMock(
        return_value={"status": "success"}
    )

    # Mock the input function to simulate user pressing Enter (empty string) and print to check output
    with patch("builtins.input", return_value=""), patch(
        "builtins.print"
    ) as mock_print:
        # Call the function
        _mark_reporting_finished_with_error_handling(match_context_mock)

        # Check that mark_reporting_finished was NOT called
        api_client_mock.mark_reporting_finished.assert_not_called()

        # Check that the invalid input message was printed
        mock_print.assert_any_call("Invalid input. Please enter 'yes' or 'no'.")
