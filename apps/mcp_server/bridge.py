from typing import Dict, Any, List
from apps.config import settings
from clients.prometheus_client import PrometheusClient
import subprocess
import json


class MCPObservabilityBridge:
    def __init__(self):
        self.prom = PrometheusClient(settings.prometheus_url)

    def query_metrics(self, service: str) -> Dict[str, Any]:
        prometheus = self.prom.incident_snapshot(service)
        fallback_slo = {
            "p95_latency_ms": 2400,
            "error_rate": 0.18,
            "retry_rate_per_second": 180,
            "symptom": "p95 latency spike and retry amplification",
        }
        return {
            "service": service,
            "prometheus": prometheus,
            "slo_snapshot": fallback_slo,
        }

    def get_k8s_pods(self, service: str) -> List[Dict[str, Any]]:
        try:
            proc = subprocess.run(
                ["kubectl", "get", "pods", "-l", f"app={service}", "-o", "json"],
                text=True,
                capture_output=True,
                timeout=8,
            )
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr)
            data = json.loads(proc.stdout)
            return [
                {
                    "name": item["metadata"]["name"],
                    "phase": item["status"]["phase"],
                    "restart_count": sum(c.get("restartCount", 0) for c in item["status"].get("containerStatuses", [])),
                }
                for item in data.get("items", [])
            ]
        except Exception as exc:
            return [{"name": f"{service}-demo-1", "phase": "Running", "restart_count": 0, "fallback_reason": str(exc)}]

    def get_recent_logs(self, service: str) -> List[str]:
        try:
            proc = subprocess.run(
                ["kubectl", "logs", "-l", f"app={service}", "--tail=50"],
                text=True,
                capture_output=True,
                timeout=8,
            )
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr)
            return proc.stdout.splitlines()[-50:]
        except Exception as exc:
            return [
                "WARN payment gateway timeout",
                "WARN retrying payment charge immediately",
                "ERROR checkout latency exceeded SLO",
                "TRACE calculate_retry_delay returned 0",
                f"fallback_logs_reason={exc}",
            ]

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        return {
            "trace_id": trace_id,
            "critical_path": [
                "checkout_api.create_order",
                "payment_client.charge_with_retry",
                "payment_client.calculate_retry_delay",
            ],
            "slow_span": "payment_client.charge_with_retry",
            "repeated_calls": 5,
        }
