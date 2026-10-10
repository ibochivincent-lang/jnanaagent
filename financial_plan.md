# Proof of Search AI (ProofSearch AI) — Financial Model & Unit Economics
*Prepared for cfo.ai business planning and neatHack 2026 submission*

---

## 1. Executive Summary & Company Profile
- **Company / Product:** Proof of Search AI (ProofSearch AI)
- **Team:** Vincci001 (Lead: Ibochi Vincent)
- **Website / Repository:** [https://github.com/ibochivincent-lang/proof-of-search-ai](https://github.com/ibochivincent-lang/proof-of-search-ai)
- **Core Value Proposition:** Autonomous, verifiable research agent pipeline that guarantees zero hallucinations and zero mock data through cryptographic SHA-256 source hashing, real-time Crustdata B2B entity enrichment, and complete Neatlogs execution observability.
- **Target Audience:** VC/PE investment associates, corporate development analysts, competitive intelligence professionals, and due diligence compliance teams.

---

## 2. Pricing & Revenue Model

| Tier | Monthly Price | Included Monthly Reports | Overage Cost / Report | Key Features |
| :--- | :--- | :--- | :--- | :--- |
| **Pay-As-You-Go** | $0 / mo | 0 | $2.50 | On-demand research queries, SHA-256 audit, Neatlogs trace link |
| **Pro Analyst** | $49 / mo | 30 reports | $1.50 | Claude Sonnet reasoning, 10 Crustdata live entity lookups/mo, markdown & PDF export |
| **Team / Enterprise** | $499 / mo | 500 reports | $0.95 | Unlimited Crustdata enrichment, multi-seat Entire session memory, custom webhooks, audit compliance logs |

---

## 3. Unit Economics Breakdown (Per Report)

Every single research report runs through a multi-node LangGraph execution: planning, multi-query web search, page fetching, live Crustdata B2B entity enrichment, and citation synthesis.

### Cost of Goods Sold (COGS) Analysis:
- **LLM Token Ingestion & Generation:**
  - Planning + Source Selection + Report Synthesis: ~2,800 prompt tokens + ~1,900 completion tokens = ~4,700 tokens total.
  - Blended model cost (Claude Haiku / Sonnet via LiteLLM): **$0.0042**
- **Data Enrichment & Ingestion (Crustdata API):**
  - Live B2B company profile enrichment (headcount, founding year, funding, headquarters): **$0.0500**
- **Compute & Networking Infrastructure (AWS Lambda / ECS):**
  - Average agent execution runtime (40 seconds @ 512MB RAM): **$0.0007**
- **Observability & Storage (Neatlogs & S3 Provenance Hash Store):**
  - Span telemetry streaming + immutable hash archive: **$0.0011**
- **Total COGS Per Report:** **$0.0560 (~5.6 cents)**

### Margin Calculations:
- **Pay-as-you-go Gross Margin:**
  $$\text{Margin} = \frac{\$2.50 - \$0.056}{\$2.50} \times 100\% = \mathbf{97.7\%}$$
- **Pro Tier Blended Gross Margin ($49 for 30 reports = $1.63/report):**
  $$\text{Margin} = \frac{\$1.63 - \$0.056}{\$1.63} \times 100\% = \mathbf{96.5\%}$$

---

## 4. 12-Month Pro-Forma Financial Projections

| Metric | Month 1 (Launch) | Month 3 | Month 6 | Month 12 |
| :--- | :--- | :--- | :--- | :--- |
| **Pro Customers ($49/mo)** | 40 | 120 | 350 | 1,200 |
| **Enterprise Teams ($499/mo)**| 2 | 8 | 25 | 80 |
| **Monthly Recurring Revenue (MRR)** | **$2,958** | **$9,872** | **$29,625** | **$98,720** |
| **Annual Run Rate (ARR)** | $35,496 | $118,464 | $355,500 | $1,184,640 |
| **COGS (Tokens, APIs, Compute)** | $125 | $420 | $1,280 | $4,250 |
| **Fixed Overhead (Host, Tooling, Domains)** | $150 | $300 | $750 | $2,000 |
| **Gross Profit** | **$2,833 (95.7%)** | **$9,452 (95.7%)** | **$28,345 (95.6%)** | **$94,470 (95.6%)** |
| **Net Operating Income** | **$2,683** | **$9,152** | **$27,595** | **$92,470** |

---

## 5. Runway & Capital Strategy
1. **Zero Cash-Burn Starting Point:** Built entirely during neatHack utilizing sponsor credits (Neatlogs free tier, Crustdata 5,000 credits, $20 LiteLLM allowance, Entire GitHub app).
2. **Break-Even:** Achieved at customer #3 (under 7 days post-launch).
3. **Reinvestment Strategy:**
   - 40% of net margin allocated to acquiring high-volume enterprise Crustdata data licenses.
   - 30% allocated to R&D for local verifiable ZK/SHA cryptographic provenance attestations.
   - 30% retained for operations and growth reserve.
