# Web UI Multi-User Deployment Guide

## Overview

This guide covers deploying the MBASIC web UI for multi-user, production environments. Multi-user mode adds session persistence, error logging, rate limiting, and other features needed for load-balanced, long-running deployments.

**Single-user mode** (default) stores everything in memory - simple but sessions are lost on restart.

**Multi-user mode** adds:
- Redis-backed session storage (survives restarts, load balancing)
- MySQL error logging (track bugs across sessions)
- Rate limiting (prevent abuse)
- Centralized configuration

## Quick Start

For local development or single-user deployments, just run:
```bash
python3 mbasic --ui web
```

For production multi-user deployments, follow this guide.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer (optional)                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐      ┌───────▼──────┐      ┌──────▼──────┐
│ MBASIC Web 1 │      │ MBASIC Web 2 │      │ MBASIC Web N│
└───────┬──────┘      └───────┬──────┘      └──────┬──────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼──────┐      ┌───────▼──────┐
│    Redis     │      │    MySQL     │
│  (Sessions)  │      │   (Errors)   │
└──────────────┘      └──────────────┘
```

## Installation

### 1. Install Dependencies

**Base requirements:**
```bash
source venv/bin/activate
pip install nicegui>=3.2.0
```

**For Redis session storage (load balancing):**
```bash
pip install redis>=5.0.0
```

**For MySQL error logging:**
```bash
pip install mysql-connector-python>=8.0
```

**All at once:**
```bash
pip install nicegui redis mysql-connector-python
```

**Note:** No apt packages needed - all dependencies are pure Python!

### 2. Install Redis (Optional)

**Only needed for load-balanced deployments** with multiple web server instances.

**Debian/Ubuntu:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Or use Docker:**
```bash
docker run -d -p 6379:6379 --name mbasic-redis redis:alpine
```

**Test connection:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Install MariaDB/MySQL (Optional)

**Only needed if you want error logging** for debugging production issues.

**Debian/Ubuntu:**
```bash
sudo apt-get install mariadb-server
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

**Secure installation:**
```bash
sudo mysql_secure_installation
```

**Create database:**
```bash
mysql < config/setup_mysql_logging.sql
```

**Test connection:**
```bash
mysql -e "SHOW DATABASES LIKE 'mbasic_logs';"
```

## Configuration

### 1. Create Configuration File

```bash
cp config/multiuser.json.example config/multiuser.json
```

### 2. Configure Multi-User Settings

Edit `config/multiuser.json`:

#### Minimal Configuration (In-Memory)

For single-server deployments without external dependencies:

```json
{
  "enabled": false,
  "session_storage": {
    "type": "memory"
  },
  "error_logging": {
    "type": "stderr"
  }
}
```

#### Redis Session Storage (Load Balancing)

For multiple web server instances sharing sessions:

```json
{
  "enabled": true,
  "session_storage": {
    "type": "redis",
    "redis": {
      "url": "redis://localhost:6379/0",
      "key_prefix": "mbasic:session:"
    }
  },
  "error_logging": {
    "type": "stderr"
  }
}
```

#### MySQL Error Logging (Unix Socket)

For local MariaDB/MySQL with Unix socket authentication:

```json
{
  "enabled": true,
  "session_storage": {
    "type": "memory"
  },
  "error_logging": {
    "type": "mysql",
    "mysql": {
      "unix_socket": "/run/mysqld/mysqld.sock",
      "user": "your_username",
      "password": "",
      "database": "mbasic_logs",
      "table": "web_errors"
    },
    "log_expected_errors": false
  }
}
```

#### MySQL Error Logging (TCP/Password)

For remote MySQL or password authentication:

