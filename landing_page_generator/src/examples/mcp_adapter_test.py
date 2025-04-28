import asyncio
import sys
import os
import inspect
from pydantic import BaseModel

# Add the src directory to the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_path)

from landing_page_generator.tools.mcp_tools import MCPServerToolProvider

async def test_mcp_adapter():
    print("Testing MCPServerToolProvider and MCPToolAdapter...")
    
    # Sample configuration - this can be adjusted based on your setup
    mcp_server_config = {
        "search": {      
            "command": "npx",
            "args": [
                "@playwright/mcp@latest"
            ]
        }
    }
    
    # Create the provider
    print("Creating MCPServerToolProvider...")
    provider = MCPServerToolProvider(server_config=mcp_server_config)
    
    # Get the tools
    tools = provider.get_tools()
    print(f"Found {len(tools)} tools")
    
    # Print information about each tool
    for i, tool in enumerate(tools):
        print(f"\nTool {i+1}:")
        print(f"  Name: {tool.name}")
        print(f"  Description: {tool.description}")
        
        # Print args schema if available
        if tool.args_schema:
            print(f"  Args Schema: {tool.args_schema.__name__}")
            for field_name, field in tool.args_schema.__fields__.items():
                print(f"    - {field_name}: {field.type_} (required: {field.required})")
                if field.description:
                    print(f"      Description: {field.description}")
    
    # Test a tool if there are any
    if tools:
        test_tool = tools[0]
        print(f"\nTesting tool: {test_tool.name}")
        try:
            # Get the required parameters for the tool
            if test_tool.args_schema:
                # Create an instance with the required parameters
                required_params = {}
                for field_name, field in test_tool.args_schema.__fields__.items():
                    if field.required:
                        if field.type_ == str:
                            if "query" in field_name.lower() or "text" in field_name.lower() or "input" in field_name.lower():
                                required_params[field_name] = "What's the weather like in New York?"
                            else:
                                required_params[field_name] = f"test-{field_name}"
                        elif field.type_ == int:
                            required_params[field_name] = 1
                        elif field.type_ == float:
                            required_params[field_name] = 1.0
                        elif field.type_ == bool:
                            required_params[field_name] = True
                
                print(f"  Running with parameters: {required_params}")
                result = await test_tool._arun(**required_params)
            else:
                # Fallback to simpler query if no schema
                query = {"query": "What's the weather like in New York?"}
                print(f"  Running with default query: {query}")
                result = await test_tool._arun(**query)
                
            print(f"  Result: {result[:100]}..." if len(str(result)) > 100 else f"  Result: {result}")
        except Exception as e:
            print(f"  Error testing tool: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Clean up
    await provider.close()
    print("\nTest completed.")

if __name__ == "__main__":
    asyncio.run(test_mcp_adapter()) 