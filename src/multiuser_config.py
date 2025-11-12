"""Multi-user configuration management for MBASIC web UI.

Centralizes all multi-user related configuration including:
- Session storage (memory/Redis)
- Error logging (stderr/MySQL)
- Rate limiting
- Autosave settings

Configuration is loaded from config/multiuser.json if it exists,
otherwise uses sensible defaults for single-user mode.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SessionStorageConfig:
    """Configuration for session storage."""
    type: str = "memory"  # "memory" or "redis"
    redis_url: Optional[str] = None
    redis_key_prefix: str = "mbasic:session:"


@dataclass
class MySQLConfig:
    """MySQL connection configuration."""
    host: str = "localhost"
    port: int = 3306
    unix_socket: Optional[str] = None  # Use Unix socket instead of host/port
    user: str = "mbasic"
    password: str = ""
    database: str = "mbasic_logs"
    table: str = "web_errors"


@dataclass
class ErrorLoggingConfig:
    """Configuration for error logging."""
    type: str = "stderr"  # "stderr", "mysql", or "both"
    mysql: Optional[MySQLConfig] = None
    log_expected_errors: bool = False
    expected_error_types: tuple = ("SyntaxError", "LexerError", "ParseError", "SemanticError")


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    enabled: bool = False
    max_requests_per_minute: int = 60
    max_concurrent_sessions: int = 100


@dataclass
class AutosaveConfig:
    """Configuration for autosave."""
    enabled: bool = True
    interval_seconds: int = 60


@dataclass
class MultiUserConfig:
    """Complete multi-user configuration."""
    enabled: bool = False
    session_storage: SessionStorageConfig = None
    error_logging: ErrorLoggingConfig = None
    rate_limiting: RateLimitConfig = None
    autosave: AutosaveConfig = None

    def __post_init__(self):
        if self.session_storage is None:
            self.session_storage = SessionStorageConfig()
        if self.error_logging is None:
            self.error_logging = ErrorLoggingConfig()
        if self.rate_limiting is None:
            self.rate_limiting = RateLimitConfig()
        if self.autosave is None:
            self.autosave = AutosaveConfig()


def load_config() -> MultiUserConfig:
    """Load multi-user configuration from config file or environment.

    Priority:
    1. config/multiuser.json (if exists)
    2. Environment variables (for backward compatibility)
    3. Default single-user configuration

    Returns:
        MultiUserConfig instance
    """
    config = MultiUserConfig()

    # Try to load from config file
    config_path = Path(__file__).parent.parent / "config" / "multiuser.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                json_content = f.read()
                # Substitute environment variables in the JSON (supports ${VAR} syntax)
                import re
                def replace_env_var(match):
                    var_name = match.group(1)
                    return os.environ.get(var_name, match.group(0))  # Keep original if not found
                json_content = re.sub(r'\$\{([A-Z_]+)\}', replace_env_var, json_content)
                data = json.loads(json_content)
                config = _parse_config_dict(data)
        except Exception as e:
            import sys
            print(f"Warning: Failed to load {config_path}: {e}", file=sys.stderr)
            print("Using default configuration", file=sys.stderr)

    # Check for legacy environment variables (backward compatibility)
    redis_url = os.environ.get('NICEGUI_REDIS_URL')
    if redis_url:
        config.enabled = True
        config.session_storage.type = "redis"
        config.session_storage.redis_url = redis_url

    mysql_host = os.environ.get('MBASIC_MYSQL_HOST')
    if mysql_host:
        config.enabled = True
        config.error_logging.type = "mysql"
        if config.error_logging.mysql is None:
            config.error_logging.mysql = MySQLConfig()
        config.error_logging.mysql.host = mysql_host
        config.error_logging.mysql.user = os.environ.get('MBASIC_MYSQL_USER', 'mbasic')
        config.error_logging.mysql.password = os.environ.get('MBASIC_MYSQL_PASSWORD', '')
        config.error_logging.mysql.database = os.environ.get('MBASIC_MYSQL_DB', 'mbasic_logs')

    return config


def _parse_config_dict(data: Dict[str, Any]) -> MultiUserConfig:
    """Parse configuration dictionary into MultiUserConfig.

    Args:
        data: Dictionary loaded from JSON config

    Returns:
        MultiUserConfig instance
    """
    config = MultiUserConfig()

    config.enabled = data.get('enabled', False)

    # Session storage
    if 'session_storage' in data:
        ss = data['session_storage']
        config.session_storage = SessionStorageConfig(
            type=ss.get('type', 'memory'),
            redis_url=ss.get('redis', {}).get('url'),
            redis_key_prefix=ss.get('redis', {}).get('key_prefix', 'mbasic:session:')
        )

    # Error logging
    if 'error_logging' in data:
        el = data['error_logging']
        mysql_config = None
        if 'mysql' in el:
            m = el['mysql']
            mysql_config = MySQLConfig(
                host=m.get('host', 'localhost'),
                port=m.get('port', 3306),
                unix_socket=m.get('unix_socket'),
                user=m.get('user', 'mbasic'),
                password=m.get('password', ''),
                database=m.get('database', 'mbasic_logs'),
                table=m.get('table', 'web_errors')
            )

        config.error_logging = ErrorLoggingConfig(
            type=el.get('type', 'stderr'),
            mysql=mysql_config,
            log_expected_errors=el.get('log_expected_errors', False),
            expected_error_types=tuple(el.get('_expected_error_types',
                                             ['SyntaxError', 'LexerError', 'ParseError', 'SemanticError']))
        )

    # Rate limiting
    if 'rate_limiting' in data:
        rl = data['rate_limiting']
        config.rate_limiting = RateLimitConfig(
            enabled=rl.get('enabled', False),
            max_requests_per_minute=rl.get('max_requests_per_minute', 60),
            max_concurrent_sessions=rl.get('max_concurrent_sessions', 100)
        )

    # Autosave
    if 'autosave' in data:
        a = data['autosave']
        config.autosave = AutosaveConfig(
            enabled=a.get('enabled', True),
            interval_seconds=a.get('interval_seconds', 60)
        )

    return config


# Global configuration instance
_config: Optional[MultiUserConfig] = None


def get_config() -> MultiUserConfig:
    """Get the global configuration instance (lazy-loaded).

    Returns:
        MultiUserConfig instance
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def is_multiuser_enabled() -> bool:
    """Check if multi-user mode is enabled.

    Returns:
        True if multi-user mode is enabled
    """
    return get_config().enabled
