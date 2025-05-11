"""Example tests using the mock server.

This module contains example tests that demonstrate how to use the mock server
and test data generator for testing the fogis-reporter application.
"""

# Check if the fogis-api-client package is available
import importlib.util

import pytest

spec = importlib.util.find_spec("fogis_api_client.fogis_api_client")
MOCK_SERVER_AVAILABLE = spec is not None


@pytest.mark.skipif(not MOCK_SERVER_AVAILABLE, reason="Mock server not available")
def test_fetch_matches(api_client):
    """Test fetching matches from the mock server."""
    # Fetch matches from the mock server
    matches = api_client.fetch_matches_list_json()

    # Verify we got a list of matches
    assert matches is not None
    assert isinstance(matches, list)
    assert len(matches) > 0


@pytest.mark.skipif(not MOCK_SERVER_AVAILABLE, reason="Mock server not available")
def test_fetch_match_details(api_client, match_with_goals):
    """Test fetching match details from the mock server."""
    # Fetch match details from the mock server
    match_id = match_with_goals["match"]["matchid"]
    match_details = api_client.fetch_match_details_json(match_id)

    # Verify we got the correct match details
    assert match_details is not None
    assert match_details["matchid"] == match_id
    assert match_details["hemmamal"] == 2
    assert match_details["bortamal"] == 1


@pytest.mark.skipif(not MOCK_SERVER_AVAILABLE, reason="Mock server not available")
def test_fetch_match_events(api_client, match_with_goals):
    """Test fetching match events from the mock server."""
    # Fetch match events from the mock server
    match_id = match_with_goals["match"]["matchid"]
    events = api_client.fetch_match_events_json(match_id)

    # Verify we got the correct match events
    assert events is not None
    assert isinstance(events, list)
    assert len(events) == 3  # 2 home goals + 1 away goal

    # Verify the events are goals
    assert all(event["matchhandelsetypid"] == 6 for event in events)


@pytest.mark.skipif(not MOCK_SERVER_AVAILABLE, reason="Mock server not available")
def test_report_goal(api_client, match_with_goals):
    """Test reporting a goal to the mock server."""
    # Fetch match details
    match_id = match_with_goals["match"]["matchid"]
    match_details = api_client.fetch_match_details_json(match_id)

    # Get team ID
    team_id = match_details["hemmalagid"]

    # Create a goal event
    goal_event = {
        "matchhandelseid": 0,  # 0 for new events
        "matchid": match_id,
        "matchhandelsetypid": 6,  # Regular goal
        "matchlagid": team_id,
        "trojnummer": 9,  # Jersey number
        "matchminut": 80,
        "period": 2,
        "hemmamal": 3,  # New score
        "bortamal": 1,
    }

    # Report the goal
    response = api_client.report_match_event(goal_event)

    # Verify the response
    assert response is not None

    # Fetch match events to verify the goal was recorded
    events = api_client.fetch_match_events_json(match_id)

    # Find our goal in the events
    goal_found = False
    for event in events:
        if (
            event["matchhandelsetypid"] == 6
            and event["matchlagid"] == team_id
            and event["matchminut"] == 80
        ):
            goal_found = True
            break

    assert goal_found


@pytest.mark.skipif(not MOCK_SERVER_AVAILABLE, reason="Mock server not available")
def test_report_card(api_client, match_with_goals):
    """Test reporting a card to the mock server."""
    # Fetch match details
    match_id = match_with_goals["match"]["matchid"]
    match_details = api_client.fetch_match_details_json(match_id)

    # Get team ID
    team_id = match_details["hemmalagid"]

    # Create a yellow card event
    card_event = {
        "matchhandelseid": 0,  # 0 for new events
        "matchid": match_id,
        "matchhandelsetypid": 7,  # Yellow card
        "matchlagid": team_id,
        "trojnummer": 5,  # Jersey number
        "matchminut": 75,
        "period": 2,
        "hemmamal": 2,
        "bortamal": 1,
    }

    # Report the card
    response = api_client.report_match_event(card_event)

    # Verify the response
    assert response is not None

    # Fetch match events to verify the card was recorded
    events = api_client.fetch_match_events_json(match_id)

    # Find our card in the events
    card_found = False
    for event in events:
        if (
            event["matchhandelsetypid"] == 7
            and event["matchlagid"] == team_id
            and event["matchminut"] == 75
        ):
            card_found = True
            break

    assert card_found


@pytest.mark.skipif(not MOCK_SERVER_AVAILABLE, reason="Mock server not available")
def test_report_match_result(api_client, match_with_goals):
    """Test reporting match results to the mock server."""
    # Fetch match details
    match_id = match_with_goals["match"]["matchid"]

    # Create result data
    result_data = {
        "matchresultatListaJSON": [
            {
                "matchid": match_id,
                "matchresultattypid": 1,  # Full time
                "matchlag1mal": 3,
                "matchlag2mal": 2,
                "wo": False,
                "ow": False,
                "ww": False,
            },
            {
                "matchid": match_id,
                "matchresultattypid": 2,  # Half-time
                "matchlag1mal": 1,
                "matchlag2mal": 1,
                "wo": False,
                "ow": False,
                "ww": False,
            },
        ]
    }

    # Report the result
    response = api_client.report_match_result(result_data)

    # Verify the response
    assert response is not None

    # Fetch match results to verify
    results = api_client.fetch_match_result_json(match_id)

    # Verify full-time result
    full_time_result = None
    half_time_result = None

    for result in results:
        if result["matchresultattypid"] == 1:  # Full time
            full_time_result = result
        elif result["matchresultattypid"] == 2:  # Half time
            half_time_result = result

    assert full_time_result is not None
    assert full_time_result["matchlag1mal"] == 3
    assert full_time_result["matchlag2mal"] == 2

    assert half_time_result is not None
    assert half_time_result["matchlag1mal"] == 1
    assert half_time_result["matchlag2mal"] == 1
