
from backend.app.agents.mcp_server.server import (
    get_recent_logs,
    get_incident_details,
    search_runbooks,
    get_approval_status,
)

INCIDENT_ID = "1a9310c2-7dd2-4134-bed5-a08950371ae2"

print("\n--- TEST 1: RECENT LOGS ---")
logs = get_recent_logs(5)
print(logs)

print("\n--- TEST 2: INCIDENT DETAILS ---")
incident = get_incident_details(INCIDENT_ID)
print(incident)

print("\n--- TEST 3: RUNBOOK SEARCH ---")
results = search_runbooks("high CPU usage", 3)
print(results)

print("\n--- TEST 4: APPROVAL STATUS ---")
approval = get_approval_status(INCIDENT_ID)
print(approval)
