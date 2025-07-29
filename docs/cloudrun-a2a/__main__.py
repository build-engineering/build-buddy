import logging
import os
import sys

import click
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from watson_orchestrate_agent import WatsonOrchestrateAgent
from watson_orchestrate_agent_executor import WatsonOrchestrateAgentExecutor
from dotenv import load_dotenv


# Load environment variables from .env file for local development
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_agent_card(host: str, port: int, app_url_override: str | None) -> AgentCard:
    """Constructs the AgentCard for the WatsonOrchestrateAgent."""
    if app_url_override:
        if app_url_override == "auto":
            service_url = os.getenv("SERVICE_URL", f"http://{host}:{port}/")
            logger.info(f"service_url is set to: {service_url}")
        else:
            service_url = app_url_override
    else:
        service_url = f"http://{host}:{port}/"

    logger.info(f"AgentCard URL set to: {service_url}")

    skills = [
        AgentSkill(
            id="list_native_agents",
            name="List Native Agents",
            description="List all native agents in WatsonX Orchestrate.",
            tags=["watsonx", "agents", "list"],
            examples=["List all native agents"],
        ),
        AgentSkill(
            id="list_external_agents",
            name="List External Agents",
            description="List all external agents in WatsonX Orchestrate.",
            tags=["watsonx", "agents", "list"],
            examples=["List all external agents"],
        ),
        AgentSkill(
            id="list_assistant_agents",
            name="List Assistant Agents",
            description="List all assistant agents in WatsonX Orchestrate.",
            tags=["watsonx", "agents", "list"],
            examples=["List all assistant agents"],
        ),
        AgentSkill(
            id="list_all_agents",
            name="List All Agents",
            description="List all agents (native, external, assistant) in WatsonX Orchestrate.",
            tags=["watsonx", "agents", "list"],
            examples=["List all agents"],
        ),
        AgentSkill(
            id="get_agent_by_id",
            name="Get Agent by ID",
            description="Get detailed information about a specific agent by its ID.",
            tags=["watsonx", "agents", "details"],
            examples=["Get agent with ID 'agent-123'"],
        ),
        AgentSkill(
            id="get_agent_by_name",
            name="Get Agent by Name",
            description="Get detailed information about a specific agent by its name.",
            tags=["watsonx", "agents", "details"],
            examples=["Get agent named 'Weather Bot'"],
        ),
        AgentSkill(
            id="invoke_agent_by_name",
            name="Invoke Agent by Name",
            description="Invoke a WatsonX Orchestrate agent by name with a message.",
            tags=["watsonx", "agents", "invoke"],
            examples=["Invoke agent 'Weather Bot' with message 'What's the weather?'"],
        ),
        AgentSkill(
            id="invoke_agent_by_id",
            name="Invoke Agent by ID",
            description="Invoke a WatsonX Orchestrate agent by ID with a message.",
            tags=["watsonx", "agents", "invoke"],
            examples=["Invoke agent with ID 'agent-123' with message 'Hello'"],
        ),
        AgentSkill(
            id="get_thread_messages",
            name="Get Thread Messages",
            description="Get all messages from a specific conversation thread.",
            tags=["watsonx", "threads", "messages"],
            examples=["Get messages from thread 'thread-456'"],
        ),
    ]

    return AgentCard(
        name="WatsonX Orchestrate Agent",
        description="An agent that provides tools to interact with WatsonX Orchestrate platform.",
        url=service_url,
        version="0.1.0",
        default_input_modes=WatsonOrchestrateAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=WatsonOrchestrateAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=AgentCapabilities(streaming=False),
        skills=skills,
    )


@click.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to.")
@click.option("--port", default=None, type=int, help="Port to bind the server to. Overridden by $PORT env var.")
@click.option("--app-url-override", default=None, help="Manually override the agent's public URL. Use 'auto' for Cloud Run detection.")
def main(host: str, port: int | None, app_url_override: str | None):
    """Entry point for the WatsonX Orchestrate A2A server."""
    # Cloud Run provides the port to listen on via the PORT environment variable.
    run_port = port if port is not None else int(os.getenv("PORT", 8080))

    # Check for required environment variables
    if not os.getenv("WXO_API_KEY"):
        logger.error("WXO_API_KEY environment variable not set. The WatsonX agent will not work.")
        sys.exit(1)
    if not os.getenv("WXO_BASE_URL"):
        logger.error("WXO_BASE_URL environment variable not set. The WatsonX agent will not work.")
        sys.exit(1)

    agent_card = get_agent_card(host, run_port, app_url_override)
    logger.info(f"agent_card is set to: {agent_card}")

    request_handler = DefaultRequestHandler(
        agent_executor=WatsonOrchestrateAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    logger.info(f"Starting WatsonX Orchestrate A2A server on {host}:{run_port}")
    uvicorn.run(server.build(), host=host, port=run_port)


if __name__ == "__main__":
    main() 