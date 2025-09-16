#!/usr/bin/env python3
"""
Comprehensive demonstration of MCP Docker Executor features.

This script demonstrates:
1. Image creation with multiple languages
2. Package installation (Python, Node.js, C#)
3. File upload and management
4. Code execution with installed packages
5. File execution
"""

import asyncio
from typing import Any

import httpx

SERVER_URL = "http://localhost:8000"


async def create_image(languages: list[str]) -> str:
    """Create a Docker image with specified languages."""
    print(f"🔨 Creating image with languages: {', '.join(languages)}")

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{SERVER_URL}/images/create",
            json={
                "languages": languages,
                "image_name": f"demo-{'-'.join(languages)}",
                "requirements": {},
            },
        )
        response.raise_for_status()

        result = response.json()
        if result["success"]:
            print(f"✅ Image created: {result['image_id'][:12]}...")
            return result["image_id"]
        else:
            raise Exception(f"Image creation failed: {result['error_message']}")


async def install_package(image_id: str, language: str, package_name: str) -> str:
    """Install a package in an image and return the new image ID."""
    print(f"📦 Installing {package_name} for {language}")

    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{SERVER_URL}/packages/install",
            json={
                "image_id": image_id,
                "language": language,
                "package_name": package_name,
                "build_new_image": True,
            },
        )
        response.raise_for_status()

        result = response.json()
        if result["success"]:
            print(f"✅ Package {package_name} installed successfully")
            return result["new_image_id"]
        else:
            raise Exception(f"Package installation failed: {result['error_message']}")


async def execute_code(image_id: str, language: str, code: str, expected_output: str | None = None) -> bool:
    """Execute code and verify the output."""
    print(f"🚀 Executing {language} code...")

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{SERVER_URL}/execute",
            json={
                "image_id": image_id,
                "language": language,
                "code": code,
                "resource_limits": {"network_enabled": True},
            },
        )
        response.raise_for_status()

        result = response.json()
        execution_id = result["execution_id"]

        # Poll for completion
        for _i in range(60):
            await asyncio.sleep(1)
            status_response = await client.get(f"{SERVER_URL}/executions/{execution_id}")
            status_response.raise_for_status()
            status = status_response.json()

            if status["status"] == "completed":
                print(f"✅ {language} execution completed!")
                print(f"Output: {status['stdout']}")

                if expected_output and expected_output not in status["stdout"]:
                    print(f"❌ Expected output '{expected_output}' not found")
                    return False

                return True
            elif status["status"] == "failed":
                print(f"❌ {language} execution failed: {status.get('error_message', 'Unknown error')}")
                print(f"Output: {status['stdout']}")
                print(f"Errors: {status['stderr']}")
                return False

        print(f"⏰ {language} execution timed out")
        return False


async def upload_file(filename: str, content: str, language: str) -> str:
    """Upload a file and return the file ID."""
    print(f"📁 Uploading {filename} ({language})")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVER_URL}/files/upload",
            json={"filename": filename, "content": content, "language": language},
        )
        response.raise_for_status()

        result = response.json()
        if result["success"]:
            print(f"✅ File uploaded: {result['file_id']}")
            return result["file_id"]
        else:
            raise Exception(f"File upload failed: {result['error_message']}")


async def execute_file(file_id: str, image_id: str) -> bool:
    """Execute an uploaded file."""
    print(f"🎯 Executing uploaded file: {file_id}")

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{SERVER_URL}/files/{file_id}/execute",
            json={"file_id": file_id, "image_id": image_id},
        )
        response.raise_for_status()

        result = response.json()
        execution_id = result["execution_id"]

        # Poll for completion
        for _i in range(60):
            await asyncio.sleep(1)
            status_response = await client.get(f"{SERVER_URL}/executions/{execution_id}")
            status_response.raise_for_status()
            status = status_response.json()

            if status["status"] == "completed":
                print("✅ File execution completed!")
                print(f"Output: {status['stdout']}")
                return True
            elif status["status"] == "failed":
                print(f"❌ File execution failed: {status.get('error_message', 'Unknown error')}")
                print(f"Output: {status['stdout']}")
                print(f"Errors: {status['stderr']}")
                return False

        print("⏰ File execution timed out")
        return False


async def list_files() -> dict[str, Any]:
    """List uploaded files."""
    print("📋 Listing uploaded files...")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_URL}/files")
        response.raise_for_status()

        result = response.json()
        print(f"Total files: {result['total_count']}")

        for file_info in result["files"]:
            print(f"  - {file_info['filename']} ({file_info['language']}) - {file_info['file_id'][:8]}...")

        return result


async def delete_file(file_id: str) -> bool:
    """Delete an uploaded file."""
    print(f"🗑️ Deleting file: {file_id}")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{SERVER_URL}/files/{file_id}")
        response.raise_for_status()

        result = response.json()
        if result["success"]:
            print("✅ File deleted successfully")
            return True
        else:
            print(f"❌ File deletion failed: {result.get('detail', 'Unknown error')}")
            return False


async def get_file_stats() -> dict[str, Any]:
    """Get file manager statistics."""
    print("📊 Getting file statistics...")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_URL}/files/stats")
        response.raise_for_status()

        result = response.json()
        print(f"Total files: {result['total_files']}")
        print(f"Total size: {result['total_size']} bytes")
        print("Files by language:")
        for lang, count in result["files_by_language"].items():
            print(f"  - {lang}: {count} files")

        return result


