import os
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

async def main():
    # Set up your OpenAI API key (if not set in environment)
    # os.environ["OPENAI_API_KEY"] = "your-api-key"
    
    # Initialize the LLM
    model = ChatOpenAI(model="gpt-4o")
    
    # Configure MCP servers
    server_config = {
        "math": {
            "command": "python",
            # Update this path to your math_server.py file
            "args": ["/path/to/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            # Make sure your weather server is running on port 8000
            "url": "http://localhost:8000/sse",
            "transport": "sse",
        }
    }
    
    # Run examples using the MCP client
    async with MultiServerMCPClient(server_config) as client:
        # Create the agent with MCP tools
        agent = create_react_agent(model, client.get_tools())
        
        # Example 1: Math calculation
        print("Running math example...")
        math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        print("\nMath response:")
        print(math_response)
        
        # Example 2: Weather information
        print("\nRunning weather example...")
        weather_response = await agent.ainvoke({"messages": "what is the weather in nyc?"})
        print("\nWeather response:")
        print(weather_response)

if __name__ == "__main__":
    asyncio.run(main()) 