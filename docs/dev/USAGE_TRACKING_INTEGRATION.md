# Usage Tracking Integration

## Overview
Custom usage tracking has been added to log website and IDE usage to MySQL database.

## Database Schema
Location: `deployment/sql/usage_tracking_schema.sql`

Tables created:
- `page_visits` - Landing page and site visits
- `ide_sessions` - IDE session tracking with duration
- `program_executions` - Track each program run
- `feature_usage` - Track feature usage (debugger, compiler, etc.)
- `daily_usage_summary` - Aggregated daily statistics

## Setup Instructions

### 1. Create Database Tables
Run on your MySQL server (awohl4 droplet):

```bash
mysql -u mbasic -p < deployment/sql/usage_tracking_schema.sql
```

### 2. Deploy Updated Configuration
The config has already been updated in `deployment/k8s_templates/mbasic-configmap.yaml` with:

```json
"usage_tracking": {
  "enabled": true,
  "mysql": {
    "host": "${MYSQL_HOST}",
    "port": 25060,
    "user": "${MYSQL_USER}",
    "password": "${MYSQL_PASSWORD}",
    "database": "mbasic_logs"
  }
}
```

Apply the updated config:
```bash
kubectl apply -f deployment/k8s_templates/mbasic-configmap.yaml
```

### 3. Code Integration Points

The following integrations need to be added to `src/ui/web/nicegui_backend.py`:

#### A. Import usage tracker (add to imports at top of file)
```python
from src.usage_tracker import init_usage_tracker, get_usage_tracker
```

#### B. Initialize tracker in `start_web_ui()` (before @ui.page decorator)
```python
def start_web_ui(port=8080):
    """Start the NiceGUI web server with per-client backend instances."""
    # ... existing startup logging ...

    # Initialize usage tracking
    import json
    config_path = os.path.join(os.path.dirname(__file__), '../../../config/multiuser.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            multiuser_config = json.load(f)

        # Replace environment variables in config
        config_str = json.dumps(multiuser_config)
        for env_var in ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD']:
            config_str = config_str.replace(f'${{{env_var}}}', os.environ.get(env_var, ''))
        multiuser_config = json.loads(config_str)

        # Initialize usage tracker
        usage_config = multiuser_config.get('usage_tracking', {})
        if usage_config.get('enabled'):
            init_usage_tracker(usage_config)
            sys.stderr.write("Usage tracking enabled\n")
        else:
            sys.stderr.write("Usage tracking disabled\n")

    @ui.page('/', viewport='width=device-width, initial-scale=1.0')
    def main_page():
        # ... rest of function ...
```

#### C. Track IDE session start in `main_page()` (after backend creation)
```python
        # Create new backend instance
        backend = NiceGUIBackend(None, program_manager)

        # Track IDE session start
        tracker = get_usage_tracker()
        if tracker:
            from nicegui import app, context
            session_id = app.storage.client.id
            user_agent = context.client.request.headers.get('user-agent')
            ip = context.client.request.client.host if context.client.request.client else None
            tracker.start_ide_session(session_id, user_agent, ip)
```

#### D. Track session end on disconnect
```python
        # Save state on disconnect
        def save_on_disconnect():
            try:
                app.storage.client['session_state'] = backend.serialize_state()

                # Track session end
                tracker = get_usage_tracker()
                if tracker:
                    tracker.end_ide_session(app.storage.client.id)

            except Exception as e:
                sys.stderr.write(f"Warning: Failed to save final session state: {e}\n")
                sys.stderr.flush()
```

#### E. Track program execution (in the run button handler)
Find the `run_program()` or similar method and add after execution:

```python
        # Track program execution
        tracker = get_usage_tracker()
        if tracker and hasattr(self, '_last_run_stats'):
            tracker.track_program_execution(
                session_id=app.storage.client.id,
                program_lines=self._last_run_stats.get('lines', 0),
                execution_time_ms=self._last_run_stats.get('time_ms', 0),
                lines_executed=self._last_run_stats.get('lines_executed', 0),
                success=self._last_run_stats.get('success', False),
                error_message=self._last_run_stats.get('error')
            )
```

### 4. Landing Page Visit Tracking

Add API endpoint for landing page tracking (in `start_web_ui()` before ui.run()):

```python
    # Landing page visit tracking endpoint
    @app.post('/api/track-visit')
    def track_visit(request: dict):
        """Track landing page visit."""
        tracker = get_usage_tracker()
        if tracker:
            tracker.track_page_visit(
                page_path=request.get('page', '/'),
                referrer=request.get('referrer'),
                user_agent=request.get('userAgent'),
                ip_address=request.get('ip'),
                session_id=request.get('sessionId')
            )
        return {'status': 'ok'}
```

Update `deployment/landing-page/index.html` to call tracking (add before closing `</script>` tag):

```javascript
    // Track page visit
    fetch('/api/track-visit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            page: window.location.pathname,
            referrer: document.referrer,
            userAgent: navigator.userAgent
        })
    }).catch(e => console.error('Tracking failed:', e));
```

## Usage Queries

### View daily statistics:
```sql
SELECT * FROM session_summary ORDER BY date DESC LIMIT 30;
```

### View recent sessions:
```sql
SELECT
    DATE_FORMAT(start_time, '%Y-%m-%d %H:%i') as started,
    CONCAT(FLOOR(duration_seconds/60), 'm ', duration_seconds%60, 's') as duration,
    programs_run,
    lines_executed
FROM ide_sessions
WHERE end_time IS NOT NULL
ORDER BY start_time DESC
LIMIT 20;
```

### View page visit stats:
```sql
SELECT
    page_path,
    COUNT(*) as visits,
    COUNT(DISTINCT ip_address) as unique_ips,
    DATE(timestamp) as date
FROM page_visits
WHERE timestamp >= CURDATE() - INTERVAL 7 DAY
GROUP BY page_path, DATE(timestamp)
ORDER BY date DESC, visits DESC;
```

## Privacy Notes
- IP addresses are stored but can be hashed/anonymized if needed
- User agents are stored for browser compatibility analysis
- No personally identifiable information is collected
- Session IDs are temporary and not linked to user accounts
