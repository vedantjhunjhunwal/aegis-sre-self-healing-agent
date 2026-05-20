
AegisSRE — Self-Healing Multi-Agent DevOps Reliability Engineer

> An AI-powered SRE system that detects production incidents, investigates the root cause, patches the code, validates the fix, audits the change, and generates a pull request for human approval.

What is AegisSRE?

AegisSRE is a **self-healing multi-agent DevOps/SRE platform**.

In simple words:

Imagine a website or app suddenly becomes slow in production.

Normally, an engineer has to:

1. Check monitoring alerts.
2. Read logs.
3. Inspect metrics.
4. Look at traces.
5. Find the broken code.
6. Write a fix.
7. Run tests.
8. Verify the fix.
9. Open a pull request.
10. Ask another engineer to review it.

AegisSRE automates this entire workflow using AI agents.

It acts like an autonomous engineering teammate that can:

- Detect a production issue.
- Understand what went wrong.
- Search the codebase.
- Identify the faulty function.
- Apply a code fix.
- Run tests.
- Validate the system behavior.
- Perform a Red Team audit.
- Create a GitHub PR or local PR artifact.
- Wait for human approval before merge.

This project is designed as a **Google L4-level AI Agent + Distributed Systems project**, combining AI agents, DevOps, observability, Kubernetes-style validation, graph search, vector search, workflow orchestration, and human-in-the-loop governance.

---

## Why This Project Matters

Modern production systems are complex.

A small bug can cause:

- Latency spikes
- API failures
- Retry storms
- Memory leaks
- Cascading failures
- Bad customer experience
- On-call incidents

Traditional AI projects only generate text or code.

AegisSRE goes further.

It connects AI agents with real engineering systems:

- Observability
- Code search
- Testing
- Security checks
- Pull request automation
- Infrastructure workflows

This makes it closer to how real production engineering teams work at companies like Google, Amazon, Meta, Netflix, and other large-scale technology companies.

---

## Core Idea

```text
Production Incident
      ↓
AI SRE Observer
      ↓
Root-Cause Analyst Agent
      ↓
Software Engineer Agent
      ↓
Sandbox Testing
      ↓
Kubernetes-style Integration Validation
      ↓
Red Team Audit
      ↓
GitHub PR / Local PR Artifact
      ↓
Human Approval
````

AegisSRE does not blindly generate code.

It follows a structured, evidence-based workflow:

1. Observe the incident.
2. Collect metrics, logs, pod state, and traces.
3. Search the codebase using vector search and code graph analysis.
4. Identify the root cause.
5. Patch the code.
6. Run tests.
7. Validate system behavior.
8. Audit the patch.
9. Generate a PR for review.

---

## Architecture

```text
Production K8s / Simulated Service
        |
        v
Kafka Event Bus
        |
        v
Temporal / LangGraph Orchestrator
        |
        v
MCP Observability Bridge
Prometheus + Logs + Kubernetes Pod State + Traces
        |
        v
Root-Cause Analyst Agent
Qdrant Vector Search + Neo4j Code Graph
        |
        v
Software Engineer Agent
Code Patch Generation
        |
        v
Sandbox Test Runner
pytest / local verification
        |
        v
kind / minikube Integration Validation
Kubernetes-style environment check
        |
        v
Red Team Verification Agent
Security + test integrity + regression audit
        |
        v
GitHub PR Agent
Real PR or local PR markdown artifact
        |
        v
Human-in-the-Loop Dashboard
```

---

## Technical Stack

| Area                  | Technology                 |
| --------------------- | -------------------------- |
| Agent Workflow        | LangGraph                  |
| Agent Tools           | LangChain Tools            |
| API Backend           | FastAPI                    |
| Runtime               | Python                     |
| Event Bus             | Kafka                      |
| Workflow Infra        | Temporal                   |
| Vector Search         | Qdrant                     |
| Code Graph            | Neo4j                      |
| Observability         | Prometheus, Grafana        |
| Kubernetes Validation | kind / minikube            |
| Testing               | pytest                     |
| GitHub Automation     | GitHub API / PyGithub      |
| Dashboard             | FastAPI HTML Control Plane |
| Local Execution       | Python virtual environment |
| Full Infra Execution  | Docker Compose             |

---

## What AegisSRE Fixes in the Demo

The demo service contains a production-style bug.

Inside the checkout service, the retry delay function is broken:

```python
def calculate_retry_delay(attempt):
    return 0
