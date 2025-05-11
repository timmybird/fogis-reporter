"""Test data generator for the mock server.

This module provides a test data generator that works with the mock server
to create realistic test data for testing the fogis-reporter application.
"""

import random
from typing import Any, Dict, Optional

# Import the MockFogisServer and MockDataFactory from the fogis-api-client package
try:
    from fogis_api_client.cli.mock_server import MockFogisServer
    from integration_tests.sample_data_factory import MockDataFactory
except ImportError:
    # Fallback for when the imports aren't available (e.g., in CI environment)
    # We'll define mock classes to allow the module to be imported
    class MockFogisServer:
        """Mock class for MockFogisServer."""

        def __init__(self, *args, **kwargs):
            pass

    class MockDataFactory:
        """Mock class for MockDataFactory."""

        @staticmethod
        def generate_id():
            """Generate a random ID."""
            return random.randint(1000000, 9999999)

        @staticmethod
        def generate_match_details(*args, **kwargs):
            """Generate mock match details."""
            return {}

        @staticmethod
        def generate_team_players(*args, **kwargs):
            """Generate mock team players."""
            return {"spelare": []}

        @staticmethod
        def generate_match_events(*args, **kwargs):
            """Generate mock match events."""
            return []

        @staticmethod
        def generate_match_result(*args, **kwargs):
            """Generate mock match result."""
            return []


