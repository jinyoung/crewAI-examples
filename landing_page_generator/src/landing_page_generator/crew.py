from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from callback import CallbackHandler

from langchain_community.agent_toolkits.file_management.toolkit import FileManagementToolkit
from tools.browser_tools import ScrapeWebsiteTool
from tools.file_tools import FileTools
from tools.search_tools import SearchInternetTool
from tools.template_tools import TemplateTools
# Import the official crewai-tools MCP integration and StdioServerParameters
from mcp import StdioServerParameters
from crewai_tools import MCPServerAdapter
from crewai.tools import BaseTool

import json
import ast
import os

from dotenv import load_dotenv
load_dotenv()


# Update MCP server configuration to use StdioServerParameters
mcp_server_params = StdioServerParameters(
    command="npx",
    args=["@playwright/mcp@latest"],
    env=os.environ
)

# Create MCP server adapter and get tools
mcp_server_adapter = MCPServerAdapter(mcp_server_params)
mcp_tools = mcp_server_adapter.tools

# Helper function to ensure all tools are BaseTool instances
def ensure_base_tools(tools_list):
    """Ensure all tools in the list are instances of BaseTool"""
    result = []
    for tool in tools_list:
        if isinstance(tool, BaseTool):
            result.append(tool)
    return result

@CrewBase
class ExpandIdeaCrew:
    """ExpandIdea crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def senior_idea_analyst_agent(self) -> Agent:
        search_tool = SearchInternetTool()
        scrape_tool = ScrapeWebsiteTool()
        # Use list of individual MCP tools instead of a single MCP tool
        tools = ensure_base_tools(mcp_tools)
        return Agent(
            config=self.agents_config['senior_idea_analyst'],
            allow_delegation=False,
            tools=tools,
            verbose=False,
            step_callback=lambda step_output: print(f"Step output: {step_output}")
            
        )
    
    @agent
    def senior_strategist_agent(self) -> Agent:
        search_tool = SearchInternetTool()
        scrape_tool = ScrapeWebsiteTool()
        # Use list of individual MCP tools instead of a single MCP tool
        tools = ensure_base_tools(mcp_tools)
        return Agent(
            config=self.agents_config['senior_strategist'],
            allow_delegation=False,
            tools=tools,
            verbose=False,
            step_callback=lambda step_output: print(f"Step output: {step_output}")
        )
    
    @task
    def expand_idea(self) -> Task: 
        return Task(
            config=self.tasks_config['expand_idea_task'],
            agent=self.senior_idea_analyst_agent(),
        )
    
    @task
    def refine_idea(self) -> Task: 
        return Task(
            config=self.tasks_config['refine_idea_task'],
            agent=self.senior_strategist_agent(),
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )

@CrewBase
class ChooseTemplateCrew:

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    toolkit = FileManagementToolkit(
      root_dir='workdir',
      selected_tools=["read_file", "list_directory"]
    )

    @agent
    def senior_react_engineer_agent(self) -> Agent:
        search_tool = SearchInternetTool()
        scrape_tool = ScrapeWebsiteTool()
        
        # Collect all tools
        all_tools = [
            # Add individual MCP tools instead of a single MCP tool
            *mcp_tools,  # Unpacking the list of tools
            TemplateTools.learn_landing_page_options,
            TemplateTools.copy_landing_page_template_to_project_folder,
            FileTools.write_file
        ]
        # Add toolkit tools
        toolkit_tools = self.toolkit.get_tools()
        all_tools.extend(toolkit_tools)
        
        # Ensure all tools are BaseTool instances
        tools = ensure_base_tools(all_tools)

        return Agent(
            config=self.agents_config['senior_react_engineer'],
            allow_delegation=False,
            tools=tools,
            verbose=False,
            step_callback=lambda step_output: print(f"Step output: {step_output}")
        )
    
    
    @task
    def choose_template(self) -> Task: 
        return Task(
            config=self.tasks_config['choose_template_task'],
            agent=self.senior_react_engineer_agent(),
        )
        
    @task
    def update_page(self) -> Task: 
        return Task(
            config=self.tasks_config['update_page_task'],
            agent=self.senior_react_engineer_agent(),
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
    
    
callback_handler = CallbackHandler()


@CrewBase
class CreateContentCrew:

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    toolkit = FileManagementToolkit(
      root_dir='workdir',
      selected_tools=["read_file", "list_directory"]
    )

    @agent
    def senior_content_editor_agent(self) -> Agent:
        # Empty list as placeholder since no tools are specified
        tools = []
        return Agent(
            config=self.agents_config['senior_content_editor'],
            allow_delegation=False,
            tools=tools,
            verbose=True,
            step_callback=lambda step_output: print(f"Step output: {step_output}")
        )
    
    @agent
    def senior_react_engineer_agent(self) -> Agent:
        search_tool = SearchInternetTool()
        scrape_tool = ScrapeWebsiteTool()
        
        # Collect all tools
        all_tools = [
            search_tool,
            scrape_tool,
            TemplateTools.learn_landing_page_options,
            TemplateTools.copy_landing_page_template_to_project_folder,
            FileTools.write_file
        ]
        # Add toolkit tools
        toolkit_tools = self.toolkit.get_tools()
        all_tools.extend(toolkit_tools)
        
        # Ensure all tools are BaseTool instances
        tools = ensure_base_tools(all_tools)
        
        return Agent(
            config=self.agents_config['senior_react_engineer'],
            allow_delegation=False,
            tools=tools,
            verbose=True,
            step_callback=lambda step_output: print(f"Step output: {step_output}")
        )
    
    @task
    def create_content(self) -> Task: 
        return Task(
            config=self.tasks_config['component_content_task'],
            agent=self.senior_content_editor_agent(),
        )
    
    @task
    def update_component(self) -> Task: 
        return Task(
            config=self.tasks_config['update_component_task'],
            agent=self.senior_content_editor_agent(),
        )
    
    
    @task
    def qa_component(self) -> Task: 
        return Task(
            config=self.tasks_config['qa_component_task'],
            agent=self.senior_content_editor_agent(),
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks, 
            process=Process.sequential,
            verbose=True,
        )
    
class LandingPageCrew():
    def __init__(self, idea):
        self.idea = idea
    
    def run(self):
        try:
            expanded_idea= self.runExpandIdeaCrew(self.idea)
                
            components_paths_list = self.runChooseTemplateCrew(expanded_idea)
                
            self.runCreateContentCrew(components_paths_list, expanded_idea)
        finally:
            # Make sure to stop the MCP server adapter when done
            mcp_server_adapter.stop()
    
    def runExpandIdeaCrew(self,idea):
        inputs1 = {
                "idea": str(idea)
        }
        expanded_idea= ExpandIdeaCrew().crew().kickoff(inputs=inputs1)
        return str(expanded_idea)

    def runChooseTemplateCrew(self, expanded_idea):
        inputs2={
            "idea": expanded_idea
        }
        components = ChooseTemplateCrew().crew().kickoff(inputs=inputs2)
        components= str(components)
        
        components = components.replace("\n", "").replace(" ",
                                                        "").replace("```","").replace("\\", "")
        
        # Convert the string to a Python list
        try:
            components_paths_list = ast.literal_eval(components)  # Safely parse the string
        except Exception as e:
            print(f"Error parsing the string: {e}")
            components_paths_list = []
        result= json.dumps(components_paths_list,indent=4)

        return json.loads(result)

    def runCreateContentCrew(self,components, expanded_idea):

        for component_path in components:
            file_content = open(
            f"./workdir/{component_path.split('./')[-1]}",
            "r"
        ).read()
            inputs3={
            "component": component_path,
            "expanded_idea": expanded_idea,
            "file_content": file_content
            }

            CreateContentCrew().crew().kickoff(inputs=inputs3)

    

    