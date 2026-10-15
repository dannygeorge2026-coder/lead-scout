from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import interrupt
from typing import Dict, Any, Optional

from backend.config import settings
from backend.agent.state import LeadState
from backend.agent.schemas import CompanyPainPoints, EmailDraft
from backend.agent.tools import execute_company_research


# Initialize Gemini LLM with structured output support
llm = ChatGoogleGenerativeAI(
    model=settings.DEFAULT_MODEL,
    temperature=settings.MODEL_TEMPERATURE,
    google_api_key=settings.GOOGLE_API_KEY
)


def research_node(state: LeadState) -> Dict[str, Any]:
    """Node 1: Scrapes web data for the given domain."""
    domain = state.get("company_domain", "")
    attempts = state.get("research_attempts", 0) + 1

    print(f"\n[Node: Research] Execution attempt #{attempts} for {domain}...")

    results = execute_company_research(domain)

    if not results:
        return {
            "raw_search_results": [],
            "research_attempts": attempts,
            "error": f"No search results returned for {domain}"
        }

    return {
        "raw_search_results": results,
        "research_attempts": attempts,
        "error": None
    }


def synthesize_node(state: LeadState) -> Dict[str, Any]:
    """Node 2: Uses LLM with structured output to extract company pain points."""
    domain = state.get("company_domain", "")
    search_data = state.get("raw_search_results", [])

    print(f"\n[Node: Synthesize] Analyzing raw search findings for {domain}...")

    context = "\n\n".join([
        f"Title: {res.get('title')}\nContent: {res.get('content')}"
        for res in search_data
    ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert enterprise business intelligence analyst. "
            "Extract company details, recent news, pain points, and sales hooks from the provided text."
        )),
        ("human", "Company Domain: {domain}\n\nSearch Context:\n{context}")
    ])

    structured_llm = llm.with_structured_output(CompanyPainPoints)
    chain = prompt | structured_llm

    try:
        analysis: CompanyPainPoints = chain.invoke({"domain": domain, "context": context[:8000]})
        return {
            "company_analysis": analysis.model_dump() if analysis else None,
            "error": None
        }
    except Exception as e:
        return {"error": f"Synthesis failed: {str(e)}"}


def write_email_node(state: LeadState) -> Dict[str, Any]:
    """Node 3: Crafts personalized outreach email draft."""
    analysis: Optional[Dict[str, Any]] = state.get("company_analysis")
    contact_name = state.get("contact_name", "Prospect")
    contact_role = state.get("contact_role", "Decision Maker")
    offering = state.get("target_offering", "our platform")
    feedback = state.get("human_feedback")

    print(f"\n[Node: Writer] Drafting cold email for {contact_name} ({contact_role})...")

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an elite B2B Sales Development Representative. "
            "Draft a concise, compelling cold outreach email based on company research. "
            "Keep it under 150 words. Focus on the prospect's pain points. "
            "If human feedback is provided, adjust the draft accordingly."
        )),
        ("human", (
            "Contact Name: {contact_name}\n"
            "Contact Role: {contact_role}\n"
            "Pitching Offering: {offering}\n"
            "Company Summary: {summary}\n"
            "Triggers: {triggers}\n"
            "Human Feedback (if any): {feedback}"
        ))
    ])

    structured_llm = llm.with_structured_output(EmailDraft)
    chain = prompt | structured_llm

    summary = analysis.get("summary", "N/A") if isinstance(analysis, dict) else "N/A"
    triggers = ", ".join(analysis.get("value_proposition_triggers", [])) if isinstance(analysis, dict) else "N/A"

    try:
        draft: EmailDraft = chain.invoke({
            "contact_name": contact_name,
            "contact_role": contact_role,
            "offering": offering,
            "summary": summary,
            "triggers": triggers,
            "feedback": feedback or "None"
        })
        return {
            "email_draft": draft.model_dump() if draft else None,
            "error": None
        }
    except Exception as e:
        return {"error": f"Email drafting failed: {str(e)}"}


def human_review_node(state: LeadState) -> Dict[str, Any]:
    """Node 4: Human-in-the-loop review interrupt checkpoint."""
    draft: Optional[Dict[str, Any]] = state.get("email_draft")

    print("\n[Node: Human Review] Pausing workflow for review...")

    # Pauses graph execution and passes state data to the client
    review_response = interrupt({
        "message": "Cold email generated. Please review, edit, approve, or reject.",
        "email_draft": draft
    })

    # When resumed via Command(resume=...), the response is received here
    status = review_response.get("status")  # "approved", "rejected", "edit_requested"
    feedback = review_response.get("feedback", "")

    return {
        "approval_status": status,
        "human_feedback": feedback,
        "email_draft": draft
    }


def crm_logger_node(state: LeadState) -> Dict[str, Any]:
    """Node 5: Final node logging outreach to CRM / DB."""
    status = state.get("approval_status")
    print(f"\n[Node: CRM Logger] Email status: {status}. Logging to database...")
    return {}