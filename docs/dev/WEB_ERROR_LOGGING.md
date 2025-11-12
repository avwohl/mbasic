# Web UI Error Logging System

## Overview

The MBASIC web UI includes comprehensive error logging designed for multi-user, long-running deployments. The system distinguishes between expected errors (syntax, lexical) and unexpected errors (program bugs, runtime exceptions), logging only unexpected errors with full stack traces to MySQL for analysis.

## Features

- **Expected vs Unexpected Errors**: Automatically classifies errors
  - **Expected**: `SyntaxError`, `LexerError`, `ParseError`, `SemanticError` - NOT logged to database
  - **Unexpected**: All other exceptions - logged with full stack traces

- **Multiple Logging Backends**:
  - `stderr` - Log to standard error (development, default)
  - `mysql` - Log to MySQL database (production)
  - `both` - Log to both stderr and MySQL

- **Session Tracking**: All errors include session ID for multi-user debugging

- **Full Stack Traces**: Unexpected errors captured with complete stack traces

- **Zero Performance Impact**: Graceful fallback if MySQL unavailable

## Configuration

### Setup Multi-User Config

1. Copy example configuration:
   ```bash
   cp config/multiuser.json.example config/multiuser.json
   ```

2. Enable error logging in `config/multiuser.json`:

   **Option A: Unix Socket (recommended for local MariaDB/MySQL)**
   ```json
   {
     "enabled": true,
     "error_logging": {
       "type": "mysql",
       "mysql": {
         "unix_socket": "/run/mysqld/mysqld.sock",
         "user": "your_user",
         "password": "",
         "database": "mbasic_logs",
         "table": "web_errors"
       },
       "log_expected_errors": false
     }
   }
   ```

   **Option B: TCP Connection (for remote databases)**
   ```json
   {
     "enabled": true,
     "error_logging": {
       "type": "mysql",
       "mysql": {
         "host": "localhost",
         "port": 3306,
         "user": "mbasic",
         "password": "your_password",
         "database": "mbasic_logs",
         "table": "web_errors"
       },
       "log_expected_errors": false
     }
   }
   ```

### Setup MySQL/MariaDB Database

1. Run the setup script:
   ```bash
   mysql < config/setup_mysql_logging.sql
   # or with password:
   mysql -u root -p < config/setup_mysql_logging.sql
   ```

2. Or manually create database:
   ```sql
   CREATE DATABASE mbasic_logs;
   USE mbasic_logs;
   -- See config/setup_mysql_logging.sql for full schema
   ```

3. **For Unix socket authentication (recommended)**:
   If your user can run `mysql` without a password (using Unix socket authentication),
   simply configure `unix_socket` in `config/multiuser.json`:
   ```json
   "mysql": {
     "unix_socket": "/run/mysqld/mysqld.sock",
     "user": "your_username",
     "password": "",
     "database": "mbasic_logs"
   }
   ```

4. **For password authentication** (optional):
   Create a MySQL user with password:
   ```sql
   CREATE USER 'mbasic'@'localhost' IDENTIFIED BY 'your_password';
   GRANT SELECT, INSERT ON mbasic_logs.* TO 'mbasic'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. Update `config/multiuser.json` with your connection settings

## Usage

### Logging Errors in Code

In the web backend, use the `_log_error` helper method:

```python
try:
    # Some operation
    result = do_something()
except Exception as e:
    self._log_error("function_name", e)
    # Handle error...
```

In other modules, use the global function:

```python
from src.error_logger import log_web_error

try:
    # Some operation
    pass
except Exception as e:
    log_web_error("context", e, session_id="abc123")
```

### Viewing Error Logs

**View recent errors:**
```bash
python3 utils/view_error_logs.py
```

**View error summary:**
```bash
python3 utils/view_error_logs.py --summary
```

**View only unexpected errors:**
```bash
python3 utils/view_error_logs.py --unexpected
```

**View errors for specific session:**
```bash
python3 utils/view_error_logs.py --session abc123
```

**View full error details:**
```bash
python3 utils/view_error_logs.py --detail 42
```

**Clear old logs (>30 days):**
```bash
python3 utils/view_error_logs.py --clear
```

### Database Queries

**Recent unexpected errors:**
```sql
SELECT timestamp, session_id, error_type, context, message
FROM web_errors
WHERE is_expected = FALSE
  AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC;
```

**Error summary by type:**
```sql
SELECT
    error_type,
    is_expected,
    COUNT(*) as error_count,
    COUNT(DISTINCT session_id) as affected_sessions
FROM web_errors
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY error_type, is_expected
ORDER BY error_count DESC;
```

**Errors with stack traces:**
```sql
SELECT id, timestamp, context, message, stack_trace
FROM web_errors
WHERE is_expected = FALSE
  AND stack_trace IS NOT NULL
