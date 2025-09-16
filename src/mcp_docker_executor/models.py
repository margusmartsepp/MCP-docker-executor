"""
Pydantic models for the MCP Docker Executor.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    NODE = "node"
    CSHARP = "csharp"
    BASH = "bash"


class ExecutionStatus(str, Enum):
    """Execution status values."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class SecurityLevel(str, Enum):
    """Security level for code execution."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResourceLimits(BaseModel):
    """Resource limits for container execution."""

    memory_mb: int = Field(default=512, ge=64, le=8192)
    cpu_cores: float = Field(default=1.0, ge=0.1, le=8.0)
    timeout_seconds: int = Field(default=300, ge=10, le=3600)
    network_enabled: bool = Field(default=False)


class CreateImageRequest(BaseModel):
    """Request to create a new Docker image."""

    languages: list[Language] = Field(min_length=1)
    requirements: dict[str, str] = Field(default_factory=dict)
    image_name: str | None = None
    custom_dockerfile: str | None = None
    base_os: str = Field(default="ubuntu:22.04")


class CreateImageResponse(BaseModel):
    """Response from image creation."""

    success: bool
    image_id: str | None = None
    image_name: str | None = None
    build_logs: list[str] = Field(default_factory=list)
    error_message: str | None = None


class ExecuteCodeRequest(BaseModel):
    """Request to execute code in a container."""

    language: Language
    code: str
    image_id: str | None = None
    working_directory: str = Field(default="/workspace")
    environment_variables: dict[str, str] = Field(default_factory=dict)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    input_data: str | None = None


class ExecuteCodeResponse(BaseModel):
    """Response from code execution."""

    execution_id: str
    status: ExecutionStatus
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    error_message: str | None = None
    execution_time_seconds: float | None = None


class FileTransferRequest(BaseModel):
    """Request for file transfer operations."""

    operation: str = Field(
        ..., description="Operation type: upload, download, list, delete, mkdir"
    )
    container_id: str
    remote_path: str
    local_path: str | None = None
    content: str | None = None


class FileTransferResponse(BaseModel):
    """Response from file transfer operations."""

    success: bool
    message: str
    data: Any | None = None


class ExecutionProgress(BaseModel):
    """Progress information for long-running executions."""

    execution_id: str
    status: ExecutionStatus
    progress_percentage: float = Field(ge=0.0, le=100.0)
    current_step: str | None = None
    logs: list[str] = Field(default_factory=list)
    start_time: float
    estimated_completion: float | None = None


class StreamExecutionRequest(BaseModel):
    """Request for streaming execution."""

    language: Language
    code: str
    image_id: str | None = None
    working_directory: str = Field(default="/workspace")
    environment_variables: dict[str, str] = Field(default_factory=dict)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)


class InstallPackageRequest(BaseModel):
    """Request to install a package."""

    image_id: str
    language: Language
    package_name: str
    build_new_image: bool = Field(default=True)
    package_version: str | None = None


class InstallPackageResponse(BaseModel):
    """Response from package installation."""

    success: bool
    new_image_id: str | None = None
    build_logs: list[str] = Field(default_factory=list)
    error_message: str | None = None


class FileUploadRequest(BaseModel):
    """Request to upload a file for execution."""

    filename: str
    content: str
    language: Language
    encoding: str = Field(default="utf-8")
    binary: bool = Field(default=False)


class FileUploadResponse(BaseModel):
    """Response from file upload."""

    success: bool
    file_id: str | None = None
    file_path: str | None = None
    error_message: str | None = None


class FileListResponse(BaseModel):
    """Response containing list of uploaded files."""

    files: list[dict[str, Any]]
    total_count: int


class FileExecutionRequest(BaseModel):
    """Request to execute an uploaded file."""

    file_id: str
    container_id: str | None = None
    image_id: str | None = None
    working_directory: str = Field(default="/workspace")
    environment_variables: dict[str, str] = Field(default_factory=dict)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    input_data: str | None = None
