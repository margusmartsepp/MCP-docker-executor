"""
FastAPI server for MCP Docker Executor.
"""

import asyncio
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .docker_manager import DockerManager
from .models import (
    CreateImageRequest,
    CreateImageResponse,
    ExecuteCodeRequest,
    ExecuteCodeResponse,
    FileExecutionRequest,
    FileListResponse,
    FileUploadRequest,
    FileUploadResponse,
    InstallPackageRequest,
    InstallPackageResponse,
    StreamExecutionRequest,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global MCP server instance
mcp_server = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global mcp_server

    # Startup
    logger.info("Starting MCP Docker Executor server...")
    mcp_server = MCPDockerExecutor()
    await mcp_server.startup()
    logger.info("MCP Docker Executor server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down MCP Docker Executor server...")
    if mcp_server:
        await mcp_server.shutdown()


app = FastAPI(
    title="MCP Docker Executor",
    description="A Python-based Master Control Program server for Docker automation",
    version="0.1.0",
    lifespan=lifespan,
)


class MCPDockerExecutor:
    """Main MCP Docker Executor server."""

    def __init__(self):
        """Initialize the MCP server."""
        self.docker_manager = DockerManager()
        self.executions: dict[str, dict[str, Any]] = {}

    async def startup(self):
        """Startup the MCP server."""
        # Check Docker health
        if not await self.docker_manager.health_check():
            raise RuntimeError("Docker is not available")

    async def shutdown(self):
        """Shutdown the MCP server."""
        # Clean up any running containers
        for execution_id, container in self.docker_manager.active_containers.items():
            try:
                container.stop()
                container.remove()
            except Exception as e:
                logger.warning("Failed to clean up container %s", execution_id)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    docker_healthy = await mcp_server.docker_manager.health_check()

    # Get additional Docker info
    active_containers = len(mcp_server.docker_manager.active_containers)
    available_images = len(mcp_server.docker_manager.client.images.list())

    return {
        "status": "healthy" if docker_healthy else "unhealthy",
        "docker_available": docker_healthy,
        "timestamp": time.time(),
        "active_containers": active_containers,
        "available_images": available_images,
    }


@app.post("/images/create", response_model=CreateImageResponse)
async def create_image(request: CreateImageRequest):
    """Create a new Docker image."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    return await mcp_server.docker_manager.create_image(request)


@app.post("/execute", response_model=ExecuteCodeResponse)
async def execute_code(request: ExecuteCodeRequest):
    """Execute code in a Docker container."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    # Execute code
    result = await mcp_server.docker_manager.execute_code(request)

    # Store execution result
    mcp_server.executions[result.execution_id] = {
        "status": result.status,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "error_message": result.error_message,
        "execution_time_seconds": result.execution_time_seconds,
        "timestamp": time.time(),
    }

    return result


@app.get("/executions/{execution_id}")
async def get_execution_result(execution_id: str):
    """Get execution result."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    if execution_id not in mcp_server.executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    return mcp_server.executions[execution_id]


@app.post("/packages/install", response_model=InstallPackageResponse)
async def install_package(request: InstallPackageRequest):
    """Install a package in a Docker image or container."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    return await mcp_server.docker_manager.install_package(request)


@app.post("/files/upload", response_model=FileUploadResponse)
async def upload_file(request: FileUploadRequest):
    """Upload a file for execution."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    return await mcp_server.docker_manager.upload_file(request)


@app.get("/files", response_model=FileListResponse)
async def list_files():
    """List all uploaded files."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    return await mcp_server.docker_manager.list_uploaded_files()


@app.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """Get file information."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    file_info = await mcp_server.docker_manager.get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")

    return file_info


@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    success = await mcp_server.docker_manager.delete_uploaded_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")

    return {"success": True, "message": "File deleted successfully"}


@app.post("/files/{file_id}/execute", response_model=ExecuteCodeResponse)
async def execute_file(file_id: str, request: FileExecutionRequest):
    """Execute an uploaded file."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    request.file_id = file_id
    return await mcp_server.docker_manager.execute_uploaded_file(request)


@app.get("/files/stats")
async def get_file_stats():
    """Get file manager statistics."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    return await mcp_server.docker_manager.get_file_manager_stats()


@app.post("/execute/stream")
async def start_streaming_execution(request: StreamExecutionRequest):
    """Start a streaming execution."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    execution_id = f"stream_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    # Start streaming execution
    await mcp_server.docker_manager.start_streaming_execution(execution_id, request)

    return {"execution_id": execution_id, "status": "started"}


@app.get("/executions/{execution_id}/progress")
async def get_execution_progress(execution_id: str):
    """Get execution progress."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    progress = await mcp_server.docker_manager.get_execution_progress(execution_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Execution not found")

    return progress


@app.get("/executions/{execution_id}/stream")
async def stream_execution_logs(execution_id: str):
    """Stream execution logs."""
    if not mcp_server:
        raise HTTPException(status_code=503, detail="Server not ready")

    async def generate_logs():
        while True:
            progress = await mcp_server.docker_manager.get_execution_progress(execution_id)
            if not progress:
                break

            if progress.get("status") in ["completed", "failed"]:
                yield f"data: {json.dumps(progress)}\n\n"
                break

            yield f"data: {json.dumps(progress)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(
        generate_logs(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
