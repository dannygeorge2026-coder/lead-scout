from typing import TypedDict, Optional, List, Dict, Any
from backend.agent.schemas import CompanyPainPoints, EmailDraft


class LeadState(TypedDict, total=False):
    """Shared state dictionary maintained across all LangGraph nodes."""

    # Input parameters
    company_domain: str
    contact_name: str
    contact_role: str
    target_offering: str  # The product/service being pitched

    # Web research raw results
    raw_search_results: List[Dict[str, Any]]
    research_attempts: int

    # Extracted structured intelligence
    company_analysis: Optional[CompanyPainPoints]

    # Generated email content
    email_draft: Optional[EmailDraft]

    # Human-in-the-Loop review status
    approval_status: Optional[str]  # "approved", "rejected", "edit_requested"
    human_feedback: Optional[str]

    # Error tracking
    error: Optional[str]