# IP Address Logging Fix for Kubernetes

## Problem

When running MBASIC web UI in a Kubernetes cluster behind an ingress controller:
- IP addresses logged to MySQL were always the ingress controller's IP (e.g., `10.244.0.5`)
- This happened because the code was using `request.client.host` which gives the TCP connection IP
- In Kubernetes, all traffic comes through the ingress controller, so all IPs were the same

## Solution

Extract the real client IP from the `X-Forwarded-For` HTTP header:
- Ingress controllers and reverse proxies add this header containing the original client IP
- Format: `X-Forwarded-For: client_ip, proxy1_ip, proxy2_ip`
- The first IP in the list is the original client

## Implementation

### Files Changed

1. **src/bot_protection.py** (already existed)
   - Contains `get_client_ip()` method that properly extracts IP from X-Forwarded-For header
   - Falls back to `request.client.host` if header is not present

2. **src/ui/web/nicegui_backend.py** (fixed)
   - Added import: `from src.bot_protection import get_bot_protection`
   - Fixed `start_ide_session()` (line ~3878):
     - Before: `ip = context.client.request.client.host`
     - After: Uses `bot_protection.get_client_ip(context.client.request)`
   - Fixed `track_visit()` endpoint (line ~4009):
     - Before: Passed `None` for IP address
     - After: Uses `bot_protection.get_client_ip(context.client.request)`

3. **tests/test_ip_logging.py** (new)
   - Comprehensive test suite for IP extraction
   - Tests single IP, multiple IPs, IPv6, empty header, fallback behavior
   - Tests Kubernetes ingress scenario specifically

### Code Changes

#### Before (line 3875)
```python
ip = context.client.request.client.host if context.client and context.client.request and context.client.request.client else None
tracker.start_ide_session(session_id, user_agent, ip)
```

#### After (line 3877-3879)
```python
# Get real client IP from X-Forwarded-For header (for Kubernetes ingress)
bot_protection = get_bot_protection()
ip = bot_protection.get_client_ip(context.client.request) if context.client and context.client.request else None
tracker.start_ide_session(session_id, user_agent, ip)
```

#### Before (line 4007)
```python
# Note: IP extraction handled in tracker, pass None for now
tracker.track_page_visit(page, referrer, userAgent, None, sessionId)
```

#### After (line 4007-4010)
```python
# Get real client IP from X-Forwarded-For header (for Kubernetes ingress)
from nicegui import context
bot_protection = get_bot_protection()
ip = bot_protection.get_client_ip(context.client.request) if context.client and context.client.request else None
tracker.track_page_visit(page, referrer, userAgent, ip, sessionId)
```

## Testing

Run the test suite:
```bash
python3 -m unittest tests.test_ip_logging -v
```

All tests pass:
- ✓ Single IP extraction
- ✓ Multiple IPs (takes first)
- ✓ IPv6 support
- ✓ Empty header fallback
- ✓ Kubernetes ingress scenario

## Deployment

### Current State
- **dev branch**: Contains the fix (this commit)
- **main branch**: Deployed to Kubernetes, does NOT have the fix yet

### Merge Strategy

1. **Merge to main**:
   ```bash
   git checkout main
   git merge dev
   ```

2. **Deploy to Kubernetes**:
   - Push to main branch
   - Kubernetes deployment will automatically pick up the changes
   - No configuration changes needed (X-Forwarded-For is already set by ingress)

3. **Verify in production**:
   - Check MySQL logs to ensure IP addresses are diverse (not all the same)
   - Example query:
     ```sql
     SELECT DISTINCT ip_address, COUNT(*) as count
     FROM page_visits
     WHERE timestamp > NOW() - INTERVAL 1 HOUR
     GROUP BY ip_address;
     ```

## Notes

- No configuration changes required
- X-Forwarded-For header is automatically added by ingress controllers
- Falls back gracefully to direct IP if header is missing (e.g., local development)
- Handles IPv4, IPv6, and multiple proxy chains correctly
- The `bot_protection.py` module was already properly implemented; we just needed to use it

## Related Files

- `src/bot_protection.py:181-197` - IP extraction implementation
- `src/usage_tracker.py` - Usage tracking database operations
- `deployment/k8s_templates/mbasic-configmap.yaml` - Kubernetes configuration
- `docs/dev/KUBERNETES_DEPLOYMENT_SETUP.md` - Deployment documentation
