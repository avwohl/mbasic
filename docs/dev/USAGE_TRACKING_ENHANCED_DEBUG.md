# Usage Tracking Enhanced Debug - Changes Made

## Problem
MySQL usage tracking tables remained empty despite configuration being correct. Root cause: Silent failures with no visibility into what was failing.

## Changes Made (v1.0.892)

### 1. Enhanced Logging in `src/usage_tracker.py`

**Added comprehensive logging to initialization:**
- ✅ Log connection method (unix socket vs TCP)
- ✅ Log host/port/user being used
- ✅ Log SSL configuration
- ✅ Execute test query (`SELECT 1`) after connection
- ✅ Verify tables exist (`SHOW TABLES LIKE 'page_visits'`)
- ✅ Log full traceback on failures
- ✅ Log connection parameters (without password) on error

**Added detailed query logging:**
- ✅ Log successful queries at DEBUG level with lastrowid
- ✅ Log failed queries at ERROR level with query text and params
- ✅ Log reconnection attempts

**Added timeout:**
- ✅ Set `connection_timeout=10` to fail fast on connection issues

### 2. Enhanced Health Check in `src/ui/web/nicegui_backend.py`

**Added usage tracking check to `/health` endpoint:**
```python
health_status['checks']['mysql_usage_tracking'] = 'ok' | 'disabled' | 'failed' | 'no connection'
```

**Health endpoint now checks:**
- Error logging MySQL (existing)
- Usage tracking MySQL (NEW)

**Health check will return 503 if usage tracking fails** (if enabled)

### 3. Configure Python Logging

**Added logging configuration at startup:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
```

**All logger messages now visible in:**
- kubectl logs
- Docker logs
- stderr output

### 4. Startup Verification Messages

**Clear success/failure indication:**
```
=== Initializing Usage Tracking ===
[timestamp] - src.usage_tracker - INFO - Usage tracking: Connecting to mysql:3306 as root
[timestamp] - src.usage_tracker - INFO - Usage tracking: SSL disabled for MySQL connection
[timestamp] - src.usage_tracker - INFO - Usage tracking: Attempting to connect to database 'mbasic_logs'...
[timestamp] - src.usage_tracker - INFO - ✓ Usage tracking database connection established successfully
[timestamp] - src.usage_tracker - INFO - ✓ Usage tracking database test query successful
[timestamp] - src.usage_tracker - INFO - ✓ Usage tracking tables verified
✓ Usage tracking enabled and connected
```

**Or on failure:**
```
[timestamp] - src.usage_tracker - ERROR - ✗ Failed to initialize usage tracking database: [error details]
[timestamp] - src.usage_tracker - ERROR -   Connection details: host=mysql, port=3306, database=mbasic_logs, user=root
[timestamp] - src.usage_tracker - ERROR -   Usage tracking will be DISABLED
[timestamp] - src.usage_tracker - ERROR -   Full traceback: [full stack trace]
✗ Usage tracking FAILED to initialize (check logs above)
```

## How to Debug

### 1. Check Pod Logs

```bash
# Get pod name
kubectl get pods -n mbasic -l app=mbasic-web

# Check logs for usage tracking initialization
kubectl logs -n mbasic <pod-name> | grep -A 20 "Initializing Usage Tracking"

# Check for any errors
kubectl logs -n mbasic <pod-name> | grep "Usage tracking"
```

**What to look for:**
- ✓ Connection details (host, port, user, database)
- ✓ SSL configuration
- ✓ Test query results
- ✓ Table verification
- ✗ Error messages with full traceback
- ✗ Connection failures

### 2. Check Health Endpoint

```bash
# From outside cluster
curl https://mbasic.awohl.com/health

