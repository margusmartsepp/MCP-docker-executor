# Contributing

Thank you for your interest in contributing to the MCP Docker Executor! This document provides guidelines and instructions for contributing.

## Development Setup

1. Make sure you have Python 3.11+ installed
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
3. Fork the repository
4. Clone your fork: `git clone https://github.com/YOUR-USERNAME/MCP-docker-executor.git`
5. Install dependencies:

```bash
uv sync --frozen --all-extras --dev
```

6. Set up pre-commit hooks:

```bash
uv tool install pre-commit --with pre-commit-uv --force-reinstall
pre-commit install
```

7. Build the Docker image:

```bash
docker build -t mcp-executor-base .
```

## Development Workflow

1. Choose the correct branch for your changes:
   - For bug fixes to a released version: use the latest release branch (e.g. v0.1.x for 0.1.1)
   - For new features: use the main branch (which will become the next minor/major version)
   - If unsure, ask in an issue first

2. Create a new branch from your chosen base branch

3. Make your changes

4. Ensure tests pass:

```bash
uv run pytest
```

5. Run type checking:

```bash
uv run pyright
```

6. Run linting:

```bash
uv run ruff check .
uv run ruff format .
```

7. (Optional) Run pre-commit hooks on all files:

```bash
pre-commit run --all-files
```

8. Submit a pull request to the same branch you branched from

## Code Style

- We use `ruff` for linting and formatting
- Follow PEP 8 style guidelines with 120 character line length
- Add type hints to all functions
- Include docstrings for public APIs
- Use `logger.exception()` instead of `logger.error()` when catching exceptions
- Follow the guidelines in `CLAUDE.md` for project-specific conventions

## Testing

### Test Categories

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions with real Docker
- **End-to-end tests**: Test complete workflows

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/ -m integration -v
uv run pytest tests/ -m docker -v
uv run pytest tests/ -m e2e -v

# Run tests for specific components
uv run pytest tests/test_docker_manager.py -v
uv run pytest tests/test_server.py -v
uv run pytest tests/test_models.py -v
```

### Test Requirements

- Integration and E2E tests require Docker Desktop to be running
- Tests should be deterministic and not depend on external services
- Add tests for new functionality
- Update tests when modifying existing features

## Docker Development

### Building Images

```bash
# Build the base image
docker build -t mcp-executor-base .

# Verify runtime installation
docker run --rm mcp-executor-base python --version
docker run --rm mcp-executor-base node --version
docker run --rm mcp-executor-base dotnet --version
```

### Testing Docker Features

- Always test package installation (pip, npm, nuget)
- Verify file upload and execution
- Test streaming execution for long-running processes
- Ensure proper cleanup of containers and images

## Pull Request Process

1. Update documentation as needed
2. Add tests for new functionality
3. Ensure CI passes
4. Update the changelog if applicable
5. Maintainers will review your code
6. Address review feedback

## Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Development Guidelines

See `CLAUDE.md` for detailed development guidelines specific to this project, including:
- Package management with uv
- Code quality tools configuration
- Git commit conventions
- Error handling patterns
- MCP-specific guidelines
