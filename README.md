# Proof of Search AI (ProofSearch AI)

[![Hackathon](https://img.shields.io/badge/neatHack-2026-blue.svg)](https://neatlogs.com)
[![Tracing](https://img.shields.io/badge/Telemetry-Neatlogs%20v1.4.26-6366f1.svg)](https://app.neatlogs.com)
[![Orchestration](https://img.shields.io/badge/Agent-LangGraph-brightgreen.svg)](https://github.com/langchain-ai/langgraph)
[![Continuous Memory](https://img.shields.io/badge/Provenance-Entire%20Checkpoints-orange.svg)](https://entire.io)
[![Live Data](https://img.shields.io/badge/Data-Crustdata%20Live%20API-emerald.svg)](https://crustdata.com)

**Proof of Search AI** is a verifiable, hallucination-resistant research agent pipeline engineered for **neatHack 2026**. It tackles the critical problem of unverified citations, fabricated data, and opaque reasoning in AI agents by delivering end-to-end execution observability via **Neatlogs**, verifiable continuous session memory via **Entire**, live B2B/market ground truth via **Crustdata**, and sustainable per-query unit economics modeled on **cfo.ai**.

---

## 🌟 Key Architecture & Capabilities

1. **Deterministic HITL Research Flow (LangGraph)**:
   - Topic ingestion -> Plan proposal with complementary search angles.
   - Human-in-the-loop (HITL) terminal gate for approval/revision prior to search execution.
   - Autonomous multi-query retrieval, source selection, full-text extraction, and synthesis.
2. **Deep Observability (Neatlogs)**:
   - Native `neatlogs.langchain_handler()` captures graph execution, node transitions, token usage, latency, and LLM calls.
   - Regional ingestion via `https://ingest.neatlogs.com`.
   - Automatic buffered span flush and clean shutdown on one-shot process exits.
3. **Live Entity & Market Intelligence (Crustdata)**:
   - Ground truth company data, verified executives, funding history, and real-time signals with zero mock records.
4. **Verifiable Agent Memory & History (Entire)**:
   - Granular session checkpoints capturing code evolution, agent decisions, and execution artifacts.
5. **Unit Economics & Sustainability (cfo.ai)**:
   - Granular cost modeling across LLM generation, search API lookups, and pricing tiers.

---

## 🛠️ Quickstart & Setup

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Installation
```bash
git clone https://github.com/ibochivincent-lang/proof-of-search-ai.git
cd proof-of-search-ai
pip install -e .
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

Ensure your `.env` contains:
```ini
# LLM Provider Configuration (Option A: neatHack sponsored LiteLLM, Option B: Anthropic)
LITELLM_API_KEY=sk-G2C...
LITELLM_BASE_URL=https://litellm.vision.aivar.app/v1
# ANTHROPIC_API_KEY=sk-ant-...

# Required for tracing: Neatlogs Project API key (Project ID: 72082073-0485-4b6b-abb0-2a1ce5116f2b)
NEATLOGS_API_KEY=g0mx_xH8a6btCYnVOH0wGk4mkzaqz1jS

# Crustdata Live B2B & Entity Intelligence (neatHack Sponsor Credits)
CRUSTDATA_API_KEY=cd_a6070a6b539f8eb3f46c1e9acdf19ab78ef6
```

### 4. Running the Agent
Run an interactive cited research session with Human-In-The-Loop (HITL) approval:
```bash
python -m research_agent "Stripe and OpenAI collaboration in financial AI"
```
Or skip the terminal HITL gate with `--auto`:
```bash
python -m research_agent "Stripe and OpenAI collaboration in financial AI" --auto
```

Every execution produces:
- A cited markdown report with verified inline brackets (`reports/`)
- Live Crustdata B2B entity enrichment (Zero Mock Data)
- An immutable **Proof of Search: Cryptographic Provenance Audit** with SHA-256 source checksums
- Live token and span telemetry streaming to your Neatlogs dashboard at [app.neatlogs.com](https://app.neatlogs.com)

---

## 📊 Telemetry Architecture with Neatlogs
- **Endpoint**: `https://ingest.neatlogs.com`
- **Workflow Name**: `research-agent`
- **Integration**: `neatlogs.langchain_handler()` attached to graph invocations (`app.invoke(..., config={"callbacks": [handler]})`).
- **Flush Guarantee**: `neatlogs.flush()` and `neatlogs.shutdown()` called inside `finally:` block of `cli.py`.

---

## 🏆 neatHack 2026 Submission
- **Team**: Vincci001 (Leader: Ibochi Vincent)
- **Repository**: [https://github.com/ibochivincent-lang/proof-of-search-ai](https://github.com/ibochivincent-lang/proof-of-search-ai)
- **Build Log**: [hackathon.md](hackathon.md)
