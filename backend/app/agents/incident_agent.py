
from typing import TypedDict, Optional
from backend.app.services.llm_service import generate_diagnosis

from langgraph.graph import StateGraph, START, END

from backend.app.services.storage_service import get_incident
from backend.app.services.rag_service import rag_service


class IncidentState(TypedDict):
    incident_id: str
    incident: Optional[dict]
    recommendations: list
    diagnosis: Optional[dict]
    error: Optional[str]


def load_incident(state: IncidentState):
    incident = get_incident(state["incident_id"])

    if not incident:
        return {
            "incident": None,
            "error": "Incident not found."
        }

    return {"incident": incident, "error": None}


def retrieve_runbooks(state: IncidentState):
    incident = state["incident"]

    query = (
        f"{incident['title']} "
        f"{incident['description']} "
        f"{incident['service']}"
    )

    recommendations = rag_service.search(query=query, top_k=3)

    return {"recommendations": recommendations}



def diagnose_incident(state: IncidentState):
    incident = state["incident"]
    recommendations = state["recommendations"]

    if not incident:
        return {"diagnosis": None}

    # Generate an AI diagnosis using Groq
    ai_analysis = generate_diagnosis(
        incident=incident,
        recommendations=recommendations
    )

    diagnosis = {
        "summary": f"AI diagnosis for {incident['title']}",
        "severity": incident["severity"],
        "probable_cause": (
            recommendations[0]["source"]
            if recommendations
            else "Unknown"
        ),
        "evidence": [
            item["source"] for item in recommendations
        ],
        "ai_analysis": ai_analysis,
        "approval_required": True,
        "status": "PENDING_HUMAN_APPROVAL"
    }

    return {"diagnosis": diagnosis}


def build_incident_agent():
    workflow = StateGraph(IncidentState)

    workflow.add_node("load_incident", load_incident)
    workflow.add_node("retrieve_runbooks", retrieve_runbooks)
    workflow.add_node("diagnose_incident", diagnose_incident)

    workflow.add_edge(START, "load_incident")

    workflow.add_conditional_edges(
        "load_incident",
        lambda state: (
            "retrieve_runbooks"
            if state["incident"] is not None
            else END
        ),
        {
            "retrieve_runbooks": "retrieve_runbooks",
            END: END
        }
    )

    workflow.add_edge("retrieve_runbooks", "diagnose_incident")
    workflow.add_edge("diagnose_incident", END)

    return workflow.compile()


incident_agent = build_incident_agent()


def analyze_incident(incident_id: str):
    initial_state = {
        "incident_id": incident_id,
        "incident": None,
        "recommendations": [],
        "diagnosis": None,
        "error": None
    }

    return incident_agent.invoke(initial_state)