```

This means that when a payment gateway fails, the service retries immediately with no delay.

That can create:

* Retry amplification
* High latency
* Increased error rate
* More pressure on downstream services
* A production incident

AegisSRE detects this issue and patches it with bounded exponential backoff:

```python
def calculate_retry_delay(attempt):
    attempt = max(1, int(attempt))
    base_delay = 0.1
    max_delay = 2.0
    jitter = (attempt % 3) * 0.01
    return min(max_delay, base_delay * (2 ** (attempt - 1)) + jitter)
```

This reduces retry pressure and improves system stability.

---

## Project Features

### 1. Incident Detection

AegisSRE accepts a production-style alert such as:

```json
{
  "service": "checkout-api",
  "severity": "critical",
  "symptom": "p95 latency above 2s after payment gateway timeout",
  "metric": "http_request_duration_seconds_p95",
  "trace_id": "trace-checkout-123"
}
```

This simulates a real production alert from a monitoring system.

---

### 2. MCP Observability Bridge

The MCP-style observability bridge collects:

* Prometheus metrics
* Kubernetes pod status
* Recent logs
* Trace context
* Service health information

This helps the AI agent reason from real operational signals instead of guessing.

In local no-Docker mode, fallback observability data is used so the project can still run easily.

---

### 3. Root-Cause Analysis Agent

The Root-Cause Analyst Agent uses:

* Qdrant-style vector search
* Neo4j-style code graph
* Logs
* Metrics
* Trace evidence
* Function-level code search

It identifies the likely broken file and function.

Example RCA result:

```json
{
  "suspected_file": "payment_client.py",
  "suspected_function": "calculate_retry_delay",
  "root_cause": "The retry delay function returns zero, causing immediate retry amplification during payment gateway timeouts.",
  "confidence": 0.91
}
```

---

### 4. Software Engineer Agent

The Software Engineer Agent applies a real patch to the codebase.

It does not only describe the fix.

It modifies the actual file in the repair workspace.

---

### 5. Sandboxed Test Execution

After patching the code, AegisSRE runs:

```bash
pytest -q
```

The workflow only continues if the tests pass.

This makes the system verification-based instead of purely LLM-based.

---

### 6. Kubernetes-style Integration Validation

The project includes kind/minikube scripts for Kubernetes-style validation.

In full infrastructure mode, the patched service can be tested in a local Kubernetes environment.

In no-Docker local mode, AegisSRE uses safe fallback validation.

---

### 7. Red Team Verification Agent

Before a PR is created, a Red Team Agent audits the patch.

It checks:

* Did the agent modify test files unfairly?
* Did the patch still return zero delay?
* Did the patch introduce unsafe code?
* Did the patch use risky constructs like `eval`, `exec`, or shell execution?
* Did the patch actually implement bounded backoff?

This prevents the system from blindly trusting generated code.

---

### 8. GitHub PR Automation

AegisSRE can create:

* A real GitHub PR if GitHub credentials are configured.
* A local PR markdown artifact if GitHub credentials are not configured.

For safe local testing, it defaults to local PR artifact mode.

Generated PRs include:

* Incident summary
* Root cause
* Patch summary
* Test results
* Integration validation
* Red Team audit
* Human approval note

---

### 9. Human-in-the-Loop Dashboard

AegisSRE includes a browser dashboard where users can:

* Trigger a demo incident.
* Watch the agent workflow.
* Inspect workflow trace events.
* View the full run JSON.
* Confirm that the system reached human approval stage.

---

## How to Run Locally Without Docker

This is the easiest mode for development.

### Step 1: Clone the repository

```bash
git clone https://github.com/vedantjhunjhunwal/aegis-sre-self-healing-agent.git
cd aegis-sre-self-healing-agent
```

### Step 2: Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Create environment file

On Windows:

```powershell
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

