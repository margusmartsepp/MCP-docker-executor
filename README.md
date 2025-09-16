# MCP Docker Executor

A Python-based Master Control Program (MCP) server that creates Linux Docker images with Python, Node.js, and C# runtimes, enabling LLMs to have full control over Docker Linux automation.

## Features

- **Multi-language Execution**: Support for Python 3.11, Node.js 22.x, .NET 8.0, and Bash
- **Docker Image Management**: Create custom Docker images with specific language runtimes
- **Code Execution**: Execute code in isolated Docker containers with resource limits
- **Package Management**: Install packages using pip (Python), npm (Node.js), nuget (C#), and apt (system)
- **File Upload System**: Upload and manage code files for execution
- **Streaming Execution**: Real-time progress updates and log streaming for long-running processes
- **Security**: Sandboxed execution with configurable resource limits
- **REST API**: FastAPI-based server with comprehensive endpoints
- **CLI Interface**: Command-line tool for easy interaction

## Prerequisites

- **Python 3.11+**
- **uv** (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Docker Desktop** (running and accessible)
- **Windows 10/11** (current environment)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp-docker-executor
   ```

2. **Install dependencies with uv**:
   ```bash
   uv sync --frozen --all-extras --dev
   ```

3. **Set up pre-commit hooks**:
   ```bash
   uv tool install pre-commit --with pre-commit-uv --force-reinstall
   pre-commit install
   ```

4. **Build the Docker image**:
   ```bash
   docker build -t mcp-executor-base .
   ```

5. **Verify installation**:
   ```bash
   docker run --rm mcp-executor-base python --version
   docker run --rm mcp-executor-base node --version
   docker run --rm mcp-executor-base dotnet --version
   ```

## Quick Start

### 1. Start the MCP Server

```bash
uv run python -m mcp_docker_executor.server
```

The server will start on `http://localhost:8000`

### 2. Test the Server

```bash
uv run python -m mcp_docker_executor.cli health
```

### 3. Create a Multi-language Image

```bash
uv run python -m mcp_docker_executor.cli create python node csharp --image-name my-multi-lang
```

### 4. Execute Code

```bash
# Python
uv run python -m mcp_docker_executor.cli exec python "print('Hello from Python!')"

# Node.js
uv run python -m mcp_docker_executor.cli exec node "console.log('Hello from Node.js!')"

# C#
uv run python -m mcp_docker_executor.cli exec csharp "Console.WriteLine(\"Hello from C#!\");"
```

## Docker Image

The project includes a comprehensive Dockerfile that creates a multi-language execution environment:

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

### Key Features

- **Python 3.11** with pip support
- **Node.js 22.x** with npm support
- **.NET SDK 8.0** with NuGet support
- **System packages** via apt
- **Non-root execution** with sandboxuser
- **Optimized for security** and performance

## Package Management

### Python Packages (pip)

```bash
# Install requests library
uv run python -m mcp_docker_executor.cli install-package <image-id> python requests

# Install specific version
uv run python -m mcp_docker_executor.cli install-package <image-id> python "requests==2.31.0"
```

### Node.js Packages (npm)

```bash
# Install lodash
uv run python -m mcp_docker_executor.cli install-package <image-id> node lodash

# Install specific version
uv run python -m mcp_docker_executor.cli install-package <image-id> node "lodash@4.17.21"
```

### C# Packages (NuGet)

```bash
# Install Newtonsoft.Json
uv run python -m mcp_docker_executor.cli install-package <image-id> csharp Newtonsoft.Json

# Install specific version
uv run python -m mcp_docker_executor.cli install-package <image-id> csharp "Newtonsoft.Json==13.0.3"
```

## File Management

### Upload Files

```bash
# Upload Python file
uv run python -m mcp_docker_executor.cli upload-file "hello.py" "print('Hello World!')" python

# Upload Node.js file
uv run python -m mcp_docker_executor.cli upload-file "hello.js" "console.log('Hello World!')" node

# Upload C# file
uv run python -m mcp_docker_executor.cli upload-file "hello.cs" "Console.WriteLine(\"Hello World!\");" csharp
```

### Manage Files

```bash
# List uploaded files
uv run python -m mcp_docker_executor.cli list-files

# Execute uploaded file
uv run python -m mcp_docker_executor.cli exec-file <file-id>

# Delete file
uv run python -m mcp_docker_executor.cli delete-file <file-id>
```

## API Endpoints

### Core Operations

- `POST /images/create` - Create Docker image
- `POST /execute` - Execute code
- `GET /executions/{id}` - Get execution result
- `GET /health` - Health check

### Package Management

- `POST /packages/install` - Install package

### File Management

- `POST /files/upload` - Upload file
- `GET /files` - List files
- `GET /files/{id}` - Get file info
- `DELETE /files/{id}` - Delete file
- `POST /files/{id}/execute` - Execute file
- `GET /files/stats` - File statistics

### Streaming Execution

- `POST /execute/stream` - Start streaming execution
- `GET /executions/{id}/progress` - Get execution progress
- `GET /executions/{id}/stream` - Stream execution logs

## Complete Package Management Demo

See `examples/package_management_demo.py` for a comprehensive demonstration of all features.

## Development Tools

### Code Quality

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

Pre-commit hooks automatically run on every commit to ensure code quality:

```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Run hooks manually on staged files
pre-commit run
```

### Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test categories
uv run pytest tests/ -m integration -v
uv run pytest tests/ -m docker -v
uv run pytest tests/ -m e2e -v
```

### Test Individual Components

```bash
# Test Docker manager
uv run pytest tests/test_docker_manager.py -v

# Test execution handlers
uv run pytest tests/test_execution_handlers.py -v

# Test server endpoints
uv run pytest tests/test_server.py -v
```

## Architecture

The system consists of several key components:

- **Docker Manager**: Handles Docker operations and container management
- **Execution Handlers**: Language-specific code execution logic
- **File Manager**: Manages uploaded files and metadata
- **Security Manager**: Implements security policies and code analysis
- **FastAPI Server**: Provides REST API endpoints
- **CLI Interface**: Command-line tool for interaction

## Security Considerations

- **Sandboxed Execution**: Code runs in isolated Docker containers
- **Resource Limits**: Configurable CPU, memory, and timeout limits
- **Network Access**: Can be disabled for enhanced security
- **Non-root Execution**: Containers run as non-privileged users
- **Code Analysis**: Basic security pattern detection

## Future Enhancements

- [x] **Package Management** - Install packages for Python, Node.js, C#
- [x] **File Upload System** - Upload and manage code files
- [x] **Streaming Execution** - Real-time progress updates
- [x] **Multi-language Support** - Python, Node.js, C#, Bash
- [ ] **Advanced Security** - Enhanced code analysis and sandboxing
- [ ] **Resource Monitoring** - Real-time resource usage tracking
- [ ] **Caching System** - Docker layer and package caching
- [ ] **Web UI** - Browser-based interface
- [ ] **Plugin System** - Extensible language support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review test examples in `tests/`
