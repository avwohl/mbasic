# MBASIC Configuration Files

This directory contains configuration files for MBASIC.

## Multi-User Web Deployment

### multiuser.json

**Purpose:** Centralized configuration for multi-user web deployments

**Location:** `config/multiuser.json` (create from example)

**Quick Setup:**
```bash
cp multiuser.json.example multiuser.json
# Edit multiuser.json with your settings
```

**What it configures:**
- Session storage (memory or Redis)
- Error logging (stderr or MySQL)
- Rate limiting
- Autosave settings

**When you need it:**
- Production deployments
- Load-balanced setups
- Multi-user environments
- Error tracking/debugging

**When you DON'T need it:**
- Single-user development
- Local testing
- Default configuration works fine

**Documentation:** See [docs/dev/WEB_MULTIUSER_DEPLOYMENT.md](../docs/dev/WEB_MULTIUSER_DEPLOYMENT.md)

## Database Setup

### setup_mysql_logging.sql

**Purpose:** Creates MySQL database and tables for error logging

**Usage:**
```bash
mysql < config/setup_mysql_logging.sql
# or with password:
mysql -u root -p < config/setup_mysql_logging.sql
```

**What it creates:**
- Database: `mbasic_logs`
- Table: `web_errors` (stores error logs)
- Views: `error_summary`, `recent_errors` (for monitoring)

**Configuration:**
After running this script, update `multiuser.json`:
```json
{
  "error_logging": {
    "type": "mysql",
    "mysql": {
      "unix_socket": "/run/mysqld/mysqld.sock",
      "user": "your_username",
      "database": "mbasic_logs"
    }
  }
}
```

**Documentation:** See [docs/dev/WEB_ERROR_LOGGING.md](../docs/dev/WEB_ERROR_LOGGING.md)

## Configuration Examples

### Development (default)
No config file needed - everything in memory:
```bash
python3 mbasic --ui web
```

### Production (Unix socket MySQL)
```json
{
  "enabled": true,
  "session_storage": {"type": "memory"},
  "error_logging": {
    "type": "mysql",
    "mysql": {
      "unix_socket": "/run/mysqld/mysqld.sock",
      "user": "wohl",
      "database": "mbasic_logs"
    }
  }
}
```

### Load Balanced (Redis + MySQL)
```json
{
  "enabled": true,
  "session_storage": {
    "type": "redis",
    "redis": {"url": "redis://localhost:6379/0"}
  },
  "error_logging": {
    "type": "mysql",
    "mysql": {
      "host": "mysql.example.com",
      "user": "mbasic",
      "password": "password",
      "database": "mbasic_logs"
    }
  }
}
```

## File Listing

- `multiuser.json.example` - Configuration template
- `setup_mysql_logging.sql` - Database setup script
- `README.md` - This file

## See Also

- [WEB_MULTIUSER_DEPLOYMENT.md](../docs/dev/WEB_MULTIUSER_DEPLOYMENT.md) - Complete deployment guide
- [WEB_ERROR_LOGGING.md](../docs/dev/WEB_ERROR_LOGGING.md) - Error logging details
- [requirements.txt](../requirements.txt) - Python dependencies
