# Testing Guide

This document provides comprehensive guidance for testing the MCP Docker Executor project.

## Prerequisites

Before running tests, ensure you have:

- **Docker Desktop** running and accessible
- **Python 3.11+** installed
- **uv** installed: [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Project dependencies** installed: `uv sync --frozen --all-extras --dev`
- **Pre-commit hooks** installed: `pre-commit install`
- **Docker image built**: `docker build -t mcp-executor-base .`

## Important Testing Philosophy

**IMPORTANT: This project uses INTEGRATION TESTS and E2E TESTS only. We do NOT write unit tests - all tests should use real Docker containers and test the actual functionality end-to-end.**

## Code Quality Tools

### Run All Quality Checks
```bash
# Run all pre-commit hooks (recommended)
pre-commit run --all-files

# Manual checks (if needed)
uv run pytest
uv run pyright
uv run ruff check .
uv run ruff format .
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks (one-time setup)
uv tool install pre-commit --with pre-commit-uv --force-reinstall
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Run hooks on staged files only
pre-commit run
```

### Individual Quality Checks
```bash
# Type checking only
uv run pyright

# Linting only
uv run ruff check .

# Auto-fix linting issues
uv run ruff check . --fix

# Format code only
uv run ruff format .
```

## Test Categories

### Integration Tests (`@pytest.mark.integration`)
- Test individual components with real Docker containers
- Use actual Docker images and containers
- Test Docker manager, file manager, and execution handlers

### End-to-End Tests (`@pytest.mark.e2e`)
- Test complete workflows through the API
- Use HTTP requests to test server endpoints
- Test full user scenarios

### Docker Tests (`@pytest.mark.docker`)
- Tests that require Docker to be running
- Automatically skipped if Docker is not available

### Slow Tests (`@pytest.mark.slow`)
- Tests that take longer to run
- Can be skipped for quick development cycles

## Running Tests

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Integration tests only
uv run pytest tests/ -m integration -v

# End-to-end tests only
uv run pytest tests/ -m e2e -v

# Docker tests only
uv run pytest tests/ -m docker -v

# Skip slow tests
uv run pytest tests/ -m "not slow" -v
```

### Run Specific Test Files
```bash
# Test Docker manager
uv run pytest tests/test_docker_manager.py -v

# Test server endpoints
uv run pytest tests/test_server.py -v

# Test models
uv run pytest tests/test_models.py -v
```

### Run Specific Tests
```bash
# Test Python execution
uv run pytest tests/test_docker_manager.py::TestDockerManager::test_execute_python_code -v

# Test file upload
uv run pytest tests/test_docker_manager.py::TestDockerManager::test_file_upload_python -v
```

## Test Structure

### `tests/conftest.py`
- Pytest configuration and fixtures
- Docker manager fixtures
- Test image creation and cleanup

### `tests/test_docker_manager.py`
- Integration tests for Docker operations
- Image creation and management
- Code execution in different languages
- Package installation
- File upload and management

### `tests/test_server.py`
- End-to-end tests for API endpoints
- HTTP request/response testing
- Complete workflow testing

### `tests/test_models.py`
- Unit tests for Pydantic models
- Data validation testing
- Serialization/deserialization testing

## Docker Image Build Testing

### Build the Image
```bash
docker build -t mcp-executor-base .
```

### Verify Runtime Installation
```bash
# Check Python
docker run --rm mcp-executor-base python --version

# Check Node.js
docker run --rm mcp-executor-base node --version
docker run --rm mcp-executor-base npm --version

# Check .NET SDK
docker run --rm mcp-executor-base dotnet --version
```

### Test Multi-language Support
```bash
# Python execution
docker run --rm mcp-executor-base python -c "print('Python works!')"

# Node.js execution
docker run --rm mcp-executor-base node -e "console.log('Node.js works!')"

# C# execution
docker run --rm mcp-executor-base dotnet --version
```

## New Features Testing

### Package Management Testing

#### Python Package Installation
```bash
# Test pip installation
uv run python -m mcp_docker_executor.cli create python --image-name test-python
uv run python -m mcp_docker_executor.cli install-package <image-id> python requests
uv run python -m mcp_docker_executor.cli exec python "import requests; print('Requests installed!')" --image-id <new-image-id>
```

#### Node.js Package Installation
```bash
# Test npm installation
uv run python -m mcp_docker_executor.cli create node --image-name test-node
uv run python -m mcp_docker_executor.cli install-package <image-id> node lodash
uv run python -m mcp_docker_executor.cli exec node "const _ = require('lodash'); console.log('Lodash installed!')" --image-id <new-image-id>
```

#### C# Package Installation
```bash
# Test NuGet installation
uv run python -m mcp_docker_executor.cli create csharp --image-name test-csharp
uv run python -m mcp_docker_executor.cli install-package <image-id> csharp Newtonsoft.Json
uv run python -m mcp_docker_executor.cli exec csharp "using Newtonsoft.Json; Console.WriteLine(\"Newtonsoft.Json installed!\");" --image-id <new-image-id>
```

### File Management Testing

#### File Upload and Execution
```bash
# Upload Python file
uv run python -m mcp_docker_executor.cli upload-file "test.py" "print('Hello from file!')" python

# List files
uv run python -m mcp_docker_executor.cli list-files

# Execute uploaded file
uv run python -m mcp_docker_executor.cli exec-file <file-id>

# Delete file
uv run python -m mcp_docker_executor.cli delete-file <file-id>
```

#### File Management API Testing
```bash
# Upload file via API
curl -X POST http://localhost:8000/files/upload \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.py", "content": "print(\"Hello World!\")", "language": "python"}'

# List files via API
curl http://localhost:8000/files

# Get file stats via API
curl http://localhost:8000/files/stats
```

### Streaming Execution Testing

#### Start Streaming Execution
```bash
# Start streaming execution
curl -X POST http://localhost:8000/execute/stream \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "code": "import time; [print(f\"Step {i}\") or time.sleep(1) for i in range(5)]"}'

# Get execution progress
curl http://localhost:8000/executions/<execution-id>/progress

# Stream execution logs
curl http://localhost:8000/executions/<execution-id>/stream
```

## Test Data and Fixtures

### Test Images
- `test-multi-lang`: Python, Node.js, C# support
- `test-python`: Python-only image
- `test-node`: Node.js-only image
- `test-csharp`: C#-only image

### Test Files
- Python test files with factorial calculations
- Node.js test files with factorial calculations
- C# test files with factorial calculations
- Simple "Hello World" test files

### Test Packages
- Python: `requests`, `numpy`, `pandas`
- Node.js: `lodash`, `express`, `axios`
- C#: `Newtonsoft.Json`, `System.Text.Json`

## Troubleshooting

### Common Issues

#### Docker Not Available
```
pytest.skip("Docker is not available")
```
**Solution**: Start Docker Desktop and ensure it's running

#### Image Build Failures
```
pytest.skip("Failed to create test image: ...")
```
**Solution**: Check Docker daemon, available disk space, and network connectivity

#### Container Execution Failures
```
assert response.status == "completed"
```
**Solution**: Check container logs, resource limits, and code syntax

#### API Connection Failures
```
httpx.ConnectError: [Errno 111] Connection refused
```
**Solution**: Ensure MCP server is running on localhost:8000

### Debug Mode

Run tests with debug output:
```bash
python -m pytest tests/ -v -s --log-cli-level=DEBUG
```

### Test Isolation

Each test is isolated and cleans up after itself:
- Docker images are removed after tests
- Uploaded files are deleted
- Containers are stopped and removed

## Performance Testing

### Resource Limits Testing
```bash
# Test memory limits
python -m mcp_docker_executor.cli exec python "import sys; print(f'Memory: {sys.getsizeof(range(1000000))} bytes')" --resource-limits '{"memory_mb": 256}'

# Test CPU limits
python -m mcp_docker_executor.cli exec python "import time; start=time.time(); [i**2 for i in range(1000000)]; print(f'Time: {time.time()-start:.2f}s')" --resource-limits '{"cpu_cores": 0.5}'

# Test timeout limits
python -m mcp_docker_executor.cli exec python "import time; time.sleep(10)" --resource-limits '{"timeout_seconds": 5}'
```

### Concurrent Execution Testing
```bash
# Run multiple executions simultaneously
for i in {1..5}; do
  python -m mcp_docker_executor.cli exec python "print(f'Execution {i}')" &
done
wait
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Start Docker
        run: sudo systemctl start docker
      - name: Build Docker image
        run: docker build -t mcp-executor-base .
      - name: Run tests
        run: python -m pytest tests/ -v
```

## Test Coverage

Generate test coverage report:
```bash
python -m pytest tests/ --cov=src/mcp_docker_executor --cov-report=html --cov-report=term
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

## Best Practices

1. **Always clean up**: Remove Docker images, containers, and files after tests
2. **Use fixtures**: Leverage pytest fixtures for setup and teardown
3. **Test real scenarios**: Use actual Docker containers and HTTP requests
4. **Isolate tests**: Each test should be independent and not affect others
5. **Handle failures gracefully**: Use appropriate assertions and error handling
6. **Document test purposes**: Write clear test names and docstrings
7. **Test edge cases**: Include tests for error conditions and boundary cases
8. **Use appropriate markers**: Mark tests with integration, e2e, docker, or slow markers
