# FOGIS Reporter

A CLI application for reporting match events to the Swedish Football Association's FOGIS system.

## Features

- Login to FOGIS
- List available matches
- Report match events (goals, cards, substitutions)
- Report match results

## Installation

```bash
pip install fogis-reporter
```

## Usage

```bash
python -m fogis_reporter
```

## Development

### Setup

1. Clone the repository
2. Create a virtual environment
3. Install dependencies

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows
.venv\Scripts\activate
# Unix/MacOS
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install the package in development mode
pip install -e .
```

### Testing

#### Running Unit Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=.
```

#### Running UI Tests

UI tests simulate user interaction with the CLI application. They require the mock server from the fogis-api-client package.

```bash
# Run UI tests
pytest tests/ui -v -m ui
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. To set up pre-commit hooks:

```bash
pre-commit install
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
