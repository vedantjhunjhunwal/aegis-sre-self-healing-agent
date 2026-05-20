#!/usr/bin/env bash
set -euo pipefail

kind create cluster --name aegis-sre || true
kubectl cluster-info --context kind-aegis-sre
