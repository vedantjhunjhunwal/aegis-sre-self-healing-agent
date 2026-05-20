from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from apps.orchestrator.langgraph_workflow import AegisWorkflowRunner

app = FastAPI(title="AegisSRE Real Infra Edition")
runner = AegisWorkflowRunner()


class Incident(BaseModel):
    service: str
    severity: str = "critical"
    symptom: str = "p95 latency above SLO"
    metric: str = "http_request_duration_seconds_p95"
    trace_id: str = "trace-demo"


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTML


@app.post("/api/incidents/demo")
def trigger_demo_incident():
    alert = {
        "service": "checkout-api",
        "severity": "critical",
        "symptom": "p95 latency above 2s after payment gateway timeout",
        "metric": "http_request_duration_seconds_p95",
        "trace_id": "trace-checkout-123",
    }
    state = runner.run(alert)
    return JSONResponse(state)


@app.post("/api/incidents")
def trigger_incident(incident: Incident):
    state = runner.run(incident.model_dump())
    return JSONResponse(state)


@app.get("/api/runs")
def list_runs():
    return runner.list_runs()


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = runner.get_run(run_id)
    if not run:
        return JSONResponse({"error": "not found"}, status_code=404)
    return run


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    content = "# HELP aegis_sre_up AegisSRE API health\n# TYPE aegis_sre_up gauge\naegis_sre_up 1\n"
    return Response(content=content, media_type="text/plain")


HTML = '''
<!doctype html>
<html>
<head>
  <title>AegisSRE Real Infra Control Plane</title>
  <style>
    body { font-family: Inter, Arial, sans-serif; margin: 0; background: #f6f7fb; color: #111827; }
    header { background: #0f172a; color: white; padding: 20px 32px; }
    main { padding: 24px 32px; max-width: 1250px; margin: auto; }
    button { background: #2563eb; color: white; border: none; padding: 12px 18px; border-radius: 10px; cursor: pointer; font-weight: 700; }
    button:hover { background: #1d4ed8; }
    .grid { display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 16px; margin-top: 20px; }
    .card { background: white; border: 1px solid #e5e7eb; border-radius: 16px; padding: 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.05); }
    pre { background: #020617; color: #dbeafe; padding: 14px; border-radius: 12px; overflow: auto; max-height: 560px; }
    .status { display: inline-block; padding: 6px 10px; border-radius: 999px; background: #dcfce7; color: #166534; font-weight: 700; margin-bottom: 10px; }
    .event { border-left: 3px solid #2563eb; padding-left: 10px; margin: 10px 0; }
    .small { color: #64748b; font-size: 14px; }
    a { color: #2563eb; }
  </style>
</head>
<body>
<header>
  <h1>AegisSRE Real Infra Control Plane</h1>
  <div>Kafka → LangGraph/Temporal → MCP → Qdrant/Neo4j RCA → Sandbox → kind/minikube → Red Team → GitHub PR</div>
</header>
<main>
  <button onclick="triggerIncident()">Trigger Demo Incident</button>
  <span id="status" class="small"></span>

  <div class="grid">
    <div class="card">
      <h2>Workflow Trace</h2>
      <div id="trace">No run yet.</div>
    </div>
    <div class="card">
      <h2>Run JSON</h2>
      <pre id="json">{}</pre>
    </div>
  </div>

  <div class="card" style="margin-top: 16px;">
    <h2>Infra Links</h2>
    <p>
      <a href="http://localhost:8233" target="_blank">Temporal UI</a> ·
      <a href="http://localhost:9090" target="_blank">Prometheus</a> ·
      <a href="http://localhost:3000" target="_blank">Grafana</a> ·
      <a href="http://localhost:7474" target="_blank">Neo4j</a> ·
      <a href="http://localhost:6333/dashboard" target="_blank">Qdrant</a>
    </p>
  </div>
</main>

<script>
async function triggerIncident() {
  document.getElementById("status").innerText = " Running LangGraph workflow...";
  const res = await fetch("/api/incidents/demo", { method: "POST" });
  const data = await res.json();
  render(data);
  document.getElementById("status").innerText = " Done.";
}

function render(data) {
  document.getElementById("json").innerText = JSON.stringify(data, null, 2);
  const trace = document.getElementById("trace");
  trace.innerHTML = "";
  const badge = document.createElement("div");
  badge.className = "status";
  badge.innerText = data.status;
  trace.appendChild(badge);

  (data.events || []).forEach(e => {
    const div = document.createElement("div");
    div.className = "event";
    div.innerHTML = `<b>${e.time} — ${e.stage}</b><br><span>${e.message}</span>`;
    trace.appendChild(div);
  });
}
</script>
</body>
</html>
'''