# From inside cluster (port-forward)
kubectl port-forward -n mbasic deployment/mbasic-web 8080:8080
curl http://localhost:8080/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "1.0.892",
  "checks": {
    "mysql_error_logging": "ok",
    "mysql_usage_tracking": "ok"
  }
}
```

**If usage tracking fails:**
```json
{
  "status": "degraded",
  "version": "1.0.892",
  "checks": {
    "mysql_error_logging": "ok",
    "mysql_usage_tracking": "failed: 2003 Can't connect to MySQL server on 'mysql:3306' (111 Connection refused)"
  }
}
```

### 3. Test Database Connection from Pod

```bash
# Execute into pod
kubectl exec -it -n mbasic deployment/mbasic-web -- /bin/bash

# Test MySQL connection
python3 -c "
import mysql.connector
import os
try:
    conn = mysql.connector.connect(
        host=os.environ['MYSQL_HOST'],
        port=3306,
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        database='mbasic_logs',
        connection_timeout=10
    )
    print('✓ Connection successful')
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    print('✓ Query successful')
    cursor.execute('SHOW TABLES')
    print('Tables:', [row[0] for row in cursor.fetchall()])
    conn.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
    import traceback
    traceback.print_exc()
"
```

### 4. Check MySQL from MySQL Pod

```bash
# Get MySQL pod name
kubectl get pods -n mbasic | grep mysql

# Connect to MySQL
kubectl exec -it -n mbasic <mysql-pod-name> -- mysql -u root -p

# Check database and tables
USE mbasic_logs;
SHOW TABLES;
SELECT COUNT(*) FROM page_visits;
SELECT COUNT(*) FROM ide_sessions;
SELECT COUNT(*) FROM program_executions;
SELECT COUNT(*) FROM feature_usage;

# Check recent data
SELECT * FROM page_visits ORDER BY timestamp DESC LIMIT 5;
SELECT * FROM ide_sessions ORDER BY start_time DESC LIMIT 5;
```

### 5. Check Environment Variables

```bash
# Check if MySQL credentials are set
kubectl exec -n mbasic deployment/mbasic-web -- printenv | grep MYSQL

# Should show:
# MYSQL_HOST=<mysql-service-name>
# MYSQL_USER=root
# MYSQL_PASSWORD=<password>
```

### 6. Check ConfigMap

```bash
# View ConfigMap
kubectl get configmap -n mbasic mbasic-config -o yaml

# Check that usage_tracking.enabled = true
# Check that ${MYSQL_HOST} etc are being substituted
```

## Common Issues and Solutions

### Issue 1: "Can't connect to MySQL server (111 Connection refused)"
**Cause:** MySQL service not running or wrong host
**Solution:**
```bash
kubectl get svc -n mbasic | grep mysql
kubectl get pods -n mbasic | grep mysql
```

### Issue 2: "Access denied for user 'root'@'%'"
**Cause:** Wrong password or user doesn't have permissions
**Solution:** Check secrets, verify MySQL user has permissions

### Issue 3: "Unknown database 'mbasic_logs'"
**Cause:** Database not created
**Solution:** Run schema creation script

### Issue 4: "Table 'page_visits' doesn't exist"
**Cause:** Schema not created or partially created
**Solution:**
```bash
kubectl exec -it -n mbasic <mysql-pod> -- mysql -u root -p mbasic_logs < deployment/sql/usage_tracking_schema.sql
```

### Issue 5: "usage_tracking: 'not initialized'"
**Cause:** UsageTracker not initialized at startup
**Solution:** Check multiuser.json config file is mounted correctly

### Issue 6: "usage_tracking: 'disabled'"
**Cause:** `enabled: false` in config or initialization failed
**Solution:** Check pod logs for error messages during startup

## Testing After Fix

### 1. Check pod starts cleanly
```bash
kubectl logs -n mbasic deployment/mbasic-web --tail=50
```
Look for:
```
=== Initializing Usage Tracking ===
✓ Usage tracking enabled and connected
```

### 2. Check health endpoint
```bash
curl https://mbasic.awohl.com/health | jq '.checks'
```
Should show:
```json
{
  "mysql_error_logging": "ok",
  "mysql_usage_tracking": "ok"
}
```

### 3. Visit the site
```bash
# Open browser to https://mbasic.awohl.com
# Run a program
```

### 4. Check database has data
```bash
kubectl exec -it -n mbasic <mysql-pod> -- mysql -u root -p -e \
  "SELECT COUNT(*) FROM mbasic_logs.page_visits; \
   SELECT COUNT(*) FROM mbasic_logs.ide_sessions; \
   SELECT COUNT(*) FROM mbasic_logs.program_executions;"
