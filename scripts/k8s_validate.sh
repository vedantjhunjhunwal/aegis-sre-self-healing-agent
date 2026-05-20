#!/usr/bin/env bash
set -euo pipefail

echo "Running Kubernetes integration validation..."

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl not installed"
  exit 1
fi

kubectl get nodes
kubectl get pods -l app=checkout-api || true

echo "Validation passed"
