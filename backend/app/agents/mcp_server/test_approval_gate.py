
import pytest

from backend.app.agents.mcp_server.mcp_incident_agent import (
    check_human_approval,
    route_after_approval,
)


@pytest.mark.parametrize(
    "approval_status, expected_allowed, expected_workflow, expected_route",
    [
        ("APPROVED", True, "READY_FOR_REMEDIATION", "approved"),
        ("REJECTED", False, "BLOCKED_REJECTED", "blocked"),
        (
            "PENDING_HUMAN_APPROVAL",
            False,
            "BLOCKED_PENDING_APPROVAL",
            "blocked",
        ),
    ],
)
def test_approval_gate(
    approval_status,
    expected_allowed,
    expected_workflow,
    expected_route,
):
    state = {
        "approval": {"status": approval_status},
        "remediation_allowed": False,
    }

    result = check_human_approval(state)
    state.update(result)

    assert state["remediation_allowed"] is expected_allowed
    assert state["workflow_status"] == expected_workflow
    assert route_after_approval(state) == expected_route
