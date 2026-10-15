import uuid
from langgraph.types import Command
from langgraph.checkpoint.memory import MemorySaver
from backend.agent.graph import compile_agent_graph


def test_agent_graph_interrupt_and_resume():
    graph = compile_agent_graph(checkpointer=MemorySaver())
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    initial_input = {
        "company_domain": "mongodb.com",
        "contact_name": "Dev Lead",
        "contact_role": "CTO",
        "target_offering": "AI Agent Infrastructure",
    }

    # Step 1: run until the human review interrupt
    print("\n--- Running Graph to Interrupt ---")
    list(graph.stream(initial_input, config=config))

    snapshot = graph.get_state(config)
    vals = snapshot.values
    print("ERROR:", vals.get("error"))
    print("ANALYSIS:", vals.get("company_analysis"))
    print("DRAFT:", vals.get("email_draft"))

    assert snapshot.next == ("human_review",), "Graph should pause at human_review"
    assert not vals.get("error"), f"A node failed: {vals.get('error')}"
    assert vals.get("company_analysis"), "Synthesize produced no analysis"
    assert vals.get("email_draft"), "Writer produced no email draft"

    # Step 2: resume with approval
    print("\n--- Resuming Graph with Approval ---")
    list(graph.stream(Command(resume={"status": "approved", "feedback": ""}), config=config))

    final = graph.get_state(config).values
    assert final["approval_status"] == "approved"
    assert final["email_draft"] is not None
    print("\n✅ Interrupt and resume worked")


if __name__ == "__main__":
    test_agent_graph_interrupt_and_resume()