# Usage Tracking Debug Report

## Problem
MySQL database tables remain empty - no usage tracking data is being recorded from Kubernetes deployment.

## Investigation Results

### Configuration ✅
**Kubernetes ConfigMap** (`deployment/k8s_templates/mbasic-configmap.yaml`):
```json
"usage_tracking": {
  "enabled": true,
  "mysql": {
    "host": "${MYSQL_HOST}",
    "port": 3306,
    "user": "${MYSQL_USER}",
    "password": "${MYSQL_PASSWORD}",
    "database": "mbasic_logs",
    "disable_ssl": true
  }
}
```
✅ Configuration looks correct

### Environment Variables ✅
**Deployment** (`deployment/k8s_templates/mbasic-deployment.yaml`):
- MYSQL_HOST - from secrets
- MYSQL_USER - from secrets
- MYSQL_PASSWORD - from secrets

✅ Environment variables properly configured from Kubernetes secrets

### Dependencies ✅
**requirements.txt**:
```
mysql-connector-python>=8.0
```
✅ MySQL connector is installed in Docker image

### Code Integration ✅
**Web backend** (`src/ui/web/nicegui_backend.py`):
- Line 3811-3818: Initializes UsageTracker from config
- Line 3852-3862: Tracks IDE session start
- Line 1187: Tracks program execution

✅ Tracking code is integrated

### Usage Tracker Implementation ✅
**`src/usage_tracker.py`**:
- Implements all tracking methods
- Has error handling with logging
- Connects to MySQL on initialization

✅ Implementation looks correct

## Suspected Issues

### 1. Silent Failures
The usage tracker catches exceptions and logs to `logger.error()` but:
- Logging might not be configured properly in production
- stderr writes may not appear in Kubernetes logs
- Errors are silently swallowed with `self.enabled = False`

### 2. Logging Visibility
The initialization logs to `sys.stderr`:
```python
sys.stderr.write("Usage tracking enabled\n")
```

But these may not be visible in kubectl logs if stderr is not captured.

### 3. Database Connection Errors
Possible connection issues:
- SSL certificate verification (though `disable_ssl: true` is set)
- Network connectivity to MySQL service
- MySQL credentials invalid
- Database/tables don't exist
- Connection timeout

### 4. No Health Check
The health check endpoint (`/health`) checks MySQL for error logging but **not** for usage tracking:
```python
# Only checks error_logging_backend, not usage tracker!
if hasattr(multiuser_backend, 'error_logging_backend'):
    ...
```

## Recommended Fixes

### 1. Enhanced Logging
Add explicit logging to Python's logging system (not just stderr):
- Log usage tracker initialization success/failure at INFO level
- Log each tracking attempt (at DEBUG level)
- Log connection parameters (without passwords)
- Add logging configuration to NiceGUI app

### 2. Health Check Enhancement
Add usage tracker health check to `/health` endpoint:
```python
# Check usage tracking
tracker = get_usage_tracker()
if tracker and tracker.enabled:
    try:
        # Test connection
        tracker._execute_query("SELECT 1", ())
    except Exception as e:
        health_details["usage_tracking"] = "unhealthy"
```

### 3. Startup Verification
Add verification on startup:
- Test database connection immediately after init
- Log connection success/failure
- Try a test INSERT to verify write permissions
- Check that tables exist

### 4. Better Error Messages
Instead of silently disabling on error:
```python
except Exception as e:
    logger.error(f"Failed to initialize usage tracking: {e}")
    logger.error(f"Connection params: host={host}, port={port}, database={db}")
    self.enabled = False
```

Add detailed error information that helps diagnose the problem.

## Next Steps

1. **Add comprehensive logging** - Make sure all initialization and tracking attempts are logged
2. **Check pod logs** - `kubectl logs -n mbasic <pod-name>` to see what's actually happening
3. **Verify MySQL connectivity** - Test connection from within a pod
4. **Check database/tables exist** - Verify schema was created
5. **Test locally** - Try usage tracking on local dev environment with MySQL

## Testing Plan

### Local Test
1. Set up local MySQL with mbasic_logs database
2. Run schema creation script
3. Configure multiuser.json with local MySQL
4. Start web UI and verify tracking works
5. Check tables have data

### Kubernetes Test
1. Port-forward to MySQL pod to test connectivity
2. Check pod logs for initialization messages
3. Test health endpoint
4. Manually INSERT test data to verify permissions
5. Check application logs for tracking attempts

## Files to Check
- Pod logs: `kubectl logs -n mbasic deployment/mbasic-web`
- MySQL connectivity: `kubectl exec -n mbasic -it <mysql-pod> -- mysql -u root -p`
- Tables: `SHOW TABLES; SELECT * FROM page_visits;`
- Secrets: `kubectl get secret -n mbasic mbasic-secrets -o yaml`
