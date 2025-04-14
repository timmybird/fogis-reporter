from match_context import MatchContext, Scores, Score


class FogisDataParser:
    """
    Parses and processes data from the FOGIS API.
    ...
    """

    @staticmethod
    def get_player_id_by_team_jersey(team_players_data, jersey_number):
        """Finds the spelareid of a player by team and jersey number from JSON data."""
        if team_players_data:
            for player in team_players_data:
                if player['trojnummer'] == int(jersey_number):
                    return player['spelareid']
        return None

    @staticmethod
    def get_matchdeltagareid_by_team_jersey(team_players_data, jersey_number):
        """Finds the matchdeltagareid of a player by team and jersey number from JSON data."""
        if team_players_data:
            for player in team_players_data:
                if player['trojnummer'] == int(jersey_number):
                    return player['matchdeltagareid']
        return None

    @staticmethod
    def calculate_scores(match_context: MatchContext) -> Scores:
        """Calculates scores for a match from match events JSON data inside MatchContext."""

        match_events_json = match_context.match_events_json
        team1_id = match_context.team1_id
        team2_id = match_context.team2_id
        if not match_events_json or len(match_events_json) == 0:
            print("No events found")

        if team1_id is None:
            print("No team1_id found")

        if team2_id is None:
            print("No team2_id found")

        """Calculates team and halftime scores from match events JSON data."""
        team1_score = 0
        team2_score = 0
        halftime_score_team1 = 0
        halftime_score_team2 = 0

        for event in match_events_json:
            if event['matchhandelsetypid'] in [6, 39, 28, 29, 15, 14]:  # Goal event types
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
