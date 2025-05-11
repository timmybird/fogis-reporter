"""Pytest fixtures for the fogis-reporter project.

This module contains pytest fixtures that can be used in tests.
"""

import threading
import time

import pytest

from tests.utils.test_data_generator import TestDataGenerator

# Try to import the MockFogisServer from the fogis-api-client package
try:
    from fogis_api_client.cli.mock_server import MockFogisServer
    from fogis_api_client.fogis_api_client import FogisApiClient

    MOCK_SERVER_AVAILABLE = True
except ImportError:
    # Create mock classes if the imports aren't available
    class MockFogisServer:
        """Mock class for MockFogisServer."""

        def __init__(self, *args, **kwargs):
            """Initialize the mock server."""
            self.host = "localhost"
            self.port = 5001

        def run(self, threaded=False):
            """Mock run method."""
            return threading.Thread()

        def shutdown(self):
            """Mock shutdown method."""
            pass

    class FogisApiClient:
        """Mock class for FogisApiClient."""

        def __init__(self, *args, **kwargs):
            """Initialize the API client."""
            self.base_url = "http://localhost:5001/mdk"

        def login(self):
            """Mock login method."""
            pass

    MOCK_SERVER_AVAILABLE = False


@pytest.fixture(scope="session")
def mock_server():
    """Start a mock FOGIS server for testing.

    This fixture starts a mock FOGIS server that can be used for testing
    the fogis-reporter application without requiring real FOGIS credentials.

    Returns:
        The mock server instance.
    """
    if not MOCK_SERVER_AVAILABLE:
        pytest.skip(
            "Mock server not available. "
            "Install fogis-api-client>=0.5.0 to use this fixture."
        )

    server = MockFogisServer(host="localhost", port=5001)
    server_thread = server.run(threaded=True)

    # Wait for the server to start
    time.sleep(1)

    yield server

    # Shutdown the server after tests
    server.shutdown()
    server_thread.join(timeout=5)


@pytest.fixture
def api_client(mock_server):
    """Create an API client configured to use the mock server.

    This fixture creates an API client that is configured to use the mock server
    for testing the fogis-reporter application without requiring real FOGIS credentials.

    Args:
        mock_server: The mock server fixture.

    Returns:
        The API client instance.
    """
    if not MOCK_SERVER_AVAILABLE:
        pytest.skip(
            "Mock server not available. "
            "Install fogis-api-client>=0.5.0 to use this fixture."
        )

    # Create a client with test credentials
    client = FogisApiClient("test_user", "test_password")

    # Override the base URL to point to the mock server
    client.base_url = f"http://{mock_server.host}:{mock_server.port}/mdk"

    # Login to the mock server
    client.login()

    return client


@pytest.fixture
def test_data_generator(mock_server):
    """Create a test data generator.

    This fixture creates a test data generator that can be used to generate
    test data for the mock server.

    Args:
        mock_server: The mock server fixture.

    Returns:
        The test data generator instance.
    """
    if not MOCK_SERVER_AVAILABLE:
        pytest.skip(
            "Mock server not available. "
            "Install fogis-api-client>=0.5.0 to use this fixture."
        )

    return TestDataGenerator(mock_server)


@pytest.fixture
def match_with_goals(test_data_generator):
    """Create a match with goals.

    This fixture creates a match with goals that can be used for testing
    the fogis-reporter application.

    Args:
        test_data_generator: The test data generator fixture.

    Returns:
        The match data.
    """
    match_data = test_data_generator.create_match_with_goals(home_goals=2, away_goals=1)
    test_data_generator.apply_to_mock_server(match_data)
    return match_data


@pytest.fixture
def match_with_cards(test_data_generator):
    """Create a match with cards.

    This fixture creates a match with cards that can be used for testing
    the fogis-reporter application.

    Args:
        test_data_generator: The test data generator fixture.

    Returns:
        The match data.
    """
    match_data = test_data_generator.create_match_with_cards(
        home_yellow_cards=1,
        home_red_cards=0,
        away_yellow_cards=2,
        away_red_cards=1,
    )
    test_data_generator.apply_to_mock_server(match_data)
    return match_data


@pytest.fixture
def match_with_substitutions(test_data_generator):
    """Create a match with substitutions.

    This fixture creates a match with substitutions that can be used for testing
    the fogis-reporter application.

    Args:
        test_data_generator: The test data generator fixture.

    Returns:
        The match data.
    """
    match_data = test_data_generator.create_match_with_substitutions(
        home_substitutions=3,
        away_substitutions=3,
    )
    test_data_generator.apply_to_mock_server(match_data)
    return match_data


@pytest.fixture
def complete_match_scenario(test_data_generator):
    """Create a complete match scenario.

    This fixture creates a complete match scenario with all types of events
    that can be used for testing the fogis-reporter application.

    Args:
        test_data_generator: The test data generator fixture.

    Returns:
        The match data.
    """
    match_data = test_data_generator.create_complete_match_scenario(
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
    test_data_generator.apply_to_mock_server(match_data)
    return match_data
