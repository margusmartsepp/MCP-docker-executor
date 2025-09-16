# Development Guidelines

This document contains critical information about working with this MCP Docker Executor codebase. Follow these guidelines precisely.

## Core Development Rules

1. **Package Management**
   - ONLY use `uv`, NEVER `pip`
   - Installation: `uv add package`
   - Running tools: `uv run tool`
   - Upgrading: `uv add --dev package --upgrade-package package`
   - FORBIDDEN: `uv pip install`, `@latest` syntax

2. **Code Quality**
   - Type hints required for all code
   - Public APIs must have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly
   - Line length: 88 chars maximum (Ruff default)

3. **Testing Requirements**
   - Framework: `uv run pytest`
   - Integration tests: Use real Docker (not mocks)
   - Coverage: Test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests
   - Mark tests: `@pytest.mark.integration`, `@pytest.mark.docker`

## Git Commit Guidelines

For commits fixing bugs or adding features based on user reports add:

```bash
git commit --trailer "Reported-by:<name>"
```

Where `<name>` is the name of the user.

For commits related to a Github issue, add:

```bash
git commit --trailer "Github-Issue:#<number>"
```

- NEVER ever mention a `co-authored-by` or similar aspects. In particular, never mention the tool used to create the commit message or PR.

## Pull Requests

- Create a detailed message of what changed. Focus on the high level description of the problem it tries to solve, and how it is solved. Don't go into the specifics of the code unless it adds clarity.
- Always add relevant reviewers based on the changes.
- NEVER ever mention a `co-authored-by` or similar aspects. In particular, never mention the tool used to create the commit message or PR.

## Python Tools

### Code Formatting

1. **Ruff**
   - Format: `uv run ruff format .`
   - Check: `uv run ruff check .`
   - Fix: `uv run ruff check . --fix`
   - Critical issues:
     - Line length (88 chars)
     - Import sorting (I001)
     - Unused imports
   - Line wrapping:
     - Strings: use parentheses
     - Function calls: multi-line with proper indent
     - Imports: split into multiple lines

2. **Type Checking**
   - Tool: `uv run pyright`
   - Configuration: External library warnings ignored in `pyproject.toml`
   - Requirements:
     - Explicit None checks for Optional
     - Type narrowing for strings
     - Version warnings can be ignored if checks pass

3. **Pre-commit**
   - Config: `.pre-commit-config.yaml`
   - Runs: on git commit
   - Tools: General checks, Ruff (Python), Pyright, Pytest
   - Installation: `pre-commit install`

## Docker Development

1. **Image Management**
   - Always use the project's `Dockerfile` when available
   - Build with cache-busting: `nocache=True` for testing
   - Test images before committing changes

2. **Container Execution**
   - Use `user="root"` for package installation
   - Enable network access: `network_disabled=False`
   - Clean up containers after execution

3. **Multi-language Support**
   - Python: Use base64 encoding for code transfer
   - Node.js: Use base64 encoding for code transfer
   - C#: Use base64 encoding + dotnet project structure
   - Bash: Execute directly

## Error Resolution

1. **CI Failures**
   - Fix order:
     1. Formatting (`uv run ruff format .`)
     2. Type errors (`uv run pyright`)
     3. Linting (`uv run ruff check .`)
   - Type errors:
     - Get full line context
     - Check Optional types
     - Add type narrowing
     - Verify function signatures

2. **Common Issues**
   - Line length:
     - Break strings with parentheses
     - Multi-line function calls
     - Split imports
   - Types:
     - Add None checks
     - Narrow string types
     - Match existing patterns
   - Docker:
     - Check if Docker Desktop is running
     - Verify image exists before execution
     - Handle container cleanup properly

3. **Best Practices**
   - Check git status before commits
   - Run formatters before type checks
   - Keep changes minimal
   - Follow existing patterns
   - Document public APIs
   - Test thoroughly with real Docker

## Exception Handling

- **Always use `logger.exception()` instead of `logger.error()` when catching exceptions**
  - Don't include the exception in the message: `logger.exception("Failed")` not `logger.exception(f"Failed: {e}")`
- **Catch specific exceptions** where possible:
  - Docker ops: `except docker.errors.DockerException:`
  - File ops: `except (OSError, PermissionError):`
  - JSON: `except json.JSONDecodeError:`
  - Network: `except (ConnectionError, TimeoutError):`
- **Only catch `Exception` for**:
  - Top-level handlers that must not crash
  - Cleanup blocks (log at debug level)

## MCP-Specific Guidelines

1. **Models**
   - Use Pydantic for all request/response models
   - Include proper validation and field descriptions
   - Follow existing naming conventions

2. **API Endpoints**
   - Use FastAPI with proper response models
   - Include comprehensive error handling
   - Document endpoints with descriptions

3. **Streaming Execution**
   - Use Server-Sent Events (SSE) for real-time updates
   - Implement proper progress tracking
   - Handle connection cleanup

4. **File Management**
   - Use base64 encoding for binary content
   - Implement proper file organization by language
   - Include metadata tracking

## Development Workflow

1. **Setup**
   ```bash
   uv sync --frozen --all-extras --dev
   pre-commit install
   ```

2. **Daily Development**
   ```bash
   uv run ruff check . --fix
   uv run ruff format .
   uv run pyright
   uv run pytest
   ```

3. **Testing New Features**
   ```bash
   # Test the MCP server
   uv run python -m mcp_docker_executor.server

   # Test CLI
   uv run python -m mcp_docker_executor.cli --help

   # Run integration tests
   uv run pytest -m integration
   ```

## Project Structure

- `src/mcp_docker_executor/` - Main source code
- `tests/` - Integration tests (no unit tests)
- `examples/` - Usage examples and demos
- `Dockerfile` - Multi-language runtime image
- `pyproject.toml` - Project configuration and dependencies

## Important Notes

- This project uses **integration tests only** - no unit tests with mocks
- Docker Desktop must be running for tests to pass
- All code execution happens in real Docker containers
- The project supports Python 3.11+, Node.js, C#, and Bash
- Package management works with pip, npm, nuget, and apt
