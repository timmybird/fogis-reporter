# FOGIS Reporter

A Python application for reporting match events to the Swedish Football Association's FOGIS system.

## Features

- Report match events (goals, cards, substitutions, etc.)
- Report match results
- View match information
- Manage multiple matches

## Installation

```bash
pip install fogis-reporter
```

## Usage

```bash
python -m fogis_reporter
```

## Development

### Code Quality Standards

This project uses several tools to ensure code quality:

1. **Black**: For code formatting
2. **isort**: For import sorting
3. **flake8**: For linting
4. **mypy**: For type checking
5. **ruff**: For fast linting

These tools are configured to run automatically as pre-commit hooks and in the CI/CD pipeline.

### Setting Up Development Environment

1. Clone the repository
2. Run the setup script to quickly set up your development environment:
   ```bash
   python scripts/setup_dev.py
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`

### Running Tests

```bash
pytest
```

### Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
