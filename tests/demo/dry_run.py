"""Demo rehearsal: runs every step of docs/demo/README.md against a stack and checks the documented outcome.

    docker compose exec api python manage.py seed_demo --reset
    python docs/demo/make_demo_import.py
    python tests/demo/dry_run.py [https://localhost]

Only the Python standard library. Prints one line per step; exits 1 if any step differs from the script.
Steps 2 (email activation) and 5 (refresh on reload) are browser flows covered by Cypress spec 1 and
tests/browser/refresh-race.mjs; step 10 is shown by hand.
"""

import json
import ssl
import sys
import urllib.error
import urllib.request
import uuid
from datetime import date, timedelta
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://localhost").rstrip("/")
PASSWORD = "Demo-Pass-2026!"
CTX = ssl.create_default_context()
CTX.check_hostname, CTX.verify_mode = False, ssl.CERT_NONE  # local certificate
IMPORT_FILE = Path(__file__).resolve().parents[2] / "docs" / "demo" / "demo-import.csv"
results = []


def call(method, path, token=None, body=None, raw=None, content_type="application/json"):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", content_type)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            payload = r.read()
            status, ctype = r.status, r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        payload, status, ctype = e.read(), e.code, e.headers.get("Content-Type", "")
    parsed = json.loads(payload) if "json" in ctype and payload else payload
    return status, parsed


def login(email):
    status, data = call("POST", "/api/v1/auth/login/", body={"email": email, "password": PASSWORD})
    assert status == 200, f"login {email}: {status} {data}"
    return data["access"]


def check(step, what, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'DIFF'}  {step:<4} {what}{'  -> ' + detail if detail else ''}")


# 1. guest: live URL and API docs
status, _ = call("GET", "/")
check("1", "app over HTTPS", status == 200, str(status))
status, _ = call("GET", "/api/docs/")
check("1", "Swagger UI at /api/docs/", status == 200, str(status))

# 3. arta: meal 60 EUR for 1 attendee is refused with the reason, 3 attendees saves, submit works
arta = login("arta@expenseflow.dev")
projects = call("GET", "/api/v1/projects/", arta)[1]
alpha = next(p for p in (projects["results"] if isinstance(projects, dict) else projects) if p["code"] == "ALPHA")
meal = {
    "type": "MEAL",
    "project": alpha["id"],
    "amount": "60.00",
    "attendees": 1,
    "expense_date": str(date.today() - timedelta(days=1)),
    "description": "Lunch with a client (demo rehearsal)",
}
status, data = call("POST", "/api/v1/expenses/", arta, meal)
reason = json.dumps(data.get("errors", {})) if isinstance(data, dict) else ""
check("3", "meal 60 EUR, 1 attendee refused with the policy reason", status == 400 and "25.00" in reason, reason[:90])
status, data = call("POST", "/api/v1/expenses/", arta, {**meal, "attendees": 3})
check("3", "with 3 attendees it saves as DRAFT", status == 201 and data.get("status") == "DRAFT", str(status))
new_id = data.get("id")
status, data = call("POST", f"/api/v1/expenses/{new_id}/submit/", arta)
check("3", "submit -> SUBMITTED", status == 200 and data.get("status") == "SUBMITTED", str(status))

# 4. arta: import demo-import.csv -> 4 created, row 5 rejected
boundary = uuid.uuid4().hex
body = (
    f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="demo-import.csv"\r\n'
    f"Content-Type: text/csv\r\n\r\n".encode()
    + IMPORT_FILE.read_bytes()
    + f"\r\n--{boundary}--\r\n".encode()
)
status, data = call(
    "POST", "/api/v1/expenses/import/", arta, raw=body, content_type=f"multipart/form-data; boundary={boundary}"
)
created, errors = (data.get("created"), data.get("errors", [])) if isinstance(data, dict) else (None, [])
check(
    "4",
    "import: 4 created, row 5 rejected (meal cap)",
    created == 4 and len(errors) == 1 and errors[0]["row"] == 5,
    f"created={created} errors={[(e['row'], list(e['errors'])) for e in errors]}",
)