### Step 5: Configure `.env` for local mode

Use this configuration:

```env
APP_HOST=127.0.0.1
APP_PORT=5000
ENV=dev

KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_ALERT_TOPIC=production-alerts

TEMPORAL_ADDRESS=temporal:7233
TEMPORAL_NAMESPACE=default

PROMETHEUS_URL=http://localhost:9090
JAEGER_URL=http://jaeger:16686
KUBECONFIG=

QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=aegis_code

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=aegis-password

GITHUB_TOKEN=
GITHUB_OWNER=
GITHUB_REPO=
GITHUB_BASE_BRANCH=main
GITHUB_CREATE_REAL_PR=false

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

WORKSPACE_DIR=workspace
MAX_REPAIR_ATTEMPTS=5
ENABLE_K8S_INTEGRATION=false
ENABLE_FIRECRACKER=false
```

### Step 6: Start the application

```bash
python apps.py
```

Open:

```text
http://127.0.0.1:5000
```

Click:

```text
Trigger Demo Incident
```

---

## What Works Without Docker?

In no-Docker local mode, these parts work:

* LangGraph workflow
* LangChain tools
* MCP fallback observability
* Root-cause analysis
* Local code patching
* pytest test execution
* Red Team audit
* Local PR artifact generation
* HITL dashboard

These parts require Docker or external services:

* Kafka
* Temporal server
* Qdrant server
* Neo4j server
* Prometheus
* Grafana
* kind/minikube Kubernetes validation

The system is designed with fallback behavior so it can still run locally without Docker.

---

## How to Run Full Infrastructure Mode With Docker

If Docker Desktop is installed, run:

```bash
cp .env.example .env
docker compose up --build
```

Then open:

```text
http://localhost:8080
```

Other infrastructure services:

