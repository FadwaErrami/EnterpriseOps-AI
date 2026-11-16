
# High Request Latency

## Symptoms
- Request latency exceeds 5000ms.
- API responses are slow.
- Users experience timeouts.

## Possible causes
- Slow database queries.
- Network problems.
- High CPU or memory usage.
- External API delays.

## Investigation
1. Check API response times.
2. Inspect application logs.
3. Measure database query duration.
4. Check network connectivity.
5. Identify slow external dependencies.

## Recommended remediation
1. Identify the slowest component.
2. Optimize database queries when necessary.
3. Investigate network and external API delays.
4. Scale the affected service if resources are insufficient.
5. Monitor response times after remediation.

## Severity
HIGH or CRITICAL depending on service impact.
