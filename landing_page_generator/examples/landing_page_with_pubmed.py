"""
Example of using PubMed MCP with the Landing Page Generator

This example demonstrates how to modify the Landing Page Generator to use
PubMed MCP tools when creating a health-related landing page.
"""

import os
import shutil
from textwrap import dedent
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
from crewai import Agent, Crew, Process, Task
from crewai.tools import BaseTool

# Helper function to ensure all tools are BaseTool instances
def ensure_base_tools(tools_list):
    """Ensure all tools in the list are instances of BaseTool"""
    result = []
    for tool in tools_list:
        if isinstance(tool, BaseTool):
            result.append(tool)
    return result

class LandingPageWithPubMed:
    """Landing Page Generator with PubMed MCP tools"""
    
    def __init__(self, idea):
        """Initialize with a business idea"""
        self.idea = idea
        
        # Configure PubMed MCP server
        self.mcp_params = StdioServerParameters(
            command="uvx",
            args=["--quiet", "pubmedmcp@0.1.3"],
            env={"UV_PYTHON": "3.12", **os.environ}
        )
        
        # The MCP adapter will be initialized during run()
        self.mcp_adapter = None
        
    def run(self):
        """Run the landing page generator with PubMed MCP tools"""
        # Initialize MCP adapter using context manager
        with MCPServerAdapter(self.mcp_params) as pubmed_tools:
            print(f"Available PubMed tools: {[tool.name for tool in pubmed_tools]}")
            
            # Create your custom medical content agent
            medical_expert = Agent(
                role="Medical Content Expert",
                goal="Create accurate and engaging medical content for the landing page",
                backstory="You are a medical expert with deep knowledge of healthcare topics and experience in writing compelling content for health websites.",
                verbose=True,
                tools=ensure_base_tools(pubmed_tools)
            )
            
            # Create a task for the medical expert
            medical_content_task = Task(
                description=f"Research and create compelling medical content for the landing page about: {self.idea}. Make sure to cite reliable medical sources and use evidence-based information.",
                agent=medical_expert
            )
            
            # Create a medical content crew
            medical_crew = Crew(
                agents=[medical_expert],
                tasks=[medical_content_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Run the medical crew to get research-backed content
            medical_content = medical_crew.kickoff()
            
            print("\n\nMedical Content Generated:")
            print("-" * 50)
            print(medical_content)
            print("-" * 50)
            
            # Here you would then pass this content to your regular landing page generation process
            # e.g., pass it to your template selection and content creation crews
            
            return medical_content

if __name__ == "__main__":
    print("Welcome to Medical Landing Page Generator")
    print(dedent("""
    This example uses PubMed MCP to access medical research for your landing page.
    It will create research-backed content for a health-related landing page.
    """
    ))
    
    idea = input("# Describe your health business idea:\n\n")
    
    generator = LandingPageWithPubMed(idea)
    content = generator.run()
    
    print("\n\nDONE!")
    print("The medical content has been generated and can now be integrated into your landing page.") 