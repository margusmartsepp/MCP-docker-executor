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
   git clone https://github.com/margusmartsepp/MCP-docker-executor.git
   cd MCP-docker-executor
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

## Claude Desktop Integration

### Setup

#### Method 1: Using MCP CLI (Recommended)

1. **Install the MCP server in Claude Desktop**:

   ```bash
   uv run mcp install src/mcp_docker_executor/mcp_server.py
   ```

2. **Restart Claude Desktop** to load the new MCP server.

3. **Verify connection** - You should see the MCP Docker Executor tools available in Claude Desktop.

#### Method 2: Manual Configuration

If the automatic installation doesn't work, you can manually configure the MCP server:

1. **Find your Claude Desktop config file**:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/claude-desktop/config.json`

2. **Add the MCP server configuration**:

   ```json
   {
     "mcpServers": {
       "mcp-docker-executor": {
         "command": "C:\\Users\\margu\\Vibe\\.venv\\Scripts\\python.exe",
         "args": [
           "-m",
           "mcp_docker_executor.mcp_server"
         ],
         "cwd": "C:\\Users\\margu\\Vibe"
       }
     }
   }
   ```

   **Note**: Update the paths to match your system:
   - `command`: Full path to your Python executable
   - `cwd`: Full path to your project directory

3. **Restart Claude Desktop** to load the configuration.

#### Using MCP Inspector

The MCP Inspector is a powerful tool for debugging and testing MCP servers:

1. **Install MCP Inspector**:

   ```bash
   npm install -g @modelcontextprotocol/inspector
   ```

2. **Run the inspector**:

   ```bash
   mcp-inspector
   ```

3. **Connect to your MCP server**:
   - In the inspector, click "Connect to Server"
   - Enter the command: `C:\Users\margu\Vibe\.venv\Scripts\python.exe`
   - Enter the args: `["-m", "mcp_docker_executor.mcp_server"]`
   - Enter the working directory: `C:\Users\margu\Vibe`

4. **Test the tools**:
   - Use the inspector to test individual tools
   - View request/response details
   - Debug connection issues
   - Verify tool parameters and outputs

#### Verification Steps

1. **Check Claude Desktop logs** for connection status
2. **Look for MCP tools** in Claude's interface
3. **Test basic functionality** with a simple command like "Check Docker health"

### Example Usage

Here's a real example of using the MCP Docker Executor through Claude Desktop:

**User Prompt:**
> "Can you write a Python Fibonacci function and run it with mcp-docker-executor?"

**Claude's Response:**
I'll create Python Fibonacci functions and execute them using the MCP Docker Executor. Let me write efficient iterative implementations and run them in a Docker container.

**Generated Code:**

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number using iterative approach."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return b

def fibonacci_sequence(n):
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []

    sequence = []
    a, b = 0, 1

    for i in range(n):
        if i == 0:
            sequence.append(0)
        elif i == 1:
            sequence.append(1)
        else:
            sequence.append(a + b)
            a, b = b, a + b

    return sequence

# Test the functions
print("Testing Fibonacci functions:")
print("-" * 30)

# Test individual numbers
test_numbers = [0, 1, 5, 10, 15]
for num in test_numbers:
    result = fibonacci(num)
    print(f"fibonacci({num}) = {result}")

print("\nFibonacci sequence (first 15 numbers):")
seq = fibonacci_sequence(15)
print(seq)
```

**Execution Result:**

- **Execution ID**: `exec_1758067574_b0bc8347`
- **Status**: `completed`
- **Exit Code**: `0`
- **Execution Time**: `0.00s`

**Output:**

```text
Testing Fibonacci functions:
------------------------------
fibonacci(0) = 0
fibonacci(1) = 1
fibonacci(5) = 5
fibonacci(10) = 55
fibonacci(15) = 610

Fibonacci sequence (first 15 numbers):
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
```

**Analysis:**
Perfect! The functions executed successfully in the Docker container. The iterative approach is efficient and handles edge cases properly. The results show:

- Individual Fibonacci numbers: F(0)=0, F(1)=1, F(5)=5, F(10)=55, F(15)=610
- Complete sequence: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

### Available Tools in Claude Desktop

When connected, you'll have access to these tools:

- **`execute_code`** - Execute Python, Node.js, C#, or Bash code
- **`create_image`** - Create custom Docker images with specific runtimes
- **`install_package`** - Install packages (pip, npm, nuget, apt)
- **`upload_file`** - Upload and manage code files
- **`execute_uploaded_file`** - Run uploaded files
- **`list_files`** - List all uploaded files
- **`delete_file`** - Remove uploaded files
- **`docker_health`** - Check Docker connection status

### Tips for Claude Desktop Usage

1. **Be specific about language**: Always specify the programming language when requesting code execution
2. **Include test cases**: Ask Claude to include test cases and examples in the generated code
3. **Request explanations**: Ask for explanations of the results and any optimization opportunities
4. **Use file uploads**: For complex code, consider asking Claude to upload files for better organization

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

### Package Management API

- `POST /packages/install` - Install package

### File Management API

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

### Recent Improvements

- ✅ **Fixed test execution issues** - Resolved server caching problems that caused test failures
- ✅ **Improved endpoint reliability** - All API endpoints now return correct response structures
- ✅ **Enhanced error handling** - Better exception handling and proper HTTP status codes

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

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for detailed instructions on how to:

1. Set up your development environment
2. Follow our coding standards
3. Run tests and quality checks
4. Submit pull requests

For release information, see our [Release Process](RELEASE.md) documentation.

For questions or discussions, please open an issue on GitHub.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

- 📝 [Create an issue on GitHub](https://github.com/margusmartsepp/MCP-docker-executor/issues)
- 📚 Check the documentation in `docs/`
- 🧪 Review test examples in `tests/`
- 💬 Join discussions in GitHub Discussions

## Project Links

- 🏠 **Homepage**: [https://github.com/margusmartsepp/MCP-docker-executor](https://github.com/margusmartsepp/MCP-docker-executor)
- 📦 **Repository**: [https://github.com/margusmartsepp/MCP-docker-executor.git](https://github.com/margusmartsepp/MCP-docker-executor.git)
- 🐛 **Issues**: [https://github.com/margusmartsepp/MCP-docker-executor/issues](https://github.com/margusmartsepp/MCP-docker-executor/issues)
- 📖 **Documentation**: [https://github.com/margusmartsepp/MCP-docker-executor#readme](https://github.com/margusmartsepp/MCP-docker-executor#readme)
