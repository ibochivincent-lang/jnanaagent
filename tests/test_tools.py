from research_agent.state import SearchResult
from research_agent.tools import dedupe_results


def _r(url):
    return SearchResult(title=url, url=url)


def test_dedupe_keeps_first_occurrence():
    results = [_r("https://a.com/x"), _r("https://b.com"), _r("https://a.com/x")]
    unique = dedupe_results(results)
    assert [r.url for r in unique] == ["https://a.com/x", "https://b.com"]


def test_dedupe_ignores_trailing_slash():
    results = [_r("https://a.com/x/"), _r("https://a.com/x")]
    assert len(dedupe_results(results)) == 1


def test_parse_github_issue_ref():
    from research_agent.tools import parse_github_issue_ref
    assert parse_github_issue_ref("https://github.com/langchain-ai/langgraph/issues/3898") == ("langchain-ai", "langgraph", 3898)
    assert parse_github_issue_ref("https://github.com/langchain-ai/langgraph/pull/420") == ("langchain-ai", "langgraph", 420)
    assert parse_github_issue_ref("langchain-ai/langgraph#3898") == ("langchain-ai", "langgraph", 3898)
    assert parse_github_issue_ref("Investigate langchain-ai/langgraph#3898 memory leak") == ("langchain-ai", "langgraph", 3898)
    assert parse_github_issue_ref("Stripe vs Adyen market share") is None


def test_entire_search_memory_live():
    from research_agent.tools import entire_search_memory
    sources = entire_search_memory("search")
    assert isinstance(sources, list)
    if sources:
        assert sources[0].source_type == "entire_memory"
        assert len(sources[0].sha256) == 64
        assert sources[0].verified is True

