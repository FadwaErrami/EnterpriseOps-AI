def execute_remediation(incident: dict, remediation_allowed: bool):
    if not remediation_allowed:
        return {
            "status": "BLOCKED",
            "message": "Human approval is required.",
            "executed": False,
        }

    return {
        "status": "SIMULATED",
        "message": (
            f"Remediation simulated for "
            f"{incident['service']}: {incident['title']}"
        ),
        "action": "restart_service",
        "executed": False,
    }


def execute_remediation(incident: dict, remediation_allowed: bool):
    if not remediation_allowed:
        return {
            "status": "BLOCKED",
            "message": "Human approval is required.",
            "executed": False,
        }

    return {
        "status": "SIMULATED",
        "message": (
            f"Remediation simulated for "
            f"{incident['service']}: {incident['title']}"
        ),
        "action": "restart_service",
        "executed": False,
    }