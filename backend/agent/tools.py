from tavily import TavilyClient
from backend.config import settings
from typing import List, Dict, Any


def execute_company_research(domain: str) -> List[Dict[str, Any]]:
    """Performs web search using Tavily API to collect company news and overview."""
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    query = f"{domain} company overview recent news technology product offerings"

    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )

        results = response.get("results", [])
        if not results and response.get("answer"):
            results = [{"title": "Summary Answer", "content": response["answer"], "url": ""}]

        return results
    except Exception as e:
        print(f"[Tool Error] Tavily search failed for domain {domain}: {str(e)}")
        return []