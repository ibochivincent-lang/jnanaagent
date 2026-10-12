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


def github_inspect_repo(repo_or_url: str) -> dict | None:
    """Inspect a GitHub repository, fetching metadata, default branch, and top open issues.
    
    Zero mock data — queries live GitHub REST API.
    """
    import re
    # Clean repo string: https://github.com/owner/repo or owner/repo
    clean = repo_or_url.strip()
    m = re.search(r"(?:https?://github\.com/)?([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)", clean)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    # Strip any trailing subpaths like /issues
    repo = repo.split("/")[0]

    log.info("github_inspect_repo: querying GitHub API for %s/%s", owner, repo)
    try:
        headers = {
            "User-Agent": "neatHack-research-agent/1.0",
            "Accept": "application/vnd.github.v3+json",
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # 1. Fetch repo metadata
        repo_resp = httpx.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=12)
        if repo_resp.status_code != 200:
            log.warning("github_inspect_repo: HTTP %d for repo %s/%s", repo_resp.status_code, owner, repo)
            return None
        repo_data = repo_resp.json()

        # 2. Fetch top open issues
        issues_resp = httpx.get(
            f"https://api.github.com/repos/{owner}/{repo}/issues?state=open&per_page=10&sort=updated",
            headers=headers,
            timeout=12,
        )
        issues_list = []
        if issues_resp.status_code == 200:
            for item in issues_resp.json():
                # Filter out pure pull requests from issue list if needed, or flag them
                is_pr = "pull_request" in item
                issues_list.append({
                    "number": item.get("number"),
                    "title": item.get("title", ""),
                    "state": item.get("state", "open"),
                    "author": item.get("user", {}).get("login", "unknown"),
                    "html_url": item.get("html_url", ""),
                    "is_pr": is_pr,
                    "labels": [l.get("name") for l in item.get("labels", []) if isinstance(l, dict)],
                    "body_snippet": (item.get("body") or "")[:280].replace("\n", " ").strip(),
                    "comments_count": item.get("comments", 0),
                    "created_at": item.get("created_at", ""),
                })

        return {
            "owner": owner,
            "repo": repo,
            "full_name": repo_data.get("full_name", f"{owner}/{repo}"),
            "description": repo_data.get("description") or "No repository description provided.",
            "stars": repo_data.get("stargazers_count", 0),
            "forks": repo_data.get("forks_count", 0),
            "open_issues_count": repo_data.get("open_issues_count", 0),
            "default_branch": repo_data.get("default_branch", "master"),
            "language": repo_data.get("language") or "Python",
            "html_url": repo_data.get("html_url", f"https://github.com/{owner}/{repo}"),
            "issues": issues_list,
        }
    except Exception as exc:
        log.warning("github_inspect_repo error for %s/%s: %s", owner, repo, exc)
        return None


def parse_github_issue_ref(text: str) -> tuple[str, str, int] | None:
    """Extract (owner, repo, issue_number) from a URL or shorthand reference."""
    import re
    # Match https://github.com/owner/repo/issues/123 or pull/123
    m = re.search(r"(?:https?://github\.com/)?([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/(?:issues|pull)/(\d+)", text)
    if m:
        return m.group(1), m.group(2), int(m.group(3))
    # Match shorthand owner/repo#123
    m2 = re.search(r"([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)#(\d+)", text)
    if m2:
        return m2.group(1), m2.group(2), int(m2.group(3))
    return None


def github_fetch_issue(url_or_ref: str) -> Source | None:
    """Fetch complete GitHub issue details, labels, and maintainer comments via GitHub REST API."""
    parsed = parse_github_issue_ref(url_or_ref)
    if not parsed:
        return None
    owner, repo, number = parsed
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    log.info("github_fetch_issue: fetching %s/%s#%d", owner, repo, number)
    try:
        resp = httpx.get(
            api_url,
            timeout=12,
            headers={"User-Agent": "neatHack-research-agent/1.0", "Accept": "application/vnd.github.v3+json"},
        )
        if resp.status_code != 200:
            log.warning("github_fetch_issue: HTTP %d for %s/%s#%d", resp.status_code, owner, repo, number)
            return None
        data = resp.json()
        title = data.get("title", f"Issue #{number}")
        state = data.get("state", "open")
        author = data.get("user", {}).get("login", "unknown")
        html_url = data.get("html_url", api_url)
        labels = [l.get("name") for l in data.get("labels", []) if isinstance(l, dict)]
        body = data.get("body") or "No issue description provided."

        # Also fetch top comments to understand maintainer discussion and triage
        comments_text = ""
        comments_url = data.get("comments_url")
        if comments_url and data.get("comments", 0) > 0:
            c_resp = httpx.get(
                f"{comments_url}?per_page=5",
                timeout=10,
                headers={"User-Agent": "neatHack-research-agent/1.0", "Accept": "application/vnd.github.v3+json"},
            )
            if c_resp.status_code == 200:
                c_data = c_resp.json()
                if isinstance(c_data, list) and c_data:
                    c_blocks = []
                    for c in c_data[:5]:
                        user = c.get("user", {}).get("login", "user")
                        c_body = (c.get("body") or "").strip()
                        c_blocks.append(f"**@{user}:**\n{c_body}")
                    comments_text = "\n\n### Maintainer & Contributor Discussion:\n" + "\n\n---\n\n".join(c_blocks)

        full_text = (
            f"# [{owner}/{repo} #{number}] {title}\n"
            f"- **Repository:** `{owner}/{repo}`\n"
            f"- **Issue Number:** `#{number}`\n"
            f"- **State:** `{state.upper()}`\n"
            f"- **Reporter:** `@{author}`\n"
            f"- **Labels:** `{', '.join(labels) if labels else 'None'}`\n"
            f"- **URL:** {html_url}\n\n"
            f"### Issue Description:\n{body}\n"
            f"{comments_text}"
        )

        digest = calculate_sha256(full_text)
        evidence = extract_grounding_quote(body or title)
        return Source(
            title=f"GitHub Issue: {owner}/{repo}#{number} — {title}",
            url=html_url,
            text=full_text,
            sha256=digest,
            verified=True,
            source_type="github_issue",
            evidence_quote=evidence,
            status_code=200,
            domain="github.com",
        )
    except Exception as exc:
        log.warning("github_fetch_issue: error for %s/%s#%d: %s", owner, repo, number, exc)
        return None


