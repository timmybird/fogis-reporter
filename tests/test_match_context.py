"""Tests for the match_context module.

This module tests the MatchContext, Score, and Scores classes.
"""

from unittest.mock import MagicMock, patch

import pytest

from match_context import MatchContext, Score, Scores


class TestScore:
    """Test class for Score."""

    def test_score_initialization_default(self):
        """Test Score initialization with default values."""
        # Act
        score = Score()

        # Assert
        assert score.home == 0
        assert score.away == 0

    def test_score_initialization_custom(self):
        """Test Score initialization with custom values."""
        # Act
        score = Score(home=2, away=1)

        # Assert
        assert score.home == 2
        assert score.away == 1


class TestScores:
    """Test class for Scores."""

    def test_scores_initialization_default(self):
        """Test Scores initialization with default values."""
        # Act
        scores = Scores()

        # Assert
        assert scores.regular_time.home == 0
        assert scores.regular_time.away == 0
        assert scores.halftime.home == 0
        assert scores.halftime.away == 0
        assert scores.extra_time.home == -1  # Default for extra time
        assert scores.extra_time.away == -1  # Default for extra time
        assert scores.penalties.home == -1  # Default for penalties
        assert scores.penalties.away == -1  # Default for penalties

    def test_scores_initialization_custom(self):
        """Test Scores initialization with custom values."""
        # Arrange
        regular_time = Score(home=2, away=1)
        halftime = Score(home=1, away=0)
        extra_time = Score(home=3, away=2)
        penalties = Score(home=5, away=4)

        # Act
        scores = Scores(
            regular_time=regular_time,
            halftime=halftime,
            extra_time=extra_time,
            penalties=penalties,
        )

        # Assert
        assert scores.regular_time.home == 2
        assert scores.regular_time.away == 1
        assert scores.halftime.home == 1
        assert scores.halftime.away == 0
        assert scores.extra_time.home == 3
        assert scores.extra_time.away == 2
        assert scores.penalties.home == 5
        assert scores.penalties.away == 4


class TestMatchContext:
    """Test class for MatchContext."""

    @pytest.fixture
    def api_client_mock(self):
        """Fixture to create a mock API client."""
        return MagicMock()

    @pytest.fixture
    def match_context(self, api_client_mock):
        """Fixture to create a MatchContext object for testing."""
        selected_match_data = {
            "matchid": 123,
            "lag1namn": "Team 1",
            "lag2namn": "Team 2",
            "matchlag1id": 1,
            "matchlag2id": 2,
            "label": "Test Match",
            "antalhalvlekar": 2,
            "tidperhalvlek": 45,
            "antalforlangningsperioder": 0,
            "tidperforlangningsperiod": 0,
        }
        team1_players_data = [
            {"spelareid": 100, "trojnummer": 1, "matchdeltagareid": 1000}
        ]
        team2_players_data = [
            {"spelareid": 200, "trojnummer": 2, "matchdeltagareid": 2000}
        ]
        match_events_data = []

        return MatchContext(
            api_client=api_client_mock,
            selected_match=selected_match_data,
            team1_players_json=team1_players_data,
            team2_players_json=team2_players_data,
            match_events_json=match_events_data,
            num_periods=selected_match_data["antalhalvlekar"],
            period_length=selected_match_data["tidperhalvlek"],
            num_extra_periods=selected_match_data["antalforlangningsperioder"],
            extra_period_length=selected_match_data["tidperforlangningsperiod"],
            team1_name=selected_match_data["lag1namn"],
            team2_name=selected_match_data["lag2namn"],
            team1_id=selected_match_data["matchlag1id"],
            team2_id=selected_match_data["matchlag2id"],
            match_id=selected_match_data["matchid"],
        )

    def test_match_context_initialization(self, match_context, api_client_mock):
        """Test MatchContext initialization."""
        # Assert
        assert match_context.api_client == api_client_mock
        assert match_context.match_id == 123
        assert match_context.team1_name == "Team 1"
        assert match_context.team2_name == "Team 2"
        assert match_context.team1_id == 1
        assert match_context.team2_id == 2
        assert match_context.num_periods == 2
        assert match_context.period_length == 45
        assert match_context.num_extra_periods == 0
        assert match_context.extra_period_length == 0
        assert len(match_context.team1_players_json) == 1
        assert len(match_context.team2_players_json) == 1
        assert len(match_context.match_events_json) == 0

    def test_scores_property(self, match_context):
        """Test the scores property."""
        # Arrange
        mock_scores = Scores(
            regular_time=Score(home=2, away=1), halftime=Score(home=1, away=0)
        )

        # Mock the FogisDataParser.calculate_scores method
        with patch(
            "fogis_data_parser.FogisDataParser.calculate_scores",
            return_value=mock_scores,
        ):
            # Act
            scores = match_context.scores

            # Assert
            assert scores.regular_time.home == 2
            assert scores.regular_time.away == 1
            assert scores.halftime.home == 1
            assert scores.halftime.away == 0
