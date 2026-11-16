
import json
from typing import TypedDict, Any
from backend.app.services.remediation_service import execute_remediation

from langgraph.graph import StateGraph, START, END

from backend.app.agents.mcp_server.client import call_mcp_tool
from backend.app.services.llm_service import generate_diagnosis
from backend.app.services.storage_service import save_remediation_audit

class MCPIncidentState(TypedDict):
    incident_id: str
    incident: dict[str, Any]
    logs: list[dict[str, Any]]
    runbooks: list[dict[str, Any]]
    approval: dict[str, Any]
    diagnosis: dict[str, Any]
    error: str
    remediation_allowed: bool
    workflow_status: str
    remediation_result: dict
    audit_record: dict


def extract_tool_result(result):
    if result.isError:
        raise RuntimeError("MCP tool execution failed.")

    for item in result.content:
        if hasattr(item, "text"):
            return json.loads(item.text)

    return {}


def normalize_list(data):
    """Ensure MCP results are represented as lists."""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


async def retrieve_incident_context(state: MCPIncidentState):
    incident_id = state["incident_id"]

    incident_result = await call_mcp_tool(
        "get_incident_details",
        {"incident_id": incident_id},
    )
    incident = extract_tool_result(incident_result)

    if "error" in incident:
        return {"error": incident["error"]}

    logs_result = await call_mcp_tool(
       "get_recent_logs",
    {
        "limit": 20,
        "incident_id": state["incident_id"],
    },
)
    logs = normalize_list(extract_tool_result(logs_result))

    runbooks_result = await call_mcp_tool(
        "search_runbooks",
        {
            "query": incident.get("title", ""),
            "top_k": 3,
        },
    )
    runbooks = normalize_list(extract_tool_result(runbooks_result))

    approval_result = await call_mcp_tool(
        "get_approval_status",
        {"incident_id": incident_id},
    )
    approval = extract_tool_result(approval_result)

    return {
        "incident": incident,
        "logs": logs,
        "runbooks": runbooks,
        "approval": approval,
        "error": "",
    }



def generate_ai_diagnosis(state: MCPIncidentState):
    """Generate an AI diagnosis using Groq and MCP context."""

    incident = state["incident"]
    runbooks = state["runbooks"]
    approval = state["approval"]

    if not incident:
        return {
            "error": "Incident not found.",
            "diagnosis": {},
        }

    ai_analysis = generate_diagnosis(
        incident=incident,
        recommendations=runbooks,
    )

    approval_status = approval.get(
        "status",
        "PENDING_HUMAN_APPROVAL"
    )

    if approval_status == "APPROVED":
        diagnosis_status = "APPROVED"
    elif approval_status == "REJECTED":
        diagnosis_status = "REJECTED"
    else:
        diagnosis_status = "PENDING_HUMAN_APPROVAL"

    diagnosis = {
        "summary": incident.get("title"),
        "severity": incident.get("severity"),
        "evidence": [
            runbook.get("source", "Unknown")
            for runbook in runbooks
        ],
        "ai_analysis": ai_analysis,
        "approval_required": True,
        "status": diagnosis_status,
    }

    return {
        "diagnosis": diagnosis,
        "error": "",
    }


def check_human_approval(state: MCPIncidentState):
    """Verify human approval before allowing remediation."""

    approval_status = state["approval"].get(
        "status",
        "PENDING_HUMAN_APPROVAL"
    )

    if approval_status == "APPROVED":
        return {
            "remediation_allowed": True,
            "workflow_status": "READY_FOR_REMEDIATION",
        }

    if approval_status == "REJECTED":
        return {
            "remediation_allowed": False,
            "workflow_status": "BLOCKED_REJECTED",
        }

    return {
        "remediation_allowed": False,
        "workflow_status": "BLOCKED_PENDING_APPROVAL",
    }


def route_after_approval(state: MCPIncidentState):
    if state["remediation_allowed"]:
        return "approved"

    return "blocked"


def approved_gate(state: MCPIncidentState):
    print("Human approval granted. Starting remediation simulation.")

    result = execute_remediation(
        incident=state["incident"],
        remediation_allowed=True,
    )

    audit = save_remediation_audit(
        incident_id=state["incident_id"],
        action=result.get("action", "unknown"),
        approval_decision="APPROVED",
        result=result,
    )

    return {
        "remediation_result": result,
        "audit_record": audit,
    }
def blocked_gate(state: MCPIncidentState):
    print("Remediation blocked.")

    result = execute_remediation(
        incident=state["incident"],
        remediation_allowed=False,
    )

    audit = save_remediation_audit(
        incident_id=state["incident_id"],
        action="restart_service",
        approval_decision=state["approval"].get(
            "status",
            "PENDING_HUMAN_APPROVAL",
        ),
        result=result,
    )

    return {
        "remediation_result": result,
        "audit_record": audit,
    }


builder = StateGraph(MCPIncidentState)

builder.add_node(
    "retrieve_incident_context",
    retrieve_incident_context,
)

builder.add_node(
    "generate_ai_diagnosis",
    generate_ai_diagnosis,
)

builder.add_node(
    "check_human_approval",
    check_human_approval,
)

builder.add_node("approved_gate", approved_gate)
builder.add_node("blocked_gate", blocked_gate)

builder.add_edge(START, "retrieve_incident_context")

builder.add_edge(
    "retrieve_incident_context",
    "generate_ai_diagnosis",
)

builder.add_edge(
    "generate_ai_diagnosis",
    "check_human_approval",
)

builder.add_conditional_edges(
    "check_human_approval",
    route_after_approval,
    {
        "approved": "approved_gate",
        "blocked": "blocked_gate",
    },
)

builder.add_edge("approved_gate", END)
builder.add_edge("blocked_gate", END)

mcp_incident_graph = builder.compile()


async def analyze_with_mcp(incident_id: str):
    return await mcp_incident_graph.ainvoke({
        "remediation_allowed": False,
        "workflow_status": "NOT_CHECKED",
        "incident_id": incident_id,
        "incident": {},
        "logs": [],
        "runbooks": [],
        "approval": {},
        "diagnosis": {},
        "remediation_result": {},
        "audit_record": {},
        "error": "",
    })
