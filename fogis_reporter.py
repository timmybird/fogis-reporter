"""Fogis Reporter module.

This module provides functionality for fogis reporter.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from fogis_api_client.fogis_api_client import (
    EVENT_TYPES,
    FogisApiClient,
    FogisLoginError,
)

# Import safe API wrapper
from api_utils import safe_fetch_json_list

# Import emoji dictionaries
from emoji_config import EVENT_EMOJIS, MENU_EMOJIS
from fogis_data_parser import FogisDataParser
from match_context import MatchContext, Score, Scores
from match_event_table_formatter import MatchEventTableFormatter


def select_match_interactively(matches):
    """Interactively allows the user to select a match from a list with enhanced formatting.

    Args:
        matches (list): A list of match dictionaries.

    Returns:
        dict: The selected match dictionary, or None if selection fails or user chooses to exit.
    """
    if not matches:
        print("No matches available to select.")
        return None

    # Create a more visually appealing header
    print("\n" + "=" * 60)
    print("  MATCH SELECTION")
    print("=" * 60)

    print("\nAvailable Matches:")
    for index, match in enumerate(matches):
        # Extract date and time for better formatting
        match_info = match["label"]
        print(f"  {index + 1}: {match_info}")

    print("\n  Enter empty string to exit")
    print("-" * 60)

    while True:
        match_choice = input("Select match number: ")
        if match_choice == "":
            print("Exiting...")
            return None
        try:
            match_index = int(match_choice) - 1
            if 0 <= match_index < len(matches):
                selected_match = matches[match_index]
                print(f"\nSelected: {selected_match['label']}")
                return selected_match
            else:
                print("Invalid match number selected. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number or empty string to exit.")


def _parse_minute_input(
    minute_str_arg: str,
    num_periods_arg: int,
    period_length_arg: int,
    num_extra_periods_arg: int,
    extra_period_length_arg: int,
) -> Tuple[int, int]:
    """Parses the minute input from the user, handling regular time and extra time."""
    try:
        if "+" in minute_str_arg:
            parts = minute_str_arg.split("+")
            minute_parsed = int(parts[0])
            stoppage_time = (
                int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            )
            # Assuming stoppage time is always added to the last minute of the current period
            total_regular_time = num_periods_arg * period_length_arg
            if minute_parsed > total_regular_time:
                raise ValueError(
                    "Invalid minute. Stoppage time can only be added to the last"
                    "minute of regular time."
                )
            # Determine which period the minute belongs to
            period_calculated = (minute_parsed - 1) // period_length_arg + 1
            minute_parsed += stoppage_time  # Apply stoppage time
        else:
            minute_parsed = int(minute_str_arg)
            total_regular_time = num_periods_arg * period_length_arg
            total_extra_time = num_extra_periods_arg * extra_period_length_arg
            if (
                minute_parsed <= 0
                or minute_parsed > total_regular_time + total_extra_time
            ):
                raise ValueError(
                    "Invalid minute. Please enter a value within the valid range."
                )
            if minute_parsed <= total_regular_time:
                # Determine which period the minute belongs to
                period_calculated = (minute_parsed - 1) // period_length_arg + 1
            else:
                # Extra time period calculation
                extra_time_start = total_regular_time
                period_calculated = num_periods_arg + (
                    (minute_parsed - extra_time_start - 1) // extra_period_length_arg
                    + 1
                )

        return minute_parsed, period_calculated

    except ValueError as err:
        raise ValueError(f"Invalid minute format: {err}")


def display_main_menu(match_context: MatchContext):
    """Displays the main menu with different event categories."""
    while True:
        # Get current scores for display
        scores = match_context.scores

        # Create a more visually appealing header with match info and current score
        print("\n" + "=" * 60)
        print(f"  MATCH: {match_context.team1_name} vs {match_context.team2_name}")
        print(
            f"CURRENT SCORE: {match_context.team1_name} {scores.regular_time.home} -"
            f"{scores.regular_time.away} {match_context.team2_name}"
        )
        print("=" * 60)

        # Main menu options with better spacing and organization
        print("\nMAIN MENU - Select an option:")
        print(
            f"1: {MENU_EMOJIS['report_events']} Report Match Events (goals, cards,"
            "substitutions)"
        )
        print(
            f"2: {MENU_EMOJIS['control_events']} Report Time Events (period start/end,"
            "game end)"
        )
        print(
            f"3: {MENU_EMOJIS['staff_events']} Report Staff Events (coach cards, officials)"
        )
        print(f"4: {MENU_EMOJIS['report_results']} Report Final Match Results")
        print(
            f"\n {MENU_EMOJIS['back']} Enter empty string to return to match selection"
        )
        print("-" * 60)

        choice = input("Select option [1-4]: ")

        if choice == "":
            return
        if choice == "1":
            report_match_events_menu(match_context)
        elif choice == "2":
            report_control_events_menu(match_context)
        elif choice == "3":
            report_staff_events_menu(match_context)
        elif choice == "4":
            report_results_menu(match_context)
        else:
            print("Invalid option. Please try again.")


def report_match_events_menu(match_context: MatchContext):
    """Menu for reporting match events (goals, cards, etc.)"""
    while True:
        # Get current scores for display
        scores = match_context.scores

        # Create a more visually appealing header with match info and current score
        print("\n" + "=" * 60)
        print(
            f"MATCH EVENTS - {match_context.team1_name} vs {match_context.team2_name}"
        )
        print(
            f"CURRENT SCORE: {match_context.team1_name} {scores.regular_time.home} - {scores.regular_time.away} {match_context.team2_name}"
        )
        print("=" * 60)

        # Team selection with better formatting
        print("\nSelect a team to report events for:")
        print(
            f"1: {MENU_EMOJIS['team1_events']} {match_context.team1_name} (Home Team)"
        )
        print(
            f"2: {MENU_EMOJIS['team2_events']} {match_context.team2_name} (Away Team)"
        )
        print("\nOther options:")
        print(f"  3: {MENU_EMOJIS['clear_events']} Clear all recorded events")
        print(f"\n  {MENU_EMOJIS['back']} Enter empty string to return to main menu")
        print("-" * 60)

        choice = input("Select option [1-3]: ")

        if choice == "":
            return
        if choice in ["1", "2"]:
            team_number = int(choice)
            report_team_event(match_context, team_number)
        elif choice == "3":
            # Add confirmation step to prevent accidental clearing
            confirm = input(
                "Are you sure you want to clear ALL events? Type 'clear' to confirm: "
            )
            if confirm.lower() == "clear":
                new_events = _handle_clear_events(match_context)
                match_context.match_events_json = new_events
                _display_current_events_table(match_context)
            else:
                print("Clear operation cancelled.")
        else:
            print("Invalid option. Please try again.")


def report_team_event(match_context: MatchContext, team_number: int):
    """Reports an event for a specific team."""
    team1_players_json = match_context.team1_players_json
    team2_players_json = match_context.team2_players_json

    scores: Scores = FogisDataParser.calculate_scores(match_context)
    team1_score = scores.regular_time.home
    team2_score = scores.regular_time.away

    # Get the current team's players
    current_team_players_json = (
        team1_players_json if team_number == 1 else team2_players_json
    )
    team_name = (
        match_context.team1_name if team_number == 1 else match_context.team2_name
    )

    # Display event type options
    print(f"\n--- Event Types for {team_name} ---")
    print("1: ⚽ Goal (NEW: Enter jersey number or goal type code)")
    print("2: 🟨 Card (Yellow/Red)")
    print("3: 🔄 Substitution")
    print("4: 👨‍💼 Team Official Action")
    print(f"{MENU_EMOJIS['back']} Enter empty string to go back")

    event_category = input("Select event category: ")

    if event_category == "":
        return
    if event_category == "1":  # Goal events - use smart input detection
        new_events = _report_goal_with_smart_input(
            match_context,
            team_number,
            current_team_players_json,
            team1_score,
            team2_score,
        )
        if new_events is not None:
            match_context.match_events_json = new_events
            _display_current_events_table(
                match_context
            )  # Display table after goal reporting
    else:
        # Use existing event selection logic for non-goal events
        try:
            (
                _,
                selected_event_type,
                event_type_id,
                event_type_name,
                is_goal_event,
                current_team_players_json,
            ) = _get_event_details_from_input(
                str(team_number), team1_players_json, team2_players_json, event_category
            )
            if not selected_event_type:  # Input was invalid
                return

            if selected_event_type["name"] == "Substitution":
                new_events = _report_substitution_event(
                    match_context,
                    team_number,
                    current_team_players_json,
                    team1_score,
                    team2_score,
                )
                if new_events is not None:
                    match_context.match_events_json = new_events
            elif selected_event_type["name"] == "Team Official Action":
                new_events = _report_team_official_action_event(match_context)
                if new_events is not None:
                    match_context.match_events_json = new_events
            else:
                new_events = _report_player_event(
                    match_context,
                    team_number,
                    selected_event_type,
                    current_team_players_json,
                    team1_score,
                    team2_score,
                )
                if new_events is not None:
                    match_context.match_events_json = new_events

                if (
                    match_context.match_events_json is not None
                ):  # Event reporting was successful
                    _display_current_events_table(
                        match_context
                    )  # Display table after each event

        except ValueError as e:
            print(
                e
            )  # Print specific error message from input parsing or event reporting


def _determine_event_type_from_timestamp(
    timestamp: int, match_context: MatchContext
) -> Tuple[int, str, int]:
    """Automatically determines the appropriate event type based on the timestamp and match structure.

    Args:
        timestamp: The match minute (e.g., 1, 45, 46, 90)
        match_context: The match context containing match structure information

    Returns:
        A tuple containing (event_type_id, event_type_name, period)

    Raises:
        ValueError: If the timestamp is invalid or doesn't map to a specific event
    """
    num_periods = match_context.num_periods
    period_length = match_context.period_length
    num_extra_periods = match_context.num_extra_periods
    extra_period_length = match_context.extra_period_length

    # Calculate period boundaries
    period_boundaries = []
    for i in range(1, num_periods + 1):
        start_minute = 1 + (i - 1) * period_length
        end_minute = i * period_length
        period_boundaries.append((start_minute, end_minute, i))

    # Add extra time periods if applicable
    if num_extra_periods > 0:
        regular_time_end = num_periods * period_length
        for i in range(1, num_extra_periods + 1):
            start_minute = regular_time_end + 1 + (i - 1) * extra_period_length
            end_minute = regular_time_end + i * extra_period_length
            period = num_periods + i
            period_boundaries.append((start_minute, end_minute, period))

    # Determine event type based on timestamp
    for start, end, period in period_boundaries:
        if timestamp == start:
            # Period Start
            return 31, "Period Start", period
        if timestamp == end or (timestamp > end and "+" in str(timestamp)):
            # Period End
            if period == num_periods and num_extra_periods == 0:
                # Last period of regular time with no extra time - both Period End and Game End
                return 33, "Game End", period
            if period == num_periods + num_extra_periods and num_extra_periods > 0:
                # Last period of extra time - both Period End and Game End
                return 33, "Game End", period
            else:
                # Regular period end
                return 32, "Period End", period

    # If we get here, the timestamp doesn't map to a specific event
    raise ValueError(
        f"Timestamp {timestamp} doesn't correspond to a period start or end."
    )


def _report_smart_control_event(
    match_context: MatchContext,
    event_type_id: int,
    event_type_name: str,
    period: int,
    time_input: str,
):
    """Reports a control event based on smart timestamp detection."""
    match_id = match_context.match_id
    team1_score = match_context.scores.regular_time.home
    team2_score = match_context.scores.regular_time.away

    # Parse the time input to get the actual minute
    try:
        match_minute, period_calculated = _parse_minute_input(
            time_input,
            match_context.num_periods,
            match_context.period_length,
            match_context.num_extra_periods,
            match_context.extra_period_length,
        )

        # Create the control event JSON in the correct API format
        control_event = {
            "matchhandelseid": 0,
            "matchid": match_id,
            "period": period,
            "matchminut": match_minute,
            "sekund": 0,
            "matchhandelsetypid": event_type_id,
            "matchlagid": 0,
            "spelareid": 0,
            "spelareid2": 0,
            "planpositionx": "-1",
            "planpositiony": "-1",
            "matchdeltagareid": 0,
            "matchdeltagareid2": 0,
            "fotbollstypId": 1,
            "relateradTillMatchhandelseID": 0,
            "hemmamal": team1_score,
            "bortamal": team2_score,
        }

        # Handle automatic period start and period end logic AND API reporting
        _add_control_event_with_implicit_events(control_event, match_context)

        print(f"{event_type_name} reported at minute {match_minute}, period {period}.")
    except ValueError as e:
        print(f"Error: {e}")


def report_control_events_menu(match_context: MatchContext):
    """Menu for reporting control events (period end, game end) with smart timestamp detection"""
    while True:
        # Get current scores for display
        scores = match_context.scores

        # Create a more visually appealing header with match info
        print("\n" + "=" * 60)
        print(
            f"TIME CONTROL EVENTS - {match_context.team1_name} vs {match_context.team2_name}"
        )
        print(
            f"CURRENT SCORE: {match_context.team1_name} {scores.regular_time.home} - {scores.regular_time.away} {match_context.team2_name}"
        )
        print("=" * 60)

        # Calculate period boundaries for help text
        period_boundaries = []
        for i in range(1, match_context.num_periods + 1):
            start_minute = 1 + (i - 1) * match_context.period_length
            end_minute = i * match_context.period_length
            period_boundaries.append((start_minute, end_minute, i))

        # Add extra time periods if applicable
        if match_context.num_extra_periods > 0:
            regular_time_end = match_context.num_periods * match_context.period_length
            for i in range(1, match_context.num_extra_periods + 1):
                start_minute = (
                    regular_time_end + 1 + (i - 1) * match_context.extra_period_length
                )
                end_minute = regular_time_end + i * match_context.extra_period_length
                period = match_context.num_periods + i
                period_boundaries.append((start_minute, end_minute, period))

        # Display smart timestamp input instructions
        print(
            "\nEnter a timestamp to automatically report the appropriate time control event:"
        )
        print("  - Enter the minute number when the event occurred")
        print(
            "  - The system will automatically determine if it's a period start, period end, or game end"
        )
        print("\nValid timestamps for this match:")

        for start, end, period in period_boundaries:
            if period <= match_context.num_periods:
                print(f"  {start} → Start of Period {period}")
                print(
                    f"  {end} → End of Period {period}"
                    + (
                        " and End of Game"
                        if period == match_context.num_periods
                        and match_context.num_extra_periods == 0
                        else ""
                    )
                )
            else:
                # Extra time period
                extra_period = period - match_context.num_periods
                print(f"  {start} → Start of Extra Time Period {extra_period}")
                print(
                    f"  {end} → End of Extra Time Period {extra_period}"
                    + (
                        " and End of Game"
                        if period
                        == match_context.num_periods + match_context.num_extra_periods
                        else ""
                    )
                )

        print("\nYou can also use stoppage time notation (e.g., 45+2, 90+3)")
        print("\nOr select a specific event type:")
        print(f"  1: {EVENT_EMOJIS['Period End']} Period End")
        print(f"  2: {EVENT_EMOJIS['Game End']} Game End")
        print(f"\n  {MENU_EMOJIS['back']} Enter empty string to return to main menu")
        print("-" * 60)

        choice = input("Enter timestamp or option [1-2]: ")

        if choice == "":
            return
        if choice in ["1", "2"]:
            # Use the existing control event reporting flow
            _report_control_event_interactively(match_context, choice)
            _display_current_events_table(match_context)
        else:
            try:
                # Parse the timestamp input
                if "+" in choice:
                    # Handle stoppage time notation (e.g., 45+2)
                    parts = choice.split("+")
                    base_minute = int(parts[0])
                    timestamp = base_minute  # We'll use the base minute to determine the event type
                else:
                    timestamp = int(choice)

                # Determine the event type based on the timestamp
                try:
                    (
                        event_type_id,
                        event_type_name,
                        period,
                    ) = _determine_event_type_from_timestamp(timestamp, match_context)

                    # Report the event
                    _report_smart_control_event(
                        match_context, event_type_id, event_type_name, period, choice
                    )
                    _display_current_events_table(match_context)

                except ValueError as e:
                    print(f"Error: {e}")
                    print(
                        "Please enter a valid timestamp corresponding to a period start or end."
                    )

            except ValueError:
                print(
                    "Invalid input. Please enter a valid number, timestamp (e.g., 45, 45+2), or option [1-2]."
                )


def report_staff_events_menu(match_context: MatchContext):
    """Menu for reporting staff member events"""
    while True:
        # Get current scores for display
        scores = match_context.scores

        # Create a more visually appealing header with match info
        print("\n" + "=" * 60)
        print(
            f"STAFF EVENTS - {match_context.team1_name} vs {match_context.team2_name}"
        )
        print(
            f"CURRENT SCORE: {match_context.team1_name} {scores.regular_time.home} - {scores.regular_time.away} {match_context.team2_name}"
        )
        print("=" * 60)

        # Staff event options with better formatting
        print("\nSelect a staff event to report:")
        print(
            f"1: {EVENT_EMOJIS['Coach Warning']} Team Official Action (warnings, cards)"
        )
        print(
            f"2: {EVENT_EMOJIS['Medical Staff Intervention']} Medical Staff Intervention"
        )
        print(f"\n  {MENU_EMOJIS['back']} Enter empty string to return to main menu")
        print("-" * 60)

        choice = input("Select option [1-2]: ")

        if choice == "":
            return
        if choice == "1":
            new_events = _report_team_official_action_event(match_context)
            if new_events is not None:
                match_context.match_events_json = new_events
            if match_context.match_events_json is not None:
                _display_current_events_table(match_context)
        elif choice == "2":
            print("\nMedical Staff Intervention reporting is not yet implemented.")
            print("This feature will be available in a future update.")
        else:
            print("Invalid option. Please try again.")


def report_results_menu(match_context: MatchContext):
    """Menu for reporting match results"""
    while True:
        # Get current scores for display
        scores = match_context.scores

        # Create a more visually appealing header with match info
        print("\n" + "=" * 60)
        print(
            f"MATCH RESULTS - {match_context.team1_name} vs {match_context.team2_name}"
        )

        print(
            f"CURRENT SCORE: {match_context.team1_name} {scores.regular_time.home} -"
            f"{scores.regular_time.away} {match_context.team2_name}"
        )
        print("=" * 60)

        # Results options with better formatting
        print("\nMatch result options:")
        print(f"  1: {MENU_EMOJIS['report_results']} Report final match results")
        print(f"\n  {MENU_EMOJIS['back']} Enter empty string to return to main menu")
        print("-" * 60)

        choice = input("Select option [1]: ")

        if choice == "":
            return
        if choice == "1":
            _report_match_results_interactively(match_context)
            # Simply continue in the loop, returning to the results menu
        else:
            print("Invalid option. Please try again.")


def _report_control_event_interactively(
    match_context: MatchContext, control_event_input: Optional[str] = None
):
    """Interactively reports control events (Period End, Game End) - Updated for API" \
    "format.
    """
    match_id = match_context.match_id
    team1_score = match_context.scores.regular_time.home
    team2_score = match_context.scores.regular_time.away

    # If control_event_input is not provided, ask for it
    if control_event_input is None:
        while True:  # Control event selection loop
            prompt_text = (
                "Report Control Event (1: Period End, 2: Game End, or empty string to"
                "go back):"
            )
            print(prompt_text, flush=True)
            control_event_input = input(prompt_text)

            if control_event_input == "":
                return
            if control_event_input in ["1", "2"]:
                break  # Valid input, proceed
            else:
                print(
                    "Invalid control event. Please enter 1, 2, or empty string to go"
                    "back."
                )

    # Process the control event
    if control_event_input == "1":  # Period End
        event_type_id = 32
        event_type_name = "Period End"
    elif control_event_input == "2":  # Game End
        event_type_id = 23
        event_type_name = "Game End"
    else:
        print("Invalid control event.")
        return

    period = 0
    match_minute = 0

    while True:  # Time input loop
        time_prompt_text = f"Enter time for {event_type_name} (e.g., 45, 45+2, 90+5): "
        print(time_prompt_text, flush=True)
        time_input = input(time_prompt_text)
        if time_input == "":
            return  # Allow going back if user enters empty string
        try:
            match_minute, period = _parse_minute_input(
                time_input,
                match_context.num_periods,
                match_context.period_length,
                match_context.num_extra_periods,
                match_context.extra_period_length,
            )
            break  # Time input is valid, exit time loop
        except ValueError as e:
            print(f"Invalid time input: {e}")
            continue  # Loop again for valid time input

    # Create the control event JSON in the correct API format
    control_event = {
        "matchhandelseid": 0,
        "matchid": match_id,
        "period": period,
        "matchminut": match_minute,
        "sekund": 0,
        "matchhandelsetypid": event_type_id,
        "matchlagid": 0,
        "spelareid": 0,
        "spelareid2": 0,
        "planpositionx": "-1",
        "planpositiony": "-1",
        "matchdeltagareid": 0,
        "matchdeltagareid2": 0,
        "fotbollstypId": 1,
        "relateradTillMatchhandelseID": 0,
        "hemmamal": team1_score,
        "bortamal": team2_score,
    }

    # Handle automatic period start and period end logic AND API reporting
    _add_control_event_with_implicit_events(
        control_event, match_context
    )  # Pass control_event and match_context

    print(f"{event_type_name} reported at minute {match_minute}, period {period}.")
    return  # No return value anymore


def _add_control_event_with_implicit_events(
    control_event: Dict[str, Any], match_context: MatchContext
) -> None:
    """Adds a control event, implicit period start/end events, and reports them to" \
    "API - Context-Aware - ITERATIVE & ORDERED.
    """
    event_type_id = control_event["matchhandelsetypid"]
    period = control_event["period"]
    match_minute = control_event["matchminut"]
    team1_score = control_event["hemmamal"]
    team2_score = control_event["bortamal"]
    api_client = match_context.api_client
    match_id = match_context.match_id  # Get match_id from context

    def _find_existing_event(
        event_type_id: int, period: int
    ) -> Optional[Dict[str, Any]]:
        """Find an existing event of the given type and period."""
        for event in match_context.match_events_json:
            # Check if the required keys exist in the event data
            if "matchhandelsetypid" not in event or "period" not in event:
                print(
                    f"Warning: Event missing required keys. Available keys: {list(event.keys())}"
                )
                continue

            if (
                event["matchhandelsetypid"] == event_type_id
                and event["period"] == period
            ):
                return dict(event)
        return None

    def _report_event_to_api(
        event_json: Dict[str, Any],
    ) -> Optional[List[Dict[str, Any]]]:
        action_type = None
        try:
            # Check if we're updating an existing event or creating a new one
            is_update = event_json["matchhandelseid"] != 0
            action_type = "updated" if is_update else "reported"

            api_response = api_client.report_match_event(event_json)
            if (
                api_response is not None
            ):  # Check if api_response is not None for success
                print(
                    f"API: Event type {event_json['matchhandelsetypid']} {action_type}"
                    "successfully."
                )
                # Use safe_fetch_json_list to ensure the response is a list of dictionaries
                # Cast the result to the expected return type
                result = safe_fetch_json_list(lambda x: x, api_response)
                # Convert to List[Dict[str, Any]]
                return [dict(item) for item in result] if result else None
            else:
                print(
                    f"API WARNING: Event type {event_json['matchhandelsetypid']} {action_type} - API acknowledged but no success response."
                )
                print(f"API WARNING: Response: {api_response}")

                return None  # Return None to indicate failure
        except Exception:
            print(
                f"API ERROR: Failed to {action_type} event type"
                "{event_json['matchhandelsetypid']} to API. Exception: {api_error}"
            )
            return None  # Return None to indicate failure

    if event_type_id == 32:  # Period End (32)
        # Check for existing Period Start (31) for the *current* period
        existing_period_start = _find_existing_event(31, period)
        if not existing_period_start:
            # No existing Period Start, create a new one
            period_start_minute = 1 + ((period - 1) * match_context.period_length)
            period_start_event = {
                "matchhandelseid": 0,  # 0 for new event
                "matchid": match_id,
                "period": period,
                "matchminut": period_start_minute,
                "sekund": 0,
                "matchhandelsetypid": 31,
                "matchlagid": 0,
                "spelareid": 0,
                "spelareid2": 0,
                "planpositionx": "-1",
                "planpositiony": "-1",
                "matchdeltagareid": 0,
                "matchdeltagareid2": 0,
                "fotbollstypId": 1,
                "relateradTillMatchhandelseID": 0,
                "hemmamal": team1_score,
                "bortamal": team2_score,
            }
            print(f"  Creating new Period Start event for period {period}")
            api_response_start = _report_event_to_api(period_start_event)
            if api_response_start is not None:
                match_context.match_events_json = api_response_start  # Update context
                print(
                    f"Context's match_events_json UPDATED with API response (Period Start Period {period})."
                )
            else:
                print(
                    f"WARNING: Period Start event (Period {period}) NOT reported to API! Context NOT updated for Period Start."
                )
        else:
            print(
                f"Found existing Period Start event for period {period} (ID: {existing_period_start['matchhandelseid']})"
            )

        # Check for existing Period End event
        existing_period_end = _find_existing_event(32, period)
        if existing_period_end:
            # Update existing Period End event
            print(
                f"Updating existing Period End event for period {period} (ID: {existing_period_end['matchhandelseid']})"
            )
            # Copy the control_event data but use the existing event ID
            updated_event = control_event.copy()
            updated_event["matchhandelseid"] = existing_period_end["matchhandelseid"]
            api_response_end = _report_event_to_api(updated_event)
        else:
            # Create new Period End event
            print(f"  Creating new Period End event for period {period}")
            api_response_end = _report_event_to_api(control_event)

        if api_response_end is not None:
            match_context.match_events_json = api_response_end  # Update context
            print(
                f"Context's match_events_json UPDATED with API response (Period End Period {period})."
            )
        else:
            print(
                f"WARNING: Period End event (Period {period}) NOT reported to API! Context NOT updated for Period End."
            )

    elif event_type_id == 23:  # Game End (23)
        # Check for existing Period End (32) for the *current* period
        existing_period_end = _find_existing_event(32, period)
        if not existing_period_end:
            # No existing Period End, create a new one
            period_end_event = {
                "matchhandelseid": 0,  # 0 for new event
                "matchid": match_id,
                "period": period,
                "matchminut": match_minute,
                "sekund": 0,
                "matchhandelsetypid": 32,
                "matchlagid": 0,
                "spelareid": 0,
                "spelareid2": 0,
                "planpositionx": "-1",
                "planpositiony": "-1",
                "matchdeltagareid": 0,
                "matchdeltagareid2": 0,
                "fotbollstypId": 1,
                "relateradTillMatchhandelseID" "hemmamal": team1_score,
                "bortamal": team2_score,
            }
            print(
                f"Creating new Period End event for period {period} (implicit with Game"
                "End)"
            )
            api_response_period_end = _report_event_to_api(period_end_event)
            if api_response_period_end is not None:
                match_context.match_events_json = (
                    api_response_period_end  # Update context
                )
                print(
                    f"Context's match_events_json UPDATED with API response (Implicit Period End Period {period} with Game End)."
                )
            else:
                print(
                    f"WARNING: Implicit Period End event (Period {period}, with Game End) NOT reported to API! Context NOT updated for implicit Period End."
                )
        else:
            print(
                f"Found existing Period End event for period {period} (ID: {existing_period_end['matchhandelseid']})"
            )

        # Check for existing Period Start (31) for the *current* period
        existing_period_start = _find_existing_event(31, period)
        if not existing_period_start:
            # No existing Period Start, create a new one
            period_start_minute = 1 + ((period - 1) * match_context.period_length)
            period_start_event = {
                "matchhandelseid": 0,  # 0 for new event
                "matchid": match_id,
                "period": period,
                "matchminut": period_start_minute,
                "sekund": 0,
                "matchhandelsetypid": 31,
                "matchlagid": 0,
                "spelareid": 0,
                "spelareid2": 0,
                "planpositionx": "-1",
                "planpositiony": "-1",
                "matchdeltagareid": 0,
                "matchdeltagareid2": 0,
                "fotbollstypId": 1,
                "relateradTillMatchhandelseID": 0,
                "hemmamal": team1_score,
                "bortamal": team2_score,
            }
            print(
                f"Creating new Period Start event for period {period} (implicit with Game End)"
            )
            api_response_start = _report_event_to_api(period_start_event)
            if api_response_start is not None:
                match_context.match_events_json = api_response_start  # Update context
                print(
                    f"Context's match_events_json UPDATED with API response (Period Start Period {period}, implicit with Game End)."
                )
            else:
                print(
                    f"WARNING: Implicit Period Start event (Period {period}, with Game End) NOT reported to API! Context NOT updated for implicit Period Start."
                )
        else:
            print(
                f"Found existing Period Start event for period {period} (ID: {existing_period_start['matchhandelseid']})"
            )

        # Check for existing Game End event
        existing_game_end = _find_existing_event(23, period)
        if existing_game_end:
            # Update existing Game End event
            print(
                f"Updating existing Game End event for period {period} (ID:"
                "{existing_game_end['matchhandelseid']})"
            )
            # Copy the control_event data but use the existing event ID
            updated_event = control_event.copy()
            updated_event["matchhandelseid"] = existing_game_end["matchhandelseid"]
            api_response_game_end = _report_event_to_api(updated_event)
        else:
            # Create new Game End event
            print(f"  Creating new Game End event for period {period}")
            api_response_game_end = _report_event_to_api(control_event)

        if api_response_game_end is not None:
            match_context.match_events_json = api_response_game_end  # Update context
            print(
                f"Context's match_events_json UPDATED with API response (Game End Period {period})."
            )
        else:
            print(
                f"WARNING: Game End event (Period {period}) NOT reported to API! Context NOT updated for Game End."
            )

    else:  # Period Start (31) - if we ever allow explicit Period Start input
        # Check for existing Period Start event
        existing_period_start = _find_existing_event(31, period)
        if existing_period_start:
            # Update existing Period Start event
            print(
                f"Updating existing Period Start event for period {period} (ID: {existing_period_start['matchhandelseid']})"
            )
            # Copy the control_event data but use the existing event ID
            updated_event = control_event.copy()
            updated_event["matchhandelseid"] = existing_period_start["matchhandelseid"]
            api_response_period_start = _report_event_to_api(updated_event)
        else:
            # Create new Period Start event
            print(f"  Creating new Period Start event for period {period}")
            period_start_event = control_event  # For Period Start, control_event is the period_start_event itself
            api_response_period_start = _report_event_to_api(period_start_event)

        if api_response_period_start is not None:
            match_context.match_events_json = (
                api_response_period_start  # Update context
            )
            print(
                f"Context's match_events_json UPDATED with API response (Period Start Period {period})."
            )
        else:
            print(
                f"WARNING: Period Start event (Period {period}) NOT reported to API! Context NOT updated for Period Start."
            )
            return


def _report_substitution_event(
    match_context: MatchContext,
    team_number: int,
    current_team_players_json: List[Dict[str, Any]],
    team1_score: int,
    team2_score: int,
) -> Optional[List[Dict[str, Any]]]:
    """Reports a substitution event based on user input."""
    api_client = match_context.api_client
    match_id = match_context.match_id
    team1_id = match_context.team1_id
    team2_id = match_context.team2_id
    num_periods = match_context.num_periods
    period_length = match_context.period_length
    num_extra_periods = match_context.num_extra_periods
    extra_period_length = match_context.extra_period_length

    jersey_number_in = input("Jersey number of player coming IN (substitute): ")
    jersey_number_out = input("Jersey number of player going OUT (being substituted): ")

    # Convert jersey numbers to integers
    try:
        jersey_number_in_int = int(jersey_number_in)
        jersey_number_out_int = int(jersey_number_out)
    except ValueError:
        print("Jersey numbers must be integers.")
        return None

    player_id_in = FogisDataParser.get_player_id_by_team_jersey(
        current_team_players_json, jersey_number_in_int
    )
    player_id_out = FogisDataParser.get_player_id_by_team_jersey(
        current_team_players_json, jersey_number_out_int
    )
    game_participant_id_in = FogisDataParser.get_matchdeltagareid_by_team_jersey(
        current_team_players_json, jersey_number_in_int
    )
    game_participant_id_out = FogisDataParser.get_matchdeltagareid_by_team_jersey(
        current_team_players_json, jersey_number_out_int
    )

    # Get player names if available
    player_name_in = "Unknown"
    player_name_out = "Unknown"
    team_name = (
        match_context.team1_name if team_number == 1 else match_context.team2_name
    )

    for player in current_team_players_json:
        # Check for player coming in
        if player.get("trojnummer") == jersey_number_in_int:
            if "namn" in player:
                player_name_in = player["namn"]
            elif "fornamn" in player and "efternamn" in player:
                player_name_in = f"{player['fornamn']} {player['efternamn']}"

        # Check for player going out
        if player.get("trojnummer") == jersey_number_out_int:
            if "namn" in player:
                player_name_out = player["namn"]
            elif "fornamn" in player and "efternamn" in player:
                player_name_out = f"{player['fornamn']} {player['efternamn']}"

    if not player_id_in or not player_id_out:
        print("Invalid jersey number(s). Players not found.")
        return None  # Indicate failure

    # Display confirmation of selected players
    print(
        f"\nSubstitution: {player_name_in} (#{jersey_number_in_int}) IN, {player_name_out} (#{jersey_number_out_int}) OUT for {team_name}"
    )

    minute_str = input(
        "Minute when substitution occurred (1-90, or '45+X' for stoppage time):"
    )

    try:
        minute, period = _parse_minute_input(
            minute_str,
            num_periods,
            period_length,
            num_extra_periods,
            extra_period_length,
        )
    except ValueError as e:
        print(e)
        return None  # Indicate failure

    game_team_id = team1_id if team_number == 1 else team2_id
    event_data = {
        "matchhandelseid": 0,
        "matchid": match_id,
        "period": period,
        "matchminut": minute,
        "sekund": 0,
        "matchhandelsetypid": 17,  # Substitution event type ID (17)
        "matchlagid": game_team_id,
        "spelareid": int(player_id_in),
        "spelareid2": int(player_id_out),
        "hemmamal": team1_score,
        "bortamal": team2_score,
        "planpositionx": "-1",
        "planpositiony": "-1",
        "matchdeltagareid": (
            int(game_participant_id_in) if game_participant_id_in else 0
        ),
        "matchdeltagareid2": (
            int(game_participant_id_out) if game_participant_id_out else 0
        ),
        "fotbollstypId": 1,
        "relateradTillMatchhandelseID": 0,
    }

    try:
        # Debug: Print the event data being sent to the API
        print("\nDEBUG - Sending substitution event data to API:")
        print(json.dumps(event_data, indent=2, ensure_ascii=False))

        report_response = api_client.report_match_event(event_data)

        # Debug: Print the API response
        print("\nDEBUG - API Response:")
        print(
            json.dumps(report_response, indent=2, ensure_ascii=False)
            if report_response
            else "None"
        )

        if report_response:
            print("\nMatch Event Report Response (Substitution):")
            print("Event Type: Substitution")
            print(json.dumps(report_response, indent=2, ensure_ascii=False))
            # Use safe API wrapper to ensure match_events_json is always a list of dictionaries
            match_events_json = safe_fetch_json_list(
                api_client.fetch_match_events_json, match_id
            )
            # Convert to List[Dict[str, Any]]
            return (
                [dict(item) for item in match_events_json]
                if match_events_json
                else None
            )
        return None
    except Exception as e:
        print("\nFailed to report substitution event.")
        print(f"DEBUG - Exception details: {type(e).__name__}: {str(e)}")
        return None  # Indicate failure


def _report_team_official_action_event(
    match_context: MatchContext,
) -> Optional[List[Dict[str, Any]]]:
    """Reports a team official action event based on user input."""
    api_client = match_context.api_client
    match_id = match_context.match_id

    team_official_id_str = input("Enter Team Official ID: ")
    lagrollid_str = input("Enter Team Official Role ID (Lagrollid): ")
    avvisadmatchminut_str = input("Enter Dismissal Minute (or 0 if no dismissal): ")
    avvisadlindrig_str = input("Minor Dismissal (yes/no): ").lower()
    avvisadgrov_str = input("Severe Dismissal (yes/no): ").lower()
    varnad_str = input("Caution/Warning (yes/no): ").lower()
    try:
        team_official_id = int(team_official_id_str) if team_official_id_str else 0
        lagrollid = int(lagrollid_str) if lagrollid_str else 0
        avvisadmatchminut = int(avvisadmatchminut_str) if avvisadmatchminut_str else 0
        avvisadlindrig = avvisadlindrig_str == "yes"
        avvisadgrov = avvisadgrov_str == "yes"
        varnad = varnad_str == "yes"
    except ValueError:
        print("Invalid input format for Team Official Action.")
        return None  # Indicate failure

    action_data = {
        "matchid": match_id,  # Required field
        "matchlagledareid": team_official_id,  # Required field
        "matchlagid": match_context.team1_id,  # Required field - using team1_id as default
        "matchlagledaretypid": 1,  # Required field - using 1 (Yellow Card) as default
        "matchminut": avvisadmatchminut,  # Optional field
        "lagrollid": lagrollid,
        "avvisadmatchminut": avvisadmatchminut,
        "avvisadlindrig": avvisadlindrig,
        "avvisadgrov": avvisadgrov,
        "varnad": varnad,
        "ansvarig": False,
    }

    try:
        # Debug: Print the action data being sent to the API
        print("\nDEBUG - Sending team official action data to API:")
        print(json.dumps(action_data, indent=2, ensure_ascii=False))

        report_response = api_client.report_team_official_action(action_data)

        # Debug: Print the API response
        print("\nDEBUG - API Response:")
        print(
            json.dumps(report_response, indent=2, ensure_ascii=False)
            if report_response
            else "None"
        )

        if report_response:
            print("\nTeam Official Action Report Response:")
            print("Event Type: Team Official Action")
            print(json.dumps(report_response, indent=2, ensure_ascii=False))
            # Use safe API wrapper to ensure match_events_json is always a list of dictionaries
            match_events_json = safe_fetch_json_list(
                api_client.fetch_match_events_json, match_id
            )
            # Convert to List[Dict[str, Any]]
            return (
                [dict(item) for item in match_events_json]
                if match_events_json
                else None
            )
        return None
    except Exception as e:
        print("\nFailed to report team official action.")
        print(f"DEBUG - Exception details: {type(e).__name__}: {str(e)}")
        return None  # Indicate failure


def _report_goal_with_smart_input(
    match_context: MatchContext,
    team_number: int,
    current_team_players_json: List[Dict[str, Any]],
    team1_score: int,
    team2_score: int,
) -> Optional[List[Dict[str, Any]]]:
    """Reports a goal event using smart input detection.

    This function implements the streamlined goal reporting system where:
    - If user enters a number → Record as regular goal by that player
    - If user enters a letter → Prompt for jersey number for that specific goal type
    """
    api_client = match_context.api_client
    match_id = match_context.match_id
    team1_id = match_context.team1_id
    team2_id = match_context.team2_id
    num_periods = match_context.num_periods
    period_length = match_context.period_length
    num_extra_periods = match_context.num_extra_periods
    extra_period_length = match_context.extra_period_length
    team_name = (
        match_context.team1_name if team_number == 1 else match_context.team2_name
    )

    # Define goal type codes with proper typing
    goal_type_codes: Dict[str, Dict[str, Union[int, str]]] = {
        "r": {"id": 6, "name": "Regular Goal"},
        "h": {"id": 39, "name": "Header Goal"},
        "c": {"id": 28, "name": "Corner Goal"},
        "f": {"id": 29, "name": "Free Kick Goal"},
        "o": {"id": 15, "name": "Own Goal"},
        "p": {"id": 14, "name": "Penalty Goal"},
    }

    # Display help text for the new input method
    print("\n" + "=" * 60)
    print(f"  GOAL REPORTING - {team_name}")
    print("=" * 60)
    print(
        "\nEnter jersey number for a regular goal, or one of these codes for special"
        "goal types:"
    )
    print("  r = Regular Goal (same as entering jersey number)")
    print("  h = Header Goal")
    print("  c = Corner Goal")
    print("  f = Free Kick Goal")
    print("  o = Own Goal")
    print("  p = Penalty Goal")
    print("\nExample: '10' for regular goal by player #10, or 'p' for penalty goal")
    print("-" * 60)

    # Get user input
    input_value = input("Enter jersey number or goal type code: ")

    if input_value == "":
        return None  # User cancelled

    # Determine if input is a jersey number or a goal type code
    event_type_id = None
    event_type_name = None
    jersey_number_int = None

    if input_value.isdigit():  # User entered a jersey number - regular goal
        jersey_number_int = int(input_value)
        event_type_id = 6  # Regular Goal
        event_type_name = "Regular Goal"
    elif input_value.lower() in goal_type_codes:  # User entered a goal type code
        goal_type = goal_type_codes[input_value.lower()]
        event_type_id = int(goal_type["id"])  # Explicit cast to int
        event_type_name = str(goal_type["name"])  # Explicit cast to str

        # For special goal types, prompt for jersey number
        jersey_input = input(f"Enter jersey number for {event_type_name}: ")
        if not jersey_input.isdigit():
            print("Jersey number must be an integer.")
            return None
        jersey_number_int = int(jersey_input)
    else:
        print(
            f"Invalid input: '{input_value}'. Please enter a jersey number or a valid"
            "goal type code."
        )
        return None

    # Validate jersey number
    player_id = FogisDataParser.get_player_id_by_team_jersey(
        current_team_players_json, jersey_number_int
    )
    game_participant_id = FogisDataParser.get_matchdeltagareid_by_team_jersey(
        current_team_players_json, jersey_number_int
    )

    # Get player name if available
    player_name = "Unknown"
    for player in current_team_players_json:
        if player.get("trojnummer") == jersey_number_int:
            # Try different possible name fields
            if "namn" in player:
                player_name = player["namn"]
            elif "fornamn" in player and "efternamn" in player:
                player_name = f"{player['fornamn']} {player['efternamn']}"
            break

    if not player_id:
        print(
            f"Player with jersey number {jersey_number_int} not found for {team_name}."
        )
        return None  # Indicate failure

    # Display confirmation of selected player
    print(
        f"\nSelected player: {player_name} (#{jersey_number_int}) for {event_type_name}"
    )

    # Get timestamp for the goal
    minute_str = input(
        f"Minute when goal by {player_name} (#{jersey_number_int}) occurred (1-90, or '45+X' for stoppage time): "
    )
    try:
        minute, period = _parse_minute_input(
            minute_str,
            num_periods,
            period_length,
            num_extra_periods,
            extra_period_length,
        )
    except ValueError as e:
        print(e)
        return None  # Indicate failure

    # Update score
    game_team_id = team1_id if team_number == 1 else team2_id
    if team_number == 1:
        team1_score += 1
    elif team_number == 2:
        team2_score += 1

    # Create event data
    event_data = {
        "matchhandelseid": 0,
        "matchid": match_id,
        "period": period,
        "matchminut": minute,
        "sekund": 0,
        "matchhandelsetypid": event_type_id,
        "matchlagid": game_team_id,
        "spelareid": int(player_id),
        "spelareid2": 0,
        "planpositionx": "-1",
        "planpositiony": "-1",
        "matchdeltagareid": int(game_participant_id) if game_participant_id else 0,
        "matchdeltagareid2": 0,
        "fotbollstypId": 1,
        "relateradTillMatchhandelseID": 0,
    }

    if team_number == 1:
        event_data["hemmamal"] = team1_score
        event_data["bortamal"] = team2_score
    elif team_number == 2:
        event_data["hemmamal"] = team1_score
        event_data["bortamal"] = team2_score

    # Report the event
    try:
        # Debug: Print the event data being sent to the API
        print("\nDEBUG - Sending event data to API:")
        print(json.dumps(event_data, indent=2, ensure_ascii=False))

        api_response = api_client.report_match_event(event_data)

        # Debug: Print the API response
        print("\nDEBUG - API Response:")
        print(
            json.dumps(api_response, indent=2, ensure_ascii=False)
            if api_response
            else "None"
        )

        if api_response is None:
            print(f"Error reporting {event_type_name} for player #{jersey_number_int}.")
            return None

        print(
            f"{event_type_name} reported for player #{jersey_number_int} at minute {minute}."
        )
        match_events_json: Optional[List[Dict[str, Any]]] = safe_fetch_json_list(
            api_client.fetch_match_events_json, match_id
        )
        return match_events_json
    except Exception as e:
        print(f"Error reporting goal: {e}")
        return None


def _report_player_event(
    match_context: MatchContext,
    team_number: int,
    selected_event_type: Dict[str, Any],
    current_team_players_json: List[Dict[str, Any]],
    team1_score: int,
    team2_score: int,
) -> Optional[List[Dict[str, Any]]]:
    """Reports a general player event (goal, card, etc.) based on user input."""
    api_client = match_context.api_client
    match_id = match_context.match_id
    team1_id = match_context.team1_id
    team2_id = match_context.team2_id
    num_periods = match_context.num_periods
    period_length = match_context.period_length
    num_extra_periods = match_context.num_extra_periods
    extra_period_length = match_context.extra_period_length
    event_type_id = list(EVENT_TYPES.keys())[
        list(EVENT_TYPES.values()).index(selected_event_type)
    ]  # Get numeric event_type_id from selected_event_type
    event_type_name = selected_event_type["name"]
    is_goal_event = selected_event_type.get("goal", False)

    jersey_number = input("Jersey number of player: ")
    try:
        jersey_number_int = int(jersey_number)
    except ValueError:
        print("Jersey number must be an integer.")
        return None

    player_id = FogisDataParser.get_player_id_by_team_jersey(
        current_team_players_json, jersey_number_int
    )
    game_participant_id = FogisDataParser.get_matchdeltagareid_by_team_jersey(
        current_team_players_json, jersey_number_int
    )

    # Get player name if available
    player_name = "Unknown"
    team_name = (
        match_context.team1_name if team_number == 1 else match_context.team2_name
    )
    for player in current_team_players_json:
        if player.get("trojnummer") == jersey_number_int:
            # Try different possible name fields
            if "namn" in player:
                player_name = player["namn"]
            elif "fornamn" in player and "efternamn" in player:
                player_name = f"{player['fornamn']} {player['efternamn']}"
            break

    if not player_id:
        print(f"Player with jersey number {jersey_number} not found for {team_name}.")
        return None  # Indicate failure

    # Display confirmation of selected player
    print(
        f"\nSelected player: {player_name} (#{jersey_number_int}) for {event_type_name}"
    )

    minute_str = input(
        f"Minute when {event_type_name} for {player_name} (#{jersey_number_int}) occurred (1-90, or '45+X' for stoppage time):"
    )
    try:
        minute, period = _parse_minute_input(
            minute_str,
            num_periods,
            period_length,
            num_extra_periods,
            extra_period_length,
        )
    except ValueError as e:
        print(e)
        return None  # Indicate failure

    game_team_id = team1_id if team_number == 1 else team2_id
    if is_goal_event:
        if team_number == 1:
            team1_score += 1
        elif team_number == 2:
            team2_score += 1

    event_data = {
        "matchhandelseid": 0,
        "matchid": match_id,
        "period": period,
        "matchminut": minute,
        "sekund": 0,
        "matchhandelsetypid": event_type_id,
        "matchlagid": game_team_id,
        "spelareid": int(player_id),
        "spelareid2": 0,
        "planpositionx": "-1",
        "planpositiony": "-1",
        "matchdeltagareid": int(game_participant_id) if game_participant_id else 0,
        "matchdeltagareid2": 0,
        "fotbollstypId": 1,
        "relateradTillMatchhandelseID": 0,
    }

    if team_number == 1:
        event_data["hemmamal"] = team1_score
        event_data["bortamal"] = team2_score
    elif team_number == 2:
        event_data["hemmamal"] = team1_score
        event_data["bortamal"] = team2_score

    try:
        # Debug: Print the event data being sent to the API
        print("\nDEBUG - Sending player event data to API:")
        print(json.dumps(event_data, indent=2, ensure_ascii=False))

        report_response = api_client.report_match_event(event_data)

        # Debug: Print the API response
        print("\nDEBUG - API Response:")
        print(
            json.dumps(report_response, indent=2, ensure_ascii=False)
            if report_response
            else "None"
        )

        if report_response:
            print("\nMatch Event Report Response:")
            print(f"Event Type: {event_type_name}")
            print(json.dumps(report_response, indent=2, ensure_ascii=False))
            # Use safe API wrapper to ensure match_events_json is always a list of dictionaries
            match_events_json = safe_fetch_json_list(
                api_client.fetch_match_events_json, match_id
            )
            # Convert to List[Dict[str, Any]]
            return (
                [dict(item) for item in match_events_json]
                if match_events_json
                else None
            )
        return None
    except Exception as e:
        print("\nFailed to report match event.")
        print(f"DEBUG - Exception details: {type(e).__name__}: {str(e)}")
        return None  # Indicate failure


def _handle_clear_events(match_context: MatchContext) -> List[Dict[str, Any]]:
    """Clears all match events and fetches the updated event list."""
    api_client = match_context.api_client
    match_id = match_context.match_id
    api_client.clear_match_events(match_id)
    # Use safe API wrapper to ensure match_events_json is always a list of dictionaries
    match_events_json = safe_fetch_json_list(
        api_client.fetch_match_events_json, match_id
    )
    print("All match events cleared.")
    return cast(List[Dict[str, Any]], match_events_json)  # Return with proper type


def _display_current_events_table(match_context: MatchContext):
    """Displays the current match events table with enhanced formatting."""
    scores: Scores = FogisDataParser.calculate_scores(match_context)
    team1_score = scores.regular_time.home
    team2_score = scores.regular_time.away
    halftime_score_team1 = scores.halftime.home
    halftime_score_team2 = scores.halftime.away
    match_events_json = match_context.match_events_json

    # Create a more visually appealing header
    print("\n" + "=" * 60)
    print(
        f"MATCH EVENTS SUMMARY - {match_context.team1_name} vs {match_context.team2_name}"
    )
    print(
        f"CURRENT SCORE: {match_context.team1_name} {team1_score} - {team2_score} {match_context.team2_name}"
    )
    if halftime_score_team1 is not None and halftime_score_team2 is not None:
        print(
            f"HALFTIME SCORE: {match_context.team1_name} {halftime_score_team1} - {halftime_score_team2} {match_context.team2_name}"
        )
    print("=" * 60)

    formatter = MatchEventTableFormatter(
        EVENT_TYPES,
        match_context.team1_name,
        match_context.team2_name,
        match_context.team1_id,
        match_context.team2_id,
    )
    table_string = formatter.format_structured_table(
        match_events_json,
        match_context.team1_players_json,
        match_context.team2_players_json,
        team1_score,
        team2_score,
        halftime_score_team1,
        halftime_score_team2,
    )
    print(table_string)
    print("-" * 60)


def _get_event_details_from_input(
    team_number_input, team1_players_json, team2_players_json, event_category=None
):
    """Gets event details from user input, including team number, event type, etc."""
    if team_number_input.lower() == "done" or team_number_input.lower() == "clear":
        return (
            None,
            None,
            None,
            None,
            None,
            None,
        )  # Signal to caller that input is 'done' or 'clear'

    try:
        team_number = int(team_number_input)
        if team_number not in [1, 2]:
            print("Invalid team number. Please enter 1 or 2.")
            return None, None, None, None, None, None  # Indicate invalid input

        # If event_category is provided, use it to filter event types
        if event_category:
            if event_category == "2":  # Cards
                print("\nSelect Card Type:")
                for event_type_id, event_type in EVENT_TYPES.items():
                    if (
                        not event_type.get("control_event")
                        and event_type_id is not None
                        and "Card" in event_type["name"]
                    ):
                        print(f"{event_type_id}: {event_type['name']}")

                # Get card type selection directly instead of falling through to general menu
                event_choice_str = input("Enter card type number:")

                if event_choice_str.isdigit():
                    event_choice = int(event_choice_str)
                    if (
                        event_choice in EVENT_TYPES
                        and not EVENT_TYPES[event_choice].get("control_event")
                        and "Card" in EVENT_TYPES[event_choice]["name"]
                    ):
                        selected_event_type = EVENT_TYPES[event_choice]
                        event_type_id = event_choice
                        event_type_name = selected_event_type["name"]
                        is_goal_event = selected_event_type.get("goal", False)
                        current_team_players_json = (
                            team1_players_json
                            if team_number == 1
                            else team2_players_json
                        )
                        return (
                            team_number,
                            selected_event_type,
                            event_type_id,
                            event_type_name,
                            is_goal_event,
                            current_team_players_json,
                        )
                    else:
                        print("Invalid card type selected.")
                        return None, None, None, None, None, None
                else:
                    print("Invalid input. Please enter a number for card type.")
                    return None, None, None, None, None, None

            elif event_category == "3":  # Substitution
                print("\nSubstitution Selected")
                event_choice_str = "17"  # Hardcode to Substitution event type
                event_choice = int(event_choice_str)
                selected_event_type = EVENT_TYPES[event_choice]
                event_type_id = event_choice
                event_type_name = selected_event_type["name"]
                is_goal_event = selected_event_type.get("goal", False)
                current_team_players_json = (
                    team1_players_json if team_number == 1 else team2_players_json
                )
                return (
                    team_number,
                    selected_event_type,
                    event_type_id,
                    event_type_name,
                    is_goal_event,
                    current_team_players_json,
                )
            if event_category == "4":  # Team Official Action
                # Handle Team Official Action
                event_choice_str = ""
                for event_id, event_type in EVENT_TYPES.items():
                    if event_type.get("name") == "Team Official Action":
                        event_choice_str = str(event_id)
                        break
                if event_choice_str:
                    event_choice = int(event_choice_str)
                    selected_event_type = EVENT_TYPES[event_choice]
                    event_type_id = event_choice
                    event_type_name = selected_event_type["name"]
                    is_goal_event = selected_event_type.get("goal", False)
                    current_team_players_json = (
                        team1_players_json if team_number == 1 else team2_players_json
                    )
                    return (
                        team_number,
                        selected_event_type,
                        event_type_id,
                        event_type_name,
                        is_goal_event,
                        current_team_players_json,
                    )
                else:
                    print("Team Official Action event type not found.")
                    return None, None, None, None, None, None

        # If no specific category handling above, or no category specified, show all event types
        if not event_category or event_category not in ["2", "3", "4"]:
            print("\nSelect Event Type:")
            for event_type_id, event_type in EVENT_TYPES.items():
                if not event_type.get("control_event") and event_type_id is not None:
                    print(f"{event_type_id}: {event_type['name']}")

        # Get event type from user
        event_choice_str = input("Enter event type number:")

        if event_choice_str.isdigit():
            event_choice = int(event_choice_str)
            if event_choice in EVENT_TYPES and not EVENT_TYPES[event_choice].get(
                "control_event"
            ):  # Check if numerical input is valid KEY and NOT a control event
                selected_event_type = EVENT_TYPES[event_choice]
                event_type_id = (
                    event_choice  # Use numerical key directly as event_type_id
                )
                event_type_name = selected_event_type["name"]
                is_goal_event = selected_event_type.get("goal", False)
                current_team_players_json = (
                    team1_players_json if team_number == 1 else team2_players_json
                )
                return (
                    team_number,
                    selected_event_type,
                    event_type_id,
                    event_type_name,
                    is_goal_event,
                    current_team_players_json,
                )
            else:
                print("Invalid event type number selected.")
                return None, None, None, None, None, None
        else:
            print("Invalid input. Please enter a number for event type.")
            return None, None, None, None, None, None  # Indicate invalid input

    except ValueError:
        print("Invalid input. Please enter 1, 2, 'done', or 'clear'.")
        return None, None, None, None, None, None  # Indicate invalid input


def _report_match_results_interactively(match_context: MatchContext):
    """Interactively reports match results and marks reporting finished.
    Uses MatchContext for data and API client.
    Verifies reported results against API data.
    """
    selected_match = match_context.selected_match
    team1_name = match_context.team1_name
    team2_name = match_context.team2_name
    match_id = selected_match["matchid"]

    reported_scores: Scores = (
        match_context.scores
    )  # Get calculated Scores object from context

    print("\n--- Match Result Reporting ---")

    (
        halftime_score_team1_input,
        halftime_score_team2_input,
        fulltime_score_team1_input,
        fulltime_score_team2_input,
    ) = _get_score_input_from_user(
        reported_scores.halftime.home,
        reported_scores.halftime.away,
        team1_name,
        team2_name,
        reported_scores.regular_time.home,
        reported_scores.regular_time.away,
    )
    if halftime_score_team1_input is None:  # Input error in scores
        return

    result_data = {
        "matchresultatListaJSON": [
            {
                "matchid": match_id,
                "matchresultattypid": 1,  # Full time
                "matchlag1mal": fulltime_score_team1_input,
                "matchlag2mal": fulltime_score_team2_input,
                "wo": False,
                "ow": False,
                "ww": False,
            },
            {
                "matchid": match_id,
                "matchresultattypid": 2,  # Half-time
                "matchlag1mal": halftime_score_team1_input,
                "matchlag2mal": halftime_score_team2_input,
                "wo": False,
                "ow": False,
                "ww": False,
            },
        ]
    }

    api_client = match_context.api_client
    try:
        api_client.report_match_result(result_data)  # Report results to API
        # result_response is expected to be None or null, so we don't check it directly

        fetched_scores = _verify_match_results(
            match_context, reported_scores
        )  # Verify and get fetched scores
        if fetched_scores is None:
            fetched_scores = Scores()  # Use default scores if verification fails
        if (
            fetched_scores
        ):  # Verification successful (fetched_scores is a Scores object)
            print("\nMatch Result Report Response: (API acknowledged)")

            print(
                "Match result reporting verified successfully! Fetched scores match"
                "reported scores."
            )
            # Removed call to _mark_reporting_finished_with_error_handling
            # This feature is implemented but not enabled to avoid unexpected API calls

            # --- Example of accessing and displaying fetched scores (optional) ---
            # print("\nFetched Scores from API:")
            # print(f"  Full Time: {team1_name} {fetched_scores.regular_time.home} - {fetched_scores.regular_time.away} {team2_name}")
            # print(f"  Halftime:  {team1_name} {fetched_scores.halftime.home} - {fetched_scores.halftime.away} {team2_name}")

        else:  # verify_match_results returned None (verification failed)
            print("\nMatch Result Report Response: (API acknowledged)")

            print(
                "\nERROR: Match result verification failed. Please check reported"
                "scores in FOGIS."
            )

    except Exception as e:  # Catch exceptions during API call
        print(f"\nERROR: Failed to report match results to API. Exception: {e}")
        print("Match result reporting and verification FAILED.")

    print("\n--- Match Result Reporting finished ---")
    return  # Return to report_results_menu


def _get_score_input_from_user(
    halftime_score_team1,
    halftime_score_team2,
    team1_name,
    team2_name,
    team1_score,
    team2_score,
):
    """Gets score input from the user for halftime and fulltime scores.

    Provides an option to accept all calculated scores at once.

    Args:
        halftime_score_team1: Calculated halftime score for team 1
        halftime_score_team2: Calculated halftime score for team 2
        team1_name: Name of team 1
        team2_name: Name of team 2
        team1_score: Calculated fulltime score for team 1
        team2_score: Calculated fulltime score for team 2

    Returns:
        Tuple of (halftime_score_team1, halftime_score_team2, fulltime_score_team1, fulltime_score_team2)
        or (None, None, None, None) if there was an input error
    """
    # Display calculated scores for reference
    print("\nCalculated scores:\n")
    print(
        f"  Halftime: {team1_name} {halftime_score_team1} - {halftime_score_team2} {team2_name}"
    )
    print(f"  Fulltime: {team1_name} {team1_score} - {team2_score} {team2_name}")

    # Ask if user wants to accept all calculated scores at once
    accept_all = input(
        "\nAccept all calculated scores? (y/yes to accept all, n/no for individual input): "
    )

    if accept_all.lower() in ["y", "yes"]:
        print("Using all calculated scores.")
        return halftime_score_team1, halftime_score_team2, team1_score, team2_score

    # If user doesn't want to accept all scores at once, proceed with individual input
    print("\nEnter scores individually (press Enter to use calculated score):")
    halftime_score_team1_input = input(
        f"  Halftime score for {team1_name} [{halftime_score_team1}]: "
    ) or str(halftime_score_team1)
    halftime_score_team2_input = input(
        f"  Halftime score for {team2_name} [{halftime_score_team2}]: "
    ) or str(halftime_score_team2)
    fulltime_score_team1_str = input(
        f"  Fulltime score for {team1_name} [{team1_score}]: "
    ) or str(team1_score)
    fulltime_score_team2_str = input(
        f"  Fulltime score for {team2_name} [{team2_score}]: "
    ) or str(team2_score)

    try:
        halftime_score_team1 = int(halftime_score_team1_input)
        halftime_score_team2 = int(halftime_score_team2_input)
        fulltime_score_team1 = int(fulltime_score_team1_str)
        fulltime_score_team2 = int(fulltime_score_team2_str)
        return (
            halftime_score_team1,
            halftime_score_team2,
            fulltime_score_team1,
            fulltime_score_team2,
        )
    except ValueError:
        print("Invalid score format. Please enter numbers only.")
        return None, None, None, None  # Indicate input error


def _mark_reporting_finished_with_error_handling(match_context: MatchContext):
    """Prompts for confirmation and marks match reporting as finished with robust
    error handling. Checks for the 'matchrapportgodkandavdomare' property to verify
    completion rather than displaying the entire match object.
    """
    # --- Prompt before marking reporting finished ---
    while True:  # Loop until valid input
        confirm_finished = input("\nMark match reporting as finished now? (yes/no):")

        if confirm_finished == "yes":
            break  # Proceed to mark finished
        elif confirm_finished == "no":
            print("Skipping 'Mark Reporting Finished' for now.")
            return
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")
            return

    api_client = match_context.api_client
    match_id = match_context.match_id

    # --- Robust Error Handling for Mark Reporting Finished ---
    try:
        finished_response = api_client.mark_reporting_finished(
            match_id
        )  # Call mark_reporting_finished
        if finished_response:
            # Check for the matchrapportgodkandavdomare property to verify completion
            if "matchrapportgodkandavdomare" in finished_response:
                print("\nMatch Reporting Marked as Finished Successfully!")
                print(
                    f"Referee confirmation status: {finished_response['matchrapportgodkandavdomare']}"
                )
            else:
                print("\nMatch Reporting Marked as Finished Successfully!")
                print("(No referee confirmation status available in the response)")
        else:
            print(
                "\nWarning: Failed to mark match reporting as finished (No response "
                "from API)."
            )
    except Exception as e:  # Catch broad exception for robustness
        print("\nERROR marking match reporting as finished!")
        print(f"Exception details: {e}")  # Print exception details for debugging
        api_error_message = getattr(
            e, "response", getattr(e, "message", "No API error message available")
        )  # Try to extract API error, handle different exception types
        print(f"API Error (if available): {api_error_message}")

        print("Please check FOGIS manually or try again later.")  # User guidance
    # --- END Robust Error Handling for Mark Reporting Finished ---


def _verify_match_results(
    match_context: MatchContext,  # Accept the entire MatchContext object
    reported_scores: Scores,  # Still accept reported_scores as Scores object
) -> Optional[Scores]:
    """Verifies reported match results by fetching from API using MatchContext.
    Compares fetched results to reported_scores.
    Returns fetched Scores object if verification successful, None otherwise.
    """
    api_client = match_context.api_client  # Get api_client from context
    match_id = match_context.match_id  # Get match_id from context

    try:
        fetched_result_json_list = api_client.fetch_match_result_json(match_id)
        if not fetched_result_json_list:
            print("Warning: No match result data fetched from API for verification.")
            return None

        fetched_scores = Scores()

        for result in fetched_result_json_list:
            if result["matchresultattypid"] == 2:  # Halftime result
                fetched_scores.halftime = Score(
                    home=result["matchlag1mal"], away=result["matchlag2mal"]
                )
            elif result["matchresultattypid"] == 1:  # Fulltime result
                fetched_scores.regular_time = Score(
                    home=result["matchlag1mal"], away=result["matchlag2mal"]
                )

        # Check if we have both halftime and fulltime scores
        missing_scores = (
            fetched_scores.halftime is None or fetched_scores.regular_time is None
        )
        if (
            missing_scores
        ):  # This condition can be true if the API response is incomplete
            print(
                "ERROR: Could not find both halftime and fulltime results in API"
                "response."
            )
            return None

        # --- Comparison (no change here) ---
        halftime_match = (
            fetched_scores.halftime.home == reported_scores.halftime.home
            and fetched_scores.halftime.away == reported_scores.halftime.away
        )
        fulltime_match = (
            fetched_scores.regular_time.home == reported_scores.regular_time.home
            and fetched_scores.regular_time.away == reported_scores.regular_time.away
        )

        if halftime_match and fulltime_match:
            print("Match result verification successful: Scores match API data.")
            return fetched_scores
        else:
            print(
                "ERROR: Match result verification failed. Scores DO NOT match API data!"
            )

            print(
                f"Reported Halftime: {reported_scores.halftime.home}-{reported_scores.halftime.away}, Fetched Halftime: {fetched_scores.halftime.home}-{fetched_scores.halftime.away}"
            )
            print(
                f"Reported Fulltime: {reported_scores.regular_time.home}-{reported_scores.regular_time.away}, Fetched Fulltime: {fetched_scores.regular_time.home}-{fetched_scores.regular_time.away}"
            )
            return None

    except Exception as e:
        print(f"Exception during match result verification: {e}")
        return None


def main():
    """Main function to orchestrate match reporting process."""
    # Display welcome banner
    print("\n" + "=" * 60)
    print("  FOGIS MATCH REPORTER")
    print("  A tool for reporting match events to the FOGIS system")
    print("=" * 60)

    # Check for credentials
    fogis_username = os.environ.get("FOGIS_USERNAME")
    fogis_password = os.environ.get("FOGIS_PASSWORD")

    if not fogis_username or not fogis_password:
        print(
            "\nError: FOGIS_USERNAME and FOGIS_PASSWORD environment variables must be set."
        )
        print("Please set these variables and try again.")
        return

    print("\nAttempting to log in to FOGIS...")
    api_client = FogisApiClient(fogis_username, fogis_password)
    try:
        if not api_client.login():
            print("Login failed. Please check your credentials and try again.")
            return
        print("Login successful! Welcome to the FOGIS Match Reporter.")

    except FogisLoginError as e:
        print(f"Login Error: {e}")
        print("Please check your credentials and try again.")
        return

    while True:  # Main loop to allow returning to match selection
        print("\nFetching available matches...")
        matches = api_client.fetch_matches_list_json()
        if not matches:
            print(
                "Could not fetch match list. The API may be unavailable or there might"
                "be no matches to report."
            )
            return

        print(f"Found {len(matches)} matches available for reporting.")
        selected_match = select_match_interactively(
            matches
        )  # Use new function for match selection
        if not selected_match:
            print("\nThank you for using FOGIS Match Reporter. Goodbye!")
            return  # Exit if no match selected or user chose to exit

        match_id = selected_match["matchid"]
        team1_name = selected_match["lag1namn"]
        team2_name = selected_match["lag2namn"]
        team1_id = selected_match["matchlag1id"]
        team2_id = selected_match["matchlag2id"]
        num_periods = selected_match["antalhalvlekar"]
        period_length = selected_match["tidperhalvlek"]
        num_extra_periods = selected_match["antalforlangningsperioder"]
        extra_period_length = selected_match["tidperforlangningsperiod"]

        print(f"\nSelected Match: {selected_match['label']}")
        print(f"Match ID: {match_id}")
        print(f"Team 1: {team1_name} (ID: {team1_id})")
        print(f"Team 2: {team2_name} (ID: {team2_id})")
        print(f"Number of Periods: {num_periods}")
        print(f"Period Length: {period_length} minutes")
        print(f"Number of Extra Periods: {num_extra_periods}")
        print(f"Extra Period Length: {extra_period_length} minutes")

        # Use safe API wrapper to ensure all JSON responses are always lists of dictionaries
        team1_players_json = safe_fetch_json_list(
            api_client.fetch_team_players_json, team1_id
        )
        team2_players_json = safe_fetch_json_list(
            api_client.fetch_team_players_json, team2_id
        )
        team1_officials_json = safe_fetch_json_list(
            api_client.fetch_team_officials_json, team1_id
        )
        team2_officials_json = safe_fetch_json_list(
            api_client.fetch_team_officials_json, team2_id
        )
        # Use safe API wrapper to ensure match_events_json is always a list of dictionaries
        match_events_json = safe_fetch_json_list(
            api_client.fetch_match_events_json, match_id
        )

        fetch_errors = False  # Flag to track fetch failures

        if team1_players_json is None:  # Check for None explicitly - FETCH FAILURE
            print("\nError: Failed to fetch Team 1 players from API.")

            fetch_errors = True  # Set fetch_errors flag
        elif (
            not team1_players_json
        ):  # Check for empty list - VALID EMPTY RESPONSE (not an error)
            print("\nWarning: Team 1 players list is empty.")  # Warning, not an error

        if team2_players_json is None:  # Check for None explicitly - FETCH FAILURE
            print("\nError: Failed to fetch Team 2 players from API.")

            fetch_errors = True  # Set fetch_errors flag
        elif (
            not team2_players_json
        ):  # Check for empty list - VALID EMPTY RESPONSE (not an error)
            print("\nWarning: Team 2 players list is empty.")  # Warning, not an error

        if team1_officials_json is None:  # Check for None explicitly - FETCH FAILURE
            print("\nError: Failed to fetch Team 1 officials from API.")

            fetch_errors = True  # Set fetch_errors flag
        elif (
            not team1_officials_json
        ):  # Check for empty list - VALID EMPTY RESPONSE (not an error)
            print("\nWarning: Team 1 officials list is empty.")  # Warning, not an error

        if team2_officials_json is None:  # Check for None explicitly - FETCH FAILURE
            print("\nError: Failed to fetch Team 2 officials from API.")

            fetch_errors = True  # Set fetch_errors flag
        elif (
            not team2_officials_json
        ):  # Check for empty list - VALID EMPTY RESPONSE (not an error)
            print("\nWarning: Team 2 officials list is empty.")  # Warning, not an error

        if match_events_json is None:  # Check for None explicitly - FETCH FAILURE
            print("\nError: Failed to fetch Match Events from API.")

            fetch_errors = True  # Set fetch_errors flag
        # No need to check for empty match_events_json list - empty list is valid

        if (
            not fetch_errors
        ):  # Check the fetch_errors flag instead of combined fetch_success
            match_context = MatchContext(
                api_client=api_client,
                selected_match=selected_match,
                team1_players_json=team1_players_json,
                team2_players_json=team2_players_json,
                match_events_json=match_events_json,
                num_periods=num_periods,
                period_length=period_length,
                num_extra_periods=num_extra_periods,
                extra_period_length=extra_period_length,
                team1_name=team1_name,
                team2_name=team2_name,
                team1_id=team1_id,
                team2_id=team2_id,
                match_id=match_id,
            )

            print("\nTeam Sheets and Match Events Fetched Successfully (or are empty)!")

            # --- Display event table immediately after match selection ---
            formatter = MatchEventTableFormatter(
                EVENT_TYPES, team1_name, team2_name, team1_id, team2_id
            )  # Instantiate formatter

            scores: Scores = FogisDataParser.calculate_scores(match_context)
            team1_score = scores.regular_time.home
            team2_score = scores.regular_time.away
            halftime_score_team1 = scores.halftime.home
            halftime_score_team2 = scores.halftime.away

            table_string = formatter.format_structured_table(
                match_events_json,
                team1_players_json,
                team2_players_json,
                team1_score,
                team2_score,
                halftime_score_team1,
                halftime_score_team2,
            )
            print("\n--- Current Match Events ---")
            print(table_string)
            # --- End event table printing ---

            # Use the new main menu instead of directly calling reporting functions
            display_main_menu(match_context)

        else:  # If fetch_errors flag is True (any fetch failed)
            print(
                "\nFailed to fetch team sheets or match events for one or more"
                "teams due to API errors."
            )  # More accurate error message
            continue  # Go back to match selection

        # Ask if user wants to select another match with better formatting
        print("\n" + "-" * 60)
        print("  Would you like to select another match?")
        print("-" * 60)
        another = input("Select another match? (y/n): ")
        if another.lower() != "y":
            print("\nThank you for using FOGIS Match Reporter. Goodbye!")
            break


if __name__ == "__main__":
    main()
