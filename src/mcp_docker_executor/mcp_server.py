#!/usr/bin/env python3
"""
MCP Server for Docker Code Execution.

This module provides an MCP (Model Context Protocol) server that enables
LLMs to execute code in Docker containers with support for multiple languages.
"""

import logging

from mcp.server.fastmcp import FastMCP

from mcp_docker_executor.docker_manager import DockerManager
from mcp_docker_executor.models import ExecuteCodeRequest, Language

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("mcp-docker-executor")

# Initialize Docker manager
docker_manager = DockerManager()


@mcp.tool()
async def execute_code(
    language: str,
    code: str,
    image_id: str = "debug-test:latest",
    working_directory: str = "/workspace",
    timeout_seconds: int = 300,
) -> str:
    """Execute code in a Docker container with support for Python, Node.js, C#, and Bash.

    Args:
        language: Programming language to execute (python, node, csharp, bash)
        code: Code to execute
        image_id: Docker image ID to use (default: debug-test:latest)
        working_directory: Working directory in container (default: /workspace)
        timeout_seconds: Execution timeout in seconds (default: 300)

    Returns:
        Execution result with status, output, and error information
    """
    try:
        lang_enum = Language(language)

        request = ExecuteCodeRequest(
            language=lang_enum,
            code=code,
            image_id=image_id,
            working_directory=working_directory,
            timeout_seconds=timeout_seconds,
        )

        result = await docker_manager.execute_code(request)

        response_text = f"""Execution Result:
- Execution ID: {result.execution_id}
- Status: {result.status.value}
- Exit Code: {result.exit_code}
- Execution Time: {result.execution_time_seconds:.2f}s

STDOUT:
{result.stdout}

STDERR:
{result.stderr}"""

        if result.error_message:
            response_text += f"\nError: {result.error_message}"

        return response_text

    except Exception as e:
        logger.exception("Error executing code")
        return f"Error executing code: {e!s}"


@mcp.tool()
async def create_image(languages: list[str], image_name: str) -> str:
    """Create a new Docker image with specified language runtimes.

    Args:
        languages: List of languages to include (python, node, csharp, bash)
        image_name: Name for the Docker image

    Returns:
        Image creation result with build logs
    """
    try:
        from mcp_docker_executor.models import CreateImageRequest
        from mcp_docker_executor.models import Language as LangEnum

        lang_enums = [LangEnum(lang) for lang in languages]

        request = CreateImageRequest(languages=lang_enums, image_name=image_name)

        result = await docker_manager.create_image(request)

        if result.success:
            response_text = f"""Image Created Successfully:
- Image ID: {result.image_id}
- Image Name: {image_name}
- Languages: {", ".join(languages)}
- Build Time: {result.build_time_seconds:.2f}s

Build Logs:
{result.build_logs}"""
        else:
            response_text = f"Failed to create image: {result.error_message}"

        return response_text

    except Exception as e:
        logger.exception("Error creating image")
        return f"Error creating image: {e!s}"


@mcp.tool()
async def install_package(
    package_name: str, language: str, image_id: str | None = None, build_new_image: bool = True
) -> str:
    """Install a package in a Docker image or running container.

    Args:
        package_name: Name of the package to install
        language: Language for package manager (python, node, csharp)
        image_id: Docker image ID (optional, will create new image if not provided)
        build_new_image: Whether to build a new image with the package (default: True)

    Returns:
        Package installation result with logs
    """
    try:
        from mcp_docker_executor.models import InstallPackageRequest
        from mcp_docker_executor.models import Language as LangEnum

        lang_enum = LangEnum(language)

        request = InstallPackageRequest(
            package_name=package_name, language=lang_enum, image_id=image_id, build_new_image=build_new_image
        )

        result = await docker_manager.install_package(request)

        if result.success:
            response_text = f"""Package Installed Successfully:
- Package: {package_name}
- Language: {language}
- New Image ID: {result.new_image_id}
- Installation Time: {result.installation_time_seconds:.2f}s

Installation Logs:
{result.installation_logs}"""
        else:
            response_text = f"Failed to install package: {result.error_message}"

        return response_text

    except Exception as e:
        logger.exception("Error installing package")
        return f"Error installing package: {e!s}"


