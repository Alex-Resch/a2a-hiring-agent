import json
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.utils import new_agent_text_message

from agents.agent_3_email_agent.graph import calendar_phase1_app, calendar_phase2_app


class CalendarAgentExecutor(AgentExecutor):
    """Execute calendar and email flows based on request payload."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Run phase 1 or 2 and emit the result as a text message."""
        user_input = json.loads(context.get_user_input())

        if "selected_slot" not in user_input:
            result = calendar_phase1_app.invoke(user_input)
            output = json.dumps(
                {
                    "free_slots": [
                        {"start": s.start.isoformat(), "end": s.end.isoformat()}
                        for s in result["free_slots"]
                    ],
                    "busy_slots": [
                        {"start": s.start.isoformat(), "end": s.end.isoformat()}
                        for s in result["busy_slots"]
                    ],
                }
            )
        else:
            result = calendar_phase2_app.invoke(user_input)
            output = json.dumps(
                {
                    "created_events": result["created_events"],
                    "emails_sent": [e.model_dump() for e in result["emails_sent"]],
                }
            )

        await event_queue.enqueue_event(new_agent_text_message(output))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Reject cancellation since it is not supported."""
        raise Exception("cancel not supported")


if __name__ == "__main__":
    skill = AgentSkill(
        id="calendar_scheduling",
        name="Calendar Scheduling",
        description="Checks calendar availability and schedules interview appointments",
        tags=["calendar", "scheduling", "email"],
        examples=["[{username: 'torvalds', email: 'torvalds@example.com'}]"],
    )

    agent_card = AgentCard(
        name="calendar-agent",
        description="Checks user calendar for free slots and schedules interview appointments with email invitations",
        url="http://localhost:8003/",
        version="0.1.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(),
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=CalendarAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    uvicorn.run(server.build(), host="localhost", port=8003)