class TestDataGenerator:
    """Generator for test data scenarios for the mock server.

    This class provides methods for generating test data for specific scenarios
    that can be used with the mock server for testing the fogis-reporter application.
    """

    def __init__(self, mock_server: Optional[MockFogisServer] = None):
        """Initialize the test data generator.

        Args:
            mock_server: The mock server to use for generating test data.
                If None, the test data generator will only generate data
                but not interact with a mock server.
        """
        self.mock_server = mock_server

    def create_match_with_goals(
        self,
        home_goals: int = 2,
        away_goals: int = 1,
        home_team_name: Optional[str] = None,
        away_team_name: Optional[str] = None,
        match_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a match with the specified number of goals.

        Args:
            home_goals: The number of goals for the home team.
            away_goals: The number of goals for the away team.
            home_team_name: The name of the home team. If None, a random name will be
                generated.
            away_team_name: The name of the away team. If None, a random name will be
                generated.
            match_id: The match ID. If None, a random ID will be generated.

        Returns:
            A dictionary containing the match data and events.
        """
        # Generate a basic match
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        match = MockDataFactory.generate_match_details(match_id)

        # Set team names if provided
        if home_team_name:
            match["hemmalag"] = home_team_name
        if away_team_name:
            match["bortalag"] = away_team_name

        # Set the score
        match["hemmamal"] = home_goals
        match["bortamal"] = away_goals

        # Generate events for the goals
        events = []

        # Home team goals
        home_team_id = match.get("hemmalagid", MockDataFactory.generate_id())
        for i in range(home_goals):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 6,  # Regular goal
                    "matchlagid": home_team_id,
                    "matchminut": 10 + i * 10,  # Spread goals throughout the match
                    "period": 1
                    if i < 2
                    else 2,  # First 2 goals in first half, rest in second
                    "hemmamal": i + 1,
                    "bortamal": 0,
                    "trojnummer": random.randint(1, 11),  # Random jersey number
                    # Random player name
                    "spelarenamn": f"Player {random.randint(1, 11)}",
                }
            )

        # Away team goals
        away_team_id = match.get("bortalagid", MockDataFactory.generate_id())
        for i in range(away_goals):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 6,  # Regular goal
                    "matchlagid": away_team_id,
                    "matchminut": 15 + i * 10,  # Spread goals throughout the match
                    "period": 1
                    if i < 1
                    else 2,  # First goal in first half, rest in second
                    "hemmamal": home_goals,
                    "bortamal": i + 1,
                    "trojnummer": random.randint(1, 11),  # Random jersey number
                    # Random player name
                    "spelarenamn": f"Player {random.randint(1, 11)}",
                }
            )

        # Sort events by minute
        events.sort(key=lambda e: e["matchminut"])

        # Generate team players
        home_team_players = MockDataFactory.generate_team_players(home_team_id)
        away_team_players = MockDataFactory.generate_team_players(away_team_id)

        # Generate match result
        match_result = [
            {
                "matchresultatid": MockDataFactory.generate_id(),
                "matchid": match_id,
                "matchresultattypid": 1,  # Full time
                "matchlag1mal": home_goals,
                "matchlag2mal": away_goals,
                "wo": False,
                "ow": False,
                "ww": False,
            },
            {
                "matchresultatid": MockDataFactory.generate_id(),
                "matchid": match_id,
                "matchresultattypid": 2,  # Half time
                "matchlag1mal": min(
                    home_goals, 1
                ),  # Assume at most 1 goal in first half
                "matchlag2mal": min(
                    away_goals, 1
                ),  # Assume at most 1 goal in first half
                "wo": False,
                "ow": False,
                "ww": False,
            },
        ]

        return {
            "match": match,
            "events": events,
            "home_team_players": home_team_players,
            "away_team_players": away_team_players,
            "match_result": match_result,
        }

    def create_match_with_cards(
        self,
        home_yellow_cards: int = 1,
        home_red_cards: int = 0,
        away_yellow_cards: int = 2,
        away_red_cards: int = 1,
        match_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a match with the specified number of cards.

        Args:
            home_yellow_cards: The number of yellow cards for the home team.
            home_red_cards: The number of red cards for the home team.
            away_yellow_cards: The number of yellow cards for the away team.
            away_red_cards: The number of red cards for the away team.
            match_id: The match ID. If None, a random ID will be generated.

        Returns:
            A dictionary containing the match data and events.
        """
        # Generate a basic match
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        match = MockDataFactory.generate_match_details(match_id)

        # Generate events for the cards
        events = []

        # Home team yellow cards
        home_team_id = match.get("hemmalagid", MockDataFactory.generate_id())
        for i in range(home_yellow_cards):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 7,  # Yellow card
                    "matchlagid": home_team_id,
                    "matchminut": 20 + i * 15,  # Spread cards throughout the match
                    "period": 1
                    if i < 2
                    else 2,  # First 2 cards in first half, rest in second
                    "hemmamal": 0,
                    "bortamal": 0,
                    "trojnummer": random.randint(1, 11),  # Random jersey number
                    # Random player name
                    "spelarenamn": f"Player {random.randint(1, 11)}",
                }
            )

        # Home team red cards
        for i in range(home_red_cards):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 8,  # Red card
                    "matchlagid": home_team_id,
                    "matchminut": 35 + i * 15,  # Spread cards throughout the match
                    "period": 1
                    if i < 1
                    else 2,  # First card in first half, rest in second
                    "hemmamal": 0,
                    "bortamal": 0,
                    "trojnummer": random.randint(1, 11),  # Random jersey number
                    # Random player name
                    "spelarenamn": f"Player {random.randint(1, 11)}",
                }
            )

        # Away team yellow cards
        away_team_id = match.get("bortalagid", MockDataFactory.generate_id())
        for i in range(away_yellow_cards):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 7,  # Yellow card
                    "matchlagid": away_team_id,
                    "matchminut": 25 + i * 15,  # Spread cards throughout the match
                    "period": 1
                    if i < 2
                    else 2,  # First 2 cards in first half, rest in second
                    "hemmamal": 0,
                    "bortamal": 0,
                    "trojnummer": random.randint(1, 11),  # Random jersey number
                    # Random player name
                    "spelarenamn": f"Player {random.randint(1, 11)}",
                }
            )

        # Away team red cards
        for i in range(away_red_cards):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 8,  # Red card
                    "matchlagid": away_team_id,
                    "matchminut": 40 + i * 15,  # Spread cards throughout the match
                    # First card in first half, rest in second
                    "period": 1 if i < 1 else 2,
                    "hemmamal": 0,
                    "bortamal": 0,
                    "trojnummer": random.randint(1, 11),  # Random jersey number
                    # Random player name
                    "spelarenamn": f"Player {random.randint(1, 11)}",
                }
            )

        # Sort events by minute
        events.sort(key=lambda e: e["matchminut"])

        # Generate team players
        home_team_players = MockDataFactory.generate_team_players(home_team_id)
        away_team_players = MockDataFactory.generate_team_players(away_team_id)

        return {
            "match": match,
            "events": events,
            "home_team_players": home_team_players,
            "away_team_players": away_team_players,
        }

    def create_match_with_substitutions(
        self,
        home_substitutions: int = 3,
        away_substitutions: int = 3,
        match_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a match with the specified number of substitutions.

        Args:
            home_substitutions: The number of substitutions for the home team.
            away_substitutions: The number of substitutions for the away team.
            match_id: The match ID. If None, a random ID will be generated.

        Returns:
            A dictionary containing the match data and events.
        """
        # Generate a basic match
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        match = MockDataFactory.generate_match_details(match_id)

        # Generate events for the substitutions
        events = []

        # Home team substitutions
        home_team_id = match.get("hemmalagid", MockDataFactory.generate_id())
        for i in range(home_substitutions):
            # Player going out
            out_event_id = MockDataFactory.generate_id()
            out_event = {
                "matchhandelseid": out_event_id,
                "matchid": match_id,
                "matchhandelsetypid": 16,  # Substitution out
                "matchlagid": home_team_id,
                "matchminut": 46
                + i * 15,  # Spread substitutions throughout the second half
                "period": 2,  # All substitutions in second half
                "hemmamal": 0,
                "bortamal": 0,
                "trojnummer": i + 1,  # Player number
                "spelarenamn": f"Player {i + 1}",  # Player name
            }
            events.append(out_event)

            # Player coming in
            in_event = {
                "matchhandelseid": MockDataFactory.generate_id(),
                "matchid": match_id,
                "matchhandelsetypid": 17,  # Substitution in
                "matchlagid": home_team_id,
                "matchminut": 46 + i * 15,  # Same minute as the out event
                "period": 2,  # All substitutions in second half
                "hemmamal": 0,
                "bortamal": 0,
                "trojnummer": i + 12,  # Substitute player number
                # Substitute player name
                "spelarenamn": f"Player {i + 12}",
                # Related to the out event
                "relateradTillMatchhandelseID": out_event_id,
            }
            events.append(in_event)

        # Away team substitutions
        away_team_id = match.get("bortalagid", MockDataFactory.generate_id())
        for i in range(away_substitutions):
            # Player going out
            out_event_id = MockDataFactory.generate_id()
            out_event = {
                "matchhandelseid": out_event_id,
                "matchid": match_id,
                "matchhandelsetypid": 16,  # Substitution out
                "matchlagid": away_team_id,
                "matchminut": 50
                + i * 15,  # Spread substitutions throughout the second half
                "period": 2,  # All substitutions in second half
                "hemmamal": 0,
                "bortamal": 0,
                "trojnummer": i + 1,  # Player number
                "spelarenamn": f"Player {i + 1}",  # Player name
            }
            events.append(out_event)

            # Player coming in
            in_event = {
                "matchhandelseid": MockDataFactory.generate_id(),
                "matchid": match_id,
                "matchhandelsetypid": 17,  # Substitution in
                "matchlagid": away_team_id,
                "matchminut": 50 + i * 15,  # Same minute as the out event
                "period": 2,  # All substitutions in second half
                "hemmamal": 0,
                "bortamal": 0,
                "trojnummer": i + 12,  # Substitute player number
                # Substitute player name
                "spelarenamn": f"Player {i + 12}",
                # Related to the out event
                "relateradTillMatchhandelseID": out_event_id,
            }
            events.append(in_event)

        # Sort events by minute
        events.sort(key=lambda e: e["matchminut"])

        # Generate team players
        home_team_players = MockDataFactory.generate_team_players(home_team_id)
        away_team_players = MockDataFactory.generate_team_players(away_team_id)

        return {
            "match": match,
            "events": events,
            "home_team_players": home_team_players,
            "away_team_players": away_team_players,
        }

    def create_match_with_team_official_actions(
        self,
        home_warnings: int = 1,
        home_dismissals: int = 0,
        away_warnings: int = 1,
        away_dismissals: int = 1,
        match_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a match with team official actions.

        Args:
            home_warnings: The number of warnings for home team officials.
            home_dismissals: The number of dismissals for home team officials.
            away_warnings: The number of warnings for away team officials.
            away_dismissals: The number of dismissals for away team officials.
            match_id: The match ID. If None, a random ID will be generated.

        Returns:
            A dictionary containing the match data and events.
        """
        # Generate a basic match
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        match = MockDataFactory.generate_match_details(match_id)

        # Generate events for the team official actions
        events = []

        # Home team warnings
        home_team_id = match.get("hemmalagid", MockDataFactory.generate_id())
        for i in range(home_warnings):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 18,  # Team official warning
                    "matchlagid": home_team_id,
                    "matchminut": 30 + i * 20,  # Spread warnings throughout the match
                    "period": 1
                    if i < 1
                    else 2,  # First warning in first half, rest in second
                    "hemmamal": 0,
                    "bortamal": 0,
                    "spelarenamn": f"Official {i + 1}",  # Official name
                }
            )

        # Home team dismissals
        for i in range(home_dismissals):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 19,  # Team official dismissal
                    "matchlagid": home_team_id,
                    "matchminut": 60 + i * 20,  # Spread dismissals throughout the match
                    "period": 2,  # All dismissals in second half
                    "hemmamal": 0,
                    "bortamal": 0,
                    "spelarenamn": f"Official {i + 1 + home_warnings}",  # Official name
                }
            )

        # Away team warnings
        away_team_id = match.get("bortalagid", MockDataFactory.generate_id())
        for i in range(away_warnings):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 18,  # Team official warning
                    "matchlagid": away_team_id,
                    "matchminut": 35 + i * 20,  # Spread warnings throughout the match
                    "period": 1
                    if i < 1
                    else 2,  # First warning in first half, rest in second
                    "hemmamal": 0,
                    "bortamal": 0,
                    "spelarenamn": f"Official {i + 1}",  # Official name
                }
            )

        # Away team dismissals
        for i in range(away_dismissals):
            events.append(
                {
                    "matchhandelseid": MockDataFactory.generate_id(),
                    "matchid": match_id,
                    "matchhandelsetypid": 19,  # Team official dismissal
                    "matchlagid": away_team_id,
                    "matchminut": 65 + i * 20,  # Spread dismissals throughout the match
                    "period": 2,  # All dismissals in second half
                    "hemmamal": 0,
                    "bortamal": 0,
                    "spelarenamn": f"Official {i + 1 + away_warnings}",  # Official name
                }
            )

        # Sort events by minute
        events.sort(key=lambda e: e["matchminut"])

        return {
            "match": match,
            "events": events,
        }

    def create_match_with_specific_result(
        self,
        home_score: int,
        away_score: int,
        halftime_home_score: Optional[int] = None,
        halftime_away_score: Optional[int] = None,
        match_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a match with a specific result.

        Args:
            home_score: The final score for the home team.
            away_score: The final score for the away team.
            halftime_home_score: The halftime score for the home team.
                If None, half of the final score will be used.
            halftime_away_score: The halftime score for the away team.
                If None, half of the final score will be used.
            match_id: The match ID. If None, a random ID will be generated.

        Returns:
            A dictionary containing the match data and result.
        """
        # Generate a basic match
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        match = MockDataFactory.generate_match_details(match_id)

        # Set the score
        match["hemmamal"] = home_score
        match["bortamal"] = away_score

        # Set halftime scores if not provided
        if halftime_home_score is None:
            halftime_home_score = home_score // 2
        if halftime_away_score is None:
            halftime_away_score = away_score // 2

        # Set halftime scores in the match
        match["halvtidHemmamal"] = halftime_home_score
        match["halvtidBortamal"] = halftime_away_score

        # Generate match result
        match_result = [
            {
                "matchresultatid": MockDataFactory.generate_id(),
                "matchid": match_id,
                "matchresultattypid": 1,  # Full time
                "matchlag1mal": home_score,
                "matchlag2mal": away_score,
                "wo": False,
                "ow": False,
                "ww": False,
            },
            {
                "matchresultatid": MockDataFactory.generate_id(),
                "matchid": match_id,
                "matchresultattypid": 2,  # Half time
                "matchlag1mal": halftime_home_score,
                "matchlag2mal": halftime_away_score,
                "wo": False,
                "ow": False,
                "ww": False,
            },
        ]

        return {
            "match": match,
            "match_result": match_result,
        }

    def create_complete_match_scenario(
        self,
        home_goals: int = 2,
        away_goals: int = 1,
        home_yellow_cards: int = 1,
        home_red_cards: int = 0,
        away_yellow_cards: int = 2,
        away_red_cards: int = 1,
        home_substitutions: int = 3,
        away_substitutions: int = 3,
        home_official_warnings: int = 1,
        home_official_dismissals: int = 0,
        away_official_warnings: int = 1,
        away_official_dismissals: int = 1,
        match_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a complete match scenario with all types of events.

        Args:
            home_goals: The number of goals for the home team.
            away_goals: The number of goals for the away team.
            home_yellow_cards: The number of yellow cards for the home team.
            home_red_cards: The number of red cards for the home team.
            away_yellow_cards: The number of yellow cards for the away team.
            away_red_cards: The number of red cards for the away team.
            home_substitutions: The number of substitutions for the home team.
            away_substitutions: The number of substitutions for the away team.
            home_official_warnings: The number of warnings for home team officials.
            home_official_dismissals: The number of dismissals for home team officials.
            away_official_warnings: The number of warnings for away team officials.
            away_official_dismissals: The number of dismissals for away team officials.
            match_id: The match ID. If None, a random ID will be generated.

        Returns:
            A dictionary containing the match data and all events.
        """
        # Generate a basic match
        if match_id is None:
            match_id = MockDataFactory.generate_id()

        # Create match with goals
        match_with_goals = self.create_match_with_goals(
            home_goals=home_goals,
            away_goals=away_goals,
            match_id=match_id,
        )

        # Create match with cards
        match_with_cards = self.create_match_with_cards(
            home_yellow_cards=home_yellow_cards,
            home_red_cards=home_red_cards,
            away_yellow_cards=away_yellow_cards,
            away_red_cards=away_red_cards,
            match_id=match_id,
        )

        # Create match with substitutions
        match_with_substitutions = self.create_match_with_substitutions(
            home_substitutions=home_substitutions,
            away_substitutions=away_substitutions,
            match_id=match_id,
        )

        # Create match with team official actions
        match_with_team_official_actions = self.create_match_with_team_official_actions(
            home_warnings=home_official_warnings,
            home_dismissals=home_official_dismissals,
            away_warnings=away_official_warnings,
            away_dismissals=away_official_dismissals,
            match_id=match_id,
        )

        # Combine all events
        all_events = (
            match_with_goals.get("events", [])
            + match_with_cards.get("events", [])
            + match_with_substitutions.get("events", [])
            + match_with_team_official_actions.get("events", [])
        )

        # Sort events by minute
        all_events.sort(key=lambda e: e["matchminut"])

        # Use the match from match_with_goals
        match = match_with_goals.get("match", {})

        # Use the team players from match_with_goals
        home_team_players = match_with_goals.get("home_team_players", {})
        away_team_players = match_with_goals.get("away_team_players", {})

        # Use the match result from match_with_goals
        match_result = match_with_goals.get("match_result", [])

        return {
            "match": match,
            "events": all_events,
            "home_team_players": home_team_players,
            "away_team_players": away_team_players,
            "match_result": match_result,
        }

    def apply_to_mock_server(self, scenario_data: Dict[str, Any]) -> None:
        """Apply the scenario data to the mock server.

        This method configures the mock server to return the scenario data
        when the corresponding API endpoints are called.

        Args:
            scenario_data: The scenario data to apply to the mock server.

        Raises:
            ValueError: If the mock server is not set.
        """
        if self.mock_server is None:
            raise ValueError(
                "Mock server is not set. Initialize the TestDataGenerator with a mock server."
            )

        # TODO: Implement this method once we have access to the mock server API
        # This would involve configuring the mock server to return the scenario data
        # when the corresponding API endpoints are called
        pass
