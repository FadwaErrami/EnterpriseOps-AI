
# High CPU Usage

## Symptoms
- CPU usage exceeds 95%.
- API requests become slow.
- Services may become unavailable.

## Possible causes
- Excessive traffic.
- Infinite loops or inefficient code.
- Too many concurrent processes.
- Background jobs consuming resources.

## Investigation
1. Check CPU usage by process.
2. Identify the process consuming the most CPU.
3. Inspect application logs around the incident timestamp.
4. Check recent deployments and traffic spikes.

## Recommended remediation
1. Notify the operations team.
2. Restart the affected process only after identifying the cause.
3. Scale the service if traffic exceeds capacity.
4. Optimize the problematic code or background task.
5. Monitor CPU usage after remediation.

## Severity
HIGH or CRITICAL depending on service impact.
