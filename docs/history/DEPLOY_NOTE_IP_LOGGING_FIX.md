# Deployment Note: Real Client IP Logging Fix

## Changes Made
Fixed MySQL logging to capture real client IP addresses instead of the nginx ingress internal cluster IP.

### Files Modified
- `src/ui/web/nicegui_backend.py`:
  - Added `get_client_ip()` helper function that extracts real client IP from HTTP headers
  - Updated `start_ide_session()` call to use `get_client_ip()` instead of `request.client.host`
  - Updated `/api/track-visit` endpoint to extract and pass real client IP

### How It Works
The new `get_client_ip()` function checks headers in this order:
1. **X-Forwarded-For** - Set by nginx ingress with real client IP (takes first IP in chain)
2. **X-Real-IP** - Alternative header used by some proxies
3. **request.client.host** - Fallback to direct connection IP (will be ingress IP if above headers missing)

## Testing Required

### On Kubernetes Cluster
1. Deploy the updated code to the k8s cluster
2. Visit the web IDE from an external IP
3. Check MySQL logs to verify IP addresses are now showing real client IPs, not 10.x.x.x addresses

### SQL Query to Check
```sql
-- Check recent IDE sessions with IP addresses
SELECT session_id, ip_address, start_time, user_agent
FROM ide_sessions
ORDER BY start_time DESC
LIMIT 20;

-- Check recent page visits with IP addresses
SELECT page_path, ip_address, visit_time, user_agent
FROM page_visits
ORDER BY visit_time DESC
LIMIT 20;
```

### Expected Results
- IP addresses should now show real external IPs (not 10.x.x.x cluster IPs)
- X-Forwarded-For header should be properly parsed
- No errors in application logs

## Nginx Ingress Configuration
Verify that your nginx ingress is configured to pass the X-Forwarded-For header:
```yaml
# Should already be set by default in most ingress controllers
# But verify if issues persist:
nginx.ingress.kubernetes.io/use-forwarded-headers: "true"
```

## Rollback Plan
If issues occur:
```bash
git revert <commit-hash>
# Redeploy previous version
```

## Date
2025-11-13
