from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from langgraph.types import Command
import uuid

from backend.database.session import get_checkpointer
from backend.agent.graph import compile_agent_graph


app = FastAPI(title="LeadScout Agent API", version="1.0.0")


class LeadRequest(BaseModel):
    company_domain: str
    contact_name: str
    contact_role: str
    target_offering: str


class ResumeRequest(BaseModel):
    thread_id: str
    status: str  # "approved", "rejected", "edit_requested"
    feedback: Optional[str] = ""


@app.post("/api/leads/start")
async def start_lead_workflow(request: LeadRequest):
    """Starts new lead outreach workflow and runs until interrupt or completion."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    input_data = request.model_dump()

    async with get_checkpointer() as saver:
        graph = compile_agent_graph(checkpointer=saver)

        # Stream graph execution until it pauses at the interrupt or finishes
        async for _ in graph.astream(input_data, config=config):
            pass

        state = await graph.aget_state(config)

    # Check if graph paused at the human review node
    is_interrupted = len(state.next) > 0 and state.next[0] == "human_review"

    return {
        "thread_id": thread_id,
        "is_waiting_for_approval": is_interrupted,
        "state": state.values
    }


@app.get("/api/leads/{thread_id}/state")
async def get_lead_state(thread_id: str):
    """Retrieves current execution state of an existing thread."""
    config = {"configurable": {"thread_id": thread_id}}

    async with get_checkpointer() as saver:
        graph = compile_agent_graph(checkpointer=saver)
        state = await graph.aget_state(config)

    if not state.values:
        raise HTTPException(status_code=404, detail="Thread not found")

    return {
        "thread_id": thread_id,
        "next_nodes": state.next,
        "state": state.values
    }


@app.post("/api/leads/resume")
async def resume_lead_workflow(request: ResumeRequest):
    """Resumes a paused workflow thread after human review input."""
    config = {"configurable": {"thread_id": request.thread_id}}

    # Command injects the human response directly into the pending interrupt()
    resume_payload = Command(resume={
        "status": request.status,
        "feedback": request.feedback
    })

    async with get_checkpointer() as saver:
        graph = compile_agent_graph(checkpointer=saver)

        async for _ in graph.astream(resume_payload, config=config):
            pass

        state = await graph.aget_state(config)

    return {
        "thread_id": request.thread_id,
        "next_nodes": state.next,
        "state": state.values
    }