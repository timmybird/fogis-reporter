"""Test fixtures for UI testing.

This module provides fixtures for UI testing, including a mock server fixture.
"""

import os
import signal
import socket
import subprocess
from typing import Generator, Optional

import pytest
from fogis_api_client.mock_server import MockServer
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
        return s.connect_ex(('localhost', port)) == 0


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
    server = MockServer(port=port)
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
        "FOGIS_API_MOCK_SERVER_PORT": str(mock_server.port)
    }
    
    return CLIRunner(env=env)
