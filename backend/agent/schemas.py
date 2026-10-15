from pydantic import BaseModel,Field
from typing import Optional, List

class CompanyPainPoints(BaseModel):
    """Structured extraction model for company research findings."""

    company_name: str = Field(description="Official name of the target company")
    industry: str = Field(description="Primary industry or business vertical")
    summary: str = Field(description="2-3 sentence overview of what the company does")
    recent_events: List[str] = Field(
        default_factory=list,
        description="Key recent news items, funding events, or product launches"
    )
    key_challenges: List[str] = Field(
        default_factory=list,
        description="Operational or technical challenges the company likely faces"
    )
    value_proposition_triggers: List[str] = Field(
        default_factory=list,
        description="Hooks or angles connecting our solution to their current situation"
    )


class EmailDraft(BaseModel):
    """Structured output model for the cold email draft."""

    subject_line: str = Field(description="Punchy, non-spammy email subject line")
    body: str = Field(description="Personalized 3-paragraph cold email draft")
    call_to_action: str = Field(description="Clear, low-friction closing call to action")
    