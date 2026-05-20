import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "canon/workflow"

STATUS_PATH = "/api/workflow/status"
TEMPLATE_PATH = "/api/workflow/templates/universal-172"
RULES_PATH = "/api/workflow/rules/transitions"
BUTTONS_PATH = "/api/workflow/ui/action-button-matrix"
SAMPLE_ITEM_PATH = "/api/workflow/items/sample"
SAMPLE_ALLOWED_PATH = "/api/workflow/items/sample/allowed-actions"

def read_json(path):
    return json.loads(path.read_text())

def response_for_path(path):
    template = read_json(WORKFLOW / "universal_172_process.json")
    rules = read_json(WORKFLOW / "rules/workflow_transition_rules_v0.json")
    buttons = read_json(WORKFLOW / "ui/roadwork_action_button_matrix_v0.json")
    sample = read_json(WORKFLOW / "samples/universal_172_sample_workflow.json")

    if path == STATUS_PATH:
        return {
            "ok": True,
            "service": "roadwork-local-api-proof",
            "mode": "local_only",
            "implemented": "proof_only",
            "production": False,
            "template_steps": template["step_count"],
            "transition_statuses": len(rules["statuses"]),
        }

    if path == TEMPLATE_PATH:
        return {
            "ok": True,
            "template": template,
            "step_count": template["step_count"],
            "macro_count": template["macro_count"],
        }

    if path == RULES_PATH:
        return {
            "ok": True,
            "rules": rules,
        }

    if path == BUTTONS_PATH:
        return {
            "ok": True,
            "matrix": buttons,
        }

    if path == SAMPLE_ITEM_PATH:
        return {
            "ok": True,
            "workflow_item": sample["workflow_item"],
            "task_count": sample["task_count"],
            "event_count": sample["event_count"],
        }

    if path == SAMPLE_ALLOWED_PATH:
        status = sample["workflow_item"]["status"]
        return {
            "ok": True,
            "workflow_item_id": sample["workflow_item"]["id"],
            "status": status,
            "actions": buttons["buttons_by_status"].get(status, []),
        }

    return {
        "ok": False,
        "error": "not_found",
        "path": path,
    }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        payload = response_for_path(path)
        status = 200 if payload.get("ok") else 404

        body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")

        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return

def smoke():
    checks = [
        STATUS_PATH,
        TEMPLATE_PATH,
        RULES_PATH,
        BUTTONS_PATH,
        SAMPLE_ITEM_PATH,
        SAMPLE_ALLOWED_PATH,
    ]

    results = {}

    for path in checks:
        payload = response_for_path(path)
        if not payload.get("ok"):
            raise SystemExit(f"smoke failed for {path}: {payload}")
        results[path] = payload

    if results[TEMPLATE_PATH]["step_count"] != 172:
        raise SystemExit("template step_count was not 172")

    if results[STATUS_PATH]["production"] is not False:
        raise SystemExit("production flag must be false")

    if not results[SAMPLE_ALLOWED_PATH]["actions"]:
        raise SystemExit("sample allowed actions empty")

    print("smoke_ok: True")
    print("endpoints:", len(checks))
    print("template_steps:", results[TEMPLATE_PATH]["step_count"])
    print("sample_status:", results[SAMPLE_ALLOWED_PATH]["status"])
    print("sample_allowed_actions:", len(results[SAMPLE_ALLOWED_PATH]["actions"]))

def serve(host, port):
    server = HTTPServer((host, port), Handler)
    print(f"RoadWork local API proof serving http://{host}:{port}")
    print("mode: local_only proof_only production=false")
    server.serve_forever()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8789)
    args = parser.parse_args()

    if args.smoke:
        smoke()
    else:
        serve(args.host, args.port)

if __name__ == "__main__":
    main()
