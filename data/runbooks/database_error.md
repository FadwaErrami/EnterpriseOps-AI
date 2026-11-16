
# Database Connection Pool Exhausted

## Symptoms
- Database connection pool exhausted.
- Database queries fail.
- API requests return errors or time out.

## Possible causes
- Too many concurrent database requests.
- Connections are not properly closed.
- Database server overload.
- Connection pool configured with insufficient capacity.

## Investigation
1. Check active database connections.
2. Inspect connection pool utilization.
3. Identify long-running database queries.
4. Check database server health.
5. Review application connection management.

## Recommended remediation
1. Identify and terminate abandoned connections when safe.
2. Verify that application connections are properly released.
3. Optimize slow database queries.
4. Adjust connection pool capacity if necessary.
5. Monitor database connections after remediation.

## Severity
HIGH or CRITICAL depending on service impact.
