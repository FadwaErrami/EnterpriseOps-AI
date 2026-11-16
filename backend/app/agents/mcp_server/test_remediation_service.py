from backend.app.services.remediation_service import execute_remediation


def test_approved_remediation_is_simulated():
    incident = {
        "service": "payment-service",
        "title": "High Cpu detected",
    }

    result = execute_remediation(incident, True)

    assert result["status"] == "SIMULATED"
    assert result["action"] == "restart_service"
    assert result["executed"] is False


def test_unapproved_remediation_is_blocked():
    incident = {
        "service": "payment-service",
        "title": "High Cpu detected",
    }

    result = execute_remediation(incident, False)

    assert result["status"] == "BLOCKED"
    assert result["executed"] is False