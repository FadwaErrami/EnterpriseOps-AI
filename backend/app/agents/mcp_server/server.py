
from mcp.server.fastmcp import FastMCP

from backend.app.services.storage_service import (
    get_logs,
    get_incident,
    get_approval_decision,
)

from backend.app.services.rag_service import rag_service


mcp = FastMCP("EnterpriseOps AI")



@mcp.tool()
def get_recent_logs(
    limit: int = 20,
    incident_id: str = None
) -> list:
    """Retrieve logs, optionally filtered by a specific incident."""
    limit = max(1, min(limit, 100))
    return get_logs(
        limit=limit,
        incident_id=incident_id
    )


@mcp.tool()
def get_incident_details(incident_id: str) -> dict:
    """Retrieve details about a specific incident."""
    incident = get_incident(incident_id)

    if incident is None:
        return {"error": "Incident not found"}

    return incident


@mcp.tool()
def search_runbooks(query: str, top_k: int = 3) -> dict:
    """Search operational runbooks for troubleshooting procedures."""
    top_k = max(1, min(top_k, 5))
    return rag_service.search(query=query, top_k=top_k)


@mcp.tool()
def get_approval_status(incident_id: str) -> dict:
    """Retrieve the human approval decision for an incident."""
    decision = get_approval_decision(incident_id)

    if decision is None:
        return {
            "incident_id": incident_id,
            "status": "PENDING_HUMAN_APPROVAL",
            "approval": None,
        }

    return {
        "incident_id": incident_id,
        "status": decision["decision"],
        "approval": decision,
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
