
from sqlalchemy import Column, String, DateTime, Boolean, Text
from datetime import datetime, timezone
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text

from backend.app.core.database import Base


class Log(Base):
    __tablename__ = "logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    service = Column(String, nullable=False)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_anomaly = Column(Boolean, default=False)
    anomaly_type = Column(String, nullable=True)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    service = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, default="HIGH")
    status = Column(String, default="OPEN")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class IncidentApproval(Base):
    __tablename__ = "incident_approvals"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )
    decision = Column(String, nullable=False)  # APPROVED or REJECTED
    comment = Column(Text, nullable=True)
    decided_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

class RemediationAudit(Base):
    __tablename__ = "remediation_audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)
    approval_decision = Column(String, nullable=False)
    status = Column(String, nullable=False)
    message = Column(Text, nullable=True)
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)