#!/usr/bin/env bash
# WebForge CI/CD Health Check
URL="${WEBFORGE_URL:-http://127.0.0.1:8000}"
KEY="wf_live_secret_key_123"

echo "=== WebForge Automated Pipeline Execution ==="
RESPONSE=$(curl -s -X POST "$URL/api/run" \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"project_id": 1, "environment": "Staging"}')

echo "Result: $RESPONSE"

STATUS=$(echo "$RESPONSE" | grep -o '"status":"[^"]*' | grep -o '[^"]*$')

if [ "$STATUS" = "SUCCESS" ]; then
    echo ">>> PIPELINE PASSED: All regression tests succeeded. Deployment allowed."
    exit 0
else
    echo ">>> PIPELINE FAILED: Test suite encountered failures. Deployment blocked."
    exit 1
fi