@mcp.tool()
async def upload_file(filename: str, content: str, language: str) -> str:
    """Upload a code file for later execution.

    Args:
        filename: Name of the file
        content: File content
        language: Programming language of the file (python, node, csharp, bash)

    Returns:
        Upload result with file ID
    """
    try:
        from mcp_docker_executor.models import FileUploadRequest
        from mcp_docker_executor.models import Language as LangEnum

        lang_enum = LangEnum(language)

        request = FileUploadRequest(filename=filename, content=content, language=lang_enum)

        result = await docker_manager.upload_file(request)

        response_text = f"""File Uploaded Successfully:
- File ID: {result.file_id}
- Filename: {filename}
- Language: {language}
- Size: {result.size} bytes"""

        return response_text

    except Exception as e:
        logger.exception("Error uploading file")
        return f"Error uploading file: {e!s}"


@mcp.tool()
async def execute_uploaded_file(file_id: str, image_id: str = "debug-test:latest") -> str:
    """Execute a previously uploaded file.

    Args:
        file_id: ID of the uploaded file
        image_id: Docker image ID to use (default: debug-test:latest)

    Returns:
        File execution result
    """
    try:
        from mcp_docker_executor.models import FileExecutionRequest

        request = FileExecutionRequest(file_id=file_id, image_id=image_id)

        result = await docker_manager.execute_uploaded_file(request)

        response_text = f"""File Execution Result:
- Execution ID: {result.execution_id}
- Status: {result.status.value}
- Exit Code: {result.exit_code}
- Execution Time: {result.execution_time_seconds:.2f}s

STDOUT:
{result.stdout}

STDERR:
{result.stderr}"""

        if result.error_message:
            response_text += f"\nError: {result.error_message}"

        return response_text

    except Exception as e:
        logger.exception("Error executing uploaded file")
        return f"Error executing uploaded file: {e!s}"


@mcp.tool()
async def list_files() -> str:
    """List all uploaded files.

    Returns:
        List of uploaded files with details
    """
    try:
        result = await docker_manager.list_uploaded_files()

        if not result.files:
            return "No files uploaded."

        response_text = f"Uploaded Files ({result.total_count}):\n\n"
        for file_info in result.files:
            response_text += f"- ID: {file_info['file_id']}\n"
            response_text += f"  Filename: {file_info['filename']}\n"
            response_text += f"  Language: {file_info['language']}\n"
            response_text += f"  Size: {file_info['size']} bytes\n"
            response_text += f"  Uploaded: {file_info['upload_time']}\n\n"

        return response_text

    except Exception as e:
        logger.exception("Error listing files")
        return f"Error listing files: {e!s}"


@mcp.tool()
async def delete_file(file_id: str) -> str:
    """Delete an uploaded file.

    Args:
        file_id: ID of the file to delete

    Returns:
        Deletion result
    """
    try:
        success = await docker_manager.delete_uploaded_file(file_id)

        if success:
            return f"File {file_id} deleted successfully."
        else:
            return f"Failed to delete file {file_id} or file not found."

    except Exception as e:
        logger.exception("Error deleting file")
        return f"Error deleting file: {e!s}"


@mcp.tool()
async def docker_health() -> str:
    """Check Docker daemon health and get system information.

    Returns:
        Docker health status and system information
    """
    try:
        health_status = await docker_manager.health_check()

        if health_status:
            # Get additional info
            active_containers = len(docker_manager.active_containers)
            available_images = len(docker_manager.client.images.list())

            response_text = f"""Docker Status: ✅ Healthy

System Information:
- Active Containers: {active_containers}
- Available Images: {available_images}
- Docker Connection: ✅ Connected"""
        else:
            response_text = "Docker Status: ❌ Unhealthy\nDocker daemon is not accessible."

        return response_text

    except Exception as e:
        logger.exception("Error checking Docker health")
        return f"Error checking Docker health: {e!s}"


if __name__ == "__main__":
    # Run the server
    mcp.run()
