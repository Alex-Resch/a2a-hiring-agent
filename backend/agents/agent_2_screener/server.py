import json
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.utils import new_agent_text_message

from agents.agent_2_screener.graph import app
from agents.agent_2_screener.state import AgentState


class GithubScreenerExecutor(AgentExecutor):
    """Execute the screening graph for incoming requests."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Run the graph and emit scored profiles as a text message."""
        user_input = context.get_user_input()
        data = json.loads(user_input)
        profiles_details = data["profiles"]
        search_criteria = data["user_input"]
        result = app.invoke(
            AgentState(
                profiles_details=profiles_details,
                user_input=search_criteria,
            )
        )
        output = json.dumps([p.model_dump() for p in result["scored_profiles"]])
        await event_queue.enqueue_event(new_agent_text_message(output))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Reject cancellation since it is not supported."""
        raise Exception("cancel not supported")


if __name__ == "__main__":
    skill = AgentSkill(
        id="github_screening",
        name="GitHub Profile Screening",
        description="Scores and evaluates GitHub profiles based on code quality, activity and impact",
        tags=["github", "screening", "scoring"],
        examples=["[{name: 'tiangolo', repos: [...]}]"],
    )

    agent_card = AgentCard(
        name="github-profile-screener",
        description="Scores and evaluates GitHub profiles based on code quality, activity, technical breadth and community impact",
        url="http://localhost:8002/",
        version="0.1.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=GithubScreenerExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host="localhost", port=8002)
