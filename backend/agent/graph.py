from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal

from backend.agent.state import LeadState
from backend.agent.nodes import (
    research_node,
    synthesize_node,
    write_email_node,
    human_review_node,
    crm_logger_node
)


# Conditional Router function
def check_research_success(state: LeadState) -> Literal["synthesize", "research", "END"]:
    """Routes based on research tool outcome and attempt count."""
    results = state.get("raw_search_results", [])
    attempts = state.get("research_attempts", 0)

    if results:
        return "synthesize"
    elif attempts < 2:
        print("[Router] Retrying research attempt...")
        return "research"
    else:
        print("[Router] Research failed max retries. Terminating graph.")
        return "END"


def check_approval_status(state: LeadState) -> Literal["crm_logger", "write_email", "END"]:
    """Routes execution based on human approval decision."""
    status = state.get("approval_status")

    if status == "approved":
        return "crm_logger"
    elif status == "edit_requested":
        print("[Router] Human requested edit. Re-drafting email...")
        return "write_email"
    else:
        print("[Router] Draft rejected by human. Ending workflow.")
        return "END"


# Build the Graph
builder = StateGraph(LeadState)

# Add Nodes
builder.add_node("research", research_node)
builder.add_node("synthesize", synthesize_node)
builder.add_node("write_email", write_email_node)
builder.add_node("human_review", human_review_node)
builder.add_node("crm_logger", crm_logger_node)

# Add Edges
builder.add_edge(START, "research")

builder.add_conditional_edges(
    "research",
    check_research_success,
    {
        "synthesize": "synthesize",
        "research": "research",
        "END": END
    }
)

builder.add_edge("synthesize", "write_email")
builder.add_edge("write_email", "human_review")

builder.add_conditional_edges(
    "human_review",
    check_approval_status,
    {
        "crm_logger": "crm_logger",
        "write_email": "write_email",
        "END": END
    }
)

builder.add_edge("crm_logger", END)


def compile_agent_graph(checkpointer=None):
    """Compiles graph with persistence enabled."""
    saver = checkpointer or MemorySaver()
    return builder.compile(checkpointer=saver)