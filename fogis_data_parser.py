"""Parser for FOGIS API data with methods to extract and process match information."""

from typing import Any, Dict, List, Optional

from match_context import MatchContext, Score, Scores


class FogisDataParser:
    """Parses and processes data from the FOGIS API.

    Provides methods to extract player IDs, calculate scores, and process match events.
    """

    @staticmethod
    def get_player_id_by_team_jersey(
            team_players_data: List[Dict[str, Any]], jersey_number: int
    ) -> Optional[int]:
        """Finds the spelareid of a player by team and jersey number from JSON data."""
        if team_players_data:
            for player in team_players_data:
                if player['trojnummer'] == int(jersey_number):
                    return int(player['spelareid'])
        return None

    @staticmethod
    def get_matchdeltagareid_by_team_jersey(
            team_players_data: List[Dict[str, Any]], jersey_number: int
    ) -> Optional[int]:
        """Find matchdeltagareid by team and jersey number from JSON data."""
        # Shorter docstring to avoid line length issues
        if team_players_data:
            for player in team_players_data:
                if player['trojnummer'] == int(jersey_number):
                    return int(player['matchdeltagareid'])
        return None

    @staticmethod
    def calculate_scores(match_context: MatchContext) -> Scores:
        """Calculate scores for a match.

        Uses match events JSON data inside MatchContext to calculate scores.
        """
        # Fixed docstring format

        match_events_json = match_context.match_events_json
        team1_id = match_context.team1_id
        team2_id = match_context.team2_id
        if not match_events_json or len(match_events_json) == 0:
            print("No events found")
            return Scores()

        # Handle case where team IDs are missing
        if team1_id is None or team2_id is None:
            print("Missing team ID")
            return Scores()

        # Calculate team and halftime scores from match events JSON data
        team1_score = 0
        team2_score = 0
        halftime_score_team1 = 0
        halftime_score_team2 = 0

        for event in match_events_json:
            # Goal event types (regular, penalty, own goal, etc.)
            if event['matchhandelsetypid'] in [6, 39, 28, 29, 15, 14]:
                if event['matchlagid'] == team1_id:
                    team1_score += 1
                    if event['period'] == 1:
                        halftime_score_team1 += 1
                elif event['matchlagid'] == team2_id:
                    team2_score += 1
                    if event['period'] == 1:
                        halftime_score_team2 += 1
        return Scores(regular_time=Score(team1_score, team2_score),
                      halftime=Score(halftime_score_team1, halftime_score_team2))
