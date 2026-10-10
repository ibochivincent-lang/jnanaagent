# neatHack 2026: Proof of Search AI (ProofSearch AI)

## Project Overview
- **Name:** Proof of Search AI (ProofSearch AI)
- **Purpose:** A decentralized, verifiable agentic research engine that combines real-time deep web search, live B2B/people intelligence via Crustdata, verifiable cryptographic and source provenance (Proof of Search), and full execution telemetry via Neatlogs, Continuous Memory with Entire, and economic unit sustainability modeled in cfo.ai.
- **Problem Solved:** LLM research agents hallucinate sources, fabricate statistics, and cannot prove whether information was actually retrieved from ground truth or invented. Enterprise and intelligence research requires verifiable audit trails, real-time live data with zero mock records, transparent cost/token economics, and observable agent traces.

---

## Team Information
- **Team Name:** Vincci001
- **Team Leader:** Ibochi Vincent
- **Hackathon:** neatHack 2026 (Oct 10–11, 2026)

---

## Technology Stack & Core Integrations
| Pillar | Tool / Platform | Role in Project | Verification Status |
| :--- | :--- | :--- | :--- |
| **Observability & Tracing** | **Neatlogs** | Telemetry, span logging, LLM token metrics, trace dashboard | SDK v1.4.26 Installed & Graph Callback Handler Hooked |
| **Continuous Memory & Versioning** | **Entire** | CLI session capture, Checkpoints, Entire Graph & Brain | Pending CLI init & first checkpoint |
| **Unit Economics & Financial Plan** | **cfo.ai** | Agent pricing, per-query cost modeling, revenue, runway plan | Financial modeling in progress |
| **Live B2B & Executive Data** | **Crustdata** | Live company & people search intelligence (Zero Mock Data) | Promo code `NEATLOGS-OCT2026` ready |
| **Agent Core Orchestration** | **LangGraph / Python** | StateGraph, interrupt-based HITL gate, citation synthesis | Initialized in workspace |

---

## Build Log

### [2026-10-10] Workspace Initialization & Hackathon Briefing
- **Actions:**
  - Initialized isolated Git workspace at `C:\Users\User\.gemini\antigravity-ide\scratch\proof-of-search-ai`.
  - Configured project `.gitignore` and `README.md`.
  - Ingested neatHack setup guidelines, sponsor integrations (Neatlogs, Entire, cfo.ai, Crustdata), and installed official `neathack` build companion skill.
  - Formatted initial `hackathon.md` tracking log.
- **Status:** Initialized. Ready for API keys, Crustdata live integration, and Entire CLI checkpointing.

### [2026-10-10] Neatlogs Observability Instrumentation
- **Actions:**
  - Installed latest `neatlogs` SDK (v1.4.26) via pip.
  - Configured Neatlogs access with project ID `72082073-0485-4b6b-abb0-2a1ce5116f2b` and documented `NEATLOGS_API_KEY` in `.env.example` and local `.env`.
  - Added native LangGraph callback integration (`neatlogs.langchain_handler()`) to the graph invocation in `src/research_agent/cli.py`.
  - Added automatic SDK initialization with regional endpoint `https://ingest.neatlogs.com` and workflow name `research-agent`.
  - Implemented one-shot process lifecycle flush (`neatlogs.flush()`) and shutdown (`neatlogs.shutdown()`) in a `finally` block.
- **Status:** Complete. Ready for probe verification and live tracing.

---

## Demo
- **Status:** In development
- **CLI / Web URL:** TBD
- **Reproduction Instructions:** TBD

---

## Known Limitations & Next Steps
1. **Prerequisite Inputs Needed:**
   - Neatlogs Project API Key (from `app.neatlogs.com` -> Settings -> API Keys).
   - Entire CLI installation and repo authorization.
   - cfo.ai business plan generation.
   - Crustdata API key using promo code `NEATLOGS-OCT2026`.
2. **Next Steps:**
   - Install `neatlogs`, `crustdata` SDK / API clients, and verify with synthetic probe.
   - Structure live agent graph combining web and Crustdata entity intelligence.
   - Capture initial Entire checkpoint (`entire checkpoint explain HEAD`).

---

## Submission Checklist
- [x] Project name & problem description
- [ ] neatlogs integrated with verified trace links in dashboard
- [ ] Entire connected with accessible checkpoint link & ID
- [ ] cfo.ai business plan & unit economics report attached
- [ ] Crustdata live intelligence integration functioning (zero mock data)
- [ ] Demo video & working reproduction commands
