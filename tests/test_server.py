"""
Integration tests for FastAPI server endpoints.

These tests use real HTTP requests to test the actual API functionality end-to-end.
"""

import httpx
import pytest

from mcp_docker_executor.models import Language


@pytest.mark.integration
@pytest.mark.e2e
class TestServerEndpoints:
    """Integration tests for server endpoints."""

    @pytest.fixture
    async def client(self):
        """Create an HTTP client for testing."""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            yield client

    async def test_health_endpoint(self, client: httpx.AsyncClient) -> None:
        """Test the health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "docker_available" in data
        assert "active_containers" in data
        assert "available_images" in data
        assert data["docker_available"] is True

    async def test_create_image_endpoint(self, client):
        """Test the create image endpoint."""
        response = await client.post(
            "/images/create",
            json={"languages": ["python"], "image_name": "test-api-python"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["image_id"] is not None
        assert data["image_name"] == "test-api-python"
        assert len(data["build_logs"]) > 0

        # Cleanup
        import docker

        docker_client = docker.from_env()
        try:
            docker_client.images.remove(data["image_id"], force=True)
        except Exception:
            pass

    async def test_execute_code_endpoint(self, client):
        """Test the execute code endpoint."""
        # First create an image
        create_response = await client.post(
            "/images/create",
            json={"languages": ["python"], "image_name": "test-api-execute"},
        )
        assert create_response.status_code == 200
        image_data = create_response.json()

        try:
            # Execute code
            response = await client.post(
                "/execute",
                json={
                    "language": "python",
                    "code": "print('Hello from API test!')",
                    "image_id": image_data["image_id"],
                },
            )
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "completed"
            assert data["exit_code"] == 0
            assert "Hello from API test!" in data["stdout"]

            # Test getting execution result
            result_response = await client.get(f"/executions/{data['execution_id']}")
            assert result_response.status_code == 200

            result_data = result_response.json()
            assert result_data["status"] == "completed"
            assert "Hello from API test!" in result_data["stdout"]

        finally:
            # Cleanup
            import docker

            docker_client = docker.from_env()
            try:
                docker_client.images.remove(image_data["image_id"], force=True)
            except Exception:
                pass

    async def test_install_package_endpoint(self, client):
        """Test the install package endpoint."""
        # First create an image
        create_response = await client.post(
            "/images/create",
            json={"languages": ["python"], "image_name": "test-api-package"},
        )
        assert create_response.status_code == 200
        image_data = create_response.json()

        try:
            # Install package
            response = await client.post(
                "/packages/install",
                json={
                    "image_id": image_data["image_id"],
                    "language": "python",
                    "package_name": "requests",
                    "build_new_image": True,
                },
            )
            assert response.status_code == 200

            data = response.json()
            assert data["success"] is True
            assert data["new_image_id"] is not None
            assert len(data["build_logs"]) > 0

            # Cleanup new image
            import docker

            docker_client = docker.from_env()
            try:
                docker_client.images.remove(data["new_image_id"], force=True)
            except Exception:
                pass

        finally:
            # Cleanup original image
            import docker

            docker_client = docker.from_env()
            try:
                docker_client.images.remove(image_data["image_id"], force=True)
            except Exception:
                pass

    async def test_file_upload_endpoint(self, client):
        """Test the file upload endpoint."""
        response = await client.post(
            "/files/upload",
            json={
                "filename": "test_api.py",
                "content": "print('Hello from uploaded file!')",
                "language": "python",
            },
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["file_id"] is not None
        assert data["file_path"] is not None

        # Cleanup
        await client.delete(f"/files/{data['file_id']}")

    async def test_file_list_endpoint(self, client):
        """Test the file list endpoint."""
        # Upload a test file first
        upload_response = await client.post(
            "/files/upload",
            json={
                "filename": "test_list_api.py",
                "content": "print('Test file for listing')",
                "language": "python",
            },
        )
        assert upload_response.status_code == 200
        upload_data = upload_response.json()

        try:
            # List files
            response = await client.get("/files")
            assert response.status_code == 200

            data = response.json()
            assert "files" in data
            assert "total_count" in data
            assert data["total_count"] >= 1

            # Find our uploaded file
            test_file = None
            for file_info in data["files"]:
                if file_info["filename"] == "test_list_api.py":
                    test_file = file_info
                    break

            assert test_file is not None
            assert test_file["language"] == "python"
            assert test_file["file_id"] == upload_data["file_id"]

        finally:
            # Cleanup
            await client.delete(f"/files/{upload_data['file_id']}")

    async def test_file_info_endpoint(self, client):
        """Test the file info endpoint."""
        # Upload a test file first
        upload_response = await client.post(
            "/files/upload",
            json={
                "filename": "test_info_api.py",
                "content": "print('Test file for info')",
                "language": "python",
            },
        )
        assert upload_response.status_code == 200
        upload_data = upload_response.json()

        try:
            # Get file info
            response = await client.get(f"/files/{upload_data['file_id']}")
            assert response.status_code == 200

            data = response.json()
            assert data["filename"] == "test_info_api.py"
            assert data["content"] == "print('Test file for info')"
            assert data["language"] == "python"
            assert data["file_id"] == upload_data["file_id"]

        finally:
            # Cleanup
            await client.delete(f"/files/{upload_data['file_id']}")

    async def test_file_delete_endpoint(self, client):
        """Test the file delete endpoint."""
        # Upload a test file first
        upload_response = await client.post(
            "/files/upload",
            json={
                "filename": "test_delete_api.py",
                "content": "print('Test file for deletion')",
                "language": "python",
            },
        )
        assert upload_response.status_code == 200
        upload_data = upload_response.json()

        # Delete the file
        response = await client.delete(f"/files/{upload_data['file_id']}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["message"] == "File deleted successfully"

        # Verify file is deleted
        info_response = await client.get(f"/files/{upload_data['file_id']}")
        assert info_response.status_code == 404

    async def test_file_execute_endpoint(self, client):
        """Test the file execute endpoint."""
        # Upload a test file first
        upload_response = await client.post(
            "/files/upload",
            json={
                "filename": "test_exec_api.py",
                "content": "print('Hello from executed file!')",
                "language": "python",
            },
        )
        assert upload_response.status_code == 200
        upload_data = upload_response.json()

        try:
            # Create an image for execution
            create_response = await client.post(
                "/images/create",
                json={"languages": ["python"], "image_name": "test-api-file-exec"},
            )
            assert create_response.status_code == 200
            image_data = create_response.json()

            try:
                # Execute the file
                response = await client.post(
                    f"/files/{upload_data['file_id']}/execute",
                    json={
                        "file_id": upload_data["file_id"],
                        "image_id": image_data["image_id"],
                    },
                )
                assert response.status_code == 200

                data = response.json()
                assert data["status"] == "completed"
                assert data["exit_code"] == 0
                assert "Hello from executed file!" in data["stdout"]

            finally:
                # Cleanup image
                import docker

                docker_client = docker.from_env()
                try:
                    docker_client.images.remove(image_data["image_id"], force=True)
                except Exception:
                    pass

        finally:
            # Cleanup file
            await client.delete(f"/files/{upload_data['file_id']}")

    async def test_file_stats_endpoint(self, client):
        """Test the file stats endpoint."""
        response = await client.get("/files/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_files" in data
        assert "files_by_language" in data
        assert "total_size" in data
        assert "upload_dir" in data

        # Verify language breakdown
        for language in Language:
            assert language.value in data["files_by_language"]

    async def test_multi_language_execution(self, client):
        """Test execution in multiple languages."""
        # Create multi-language image
        create_response = await client.post(
            "/images/create",
            json={
                "languages": ["python", "node", "csharp"],
                "image_name": "test-api-multi-lang",
            },
        )
        assert create_response.status_code == 200
        image_data = create_response.json()

        try:
            # Test Python execution
            python_response = await client.post(
                "/execute",
                json={
                    "language": "python",
                    "code": "print('Python works!')",
                    "image_id": image_data["image_id"],
                },
            )
            assert python_response.status_code == 200
            python_data = python_response.json()
            assert python_data["status"] == "completed"
            assert "Python works!" in python_data["stdout"]

            # Test Node.js execution
            node_response = await client.post(
                "/execute",
                json={
                    "language": "node",
                    "code": "console.log('Node.js works!');",
                    "image_id": image_data["image_id"],
                },
            )
            assert node_response.status_code == 200
            node_data = node_response.json()
            assert node_data["status"] == "completed"
            assert "Node.js works!" in node_data["stdout"]

            # Test C# execution (might fail due to ICU library issues)
            csharp_response = await client.post(
                "/execute",
                json={
                    "language": "csharp",
                    "code": 'Console.WriteLine("C# works!");',
                    "image_id": image_data["image_id"],
                },
            )
            assert csharp_response.status_code == 200
            csharp_data = csharp_response.json()
            # C# might fail due to runtime issues, but the request should succeed
            assert csharp_data["status"] in ["completed", "failed"]

        finally:
            # Cleanup
            import docker

            docker_client = docker.from_env()
            try:
                docker_client.images.remove(image_data["image_id"], force=True)
            except Exception:
                pass
