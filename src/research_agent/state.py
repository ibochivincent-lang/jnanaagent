"""Graph state and the structured objects that flow through it."""

from typing import TypedDict

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    """The plan the agent proposes before any searching happens."""

    objective: str = Field(description="One-sentence statement of what the report will answer")
    search_queries: list[str] = Field(
        description="3-5 web search queries that together cover the topic", min_length=1
    )
    outline: list[str] = Field(
        description="Section headings the final report should contain", min_length=1
    )


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""


class SourceSelection(BaseModel):
    """LLM's pick of which search results are worth fetching."""

    urls: list[str] = Field(description="URLs to fetch, most promising first")
    reasoning: str = Field(description="One sentence on why these were chosen")


class Source(BaseModel):
    """A fetched and text-extracted web page, B2B intelligence record, or GitHub issue."""

    title: str
    url: str
    text: str
    sha256: str = ""
    verified: bool = True
    source_type: str = "web"  # "web" | "crustdata_live" | "github_issue" | "github_pr" | "entire_memory"
    evidence_quote: str = ""  # Direct extracted quote proving the citation
    status_code: int = 200
    domain: str = ""


class ResearchState(TypedDict, total=False):
    topic: str
    feedback: str  # human feedback when a plan is sent back for revision
    plan: dict  # ResearchPlan.model_dump() — plain dict keeps checkpoints serializer-friendly
    search_results: list[SearchResult]
    sources: list[Source]
    search_round: int
    report: str
    recoveries: list[dict]  # Tool recovery events for hackathon failure handling
    disagreements: list[dict]  # Detected and resolved source contradictions
    code_patch: str  # Unified diff patch for autonomous SWE resolution
    similar_issues: list[dict]  # Similar GitHub issues & Entire memory records
    test_verification: str  # Executable reproduction/verification test code

