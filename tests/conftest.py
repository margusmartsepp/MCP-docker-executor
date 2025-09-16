"""
Pytest configuration and fixtures for MCP Docker Executor tests.

IMPORTANT: This project uses INTEGRATION TESTS and E2E TESTS only.
We do NOT write unit tests - all tests should use real Docker containers
and test the actual functionality end-to-end.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest

from mcp_docker_executor.docker_manager import DockerManager
from mcp_docker_executor.models import CreateImageRequest, Language


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def docker_manager() -> AsyncGenerator[DockerManager, None]:
    """Create a Docker manager instance for testing."""
    manager = DockerManager()

    # Verify Docker is available
    if not await manager.health_check():
        pytest.skip("Docker is not available")

    yield manager


@pytest.fixture
async def test_image_id(docker_manager: DockerManager) -> AsyncGenerator[str, None]:
    """Create a test Docker image with all languages."""
    request = CreateImageRequest(
        languages=[Language.PYTHON, Language.NODE, Language.CSHARP],
        image_name="test-multi-lang",
    )

    response = await docker_manager.create_image(request)
    if not response.success or not response.image_id:
        pytest.skip(f"Failed to create test image: {response.error_message}")

    yield response.image_id

    # Cleanup: Remove the test image
    try:
        docker_manager.client.images.remove(response.image_id, force=True)  # type: ignore[attr-defined]
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
async def python_image_id(docker_manager: DockerManager) -> AsyncGenerator[str, None]:
    """Create a Python-only test image."""
    request = CreateImageRequest(languages=[Language.PYTHON], image_name="test-python")

    response = await docker_manager.create_image(request)
    if not response.success or not response.image_id:
        pytest.skip(f"Failed to create Python image: {response.error_message}")

    yield response.image_id

    # Cleanup
    try:
        docker_manager.client.images.remove(response.image_id, force=True)  # type: ignore[attr-defined]
    except Exception:
        pass


@pytest.fixture
async def node_image_id(docker_manager: DockerManager) -> AsyncGenerator[str, None]:
    """Create a Node.js-only test image."""
    request = CreateImageRequest(languages=[Language.NODE], image_name="test-node")

    response = await docker_manager.create_image(request)
    if not response.success or not response.image_id:
        pytest.skip(f"Failed to create Node.js image: {response.error_message}")

    yield response.image_id

    # Cleanup
    try:
        docker_manager.client.images.remove(response.image_id, force=True)  # type: ignore[attr-defined]
    except Exception:
        pass


@pytest.fixture
async def csharp_image_id(docker_manager: DockerManager) -> AsyncGenerator[str, None]:
    """Create a C#-only test image."""
    request = CreateImageRequest(languages=[Language.CSHARP], image_name="test-csharp")

    response = await docker_manager.create_image(request)
    if not response.success or not response.image_id:
        pytest.skip(f"Failed to create C# image: {response.error_message}")

    yield response.image_id

    # Cleanup
    try:
        docker_manager.client.images.remove(response.image_id, force=True)  # type: ignore[attr-defined]
    except Exception:
        pass


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Modify test collection to add default markers."""
    for item in items:
        # Add integration marker by default if no specific marker is present
        if not any(marker.name in ["unit", "integration", "e2e"] for marker in item.iter_markers()):
            item.add_marker(pytest.mark.integration)

        # Add docker marker for tests that use Docker
        if "docker_manager" in item.fixturenames or "test_image_id" in item.fixturenames:
            item.add_marker(pytest.mark.docker)


def pytest_configure(config: Any) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
