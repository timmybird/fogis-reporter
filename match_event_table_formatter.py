"""Match Event Table Formatter module.

This module provides functionality for match event table formatter.
"""

from typing import Any, Dict, List, Optional

from tabulate import tabulate

from emoji_config import EVENT_EMOJIS


class MatchEventTableFormatter:
    def __init__(
        self,
        event_types: Dict[int, Dict[str, Any]],
        team1_name: str,
        team2_name: str,
        team1_id: int,
        team2_id: int
    ):
        """
        Initializes the MatchEventTableFormatter.

        Args:
            event_types (dict): Dictionary of event types from fogis_api_client.
            team1_name (str): Name of team 1 (home team).
            team2_name (str): Name of team 2 (away team).
            team1_id (int): ID of team 1.  # ADDED
            team2_id (int): ID of team 2.  # ADDED
        """
        self.event_types = event_types
        self.team1_name = team1_name
        self.team2_name = team2_name
        self.team1_id = team1_id  # ADDED
        self.team2_id = team2_id  # ADDED
        self.event_categories: Dict[str, List[str]] = {
            "Goals": [
                "Regular Goal",
                "Header Goal",
                "Corner Goal",
                "Free Kick Goal",
                "Own Goal",
                "Penalty Goal"
            ],
            "Yellow Cards": ["Yellow Card", "Second Yellow Card"],
            "Red Cards": ["Red Card (Denying Goal Opportunity)"],
            "Substitutions": ["Substitution"],
            "Other Events": []
        }
        self._populate_other_events_category()

        self.category_icons: Dict[str, str] = {
            "Goals": "⚽️ ",
            "Yellow Cards": "🟨 ",
            "Red Cards": "🟥 ",
            "Substitutions": "🔄 ",
            "Other Events": "ℹ️ "
        }

    def _populate_other_events_category(self) -> None:
        """Populates the 'Other Events' category with event types not in other" \
            "categories."""
        categorized_event_names: List[str] = []
        for category_list in self.event_categories.values():
            if isinstance(category_list, list):
                categorized_event_names.extend(category_list)

        for event_type_id, event_data in self.event_types.items():
            event_name = event_data['name']
            if event_name not in categorized_event_names and not event_data.get("control_event"):
                self.event_categories["Other Events"].append(event_name)

    def format_structured_table(self, match_events_json: List[Dict[str, Any]], team1_players_json: List[Dict[str, Any]],
                             team2_players_json: List[Dict[str, Any]], team1_score: int, team2_score: int,
                             halftime_score_team1: int, halftime_score_team2: int) -> str:
        """Formats match events into a structured table with scoreline, skipping" \
            "'Unknown Team' events."""
        if not match_events_json:
            return "No events reported yet."

        structured_data: Dict[str, Dict[str, List[str]]] = {}
        structured_data["Score"] = {self.team1_name: [], self.team2_name: []}
        structured_data["Score"][self.team1_name].append(f"Full: {team1_score}")
        structured_data["Score"][self.team2_name].append(f"Full: {team2_score}")
        structured_data["Score"][self.team1_name].append(f"(HT: {halftime_score_team1})")
        structured_data["Score"][self.team2_name].append(f"(HT: {halftime_score_team2})")

        for category in self.event_categories:
            structured_data[category] = {self.team1_name: [], self.team2_name: []}

        for event in match_events_json:
            # Add a reference to all events for looking up related events (for substitutions)
            event['_all_events'] = match_events_json

            event_type_id = event['matchhandelsetypid']
            event_type_name = self.event_types.get(
                event_type_id,
                {}).get('name',
                'Unknown Event'
            )
            team_id = event['matchlagid']
            team_name = self.team1_name if team_id == self.team1_id else self.team2_name if team_id == self.team2_id else "Unknown Team"

            player_jersey = self._get_player_jersey_from_event(
                event,
                team_id,
                team1_players_json,
                team2_players_json
            )

            event_info = ""
            event_emoji = EVENT_EMOJIS.get(event_type_name, "")

            if event_type_name in self.event_categories["Yellow Cards"]:
                event_info = f"{event_emoji} {player_jersey} - {event['matchminut']}'"
            elif event_type_name in self.event_categories["Red Cards"]:
                event_info = f"{event_emoji} {player_jersey} - {event['matchminut']}'"
            elif event_type_name in self.event_categories["Substitutions"]:
                # Add debug logging for substitution events
                print(f"\n[DEBUG] Substitution event data: {event}")

                # Check for related event
                related_event_id = event.get('relateradTillMatchhandelseID')
                if related_event_id and related_event_id != 0:
                    print(f"[DEBUG] Related event ID: {related_event_id}")
                    # Find the related event
                    for related_event in event.get('_all_events', []):
                        if related_event.get('matchhandelseid') == related_event_id:
                            print(f"[DEBUG] Found related event: {related_event}")
                            break

                player2_jersey_out = self._get_player2_jersey_from_event(
                    event,
                    team_id,
                    team1_players_json,
                    team2_players_json
                )
                print(f"[DEBUG] Player coming in: {player_jersey}, Player going out: {player2_jersey_out}")

                event_info = f"{event_emoji} {player_jersey} in - {player2_jersey_out} out ({event['matchminut']}')"
            elif event_type_name in self.event_categories["Goals"]:
                goal_type_note = ""
                if event_type_name != "Regular Goal":
                    goal_type_note = f" ({event_type_name.replace(' Goal', '')})"
                event_info = f"{event_emoji} {player_jersey} - {event['matchminut']}'{goal_type_note}"
            else:
                event_info = f"{event_emoji} {event_type_name} ({player_jersey} - {event['matchminut']}')"

            category_found = False
            for category_name, event_name_list in self.event_categories.items():
                if event_type_name in event_name_list:
                    # --- ADDED condition to skip "Unknown Team" events ---
                    if team_name != "Unknown Team":
                        structured_data[category_name][team_name].append(event_info)
                    category_found = True
                    break
            if not category_found and event_type_name != "Unknown Event":
                # --- ADDED condition to skip "Unknown Team" events here as well (for "Other Events" category) ---
                if team_name != "Unknown Team":
                    structured_data["Other Events"][team_name].append(event_info)

        table_rows = []
        table_rows.append([f"{self.category_icons.get('Score', '')}**Score**", "", ""])
        max_score_lines = 2
        for i in range(max_score_lines):
            team1_score_line = structured_data["Score"][self.team1_name][i] if i < len(structured_data["Score"][self.team1_name]) else ""
            team2_score_line = structured_data["Score"][self.team2_name][i] if i < len(structured_data["Score"][self.team2_name]) else ""
            table_rows.append(["", team1_score_line, team2_score_line])

        for category_name, team_data in structured_data.items():
            if category_name == "Score":
                continue

            if any(team_data.values()):
                category_header = f"{self.category_icons.get(category_name, '')}**{category_name}**"
                table_rows.append([category_header, "", ""])
                max_events_in_category = max(
                    len(team_data[self.team1_name]),
                    len(team_data[self.team2_name])
                )
                for i in range(max_events_in_category):
                    team1_event = team_data[self.team1_name][i] if i < len(team_data[self.team1_name]) else ""
                    team2_event = team_data[self.team2_name][i] if i < len(team_data[self.team2_name]) else ""
                    table_rows.append(["", team1_event, team2_event])

        headers = ["Event Type", f"**{self.team1_name}**", f"**{self.team2_name}**"]

        if not table_rows:
            return "No events reported yet."

        return tabulate(
            table_rows,
            headers=headers,
            tablefmt="grid",
            numalign="left",
            stralign="left"
        )

    def _get_player_jersey_from_event(self, event: Dict[str, Any], team_id: int,
                                  team1_players_json: List[Dict[str, Any]],
                                  team2_players_json: List[Dict[str, Any]]) -> str:
        """Helper function to get player jersey number from event data.

        First tries to get trojnummer directly from the event. If not available,
        tries to look up the jersey number using spelareid.
        """
        # First try to get trojnummer directly
        jersey = event.get('trojnummer')
        if jersey is not None:
            return str(jersey)

        # If trojnummer is not available, try to look up using spelareid
        player_id = event.get('spelareid')
        if player_id is not None:
            # Determine which team's players to search
            players_json = team1_players_json if team_id == self.team1_id else team2_players_json

            # Look for the player with matching spelareid
            for player in players_json:
                if player.get('spelareid') == player_id:
                    jersey = player.get('trojnummer')
                    if jersey is not None:
                        return str(jersey)

        # If all else fails, return N/A
        return "N/A"

    def _get_player2_jersey_from_event(self, event: Dict[str, Any], team_id: int,
                                   team1_players_json: List[Dict[str, Any]],
                                   team2_players_json: List[Dict[str, Any]]) -> str:
        """Helper function to get player2 jersey number from event data for substitutions.

        For substitutions, we need to find the related event (player leaving the field)
        using the relateradTillMatchhandelseID property.
        """
        # Check if this is a substitution event with a related event ID
        related_event_id = event.get('relateradTillMatchhandelseID')

        # If there's no related event ID, try the old methods
        if not related_event_id or related_event_id == 0:
            # First try to get trojnummer2 directly
            jersey = event.get('trojnummer2')
            if jersey is not None:
                return str(jersey)

            # If trojnummer2 is not available, try to look up using spelareid2
            player_id = event.get('spelareid2')
            if player_id is not None:
                # Determine which team's players to search
                players_json = team1_players_json if team_id == self.team1_id else team2_players_json

                # Look for the player with matching spelareid
                for player in players_json:
                    if player.get('spelareid') == player_id:
                        jersey = player.get('trojnummer')
                        if jersey is not None:
                            return str(jersey)

            # If all else fails, return N/A
            return "N/A"

        # If we have a related event ID, find the corresponding event
        # This is the event for the player leaving the field
        match_events_json = event.get('_all_events', [])
        if not match_events_json:
            return "N/A"

        # Find the related event
        for related_event in match_events_json:
            if related_event.get('matchhandelseid') == related_event_id:
                # Get the jersey number from the related event
                jersey = related_event.get('trojnummer')
                if jersey is not None:
                    return str(jersey)

                # If trojnummer is not available, try to look up using spelareid
                player_id = related_event.get('spelareid')
                if player_id is not None:
                    # Determine which team's players to search
                    players_json = team1_players_json if team_id == self.team1_id else team2_players_json

                    # Look for the player with matching spelareid
                    for player in players_json:
                        if player.get('spelareid') == player_id:
                            jersey = player.get('trojnummer')
                            if jersey is not None:
                                return str(jersey)

        # If all else fails, return N/A
        return "N/A"
