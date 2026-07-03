# Capstone Project  
# Retail Policy Intelligence & Decision Support System  
*(SLO-Bound Autonomous Agentic AI System)*

---

## 📌 Problem Statement

A large global enterprise operates across multiple countries and must comply with complex regulatory frameworks, internal policies, supplier agreements, labor laws, anti-corruption statutes, and data protection regulations.

The Global Policy & Compliance Office receives approximately:

- ~2,000–3,000 policy-related queries per month  
- 30–40% related to data protection & retention  
- 20–30% related to supplier/vendor compliance  
- 10–15% cross-border or jurisdiction-specific queries (high risk)  
- 10–15% anti-corruption and ethics-related concerns (high risk)  
- Remaining queries across labor law, contractual obligations, and operational governance  

These queries require interpreting lengthy policy documents, structured compliance records, and cross-referenced regulations.

Manual interpretation is slow, inconsistent, and expensive. Misinterpretation can result in:

- Regulatory penalties  
- Legal exposure  
- Audit failures  
- Reputational damage  
- Operational delays  

Existing enterprise systems lack intelligent reasoning, structured routing, audit traceability, and measurable performance guarantees.

---

## 🌍 Current Situation

### Current Manual Process

1. Query received via email or internal portal  
2. Compliance officer manually searches policy repositories  
3. Cross-references structured compliance databases  
4. Drafts response with citations  
5. Escalates high-risk queries to legal counsel  

Average resolution time: 24–72 hours  
High-risk cases: Multiple-day review cycles  

---

## 💰 The Cost of the Problem

### Direct Costs
- Compliance team effort hours  
- Legal review escalation costs  
- Audit remediation expenses  

### Indirect Costs
- Delayed operational decisions  
- Vendor onboarding slowdowns  
- Risk of regulatory fines  
- Reduced trust in internal compliance systems  

---

## ❗ Why Current Systems Fail

### Pattern Analysis of Monthly Queries

- 60% require interpretation of unstructured policy text  
- 30% require deterministic structured database lookups  
- 10% require hybrid reasoning (policy + structured validation)  

### Key Inefficiencies

- Static keyword search (no contextual reasoning)  
- No intelligent routing between RAG and SQL  
- No structured confidence scoring  
- Limited audit traceability  
- No SLO-based reliability guarantees  
- No automated escalation triggers  

---

## 🎯 Project Goal

Build a Production-Grade Autonomous Agentic AI System that:

- Answers policy and compliance queries conversationally  
- Intelligently routes queries to RAG, SQL, or hybrid workflows  
- Uses multi-agent validation for high-risk scenarios  
- Provides source attribution and confidence scoring  
- Logs all decisions for auditability  
- Escalates high-risk or low-confidence cases  
- Meets clearly defined Service Level Objectives (SLOs)  

---

## 🧠 Core Requirements

### 1️⃣ Intelligent Query Handling

The system must:

- Understand user intent
- Classify risk level (Low / Medium / High)
- Detect need for structured lookup vs policy interpretation
- Maintain multi-turn context
- Enforce role-based access control

---

### 2️⃣ Intelligent Query Routing

Route dynamically to:

- **RAG** → Policy explanation, clause interpretation, summaries  
- **SQL** → Compliance records, approval status, audit logs  
- **Hybrid** → Interpretation + structured validation  
- **Multi-Agent Flow** → High-risk validation workflows  

---

### 3️⃣ Multi-Agent Orchestration

Minimum required agents:

- Intent Classification Agent  
- Retrieval Agent  
- Compliance Validation Agent  
- Risk Assessment Agent  
- Escalation Manager Agent  

Agents must operate in a Plan–Reason–Act workflow with reflection/self-correction.

---

### 4️⃣ Source Attribution & Trust

Every response must include:

- Cited document references  
- Structured validation outputs (if SQL involved)  
- Confidence score  
- Risk classification  
- Clear uncertainty disclosure  

---