```json
{
  "enabled": true,
  "session_storage": {
    "type": "memory"
  },
  "error_logging": {
    "type": "mysql",
    "mysql": {
      "host": "mysql.example.com",
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

#### Full Production Configuration

Redis sessions + MySQL logging + rate limiting:

```json
{
  "enabled": true,

  "session_storage": {
    "type": "redis",
    "redis": {
      "url": "redis://localhost:6379/0",
      "key_prefix": "mbasic:session:"
    }
  },

  "error_logging": {
    "type": "both",
    "mysql": {
      "unix_socket": "/run/mysqld/mysqld.sock",
      "user": "mbasic",
      "password": "",
      "database": "mbasic_logs",
      "table": "web_errors"
    },
    "log_expected_errors": false
  },

  "rate_limiting": {
    "enabled": true,
    "max_requests_per_minute": 60,
    "max_concurrent_sessions": 100
  },

  "autosave": {
    "enabled": true,
    "interval_seconds": 60
  }
}
```

### 3. Environment Variables (Legacy)

For backward compatibility, environment variables still work:

```bash
# Redis session storage
export NICEGUI_REDIS_URL="redis://localhost:6379/0"

# MySQL error logging
export MBASIC_MYSQL_HOST="localhost"
export MBASIC_MYSQL_USER="mbasic"
export MBASIC_MYSQL_PASSWORD="password"
export MBASIC_MYSQL_DB="mbasic_logs"
```

**Note:** `config/multiuser.json` takes precedence over environment variables.

## Setup Database (MySQL/MariaDB)

### Using Unix Socket (Recommended)

If your user can run `mysql` without a password:

1. **Create database:**
   ```bash
   mysql < config/setup_mysql_logging.sql
   ```

2. **Verify:**
   ```bash
   mysql mbasic_logs -e "SHOW TABLES;"
   # Should show: web_errors, error_summary, recent_errors
   ```

3. **Configure:**
   ```json
   "mysql": {
     "unix_socket": "/run/mysqld/mysqld.sock",
     "user": "your_username",
     "password": "",
     "database": "mbasic_logs"
   }
   ```

### Using Password Authentication

1. **Create database and user:**
   ```bash
   sudo mysql < config/setup_mysql_logging.sql
   sudo mysql << 'EOF'
   CREATE USER 'mbasic'@'localhost' IDENTIFIED BY 'your_password';
   GRANT SELECT, INSERT ON mbasic_logs.* TO 'mbasic'@'localhost';
   FLUSH PRIVILEGES;
   EOF
   ```

2. **Configure:**
   ```json
   "mysql": {
     "host": "localhost",
     "port": 3306,
     "user": "mbasic",
     "password": "your_password",
     "database": "mbasic_logs"
   }
   ```

## Running the Web UI

### Development

```bash
source venv/bin/activate
python3 mbasic --ui web --port 8080
```

### Production (Single Instance)

Using systemd:

```ini
# /etc/systemd/system/mbasic-web.service
[Unit]
Description=MBASIC Web UI
After=network.target redis.service mariadb.service

[Service]
Type=simple
User=mbasic
WorkingDirectory=/opt/mbasic
Environment="PATH=/opt/mbasic/venv/bin:/usr/bin"
ExecStart=/opt/mbasic/venv/bin/python3 /opt/mbasic/mbasic --ui web --port 8080
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start mbasic-web
sudo systemctl enable mbasic-web
```

### Production (Load Balanced)

**Requirements:**
- Redis for session storage
- Multiple web instances on different ports
- Nginx/HAProxy for load balancing

**Start multiple instances:**
```bash
# Instance 1
python3 mbasic --ui web --port 8081 &

# Instance 2
python3 mbasic --ui web --port 8082 &

# Instance 3
python3 mbasic --ui web --port 8083 &
```

**Nginx configuration:**
```nginx
upstream mbasic_backend {
    least_conn;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
    server 127.0.0.1:8083;
}