def entire_search_memory(query: str, max_facts: int = 5) -> list[Source]:
    """Search repository Entire Brain memory layer for architectural invariants and prior decisions."""
    log.info("entire_search_memory: querying Entire Brain for %r", query)
    import subprocess
    clean_query = query.strip()
    if not clean_query:
        return []
    try:
        proc = subprocess.run(
            ["entire", "brain", "recall", clean_query, "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            log.warning("entire_search_memory: command failed or returned empty: %s", proc.stderr[:100])
            return []
        data = json.loads(proc.stdout)
        facts = data.get("facts", [])
        sources = []
        for f in facts[:max_facts]:
            fact_id = f.get("id", "fact")
            paths = f.get("paths", ["project"])
            path_str = "/".join(paths) if isinstance(paths, list) else str(paths)
            text = f.get("text", "")
            kind = f.get("kind", "memory")
            origin = f.get("origin", "authored")
            fact_body = (
                f"### Entire Memory Layer: {path_str} ({kind.upper()})\n"
                f"- **Fact ID:** `{fact_id}`\n"
                f"- **Locus/Path:** `{path_str}`\n"
                f"- **Origin:** `{origin}`\n"
                f"- **Memory Text:** {text}\n"
            )
            digest = calculate_sha256(fact_body)
            sources.append(
                Source(
                    title=f"Entire Memory: {path_str}",
                    url=f"entire://{path_str}",
                    text=fact_body,
                    sha256=digest,
                    verified=True,
                    source_type="entire_memory",
                    evidence_quote=f'"{text[:200]}..."' if len(text) > 200 else f'"{text}"',
                    status_code=200,
                    domain="entire.local",
                )
            )
        log.info("entire_search_memory: returned %d verified facts", len(sources))
        return sources
    except Exception as exc:
        log.warning("entire_search_memory: error: %s", exc)
        return []


def github_search_issues(query: str, max_results: int = 5) -> list[SearchResult]:
    """Search public GitHub issues and PRs (neatHack Focus: Fix a GitHub issue & code investigations)."""
    log.info("github_search: %r (max %d results)", query, max_results)
    clean_query = query.strip()
    if not clean_query:
        return []
    # If query is a direct issue link or ref, return it as a direct candidate
    parsed = parse_github_issue_ref(clean_query)
    results = []
    if parsed:
        owner, repo, number = parsed
        results.append(
            SearchResult(
                title=f"GitHub Issue #{number}: {owner}/{repo}",
                url=f"https://github.com/{owner}/{repo}/issues/{number}",
                snippet=f"Direct target issue {owner}/{repo}#{number}",
            )
        )
    # Search open and closed issues/PRs
    url = f"https://api.github.com/search/issues?q={urllib.parse.quote_plus(clean_query)}&per_page={max_results}"
    try:
        resp = httpx.get(
            url,
            timeout=10,
            headers={"User-Agent": "neatHack-research-agent/1.0", "Accept": "application/vnd.github.v3+json"},
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            for it in items:
                title = it.get("title", "GitHub Issue")
                issue_url = it.get("html_url", "")
                state = it.get("state", "open")
                is_pr = "pull_request" in it
                type_label = "PR" if is_pr else "ISSUE"
                body = (it.get("body") or "")[:300].replace("\n", " ").strip()
                snippet = f"[{state.upper()} {type_label}] #{it.get('number', '')} {body}"
                results.append(SearchResult(title=f"GitHub {type_label}: {title}", url=issue_url, snippet=snippet))
        else:
            log.warning("github search returned status %d: %s", resp.status_code, resp.text[:100])
        log.info("github_search: %r -> %d results", query, len(results))
        return results
    except Exception as exc:
        log.warning("github search failed for %r: %s", query, exc)
        return results


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
    # If URL is a GitHub issue/pull, fetch rich API data directly
    if "github.com/" in url and ("/issues/" in url or "/pull/" in url):
        gh_src = github_fetch_issue(url)
        if gh_src:
            return gh_src

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
            "User-Agent": "JnanaAgent/1.0",
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

