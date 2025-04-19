"""
Utility functions for safely interacting with the API.
Ensures consistent return types regardless of what the API returns.
"""
from typing import Any, Callable, Dict, List, TypeVar, cast

T = TypeVar('T')  # Generic type for the return value of the API function

def safe_fetch_json_list(api_func: Callable[..., Any], *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
    """
    Safely fetch JSON data and ensure it's a list of dictionaries.

    Args:
        api_func: The API function to call
        *args: Positional arguments to pass to the API function
        **kwargs: Keyword arguments to pass to the API function

    Returns:
        List[Dict[str, Any]]: A list of dictionaries. May be empty if the API returns None.

    Note:
        This function ensures the return value is always a list, even if the API
        returns a single dictionary or None.

        Special handling for team_players_json which returns a dict with 'spelare' key.
    """
    result = api_func(*args, **kwargs)

    if result is None:
        return []

    if isinstance(result, dict):
        # Special handling for team_players_json which returns a dict with 'spelare' key
        if 'spelare' in result and isinstance(result['spelare'], list):
            return cast(List[Dict[str, Any]], result['spelare'])
        return [result]

    # Assume it's already a list
    return cast(List[Dict[str, Any]], result)
