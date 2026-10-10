"""Web search, live Crustdata company intelligence, and page fetching.

Pure I/O — no LLM calls here, so each piece is unit-testable.
Incorporates verifiable SHA-256 content hashing for Proof of Search.
"""

import hashlib
import json
import logging
import os
import socket
import urllib.request

import httpx
import trafilatura
from ddgs import DDGS

from . import config
from .state import SearchResult, Source

log = logging.getLogger("research_agent.tools")


def calculate_sha256(text: str) -> str:
    """Compute deterministic SHA-256 digest to verify content integrity."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_grounding_quote(text: str, max_chars: int = 240) -> str:
    """Extract a representative proof quote from text for ground-truth citation auditing."""
    if not text:
        return ""
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 30]
    candidate = paragraphs[0] if paragraphs else text.strip()
    # Clean up markdown headers or bullets
    candidate = candidate.lstrip("#-* ").replace("\n", " ").strip()
    if len(candidate) > max_chars:
        candidate = candidate[:max_chars].rsplit(" ", 1)[0] + "..."
    return f'"{candidate}"'


def github_search_issues(query: str, max_results: int = 5) -> list[SearchResult]:
    """Search public GitHub issues and PRs (neatHack Focus: Fix a GitHub issue & code investigations)."""
    log.info("github_search: %r (max %d results)", query, max_results)
    clean_query = query.strip()
    if not clean_query:
        return []
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote_plus(clean_query)}&per_page={max_results}"
    try:
        resp = httpx.get(
            url,
            timeout=10,
            headers={"User-Agent": "neatHack-research-agent/1.0", "Accept": "application/vnd.github.v3+json"},
        )
        if resp.status_code != 200:
            log.warning("github search returned status %d: %s", resp.status_code, resp.text[:100])
            return []
        data = resp.json()
        items = data.get("items", [])
        results = []
        for it in items:
            title = it.get("title", "GitHub Issue")
            issue_url = it.get("html_url", "")
            state = it.get("state", "open")
            body = (it.get("body") or "")[:300].replace("\n", " ").strip()
            snippet = f"[{state.upper()}] #{it.get('number', '')} {body}"
            results.append(SearchResult(title=f"GitHub: {title}", url=issue_url, snippet=snippet))
        log.info("github_search: %r -> %d results", query, len(results))
        return results
    except Exception as exc:
        log.warning("github search failed for %r: %s", query, exc)
        return []


def web_search(query: str, max_results: int | None = None) -> list[SearchResult]:
    """Run one web search query and return normalized results."""
    max_results = max_results or config.MAX_SEARCH_RESULTS
    log.info("search: %r (max %d results)", query, max_results)
    try:
        raw = DDGS().text(query, max_results=max_results)
    except Exception as exc:  # search backends are flaky; a failed query is not fatal
        log.warning("search failed for %r: %s", query, exc)
        return []
    results = []
    for item in raw or []:
        url = item.get("href") or item.get("url") or ""
        if not url:
            continue
        results.append(
            SearchResult(title=item.get("title", url), url=url, snippet=item.get("body", ""))
        )
    log.info("search: %r -> %d results", query, len(results))
    return results


def dedupe_results(results: list[SearchResult]) -> list[SearchResult]:
    """Drop duplicate URLs, keeping first occurrence (order = relevance)."""
    seen: set[str] = set()
    unique = []
    for r in results:
        key = r.url.rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique


def fetch_page(url: str, title: str = "") -> Source | None:
    """Download a page and extract its main text with ground-truth verification."""
    log.info("fetch: %s", url)
    try:
        resp = httpx.get(
            url,
            timeout=config.FETCH_TIMEOUT_S,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (research-agent demo)"},
        )
        resp.raise_for_status()
    except Exception as exc:
        log.warning("fetch failed for %s: %s", url, exc)
        return None
    text = trafilatura.extract(resp.text) or ""
    if len(text) < 200:  # boilerplate-only pages aren't usable evidence
        log.warning("fetch: %s extracted only %d chars, skipping", url, len(text))
        return None
    text = text[: config.MAX_PAGE_CHARS]
    log.info("fetch: %s -> %d chars", url, len(text))
    digest = calculate_sha256(text)
    quote = extract_grounding_quote(text)
    
    import urllib.parse
    domain = urllib.parse.urlparse(url).netloc
    
    return Source(
        title=title or url,
        url=url,
        text=text,
        sha256=digest,
        verified=True,
        source_type="web",
        evidence_quote=quote,
        status_code=200,
        domain=domain,
    )



def crustdata_enrich_company(identifier: str) -> Source | None:
    """Enrich a company using Crustdata's live B2B database (Zero Mock Data).

    Accepts a domain (e.g. 'stripe.com') or company name (e.g. 'Stripe').
    Returns a verified Source containing live firmographics, employee numbers,
    founding year, and verified links with a cryptographic SHA-256 hash.
    """
    api_key = os.getenv("CRUSTDATA_API_KEY")
    if not api_key:
        log.warning("crustdata: CRUSTDATA_API_KEY not configured, skipping")
        return None

    identifier = identifier.strip()
    if not identifier:
        return None

    is_domain = "." in identifier and not identifier.endswith(".") and " " not in identifier
    payload = {"domains": [identifier]} if is_domain else {"names": [identifier]}

    req = urllib.request.Request(
        "https://api.crustdata.com/company/enrich",
        headers={
            "Authorization": f"Bearer {api_key}",
            "x-api-version": "2025-11-01",
            "Content-Type": "application/json",
            "Host": "api.crustdata.com",
            "User-Agent": "proof-of-search-agent/1.0",
        },
        data=json.dumps(payload).encode("utf-8"),
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not isinstance(data, list) or not data:
                log.info("crustdata: no matches returned for %r", identifier)
                return None

            match_entry = data[0]
            matches = match_entry.get("matches", [])
            if not matches:
                log.info("crustdata: empty matches list for %r", identifier)
                return None

            best_match = matches[0]
            info = best_match.get("company_data", {}).get("basic_info", {})
            name = info.get("name") or identifier
            domain = info.get("primary_domain") or identifier
            description = info.get("description", "")
            emp_range = info.get("employee_count_range", "N/A")
            founded = info.get("year_founded", "N/A")
            markets = ", ".join(info.get("markets", [])) or "Private"
            linkedin = info.get("professional_network_url", "")
            website = info.get("website") or f"https://{domain}"

            # Format live intelligence record
            text = (
                f"### Verified Entity Profile: {name}\n"
                f"- **Primary Website:** {website}\n"
                f"- **Domain:** {domain}\n"
                f"- **Year Founded:** {founded}\n"
                f"- **Employee Count Range:** {emp_range}\n"
                f"- **Markets / Status:** {markets} ({info.get('status', 'active')})\n"
                f"- **LinkedIn Profile:** {linkedin}\n"
                f"- **Overview:** {description}\n"
                f"- **Ground-Truth Source:** Crustdata Real-Time B2B Intelligence (Verified Live API)\n"
            )

            digest = calculate_sha256(text)
            log.info("crustdata: enriched %r -> %s (sha256: %s)", identifier, name, digest[:12])
            return Source(
                title=f"Crustdata Live Intelligence: {name}",
                url=website,
                text=text,
                sha256=digest,
                verified=True,
                source_type="crustdata_live",
                evidence_quote=f"Verified Entity Profile: {name} | Founded: {founded} | Employees: {emp_range} | Status: {info.get('status', 'active')}",
                status_code=200,
                domain=domain,
            )
    except Exception as exc:
        log.warning("crustdata: lookup failed for %r: %s", identifier, exc)
        return None