### 5️⃣ Human Escalation

The system must escalate when:

- Confidence score < threshold  
- Risk level = High  
- Ambiguous or conflicting information detected  
- Explicit request for legal validation  

Escalation must include full context transfer:
- Conversation history  
- Retrieved documents  
- Structured validation results  
- Agent reasoning trace  

---

## 📊 Success Criteria (Measurable Outcomes)

The system must meet defined SLOs:

- **Task Success Rate (TSR)** ≥ 90%  
- **P95 Latency** ≤ defined threshold (e.g., 3–6 seconds)  
- **Zero PII leakage**  
- Structured SQL correctness ≥ 95%  
- High-risk misclassification rate < 5%  
- Controlled cost per query within defined budget  

---

## ⚙️ Technical Scope

### System Layers

1. API Layer (FastAPI, authentication, validation)
2. Agent Orchestration Layer (LangGraph/CrewAI)
3. Retrieval & Knowledge Layer (RAG + SQL)
4. External Tools Layer (MCP integrations)
5. Evaluation & Observability Layer (Langfuse, metrics, tracing)
6. Human-in-the-Loop Layer (Escalation + audit logs)

---

## 📚 Sample Dataset Guidance

Learners may use:

- Public GDPR excerpts  
- ISO policy summaries  
- Open compliance frameworks  
- Synthetic vendor compliance records  
- Synthetic audit logs  
- Public regulatory documentation  

No proprietary or confidential corporate documents should be used.

Structured Tables Included:
- `vendors`
- `audit_logs`
- `retention_records`
- `compliance_reviews`

---

## High-Risk Scenario Examples (Mandatory Multi-Agent Validation Cases)

The system must correctly detect, route, and escalate the following high-risk scenarios:
- Cross-border data transfer involving restricted jurisdictions
- Deletion request for records under active legal hold
- Approval override for a Critical-risk vendor
- Hospitality or gift approval involving overseas suppliers
- Audit findings overdue beyond target resolution date
- Conflicting policy clauses across departments
- Vendor onboarding with unresolved compliance findings
- High-severity issue marked “Closed” without resolution evidence

These scenarios must trigger:
- Risk re-evaluation
- Multi-agent validation workflow
- Confidence recalculation
- Escalation to human review when required

## 📦 Deliverables

1. Architecture Diagram  
2. Agent Workflow Diagram  
3. RAG + SQL Integration  
4. Multi-Agent Orchestration  
5. SLO Definition & Evaluation Report  
6. Observability Dashboard Evidence  
7. Escalation Workflow Implementation  
8. 4–6 Minute Live Demo  
9. Deployment & Runbook Documentation  

---

## ⚠️ Important Note

This system is intended to assist policy and compliance teams by providing explainable insights and structured retrieval. It does not replace legal or regulatory professionals. High-risk or ambiguous queries must trigger human review workflows.

---

## 🚀 Capstone Outcome

By completing this project, learners will demonstrate the ability to:

- Engineer a production-grade agentic AI system  
- Implement intelligent query routing across multiple data sources  
- Build stateful multi-agent orchestration workflows  
- Enforce guardrails and measurable SLOs  
- Deliver an enterprise-ready AI system with auditability, reliability, and human oversight  

---

## 🧪 Evaluation Criteria

The system will be evaluated on:

- Architectural quality  
- Multi-agent orchestration depth  
- Retrieval performance  
- Structured data correctness  
- Guardrail effectiveness  
- SLO compliance  
- Human handoff design  
- Code modularity  
- Documentation clarity  

---

## 🚀 Getting Started

1. Set up PostgreSQL with pgvector  
2. Create structured policy database schema  
3. Ingest enterprise documents  
4. Implement RAG pipeline  
5. Add SQL integration  
6. Implement query routing  
7. Add agent orchestration  
8. Integrate guardrails  
9. Define and measure SLOs  
10. Implement escalation workflows  
11. Deploy and test end-to-end  

---