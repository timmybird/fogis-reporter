from unittest.mock import MagicMock

from api_utils import safe_fetch_json_list


def test_safe_fetch_json_list_with_dict():
    """Test that safe_fetch_json_list correctly handles a dictionary response."""
    # Create a mock API function that returns a dictionary
    mock_api_func = MagicMock(return_value={"id": 1, "name": "Test"})

    # Call the safe_fetch_json_list function with the mock
    result = safe_fetch_json_list(mock_api_func, "arg1", arg2="value")

    # Assert that the result is a list containing the dictionary
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["name"] == "Test"

    # Assert that the mock was called with the correct arguments
    mock_api_func.assert_called_once_with("arg1", arg2="value")


def test_safe_fetch_json_list_with_list():
    """Test that safe_fetch_json_list correctly handles a list response."""
    # Create a mock API function that returns a list of dictionaries
    mock_api_func = MagicMock(
        return_value=[{"id": 1, "name": "Test1"}, {"id": 2, "name": "Test2"}]
    )

    # Call the safe_fetch_json_list function with the mock
    result = safe_fetch_json_list(mock_api_func)

    # Assert that the result is the same list
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["name"] == "Test1"
    assert result[1]["id"] == 2
    assert result[1]["name"] == "Test2"

    # Assert that the mock was called
    mock_api_func.assert_called_once_with()


def test_safe_fetch_json_list_with_none():
    """Test that safe_fetch_json_list correctly handles a None response."""
    # Create a mock API function that returns None
    mock_api_func = MagicMock(return_value=None)

    # Call the safe_fetch_json_list function with the mock
    result = safe_fetch_json_list(mock_api_func)

    # Assert that the result is an empty list
    assert isinstance(result, list)
    assert len(result) == 0

    # Assert that the mock was called
    mock_api_func.assert_called_once_with()
