# MCP Integration Update

## Changes Made

This update modifies the project to use the official `crewai-tools` MCP integration instead of the custom implementation. The following changes were made:

1. Updated `crew.py` to use `MCPServerAdapter` from `crewai_tools` with `StdioServerParameters` from the `mcp` package.
2. Updated the MCP server configuration format to use `StdioServerParameters` for better type safety and features.
3. Added proper cleanup by calling `mcp_server_adapter.stop()` in a `finally` block in the `LandingPageCrew.run()` method.
4. Added `crewai-tools` with MCP extras and the `mcp` package to project dependencies in `pyproject.toml`.
5. Marked the custom MCP tools implementation as deprecated.

## Benefits of Using the Official Implementation

- Better integration with the CrewAI ecosystem
- Community support for the MCP integration
- More reliable and up-to-date implementation
- Type-safe MCP configuration with `StdioServerParameters`
- Access to thousands of tools from the community-built MCP servers

## Usage Example

### Using Playwright MCP

```python
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter

# Configure MCP server for Playwright
server_params = StdioServerParameters(
    command="npx",
    args=["@playwright/mcp@latest"],
    env=os.environ
)

# Create adapter and get tools
mcp_server_adapter = MCPServerAdapter(server_params)
tools = mcp_server_adapter.tools

# Using with context manager (alternative approach)
with MCPServerAdapter(server_params) as tools:
    # tools is now available for use
    agent = Agent(..., tools=tools)
    # ...
```

### Using PubMed MCP

```python
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
import os

# Configure MCP server for PubMed
server_params = StdioServerParameters(
    command="uvx",
    args=["--quiet", "pubmedmcp@0.1.3"],
    env={"UV_PYTHON": "3.12", **os.environ}
)

# Using with context manager
with MCPServerAdapter(server_params) as pubmed_tools:
    # pubmed_tools is now available for use
    agent = Agent(..., tools=pubmed_tools)
    task = Task(...)
    crew = Crew(..., agents=[agent], tasks=[task])
    crew.kickoff(...)
```

## Installation

After updating, make sure to install the updated dependencies:

```bash
# Using Poetry
poetry install

# Using pip
pip install -e .
```

## Documentation 

For more details on the official CrewAI Tools MCP integration, see:
https://github.com/crewAIInc/crewAI-tools#crewaI-tools-and-mcp 