"""Node-level tests: every node is exercised in isolation with stubbed LLM/network calls."""

import pytest

from research_agent import config, nodes
from research_agent.state import ResearchPlan, SearchResult, Source, SourceSelection


class StubLLM:
    """Stands in for ChatAnthropic: records prompts, returns canned results."""

    def __init__(self, result):
        self.result = result
        self.prompts = []

    def with_structured_output(self, schema):
        return self

    def invoke(self, prompt):
        self.prompts.append(prompt)
        return self.result


PLAN = ResearchPlan(
    objective="Explain X",
    search_queries=["x basics", "x criticism"],
    outline=["Background", "Findings"],
).model_dump()


def test_plan_node_returns_plan_and_clears_feedback(monkeypatch):
    stub = StubLLM(ResearchPlan.model_validate(PLAN))
    monkeypatch.setattr(nodes.llm, "get_llm", lambda **kw: stub)
    out = nodes.plan({"topic": "X", "feedback": "too narrow"})
    assert out["plan"] == PLAN
    assert out["feedback"] == ""
    # human feedback must actually reach the prompt on a revision pass
    assert "too narrow" in stub.prompts[0]


def test_search_broadens_queries_on_retry(monkeypatch):
    calls = []
    monkeypatch.setattr(nodes.tools, "web_search", lambda q, **kw: calls.append(q) or [])
    nodes.search({"topic": "X", "plan": PLAN, "search_round": 1})
    assert "X overview" in calls  # round 2 adds broadened queries
    assert "x basics" in calls


def test_select_sources_drops_hallucinated_urls(monkeypatch):
    candidates = [SearchResult(title="A", url="https://a.com"), SearchResult(title="B", url="https://b.com")]
    selection = SourceSelection(urls=["https://a.com", "https://fake.invalid"], reasoning="test")
    monkeypatch.setattr(nodes.llm, "get_llm", lambda **kw: StubLLM(selection))
    out = nodes.select_sources({"plan": PLAN, "search_results": candidates})
    assert [r.url for r in out["search_results"]] == ["https://a.com"]


def test_fetch_skips_failed_pages(monkeypatch):
    def fake_fetch(url, title=""):
        return Source(title=title, url=url, text="x" * 300) if "good" in url else None

    monkeypatch.setattr(nodes.tools, "fetch_page", fake_fetch)
    monkeypatch.setattr(nodes.tools, "crustdata_enrich_company", lambda d: None)
    out = nodes.fetch(
        {"search_results": [SearchResult(title="g", url="https://good.com"),
                            SearchResult(title="b", url="https://bad.com")]}
    )
    assert len(out["sources"]) == 1


def test_fetch_adds_crustdata_enrichment(monkeypatch):
    monkeypatch.setattr(nodes.tools, "fetch_page", lambda u, **kw: Source(title=u, url=u, text="x" * 300))
    monkeypatch.setattr(
        nodes.tools,
        "crustdata_enrich_company",
        lambda d: Source(title=f"Crustdata: {d}", url=f"https://{d}", text="Company details", source_type="crustdata_live")
    )
    monkeypatch.setenv("CRUSTDATA_API_KEY", "dummy_key")
    out = nodes.fetch({"search_results": [SearchResult(title="Stripe", url="https://stripe.com/about")]})
    assert len(out["sources"]) == 2
    assert any(s.source_type == "crustdata_live" for s in out["sources"])


@pytest.mark.parametrize(
    "n_sources,search_round,expected",
    [
        (config.MIN_SOURCES, 1, "synthesize"),        # enough evidence -> write
        (0, 1, "search"),                             # not enough -> retry
        (0, config.MAX_SEARCH_ROUNDS, "synthesize"),  # retries exhausted -> write anyway
    ],
)
def test_route_after_fetch(n_sources, search_round, expected):
    state = {
        "sources": [Source(title="t", url="u", text="x") for _ in range(n_sources)],
        "search_round": search_round,
    }
    assert nodes.route_after_fetch(state) == expected


def test_synthesize_appends_proof_of_search_audit(monkeypatch):
    class StubLLMResponse:
        text = "# Sample Report\n\nExecutive summary."
    
    class StubSynthesizeLLM:
        def invoke(self, prompt):
            return StubLLMResponse()

    monkeypatch.setattr(nodes.llm, "get_llm", lambda **kw: StubSynthesizeLLM())
    state = {
        "topic": "Payments",
        "plan": {"objective": "Explain payments", "outline": ["Overview"]},
        "sources": [
            Source(title="Stripe", url="https://stripe.com", text="Stripe info", sha256="abc1234567890def", verified=True)
        ],
    }
    out = nodes.synthesize(state)
    assert "Proof of Search: Cryptographic Provenance Audit" in out["report"]
    assert "abc1234567890def"[:16] in out["report"]


