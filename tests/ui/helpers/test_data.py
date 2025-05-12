"""Test data for UI testing.

This module provides test data for UI testing.
"""

from typing import Dict, List, Optional


def create_test_match(
    match_id: int = 123,
    team1_name: str = "Home Team",
    team2_name: str = "Away Team",
    team1_id: int = 1,
    team2_id: int = 2,
    match_date: str = "2025-05-15",
    match_time: str = "19:00",
    status: str = "Upcoming",
) -> Dict:
    """Create a test match.

    Args:
        match_id: The match ID
        team1_name: The home team name
        team2_name: The away team name
        team1_id: The home team ID
        team2_id: The away team ID
        match_date: The match date
        match_time: The match time
        status: The match status

    Returns:
        A dictionary with match data
    """
    return {
        "matchid": match_id,
        "lag1namn": team1_name,
        "lag2namn": team2_name,
        "matchlag1id": team1_id,
        "matchlag2id": team2_id,
        "label": f"{team1_name} vs {team2_name}",
        "datum": match_date,
        "tid": match_time,
        "status": status,
        "antalhalvlekar": 2,
        "tidperhalvlek": 45,
        "antalforlangningsperioder": 0,
        "tidperforlangningsperiod": 0,
    }


def create_test_player(
    player_id: int,
    team_id: int,
    jersey_number: int,
    first_name: str = "Player",
    last_name: str = "Name",
    is_substitute: bool = False,
) -> Dict:
    """Create a test player.

    Args:
        player_id: The player ID
        team_id: The team ID
        jersey_number: The jersey number
        first_name: The player's first name
        last_name: The player's last name
        is_substitute: Whether the player is a substitute

    Returns:
        A dictionary with player data
    """
    return {
        "spelareid": player_id,
        "matchlagid": team_id,
        "trojnummer": jersey_number,
        "fornamn": first_name,
        "efternamn": last_name,
        "ersattare": is_substitute,
        "byte1": 0,
        "byte2": 0,
    }


def create_test_team_players(
    team_id: int,
    num_starters: int = 11,
    num_substitutes: int = 7,
    start_player_id: int = 100,
) -> List[Dict]:
    """Create test players for a team.

    Args:
        team_id: The team ID
        num_starters: The number of starting players
        num_substitutes: The number of substitute players
        start_player_id: The starting player ID

    Returns:
        A list of dictionaries with player data
    """
    players = []

    # Create starters
    for i in range(num_starters):
        player_id = start_player_id + i
        jersey_number = i + 1
        players.append(
            create_test_player(
                player_id=player_id,
                team_id=team_id,
                jersey_number=jersey_number,
                first_name="Starter",
                last_name=f"Player{jersey_number}",
                is_substitute=False,
            )
        )

    # Create substitutes
    for i in range(num_substitutes):
        player_id = start_player_id + num_starters + i
        jersey_number = num_starters + i + 1
        players.append(
            create_test_player(
                player_id=player_id,
                team_id=team_id,
                jersey_number=jersey_number,
                first_name="Sub",
                last_name=f"Player{jersey_number}",
                is_substitute=True,
            )
        )

    return players


def create_test_goal_event(
    match_id: int,
    team_id: int,
    player_id: int,
    minute: int,
    event_id: Optional[int] = None,
    goal_type: int = 6,  # Regular goal
) -> Dict:
    """Create a test goal event.

    Args:
        match_id: The match ID
        team_id: The team ID
        player_id: The player ID
        minute: The minute of the goal
        event_id: The event ID (optional)
        goal_type: The goal type (default: regular goal)

    Returns:
        A dictionary with goal event data
    """
    return {
        "matchhandelseid": event_id if event_id is not None else 1000,
        "matchid": match_id,
        "matchlagid": team_id,
        "spelareid": player_id,
        "matchhandelsetypid": goal_type,
        "minut": minute,
        "period": 1 if minute <= 45 else 2,
    }


def create_test_card_event(
    match_id: int,
    team_id: int,
    player_id: int,
    minute: int,
    event_id: Optional[int] = None,
    card_type: int = 7,  # Yellow card
) -> Dict:
    """Create a test card event.

    Args:
        match_id: The match ID
        team_id: The team ID
        player_id: The player ID
        minute: The minute of the card
        event_id: The event ID (optional)
        card_type: The card type (default: yellow card)

    Returns:
        A dictionary with card event data
    """
    return {
        "matchhandelseid": event_id if event_id is not None else 2000,
        "matchid": match_id,
        "matchlagid": team_id,
        "spelareid": player_id,
        "matchhandelsetypid": card_type,
        "minut": minute,
        "period": 1 if minute <= 45 else 2,
    }


def create_test_substitution_event(
    match_id: int,
    team_id: int,
    player_in_id: int,
    player_out_id: int,
    minute: int,
    event_id: Optional[int] = None,
) -> Dict:
    """Create a test substitution event.

    Args:
        match_id: The match ID
        team_id: The team ID
        player_in_id: The ID of the player coming on
        player_out_id: The ID of the player going off
        minute: The minute of the substitution
        event_id: The event ID (optional)

    Returns:
        A dictionary with substitution event data
    """
    return {
        "matchhandelseid": event_id if event_id is not None else 3000,
        "matchid": match_id,
        "matchlagid": team_id,
        "spelareid": player_in_id,
        "utbytt_spelareid": player_out_id,
        "matchhandelsetypid": 9,  # Substitution
        "minut": minute,
        "period": 1 if minute <= 45 else 2,
    }


def create_test_control_event(
    match_id: int,
    event_type: int,
    minute: int,
    period: int,
    event_id: Optional[int] = None,
) -> Dict:
    """Create a test control event.

    Args:
        match_id: The match ID
        event_type: The event type (e.g., period start, period end, game end)
        minute: The minute of the event
        period: The period of the event
        event_id: The event ID (optional)

    Returns:
        A dictionary with control event data
    """
    return {
        "matchhandelseid": event_id if event_id is not None else 4000,
        "matchid": match_id,
        "matchhandelsetypid": event_type,
        "minut": minute,
        "period": period,
    }


def create_test_match_result(
    match_id: int,
    home_score: int,
    away_score: int,
    halftime_home_score: int,
    halftime_away_score: int,
) -> Dict:
    """Create a test match result.

    Args:
        match_id: The match ID
        home_score: The home team score
        away_score: The away team score
        halftime_home_score: The home team halftime score
        halftime_away_score: The away team halftime score

    Returns:
        A dictionary with match result data
    """
    return {
        "matchid": match_id,
        "hemmamal": home_score,
        "bortamal": away_score,
        "halvtidHemmamal": halftime_home_score,
        "halvtidBortamal": halftime_away_score,
    }
