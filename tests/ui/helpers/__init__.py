"""Helpers for UI testing."""

from .assertions import (
    assert_exit_code,
    assert_failure,
    assert_menu_contains,
    assert_output_contains,
    assert_output_matches,
    assert_success,
)
from .cli_runner import CLIResult, CLIRunner
from .test_data import (
    create_test_card_event,
    create_test_control_event,
    create_test_goal_event,
    create_test_match,
    create_test_match_result,
    create_test_player,
    create_test_substitution_event,
    create_test_team_players,
)

__all__ = [
    "CLIRunner",
    "CLIResult",
    "assert_output_contains",
    "assert_output_matches",
    "assert_exit_code",
    "assert_success",
    "assert_failure",
    "assert_menu_contains",
    "create_test_match",
    "create_test_player",
    "create_test_team_players",
    "create_test_goal_event",
    "create_test_card_event",
    "create_test_substitution_event",
    "create_test_control_event",
    "create_test_match_result",
]
