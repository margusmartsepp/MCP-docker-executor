"""
Unit tests for Pydantic models.

These tests verify that the data models are correctly defined and validated.
"""

import pytest
from pydantic import ValidationError

from mcp_docker_executor.models import (
    CreateImageRequest,
    CreateImageResponse,
    ExecuteCodeRequest,
    ExecuteCodeResponse,
    ExecutionStatus,
    FileUploadRequest,
    FileUploadResponse,
    InstallPackageRequest,
    InstallPackageResponse,
    Language,
    ResourceLimits,
    SecurityLevel,
)


class TestModels:
    """Test Pydantic models validation."""

    def test_language_enum(self):
        """Test Language enum values."""
        assert Language.PYTHON == "python"
        assert Language.NODE == "node"
        assert Language.CSHARP == "csharp"
        assert Language.BASH == "bash"

    def test_execution_status_enum(self):
        """Test ExecutionStatus enum values."""
        assert ExecutionStatus.PENDING == "pending"
        assert ExecutionStatus.RUNNING == "running"
        assert ExecutionStatus.COMPLETED == "completed"
        assert ExecutionStatus.FAILED == "failed"
        assert ExecutionStatus.TIMEOUT == "timeout"

    def test_security_level_enum(self):
        """Test SecurityLevel enum values."""
        assert SecurityLevel.LOW == "low"
        assert SecurityLevel.MEDIUM == "medium"
        assert SecurityLevel.HIGH == "high"

    def test_resource_limits_defaults(self):
        """Test ResourceLimits default values."""
        limits = ResourceLimits()

        assert limits.memory_mb == 512
        assert limits.cpu_cores == 1.0
        assert limits.timeout_seconds == 300
        assert not limits.network_enabled

    def test_resource_limits_validation(self):
        """Test ResourceLimits validation."""
        # Valid values
        limits = ResourceLimits(memory_mb=1024, cpu_cores=2.0, timeout_seconds=600, network_enabled=True)

        assert limits.memory_mb == 1024
        assert limits.cpu_cores == 2.0
        assert limits.timeout_seconds == 600
        assert limits.network_enabled

        # Invalid values should raise ValidationError
        with pytest.raises(ValidationError):
            ResourceLimits(memory_mb=32)  # Below minimum (64)

        with pytest.raises(ValidationError):
            ResourceLimits(memory_mb=10000)  # Above maximum (8192)

        with pytest.raises(ValidationError):
            ResourceLimits(cpu_cores=0.05)  # Below minimum (0.1)

        with pytest.raises(ValidationError):
            ResourceLimits(cpu_cores=10.0)  # Above maximum (8.0)

        with pytest.raises(ValidationError):
            ResourceLimits(timeout_seconds=5)  # Below minimum (10)

        with pytest.raises(ValidationError):
            ResourceLimits(timeout_seconds=4000)  # Above maximum (3600)

    def test_create_image_request_validation(self):
        """Test CreateImageRequest validation."""
        # Valid request
        request = CreateImageRequest(languages=[Language.PYTHON, Language.NODE], image_name="test-image")

        assert request.languages == [Language.PYTHON, Language.NODE]
        assert request.image_name == "test-image"
        assert request.requirements == {}
        assert request.base_os == "ubuntu:22.04"

        # Empty languages list should raise ValidationError
        with pytest.raises(ValidationError):
            CreateImageRequest(languages=[])

        # Invalid language should raise ValidationError
        with pytest.raises(ValidationError):
            CreateImageRequest(languages=["invalid_language"])  # type: ignore[arg-type]

    def test_execute_code_request_validation(self):
        """Test ExecuteCodeRequest validation."""
        # Valid request
        request = ExecuteCodeRequest(language=Language.PYTHON, code="print('Hello World!')")

        assert request.language == Language.PYTHON
        assert request.code == "print('Hello World!')"
        assert request.working_directory == "/workspace"
        assert request.environment_variables == {}
        assert request.input_data is None

        # Invalid language should raise ValidationError
        with pytest.raises(ValidationError):
            ExecuteCodeRequest(
                language="invalid_language",  # type: ignore[arg-type][arg-type]
                code="print('Hello World!')",
            )

    def test_file_upload_request_validation(self):
        """Test FileUploadRequest validation."""
        # Valid request
        request = FileUploadRequest(
            filename="test.py",
            content="print('Hello World!')",
            language=Language.PYTHON,
        )

        assert request.filename == "test.py"
        assert request.content == "print('Hello World!')"
        assert request.language == Language.PYTHON
        assert request.encoding == "utf-8"
        assert not request.binary

        # Invalid language should raise ValidationError
        with pytest.raises(ValidationError):
            FileUploadRequest(
                filename="test.py",
                content="print('Hello World!')",
                language="invalid_language",  # type: ignore[arg-type]
            )

    def test_install_package_request_validation(self):
        """Test InstallPackageRequest validation."""
        # Valid request
        request = InstallPackageRequest(image_id="test-image-id", language=Language.PYTHON, package_name="requests")

        assert request.image_id == "test-image-id"
        assert request.language == Language.PYTHON
        assert request.package_name == "requests"
        assert request.build_new_image
        assert request.package_version is None

        # Invalid language should raise ValidationError
        with pytest.raises(ValidationError):
            InstallPackageRequest(
                image_id="test-image-id",
                language="invalid_language",  # type: ignore[arg-type]
                package_name="requests",
            )

    def test_response_models(self):
        """Test response model creation."""
        # CreateImageResponse
        response = CreateImageResponse(success=True, image_id="test-image-id", image_name="test-image")

        assert response.success
        assert response.image_id == "test-image-id"
        assert response.image_name == "test-image"
        assert response.build_logs == []
        assert response.error_message is None

        # ExecuteCodeResponse
        response = ExecuteCodeResponse(
            execution_id="test-exec-id",
            status=ExecutionStatus.COMPLETED,
            stdout="Hello World!",
            exit_code=0,
        )

        assert response.execution_id == "test-exec-id"
        assert response.status == ExecutionStatus.COMPLETED
        assert response.stdout == "Hello World!"
        assert response.exit_code == 0
        assert response.stderr is None
        assert response.error_message is None
        assert response.execution_time_seconds is None

        # FileUploadResponse
        response = FileUploadResponse(success=True, file_id="test-file-id", file_path="/tmp/test.py")

        assert response.success
        assert response.file_id == "test-file-id"
        assert response.file_path == "/tmp/test.py"
        assert response.error_message is None

        # InstallPackageResponse
        response = InstallPackageResponse(
            success=True,
            new_image_id="new-image-id",
            build_logs=["Building image...", "Package installed successfully"],
        )

        assert response.success
        assert response.new_image_id == "new-image-id"
        assert len(response.build_logs) == 2
        assert response.error_message is None

    def test_model_serialization(self):
        """Test model serialization and deserialization."""
        # Create a request
        request = ExecuteCodeRequest(
            language=Language.PYTHON,
            code="print('Hello World!')",
            image_id="test-image",
        )

        # Serialize to dict
        data = request.model_dump()

        assert data["language"] == "python"
        assert data["code"] == "print('Hello World!')"
        assert data["image_id"] == "test-image"
        assert data["working_directory"] == "/workspace"

        # Deserialize from dict
        new_request = ExecuteCodeRequest(**data)

        assert new_request.language == Language.PYTHON
        assert new_request.code == "print('Hello World!')"
        assert new_request.image_id == "test-image"
        assert new_request.working_directory == "/workspace"

    def test_model_json_serialization(self):
        """Test model JSON serialization."""
        request = CreateImageRequest(
            languages=[Language.PYTHON, Language.NODE],
            image_name="test-image",
            requirements={"requests": "2.31.0"},
        )

        # Serialize to JSON
        json_str = request.model_dump_json()

        assert '"languages":["python","node"]' in json_str
        assert '"image_name":"test-image"' in json_str
        assert '"requirements":{"requests":"2.31.0"}' in json_str

        # Deserialize from JSON
        new_request = CreateImageRequest.model_validate_json(json_str)

        assert new_request.languages == [Language.PYTHON, Language.NODE]
        assert new_request.image_name == "test-image"
        assert new_request.requirements == {"requests": "2.31.0"}
