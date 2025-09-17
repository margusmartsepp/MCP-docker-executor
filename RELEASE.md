# Release Process

This document outlines the process for releasing new versions of the MCP Docker Executor.

## Prerequisites

- Ensure all tests pass: `uv run pytest`
- Run code quality checks: `uv run ruff check . && uv run pyright`
- Verify pre-commit hooks pass: `pre-commit run --all-files`
- Update `CHANGELOG.md` with the new version

## Release Types

### Patch Release (Bug Fixes)

For bug fixes and minor improvements:

1. **Update version in `pyproject.toml`** (if using static versioning)
2. **Update `CHANGELOG.md`**:
   - Move items from "Unreleased" to new version section
   - Update release date
   - Add any additional bug fixes
3. **Commit changes**:

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: prepare for vX.Y.Z release"
   ```

### Minor Release (New Features)

For new features and enhancements:

1. **Update dependencies** (if needed):

   ```bash
   # Change dependency version in pyproject.toml
   # Upgrade lock with lowest direct resolution
   uv lock --resolution lowest-direct
   ```

2. **Update version in `pyproject.toml`** (if using static versioning)
3. **Update `CHANGELOG.md`**:
   - Move items from "Unreleased" to new version section
   - Update release date
   - Add comprehensive feature descriptions
4. **Update documentation** if new features require it
5. **Commit changes**:

   ```bash
   git add pyproject.toml CHANGELOG.md uv.lock README.md docs/
   git commit -m "chore: prepare for vX.Y.Z release"
   ```

### Major Release (Breaking Changes)

For breaking changes and major overhauls:

1. **Follow all steps from Minor Release**
2. **Update `README.md`** with any breaking changes
3. **Update migration guide** (if applicable)
4. **Test compatibility** with existing Docker images
5. **Commit changes**:

   ```bash
   git add -A
   git commit -m "chore: prepare for vX.Y.Z major release"
   ```

## Creating the Release

### Using GitHub UI (Recommended)

1. **Push all changes**:

   ```bash
   git push origin master
   ```

2. **Create GitHub release**:
   - Go to [GitHub Releases](https://github.com/margusmartsepp/MCP-docker-executor/releases)
   - Click "Create a new release"
   - **Tag version**: `vX.Y.Z` (e.g., `v0.2.0`)
   - **Release title**: Same as tag (e.g., `v0.2.0`)
   - **Description**: Copy relevant section from `CHANGELOG.md`
   - **Target**: `master` branch
   - Click "Publish release"

3. **Package version** will be set automatically from the tag

### Using Command Line (Alternative)

```bash
# Create and push tag
git tag vX.Y.Z
git push origin vX.Y.Z

# Create release using GitHub CLI (if installed)
gh release create vX.Y.Z --title "vX.Y.Z" --notes "Release notes from CHANGELOG.md"
```

## Post-Release

### Verification

1. **Test the release**:

   ```bash
   # Install from PyPI (when available)
   pip install mcp-docker-executor==X.Y.Z

   # Or test from GitHub
   pip install git+https://github.com/margusmartsepp/MCP-docker-executor.git@vX.Y.Z
   ```

2. **Verify Docker image**:

   ```bash
   docker build -t mcp-executor-base:latest .
   docker run --rm mcp-executor-base python --version
   docker run --rm mcp-executor-base node --version
   docker run --rm mcp-executor-base dotnet --version
   ```

3. **Test Claude Desktop integration**:
   - Verify MCP server works with new version
   - Test all available tools
   - Confirm documentation is up-to-date

### Documentation Updates

1. **Update README.md** if needed
2. **Update examples** if new features require it
3. **Update troubleshooting guide** if new issues discovered

### Communication

1. **Update project status** in relevant forums/communities
2. **Notify users** of breaking changes (for major releases)
3. **Update any related documentation** or tutorials

## Version Numbering

Follow [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (X.Y.0): New features, backward compatible
- **PATCH** (X.Y.Z): Bug fixes, backward compatible

## Release Checklist

Before creating any release, ensure:

- [ ] All tests pass (`uv run pytest`)
- [ ] Code quality checks pass (`uv run ruff check . && uv run pyright`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] `CHANGELOG.md` is updated
- [ ] Documentation is current
- [ ] Docker image builds successfully
- [ ] No breaking changes without proper migration guide (for major releases)
- [ ] Version numbers are consistent across all files
- [ ] All changes are committed and pushed

## Emergency Releases

For critical security fixes or urgent bug fixes:

1. **Create hotfix branch**:

   ```bash
   git checkout -b hotfix/vX.Y.Z
   ```

2. **Apply minimal fix** and test thoroughly

3. **Follow standard release process** but with expedited timeline

4. **Merge back to master** and create release

## Rollback Process

If a release has critical issues:

1. **Create new patch release** with fixes
2. **Update documentation** to warn about problematic version
3. **Communicate** the issue to users
4. **Consider deprecating** the problematic version

## Release Notes Template

When creating release notes, include:

```markdown
## What's New in vX.Y.Z

### 🚀 New Features
- Feature 1: Description
- Feature 2: Description

### 🐛 Bug Fixes
- Fix 1: Description
- Fix 2: Description

### 📚 Documentation
- Updated README with new examples
- Added troubleshooting guide

### 🔧 Technical Changes
- Updated dependencies
- Improved error handling

### ⚠️ Breaking Changes (Major releases only)
- Change 1: Migration guide
- Change 2: Migration guide

### 📦 Installation
```bash
# From PyPI (when available)
pip install mcp-docker-executor==X.Y.Z

# From GitHub
pip install git+https://github.com/margusmartsepp/MCP-docker-executor.git@vX.Y.Z
```

### 🔗 Links

- [Full Changelog](https://github.com/margusmartsepp/MCP-docker-executor/compare/vPREVIOUS...vX.Y.Z)
- [Documentation](https://github.com/margusmartsepp/MCP-docker-executor#readme)

## Automation

Consider automating parts of this process:

- **GitHub Actions** for automated testing
- **Dependabot** for dependency updates
- **Release automation** using GitHub CLI
- **Docker image building** and publishing
- **PyPI publishing** (when package is ready)
