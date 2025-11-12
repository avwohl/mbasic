"""Error logging module for MBASIC web UI.

Provides centralized error logging with support for:
- MySQL database logging (for multi-user deployments)
- Stderr logging (fallback and development)
- Distinguishing expected vs unexpected errors
- Full stack trace capture for unexpected errors
- Session tracking for debugging

Usage:
    from src.error_logger import log_web_error, ErrorLogger

    # Simple usage (uses global logger)
    log_web_error("function_name", exception, session_id="abc123")

    # Or create custom logger instance
    logger = ErrorLogger()
    logger.log("function_name", exception, session_id="abc123")
"""

import sys
import traceback
from datetime import datetime
from typing import Optional
from src.multiuser_config import get_config
from src.version import VERSION


class ErrorLogger:
    """Centralized error logger with MySQL and stderr support."""

    def __init__(self):
        """Initialize error logger."""
        self.config = get_config().error_logging
        self._mysql_connection = None
        self._mysql_available = False
        self._mysql_checked = False

    def _ensure_mysql_connection(self):
        """Ensure MySQL connection is established (lazy initialization).

        Returns:
            True if MySQL is available, False otherwise
        """
        if self._mysql_checked:
            return self._mysql_available

        self._mysql_checked = True

        # Only attempt MySQL if configured
        if self.config.type not in ('mysql', 'both'):
            return False

        if self.config.mysql is None:
            return False

        try:
            import mysql.connector
            from mysql.connector import Error

            # Build connection parameters
            conn_params = {
                'user': self.config.mysql.user,
                'database': self.config.mysql.database,
                'autocommit': True
            }

            # Use Unix socket if specified, otherwise use host/port
            if self.config.mysql.unix_socket:
                conn_params['unix_socket'] = self.config.mysql.unix_socket
            else:
                conn_params['host'] = self.config.mysql.host
                conn_params['port'] = self.config.mysql.port

            # Add password if provided
            if self.config.mysql.password:
                conn_params['password'] = self.config.mysql.password

            self._mysql_connection = mysql.connector.connect(**conn_params)
            self._mysql_available = True
            return True

        except ImportError:
            sys.stderr.write(
                "Warning: mysql-connector-python not installed. "
                "Install with: pip install mysql-connector-python\n"
                "Falling back to stderr logging only.\n"
            )
            sys.stderr.flush()
            return False

        except Exception as e:
            sys.stderr.write(
                f"Warning: Failed to connect to MySQL: {e}\n"
                f"Falling back to stderr logging only.\n"
            )
            sys.stderr.flush()
            return False

    def _is_expected_error(self, exception: Exception) -> bool:
        """Check if an error is expected (syntax/lexical).

        Args:
            exception: The exception to check

        Returns:
            True if this is an expected error type
        """
        if self.config.log_expected_errors:
            return False

        exception_type = type(exception).__name__
        return exception_type in self.config.expected_error_types

    def log(self,
            context: str,
            exception: Exception,
            session_id: Optional[str] = None,
            user_agent: Optional[str] = None,
            request_path: Optional[str] = None) -> None:
        """Log an error to configured destinations.

        Args:
            context: Function/method where error occurred (e.g., "_menu_run")
            exception: The exception that occurred
            session_id: Optional session ID for tracking
            user_agent: Optional user agent string
            request_path: Optional request path
        """
        is_expected = self._is_expected_error(exception)
        error_type = type(exception).__name__
        message = str(exception)

        # Get stack trace for unexpected errors
        stack_trace = None
        if not is_expected:
            stack_trace = traceback.format_exc()

        # Log to stderr (always, or when configured)
        if self.config.type in ('stderr', 'both'):
            self._log_to_stderr(context, error_type, message, stack_trace, is_expected)

        # Log to MySQL (if configured and available)
        if self.config.type in ('mysql', 'both'):
            self._log_to_mysql(
                context=context,
                error_type=error_type,
                message=message,
                stack_trace=stack_trace,
                is_expected=is_expected,
                session_id=session_id,
                user_agent=user_agent,
                request_path=request_path
            )

    def _log_to_stderr(self,
                       context: str,
                       error_type: str,
                       message: str,
                       stack_trace: Optional[str],
                       is_expected: bool) -> None:
        """Log error to stderr.

        Args:
            context: Function/method where error occurred
            error_type: Exception type name
            message: Error message
            stack_trace: Full stack trace (if available)
            is_expected: Whether this is an expected error
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expected_flag = "[EXPECTED]" if is_expected else "[UNEXPECTED]"

        sys.stderr.write(f"\n{'='*70}\n")
        sys.stderr.write(f"MBASIC WEB ERROR {expected_flag}\n")
        sys.stderr.write(f"{timestamp} | {context}\n")
        sys.stderr.write(f"{'='*70}\n")
        sys.stderr.write(f"Type: {error_type}\n")
        sys.stderr.write(f"Message: {message}\n")

        if stack_trace:
            sys.stderr.write(f"\nStack Trace:\n{stack_trace}\n")

        sys.stderr.write(f"{'='*70}\n\n")
        sys.stderr.flush()

    def _log_to_mysql(self,
                      context: str,
                      error_type: str,
                      message: str,
                      stack_trace: Optional[str],
                      is_expected: bool,
                      session_id: Optional[str],
                      user_agent: Optional[str],
                      request_path: Optional[str]) -> None:
        """Log error to MySQL database.

        Args:
            context: Function/method where error occurred
            error_type: Exception type name
            message: Error message
            stack_trace: Full stack trace (if available)
            is_expected: Whether this is an expected error
            session_id: Session ID
            user_agent: User agent string
            request_path: Request path
        """
        if not self._ensure_mysql_connection():
            return

        try:
            cursor = self._mysql_connection.cursor()

            query = """
                INSERT INTO web_errors
                (timestamp, session_id, error_type, is_expected, context,
                 message, stack_trace, user_agent, request_path, version)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                session_id,
                error_type,
                is_expected,
                context,
                message,
                stack_trace,
                user_agent,
                request_path,
                VERSION
            )

            cursor.execute(query, values)
            cursor.close()

        except Exception as e:
            # If MySQL logging fails, at least log to stderr
            sys.stderr.write(f"Warning: Failed to log to MySQL: {e}\n")
            sys.stderr.flush()

    def __del__(self):
        """Clean up MySQL connection on deletion."""
        if self._mysql_connection and self._mysql_connection.is_connected():
            self._mysql_connection.close()


# Global error logger instance
_logger: Optional[ErrorLogger] = None


def get_logger() -> ErrorLogger:
    """Get the global error logger instance (lazy-loaded).

    Returns:
        ErrorLogger instance
    """
    global _logger
    if _logger is None:
        _logger = ErrorLogger()
    return _logger


def log_web_error(context: str,
                  exception: Exception,
                  session_id: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  request_path: Optional[str] = None) -> None:
    """Log a web error using the global logger.

    This is the main entry point for error logging throughout the codebase.

    Args:
        context: Function/method where error occurred (e.g., "_menu_run")
        exception: The exception that occurred
        session_id: Optional session ID for tracking
        user_agent: Optional user agent string
        request_path: Optional request path

    Example:
        try:
            # Some operation
            pass
        except Exception as e:
            log_web_error("_menu_run", e, session_id="abc123")
            # Re-raise or handle as needed
    """
    get_logger().log(
        context=context,
        exception=exception,
        session_id=session_id,
        user_agent=user_agent,
        request_path=request_path
    )
