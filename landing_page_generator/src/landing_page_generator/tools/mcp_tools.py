"""
DEPRECATED: This module is no longer in use. 
The implementation has been replaced with the official crewai-tools MCPServerAdapter.

See crew.py for the updated implementation which uses:
    from crewai_tools import MCPServerAdapter
"""

import os
import json
import asyncio
import threading
from crewai.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import Dict, Any, Optional, List, Callable, Type, ClassVar
from pydantic import BaseModel, Field, root_validator


class MCPToolAdapter(BaseTool):
    """
    Adapter class to convert LangChain compatible MCP tools to CrewAI BaseTool.
    This acts as a wrapper for individual tools from the MCP client.
    """
    langchain_tool: Any = None
    
    class Config:
        arbitrary_types_allowed = True
    
    @root_validator(pre=True)
    def set_name_description(cls, values):
        """Set name and description from the langchain tool."""
        if 'langchain_tool' in values and values['langchain_tool'] is not None:
            tool = values['langchain_tool']
            if hasattr(tool, 'name'):
                values['name'] = tool.name
            if hasattr(tool, 'description'):
                values['description'] = tool.description
            
            # Extract schema from langchain tool if available
            if hasattr(tool, 'args_schema') and tool.args_schema is not None:
                values['args_schema'] = tool.args_schema
        
        return values
    
    def _run(self, **kwargs) -> str:
        """
        Run the MCP tool synchronously.
        
        Args:
            **kwargs: Arguments to pass to the tool
            
        Returns:
            str: The response from the MCP tool
        """
        if not self.langchain_tool:
            return "Error: Langchain tool not initialized"
            
        # Handle synchronous calls by creating a new event loop
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.langchain_tool.ainvoke(kwargs))
            return result
        finally:
            loop.close()
    
    async def _arun(self, **kwargs) -> str:
        """
        Run the MCP tool asynchronously.
        
        Args:
            **kwargs: Arguments to pass to the tool
            
        Returns:
            str: The response from the MCP tool
        """
        if not self.langchain_tool:
            return "Error: Langchain tool not initialized"
            
        result = await self.langchain_tool.ainvoke(kwargs)
        return result


class MCPServerToolProvider:
    """
    Provider class that initializes MCP client and returns a list of adapted tools.
    This is not a tool itself but provides multiple tools.
    """
    def __init__(self, server_config=None):
        """
        Initialize the MCP Server Tool Provider.
        
        Args:
            server_config (dict, optional): Configuration for MCP servers.
                Example: {
                    "math": {
                        "command": "python",
                        "args": ["/path/to/math_server.py"],
                        "transport": "stdio",
                    },
                    "weather": {
                        "url": "http://localhost:8000/sse",
                        "transport": "sse",
                    }
                }
        """
        self.server_config = server_config or {}
        self.client = None
        self.tools = []
        self._initialized = False
        
        # Try to initialize immediately if possible
        self._try_initialize()
    
    def _try_initialize(self):
        """Try to initialize the client synchronously if possible."""
        try:
            # Run initialization in a separate thread if we're in an event loop
            if asyncio.get_event_loop().is_running():
                thread = threading.Thread(target=self._thread_initialize)
                thread.daemon = True  # Don't block program exit
                thread.start()
                thread.join(timeout=10)  # Wait for up to 10 seconds
            else:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self._initialize_client())
                finally:
                    loop.close()
        except Exception as e:
            print(f"Warning: Could not initialize MCPServerToolProvider: {e}")
            self._initialized = False
    
    def _thread_initialize(self):
        """Initialize the client in a separate thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._initialize_client())
        finally:
            loop.close()
    
    async def _initialize_client(self):
        """Initialize the MCP client and get available tools."""
        try:
            self.client = MultiServerMCPClient(self.server_config)
            await self.client.__aenter__()
            langchain_tools = self.client.get_tools()
            
            # Adapt each LangChain tool to a CrewAI BaseTool
            self.tools = []
            for tool in langchain_tools:
                # Create adapter instance
                adapter = MCPToolAdapter(langchain_tool=tool)
                self.tools.append(adapter)
                
            self._initialized = True
        except Exception as e:
            print(f"Error initializing MCP client: {e}")
            self._initialized = False
            raise
    
    def get_tools(self) -> List[BaseTool]:
        """
        Get all available MCP tools adapted for CrewAI.
        
        Returns:
            List[BaseTool]: List of adapted MCP tools
        """
        if not self._initialized:
            print("Warning: MCP tools not initialized. Returning empty list.")
        return self.tools
    
    async def close(self):
        """Close the MCP client connection."""
        if self.client:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception as e:
                print(f"Error closing MCP client: {e}")
            finally:
                self.client = None


class MCPServerTool(BaseTool):
    """
    DEPRECATED: This class is maintained for backward compatibility.
    Use MCPServerToolProvider instead.
    
    This tool will be removed in a future update.
    """
    name: str = "mcp_tools_deprecated"
    description: str = "DEPRECATED: Use the tools from MCPServerToolProvider.get_tools() instead"
    
    def __init__(self, server_config=None, **kwargs):
        """
        Initialize the deprecated MCP Server Tool.
        
        Args:
            server_config (dict, optional): Configuration for MCP servers.
        """
        import warnings
        warnings.warn(
            "MCPServerTool is deprecated. Use MCPServerToolProvider.get_tools() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        super().__init__(**kwargs)
        self.server_config = server_config or {}
        self.provider = MCPServerToolProvider(server_config=server_config)
    
    def _run(self, query: str, server_name: str = None) -> str:
        """
        Deprecated synchronous method. Raises NotImplementedError.
        """
        raise NotImplementedError(
            "MCPServerTool is deprecated. Use tools from MCPServerToolProvider.get_tools() instead."
        )
        
    async def _arun(self, query: str, server_name: str = None) -> str:
        """
        Deprecated asynchronous method. Raises NotImplementedError.
        """
        raise NotImplementedError(
            "MCPServerTool is deprecated. Use tools from MCPServerToolProvider.get_tools() instead."
        ) 