"""Data classes for storing match context and score information."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from fogis_api_client.fogis_api_client import FogisApiClient


@dataclass
class Score:
    """Represents a single scoreline (e.g., regular time, halftime) for a match."""
    home: int = 0  # Score for the home team
    away: int = 0  # Score for the away team


@dataclass
class Scores:
    """Represents all scores for a match.

    Includes regular time, halftime, extra time, and penalties.
    """
    regular_time: Score = field(default_factory=Score)  # Regular time score
    halftime: Score = field(default_factory=Score)  # Halftime score
    # Extra time score (default -1 means not played)
    extra_time: Score = field(default_factory=lambda: Score(home=-1, away=-1))
    # Penalty shootout score (default -1 means not played)
    penalties: Score = field(default_factory=lambda: Score(home=-1, away=-1))


@dataclass
class MatchContext:
    """Context object to hold all relevant data for a match.

    Includes API client, match details, player lists, and match events.
    Provides dynamic properties to access calculated scores.
    """
    api_client: FogisApiClient
    selected_match: dict
    team1_players_json: List[Dict[str, Any]]
    team2_players_json: List[Dict[str, Any]]
    match_events_json: List[Dict[str, Any]]
    num_periods: int
    period_length: int
    num_extra_periods: int
    extra_period_length: int
    team1_name: str
    team2_name: str
    team1_id: int
    team2_id: int
    match_id: int

    @property
    def scores(self) -> 'Scores':
        """Dynamically calculates and returns all scores for the match."""
        from fogis_data_parser import FogisDataParser
        # Use explicit cast to ensure correct return type
        from typing import cast
        return cast('Scores', FogisDataParser.calculate_scores(self))
