from datetime import datetime
import uuid

from backend.app.core.database import SessionLocal
from backend.app.models import (
    Log,
    Incident,
    IncidentApproval,
    RemediationAudit,
)

def save_logs(logs):
    db = SessionLocal()
    try:
        for item in logs:
            item = item.copy()

            if isinstance(item.get("timestamp"), str):
                item["timestamp"] = datetime.fromisoformat(
                    item["timestamp"]
                )

            db.add(Log(**item))

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



def get_logs(limit=50, incident_id=None):
    db = SessionLocal()

    try:
        query = db.query(Log)

        if incident_id:
            incident = (
                db.query(Incident)
                .filter(Incident.id == incident_id)
                .first()
            )

            if incident:
                source_log_id = None

                marker = "Source log ID: "

                if incident.description and marker in incident.description:
                    source_log_id = (
                        incident.description
                        .split(marker, 1)[1]
                        .split(".", 1)[0]
                        .strip()
                    )

                if source_log_id:
                    query = query.filter(Log.id == source_log_id)
                else:
                    query = query.filter(
                        Log.service == incident.service
                    )

        rows = (
            query.order_by(Log.timestamp.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat()
                if log.timestamp else None,
                "service": log.service,
                "level": log.level,
                "message": log.message,
                "is_anomaly": log.is_anomaly,
                "anomaly_type": log.anomaly_type,
            }
            for log in rows
        ]

    finally:
        db.close()



def save_incident(incident):
    db = SessionLocal()
    try:
        db.add(Incident(**incident))
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_incidents(limit=50):
    db = SessionLocal()
    try:
        rows = (
            db.query(Incident)
            .order_by(Incident.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": incident.id,
                "service": incident.service,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity,
                "status": incident.status,
                "created_at": incident.created_at.isoformat()
                if incident.created_at else None,
            }
            for incident in rows
        ]
    finally:
        db.close()

def create_incidents_from_anomalies(anomalies):
    db = SessionLocal()
    created = []
    skipped = 0

    severity_map = {
        "CRITICAL": "CRITICAL",
        "ERROR": "HIGH",
        "WARNING": "MEDIUM",
        "INFO": "LOW",
    }

    try:
        for anomaly in anomalies:
            service = anomaly["service"]
            anomaly_type = (
                anomaly.get("anomaly_type")
                or anomaly["message"]
            )

            title = f"{anomaly_type.replace('_', ' ').title()} detected"

            # Avoid creating a duplicate open incident
            existing = (
                db.query(Incident)
                .filter(
                    Incident.service == service,
                    Incident.title == title,
                    Incident.status == "OPEN",
                )
                .first()
            )

            if existing:
                skipped += 1
                continue

            incident = Incident(
                id=str(uuid.uuid4()),
                service=service,
                title=title,
                description=(
                    f"Detected anomaly: {anomaly['message']}. "
                    f"Log level: {anomaly['level']}. "
                    f"Source log ID: {anomaly['id']}."
                ),
                severity=severity_map.get(
                    anomaly["level"].upper(),
                    "HIGH"
                ),
                status="OPEN",
            )

            db.add(incident)
            db.flush()

            created.append({
                "id": incident.id,
                "service": incident.service,
                "title": incident.title,
                "severity": incident.severity,
                "status": incident.status,
            })

        db.commit()

        return {
            "created": len(created),
            "skipped_duplicates": skipped,
            "incidents": created,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()




def get_incident(incident_id):
    db = SessionLocal()

    try:
        incident = (
            db.query(Incident)
            .filter(Incident.id == incident_id)
            .first()
        )

        if not incident:
            return None

        return {
            "id": incident.id,
            "service": incident.service,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity,
            "status": incident.status,
            "created_at": (
                incident.created_at.isoformat()
                if incident.created_at
                else None
            ),
        }

    finally:
        db.close()



def save_approval_decision(incident_id, decision, comment=None):
    db = SessionLocal()

    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()

        if not incident:
            return None, "Incident not found."

        existing = db.query(IncidentApproval).filter(
            IncidentApproval.incident_id == incident_id
        ).first()

        if existing:
            return None, "A decision has already been recorded."

        approval = IncidentApproval(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            decision=decision,
            comment=comment,
        )

        db.add(approval)
        db.commit()
        db.refresh(approval)

        return {
            "id": approval.id,
            "incident_id": approval.incident_id,
            "decision": approval.decision,
            "comment": approval.comment,
            "decided_at": (
                approval.decided_at.isoformat()
                if approval.decided_at else None
            ),
        }, None

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def get_approval_decision(incident_id):
    db = SessionLocal()

    try:
        approval = db.query(IncidentApproval).filter(
            IncidentApproval.incident_id == incident_id
        ).first()

        if not approval:
            return None

        return {
            "id": approval.id,
            "incident_id": approval.incident_id,
            "decision": approval.decision,
            "comment": approval.comment,
            "decided_at": (
                approval.decided_at.isoformat()
                if approval.decided_at else None
            ),
        }

    finally:
        db.close()



def save_remediation_audit(
    incident_id: str,
    action: str,
    approval_decision: str,
    result: dict,
):
    db = SessionLocal()

    try:
        audit = RemediationAudit(
            incident_id=incident_id,
            action=action,
            approval_decision=approval_decision,
            status=result["status"],
            message=result.get("message"),
            executed=result.get("executed", False),
        )

        db.add(audit)
        db.commit()
        db.refresh(audit)

        return {
            "id": audit.id,
            "incident_id": audit.incident_id,
            "action": audit.action,
            "approval_decision": audit.approval_decision,
            "status": audit.status,
            "executed": audit.executed,
            "created_at": audit.created_at.isoformat(),
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

def get_remediation_audits(incident_id=None, limit=50):
    db = SessionLocal()

    try:
        query = db.query(RemediationAudit)

        if incident_id:
            query = query.filter(
                RemediationAudit.incident_id == incident_id
            )

        rows = (
            query.order_by(RemediationAudit.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": row.id,
                "incident_id": row.incident_id,
                "action": row.action,
                "approval_decision": row.approval_decision,
                "status": row.status,
                "message": row.message,
                "executed": row.executed,
                "created_at": (
                    row.created_at.isoformat()
                    if row.created_at else None
                ),
            }
            for row in rows
        ]

    finally:
        db.close()