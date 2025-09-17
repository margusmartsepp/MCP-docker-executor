# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Future enhancements and improvements

## [0.1.0a1] - 2025-01-17

### Features

- Initial alpha release of MCP Docker Executor
- Multi-language execution support (Python 3.11, Node.js 22.x, .NET 8.0, Bash)
- Docker image management and creation
- Package management (pip, npm, nuget, apt)
- File upload and management system
- Streaming execution with real-time progress updates
- REST API with FastAPI
- Command-line interface (CLI)
- Claude Desktop integration with FastMCP
- MCP Inspector support for debugging

### Documentation

- Comprehensive README.md with setup and usage instructions
- Detailed Claude Desktop integration examples
- MCP Inspector setup and troubleshooting guide
- Manual configuration methods with exact JSON examples
- Release process documentation (RELEASE.md)
- Contributing guidelines (CONTRIBUTING.md)
- Code of conduct (CODE_OF_CONDUCT.md)

### Technical Details

- **Python**: 3.11+ with uv package management
- **Docker**: Multi-stage build with Python, Node.js, .NET SDK
- **API**: FastAPI with async/await support
- **Testing**: pytest with async support and Docker integration
- **Code Quality**: ruff (linting/formatting), pyright (type checking)
- **CI/CD**: Pre-commit hooks and automated quality checks

### Fixed

- Fixed execution response mismatch - server was running old cached code with different response structure
- Fixed file info endpoint - properly includes content field in response
- Fixed file delete endpoint - correctly returns 404 for non-existent files
- Fixed file stats endpoint - handles exceptions properly
- Fixed async execution timing - server now completes execution before returning response
- Resolved test failures caused by server running outdated cached code

### Dependencies

- mcp[cli]>=1.14.0
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- docker>=6.1.0
- pydantic>=2.11.7
- httpx>=0.25.0
- aiofiles>=23.2.0

[Unreleased]: https://github.com/margusmartsepp/MCP-docker-executor/compare/v0.1.0a1...HEAD
[0.1.0a1]: https://github.com/margusmartsepp/MCP-docker-executor/releases/tag/v0.1.0a1
