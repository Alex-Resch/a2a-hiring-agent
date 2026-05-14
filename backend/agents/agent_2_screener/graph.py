from langgraph.graph import END, StateGraph

from agents.agent_2_screener.nodes import score_profiles
from agents.agent_2_screener.state import AgentState


graph = StateGraph(AgentState)
graph.add_node("score_profiles", score_profiles)

graph.set_entry_point("score_profiles")
graph.add_edge("score_profiles", END)

app = graph.compile()
