# Redis Storage - Per-Session Settings

When using Redis storage for load-balanced deployments, each user session has independent settings stored in Redis.

## Implementation

As of the latest version, MBASIC uses **pluggable settings backends** that automatically adapt based on environment:

### Single-User Mode (No Redis)
- **Backend**: `FileSettingsBackend`
- **Storage**: `~/.mbasic/settings.json` (global) and `.mbasic/settings.json` (project)
- **Behavior**: Read/write to local filesystem
- **Use case**: Development, single-user deployments

### Multi-User Mode (Redis Enabled)
- **Backend**: `RedisSettingsBackend`
- **Storage**: Redis at key `nicegui:settings:{session_id}`
- **Behavior**:
  - Default settings loaded from disk once on startup
  - Each session gets independent settings in Redis
  - No disk writes after initialization (read-only from filesystem)
  - Settings persist for 24 hours (matches NiceGUI session TTL)
- **Use case**: Load-balanced web deployments

### What's Synchronized

**Synchronized via Redis** ✅:
- Session state (programs, variables, output, execution state)
- Runtime state
- Editor content
- Recent files
- **Settings (per-session)** ← NEW!

### Architecture

**Settings Backend Abstraction** (`src/settings_backend.py`):
```python
class SettingsBackend(ABC):
    """Abstract base class for settings storage."""
    def load_global(self) -> Dict[str, Any]: ...
    def save_global(self, settings: Dict[str, Any]) -> None: ...
    def load_project(self) -> Dict[str, Any]: ...
    def save_project(self, settings: Dict[str, Any]) -> None: ...
```

**Automatic Backend Selection** (`create_settings_backend()`):
```python
redis_url = os.environ.get('NICEGUI_REDIS_URL')

if redis_url and session_id:
    # Redis mode: Load defaults from disk, use per-session Redis storage
    file_backend = FileSettingsBackend(project_dir)
    default_settings = file_backend.load_global()
    return RedisSettingsBackend(redis_client, session_id, default_settings)
else:
    # File mode: Traditional filesystem storage
    return FileSettingsBackend(project_dir)
```

**Redis Key Structure**:
- Session state: `nicegui:client:{session_id}`
- Settings: `nicegui:settings:{session_id}`
- TTL: 24 hours (matches NiceGUI session expiry)

### How It Works

1. **Session Creation**: Each browser session gets unique `session_id = str(id(backend_instance))`
2. **Initialization**: Default settings loaded from `~/.mbasic/settings.json` once
3. **First Access**: Redis backend seeds session with default settings
4. **User Changes**: Saved to `nicegui:settings:{session_id}` in Redis
5. **Page Refresh**: `restore_state()` recreates settings backend with same session_id
6. **Session Isolation**: Each user sees only their own settings

## Usage

### Development / Single-User

No configuration needed. Settings work as before:

```bash
python3 mbasic --ui web
```

Settings stored in `~/.mbasic/settings.json`.

### Production / Multi-User (Load-Balanced)

1. **Start Redis server**:
```bash
redis-server
```

2. **Set environment variable**:
```bash
export NICEGUI_REDIS_URL="redis://localhost:6379/0"
```

3. **Start MBASIC instances**:
```bash
# Instance 1
python3 mbasic --ui web --port 8080

# Instance 2
python3 mbasic --ui web --port 8081

# Instance 3
python3 mbasic --ui web --port 8082
```

4. **Configure load balancer** (nginx, HAProxy, etc.) to distribute requests.

Each user session gets independent settings automatically!

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Default settings (optional)
COPY default_settings.json /root/.mbasic/settings.json

ENV NICEGUI_REDIS_URL="redis://redis:6379/0"
CMD ["python3", "mbasic", "--ui", "web"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:alpine

  mbasic:
    build: .
    ports:
      - "8080-8082:8080"
    environment:
      - NICEGUI_REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    deploy:
      replicas: 3
```

### Testing Per-Session Isolation

```bash
# Set Redis URL
export NICEGUI_REDIS_URL="redis://localhost:6379/0"

# Run test script
python3 test_redis_settings.py
```

Expected output:
```
✓ Both sessions start with defaults
✓ Session 2 unaffected by Session 1 changes
✓ Sessions have independent settings
✓ Settings persist across manager instances
```

## Implementation Details

### Files Modified/Created

- **`src/settings_backend.py`** (NEW): Backend abstraction layer
  - `SettingsBackend` abstract base class
  - `FileSettingsBackend` for local filesystem
  - `RedisSettingsBackend` for per-session Redis storage
  - `create_settings_backend()` factory function

- **`src/settings.py`** (MODIFIED): Pluggable backend support
  - Added `backend` parameter to `SettingsManager.__init__()`
  - Delegated all load/save operations to backend
  - Maintained backward compatibility

- **`src/ui/web/nicegui_backend.py`** (MODIFIED): Per-session settings
  - Create session_id early in `__init__`
  - Use `create_settings_backend(session_id=session_id)`
  - Restore session_id in `restore_state()` for Redis reconnection

- **`test_redis_settings.py`** (NEW): Integration tests
  - Verify per-session isolation
  - Test settings persistence
  - Validate backend selection

### Key Design Decisions

1. **Per-Session, Not Global**: Each user session has independent settings
   - Rationale: Different users may have different preferences
   - Trade-off: Settings don't sync across user's own sessions (acceptable)

2. **Read-Only Disk Access**: Redis mode never writes to filesystem
   - Rationale: Prevent file conflicts in multi-instance deployments
   - Default settings loaded once on first Redis access

3. **Automatic Backend Selection**: Based on `NICEGUI_REDIS_URL` environment variable
   - Rationale: Zero code changes for users, just configuration
   - Fallback: File backend if Redis unavailable

4. **24-Hour TTL**: Matches NiceGUI's session expiry
   - Rationale: Prevent Redis memory bloat from abandoned sessions
   - Sessions expire naturally when inactive

## References

- Settings Manager: `src/settings.py`
- Settings Backend: `src/settings_backend.py`
- Settings Definitions: `src/settings_definitions.py`
- Web Settings Dialog: `src/ui/web/web_settings_dialog.py`
- NiceGUI Backend: `src/ui/web/nicegui_backend.py`
- Redis Session Storage Setup: `docs/dev/REDIS_SESSION_STORAGE_SETUP.md`
