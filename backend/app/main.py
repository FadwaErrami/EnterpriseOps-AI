
from backend.app.ml.anomaly_detector import detector
from backend.app.services.rag_service import rag_service
from backend.app.agents.incident_agent import analyze_incident
from fastapi import FastAPI, Query
from backend.app.core.database import Base, engine
from fastapi import HTTPException
from pydantic import BaseModel
from backend.app.services.storage_service import (
    get_remediation_audits,
)

from backend.app.services.storage_service import (
    save_approval_decision,
    get_approval_decision,
)
from backend.app.services.storage_service import (
    save_logs,
    get_logs,
    get_incidents,
    get_incident,
    create_incidents_from_anomalies,
)
from backend.app.services.log_service import simulate_logs
from backend.app.services.storage_service import (
    save_logs,
    get_logs,
    get_incidents,
    create_incidents_from_anomalies,
)
from backend.app.services.storage_service import (
    save_logs,
    get_logs,
    get_incidents,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EnterpriseOps AI",
    description="AI-powered IT Operations and Incident Management Platform",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to EnterpriseOps AI",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/logs/simulate")
def generate_logs(count: int = Query(default=20, ge=1, le=1000)):
    logs = simulate_logs(count)
    save_logs(logs)

    return {
        "generated": len(logs),
        "message": "Logs generated and saved successfully",
    }


@app.get("/logs")
def list_logs(limit: int = Query(default=50, ge=1, le=1000)):
    logs = get_logs(limit)

    return {
        "total": len(logs),
        "logs": logs,
    }


@app.get("/incidents")
def list_incidents(limit: int = Query(default=50, ge=1, le=1000)):
    incidents = get_incidents(limit)

    return {
        "total": len(incidents),
        "incidents": incidents,
    }



@app.post("/ml/train")
def train_model():
    logs = get_logs(limit=1000)

    if len(logs) < 20:
        return {"error": "Generate at least 20 logs before training."}

    training_data = [
        {
            "level": log["level"],
            "service": log["service"],
            "message": log["message"],
        }
        for log in logs
    ]

    return detector.train(training_data)


@app.post("/ml/detect")
def detect_anomalies():
    logs = get_logs(limit=1000)

    if not logs:
        return {"error": "No logs available."}

    if not detector.is_trained:
        return {"error": "Train the model first using /ml/train."}

    results = detector.predict(logs)

    anomalies = [
        item for item in results
        if item["ml_anomaly"]
    ]

    return {
        "total_logs": len(results),
        "detected_anomalies": len(anomalies),
        "anomalies": anomalies,
    }



@app.post("/incidents/process-anomalies")
def process_anomalies():
    if not detector.is_trained:
        return {
            "error": "Train the model first using /ml/train."
        }

    logs = get_logs(limit=1000)

    if not logs:
        return {"error": "No logs available."}

    results = detector.predict(logs)

    anomalies = [
        item for item in results
        if item["ml_anomaly"]
    ]

    incident_result = create_incidents_from_anomalies(anomalies)

    return {
        "total_logs": len(logs),
        "detected_anomalies": len(anomalies),
        **incident_result,
    }



@app.get("/incidents")
def list_incidents(limit: int = Query(default=50, ge=1, le=1000)):
    incidents = get_incidents(limit)
    return {
        "total": len(incidents),
        "incidents": incidents,
    }


@app.get("/ml/status")
def model_status():
    return {
        "is_trained": detector.is_trained,
        "model_saved": detector.is_trained,
    }



@app.get("/rag/search")
def search_runbooks(
    query: str = Query(min_length=3),
    top_k: int = Query(default=3, ge=1, le=10),
):
    results = rag_service.search(query, top_k)

    return {
        "query": query,
        "results_found": len(results),
        "results": results,
    }





@app.get("/incidents/{incident_id}/recommendations")
def get_incident_recommendations(incident_id: str):

    incident = get_incident(incident_id)

    if not incident:
        return {
            "error": "Incident not found."
        }

    query = (
        f"{incident['title']} "
        f"{incident['description']} "
        f"{incident['service']}"
    )

    recommendations = rag_service.search(
        query=query,
        top_k=2,
    )

    return {
        "incident": {
            "id": incident["id"],
            "title": incident["title"],
            "service": incident["service"],
            "severity": incident["severity"],
            "status": incident["status"],
        },
        "recommendations_found": len(recommendations),
        "recommendations": recommendations,
    }



@app.post("/incidents/{incident_id}/analyze")
def analyze_incident_endpoint(incident_id: str):
    result = analyze_incident(incident_id)

    if result["error"]:
        return {"error": result["error"]}

    return {
        "incident": result["incident"],
        "diagnosis": result["diagnosis"],
    }




class ApprovalRequest(BaseModel):
    comment: str | None = None


@app.post("/incidents/{incident_id}/approve")
def approve_incident(
    incident_id: str,
    payload: ApprovalRequest | None = None,
):
    decision, error = save_approval_decision(
        incident_id=incident_id,
        decision="APPROVED",
        comment=payload.comment if payload else None,
    )

    if error == "Incident not found.":
        raise HTTPException(status_code=404, detail=error)

    if error:
        raise HTTPException(status_code=409, detail=error)

    return {
        "message": "Incident remediation approved.",
        "approval": decision,
    }


@app.post("/incidents/{incident_id}/reject")
def reject_incident(
    incident_id: str,
    payload: ApprovalRequest | None = None,
):
    decision, error = save_approval_decision(
        incident_id=incident_id,
        decision="REJECTED",
        comment=payload.comment if payload else None,
    )

    if error == "Incident not found.":
        raise HTTPException(status_code=404, detail=error)

    if error:
        raise HTTPException(status_code=409, detail=error)

    return {
        "message": "Incident remediation rejected.",
        "approval": decision,
    }


@app.get("/incidents/{incident_id}/approval")
def get_incident_approval(incident_id: str):
    if not get_incident(incident_id):
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    decision = get_approval_decision(incident_id)

    return {
        "incident_id": incident_id,
        "approval": decision,
        "status": (
            decision["decision"]
            if decision
            else "PENDING_HUMAN_APPROVAL"
        ),
    }


@app.get("/incidents/{incident_id}/audit")
def get_incident_audit(
    incident_id: str,
    limit: int = Query(default=50, ge=1, le=500),
):
    incident = get_incident(incident_id)

    if not incident:
        raise HTTPException(
            status_code=404,
            detail="Incident not found.",
        )

    audits = get_remediation_audits(
        incident_id=incident_id,
        limit=limit,
    )

    return {
        "incident_id": incident_id,
        "total": len(audits),
        "audits": audits,
    }
