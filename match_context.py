from dataclasses import dataclass, field
from fogis_api_client.fogis_api_client import FogisApiClient


@dataclass
class Score:
    """Represents a single scoreline (e.g., regular time, halftime) for a match."""
    home: int = 0  # Score for the home team
    away: int = 0  # Score for the away team


@dataclass
class Scores:
    """Represents all scores for a match, including regular time, halftime, extra time, and penalties."""
    regular_time: Score = field(default_factory=Score)  # Regular time score
    halftime: Score = field(default_factory=Score)  # Halftime score
    extra_time: Score = field(default_factory=lambda: Score(home=-1, away=-1) )  # Extra time score
    penalties: Score = field(default_factory=lambda: Score(home=-1, away=-1) )  # Penalty shootout score


@dataclass
class MatchContext:
    """
    Context object to hold all relevant data for a match.
    Includes API client, match details, player lists, and match events.
    Provides dynamic properties to access calculated scores.
    """
    api_client: FogisApiClient
    selected_match: dict
    team1_players_json: list[dict]
    team2_players_json: list[dict]
    match_events_json: list[dict]
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
        return FogisDataParser.calculate_scores(self)
