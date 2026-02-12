#!/usr/bin/env bash

set -euo pipefail

TARGET_IP=${1:-172.20.0.40}
SEQUENCE=${2:-"1234,5678,9012"}
PROTECTED_PORT=${3:-2222}
TIMEOUT=${4:-3}

echo "[1/3] Attempting protected port before knocking (timeout ${TIMEOUT}s)"
nc -z -v -w "$TIMEOUT" "$TARGET_IP" "$PROTECTED_PORT" || true

echo "[2/3] Sending knock sequence: $SEQUENCE"
python3 knock_client.py --target "$TARGET_IP" --sequence "$SEQUENCE" --check

echo "[3/3] Attempting protected port after knocking (timeout ${TIMEOUT}s)"
nc -z -v -w "$TIMEOUT" "$TARGET_IP" "$PROTECTED_PORT" || true
