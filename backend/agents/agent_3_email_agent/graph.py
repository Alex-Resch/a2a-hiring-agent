from langgraph.graph import END, StateGraph

from agents.agent_3_email_agent.nodes import (
    check_busy_slots,
    get_free_slots,
    create_appointment,
    send_interview_invitations,
)
from agents.agent_3_email_agent.state import AgentState

# Phase 1: Check calendar → find free slots
calendar_graph1 = StateGraph(AgentState)
calendar_graph1.add_node("check_busy_slots", check_busy_slots)
calendar_graph1.add_node("get_free_slots", get_free_slots)
calendar_graph1.set_entry_point("check_busy_slots")
calendar_graph1.add_edge("check_busy_slots", "get_free_slots")
calendar_graph1.add_edge("get_free_slots", END)
calendar_phase1_app = calendar_graph1.compile()

# Phase 2: Create appointment → send invitations
calendar_graph2 = StateGraph(AgentState)
calendar_graph2.add_node("create_appointment", create_appointment)
calendar_graph2.add_node("send_interview_invitations", send_interview_invitations)
calendar_graph2.set_entry_point("create_appointment")
calendar_graph2.add_edge("create_appointment", "send_interview_invitations")
calendar_graph2.add_edge("send_interview_invitations", END)
calendar_phase2_app = calendar_graph2.compile()
