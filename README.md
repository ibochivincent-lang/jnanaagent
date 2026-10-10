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

### 4. Running the Agent (Web Console or CLI)

#### Option A: Interactive Web Console (Recommended for Demos)
Launch the modern glassmorphic web dashboard:
```bash
python -m research_agent.server --port 8000
```
Then open [http://localhost:8000](http://localhost:8000) in your browser to experience:
- Real-time Server-Sent Events (SSE) streaming pipeline progress.
- Live Crustdata B2B intelligence cards and company profiling.
- Proof of Search cryptographic SHA-256 provenance ledger table.
- Direct links to Neatlogs trace visualizations and Entire continuous memory.

#### Option B: Terminal CLI Execution
Run an interactive cited research session with Human-In-The-Loop (HITL) approval:
```bash
python -m research_agent "Stripe and OpenAI collaboration in financial AI"
```
Or run autonomously with `--auto`:
```bash
python -m research_agent "Stripe and OpenAI collaboration in financial AI" --auto
```

Every execution produces:
- A cited markdown report with verified inline brackets (`reports/`)
- Live Crustdata B2B entity enrichment (Zero Mock Data)
- An immutable **Proof of Search: Cryptographic Provenance Audit** with SHA-256 source checksums
- Live token and span telemetry streaming to your Neatlogs dashboard at [app.neatlogs.com](https://app.neatlogs.com)

---

## 🧠 Continuous Memory & Code Intelligence with Entire (Graph & Brain)
Proof of Search AI is instrumented with the **Entire CLI v0.11.4**, **entire-graph**, and **entire-brain**:
- **Entire Repository Index**: [https://entire.io/gh/ibochivincent-lang/proof-of-search-ai](https://entire.io/gh/ibochivincent-lang/proof-of-search-ai)
- **Check Agent Health**: `entire doctor` and `entire status`
- **Agent Blame**: `entire blame src/research_agent/nodes.py` (tracks AI vs human line provenance)
- **Repo Memory Retrieval**: `entire brain recall "mock data"` and `entire brain brief "add web dashboard"`
- **Durable Invariants**: Core project invariants recorded to Entire Brain memory layer (`constraints.data.rules`, `architecture.llm.provider`, `architecture.observability.tracing`).

---

## 📊 Telemetry Architecture with Neatlogs
- **Endpoint**: `https://ingest.neatlogs.com`
- **Workflow Name**: `research-agent`
- **Integration**: `neatlogs.langchain_handler()` attached to graph invocations (`app.invoke(..., config={"callbacks": [handler]})`).
- **Flush Guarantee**: `neatlogs.flush()` and `neatlogs.shutdown()` called inside `finally:` block of `cli.py`.

---

## ☁️ Deployment: Live AWS Cloud & Docker

### 🌐 Live Production Cloud Deployment (neatHack AWS Credits)
- **Live Public URL**: **[http://34.227.107.171:8000](http://34.227.107.171:8000)**
- **Cloud Provider**: Amazon Web Services (AWS)
- **Region**: `us-east-1` (US East, N. Virginia)
- **Instance ID**: `i-0442ddfa2604f5923` (`t2.micro`, Ubuntu 24.04 LTS)
- **Status Endpoint**: [http://34.227.107.171:8000/api/status](http://34.227.107.171:8000/api/status) (HTTP 200 OK — all sponsor integrations online)
- **System Service**: Managed by `systemd` (`proofsearch.service`) running 24/7 with automatic restart and crash recovery.

### Option 1: Docker / Docker Compose
Run with a single command:
```bash
docker-compose up --build -d
```
Then access `http://localhost:8000`.

### Option 2: AWS EC2 (Automated Cloud Launch via User Data)
1. In the AWS Management Console (`us-east-1` N. Virginia or preferred region), navigate to **EC2** → **Launch Instance**.
2. Select **Ubuntu 24.04 LTS** (`t2.micro` or `t3.micro`).
3. In **Network Settings**, allow Custom TCP port `8000` (and `80`/`22`).
4. Under **Advanced Details** → **User data**, paste the contents of [`deploy/ec2-userdata.sh`](deploy/ec2-userdata.sh).
5. Click **Launch Instance**. The automated userdata bootstrap installs Python, dependencies, clones the repo, and launches the service in ~90 seconds!
6. If connecting via **EC2 Instance Connect** in the AWS console:
   - User name: `ubuntu`
   - Click orange **Connect** button (no key pair required in browser).
   - Check status: `sudo systemctl status proofsearch`

---

## 🏆 neatHack 2026 Submission
- **Team**: Vincci001 (Leader: Ibochi Vincent)
- **Repository**: [https://github.com/ibochivincent-lang/proof-of-search-ai](https://github.com/ibochivincent-lang/proof-of-search-ai)
- **Build Log**: [hackathon.md](hackathon.md)
