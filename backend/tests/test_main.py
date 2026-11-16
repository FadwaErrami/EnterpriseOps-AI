
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

INCIDENT_ID = "1a9310c2-7dd2-4134-bed5-a08950371ae2"


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to EnterpriseOps AI",
        "status": "running"
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }

def test_get_incidents():
    response = client.get("/incidents")

    assert response.status_code == 200

    data = response.json()

    assert "total" in data
    assert "incidents" in data
    assert isinstance(data["incidents"], list)
    assert data["total"] == len(data["incidents"])


def test_get_incident_audit():
    response = client.get(
        f"/incidents/{INCIDENT_ID}/audit"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["incident_id"] == INCIDENT_ID
    assert isinstance(data["audits"], list)
    assert data["total"] == len(data["audits"])

    if data["total"] > 0:
        audit = data["audits"][0]

        assert audit["approval_decision"] == "APPROVED"
        assert audit["status"] == "SIMULATED"
        assert audit["executed"] is False


def test_audit_for_unknown_incident():
    response = client.get(
        "/incidents/unknown-incident-id/audit"
    )

    assert response.status_code == 404
