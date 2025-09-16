# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive CONTRIBUTING.md guide
- CODE_OF_CONDUCT.md following Contributor Covenant
- CHANGELOG.md for version tracking
- Improved README.md with correct repository URLs

## [0.1.0] - 2025-01-17

### Added
- Initial release of MCP Docker Executor
- Multi-language execution support (Python 3.11, Node.js 22.x, .NET 8.0, Bash)
- Docker image management and creation
- Package management (pip, npm, nuget, apt)
- File upload and management system
- Streaming execution with real-time progress updates
- REST API with FastAPI
- Command-line interface (CLI)
- Comprehensive testing suite (unit, integration, E2E)
- Pre-commit hooks for code quality
- Modern Python tooling (uv, ruff, pyright)
- Docker multi-stage build with optimized runtime
- Security features with sandboxed execution
- Resource limits and timeout management
- Comprehensive documentation and examples

### Technical Details
- **Python**: 3.11+ with uv package management
- **Docker**: Multi-stage build with Python, Node.js, .NET SDK
- **API**: FastAPI with async/await support
- **Testing**: pytest with async support and Docker integration
- **Code Quality**: ruff (linting/formatting), pyright (type checking)
- **CI/CD**: Pre-commit hooks and automated quality checks

### Dependencies
- mcp[cli]>=1.14.0
- fastapi>=0.104.0
- uvicorn[standard]>=0.24.0
- docker>=6.1.0
- pydantic>=2.11.7
- httpx>=0.25.0
- aiofiles>=23.2.0

[Unreleased]: https://github.com/margusmartsepp/MCP-docker-executor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/margusmartsepp/MCP-docker-executor/releases/tag/v0.1.0
