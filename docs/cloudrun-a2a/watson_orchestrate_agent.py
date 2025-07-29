import asyncio
import json
from typing import Optional, Dict, Any, List

from smolagents import LiteLLMModel, ToolCallingAgent, tool
from watsonx_client import WatsonXClient


class WatsonOrchestrateAgent:
    """
    A smolagents agent that provides tools to interact with WatsonX Orchestrate platform.
    It wraps WatsonXClient methods as tools for easy LLM interaction.
    """

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        # Initialize WatsonX client
        self.watsonx_client = WatsonXClient(force_refresh_on_every_request=False)
        
        # Define tools inside __init__ method (following smolagents pattern)
        @tool
        def list_native_agents() -> str:
            """
            List all native agents in WatsonX Orchestrate.
            
            Returns:
                A formatted string containing information about all native agents.
            """
            try:
                agents = self.watsonx_client.list_native_agents()
                if not agents:
                    return "No native agents found in WatsonX Orchestrate."
                
                result = f"Found {len(agents)} native agent(s):\n\n"
                for i, agent in enumerate(agents, 1):
                    result += f"{i}. **{agent.get('name', 'Unknown')}**\n"
                    result += f"   - ID: {agent.get('id', 'Unknown')}\n"
                    result += f"   - Description: {agent.get('description', 'No description')}\n"
                    result += f"   - Status: {agent.get('status', 'Unknown')}\n\n"
                
                return result
            except Exception as e:
                return f"Error listing native agents: {str(e)}"

        @tool
        def list_external_agents() -> str:
            """
            List all external agents in WatsonX Orchestrate.
            
            Returns:
                A formatted string containing information about all external agents.
            """
            try:
                agents = self.watsonx_client.list_external_agents()
                if not agents:
                    return "No external agents found in WatsonX Orchestrate."
                
                result = f"Found {len(agents)} external agent(s):\n\n"
                for i, agent in enumerate(agents, 1):
                    result += f"{i}. **{agent.get('name', 'Unknown')}**\n"
                    result += f"   - ID: {agent.get('id', 'Unknown')}\n"
                    result += f"   - Description: {agent.get('description', 'No description')}\n"
                    result += f"   - Status: {agent.get('status', 'Unknown')}\n\n"
                
                return result
            except Exception as e:
                return f"Error listing external agents: {str(e)}"

        @tool
        def list_assistant_agents() -> str:
            """
            List all assistant agents in WatsonX Orchestrate.
            
            Returns:
                A formatted string containing information about all assistant agents.
            """
            try:
                agents = self.watsonx_client.list_assistant_agents()
                if not agents:
                    return "No assistant agents found in WatsonX Orchestrate."
                
                result = f"Found {len(agents)} assistant agent(s):\n\n"
                for i, agent in enumerate(agents, 1):
                    result += f"{i}. **{agent.get('name', 'Unknown')}**\n"
                    result += f"   - ID: {agent.get('id', 'Unknown')}\n"
                    result += f"   - Description: {agent.get('description', 'No description')}\n"
                    result += f"   - Status: {agent.get('status', 'Unknown')}\n\n"
                
                return result
            except Exception as e:
                return f"Error listing assistant agents: {str(e)}"

        @tool
        def list_all_agents() -> str:
            """
            List all agents (native, external, and assistant) in WatsonX Orchestrate.
            
            Returns:
                A formatted string containing information about all agents by type.
            """
            try:
                all_agents = self.watsonx_client.list_all_agents()
                
                result = "**All Agents in WatsonX Orchestrate:**\n\n"
                
                for agent_type, agents in all_agents.items():
                    result += f"## {agent_type.title()} Agents ({len(agents)})\n"
                    if not agents:
                        result += "No agents found.\n\n"
                    else:
                        for i, agent in enumerate(agents, 1):
                            result += f"{i}. **{agent.get('name', 'Unknown')}**\n"
                            result += f"   - ID: {agent.get('id', 'Unknown')}\n"
                            result += f"   - Description: {agent.get('description', 'No description')}\n"
                            result += f"   - Status: {agent.get('status', 'Unknown')}\n\n"
                
                return result
            except Exception as e:
                return f"Error listing all agents: {str(e)}"

        @tool
        def get_agent_by_id(agent_id: str, agent_type: Optional[str] = None) -> str:
            """
            Get detailed information about a specific agent by its ID.
            
            Args:
                agent_id: The ID of the agent to retrieve
                agent_type: Optional agent type (native, external, assistant). If not specified, searches all types.
            
            Returns:
                A formatted string containing detailed information about the agent.
            """
            try:
                agent = self.watsonx_client.get_agent_by_id(agent_id, agent_type)
                if not agent:
                    return f"Agent with ID '{agent_id}' not found."
                
                result = f"**Agent Details:**\n\n"
                result += f"**Name:** {agent.get('name', 'Unknown')}\n"
                result += f"**ID:** {agent.get('id', 'Unknown')}\n"
                result += f"**Description:** {agent.get('description', 'No description')}\n"
                result += f"**Status:** {agent.get('status', 'Unknown')}\n"
                result += f"**Type:** {agent.get('type', 'Unknown')}\n"
                result += f"**Created:** {agent.get('created_at', 'Unknown')}\n"
                result += f"**Updated:** {agent.get('updated_at', 'Unknown')}\n"
                
                # Add any additional fields that might be present
                for key, value in agent.items():
                    if key not in ['name', 'id', 'description', 'status', 'type', 'created_at', 'updated_at']:
                        result += f"**{key.title()}:** {value}\n"
                
                return result
            except Exception as e:
                return f"Error getting agent by ID: {str(e)}"

        @tool
        def get_agent_by_name(name: str, agent_type: Optional[str] = None) -> str:
            """
            Get detailed information about a specific agent by its name.
            
            Args:
                name: The name of the agent to retrieve
                agent_type: Optional agent type (native, external, assistant). If not specified, searches all types.
            
            Returns:
                A formatted string containing detailed information about the agent.
            """
            try:
                agent = self.watsonx_client.get_agent_by_name(name, agent_type)
                if not agent:
                    return f"Agent with name '{name}' not found."
                
                result = f"**Agent Details:**\n\n"
                result += f"**Name:** {agent.get('name', 'Unknown')}\n"
                result += f"**ID:** {agent.get('id', 'Unknown')}\n"
                result += f"**Description:** {agent.get('description', 'No description')}\n"
                result += f"**Status:** {agent.get('status', 'Unknown')}\n"
                result += f"**Type:** {agent.get('type', 'Unknown')}\n"
                result += f"**Created:** {agent.get('created_at', 'Unknown')}\n"
                result += f"**Updated:** {agent.get('updated_at', 'Unknown')}\n"
                
                # Add any additional fields that might be present
                for key, value in agent.items():
                    if key not in ['name', 'id', 'description', 'status', 'type', 'created_at', 'updated_at']:
                        result += f"**{key.title()}:** {value}\n"
                
                return result
            except Exception as e:
                return f"Error getting agent by name: {str(e)}"

        @tool
        def invoke_agent_by_name(agent_name: str, message: str, thread_id: Optional[str] = None) -> str:
            """
            Invoke a WatsonX Orchestrate agent by name with a message.
            
            Args:
                agent_name: The name of the agent to invoke
                message: The message to send to the agent
                thread_id: Optional thread ID for conversation continuity
            
            Returns:
                The response from the invoked agent.
            """
            try:
                result = self.watsonx_client.invoke_agent_by_name(agent_name, message, thread_id)
                
                if result["status"] == "success":
                    response = result.get("response", {})
                    thread_id = result.get("thread_id")
                    
                    result_text = f"**Agent Response:**\n\n"
                    result_text += f"**Agent:** {agent_name}\n"
                    if thread_id:
                        result_text += f"**Thread ID:** {thread_id}\n"
                    result_text += f"**Response:** {response}\n"
                    
                    return result_text
                else:
                    return f"Error invoking agent '{agent_name}': {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                return f"Error invoking agent by name: {str(e)}"

        @tool
        def invoke_agent_by_id(agent_id: str, message: str, thread_id: Optional[str] = None) -> str:
            """
            Invoke a WatsonX Orchestrate agent by ID with a message.
            
            Args:
                agent_id: The ID of the agent to invoke
                message: The message to send to the agent
                thread_id: Optional thread ID for conversation continuity
            
            Returns:
                The response from the invoked agent.
            """
            try:
                result = self.watsonx_client.invoke_agent(agent_id, message, thread_id)
                
                if result["status"] == "success":
                    response = result.get("response", {})
                    thread_id = result.get("thread_id")
                    
                    result_text = f"**Agent Response:**\n\n"
                    result_text += f"**Agent ID:** {agent_id}\n"
                    if thread_id:
                        result_text += f"**Thread ID:** {thread_id}\n"
                    result_text += f"**Response:** {response}\n"
                    
                    return result_text
                else:
                    return f"Error invoking agent with ID '{agent_id}': {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                return f"Error invoking agent by ID: {str(e)}"

        @tool
        def get_thread_messages(thread_id: str) -> str:
            """
            Get all messages from a specific conversation thread.
            
            Args:
                thread_id: The thread ID to retrieve messages from
            
            Returns:
                A formatted string containing all messages in the thread.
            """
            try:
                result = self.watsonx_client.get_thread_messages(thread_id)
                
                if result["status"] == "success":
                    messages = result.get("messages", [])
                    
                    if not messages:
                        return f"No messages found in thread '{thread_id}'."
                    
                    result_text = f"**Thread Messages (Thread ID: {thread_id}):**\n\n"
                    
                    for i, message in enumerate(messages, 1):
                        result_text += f"**Message {i}:**\n"
                        result_text += f"**Role:** {message.get('role', 'Unknown')}\n"
                        result_text += f"**Content:** {message.get('content', 'No content')}\n"
                        result_text += f"**Timestamp:** {message.get('timestamp', 'Unknown')}\n\n"
                    
                    return result_text
                else:
                    return f"Error getting thread messages: {result.get('error', 'Unknown error')}"
                    
            except Exception as e:
                return f"Error getting thread messages: {str(e)}"

        # Configure the agent to use OpenAI via LiteLLM
        model = LiteLLMModel(model_id="gpt-4o-mini")

        self.agent = ToolCallingAgent(
            tools=[
                list_native_agents,
                list_external_agents,
                list_assistant_agents,
                list_all_agents,
                get_agent_by_id,
                get_agent_by_name,
                invoke_agent_by_name,
                invoke_agent_by_id,
                get_thread_messages,
            ],
            model=model,
            verbosity_level=1,
        )

    async def ainvoke(self, query: str) -> str:
        """
        Asynchronously invoke the agent's synchronous run method in a separate thread
        to avoid blocking the main async event loop.
        """
        # smolagents agent.run() is synchronous, so we run it in a thread
        # to be compatible with the async A2A server.
        return await asyncio.to_thread(self.agent.run, query) 