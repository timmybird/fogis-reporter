"""Assertions for UI testing.

This module provides custom assertions for UI testing.
"""

import re
from typing import List, Pattern, Union

from .cli_runner import CLIResult


def assert_output_contains(
    result: CLIResult, expected: Union[str, List[str], Pattern]
) -> None:
    """Assert that the output contains the expected string or pattern.

    Args:
        result: The CLI result
        expected: The expected string, list of strings, or pattern

    Raises:
        AssertionError: If the output does not contain the expected string or pattern
    """
    if isinstance(expected, str):
        assert (
            expected in result.stdout
        ), f"Expected {expected!r} in output, but got {result.stdout!r}"
    elif isinstance(expected, list):
        for item in expected:
            assert (
                item in result.stdout
            ), f"Expected {item!r} in output, but got {result.stdout!r}"
    elif isinstance(expected, Pattern):
        assert expected.search(
            result.stdout
        ), f"Expected pattern {expected.pattern!r} in output, but got {result.stdout!r}"
    else:
        raise TypeError(
            f"Expected must be a string, list of strings, or pattern, but got {type(expected)}"
        )


def assert_output_matches(result: CLIResult, pattern: Union[str, Pattern]) -> None:
    """Assert that the output matches the expected pattern.

    Args:
        result: The CLI result
        pattern: The expected pattern

    Raises:
        AssertionError: If the output does not match the expected pattern
    """
    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    assert pattern.search(
        result.stdout
    ), f"Expected pattern {pattern.pattern!r} in output, but got {result.stdout!r}"


def assert_exit_code(result: CLIResult, expected: int) -> None:
    """Assert that the exit code is as expected.

    Args:
        result: The CLI result
        expected: The expected exit code

    Raises:
        AssertionError: If the exit code is not as expected
    """
    assert (
        result.exit_code == expected
    ), f"Expected exit code {expected}, but got {result.exit_code}"


def assert_success(result: CLIResult) -> None:
    """Assert that the command succeeded.

    Args:
        result: The CLI result

    Raises:
        AssertionError: If the command did not succeed
    """
    assert_exit_code(result, 0)


def assert_failure(result: CLIResult) -> None:
    """Assert that the command failed.

    Args:
        result: The CLI result

    Raises:
        AssertionError: If the command did not fail
    """
    assert result.exit_code != 0, f"Expected non-zero exit code, but got {result.exit_code}"


def assert_menu_contains(result: CLIResult, menu_title: str, options: List[str]) -> None:
    """Assert that the output contains a menu with the given title and options.

    Args:
        result: The CLI result
        menu_title: The menu title
        options: The menu options

    Raises:
        AssertionError: If the output does not contain the expected menu
    """
    assert (
        menu_title in result.stdout
    ), f"Expected menu title {menu_title!r} in output, but got {result.stdout!r}"

    for option in options:
        assert (
            option in result.stdout
        ), f"Expected menu option {option!r} in output, but got {result.stdout!r}"
