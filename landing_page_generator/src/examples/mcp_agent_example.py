import os
import asyncio
from crewai import Agent, Task, Crew
from crewai.agent import CrewAgentExecutor
from landing_page_generator.tools.mcp_tools import MCPServerToolProvider

async def main():
    # Configure MCP server tool
    mcp_server_config = {
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
    
    # Create MCP server tool provider and get individual tools
    mcp_provider = MCPServerToolProvider(server_config=mcp_server_config)
    mcp_tools = mcp_provider.get_tools()
    
    # Create an agent with the MCP tools
    data_analyst = Agent(
        role="Data Analyst",
        goal="Provide accurate data and calculations",
        backstory="You are an expert data analyst with access to specialized computational tools.",
        verbose=True,
        allow_delegation=False,
        tools=mcp_tools  # Pass the list of tools directly
    )
    
    # Create tasks that use the MCP server
    math_task = Task(
        description="Calculate (3 + 5) x 12 using the math server",
        agent=data_analyst,
        expected_output="The result of the calculation with step-by-step explanation"
    )
    
    weather_task = Task(
        description="Get the current weather in New York City using the weather server",
        agent=data_analyst,
        expected_output="Current weather conditions in NYC"
    )
    
    # Create a crew with the agent and tasks
    crew = Crew(
        agents=[data_analyst],
        tasks=[math_task, weather_task],
        verbose=True
    )
    
    # Run the crew asynchronously
    result = await crew.kickoff_async()
    print("\nCrew Execution Results:")
    print(result)
    
    # Close the MCP provider when done
    await mcp_provider.close()

if __name__ == "__main__":
    asyncio.run(main()) 