def test_is_code_issue_task():
    from research_agent.nodes import is_code_issue_task
    assert is_code_issue_task("Investigate LangGraph memory leak in checkpointing") is True
    assert is_code_issue_task("https://github.com/langchain-ai/langgraph/issues/3898") is True
    assert is_code_issue_task("langchain-ai/langgraph#3898") is True
    assert is_code_issue_task("Fix bug in nodes.py: KeyError on state") is True
    assert is_code_issue_task("Stripe vs Adyen market share") is False


def test_extract_code_patch():
    from research_agent.nodes import extract_code_patch
    report = """# Resolution
Some explanation.
```diff
diff --git a/pkg/graph.py b/pkg/graph.py
--- a/pkg/graph.py
+++ b/pkg/graph.py
@@ -10,3 +10,3 @@
- old_leaky_cache.clear()
+ weakref_cache.clear()
```
Further notes.
"""
    patch = extract_code_patch(report)
    assert "diff --git a/pkg/graph.py b/pkg/graph.py" in patch
    assert "+ weakref_cache.clear()" in patch


def test_extract_test_verification():
    from research_agent.nodes import extract_test_verification
    report = """# Resolution
## 5. Reproduction & Verification Test Plan
```python
def test_checkpoint_memory_leak():
    assert True
```
"""
    test_code = extract_test_verification(report)
    assert "def test_checkpoint_memory_leak():" in test_code


def test_extract_similar_issues():
    from research_agent.nodes import extract_similar_issues
    from research_agent.state import Source
    sources = [
        Source(title="Issue 3898", url="https://github.com/langchain/langgraph/issues/3898", text="leak", source_type="github_issue", sha256="123"),
        Source(title="PR 4001", url="https://github.com/langchain/langgraph/pull/4001", text="fix", source_type="github_pr", sha256="456"),
        Source(title="Memory Invariant", url="entire://repo", text="arch", source_type="entire_memory", sha256="789"),
        Source(title="Blog Post", url="https://medium.com/post", text="article", source_type="web", sha256="abc"),
    ]
    similar = extract_similar_issues(sources)
    assert len(similar) == 3
    types = [s["type"] for s in similar]
    assert "github_issue" in types
    assert "github_pr" in types
    assert "entire_memory" in types


def test_extract_multi_file_patches():
    from research_agent.nodes import extract_multi_file_patches
    multi_diff = """```diff
diff --git a/src/sweagent/run.py b/src/sweagent/run.py
--- a/src/sweagent/run.py
+++ b/src/sweagent/run.py
@@ -10,1 +10,1 @@
- old_line
+ new_line

diff --git a/tests/test_run.py b/tests/test_run.py
--- a/tests/test_run.py
+++ b/tests/test_run.py
@@ -20,1 +20,1 @@
- assert False
+ assert True
```"""
    parsed = extract_multi_file_patches(multi_diff)
    assert parsed["total_files"] == 2
    assert len(parsed["files"]) == 2
    assert "sweagent/run.py" in parsed["files"][0]["filename"]
    assert "test_run.py" in parsed["files"][1]["filename"]


def test_extract_consensus_matrix():
    from research_agent.nodes import extract_consensus_matrix
    from research_agent.state import Source
    sources = [
        Source(title="Source 1", url="https://example.com/1", text="Data", sha256="111", verified=True, source_type="web"),
        Source(title="Crustdata B2B", url="https://crustdata.com", text="Company", sha256="222", verified=True, source_type="crustdata_live"),
    ]
    matrix = extract_consensus_matrix("", sources)
    assert len(matrix) >= 2
    assert any("Crustdata" in m["claim"] or "Company" in m["claim"] for m in matrix)


def test_approve_plan_interrupt_and_otel_span(monkeypatch):
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, START, StateGraph
    from opentelemetry import trace
    from opentelemetry.trace import StatusCode
    from research_agent.state import ResearchState

    class MockSpan:
        def __init__(self):
            self.status = None

        def is_recording(self):
            return True

        def set_status(self, status):
            self.status = status

    mock_span = MockSpan()
    monkeypatch.setattr(trace, "get_current_span", lambda: mock_span)

    # Test approve_plan in compiled graph runnable context
    g = StateGraph(ResearchState)
    g.add_node("approve_plan", nodes.approve_plan)
    g.add_edge(START, "approve_plan")
    g.add_edge("approve_plan", END)
    app = g.compile(checkpointer=MemorySaver())

    state = {"topic": "test", "plan": {"objective": "Test", "search_queries": []}}
    res = app.invoke(state, {"configurable": {"thread_id": "test-otel-span"}})

    # Verify interrupt triggered cleanly and span was marked as OK to prevent Neatlogs error
    assert "__interrupt__" in res
    assert mock_span.status == StatusCode.OK
