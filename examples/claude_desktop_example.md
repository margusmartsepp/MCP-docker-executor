# Claude Desktop Integration Example

This document demonstrates how to use the MCP Docker Executor with Claude Desktop through a real-world example.

## Setup

1. **Install the MCP server in Claude Desktop**:

   ```bash
   uv run mcp install src/mcp_docker_executor/mcp_server.py
   ```

2. **Restart Claude Desktop** to load the new MCP server.

3. **Verify connection** - You should see the MCP Docker Executor tools available in Claude Desktop.

## Example: Fibonacci Function Implementation

### User Prompt

> "Can you write a Python Fibonacci function and run it with mcp-docker-executor?"

### Claude's Response

I'll create Python Fibonacci functions and execute them using the MCP Docker Executor. Let me write efficient iterative implementations and run them in a Docker container.

### Generated Code

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number using iterative approach."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return b

def fibonacci_sequence(n):
    """Generate Fibonacci sequence up to n terms."""
    if n <= 0:
        return []

    sequence = []
    a, b = 0, 1

    for i in range(n):
        if i == 0:
            sequence.append(0)
        elif i == 1:
            sequence.append(1)
        else:
            sequence.append(a + b)
            a, b = b, a + b

    return sequence

# Test the functions
print("Testing Fibonacci functions:")
print("-" * 30)

# Test individual numbers
test_numbers = [0, 1, 5, 10, 15]
for num in test_numbers:
    result = fibonacci(num)
    print(f"fibonacci({num}) = {result}")

print("\nFibonacci sequence (first 15 numbers):")
seq = fibonacci_sequence(15)
print(seq)
```

### Execution Result

- **Execution ID**: `exec_1758067574_b0bc8347`
- **Status**: `completed`
- **Exit Code**: `0`
- **Execution Time**: `0.00s`

### Output

```text
Testing Fibonacci functions:
------------------------------
fibonacci(0) = 0
fibonacci(1) = 1
fibonacci(5) = 5
fibonacci(10) = 55
fibonacci(15) = 610

Fibonacci sequence (first 15 numbers):
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
```

### Analysis

Perfect! The functions executed successfully in the Docker container. The iterative approach is efficient and handles edge cases properly. The results show:

- **Individual Fibonacci numbers**: F(0)=0, F(1)=1, F(5)=5, F(10)=55, F(15)=610
- **Complete sequence**: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]

## Available Tools in Claude Desktop

When connected, you'll have access to these tools:

- **`execute_code`** - Execute Python, Node.js, C#, or Bash code
- **`create_image`** - Create custom Docker images with specific runtimes
- **`install_package`** - Install packages (pip, npm, nuget, apt)
- **`upload_file`** - Upload and manage code files
- **`execute_uploaded_file`** - Run uploaded files
- **`list_files`** - List all uploaded files
- **`delete_file`** - Remove uploaded files
- **`docker_health`** - Check Docker connection status

## More Example Prompts

### Python Examples

- "Write a Python function to sort a list using quicksort and test it with mcp-docker-executor"
- "Create a Python script that reads a CSV file and calculates statistics, then run it"
- "Write a Python web scraper using requests and beautifulsoup, test it with some sample data"

### Node.js Examples

- "Write a Node.js function that processes JSON data and run it with mcp-docker-executor"
- "Create a Node.js script that uses async/await to fetch data from an API"

### C# Examples

- "Write a C# class that implements a binary tree and test it with mcp-docker-executor"
- "Create a C# console application that processes command line arguments"

### Multi-language Examples

- "Write the same algorithm in Python, Node.js, and C#, then compare their performance using mcp-docker-executor"
- "Create a simple REST API in Python and test it with curl commands"

## Tips for Claude Desktop Usage

1. **Be specific about language**: Always specify the programming language when requesting code execution
2. **Include test cases**: Ask Claude to include test cases and examples in the generated code
3. **Request explanations**: Ask for explanations of the results and any optimization opportunities
4. **Use file uploads**: For complex code, consider asking Claude to upload files for better organization
5. **Test edge cases**: Ask Claude to test with various inputs including edge cases
6. **Performance analysis**: Request timing information and complexity analysis
7. **Error handling**: Ask Claude to include proper error handling in the generated code

## Troubleshooting

### MCP Server Not Appearing

If the MCP server doesn't appear in Claude Desktop:

1. **Check the configuration file**:

   ```bash
   Get-Content "$env:APPDATA\Claude\claude_desktop_config.json"
   ```

2. **Verify the Python path**:

   ```bash
   uv run python -c "import sys; print(sys.executable)"
   ```

3. **Test the server manually**:

   ```bash
   uv run python -m mcp_docker_executor.mcp_server
   ```

4. **Restart Claude Desktop** completely after configuration changes

### Execution Failures

If code execution fails:

1. **Check Docker status**: Ensure Docker Desktop is running
2. **Verify image exists**: Make sure the base Docker image is built
3. **Check resource limits**: Ensure sufficient system resources are available
4. **Review error messages**: Look at the detailed error output for specific issues

### Connection Issues

If you see connection errors:

1. **Check firewall settings**: Ensure no firewall is blocking the connection
2. **Verify file paths**: Ensure all file paths in the configuration are correct
3. **Check permissions**: Ensure the user has proper permissions to run Docker commands
4. **Review logs**: Check both Claude Desktop and MCP server logs for detailed error information
