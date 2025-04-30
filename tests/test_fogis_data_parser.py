"""Tests for the fogis_data_parser module.

This module tests the FogisDataParser class and its methods.
"""

from unittest.mock import MagicMock

from fogis_data_parser import FogisDataParser
from match_context import MatchContext, Scores


class TestFogisDataParser:
    """Test class for FogisDataParser."""

    def test_get_player_id_by_team_jersey_valid(self):
        """Test getting player ID by jersey number with valid data."""
        # Arrange
        team_players_data = [
            {"spelareid": 100, "trojnummer": 1},
            {"spelareid": 200, "trojnummer": 2},
            {"spelareid": 300, "trojnummer": 3},
        ]

        # Act
        player_id = FogisDataParser.get_player_id_by_team_jersey(team_players_data, 2)

        # Assert
        assert player_id == 200

    def test_get_player_id_by_team_jersey_invalid(self):
        """Test getting player ID by jersey number with invalid jersey number."""
        # Arrange
        team_players_data = [
            {"spelareid": 100, "trojnummer": 1},
            {"spelareid": 200, "trojnummer": 2},
            {"spelareid": 300, "trojnummer": 3},
        ]

        # Act
        player_id = FogisDataParser.get_player_id_by_team_jersey(team_players_data, 99)

        # Assert
        assert player_id is None

    def test_get_player_id_by_team_jersey_empty_data(self):
        """Test getting player ID by jersey number with empty data."""
        # Arrange
        team_players_data = []

        # Act
        player_id = FogisDataParser.get_player_id_by_team_jersey(team_players_data, 1)

        # Assert
        assert player_id is None

    def test_get_player_id_by_team_jersey_missing_keys(self, capsys):
        """Test getting player ID by jersey number with missing keys in data."""
        # Arrange
        team_players_data = [
            {"name": "Player 1"},  # Missing spelareid and trojnummer
            {"spelareid": 200, "trojnummer": 2},
            {"trojnummer": 3},  # Missing spelareid
        ]

        # Act
        player_id = FogisDataParser.get_player_id_by_team_jersey(team_players_data, 2)

        # Assert
        assert player_id == 200

        # Check warning messages
        captured = capsys.readouterr()
        assert "Warning: Player data missing 'trojnummer' key" in captured.out
        # Note: The function stops checking after finding the first missing key

    def test_get_matchdeltagareid_by_team_jersey_valid(self):
        """Test getting matchdeltagareid by jersey number with valid data."""
        # Arrange
        team_players_data = [
            {"matchdeltagareid": 1000, "trojnummer": 1},
            {"matchdeltagareid": 2000, "trojnummer": 2},
            {"matchdeltagareid": 3000, "trojnummer": 3},
        ]

        # Act
        matchdeltagareid = FogisDataParser.get_matchdeltagareid_by_team_jersey(
            team_players_data, 2
        )

        # Assert
        assert matchdeltagareid == 2000

    def test_get_matchdeltagareid_by_team_jersey_invalid(self):
        """Test getting matchdeltagareid by jersey number with invalid jersey number."""
        # Arrange
        team_players_data = [
            {"matchdeltagareid": 1000, "trojnummer": 1},
            {"matchdeltagareid": 2000, "trojnummer": 2},
            {"matchdeltagareid": 3000, "trojnummer": 3},
        ]

        # Act
        matchdeltagareid = FogisDataParser.get_matchdeltagareid_by_team_jersey(
            team_players_data, 99
        )

        # Assert
        assert matchdeltagareid is None

    def test_get_matchdeltagareid_by_team_jersey_empty_data(self):
        """Test getting matchdeltagareid by jersey number with empty data."""
        # Arrange
        team_players_data = []

        # Act
        matchdeltagareid = FogisDataParser.get_matchdeltagareid_by_team_jersey(
            team_players_data, 1
        )

        # Assert
        assert matchdeltagareid is None

    def test_get_matchdeltagareid_by_team_jersey_missing_keys(self, capsys):
        """Test getting matchdeltagareid by jersey number with missing keys in data."""
        # Arrange
        team_players_data = [
            {"name": "Player 1"},  # Missing matchdeltagareid and trojnummer
            {"matchdeltagareid": 2000, "trojnummer": 2},
            {"trojnummer": 3},  # Missing matchdeltagareid
        ]

        # Act
        matchdeltagareid = FogisDataParser.get_matchdeltagareid_by_team_jersey(
            team_players_data, 2
        )

        # Assert
        assert matchdeltagareid == 2000

        # Check warning messages
        captured = capsys.readouterr()
        assert "Warning: Player data missing 'trojnummer' key" in captured.out
        # Note: The function stops checking after finding the first missing key

    def test_calculate_scores_empty_events(self, capsys):
        """Test calculating scores with empty events."""
        # Arrange
        match_context = MagicMock(spec=MatchContext)
        match_context.match_events_json = []
        match_context.team1_id = 1
        match_context.team2_id = 2

        # Act
        scores = FogisDataParser.calculate_scores(match_context)

        # Assert
        assert isinstance(scores, Scores)
        assert scores.regular_time.home == 0
        assert scores.regular_time.away == 0
        assert scores.halftime.home == 0
        assert scores.halftime.away == 0

        # Check messages
        captured = capsys.readouterr()
        assert "No events found" in captured.out

    def test_calculate_scores_missing_team_ids(self, capsys):
        """Test calculating scores with missing team IDs."""
        # Arrange
        match_context = MagicMock(spec=MatchContext)
        match_context.match_events_json = [
            {"matchhandelsetypid": 6, "matchlagid": 1, "period": 1}
        ]
        match_context.team1_id = None
        match_context.team2_id = 2

        # Act
        scores = FogisDataParser.calculate_scores(match_context)

        # Assert
        assert isinstance(scores, Scores)
        assert scores.regular_time.home == 0
        assert scores.regular_time.away == 0
        assert scores.halftime.home == 0
        assert scores.halftime.away == 0

        # Check messages
        captured = capsys.readouterr()
        assert "Missing team ID" in captured.out

    def test_calculate_scores_with_goals(self):
        """Test calculating scores with goal events."""
        # Arrange
        match_context = MagicMock(spec=MatchContext)
        match_context.match_events_json = [
            # Team 1 goals
            {
                "matchhandelsetypid": 6,
                "matchlagid": 1,
                "period": 1,
            },  # Regular goal in first half
            {
                "matchhandelsetypid": 39,
                "matchlagid": 1,
                "period": 2,
            },  # Goal in second half
            # Team 2 goals
            {
                "matchhandelsetypid": 28,
                "matchlagid": 2,
                "period": 1,
            },  # Goal in first half
            {
                "matchhandelsetypid": 29,
                "matchlagid": 2,
                "period": 1,
            },  # Goal in first half
            {
                "matchhandelsetypid": 15,
                "matchlagid": 2,
                "period": 2,
            },  # Goal in second half
        ]
        match_context.team1_id = 1
        match_context.team2_id = 2

        # Act
        scores = FogisDataParser.calculate_scores(match_context)

        # Assert
        assert isinstance(scores, Scores)
        assert scores.regular_time.home == 2  # Team 1 total goals
        assert scores.regular_time.away == 3  # Team 2 total goals
        assert scores.halftime.home == 1  # Team 1 first half goals
        assert scores.halftime.away == 2  # Team 2 first half goals

    def test_calculate_scores_with_non_goal_events(self):
        """Test calculating scores with non-goal events."""
        # Arrange
        match_context = MagicMock(spec=MatchContext)
        match_context.match_events_json = [
            # Team 1 goals
            {
                "matchhandelsetypid": 6,
                "matchlagid": 1,
                "period": 1,
            },  # Regular goal in first half
            # Team 1 non-goal events
            {
                "matchhandelsetypid": 7,
                "matchlagid": 1,
                "period": 1,
            },  # Yellow card (not a goal)
            {
                "matchhandelsetypid": 9,
                "matchlagid": 1,
                "period": 2,
            },  # Substitution (not a goal)
            # Team 2 goals
            {
                "matchhandelsetypid": 28,
                "matchlagid": 2,
                "period": 2,
            },  # Goal in second half
            # Team 2 non-goal events
            {
                "matchhandelsetypid": 8,
                "matchlagid": 2,
                "period": 1,
            },  # Red card (not a goal)
        ]
        match_context.team1_id = 1
        match_context.team2_id = 2

        # Act
        scores = FogisDataParser.calculate_scores(match_context)

        # Assert
        assert isinstance(scores, Scores)
        assert scores.regular_time.home == 1  # Team 1 total goals
        assert scores.regular_time.away == 1  # Team 2 total goals
        assert scores.halftime.home == 1  # Team 1 first half goals
        assert scores.halftime.away == 0  # Team 2 first half goals
