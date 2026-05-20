from typing import Dict, Any
import requests


class PrometheusClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def query(self, promql: str) -> Dict[str, Any]:
        try:
            res = requests.get(
                f"{self.base_url}/api/v1/query",
                params={"query": promql},
                timeout=5,
            )
            res.raise_for_status()
            return res.json()
        except Exception as exc:
            return {
                "status": "fallback",
                "error": str(exc),
                "query": promql,
                "data": {"result": []},
            }

    def incident_snapshot(self, service: str) -> Dict[str, Any]:
        queries = {
            "p95_latency": f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m]))',
            "error_rate": f'rate(http_requests_total{{service="{service}",status=~"5.."}}[5m])',
            "cpu": f'rate(container_cpu_usage_seconds_total{{pod=~"{service}.*"}}[5m])',
            "memory": f'container_memory_usage_bytes{{pod=~"{service}.*"}}',
        }
        return {name: self.query(q) for name, q in queries.items()}
