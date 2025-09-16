"""
Command-line interface for MCP Docker Executor.
"""

import argparse
import asyncio
import sys
from typing import Any

import httpx

from .models import Language


class MCPCLI:
    """Command-line interface for the MCP Docker Executor."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the CLI."""
        self.base_url = base_url

    async def health_check(self) -> bool:
        """Check if the server is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
        except Exception:
            return False

    async def create_image(self, languages: list[str], image_name: str | None = None) -> dict[str, Any]:
        """Create a new Docker image."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/images/create",
                json={
                    "languages": languages,
                    "image_name": image_name,
                    "requirements": {},
                },
            )
            return response.json()

    async def execute_code(self, language: str, code: str, image_id: str | None = None) -> dict[str, Any]:
        """Execute code in a container."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/execute",
                json={"language": language, "code": code, "image_id": image_id},
            )
            return response.json()

    async def get_execution_result(self, execution_id: str) -> dict:
        """Get execution result."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/executions/{execution_id}")
            return response.json()

    async def install_package(
        self,
        image_id: str,
        language: str,
        package_name: str,
        build_new_image: bool = True,
    ) -> dict[str, Any]:
        """Install a package."""
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/packages/install",
                json={
                    "image_id": image_id,
                    "language": language,
                    "package_name": package_name,
                    "build_new_image": build_new_image,
                },
            )
            return response.json()

    async def upload_file(self, filename: str, content: str, language: str) -> dict:
        """Upload a file for execution."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/files/upload",
                json={"filename": filename, "content": content, "language": language},
            )
            return response.json()

    async def list_files(self) -> dict:
        """List uploaded files."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/files")
            return response.json()

    async def delete_file(self, file_id: str) -> dict:
        """Delete an uploaded file."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/files/{file_id}")
            return response.json()

    async def execute_file(self, file_id: str, image_id: str | None = None) -> dict:
        """Execute an uploaded file."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/files/{file_id}/execute",
                json={"file_id": file_id, "image_id": image_id},
            )
            return response.json()


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="MCP Docker Executor CLI")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the MCP server",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Health check command
    subparsers.add_parser("health", help="Check server health")

    # Create image command
    create_parser = subparsers.add_parser("create", help="Create a Docker image")
    create_parser.add_argument(
        "languages",
        nargs="+",
        choices=[lang.value for lang in Language],
        help="Languages to include",
    )
    create_parser.add_argument("--image-name", help="Custom image name")

    # Execute code command
    exec_parser = subparsers.add_parser("exec", help="Execute code")
    exec_parser.add_argument(
        "language",
        choices=[lang.value for lang in Language],
        help="Programming language",
    )
    exec_parser.add_argument("code", help="Code to execute")
    exec_parser.add_argument("--image-id", help="Docker image ID to use")

    # Get execution result command
    result_parser = subparsers.add_parser("result", help="Get execution result")
    result_parser.add_argument("execution_id", help="Execution ID")

    # Install package command
    install_parser = subparsers.add_parser("install-package", help="Install a package")
    install_parser.add_argument("image_id", help="Docker image ID")
    install_parser.add_argument(
        "language",
        choices=[lang.value for lang in Language],
        help="Programming language",
    )
    install_parser.add_argument("package_name", help="Package name to install")
    install_parser.add_argument(
        "--build-new-image",
        action="store_true",
        default=True,
        help="Build new image with package",
    )

    # Upload file command
    upload_parser = subparsers.add_parser("upload-file", help="Upload a file")
    upload_parser.add_argument("filename", help="Filename")
    upload_parser.add_argument("content", help="File content")
    upload_parser.add_argument(
        "language",
        choices=[lang.value for lang in Language],
        help="Programming language",
    )

    # List files command
    subparsers.add_parser("list-files", help="List uploaded files")

    # Delete file command
    delete_parser = subparsers.add_parser("delete-file", help="Delete an uploaded file")
    delete_parser.add_argument("file_id", help="File ID to delete")

    # Execute file command
    exec_file_parser = subparsers.add_parser("exec-file", help="Execute an uploaded file")
    exec_file_parser.add_argument("file_id", help="File ID to execute")
    exec_file_parser.add_argument("--image-id", help="Docker image ID to use")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = MCPCLI(args.base_url)

    try:
        if args.command == "health":
            if await cli.health_check():
                print("✅ Server is healthy")
            else:
                print("❌ Server is not healthy")
                sys.exit(1)

        elif args.command == "create":
            result = await cli.create_image(args.languages, args.image_name)
            if result["success"]:
                print("✅ Image created successfully!")
                print(f"Image ID: {result['image_id']}")
                print(f"Image Name: {result['image_name']}")
            else:
                print(f"❌ Image creation failed: {result['error_message']}")
                sys.exit(1)

        elif args.command == "exec":
            result = await cli.execute_code(args.language, args.code, args.image_id)
            if result["status"] == "running":
                execution_id = result["execution_id"]
                print(f"🔄 Execution started: {execution_id}")

                # Wait for completion
                for _i in range(60):
                    await asyncio.sleep(1)
                    status_result = await cli.get_execution_result(execution_id)
                    if status_result["status"] == "completed":
                        print("✅ Execution completed!")
                        if status_result.get("stdout"):
                            print(f"Output:\n{status_result['stdout']}")
                        if status_result.get("stderr"):
                            print(f"Errors:\n{status_result['stderr']}")
                        break
                    elif status_result["status"] == "failed":
                        error_msg = status_result.get("error_message", "Unknown error")
                        print(f"❌ Execution failed: {error_msg}")
                        sys.exit(1)
                else:
                    print("⏰ Execution timed out")
                    sys.exit(1)
            else:
                error_msg = result.get("error_message", "Unknown error")
                print(f"❌ Execution failed to start: {error_msg}")
                sys.exit(1)

        elif args.command == "result":
            result = await cli.get_execution_result(args.execution_id)
            print(f"Status: {result['status']}")
            if result.get("stdout"):
                print(f"Output:\n{result['stdout']}")
            if result.get("stderr"):
                print(f"Errors:\n{result['stderr']}")
            if result.get("exit_code") is not None:
                print(f"Exit Code: {result['exit_code']}")

        elif args.command == "install-package":
            result = await cli.install_package(args.image_id, args.language, args.package_name, args.build_new_image)
            if result["success"]:
                print("✅ Package installed successfully!")
                if result.get("new_image_id"):
                    print(f"New Image ID: {result['new_image_id']}")
            else:
                print(f"❌ Package installation failed: {result['error_message']}")
                sys.exit(1)

        elif args.command == "upload-file":
            result = await cli.upload_file(args.filename, args.content, args.language)
            if result["success"]:
                print("✅ File uploaded successfully!")
                print(f"File ID: {result['file_id']}")
            else:
                print(f"❌ File upload failed: {result['error_message']}")
                sys.exit(1)

        elif args.command == "list-files":
            result = await cli.list_files()
            print(f"Total files: {result['total_count']}")
            for file_info in result["files"]:
                file_id = file_info["file_id"]
                filename = file_info["filename"]
                language = file_info["language"]
                print(f"- {filename} ({language}) - {file_id}")

        elif args.command == "delete-file":
            result = await cli.delete_file(args.file_id)
            if result["success"]:
                print("✅ File deleted successfully!")
            else:
                print(f"❌ File deletion failed: {result.get('detail', 'Unknown error')}")
                sys.exit(1)

        elif args.command == "exec-file":
            result = await cli.execute_file(args.file_id, args.image_id)
            if result["status"] == "running":
                execution_id = result["execution_id"]
                print(f"🔄 Execution started: {execution_id}")

                # Wait for completion
                for _i in range(60):
                    await asyncio.sleep(1)
                    status_result = await cli.get_execution_result(execution_id)
                    if status_result["status"] == "completed":
                        print("✅ Execution completed!")
                        if status_result.get("stdout"):
                            print(f"Output:\n{status_result['stdout']}")
                        if status_result.get("stderr"):
                            print(f"Errors:\n{status_result['stderr']}")
                        break
                    elif status_result["status"] == "failed":
                        error_msg = status_result.get("error_message", "Unknown error")
                        print(f"❌ Execution failed: {error_msg}")
                        sys.exit(1)
                else:
                    print("⏰ Execution timed out")
                    sys.exit(1)
            else:
                error_msg = result.get("error_message", "Unknown error")
                print(f"❌ Execution failed to start: {error_msg}")
                sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