server {
    listen 80;
    server_name mbasic.example.com;

    location / {
        proxy_pass http://mbasic_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### View Error Logs

**Recent errors:**
```bash
source venv/bin/activate
python3 utils/view_error_logs.py
```

**Error summary:**
```bash
python3 utils/view_error_logs.py --summary
```

**Unexpected errors only:**
```bash
python3 utils/view_error_logs.py --unexpected
```

**Filter by session:**
```bash
python3 utils/view_error_logs.py --session abc123
```

**Full error details:**
```bash
python3 utils/view_error_logs.py --detail 42
```

### Database Queries

**Recent unexpected errors:**
```sql
SELECT timestamp, session_id, error_type, context, message
FROM mbasic_logs.web_errors
WHERE is_expected = FALSE
  AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC
LIMIT 50;
```

**Error summary:**
```sql
SELECT * FROM mbasic_logs.error_summary;
```

**Recent errors view:**
```sql
SELECT * FROM mbasic_logs.recent_errors;
```

### Redis Session Monitoring

**Check session count:**
```bash
redis-cli KEYS "mbasic:session:*" | wc -l
```

**View session data:**
```bash
redis-cli KEYS "mbasic:session:*"
```

**Clear old sessions:**
```bash
redis-cli FLUSHDB  # Warning: Clears all Redis data!
```

## Maintenance

### Clear Old Error Logs

**Using utility script:**
```bash
python3 utils/view_error_logs.py --clear
# Removes errors older than 30 days
```

**Manual cleanup:**
```sql
DELETE FROM mbasic_logs.web_errors
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### Backup Database

```bash
mysqldump mbasic_logs > mbasic_logs_backup.sql
```

### Restore Database

```bash
mysql mbasic_logs < mbasic_logs_backup.sql
```

## Troubleshooting

### Redis Connection Failed

**Symptom:** Warning about Redis not available

**Solutions:**
1. Check Redis is running: `systemctl status redis`
2. Test connection: `redis-cli ping`
3. Check URL in config: `redis://localhost:6379/0`
4. Check firewall: `sudo ufw allow 6379`

**Fallback:** System automatically falls back to in-memory sessions

### MySQL Connection Failed

**Symptom:** Warning about MySQL not available

**Solutions:**
1. Check MySQL running: `systemctl status mariadb`
2. Test connection: `mysql -u mbasic -p mbasic_logs`
3. Check socket path: `/run/mysqld/mysqld.sock`
4. Verify grants: `SHOW GRANTS FOR 'mbasic'@'localhost';`

**Fallback:** System automatically falls back to stderr logging

### Sessions Not Persisting

**Possible causes:**
1. Redis not configured in `config/multiuser.json`
2. Redis server not running
3. Connection refused (check firewall)

**Verify:**
```bash
redis-cli KEYS "mbasic:session:*"
# Should show session keys
```

### Errors Not Being Logged

**Check:**
1. `config/multiuser.json` has `"type": "mysql"` or `"both"`
2. MySQL credentials are correct
3. Database table exists: `mysql mbasic_logs -e "SHOW TABLES;"`

**Test:**
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')
from error_logger import log_web_error

try:
    raise ValueError("Test error")
except Exception as e:
    log_web_error("test", e, session_id="TEST")
    print("Error logged!")
EOF
```

## Security Considerations

### MySQL Security

1. **Use separate user** with limited privileges:
   ```sql
   GRANT SELECT, INSERT ON mbasic_logs.* TO 'mbasic'@'localhost';
   ```

2. **Don't use root** in production

3. **Use Unix sockets** when possible (more secure than TCP)

4. **Rotate passwords** regularly

### Redis Security

1. **Enable password authentication:**
   ```bash
   # /etc/redis/redis.conf
   requirepass your_strong_password
   ```

2. **Bind to localhost only:**
   ```bash
   bind 127.0.0.1
   ```

3. **Disable dangerous commands:**
   ```bash
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""
   ```

### Rate Limiting

Enable in `config/multiuser.json`:
```json
"rate_limiting": {
  "enabled": true,
  "max_requests_per_minute": 60,
  "max_concurrent_sessions": 100
}
```

## Performance Tuning

### Redis

**Increase max memory:**
```bash
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

**Enable persistence:**
```bash
save 900 1
save 300 10
save 60 10000
```

### MySQL

**Optimize for writes:**
```sql
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL innodb_buffer_pool_size = 256M;
```

**Add indexes if needed:**
```sql
CREATE INDEX idx_timestamp_expected ON web_errors(timestamp, is_expected);
```

### Web Server

**Increase worker threads** if handling many concurrent users:
```python
# In nicegui_backend.py start_web_ui()
ui.run(
    port=port,
    reload=False,
    show=False,
    workers=4  # Add this for multiple workers
)
```

## Production Checklist

- [ ] Dependencies installed (nicegui, redis, mysql-connector-python)
- [ ] Redis server running (if using session storage)
- [ ] MySQL/MariaDB server running (if using error logging)
- [ ] Database created (`config/setup_mysql_logging.sql`)
- [ ] Configuration file created (`config/multiuser.json`)
- [ ] Credentials configured (MySQL user/password)
- [ ] Systemd service created (if using)
- [ ] Load balancer configured (if using)
- [ ] Firewall rules set (ports 8080, 6379, 3306)
- [ ] Monitoring set up (error logs, sessions)
- [ ] Backup strategy in place (database dumps)
- [ ] Security hardened (passwords, socket permissions)
- [ ] Rate limiting enabled (if public-facing)
- [ ] SSL/TLS configured (nginx/haproxy)

## Example Deployments

### Small Team (5-10 users)

**Setup:**
- Single web instance
- In-memory sessions
- MySQL error logging (Unix socket)

**Config:**
```json
{
  "enabled": true,
  "session_storage": {"type": "memory"},
  "error_logging": {
    "type": "mysql",
    "mysql": {
      "unix_socket": "/run/mysqld/mysqld.sock",
      "user": "mbasic",
      "database": "mbasic_logs"
    }
  }
}
```

### Medium Organization (50-100 users)

**Setup:**
- 3 web instances (load balanced)
- Redis session storage
- MySQL error logging
- Nginx load balancer

**Config:**
```json
{
  "enabled": true,
  "session_storage": {
    "type": "redis",
    "redis": {"url": "redis://localhost:6379/0"}
  },
  "error_logging": {
    "type": "both",
    "mysql": {
      "unix_socket": "/run/mysqld/mysqld.sock",
      "user": "mbasic",
      "database": "mbasic_logs"
    }
  },
  "rate_limiting": {
    "enabled": true,
    "max_requests_per_minute": 100,
    "max_concurrent_sessions": 200
  }
}
```

### Large Scale (1000+ users)

**Setup:**
- 10+ web instances
- Redis Cluster for sessions
- Remote MySQL cluster
- HAProxy load balancer
- Docker/Kubernetes orchestration

**Config:**
```json
{
  "enabled": true,
  "session_storage": {
    "type": "redis",
    "redis": {"url": "redis://redis-cluster:6379/0"}
  },
  "error_logging": {
    "type": "mysql",
    "mysql": {
      "host": "mysql-cluster.internal",
      "port": 3306,
      "user": "mbasic",
      "password": "ENV_VAR_PASSWORD",
      "database": "mbasic_logs"
    }
  },
  "rate_limiting": {
    "enabled": true,
    "max_requests_per_minute": 200,
    "max_concurrent_sessions": 5000
  }
}
```

## Related Documentation

- [WEB_ERROR_LOGGING.md](WEB_ERROR_LOGGING.md) - Error logging system details
- `config/multiuser.json.example` - Configuration template
- `config/setup_mysql_logging.sql` - Database schema
- `utils/view_error_logs.py` - Error viewing utility
- `old_dev_docs/INSTALLATION_FOR_DEVELOPERS.md` - Development setup (archived)
