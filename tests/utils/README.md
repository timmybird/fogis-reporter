# Test Data Generator for Mock Server

This directory contains a test data generator for the mock server in the fogis-reporter project. The test data generator makes it easier to create realistic test data for testing the application without requiring real FOGIS credentials.

## Overview

The `TestDataGenerator` class provides methods for generating test data for specific scenarios that can be used with the mock server for testing the fogis-reporter application. It extends the functionality of the existing `MockDataFactory` class in the fogis-api-client package.

## Usage

### Basic Usage

```python
from tests.utils.test_data_generator import TestDataGenerator
from fogis_api_client.cli.mock_server import MockFogisServer

# Create a mock server
mock_server = MockFogisServer(host="localhost", port=5001)
server_thread = mock_server.run(threaded=True)

# Create a test data generator
generator = TestDataGenerator(mock_server)

# Generate test data for a match with goals
match_data = generator.create_match_with_goals(home_goals=2, away_goals=1)

# Apply the test data to the mock server
generator.apply_to_mock_server(match_data)

# Use the mock server for testing
# ...

# Shutdown the mock server
mock_server.shutdown()
server_thread.join(timeout=5)
```

### Using with Pytest

```python
import pytest
from tests.utils.test_data_generator import TestDataGenerator
from fogis_api_client.cli.mock_server import MockFogisServer

@pytest.fixture(scope="session")
def mock_server():
    """Start a mock FOGIS server for testing."""
    server = MockFogisServer(host="localhost", port=5001)
    server_thread = server.run(threaded=True)
    yield server
    server.shutdown()
    server_thread.join(timeout=5)

@pytest.fixture
def test_data_generator(mock_server):
    """Create a test data generator."""
    return TestDataGenerator(mock_server)

@pytest.fixture
def match_with_goals(test_data_generator):
    """Create a match with goals."""
    match_data = test_data_generator.create_match_with_goals(home_goals=2, away_goals=1)
    test_data_generator.apply_to_mock_server(match_data)
    return match_data

def test_report_goal(mock_server, match_with_goals):
    """Test reporting a goal."""
    # Create an API client configured to use the mock server
    client = FogisApiClient("test_user", "test_password")
    client.base_url = f"http://{mock_server.host}:{mock_server.port}/mdk"
    client.login()

    # Fetch the match
    match_id = match_with_goals["match"]["matchid"]

    # Report a goal
    goal_event = {
        "matchhandelseid": 0,
        "matchid": match_id,
        "matchhandelsetypid": 6,  # Regular goal
        "matchlagid": match_with_goals["match"]["hemmalagid"],
        "trojnummer": 9,
        "matchminut": 10,
        "period": 1,
        "hemmamal": 3,  # New score
        "bortamal": 1,
    }

    response = client.report_match_event(goal_event)
    assert response is not None

    # Verify the goal was recorded
    events = client.fetch_match_events_json(match_id)
    assert any(e["matchhandelsetypid"] == 6 and e["matchminut"] == 10 and e["trojnummer"] == 9 for e in events)
```

## Available Methods

The `TestDataGenerator` class provides the following methods for generating test data:

### `create_match_with_goals`

Create a match with the specified number of goals.

```python
match_data = generator.create_match_with_goals(
    home_goals=2,
    away_goals=1,
    home_team_name="Home Team",
    away_team_name="Away Team",
    match_id=123456,
)
```

### `create_match_with_cards`

Create a match with the specified number of cards.

```python
match_data = generator.create_match_with_cards(
    home_yellow_cards=1,
    home_red_cards=0,
    away_yellow_cards=2,
    away_red_cards=1,
    match_id=123456,
)
```

### `create_match_with_substitutions`

Create a match with the specified number of substitutions.

```python
match_data = generator.create_match_with_substitutions(
    home_substitutions=3,
    away_substitutions=3,
    match_id=123456,
)
```

### `create_match_with_team_official_actions`

Create a match with team official actions.

```python
match_data = generator.create_match_with_team_official_actions(
    home_warnings=1,
    home_dismissals=0,
    away_warnings=1,
    away_dismissals=1,
    match_id=123456,
)
```

### `create_match_with_specific_result`

Create a match with a specific result.

```python
match_data = generator.create_match_with_specific_result(
    home_score=2,
    away_score=1,
    halftime_home_score=1,
    halftime_away_score=0,
    match_id=123456,
)
```

### `create_complete_match_scenario`

Create a complete match scenario with all types of events.

```python
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
    match_id=123456,
)
```

## Extending the Test Data Generator

You can extend the `TestDataGenerator` class to add more methods for generating test data for specific scenarios:

```python
from tests.utils.test_data_generator import TestDataGenerator

class MyTestDataGenerator(TestDataGenerator):
    """Extended test data generator with additional methods."""

    def create_match_with_penalty_shootout(self, home_penalties, away_penalties):
        """Create a match with a penalty shootout."""
        # Implementation...
        pass
```

## Contributing

If you find a bug or have a suggestion for improvement, please open an issue or submit a pull request.
