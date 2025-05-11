"""Tests for the match_event_table_formatter module.

This module tests the MatchEventTableFormatter class.
"""

from unittest.mock import patch

import pytest

from match_event_table_formatter import MatchEventTableFormatter


class TestMatchEventTableFormatter:
    """Test class for MatchEventTableFormatter."""

    @pytest.fixture
    def event_types(self):
        """Fixture to create event types dictionary."""
        return {
            6: {"name": "Regular Goal", "goal": True},
            7: {"name": "Yellow Card"},
            8: {"name": "Red Card (Denying Goal Opportunity)"},
            9: {"name": "Substitution"},
            15: {"name": "Header Goal", "goal": True},
            28: {"name": "Corner Goal", "goal": True},
            29: {"name": "Free Kick Goal", "goal": True},
            31: {"name": "Period Start", "control_event": True},
            32: {"name": "Period End", "control_event": True},
            39: {"name": "Penalty Goal", "goal": True},
        }

    @pytest.fixture
    def formatter(self, event_types):
        """Fixture to create a MatchEventTableFormatter instance."""
        return MatchEventTableFormatter(
            event_types=event_types,
            team1_name="Home Team",
            team2_name="Away Team",
            team1_id=1,
            team2_id=2,
        )

    def test_initialization(self, formatter, event_types):
        """Test MatchEventTableFormatter initialization."""
        # Assert
        assert formatter.event_types == event_types
        assert formatter.team1_name == "Home Team"
        assert formatter.team2_name == "Away Team"
        assert formatter.team1_id == 1
        assert formatter.team2_id == 2

        # Check event categories
        assert "Goals" in formatter.event_categories
        assert "Yellow Cards" in formatter.event_categories
        assert "Red Cards" in formatter.event_categories
        assert "Substitutions" in formatter.event_categories
        assert "Other Events" in formatter.event_categories

        # Check category icons
        assert "⚽️" in formatter.category_icons["Goals"]
        assert "🟨" in formatter.category_icons["Yellow Cards"]
        assert "🟥" in formatter.category_icons["Red Cards"]
        assert "🔄" in formatter.category_icons["Substitutions"]
        assert "ℹ️" in formatter.category_icons["Other Events"]

    def test_populate_other_events_category(self, event_types):
        """Test _populate_other_events_category method."""
        # Arrange
        # Add a custom event type that doesn't fit in any predefined category
        event_types[99] = {"name": "Custom Event"}

        # Act
        formatter = MatchEventTableFormatter(
            event_types=event_types,
            team1_name="Home Team",
            team2_name="Away Team",
            team1_id=1,
            team2_id=2,
        )

        # Assert
        assert "Custom Event" in formatter.event_categories["Other Events"]
        # Control events should not be included in Other Events
        assert "Period Start" not in formatter.event_categories["Other Events"]
        assert "Period End" not in formatter.event_categories["Other Events"]

    def test_format_structured_table_no_events(self, formatter):
        """Test format_structured_table with no events."""
        # Arrange
        match_events_json = []
        team1_players_json = []
        team2_players_json = []

        # Act
        result = formatter.format_structured_table(
            match_events_json, team1_players_json, team2_players_json, 0, 0, 0, 0
        )

        # Assert
        assert result == "No events reported yet."

    def test_format_structured_table_with_events(self, formatter):
        """Test format_structured_table with events."""
        # Arrange
        match_events_json = [
            # Team 1 goal
            {
                "matchhandelsetypid": 6,  # Regular Goal
                "matchlagid": 1,
                "period": 1,
                "matchminut": 10,
                "trojnummer": 9,
            },
            # Team 2 goal
            {
                "matchhandelsetypid": 15,  # Header Goal
                "matchlagid": 2,
                "period": 1,
                "matchminut": 25,
                "trojnummer": 10,
            },
            # Team 1 yellow card
            {
                "matchhandelsetypid": 7,  # Yellow Card
                "matchlagid": 1,
                "period": 1,
                "matchminut": 30,
                "trojnummer": 5,
            },
            # Team 2 substitution
            {
                "matchhandelsetypid": 9,  # Substitution
                "matchlagid": 2,
                "period": 2,
                "matchminut": 60,
                "trojnummer": 14,
                "trojnummer2": 10,
            },
        ]
        team1_players_json = [
            {"spelareid": 101, "trojnummer": 9, "matchdeltagareid": 1001},
            {"spelareid": 102, "trojnummer": 5, "matchdeltagareid": 1002},
        ]
        team2_players_json = [
            {"spelareid": 201, "trojnummer": 10, "matchdeltagareid": 2001},
            {"spelareid": 202, "trojnummer": 14, "matchdeltagareid": 2002},
        ]

        # Mock tabulate to return a predictable string
        with patch(
            "match_event_table_formatter.tabulate", return_value="Formatted Table"
        ) as mock_tabulate:
            # Act
            result = formatter.format_structured_table(
                match_events_json, team1_players_json, team2_players_json, 1, 1, 1, 0
            )

            # Assert
            assert result == "Formatted Table"
            # We can't easily check the exact table content due to the tabulate mock,
            # but we can verify that tabulate was called with the correct headers
            assert mock_tabulate.call_count == 1
            args, kwargs = mock_tabulate.call_args
            headers = kwargs.get("headers")
            assert "Event Type" in headers
            assert "**Home Team**" in headers
            assert "**Away Team**" in headers

    def test_format_structured_table_unknown_team(self, formatter):
        """Test format_structured_table with events from unknown team."""
        # Arrange
        match_events_json = [
            # Team 1 goal
            {
                "matchhandelsetypid": 6,  # Regular Goal
                "matchlagid": 1,
                "period": 1,
                "matchminut": 10,
                "trojnummer": 9,
            },
            # Unknown team event (should be skipped)
            {
                "matchhandelsetypid": 6,  # Regular Goal
                "matchlagid": 99,  # Unknown team ID
                "period": 1,
                "matchminut": 15,
                "trojnummer": 7,
            },
        ]
        team1_players_json = [
            {"spelareid": 101, "trojnummer": 9, "matchdeltagareid": 1001}
        ]
        team2_players_json = []

        # Mock tabulate to return a predictable string
        with patch(
            "match_event_table_formatter.tabulate", return_value="Formatted Table"
        ):
            # Act
            result = formatter.format_structured_table(
                match_events_json, team1_players_json, team2_players_json, 1, 0, 1, 0
            )

            # Assert
            assert result == "Formatted Table"
            # The unknown team event should be skipped

    def test_get_player_jersey_from_event(self, formatter):
        """Test _get_player_jersey_from_event method."""
        # Arrange
        event_with_jersey = {"trojnummer": 9}
        event_without_jersey = {}

        # Act
        jersey_with = formatter._get_player_jersey_from_event(
            event_with_jersey, 1, [], []
        )
        jersey_without = formatter._get_player_jersey_from_event(
            event_without_jersey, 1, [], []
        )

        # Assert
        assert jersey_with == "9"
        assert jersey_without == "N/A"

    def test_get_player2_jersey_from_event(self, formatter):
        """Test _get_player2_jersey_from_event method."""
        # Arrange
        event_with_jersey = {"trojnummer2": 10}
        event_without_jersey = {}

        # Act
        jersey_with = formatter._get_player2_jersey_from_event(
            event_with_jersey, 1, [], []
        )
        jersey_without = formatter._get_player2_jersey_from_event(
            event_without_jersey, 1, [], []
        )

        # Assert
        assert jersey_with == "10"
        assert jersey_without == "N/A"