# 6. arta approves her own expense -> 403
status, _ = call("POST", f"/api/v1/expenses/{new_id}/approve/", arta)
check("6", "employee approving her own expense -> 403", status == 403, str(status))

# 7. besa: full-text search "hotel", approve one, GAMMA approval blocked by the budget trigger
besa = login("besa@expenseflow.dev")
status, data = call("GET", "/api/v1/expenses/?status=SUBMITTED&q=hotel", besa)
hits = data.get("results", []) if isinstance(data, dict) else []
check("7", 'search "hotel" in the approval queue finds expenses', status == 200 and len(hits) > 0, f"{len(hits)} found")
approvable = next((e for e in hits if e["_links"].get("approve")), None)
if approvable:
    status, data = call("POST", f"/api/v1/expenses/{approvable['id']}/approve/", besa)
    check("7", "approve one of them -> APPROVED", status == 200 and data.get("status") == "APPROVED", str(status))
else:
    check("7", "approve one of them -> APPROVED", False, "no hotel expense besa may approve")
status, data = call("GET", "/api/v1/expenses/?status=SUBMITTED&q=docking", besa)
gamma = next((e for e in data.get("results", []) if e.get("project_code") == "GAMMA"), None)
status, data = call("POST", f"/api/v1/expenses/{gamma['id']}/approve/", besa) if gamma else (None, {})
detail = data.get("detail", "") if isinstance(data, dict) else ""
check(
    "7",
    "GAMMA approval refused: budget would be exceeded",
    status == 409 and "budget would be exceeded" in detail,
    detail[:90],
)

# 8. admin: report last quarter by department, APPROVED; save; export XLSX
admin = login("admin@expenseflow.dev")
criteria = {
    "date_from": str(date.today() - timedelta(days=92)),
    "date_to": str(date.today()),
    "group_by": "department",
    "statuses": ["APPROVED"],
}
status, data = call("POST", "/api/v1/reports/run/", admin, criteria)
rows = data.get("rows", []) if isinstance(data, dict) else []
check("8", "report by department, APPROVED", status == 200 and len(rows) > 0, f"{len(rows)} groups")
status, data = call("POST", "/api/v1/reports/", admin, {"name": "Demo rehearsal: last quarter", "criteria": criteria})
report_id = data.get("id") if isinstance(data, dict) else None
check("8", "save the report (MongoDB snapshot)", status == 201 and bool(report_id), str(status))
status, data = call("GET", f"/api/v1/reports/{report_id}/export/?format=xlsx", admin)
check(
    "8",
    "export XLSX",
    status == 200 and isinstance(data, bytes) and data[:2] == b"PK",
    f"{status}, {len(data or b'')} bytes",
)
call("DELETE", f"/api/v1/reports/{report_id}/", admin)

# 9. admin: reimburse until today, audit log has the entries
status, data = call("POST", "/api/v1/expenses/reimburse/", admin, {"until": str(date.today())})
count = data.get("count", data.get("reimbursed")) if isinstance(data, dict) else None
check("9", "reimburse until today returns a count", status == 200 and isinstance(count, int) and count > 0, f"{data}")
status, data = call("GET", "/api/v1/audit-logs/?action=EXPENSES_REIMBURSED", admin)
entries = data.get("results", data) if isinstance(data, (dict, list)) else []
check("9", "audit log shows the reimbursement", status == 200 and len(entries) > 0, f"{len(entries)} entries")

# 10. health
status, data = call("GET", "/health/")
check("10", "/health/ ok", status == 200 and data.get("status") == "ok", json.dumps(data))

print(f"\n{sum(results)}/{len(results)} checks as written in the demo script")
sys.exit(0 if all(results) else 1)
