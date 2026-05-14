from langgraph.graph import StateGraph, END

from agents.agent_1_github_searcher.nodes import search_profiles, get_profile_details
from agents.agent_1_github_searcher.state import AgentState


graph = StateGraph(AgentState)
graph.add_node("search_profiles", search_profiles)
graph.add_node("get_profile_details", get_profile_details)

graph.set_entry_point("search_profiles")
graph.add_edge("search_profiles", "get_profile_details")
graph.add_edge("get_profile_details", END)

app = graph.compile()