ORDER BY timestamp DESC
LIMIT 10;
```

## Architecture

### Components

1. **multiuser_config.py**: Centralized configuration management
   - Single JSON config for all multi-user settings
   - Session storage (memory/Redis)
   - Error logging (stderr/MySQL)
   - Rate limiting, autosave, etc.

2. **error_logger.py**: Core error logging module
   - `ErrorLogger` class with MySQL support
   - Expected vs unexpected error classification
   - Stack trace capture for unexpected errors
   - Graceful fallback if MySQL unavailable

3. **nicegui_backend.py**: Web UI integration
   - `_log_error()` helper method with session tracking
   - 40+ error handlers updated to log errors
   - Session ID automatically included

4. **view_error_logs.py**: Error analysis utility
   - View recent errors
   - Filter by session, type, expected/unexpected
   - Summary statistics
   - Clear old logs

### Database Schema

```sql
CREATE TABLE web_errors (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    session_id VARCHAR(255),
    error_type VARCHAR(100),
    is_expected BOOLEAN DEFAULT FALSE,
    context VARCHAR(500),
    message TEXT,
    stack_trace TEXT,
    user_agent TEXT,
    request_path VARCHAR(500),
    version VARCHAR(50),
    created_at DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_timestamp (timestamp),
    INDEX idx_session (session_id),
    INDEX idx_type (error_type),
    INDEX idx_expected (is_expected)
);
```

## Error Types

### Expected Errors (NOT logged to database)

These are user errors, not program bugs:

- **LexerError**: Tokenization errors (invalid characters, etc.)
  - Example: `Invalid character '@' at line 100`

- **ParseError**: Syntax errors during parsing
  - Example: `Expected '=' after variable name`

- **SemanticError**: Semantic analysis errors
  - Example: `Variable used before being declared`

- **BASIC Runtime Errors**: Errors reported via `state.error_info`
  - Example: `?SN Error in 100` (Syntax error)

### Unexpected Errors (logged with stack traces)

These indicate program bugs that should be fixed:

- **RuntimeError**: Python runtime errors
  - Example: Array subscript out of range

- **TypeError**: Type errors in Python code
  - Example: Cannot concatenate str and int

- **AttributeError**: Missing attributes/methods
  - Example: 'NoneType' object has no attribute 'tick'

- **KeyError**, **IndexError**, etc.: Other Python exceptions

- **Generic Exception**: Catch-all for unexpected errors

## Troubleshooting

### MySQL Not Available

If MySQL is not installed or not configured:
- Errors are logged to stderr only
- No functionality is lost
- Warning printed once on first error

### MySQL Connection Fails

If MySQL connection fails:
- System falls back to stderr logging
- Warning printed to stderr
- Application continues normally

### Dependencies Missing

Install MySQL connector:
```bash
pip install mysql-connector-python
```

### View Stderr Logs

When using stderr logging (default):
```bash
python3 mbasic --ui web 2> errors.log
# Errors written to errors.log
```

## Production Deployment

For production multi-user deployments:

1. **Enable MySQL logging** in `config/multiuser.json`
2. **Set up log rotation** for old errors:
   ```bash
   # Cron job to clean up logs monthly
   0 0 1 * * python3 /path/to/utils/view_error_logs.py --clear
   ```
3. **Monitor unexpected errors**:
   ```bash
   # Daily summary email
   python3 utils/view_error_logs.py --summary | mail -s "MBASIC Errors" admin@example.com
   ```
4. **Set up alerting** for critical errors:
   ```sql
   -- Check for new unexpected errors in last hour
   SELECT COUNT(*) FROM web_errors
   WHERE is_expected = FALSE
     AND timestamp >= DATE_SUB(NOW(), INTERVAL 1 HOUR);
   ```

## Performance

- **Zero overhead** when MySQL not configured
- **Minimal overhead** when MySQL enabled:
  - Error logging is asynchronous
  - Only logs unexpected errors
  - Connection pooling via mysql-connector-python
  - No impact on successful operations

## Future Enhancements

- [ ] Add user_agent extraction from request headers
- [ ] Add request_path tracking for error context
- [ ] Email notifications for critical errors
- [ ] Web dashboard for error analysis
- [ ] Export errors to CSV/JSON
- [ ] Integration with external logging services (Sentry, Rollbar)

## Related Documentation

- `config/multiuser.json.example` - Configuration template
- `config/setup_mysql_logging.sql` - Database schema
- `src/multiuser_config.py` - Configuration loader
- `src/error_logger.py` - Error logging implementation
- `utils/view_error_logs.py` - Error viewing utility
