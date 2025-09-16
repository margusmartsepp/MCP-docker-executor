"""
Docker manager for MCP Docker Executor.
"""

import asyncio
import base64
import json
import logging
import os
import re
import tempfile
import time
from typing import Any

import docker
from docker.errors import DockerException

from .file_manager import FileManager
from .models import (
    CreateImageRequest,
    CreateImageResponse,
    ExecuteCodeRequest,
    ExecuteCodeResponse,
    ExecutionStatus,
    FileExecutionRequest,
    FileListResponse,
    FileUploadRequest,
    FileUploadResponse,
    InstallPackageRequest,
    InstallPackageResponse,
    Language,
    StreamExecutionRequest,
)

logger = logging.getLogger(__name__)


class DockerManager:
    """Manages Docker operations for the MCP server."""

    def __init__(self, client=None):
        """Initialize the Docker manager."""
        self.client = client or docker.from_env()
        self.active_containers: dict[str, Any] = {}
        self.streaming_executions: dict[str, dict] = {}
        self.file_manager = FileManager()

        # Test Docker connection
        try:
            self.client.ping()
            logger.info("Docker connection established successfully")
        except DockerException as e:
            logger.exception("Failed to connect to Docker")
            raise

    async def health_check(self) -> bool:
        """Check if Docker is healthy."""
        try:
            self.client.ping()
            return True
        except DockerException:
            return False

    async def create_image(self, request: CreateImageRequest) -> CreateImageResponse:
        """Create a new Docker image with specified languages and requirements."""
        try:
            # Always use the project's Dockerfile if it exists
            dockerfile_path = os.path.join(os.getcwd(), "Dockerfile")
            if os.path.exists(dockerfile_path):
                with open(dockerfile_path) as f:
                    dockerfile_content = f.read()
                logger.info("Using project's Dockerfile")
            elif request.custom_dockerfile:
                dockerfile_content = request.custom_dockerfile
                logger.info("Using custom Dockerfile")
            else:
                # Fallback to generated Dockerfile if project Dockerfile doesn't exist
                dockerfile_content = self._generate_dockerfile(request)
                logger.info("Using generated Dockerfile")

            # Create temporary directory for build context
            with tempfile.TemporaryDirectory() as temp_dir:
                dockerfile_path = os.path.join(temp_dir, "Dockerfile")
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)

                # Generate image name
                image_name = request.image_name or f"mcp-executor-{int(time.time())}"
                tag = f"{image_name}:latest"

                # Build image
                build_logs = []
                try:
                    image, build_logs = self.client.images.build(
                        path=temp_dir, tag=tag, rm=True, forcerm=True, nocache=True
                    )

                    return CreateImageResponse(
                        image_id=image.id,
                        image_name=image_name,
                        build_logs=[
                            str(log.get("stream", "")) if isinstance(log, dict) and "stream" in log else str(log)
                            for log in build_logs
                        ],
                        success=True,
                    )

                except Exception as e:
                    logger.exception("Failed to build image")
                    return CreateImageResponse(
                        success=False,
                        error_message=f"Build failed: {e!s}",
                        build_logs=[
                            str(log.get("stream", "")) if isinstance(log, dict) and "stream" in log else str(log)
                            for log in build_logs
                        ],
                    )

        except Exception as e:
            logger.exception("Error creating image")
            return CreateImageResponse(success=False, error_message=str(e))

    def _generate_dockerfile(self, request: CreateImageRequest) -> str:
        """Generate a Dockerfile based on the request."""
        dockerfile_lines = [
            f"FROM {request.base_os}",
            "",
            "# Cache busting",
            f"RUN echo 'Cache bust: {int(time.time())}' > /tmp/cache_bust.txt",
            f"RUN echo 'Build time: {int(time.time())}' > /tmp/build_time.txt",
            "",
        ]

        # Add system dependencies
        dockerfile_lines.extend(
            [
                "# Install system dependencies",
                "RUN apt-get update && apt-get install -y \\",
                "    curl \\",
                "    git \\",
                "    build-essential \\",
                "    wget \\",
                "    gnupg \\",
                "    libicu-dev \\",
                "    libssl-dev \\",
                "    && rm -rf /var/lib/apt/lists/*",
                "",
            ]
        )

        # Add language-specific installations
        if Language.NODE in request.languages:
            dockerfile_lines.extend(
                [
                    "# Install Node.js",
                    "RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \\",
                    "    && apt-get install -y nodejs \\",
                    "    && node --version \\",
                    "    && npm --version",
                    "",
                ]
            )

        if Language.CSHARP in request.languages:
            dockerfile_lines.extend(
                [
                    "# Install .NET SDK",
                    "RUN wget https://packages.microsoft.com/config/ubuntu/22.04/\\",
                    "    packages-microsoft-prod.deb \\",
                    "    -O packages-microsoft-prod.deb && \\",
                    "    dpkg -i packages-microsoft-prod.deb && \\",
                    "    rm packages-microsoft-prod.deb && \\",
                    "    apt-get update && \\",
                    "    apt-get install -y dotnet-sdk-8.0 && \\",
                    "    dotnet --version",
                    "",
                ]
            )

        # Add workspace setup
        dockerfile_lines.extend(
            [
                "# Create workspace and user",
                "RUN useradd -ms /bin/bash sandboxuser",
                "RUN mkdir -p /workspace && chown sandboxuser:sandboxuser /workspace",
                "USER sandboxuser",
                "WORKDIR /workspace",
                "",
                "# Default command",
                'CMD ["/bin/bash"]',
            ]
        )

        return "\n".join(dockerfile_lines)

    async def execute_code(self, request: ExecuteCodeRequest) -> ExecuteCodeResponse:
        """Execute code in a Docker container."""
        try:
            # Prepare execution environment
            command, temp_file = await self._prepare_code_execution(request)

            # Create and run container
            container = self.client.containers.create(
                image=request.image_id or "mcp-executor-test:latest",
                environment={
                    "PYTHONUNBUFFERED": "1",
                    "NODE_ENV": "development",
                    **request.environment_variables,
                },
                working_dir=request.working_directory,
                mem_limit=f"{request.resource_limits.memory_mb}m",
                cpu_quota=int(request.resource_limits.cpu_cores * 100000),
                cpu_period=100000,
                network_disabled=False,  # Enable network access
                detach=True,
                stdin_open=True,
                tty=True,
                user="root",  # Use root user for package installation
            )

            container_id = container.id[:8] if container.id else "unknown"
            execution_id = f"exec_{int(time.time())}_{container_id}"
            self.active_containers[execution_id] = container

            # Start container
            container.start()

            # Execute command
            result = container.exec_run(["bash", "-c", command], user="root")

            # Clean up
            container.stop()
            container.remove()
            del self.active_containers[execution_id]

            # Parse result
            stdout = result.output.decode() if result.output else ""
            stderr = ""

            return ExecuteCodeResponse(
                execution_id=execution_id,
                status=ExecutionStatus.COMPLETED if result.exit_code == 0 else ExecutionStatus.FAILED,
                stdout=stdout,
                stderr=stderr,
                exit_code=result.exit_code,
                execution_time_seconds=0.0,
            )

        except Exception as e:
            logger.exception("Error executing code")
            return ExecuteCodeResponse(
                execution_id=f"exec_{int(time.time())}_error",
                status=ExecutionStatus.FAILED,
                error_message=str(e),
            )

    async def _prepare_code_execution(self, request: ExecuteCodeRequest) -> tuple[str, str | None]:
        """Prepare the execution environment for code."""
        if request.language == Language.PYTHON:
            # Encode the Python code in base64 to avoid shell escaping issues
            encoded_code = base64.b64encode(request.code.encode()).decode()
            timestamp = int(time.time())
            command = (
                f"echo '{encoded_code}' | base64 -d > /tmp/exec_{timestamp}.py && "
                f"python3 /tmp/exec_{timestamp}.py && rm /tmp/exec_{timestamp}.py"
            )
            return command, None

        elif request.language == Language.NODE:
            # Encode the Node.js code in base64
            encoded_code = base64.b64encode(request.code.encode()).decode()
            timestamp = int(time.time())
            command = (
                f"echo '{encoded_code}' | base64 -d > /tmp/exec_{timestamp}.js && "
                f"node /tmp/exec_{timestamp}.js && rm /tmp/exec_{timestamp}.js"
            )
            return command, None

        elif request.language == Language.CSHARP:
            # For C#, create a simple console app and compile/run
            encoded_code = base64.b64encode(request.code.encode()).decode()
            command = f"""mkdir -p /tmp/csharp_exec_{int(time.time())} && \\
cd /tmp/csharp_exec_{int(time.time())} && \\
echo '{encoded_code}' | base64 -d > Program.cs && \\
dotnet new console --force && \\
cp Program.cs Program.cs.bak && \\
echo '{encoded_code}' | base64 -d > Program.cs && \\
dotnet run && \\
cd / && \\
rm -rf /tmp/csharp_exec_{int(time.time())}"""
            return command, None

        elif request.language == Language.BASH:
            # For bash, execute directly
            command = request.code
            return command, None

        else:
            raise ValueError(f"Unsupported language: {request.language}")

    # File management methods
    async def upload_file(self, request: FileUploadRequest) -> FileUploadResponse:
        """Upload a file for execution."""
        return await self.file_manager.upload_file(request)

    async def list_uploaded_files(self) -> FileListResponse:
        """List all uploaded files."""
        return await self.file_manager.list_files()

    async def get_uploaded_file(self, file_id: str) -> dict[str, Any] | None:
        """Get details of an uploaded file."""
        return await self.file_manager.get_file(file_id)

    async def delete_uploaded_file(self, file_id: str) -> bool:
        """Delete an uploaded file."""
        return await self.file_manager.delete_file(file_id)

    async def execute_uploaded_file(self, request: FileExecutionRequest) -> ExecuteCodeResponse:
        """Execute an uploaded file."""
        file_info = await self.file_manager.get_file(request.file_id)
        if not file_info:
            return ExecuteCodeResponse(
                execution_id=f"exec_{int(time.time())}_error",
                status=ExecutionStatus.FAILED,
                error_message="File not found",
            )

        # Create execute request from file content
        execute_request = ExecuteCodeRequest(
            language=file_info["language"],
            code=file_info["content"],
            image_id=request.image_id,
            working_directory=request.working_directory,
            environment_variables=request.environment_variables,
            resource_limits=request.resource_limits,
            input_data=request.input_data,
        )

        return await self.execute_code(execute_request)

    async def get_file_manager_stats(self) -> dict[str, Any]:
        """Get file manager statistics."""
        return await self.file_manager.get_stats()

    # Package management methods
    async def install_package(self, request: InstallPackageRequest) -> InstallPackageResponse:
        """Install a package in a Docker image or container."""
        try:
            if request.build_new_image:
                return await self._build_image_with_package(request)
            else:
                return await self._install_package_in_container(request)
        except Exception as e:
            logger.exception("Package installation failed")
            return InstallPackageResponse(success=False, error_message=str(e))

    async def _build_image_with_package(self, request: InstallPackageRequest) -> InstallPackageResponse:
        """Build a new image with the package installed."""
        try:
            # Get the base image
            try:
                base_image = self.client.images.get(request.image_id)
            except docker.errors.ImageNotFound:  # type: ignore[import-untyped]
                return InstallPackageResponse(
                    success=False,
                    error_message=f"Base image not found: {request.image_id}",
                )

            # Generate package installation command
            install_command = self._get_package_install_command(
                request.language, request.package_name, request.package_version
            )

            # Create Dockerfile for package installation
            dockerfile_content = f"""
FROM {request.image_id}
USER root
{install_command}
USER sandboxuser
"""

            # Sanitize package name for Docker tag
            safe_package_name = re.sub(r"[^a-zA-Z0-9-]", "-", request.package_name).lower()
            safe_package_name = re.sub(r"-+", "-", safe_package_name).strip("-")

            # Generate new image name
            new_image_name = f"mcp-executor-with-{safe_package_name}-{int(time.time())}"

            # Build new image
            with tempfile.TemporaryDirectory() as temp_dir:
                dockerfile_path = os.path.join(temp_dir, "Dockerfile")
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile_content)

                image, build_logs = self.client.images.build(
                    path=temp_dir, tag=f"{new_image_name}:latest", rm=True, forcerm=True
                )

                return InstallPackageResponse(
                    success=True,
                    new_image_id=image.id,
                    build_logs=[
                        str(log.get("stream", "")) if isinstance(log, dict) and "stream" in log else str(log)
                        for log in build_logs
                    ],
                )

        except Exception as e:
            logger.exception("Failed to build image with package")
            return InstallPackageResponse(success=False, error_message=f"Build failed: {e!s}")

    async def _install_package_in_container(self, request: InstallPackageRequest) -> InstallPackageResponse:
        """Install package in a running container."""
        try:
            # Find running containers for the image
            containers = self.client.containers.list(filters={"ancestor": request.image_id})
            if not containers:
                return InstallPackageResponse(
                    success=False,
                    error_message="No running containers found for the specified image",
                )

            container = containers[0]  # Use the first running container

            # Get package installation command
            package_spec = (
                f"{request.package_name}=={request.package_version}"
                if request.package_version
                else request.package_name
            )

            if request.language == Language.PYTHON:
                cmd = ["pip", "install", package_spec]
            elif request.language == Language.NODE:
                cmd = ["npm", "install", "-g", package_spec]
            elif request.language == Language.CSHARP:
                cmd = [
                    "bash",
                    "-c",
                    "mkdir -p /workspace && cd /workspace && "
                    + f"dotnet new console --force && dotnet add package {package_spec}",
                ]
            elif request.language == Language.BASH:
                cmd = [
                    "bash",
                    "-c",
                    f"apt-get update && apt-get install -y {package_spec}",
                ]
            else:
                raise ValueError(f"Unsupported language: {request.language}")

            # Execute the installation command as root for npm and C#
            if request.language in [Language.NODE, Language.CSHARP]:
                result = container.exec_run(cmd, user="root")
            else:
                result = container.exec_run(cmd)

            if result.exit_code == 0:
                return InstallPackageResponse(
                    success=True,
                    build_logs=[result.output.decode() if result.output else "Package installed successfully"],
                )
            else:
                output_msg = result.output.decode() if result.output else "Unknown error"
                return InstallPackageResponse(
                    success=False,
                    error_message=f"Package installation failed: {output_msg}",
                )

        except Exception as e:
            logger.exception("Package installation in container failed")
            return InstallPackageResponse(success=False, error_message=f"Package installation failed: {e!s}")

    def _get_package_install_command(
        self, language: Language, package_name: str, package_version: str | None = None
    ) -> str:
        """Get the package installation command for a language."""
        package_spec = f"{package_name}=={package_version}" if package_version else package_name

        if language == Language.PYTHON:
            return f"RUN pip install {package_spec}"
        elif language == Language.NODE:
            return f"RUN npm install -g {package_spec}"
        elif language == Language.CSHARP:
            return f"""RUN mkdir -p /workspace && cd /workspace && \\
dotnet new console --force && \\
dotnet add package {package_spec}"""
        elif language == Language.BASH:
            return f"RUN apt-get update && apt-get install -y {package_spec}"
        else:
            raise ValueError(f"Unsupported language: {language}")

    async def install_package_in_container(
        self,
        container_id: str,
        language: Language,
        package_name: str,
        package_version: str | None = None,
    ) -> bool:
        """Install a package in a specific running container."""
        try:
            container = self.client.containers.get(container_id)

            package_spec = f"{package_name}=={package_version}" if package_version else package_name

            if language == Language.PYTHON:
                cmd = ["pip", "install", package_spec]
            elif language == Language.NODE:
                cmd = ["npm", "install", "-g", package_spec]
            elif language == Language.CSHARP:
                cmd = [
                    "bash",
                    "-c",
                    "mkdir -p /workspace && cd /workspace && "
                    + f"dotnet new console --force && dotnet add package {package_spec}",
                ]
            elif language == Language.BASH:
                cmd = [
                    "bash",
                    "-c",
                    f"apt-get update && apt-get install -y {package_spec}",
                ]
            else:
                raise ValueError(f"Unsupported language: {language}")

            # Execute the command as root for npm and C#
            if language in [Language.NODE, Language.CSHARP]:
                result = container.exec_run(cmd, user="root")
            else:
                result = container.exec_run(cmd)

            if result.exit_code == 0:
                logger.info(f"Successfully installed {package_spec} in container {container_id}")
                return True
            else:
                logger.error(
                    f"Failed to install {package_spec} in container {container_id}: "
                    + f"{result.output.decode() if result.output else 'Unknown error'}"
                )
                return False

        except Exception as e:
            logger.exception(f"Error installing package in container {container_id}")
            return False

    async def start_streaming_execution(self, execution_id: str, request: "StreamExecutionRequest") -> None:
        """Start a streaming execution and store it in the tracking dict."""
        try:
            # Store execution metadata
            self.streaming_executions[execution_id] = {
                "request": request,
                "status": "running",
                "start_time": time.time(),
                "logs": [],
            }

            # Start the execution in the background
            task = asyncio.create_task(self._monitor_streaming_execution(execution_id))
            # Store task reference to prevent garbage collection
            self.streaming_executions[execution_id]["task"] = task

        except Exception as e:
            logger.exception(f"Error starting streaming execution {execution_id}")
            if execution_id in self.streaming_executions:
                self.streaming_executions[execution_id]["status"] = "failed"
                self.streaming_executions[execution_id]["error"] = str(e)

    async def _monitor_streaming_execution(self, execution_id: str) -> None:
        """Monitor a streaming execution and update its status."""
        try:
            execution_data = self.streaming_executions.get(execution_id)
            if not execution_data:
                return

            # Execute the code
            response = await self.execute_code(execution_data["request"])

            # Update execution status
            execution_data["status"] = "completed" if response.status == ExecutionStatus.COMPLETED else "failed"
            execution_data["response"] = response
            execution_data["end_time"] = time.time()

        except Exception as e:
            logger.exception(f"Error monitoring streaming execution {execution_id}")
            if execution_id in self.streaming_executions:
                self.streaming_executions[execution_id]["status"] = "failed"
                self.streaming_executions[execution_id]["error"] = str(e)

    async def get_execution_progress(self, execution_id: str) -> dict:
        """Get the progress of a streaming execution."""
        execution_data = self.streaming_executions.get(execution_id)
        if not execution_data:
            return {"error": "Execution not found"}

        return {
            "execution_id": execution_id,
            "status": execution_data["status"],
            "start_time": execution_data["start_time"],
            "end_time": execution_data.get("end_time"),
            "logs": execution_data.get("logs", []),
            "response": execution_data.get("response"),
            "error": execution_data.get("error"),
        }

    async def stream_execution_logs(self, execution_id: str) -> str:
        """Stream logs for a specific execution."""
        execution_data = self.streaming_executions.get(execution_id)
        if not execution_data:
            return f"data: {json.dumps({'error': 'Execution not found'})}\n\n"

        logs = execution_data.get("logs", [])
        return f"data: {json.dumps({'logs': logs})}\n\n"
