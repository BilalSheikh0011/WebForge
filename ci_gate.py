import sys
import json
import urllib.request
import urllib.error

print("========================================================")
print("  WebForge Automated CI/CD Quality Gate Runner")
print("========================================================")

# Change this value to switch between PASS and FAIL:
# "leather"               -> PASSES (Exit Code 0)
# "NON_EXISTENT_TEXT_XYZ" -> FAILS (Exit Code 1)
expected_text = "leather"

payload = {
    "test_case_id": 1,
    "base_url": "https://leatherlaneatelier.store",
    "stop_on_fail": True,
    "steps": [
        {"action": "navigate", "value": "https://leatherlaneatelier.store"},
        {"action": "wait", "value": "2000"},
        {
            "action": "assert_text_contains",
            "selector_type": "css",
            "selector": "body",
            "expected": expected_text
        }
    ]
}

url = "http://localhost:8000/runs/execute"
req_data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    url,
    data=req_data,
    headers={"Content-Type": "application/json"}
)

try:
    print(f"Triggering WebForge Execution Engine on target: {payload['base_url']}...")
    with urllib.request.urlopen(req, timeout=60) as response:
        res_body = response.read().decode("utf-8")
        data = json.loads(res_body)

    status = data.get("overall_status", "UNKNOWN")
    print(f"Execution Verdict: {status}")

    if status == "FAIL":
        print("\n❌ [QUALITY GATE TRIPPED]: Assertion mismatch detected!")
        print("🛑 [DEPLOYMENT HALTED]: Blocking pipeline release. Exiting with Code 1.")
        print("========================================================")
        sys.exit(1)
    else:
        print("\n✅ [QUALITY GATE PASSED]: All regression steps verified.")
        print("🚀 [DEPLOYMENT PROCEEDING]: Release approved. Exiting with Code 0.")
        print("========================================================")
        sys.exit(0)

except urllib.error.HTTPError as http_err:
    print(f"❌ Backend returned HTTP error: {http_err.code}")
    sys.exit(1)
except Exception as err:
    print(f"\n❌ Error contacting WebForge Engine: {err}")
    sys.exit(1)