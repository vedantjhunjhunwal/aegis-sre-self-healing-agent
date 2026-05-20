from __future__ import annotations

from typing import TypedDict, Dict, Any, List
from pathlib import Path
import json
import uuid
import shutil
import time

from langgraph.graph import StateGraph, END

from apps.config import settings
from agents.langchain_tools import (
    mcp_observability_context,
    index_repository,
    repo_root_cause_search,
    apply_retry_backoff_patch,
    run_sandbox_tests,
    run_k8s_integration_validation,
    red_team_audit_patch,
    create_github_pr,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class AegisState(TypedDict, total=False):
    run_id: str
    status: str
    alert: Dict[str, Any]
    repo_root: str
    context: Dict[str, Any]
    index_result: Dict[str, Any]
    rca: Dict[str, Any]
    patch: Dict[str, Any]
    unit_tests: Dict[str, Any]
    integration: Dict[str, Any]
    red_team: Dict[str, Any]
    pull_request: Dict[str, Any]
    events: List[Dict[str, Any]]
    repair_attempts: int
    error: str


def event(state: AegisState, stage: str, message: str):
    state.setdefault("events", []).append({
        "time": time.strftime("%H:%M:%S"),
        "stage": stage,
        "message": message,
    })


def create_workspace(run_id: str) -> Path:
    src = PROJECT_ROOT / "sample_services" / "checkout_service"
    dst = PROJECT_ROOT / settings.workspace_dir / "runs" / run_id
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def observe_alert(state: AegisState) -> AegisState:
    state["run_id"] = state.get("run_id", str(uuid.uuid4())[:8])
    state["status"] = "running"
    state["repair_attempts"] = 0
    workspace = create_workspace(state["run_id"])
    state["repo_root"] = str(workspace)
    event(state, "observe_alert", "Incident accepted from Kafka/API and workspace created.")
    return state


def collect_context(state: AegisState) -> AegisState:
    alert = state["alert"]
    raw = mcp_observability_context.invoke(json.dumps({
        "service": alert["service"],
        "trace_id": alert.get("trace_id", "unknown"),
    }))
    state["context"] = json.loads(raw)
    event(state, "collect_context", "MCP bridge collected metrics, logs, pods, and trace context.")
    return state


def root_cause_analysis(state: AegisState) -> AegisState:
    idx_raw = index_repository.invoke(json.dumps({"repo_root": state["repo_root"]}))
    state["index_result"] = json.loads(idx_raw)

    search_raw = repo_root_cause_search.invoke(json.dumps({
        "repo_root": state["repo_root"],
        "query": "payment timeout retry amplification calculate_retry_delay return 0 latency",
        "function": "calculate_retry_delay",
    }))
    evidence = json.loads(search_raw)

    hits = evidence.get("qdrant_hits", [])
    suspected_file = hits[0]["file"] if hits else "payment_client.py"

    state["rca"] = {
        "suspected_file": suspected_file,
        "suspected_function": "calculate_retry_delay",
        "root_cause": "The retry delay function returns zero, causing immediate retry amplification during payment gateway timeouts and increasing p95 latency.",
        "confidence": 0.91,
        "evidence": evidence,
    }
    event(state, "root_cause_analysis", f"RCA mapped incident to {suspected_file}:calculate_retry_delay.")
    return state


def engineer_patch(state: AegisState) -> AegisState:
    state["repair_attempts"] = state.get("repair_attempts", 0) + 1
    raw = apply_retry_backoff_patch.invoke(json.dumps({
        "repo_root": state["repo_root"],
        "file": state["rca"]["suspected_file"],
    }))
    state["patch"] = json.loads(raw)
    event(state, "engineer_patch", f"Patch attempt {state['repair_attempts']}: {state['patch'].get('status')}.")
    return state


def sandbox_unit_tests(state: AegisState) -> AegisState:
    raw = run_sandbox_tests.invoke(json.dumps({"repo_root": state["repo_root"]}))
    state["unit_tests"] = json.loads(raw)
    event(state, "sandbox_unit_tests", f"Unit tests {state['unit_tests']['status']}.")
    return state


def integration_validate(state: AegisState) -> AegisState:
    raw = run_k8s_integration_validation.invoke(json.dumps({
        "repo_root": state["repo_root"],
        "service": state["alert"]["service"],
    }))
    state["integration"] = json.loads(raw)
    event(state, "integration_validate", f"Kubernetes/kind validation {state['integration']['status']}.")
    return state


def red_team_audit(state: AegisState) -> AegisState:
    modified_file = state["patch"].get("file", state["rca"]["suspected_file"])
    raw = red_team_audit_patch.invoke(json.dumps({
        "repo_root": state["repo_root"],
        "modified_file": modified_file,
    }))
    state["red_team"] = json.loads(raw)
    event(state, "red_team_audit", f"Red Team audit {state['red_team']['audit_status']}.")
    return state


def open_pr(state: AegisState) -> AegisState:
    title = "Fix checkout retry amplification with bounded exponential backoff"
    body = build_pr_body(state)
    raw = create_github_pr.invoke(json.dumps({
        "title": title,
        "body": body,
        "branch_name": f"aegis/self-heal-{state['run_id']}",
        "repo_path": state["repo_root"],
    }))
    state["pull_request"] = json.loads(raw)
    state["status"] = "awaiting_human_approval"
    event(state, "open_pr", "GitHub PR/local PR artifact created.")
    return state


def fail_workflow(state: AegisState) -> AegisState:
    state["status"] = "failed"
    event(state, "failed", "Workflow stopped because validation or audit failed.")
    return state


def decide_after_unit_tests(state: AegisState) -> str:
    if state["unit_tests"]["status"] == "passed":
        return "integration_validate"
    if state.get("repair_attempts", 0) < settings.max_repair_attempts:
        return "engineer_patch"
    return "fail_workflow"


def decide_after_integration(state: AegisState) -> str:
    return "red_team_audit" if state["integration"]["status"] == "passed" else "fail_workflow"


def decide_after_red_team(state: AegisState) -> str:
    if state["red_team"]["audit_status"] == "approved":
        return "open_pr"
    if state.get("repair_attempts", 0) < settings.max_repair_attempts:
        return "engineer_patch"
    return "fail_workflow"


def build_pr_body(state: AegisState) -> str:
    return f'''
## Incident Summary

Service: `{state['alert']['service']}`  
Severity: `{state['alert']['severity']}`  
Symptom: `{state['alert']['symptom']}`

## Root Cause

{state['rca']['root_cause']}

Confidence: `{state['rca']['confidence']}`

## Patch

{state['patch'].get('summary')}

## Unit Tests

Status: `{state['unit_tests']['status']}`

```text
{state['unit_tests'].get('stdout', '')}
{state['unit_tests'].get('stderr', '')}
```

## Integration Validation

Status: `{state['integration']['status']}`

```json
{json.dumps(state['integration'], indent=2)}
```

## Red Team Audit

Status: `{state['red_team']['audit_status']}`

```json
{json.dumps(state['red_team'], indent=2)}
```

## Human Approval

This PR was generated by AegisSRE and should be reviewed by a human SRE before merge.
'''


def build_graph():
    graph = StateGraph(AegisState)

    graph.add_node("observe_alert", observe_alert)
    graph.add_node("collect_context", collect_context)
    graph.add_node("root_cause_analysis", root_cause_analysis)
    graph.add_node("engineer_patch", engineer_patch)
    graph.add_node("sandbox_unit_tests", sandbox_unit_tests)
    graph.add_node("integration_validate", integration_validate)
    graph.add_node("red_team_audit", red_team_audit)
    graph.add_node("open_pr", open_pr)
    graph.add_node("fail_workflow", fail_workflow)

    graph.set_entry_point("observe_alert")
    graph.add_edge("observe_alert", "collect_context")
    graph.add_edge("collect_context", "root_cause_analysis")
    graph.add_edge("root_cause_analysis", "engineer_patch")
    graph.add_edge("engineer_patch", "sandbox_unit_tests")

    graph.add_conditional_edges(
        "sandbox_unit_tests",
        decide_after_unit_tests,
        {
            "integration_validate": "integration_validate",
            "engineer_patch": "engineer_patch",
            "fail_workflow": "fail_workflow",
        },
    )

    graph.add_conditional_edges(
        "integration_validate",
        decide_after_integration,
        {
            "red_team_audit": "red_team_audit",
            "fail_workflow": "fail_workflow",
        },
    )

    graph.add_conditional_edges(
        "red_team_audit",
        decide_after_red_team,
        {
            "open_pr": "open_pr",
            "engineer_patch": "engineer_patch",
            "fail_workflow": "fail_workflow",
        },
    )

    graph.add_edge("open_pr", END)
    graph.add_edge("fail_workflow", END)

    return graph.compile()


class AegisWorkflowRunner:
    def __init__(self):
        self.graph = build_graph()
        self.runs: Dict[str, AegisState] = {}

    def run(self, alert: Dict[str, Any]) -> AegisState:
        initial: AegisState = {
            "alert": alert,
            "events": [],
        }
        final = self.graph.invoke(initial)
        self.runs[final["run_id"]] = final
        return final

    def list_runs(self):
        return list(self.runs.values())

    def get_run(self, run_id: str):
        return self.runs.get(run_id)