```

Should show non-zero counts!

## Expected Log Output (Success)

```
=== Initializing Usage Tracking ===
2025-11-12 22:30:15,123 - src.usage_tracker - INFO - Usage tracking: Connecting to mysql-service:3306 as root
2025-11-12 22:30:15,124 - src.usage_tracker - INFO - Usage tracking: SSL disabled for MySQL connection
2025-11-12 22:30:15,125 - src.usage_tracker - INFO - Usage tracking: Attempting to connect to database 'mbasic_logs'...
2025-11-12 22:30:15,250 - src.usage_tracker - INFO - ✓ Usage tracking database connection established successfully
2025-11-12 22:30:15,255 - src.usage_tracker - INFO - ✓ Usage tracking database test query successful
2025-11-12 22:30:15,260 - src.usage_tracker - INFO - ✓ Usage tracking tables verified
✓ Usage tracking enabled and connected
```

## Expected Log Output (Failure)

```
=== Initializing Usage Tracking ===
2025-11-12 22:30:15,123 - src.usage_tracker - INFO - Usage tracking: Connecting to mysql-service:3306 as root
2025-11-12 22:30:15,124 - src.usage_tracker - INFO - Usage tracking: SSL disabled for MySQL connection
2025-11-12 22:30:15,125 - src.usage_tracker - INFO - Usage tracking: Attempting to connect to database 'mbasic_logs'...
2025-11-12 22:30:25,126 - src.usage_tracker - ERROR - ✗ Failed to initialize usage tracking database: 2003 (HY000): Can't connect to MySQL server on 'mysql-service:3306' (111 Connection refused)
2025-11-12 22:30:25,127 - src.usage_tracker - ERROR -   Connection details: host=mysql-service, port=3306, database=mbasic_logs, user=root
2025-11-12 22:30:25,128 - src.usage_tracker - ERROR -   Usage tracking will be DISABLED
2025-11-12 22:30:25,129 - src.usage_tracker - ERROR -   Full traceback: Traceback (most recent call last):
  File "/app/src/usage_tracker.py", line 67, in _init_db_connection
    self.db_connection = mysql.connector.connect(**conn_params)
  ... [full stack trace] ...
✗ Usage tracking FAILED to initialize (check logs above)
```

## Files Modified
- `src/usage_tracker.py` - Enhanced logging and verification
- `src/ui/web/nicegui_backend.py` - Health check and logging config

## Next Steps

1. **Rebuild and deploy:**
   ```bash
   # Build new image
   docker build -t registry.digitalocean.com/awohl-mbasic/mbasic-web:latest .
   docker push registry.digitalocean.com/awohl-mbasic/mbasic-web:latest

   # Restart pods to pull new image
   kubectl rollout restart deployment/mbasic-web -n mbasic

   # Watch rollout
   kubectl rollout status deployment/mbasic-web -n mbasic
   ```

2. **Check logs immediately:**
   ```bash
   kubectl logs -n mbasic deployment/mbasic-web --tail=100 | grep -A 20 "Initializing Usage Tracking"
   ```

3. **Check health:**
   ```bash
   curl https://mbasic.awohl.com/health | jq
   ```

4. **Test tracking:**
   - Visit site
   - Run a program
   - Check database for data

With these changes, you'll now see exactly what's happening and why usage tracking is working or failing!
