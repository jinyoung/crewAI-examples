"""
Example of using PubMed MCP with CrewAI Tools

This example shows how to use the PubMed MCP server adapter with CrewAI.
"""

import os
from dotenv import load_dotenv
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
from crewai import Agent, Task, Crew, Process

# Load environment variables
load_dotenv()

def main():
    """Run the PubMed MCP example"""
    
    # Configure MCP server for PubMed
    server_params = StdioServerParameters(
        command="uvx",
        args=["--quiet", "pubmedmcp@0.1.3"],
        env={"UV_PYTHON": "3.12", **os.environ}
    )
    
    # Use context manager for clean setup/teardown
    with MCPServerAdapter(server_params) as pubmed_tools:
        print(f"Available PubMed tools: {[tool.name for tool in pubmed_tools]}")
        
        # Create an agent with the PubMed tools
        researcher = Agent(
            role="Medical Researcher",
            goal="Find and summarize recent research on a medical topic",
            backstory="You are an expert in medical research with years of experience analyzing scientific publications.",
            verbose=True,
            tools=pubmed_tools
        )
        
        # Create a research task
        research_task = Task(
            description="Research the latest findings on COVID-19 treatments and summarize the key findings from the last year.",
            agent=researcher
        )
        
        # Create a crew with just the researcher
        medical_crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Run the crew
        result = medical_crew.kickoff()
        
        print("\n\nResearch Results:")
        print(result)
        
if __name__ == "__main__":
    main() 