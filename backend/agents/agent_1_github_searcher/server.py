import json
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.utils import new_agent_text_message

from agents.agent_1_github_searcher.graph import app
from agents.agent_1_github_searcher.state import AgentState


class GithubSearcherExecutor(AgentExecutor):
    """Execute the GitHub profile search graph for incoming requests."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Run the graph and emit the found profiles as a text message."""
        user_input = context.get_user_input()
        result = app.invoke(
            AgentState(user_input=user_input, found_profiles=[], profiles_details=[])
        )
        output = json.dumps([p.model_dump() for p in result["profiles_details"]])
        await event_queue.enqueue_event(new_agent_text_message(output))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Reject cancellation since it is not supported."""
        raise Exception("cancel not supported")


if __name__ == "__main__":  # pragma: no cover
    skill = AgentSkill(
        id="github_search",
        name="GitHub Profile Search",
        description="Searches GitHub profiles based on criteria",
        tags=["github", "search", "profiles"],
        examples=["language:python location:germany"],
    )

    agent_card = AgentCard(
        name="github-profile-searcher",
        description="Searches and fetches GitHub profiles based on criteria",
        url="http://localhost:8001/",
        version="0.1.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=GithubSearcherExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host="localhost", port=8001)
