#!/usr/bin/env bash
set -euo pipefail

minikube start -p aegis-sre
kubectl config use-context aegis-sre