async def main():
    """Main demonstration function."""
    print("🎉 MCP Docker Executor - Comprehensive Feature Demo")
    print("=" * 60)

    try:
        # 1. Create base image with all languages
        base_image_id = await create_image(["python", "node", "csharp"])

        # 2. Test Python package management
        print("\n🐍 Python Package Management")
        print("-" * 30)

        python_code = """
import requests
try:
    response = requests.get('https://httpbin.org/json')
    print(f"✅ Requests library works! Status: {response.status_code}")
    print(f"Response keys: {list(response.json().keys())}")
except Exception as e:
    print(f"⚠️ Network request failed (expected): {e}")
    print("✅ Requests library is installed and imported successfully!")
"""

        # Install requests package
        python_image_id = await install_package(base_image_id, "python", "requests")

        # Execute code with requests
        await execute_code(python_image_id, "python", python_code, "Requests library")

        # 3. Test Node.js package management
        print("\n🟢 Node.js Package Management")
        print("-" * 30)

        node_code = """
const _ = require('lodash');
const numbers = [1, 2, 3, 4, 5];
const doubled = _.map(numbers, n => n * 2);
const sum = _.sum(doubled);
console.log(`✅ Lodash library works!`);
console.log(`Original: ${JSON.stringify(numbers)}`);
console.log(`Doubled: ${JSON.stringify(doubled)}`);
console.log(`Sum: ${sum}`);
"""

        # Install lodash package
        node_image_id = await install_package(base_image_id, "node", "lodash")

        # Execute code with lodash
        await execute_code(node_image_id, "node", node_code, "Lodash library")

        # 4. Test C# package management
        print("\n🔵 C# Package Management")
        print("-" * 30)

        csharp_code = """
using Newtonsoft.Json;
using System;

public class Program
{
    public static void Main(string[] args)
    {
        var data = new { Name = "Test", Value = 42 };
        var json = JsonConvert.SerializeObject(data);
        Console.WriteLine($"✅ Newtonsoft.Json library works!");
        Console.WriteLine($"Serialized: {json}");

        var deserialized = JsonConvert.DeserializeObject(json);
        Console.WriteLine($"Deserialized: {deserialized}");
    }
}
"""

        # Install Newtonsoft.Json package
        csharp_image_id = await install_package(base_image_id, "csharp", "Newtonsoft.Json")

        # Execute code with Newtonsoft.Json
        await execute_code(csharp_image_id, "csharp", csharp_code, "Newtonsoft.Json")

        # 5. Test file management
        print("\n📁 File Management")
        print("-" * 30)

        # Upload Python file
        python_file_content = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def combinations(n, r):
    if r > n or r < 0:
        return 0
    return factorial(n) // (factorial(r) * factorial(n - r))

print("Python Combinations Calculator")
print("=" * 30)
print(f"factorial(5) = {factorial(5)}")
print(f"combinations(5, 2) = {combinations(5, 2)}")
print(f"combinations(10, 3) = {combinations(10, 3)}")
print("✅ Python combinations calculation completed!")
"""

        python_file_id = await upload_file("combinations.py", python_file_content, "python")

        # Upload Node.js file
        node_file_content = """
function factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

function combinations(n, r) {
    if (r > n || r < 0) {
        return 0;
    }
    return factorial(n) / (factorial(r) * factorial(n - r));
}

console.log("Node.js Combinations Calculator");
console.log("=" * 30);
console.log(`factorial(5) = ${factorial(5)}`);
console.log(`combinations(5, 2) = ${combinations(5, 2)}`);
console.log(`combinations(10, 3) = ${combinations(10, 3)}`);
console.log("✅ Node.js combinations calculation completed!");
"""

        node_file_id = await upload_file("combinations.js", node_file_content, "node")

        # Upload C# file
        csharp_file_content = """
using System;

public class Program
{
    public static long Factorial(int n)
    {
        if (n <= 1)
        {
            return 1;
        }
        return n * Factorial(n - 1);
    }

    public static long Combinations(int n, int r)
    {
        if (r > n || r < 0)
        {
            return 0;
        }
        return Factorial(n) / (Factorial(r) * Factorial(n - r));
    }

    public static void Main(string[] args)
    {
        Console.WriteLine("C# Combinations Calculator");
        Console.WriteLine("=" * 30);
        Console.WriteLine($"factorial(5) = {Factorial(5)}");
        Console.WriteLine($"combinations(5, 2) = {Combinations(5, 2)}");
        Console.WriteLine($"combinations(10, 3) = {Combinations(10, 3)}");
        Console.WriteLine("✅ C# combinations calculation completed!");
    }
}
"""

        csharp_file_id = await upload_file("combinations.cs", csharp_file_content, "csharp")

        # List files
        await list_files()

        # Execute uploaded files
        print("\n🎯 Executing Uploaded Files")
        print("-" * 30)

        await execute_file(python_file_id, python_image_id)
        await execute_file(node_file_id, node_image_id)
        await execute_file(csharp_file_id, csharp_image_id)

        # Get file statistics
        await get_file_stats()

        # Cleanup files
        print("\n🧹 Cleanup")
        print("-" * 30)

        await delete_file(python_file_id)
        await delete_file(node_file_id)
        await delete_file(csharp_file_id)

        # Final statistics
        await get_file_stats()

        print("\n🎉 Demo completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
