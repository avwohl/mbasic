"""Usage tracking for MBASIC web application.

Tracks page visits, IDE sessions, program executions, and feature usage.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


class UsageTracker:
    """Tracks usage metrics for MBASIC web application."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize usage tracker with configuration.

        Args:
            config: Configuration dict with MySQL connection settings
        """
        self.enabled = config.get('enabled', False)
        self.config = config
        self.db_connection = None

        if self.enabled:
            self._init_db_connection()

    def _init_db_connection(self):
        """Initialize MySQL database connection."""
        try:
            import mysql.connector
            mysql_config = self.config.get('mysql', {})

            # Build connection params
            conn_params = {
                'database': mysql_config.get('database', 'mbasic_logs'),
                'charset': 'utf8mb4',
                'autocommit': True
            }

            # Use unix socket or host/port
            if 'unix_socket' in mysql_config:
                conn_params['unix_socket'] = mysql_config['unix_socket']
                conn_params['user'] = mysql_config.get('user', 'root')
            else:
                conn_params['host'] = mysql_config.get('host', 'localhost')
                conn_params['port'] = mysql_config.get('port', 3306)
                conn_params['user'] = mysql_config.get('user', 'root')

            # Add password if provided
            if 'password' in mysql_config:
                conn_params['password'] = mysql_config['password']

            # Disable SSL for private network connections (self-signed cert issues)
            # This is safe since traffic is on DigitalOcean private network
            if mysql_config.get('disable_ssl', False):
                conn_params['ssl_disabled'] = True

            self.db_connection = mysql.connector.connect(**conn_params)
            logger.info("Usage tracking database connection initialized")

        except Exception as e:
            logger.error(f"Failed to initialize usage tracking database: {e}")
            self.enabled = False

    def _execute_query(self, query: str, params: tuple = None) -> Optional[int]:
        """Execute a database query.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Last inserted ID or None on error
        """
        if not self.enabled or not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, params or ())
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Exception as e:
            logger.error(f"Usage tracking query failed: {e}")
            # Try to reconnect
            try:
                self._init_db_connection()
            except:
                pass
            return None

    def track_page_visit(self, page_path: str, referrer: Optional[str] = None,
                        user_agent: Optional[str] = None, ip_address: Optional[str] = None,
                        session_id: Optional[str] = None):
        """Track a page visit.

        Args:
            page_path: Path of the page visited (e.g., '/', '/ide')
            referrer: HTTP referrer
            user_agent: User agent string
            ip_address: Client IP address
            session_id: Session identifier
        """
        if not self.enabled:
            return

        query = """
            INSERT INTO page_visits (page_path, referrer, user_agent, ip_address, session_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        self._execute_query(query, (page_path, referrer, user_agent, ip_address, session_id))

    def start_ide_session(self, session_id: str, user_agent: Optional[str] = None,
                         ip_address: Optional[str] = None):
        """Track the start of an IDE session.

        Args:
            session_id: Unique session identifier
            user_agent: User agent string
            ip_address: Client IP address
        """
        if not self.enabled:
            return

        query = """
            INSERT INTO ide_sessions (session_id, user_agent, ip_address, last_activity)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE last_activity = NOW()
        """
        self._execute_query(query, (session_id, user_agent, ip_address))

    def update_session_activity(self, session_id: str):
        """Update the last activity time for a session.

        Args:
            session_id: Session identifier
        """
        if not self.enabled:
            return

        query = """
            UPDATE ide_sessions
            SET last_activity = NOW()
            WHERE session_id = %s
        """
        self._execute_query(query, (session_id,))

    def end_ide_session(self, session_id: str):
        """Mark an IDE session as ended and calculate duration.

        Args:
            session_id: Session identifier
        """
        if not self.enabled:
            return

        query = """
            UPDATE ide_sessions
            SET end_time = NOW(),
                duration_seconds = TIMESTAMPDIFF(SECOND, start_time, NOW())
            WHERE session_id = %s AND end_time IS NULL
        """
        self._execute_query(query, (session_id,))

    def track_program_execution(self, session_id: str, program_lines: int,
                               execution_time_ms: int, lines_executed: int,
                               success: bool, error_message: Optional[str] = None):
        """Track a program execution.

        Args:
            session_id: Session identifier
            program_lines: Number of lines in the program
            execution_time_ms: Execution time in milliseconds
            lines_executed: Number of lines executed
            success: Whether execution completed successfully
            error_message: Error message if execution failed
        """
        if not self.enabled:
            return

        # Insert execution record
        query = """
            INSERT INTO program_executions
            (session_id, program_lines, execution_time_ms, lines_executed, success, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self._execute_query(query, (session_id, program_lines, execution_time_ms,
                                    lines_executed, success, error_message))

        # Update session statistics
        update_query = """
            UPDATE ide_sessions
            SET programs_run = programs_run + 1,
                lines_executed = lines_executed + %s,
                errors_encountered = errors_encountered + %s,
                last_activity = NOW()
            WHERE session_id = %s
        """
        error_count = 0 if success else 1
        self._execute_query(update_query, (lines_executed, error_count, session_id))

    def track_feature_usage(self, session_id: str, feature_name: str,
                           feature_data: Optional[Dict[str, Any]] = None):
        """Track usage of a specific feature.

        Args:
            session_id: Session identifier
            feature_name: Name of the feature (e.g., 'debugger', 'compiler', 'file_save')
            feature_data: Optional additional data about feature usage
        """
        if not self.enabled:
            return

        json_data = json.dumps(feature_data) if feature_data else None

        query = """
            INSERT INTO feature_usage (session_id, feature_name, feature_data)
            VALUES (%s, %s, %s)
        """
        self._execute_query(query, (session_id, feature_name, json_data))

        # Update session activity
        self.update_session_activity(session_id)

    def close(self):
        """Close database connection."""
        if self.db_connection:
            try:
                self.db_connection.close()
            except:
                pass
            self.db_connection = None


# Global usage tracker instance (initialized by web backend)
_global_tracker: Optional[UsageTracker] = None


def init_usage_tracker(config: Dict[str, Any]) -> UsageTracker:
    """Initialize global usage tracker.

    Args:
        config: Configuration dict

    Returns:
        Initialized UsageTracker instance
    """
    global _global_tracker
    _global_tracker = UsageTracker(config)
    return _global_tracker


def get_usage_tracker() -> Optional[UsageTracker]:
    """Get global usage tracker instance.

    Returns:
        UsageTracker instance or None if not initialized
    """
    return _global_tracker
