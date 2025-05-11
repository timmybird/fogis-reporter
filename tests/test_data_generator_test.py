"""Tests for the test data generator.

This module contains tests for the test data generator to ensure it
generates valid test data for the mock server.
"""


from tests.utils.test_data_generator import TestDataGenerator


class TestTestDataGenerator:
    """Tests for the TestDataGenerator class."""

    def test_create_match_with_goals(self):
        """Test creating a match with goals."""
        generator = TestDataGenerator()
        match_data = generator.create_match_with_goals(home_goals=2, away_goals=1)

        # Check that the match data contains the expected keys
        assert "match" in match_data
        assert "events" in match_data
        assert "home_team_players" in match_data
        assert "away_team_players" in match_data
        assert "match_result" in match_data

        # Check that the match has the correct score
        assert match_data["match"]["hemmamal"] == 2
        assert match_data["match"]["bortamal"] == 1

        # Check that the events contain the correct number of goals
        goal_events = [e for e in match_data["events"] if e["matchhandelsetypid"] == 6]
        assert len(goal_events) == 3  # 2 home goals + 1 away goal

        # Check that the match result contains the correct score
        full_time_result = [
            r for r in match_data["match_result"] if r["matchresultattypid"] == 1
        ][0]
        assert full_time_result["matchlag1mal"] == 2
        assert full_time_result["matchlag2mal"] == 1

    def test_create_match_with_cards(self):
        """Test creating a match with cards."""
        generator = TestDataGenerator()
        match_data = generator.create_match_with_cards(
            home_yellow_cards=1,
            home_red_cards=0,
            away_yellow_cards=2,
            away_red_cards=1,
        )

        # Check that the match data contains the expected keys
        assert "match" in match_data
        assert "events" in match_data
        assert "home_team_players" in match_data
        assert "away_team_players" in match_data

        # Check that the events contain the correct number of cards
        yellow_card_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 7
        ]
        red_card_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 8
        ]
        assert len(yellow_card_events) == 3  # 1 home yellow card + 2 away yellow cards
        assert len(red_card_events) == 1  # 0 home red cards + 1 away red card

    def test_create_match_with_substitutions(self):
        """Test creating a match with substitutions."""
        generator = TestDataGenerator()
        match_data = generator.create_match_with_substitutions(
            home_substitutions=3,
            away_substitutions=3,
        )

        # Check that the match data contains the expected keys
        assert "match" in match_data
        assert "events" in match_data
        assert "home_team_players" in match_data
        assert "away_team_players" in match_data

        # Check that the events contain the correct number of substitutions
        sub_out_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 16
        ]
        sub_in_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 17
        ]
        assert len(sub_out_events) == 6  # 3 home subs + 3 away subs
        assert len(sub_in_events) == 6  # 3 home subs + 3 away subs

        # Check that each sub in event is related to a sub out event
        for sub_in_event in sub_in_events:
            assert "relateradTillMatchhandelseID" in sub_in_event
            related_id = sub_in_event["relateradTillMatchhandelseID"]
            assert any(e["matchhandelseid"] == related_id for e in sub_out_events)

    def test_create_match_with_team_official_actions(self):
        """Test creating a match with team official actions."""
        generator = TestDataGenerator()
        match_data = generator.create_match_with_team_official_actions(
            home_warnings=1,
            home_dismissals=0,
            away_warnings=1,
            away_dismissals=1,
        )

        # Check that the match data contains the expected keys
        assert "match" in match_data
        assert "events" in match_data

        # Check that the events contain the correct number of team official actions
        warning_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 18
        ]
        dismissal_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 19
        ]
        assert len(warning_events) == 2  # 1 home warning + 1 away warning
        assert len(dismissal_events) == 1  # 0 home dismissals + 1 away dismissal

    def test_create_match_with_specific_result(self):
        """Test creating a match with a specific result."""
        generator = TestDataGenerator()
        match_data = generator.create_match_with_specific_result(
            home_score=3,
            away_score=2,
            halftime_home_score=1,
            halftime_away_score=1,
        )

        # Check that the match data contains the expected keys
        assert "match" in match_data
        assert "match_result" in match_data

        # Check that the match has the correct score
        assert match_data["match"]["hemmamal"] == 3
        assert match_data["match"]["bortamal"] == 2
        assert match_data["match"]["halvtidHemmamal"] == 1
        assert match_data["match"]["halvtidBortamal"] == 1

        # Check that the match result contains the correct score
        full_time_result = [
            r for r in match_data["match_result"] if r["matchresultattypid"] == 1
        ][0]
        half_time_result = [
            r for r in match_data["match_result"] if r["matchresultattypid"] == 2
        ][0]
        assert full_time_result["matchlag1mal"] == 3
        assert full_time_result["matchlag2mal"] == 2
        assert half_time_result["matchlag1mal"] == 1
        assert half_time_result["matchlag2mal"] == 1

    def test_create_complete_match_scenario(self):
        """Test creating a complete match scenario."""
        generator = TestDataGenerator()
        match_data = generator.create_complete_match_scenario(
            home_goals=2,
            away_goals=1,
            home_yellow_cards=1,
            home_red_cards=0,
            away_yellow_cards=2,
            away_red_cards=1,
            home_substitutions=3,
            away_substitutions=3,
            home_official_warnings=1,
            home_official_dismissals=0,
            away_official_warnings=1,
            away_official_dismissals=1,
        )

        # Check that the match data contains the expected keys
        assert "match" in match_data
        assert "events" in match_data
        assert "home_team_players" in match_data
        assert "away_team_players" in match_data
        assert "match_result" in match_data

        # Check that the events contain the correct number of events
        goal_events = [e for e in match_data["events"] if e["matchhandelsetypid"] == 6]
        yellow_card_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 7
        ]
        red_card_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 8
        ]
        sub_out_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 16
        ]
        sub_in_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 17
        ]
        warning_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 18
        ]
        dismissal_events = [
            e for e in match_data["events"] if e["matchhandelsetypid"] == 19
        ]

        assert len(goal_events) == 3  # 2 home goals + 1 away goal
        assert len(yellow_card_events) == 3  # 1 home yellow card + 2 away yellow cards
        assert len(red_card_events) == 1  # 0 home red cards + 1 away red card
        assert len(sub_out_events) == 6  # 3 home subs + 3 away subs
        assert len(sub_in_events) == 6  # 3 home subs + 3 away subs
        assert len(warning_events) == 2  # 1 home warning + 1 away warning
        assert len(dismissal_events) == 1  # 0 home dismissals + 1 away dismissal

        # Check that the events are sorted by minute
        minutes = [e["matchminut"] for e in match_data["events"]]
        assert minutes == sorted(minutes)
