from backend.agent.tools import execute_company_research


def test_tavily_search():
    domain = "stripe.com"
    results = execute_company_research(domain)

    assert isinstance(results, list)
    assert len(results) > 0, "Should return at least 1 search result"
    assert "content" in results[0] or "title" in results[0]
    print(f"\n✅ Tavily Search returned {len(results)} items for {domain}")


if __name__ == "__main__":
    test_tavily_search()