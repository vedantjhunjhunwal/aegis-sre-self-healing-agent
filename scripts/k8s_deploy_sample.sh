#!/usr/bin/env bash
set -euo pipefail

docker build -t checkout-api:local sample_services/checkout_service

if command -v kind >/dev/null 2>&1; then
  kind load docker-image checkout-api:local --name aegis-sre || true
fi

kubectl apply -f infra/k8s/checkout-deployment.yaml
kubectl rollout status deployment/checkout-api --timeout=120s
kubectl get pods -l app=checkout-api
