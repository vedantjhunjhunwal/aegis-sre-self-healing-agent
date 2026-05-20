# AegisSRE Real Infra Edition

AegisSRE is a self-healing multi-agent DevOps/SRE system implemented using this architecture:

```text
Production K8s
   ↓
Kafka Event Bus
   ↓
Temporal/LangGraph Orchestrator
   ↓
MCP Observability Bridge
   ↓
RCA: Neo4j Code Graph + Qdrant Vector Search
   ↓
SWE Agent: sandboxed code patching
   ↓
kind/minikube integration environment
   ↓
Red Team Audit
   ↓
GitHub PR
   ↓
HITL Dashboard
```

## What is implemented

- LangGraph is the actual workflow graph.
- LangChain tools wrap MCP, repo search, patching, testing, Kubernetes, and GitHub.
- Docker Compose provides Kafka, Temporal, Qdrant, Neo4j, Prometheus, Grafana, Postgres, and the AegisSRE API.
- GitHub API can open real PRs when configured.
- kind/minikube scripts provide Kubernetes-style integration validation.
- Firecracker is optional because it is hard to run on Windows.

## Quick Start: Full Infra

```bash
cp .env.example .env
docker compose up --build
```

Open:

```text
http://localhost:8080
```

Trigger incident:

```bash
curl -X POST http://localhost:8080/api/incidents/demo
```

## Python-only Dev Mode

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python apps.py
```

Open:

```text
http://127.0.0.1:8080
```

## GitHub PR Configuration

Edit `.env`:

```env
GITHUB_TOKEN=ghp_your_token
GITHUB_OWNER=your-github-username
GITHUB_REPO=your-target-repo
GITHUB_BASE_BRANCH=main
GITHUB_CREATE_REAL_PR=true
```

If `GITHUB_CREATE_REAL_PR=false`, AegisSRE creates a local PR markdown artifact in `workspace/prs`.

## Infra URLs

| Service | URL |
|---|---|
| AegisSRE Dashboard/API | http://localhost:8080 |
| Temporal UI | http://localhost:8233 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Neo4j Browser | http://localhost:7474 |
| Qdrant | http://localhost:6333 |

Neo4j login: `neo4j / aegis-password`  
Grafana login: `admin / admin`

## Workflow

The real LangGraph workflow is in:

```text
apps/orchestrator/langgraph_workflow.py
```

Nodes:

```text
observe_alert → collect_context → root_cause_analysis → engineer_patch
→ sandbox_unit_tests → integration_validate → red_team_audit → open_pr
```

Conditional repair loop:

```text
tests fail → engineer_patch
red team rejects → engineer_patch
max attempts reached → fail
success → PR
```

## Interview Explanation

> I built AegisSRE, a self-healing multi-agent SRE platform where production incidents are ingested through Kafka, orchestrated through a LangGraph/Temporal-style workflow, enriched using an MCP observability bridge, diagnosed with Neo4j code graph and Qdrant semantic search, patched by a software engineer agent, validated in sandbox and Kubernetes-style integration environments, audited by an adversarial Red Team agent, and finally converted into a GitHub pull request with a HITL dashboard.
