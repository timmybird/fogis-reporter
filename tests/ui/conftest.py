"""Test fixtures for UI testing.

This module provides fixtures for UI testing, including a mock server fixture.
"""

import os
import signal
import socket
import subprocess
from typing import Generator, Optional

import pytest
from tests.ui.helpers.cli_runner import CLIRunner

# Default port for the mock server
DEFAULT_MOCK_SERVER_PORT = 8080


def is_port_in_use(port: int) -> bool:
    """Check if a port is in use.

    Args:
        port: The port to check

    Returns:
        True if the port is in use, False otherwise
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def find_available_port(start_port: int = DEFAULT_MOCK_SERVER_PORT) -> int:
    """Find an available port starting from the given port.

    Args:
        start_port: The port to start checking from

    Returns:
        An available port
    """
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port


class MockServer:
    """Mock server for testing.

    This class manages a mock server process for testing.
    """

    def __init__(self, port: int = DEFAULT_MOCK_SERVER_PORT):
        """Initialize the mock server.

        Args:
            port: The port to run the mock server on
        """
        self.port = port
        self.process: Optional[subprocess.Popen] = None

    def start(self) -> None:
        """Start the mock server."""
        # This is a placeholder for the actual mock server start command
        # When the mock server is available as a package, this will be updated
        # For now, we'll just print a message
        print(f"Mock server would start on port {self.port}")
        # Example of how this would work with a real mock server:
        # self.process = subprocess.Popen(
        #     [
        #         "python", "-m", "fogis_api_client.mock_server",
        #         "--port", str(self.port)
        #     ],
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     preexec_fn=os.setsid
        # )
        # Wait for the server to start
        # time.sleep(1)

    def stop(self) -> None:
        """Stop the mock server."""
        if self.process:
            # Kill the process group
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            self.process = None
        print("Mock server would stop")

    def add_valid_credentials(self, username: str, password: str) -> None:
        """Add valid credentials to the mock server.

        Args:
            username: The username to add
            password: The password to add
        """
        # This is a placeholder for the actual implementation
        print(f"Would add credentials: {username}:{password}")

    def add_match(self, match_data: dict) -> None:
        """Add a match to the mock server.

        Args:
            match_data: The match data to add
        """
        # This is a placeholder for the actual implementation
        print(f"Would add match: {match_data}")

    def add_team_players(self, team_id: int, players_data: list) -> None:
        """Add team players to the mock server.

        Args:
            team_id: The team ID
            players_data: The players data to add
        """
        # This is a placeholder for the actual implementation
        print(f"Would add players for team {team_id}: {players_data}")

    def add_match_events(self, match_id: int, events_data: list) -> None:
        """Add match events to the mock server.

        Args:
            match_id: The match ID
            events_data: The events data to add
        """
        # This is a placeholder for the actual implementation
        print(f"Would add events for match {match_id}: {events_data}")

    def reset(self) -> None:
        """Reset the mock server data."""
        # This is a placeholder for the actual implementation
        print("Would reset mock server data")


@pytest.fixture
def mock_server() -> Generator[MockServer, None, None]:
    """Fixture that provides a mock server for testing.

    This fixture starts a mock server before the test and stops it after the test.

    Yields:
        A MockServer instance
    """
    # Find an available port
    port = find_available_port()

    # Create and start the mock server
    server = MockServer(port)
    server.start()

    try:
        yield server
    finally:
        server.stop()


@pytest.fixture
def cli_runner(mock_server: MockServer) -> CLIRunner:
    """Fixture that provides a CLI runner for testing.

    This fixture creates a CLI runner that is configured to use the mock server.

    Args:
        mock_server: The mock server fixture

    Returns:
        A CLIRunner instance
    """
    # Create a CLI runner with environment variables for the mock server
    env = {
        "FOGIS_API_MOCK_SERVER": "true",
        "FOGIS_API_MOCK_SERVER_PORT": str(mock_server.port),
    }

    return CLIRunner(env=env)
