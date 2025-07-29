"""
WatsonX Orchestrate client utilities
"""
from ibm_watsonx_orchestrate.client.agents.agent_client import AgentClient
from ibm_watsonx_orchestrate.client.agents.external_agent_client import ExternalAgentClient
from ibm_watsonx_orchestrate.client.agents.assistant_agent_client import AssistantAgentClient
from ibm_watsonx_orchestrate.client.utils import instantiate_client
from ibm_watsonx_orchestrate.agent_builder.agents.types import AgentKind
from ibm_watsonx_orchestrate.cli.config import Config
from typing import List, Dict, Any, Optional
import logging
import requests
import json
import os
from dotenv import load_dotenv
import time
import subprocess

logger = logging.getLogger(__name__)


class WatsonXClient:
    """Client wrapper for WatsonX Orchestrate operations"""
    
    def __init__(self, force_refresh_on_every_request: bool = False):
        self.native_client = None
        self.external_client = None
        self.assistant_client = None
        self.last_auth_time = 0
        
        # Set auth interval based on preference
        if force_refresh_on_every_request:
            self.auth_interval = 0  # Re-authenticate on every request
            logger.info("Configured to re-authenticate on every request")
        else:
            self.auth_interval = 300  # Re-authenticate every 5 minutes (300 seconds)
            logger.info("Configured to re-authenticate every 5 minutes")
        
        # Automatically activate environment on initialization
        self._auto_activate_environment()
    
    def _auto_activate_environment(self):
        """Automatically activate the WatsonX Orchestrate environment on initialization"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Get environment configuration
            environment = os.getenv('WXO_ENVIRONMENT', 'build_engg')
            base_url = os.getenv('WXO_BASE_URL')
            api_key = os.getenv('WXO_API_KEY')
            
            if not base_url:
                logger.error("WXO_BASE_URL not found in environment variables")
                return False
            
            if not api_key:
                logger.error("WXO_API_KEY not found in environment variables")
                return False
            
            logger.info(f"Auto-activating environment '{environment}'...")
            
            # First, ensure the environment is configured
            self._ensure_environment_configured(environment, base_url)
            
            # Then activate the environment using the CLI command
            success = self._activate_environment_cli(environment, api_key)
            
            if success:
                logger.info(f"✅ Environment '{environment}' auto-activated successfully")
                self.last_auth_time = time.time()
                return True
            else:
                logger.error(f"❌ Failed to auto-activate environment '{environment}'")
                return False
                
        except Exception as e:
            logger.error(f"Error in auto-activation: {e}")
            return False
    
    def _ensure_environment_configured(self, environment: str, base_url: str):
        """Ensure the environment is configured in the CLI config"""
        try:
            cfg = Config()
            
            # Add environment to config if not already present
            try:
                cfg.read('environments', environment)
                logger.info(f"Environment '{environment}' already configured")
            except:
                cfg.write('environments', environment, {'wxo_url': base_url})
                logger.info(f"Environment '{environment}' configured with URL: {base_url}")
                
        except Exception as e:
            logger.error(f"Error configuring environment: {e}")
    
    def _activate_environment_cli(self, environment: str, api_key: str) -> bool:
        """Activate environment using the CLI command"""
        try:
            # Use subprocess to run the orchestrate CLI command
            # We'll use echo to provide the API key non-interactively
            cmd = f'echo "{api_key}" | orchestrate env activate {environment}'
            
            logger.info(f"Running CLI command: orchestrate env activate {environment}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                logger.info("CLI activation successful")
                return True
            else:
                logger.error(f"CLI activation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("CLI activation timed out")
            return False
        except Exception as e:
            logger.error(f"Error running CLI activation: {e}")
            return False
    
    def _ensure_environment_activated(self):
        """Ensure the WatsonX Orchestrate environment is activated"""
        try:
            # Load environment variables
            load_dotenv()
            
            # Get environment configuration
            environment = os.getenv('WXO_ENVIRONMENT', 'build_engg')
            base_url = os.getenv('WXO_BASE_URL')
            api_key = os.getenv('WXO_API_KEY')
            token = os.getenv('WXO_TOKEN')
            
            if not base_url:
                logger.error("WXO_BASE_URL not found in environment variables")
                return False
            
            if not api_key and not token:
                logger.error("Neither WXO_API_KEY nor WXO_TOKEN found in environment variables")
                return False
            
            # Create config instance
            cfg = Config()
            
            # Add environment to config if not already present
            try:
                cfg.read('environments', environment)
            except:
                cfg.write('environments', environment, {'wxo_url': base_url})
            
            # If we have an API key, authenticate
            if api_key:
                try:
                    from ibm_watsonx_orchestrate.client.credentials import Credentials
                    from ibm_watsonx_orchestrate.client.client import Client
                    import jwt
                    
                    logger.info("Authenticating with API key...")
                    creds = Credentials(url=base_url, api_key=api_key)
                    client = Client(creds)
                    
                    # Decode and store token properly
                    try:
                        decoded = jwt.decode(client.token, options={"verify_signature": False})
                        token_data = {
                            'wxo_mcsp_token': client.token,
                            'wxo_mcsp_token_expiry': decoded.get("exp")
                        }
                    except:
                        token_data = {'wxo_mcsp_token': client.token}
                    
                    # Store token in auth config
                    auth_cfg = Config('~/.cache/orchestrate', 'credentials.yaml')
                    auth_cfg.save({
                        'auth': {
                            environment: token_data
                        }
                    })
                    logger.info("Authentication successful")
                    self.last_auth_time = time.time()
                except Exception as e:
                    logger.error(f"Authentication failed: {e}")
                    return False
            
            # Activate environment
            cfg.write('context', 'active_environment', environment)
            logger.info(f"Environment '{environment}' activated")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up environment: {e}")
            return False
    
    def _check_and_refresh_auth(self):
        """Check if authentication needs to be refreshed"""
        current_time = time.time()
        if self.auth_interval == 0 or (current_time - self.last_auth_time > self.auth_interval):
            logger.info("Authentication expired, refreshing...")
            return self._ensure_environment_activated()
        return True
    
    def force_refresh_auth(self):
        """Force refresh authentication immediately"""
        logger.info("Forcing authentication refresh...")
        self.last_auth_time = 0  # Reset to force refresh
        return self._ensure_environment_activated()
    
    def _get_native_client(self):
        """Get native agent client with dynamic environment activation"""
        # Ensure environment is activated for each request
        if not self._check_and_refresh_auth():
            raise Exception("Failed to activate environment")
        
        if not self.native_client:
            self.native_client = instantiate_client(AgentClient)
        return self.native_client
    
    def _get_external_client(self):
        """Get external agent client with dynamic environment activation"""
        # Ensure environment is activated for each request
        if not self._check_and_refresh_auth():
            raise Exception("Failed to activate environment")
        
        if not self.external_client:
            self.external_client = instantiate_client(ExternalAgentClient)
        return self.external_client
    
    def _get_assistant_client(self):
        """Get assistant agent client with dynamic environment activation"""
        # Ensure environment is activated for each request
        if not self._check_and_refresh_auth():
            raise Exception("Failed to activate environment")
        
        if not self.assistant_client:
            self.assistant_client = instantiate_client(AssistantAgentClient)
        return self.assistant_client
    
    def list_native_agents(self) -> List[Dict[str, Any]]:
        """List all native agents"""
        try:
            client = self._get_native_client()
            agents = client.get()
            return agents
        except Exception as e:
            logger.error(f"Error listing native agents: {e}")
            return []
    
    def list_external_agents(self) -> List[Dict[str, Any]]:
        """List all external agents"""
        try:
            client = self._get_external_client()
            agents = client.get()
            return agents
        except Exception as e:
            logger.error(f"Error listing external agents: {e}")
            return []
    
    def list_assistant_agents(self) -> List[Dict[str, Any]]:
        """List all assistant agents"""
        try:
            client = self._get_assistant_client()
            agents = client.get()
            return agents
        except Exception as e:
            logger.error(f"Error listing assistant agents: {e}")
            return []
    
    def list_all_agents(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all agents by type"""
        return {
            "native": self.list_native_agents(),
            "external": self.list_external_agents(),
            "assistant": self.list_assistant_agents()
        }
    
    def get_agent_by_id(self, agent_id: str, agent_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        try:
            if agent_type == "native" or agent_type is None:
                agents = self.list_native_agents()
            elif agent_type == "external":
                agents = self.list_external_agents()
            elif agent_type == "assistant":
                agents = self.list_assistant_agents()
            else:
                return None
            
            for agent in agents:
                if agent.get('id') == agent_id:
                    return agent
            return None
        except Exception as e:
            logger.error(f"Error getting agent by ID: {e}")
            return None
    
    def get_agent_by_name(self, name: str, agent_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get agent by name"""
        try:
            if agent_type == "native" or agent_type is None:
                agents = self.list_native_agents()
            elif agent_type == "external":
                agents = self.list_external_agents()
            elif agent_type == "assistant":
                agents = self.list_assistant_agents()
            else:
                return None
            
            for agent in agents:
                if agent.get('name') == name:
                    return agent
            return None
        except Exception as e:
            logger.error(f"Error getting agent by name: {e}")
            return None

    def invoke_agent(self, agent_id: str, message: str, thread_id: Optional[str] = None, stream: bool = False, include_messages: bool = True) -> Dict[str, Any]:
        """
        Invoke an agent with a message and return the response
        
        Args:
            agent_id: The ID of the agent to invoke
            message: The message to send to the agent
            thread_id: Optional thread ID for conversation continuity
            stream: Whether to stream the response
            include_messages: Whether to include the actual conversation messages in the response
            
        Returns:
            Dictionary containing the response data with optional conversation messages
        """
        try:
            # Get the base client to access the base URL and headers
            client = self._get_native_client()
            
            # Prepare the payload
            payload = {
                "message": {
                    "role": "user",
                    "content": message
                },
                "agent_id": agent_id
            }
            
            if thread_id:
                payload["thread_id"] = thread_id
            
            # Determine the endpoint path
            if stream:
                path = "/runs?stream=true"
            else:
                path = "/runs"
            
            # Make the request
            response = client._post(path, payload)
            
            # Prepare the result
            result = {
                "status": "success",
                "response": response,
                "thread_id": response.get("thread_id") if not stream else None
            }
            
            # If not streaming and include_messages is True, fetch the conversation
            if not stream and include_messages and response.get("thread_id"):
                try:
                    # Wait for the agent to process the message with retries
                    import time
                    max_wait_time = 300  # 5 minutes total
                    check_interval = 2   # Check every 2 seconds
                    total_wait_time = 0
                    last_message_count = 0
                    
                    while total_wait_time < max_wait_time:
                        time.sleep(check_interval)
                        total_wait_time += check_interval
                        
                        # Try to fetch thread messages
                        thread_result = self.get_thread_messages(response.get("thread_id"))
                        if thread_result["status"] == "success":
                            messages = thread_result["messages"]
                            current_message_count = len(messages)
                            
                            # Check if we have both user and assistant messages
                            if current_message_count >= 2:
                                # Get the latest assistant message
                                assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
                                if assistant_messages:
                                    latest_assistant = assistant_messages[-1]
                                    content = latest_assistant.get("content", "")
                                    
                                    # Check if the response seems complete
                                    # Look for indicators that the agent is done
                                    
                                    # Extract text content from the message
                                    text_content = ""
                                    if isinstance(content, list):
                                        for item in content:
                                            if isinstance(item, dict) and item.get('response_type') == 'text':
                                                text_content = item.get('text', '')
                                                break
                                    elif isinstance(content, str):
                                        text_content = content
                                    else:
                                        text_content = str(content)
                                    
                                    is_complete = (
                                        len(text_content) > 50 or  # Longer response
                                        any(phrase in text_content.lower() for phrase in [
                                            "hope this helps", "let me know", "anything else", 
                                            "is there anything", "do you have", "can i help",
                                            "feel free", "if you need", "additional"
                                        ]) or
                                        text_content.endswith(('.', '!', '?')) or  # Ends with punctuation
                                        total_wait_time > 30  # Wait at least 30 seconds for complex responses
                                    )
                                    
                                    if is_complete:
                                        result["messages"] = messages
                                        result["conversation"] = self._format_conversation(messages)
                                        logger.info(f"Complete conversation fetched after {total_wait_time} seconds")
                                        break
                                    else:
                                        logger.info(f"Waiting for complete response... ({total_wait_time}s elapsed, message length: {len(text_content)})")
                                else:
                                    logger.info(f"Waiting for assistant response... ({total_wait_time}s elapsed)")
                            else:
                                logger.info(f"Waiting for agent response... ({total_wait_time}s elapsed, messages: {current_message_count})")
                            
                            # Check if we got new messages
                            if current_message_count > last_message_count:
                                logger.info(f"New messages detected: {current_message_count} (was {last_message_count})")
                                last_message_count = current_message_count
                        else:
                            logger.warning(f"Failed to fetch thread messages: {thread_result.get('error')}")
                            break
                    else:
                        # Timeout reached, fetch whatever we have
                        thread_result = self.get_thread_messages(response.get("thread_id"))
                        if thread_result["status"] == "success":
                            result["messages"] = thread_result["messages"]
                            result["conversation"] = self._format_conversation(thread_result["messages"])
                            logger.warning(f"Timeout reached after {max_wait_time} seconds, fetched available messages")
                        else:
                            logger.warning(f"Failed to fetch thread messages after timeout: {thread_result.get('error')}")
                            
                except Exception as e:
                    logger.warning(f"Error fetching thread messages: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error invoking agent {agent_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _format_conversation(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format conversation messages for easier consumption
        
        Args:
            messages: Raw messages from the API
            
        Returns:
            List of formatted conversation messages
        """
        formatted_messages = []
        
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # Extract text content from complex content objects
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('response_type') == 'text':
                        content = item.get('text', '')
                        break
            elif not isinstance(content, str):
                content = str(content)
            
            formatted_messages.append({
                "role": role,
                "content": content
            })
        
        return formatted_messages

    def invoke_agent_by_name(self, agent_name: str, message: str, thread_id: Optional[str] = None, stream: bool = False, include_messages: bool = True) -> Dict[str, Any]:
        """
        Invoke an agent by name with a message and return the response
        
        Args:
            agent_name: The name of the agent to invoke
            message: The message to send to the agent
            thread_id: Optional thread ID for conversation continuity
            stream: Whether to stream the response
            include_messages: Whether to include the actual conversation messages in the response
            
        Returns:
            Dictionary containing the response data with optional conversation messages
        """
        try:
            # Find the agent by name
            agent = self.get_agent_by_name(agent_name)
            if not agent:
                return {
                    "status": "error",
                    "error": f"Agent with name '{agent_name}' not found"
                }
            
            # Invoke the agent using its ID
            return self.invoke_agent(agent['id'], message, thread_id, stream, include_messages)
            
        except Exception as e:
            logger.error(f"Error invoking agent by name {agent_name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_thread_messages(self, thread_id: str) -> Dict[str, Any]:
        """
        Get messages from a specific thread
        
        Args:
            thread_id: The thread ID to retrieve messages from
            
        Returns:
            Dictionary containing the thread messages
        """
        try:
            client = self._get_native_client()
            path = f"/threads/{thread_id}/messages"
            response = client._get(path)
            
            return {
                "status": "success",
                "messages": response
            }
            
        except Exception as e:
            logger.error(f"Error getting thread messages for {thread_id}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global client instances - you can choose which one to use
# Option 1: Re-authenticate every 5 minutes (default)
watsonx_client = WatsonXClient(force_refresh_on_every_request=False)

# Option 2: Re-authenticate on every request (for environments with very short token expiry)
# watsonx_client = WatsonXClient(force_refresh_on_every_request=True) 