| Service            | URL                                            |
| ------------------ | ---------------------------------------------- |
| AegisSRE Dashboard | [http://localhost:8080](http://localhost:8080) |
| Temporal UI        | [http://localhost:8233](http://localhost:8233) |
| Prometheus         | [http://localhost:9090](http://localhost:9090) |
| Grafana            | [http://localhost:3000](http://localhost:3000) |
| Neo4j Browser      | [http://localhost:7474](http://localhost:7474) |
| Qdrant             | [http://localhost:6333](http://localhost:6333) |

Default credentials:

```text
Neo4j: neo4j / aegis-password
Grafana: admin / admin
```

---

## GitHub PR Mode

By default, AegisSRE does not create a real GitHub PR.

It creates a local PR artifact inside:

```text
workspace/prs/
```

To enable real GitHub PR creation, edit `.env`:

```env
GITHUB_TOKEN=your_github_token
GITHUB_OWNER=your_github_username
GITHUB_REPO=your_repository_name
GITHUB_BASE_BRANCH=main
GITHUB_CREATE_REAL_PR=true
```

Then run:

```bash
python apps.py
```

When the workflow completes, it will attempt to create a real GitHub pull request.

---

## Example Workflow Output

After clicking **Trigger Demo Incident**, the dashboard will show events like:

```text
observe_alert → Incident accepted and workspace created
collect_context → MCP bridge collected metrics, logs, pods, and trace context
root_cause_analysis → RCA mapped incident to payment_client.py
engineer_patch → Patch applied
sandbox_unit_tests → Unit tests passed
integration_validate → Kubernetes/local validation passed
red_team_audit → Red Team audit approved
open_pr → GitHub PR/local PR artifact created
```

Final status:

```text
awaiting_human_approval
```

This means the AI system completed the repair workflow and is waiting for a human engineer to review the generated PR.

---

## Repository Structure

```text
aegis-sre-self-healing-agent/
│
├── apps.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── README.md
├── .env.example
│
├── apps/
│   ├── config.py
│   ├── dashboard/
│   │   └── server.py
│   ├── mcp_server/
│   │   └── bridge.py
│   └── orchestrator/
│       ├── langgraph_workflow.py
│       └── temporal_worker.py
│
├── agents/
│   └── langchain_tools.py
│
├── clients/
│   ├── github_client.py
│   ├── kafka_client.py
│   ├── neo4j_client.py
│   ├── prometheus_client.py
│   └── qdrant_client.py
│
├── infra/
│   ├── prometheus/
│   ├── grafana/
│   └── k8s/
│
├── sample_services/
│   └── checkout_service/
│       ├── payment_client.py
│       ├── checkout_api.py
│       └── tests/
│
├── scripts/
│   ├── kind_create.sh
│   ├── minikube_create.sh
│   ├── k8s_deploy_sample.sh
│   ├── k8s_validate.sh
│   └── index_repo.py
│
└── workspace/
    ├── runs/
    └── prs/
```

---

## Why This Is More Than a Basic AI Project

A basic AI project usually works like this:

```text
Prompt → LLM → Answer
```

AegisSRE works like this:

```text
Production Alert
→ Observability Context
→ Codebase Search
→ Root-Cause Analysis
→ Code Patch
→ Test Execution
→ Integration Validation
→ Red Team Audit
→ Pull Request
→ Human Approval
```

This makes it a true agentic engineering system.

It includes:

* Multi-step reasoning
* Tool usage
* State transitions
* Conditional retries
* Verification loops
* Infrastructure integration
* Human-in-the-loop control
* Safety checks
* Production-style architecture

---

## Design Principles

### 1. Evidence Before Action

The system does not patch code randomly.

It first collects operational and codebase evidence.

### 2. Verification Over Guessing

The workflow requires tests and audits before PR creation.

### 3. Human Approval

The system does not auto-merge.

It generates a PR and waits for a human engineer.

### 4. Modular Infrastructure

Each real service can be swapped or upgraded:

* Kafka can be replaced with Redpanda.
* Qdrant can use stronger embeddings.
* Neo4j can use deeper AST graphs.
* Local validation can be upgraded to real Kubernetes.
* Rule-based Red Team checks can be upgraded to LLM-based review.

### 5. Safe Local Defaults

By default, the system does not push to GitHub and does not require production credentials.

---

## Future Improvements

Planned upgrades:

* Real OpenTelemetry trace ingestion
* Live Kubernetes pod remediation
* Real k6 load testing
* Firecracker microVM sandbox for Linux environments
* LLM-powered Red Team reviewer
* GitHub Checks integration
* Slack / Discord incident notifications
* Policy-as-code approval gates
* Multi-service dependency graph
* Automated rollback recommendation
* More incident types such as memory leak, CPU spike, and database timeout

---

## Resume Bullet

**AegisSRE — Self-Healing Multi-Agent DevOps Reliability Engineer | LangGraph · LangChain · Kafka · Temporal · Qdrant · Neo4j · Prometheus · Kubernetes**

* Built a self-healing AI SRE platform that detects production incidents, performs root-cause analysis using metrics, logs, traces, vector search, and code graph evidence, then generates verified code patches.
* Designed a LangGraph-based multi-agent workflow with sandboxed test execution, Kubernetes-style validation, Red Team audit, GitHub PR automation, and human-in-the-loop approval.
* Integrated real-infrastructure adapters for Kafka, Temporal, Qdrant, Neo4j, Prometheus, Grafana, GitHub API, and kind/minikube validation.

---

## Interview Explanation

> AegisSRE is a self-healing multi-agent DevOps reliability platform. When a production incident occurs, the system collects metrics, logs, traces, and pod state through an MCP-style observability bridge. It then uses Qdrant vector search and Neo4j code graph analysis to locate the likely root cause in the codebase. A software engineer agent applies a patch, runs tests, validates the behavior through Kubernetes-style integration checks, passes the patch through a Red Team audit, and finally generates a GitHub PR for human approval. The project demonstrates agentic AI, distributed systems, DevOps automation, observability, verification, and production-style engineering workflows.

---

## License

This project is intended for educational, research, and portfolio purposes.


