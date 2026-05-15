import json
from uuid import uuid4
from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    Message,
    Part,
    Role,
    TextPart,
)
import httpx
from typing import AsyncGenerator

from agents.agent_3_email_agent.state import FreeSlot
from shared.models import SearchRequest, SelectedProfile


async def run_calendar_phase1(selected_profiles: list) -> AsyncGenerator[dict, None]:
    async with httpx.AsyncClient(timeout=300) as http_client:
        yield {"status": "Agent 3 is checking calendar..."}

        resolver3 = A2ACardResolver(
            httpx_client=http_client, base_url="http://localhost:8003"
        )
        card3 = await resolver3.get_agent_card()
        client3 = A2AClient(httpx_client=http_client, agent_card=card3)

        request3 = SendMessageRequest(
            id=uuid4().hex,
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[
                        Part(
                            root=TextPart(
                                text=json.dumps(
                                    {
                                        "selected_profiles": [
                                            p.model_dump() for p in selected_profiles
                                        ]
                                    }
                                )
                            )
                        )
                    ],
                    message_id=uuid4().hex,
                )
            ),
        )

        response3 = await client3.send_message(request3)

        try:
            result_text = response3.root.result.parts[0].root.text  # type: ignore
            result = json.loads(result_text)
        except Exception as e:
            yield {"status": "Error", "error": f"Agent 3 failed: {str(e)}"}
            return

        yield {
            "status": "Free slots found",
            "free_slots": result["free_slots"],
            "busy_slots": result["busy_slots"],
        }


async def run_calendar_phase2(
    selected_profiles: list[SelectedProfile],
    selected_slot: FreeSlot,
) -> AsyncGenerator[dict, None]:
    async with httpx.AsyncClient(timeout=300) as http_client:
        yield {"status": "Agent 3 is scheduling appointment..."}

        resolver3 = A2ACardResolver(
            httpx_client=http_client, base_url="http://localhost:8003"
        )
        card3 = await resolver3.get_agent_card()
        client3 = A2AClient(httpx_client=http_client, agent_card=card3)

        payload = {
            "selected_profiles": [p.model_dump() for p in selected_profiles],
            "selected_slot": selected_slot.model_dump(mode="json"),
        }

        request3 = SendMessageRequest(
            id=uuid4().hex,
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[Part(root=TextPart(text=json.dumps(payload)))],
                    message_id=uuid4().hex,
                )
            ),
        )

        try:
            await client3.send_message(request3)
        except Exception as e:
            yield {"status": "Error", "error": f"Agent 3 failed: {str(e)}"}
            return

        yield {
            "status": "Done",
        }


async def run(request: SearchRequest) -> AsyncGenerator[dict, None]:
    user_input = json.dumps(request.model_dump())

    async with httpx.AsyncClient(timeout=300) as http_client:
        yield {"status": "Agent 1 is searching GitHub profiles..."}

        resolver1 = A2ACardResolver(
            httpx_client=http_client, base_url="http://localhost:8001"
        )
        card1 = await resolver1.get_agent_card()
        client1 = A2AClient(httpx_client=http_client, agent_card=card1)

        request1 = SendMessageRequest(
            id=uuid4().hex,
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[Part(root=TextPart(text=user_input))],
                    message_id=uuid4().hex,
                )
            ),
        )

        response1 = await client1.send_message(request1)

        try:
            profiles_text = response1.root.result.parts[0].root.text  # type: ignore
            profiles = json.loads(profiles_text)
        except Exception as e:
            yield {"status": "Error", "error": f"Agent 1 failed: {str(e)}"}
            return

        yield {"status": f"{len(profiles)} profiles found", "profiles": profiles}
        yield {"status": "Agent 2 is scoring profiles..."}

        resolver2 = A2ACardResolver(
            httpx_client=http_client, base_url="http://localhost:8002"
        )
        card2 = await resolver2.get_agent_card()
        client2 = A2AClient(httpx_client=http_client, agent_card=card2)

        request2 = SendMessageRequest(
            id=uuid4().hex,
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[Part(root=TextPart(text=profiles_text))],
                    message_id=uuid4().hex,
                )
            ),
        )

        response2 = await client2.send_message(request2)

        try:
            scored_text = response2.root.result.parts[0].root.text  # type: ignore
            scored_profiles = json.loads(scored_text)
        except Exception as e:
            yield {"status": "Error", "error": f"Agent 2 failed: {str(e)}"}
            return

        yield {"status": "Done", "scored_profiles": scored_profiles}
