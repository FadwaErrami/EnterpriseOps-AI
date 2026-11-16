
import random
import uuid
from datetime import datetime, timezone

SERVICES = ["api-gateway", "payment-service", "database", "auth-service"]

NORMAL_MESSAGES = [
    "Request processed successfully",
    "User authenticated successfully",
    "Database query completed",
    "Payment processed successfully",
    "Health check completed",
    "Cache response returned",
]

ANOMALIES = [
    ("HIGH_CPU", "CPU usage exceeded 95%"),
    ("DATABASE_ERROR", "Database connection pool exhausted"),
    ("HIGH_LATENCY", "Request latency exceeded 5000ms"),
    ("MEMORY_ERROR", "Memory usage reached critical threshold"),
    ("SERVICE_FAILURE", "Service returned repeated 503 errors"),
]

logs_store = []


def generate_log(force_anomaly=False):
    is_anomaly = force_anomaly or random.random() < 0.12

    if is_anomaly:
        anomaly_type, message = random.choice(ANOMALIES)
        level = random.choice(["ERROR", "CRITICAL"])
    else:
        anomaly_type = None
        message = random.choice(NORMAL_MESSAGES)
        level = random.choices(
            ["INFO", "WARNING"],
            weights=[0.9, 0.1]
        )[0]

    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": random.choice(SERVICES),
        "level": level,
        "message": message,
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type,
    }


def simulate_logs(count=20):
    generated_logs = [generate_log() for _ in range(count)]
    logs_store.extend(generated_logs)
    return generated_logs


def get_recent_logs(limit=50):
    return logs_store[-limit:][::-1]
