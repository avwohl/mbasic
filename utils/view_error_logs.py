#!/usr/bin/env python3
"""View and analyze error logs from MySQL database.

Usage:
    python3 utils/view_error_logs.py                    # Show recent errors
    python3 utils/view_error_logs.py --all              # Show all errors
    python3 utils/view_error_logs.py --unexpected       # Show only unexpected errors
    python3 utils/view_error_logs.py --session ABC123   # Show errors for specific session
    python3 utils/view_error_logs.py --summary          # Show error summary
    python3 utils/view_error_logs.py --clear            # Clear old error logs (>30 days)
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from multiuser_config import get_config


def get_mysql_connection():
    """Get MySQL connection if configured.

    Returns:
        MySQL connection object or None
    """
    config = get_config()

    if config.error_logging.type not in ('mysql', 'both'):
        print("Error: MySQL logging not configured in multiuser.json", file=sys.stderr)
        print("Set error_logging.type to 'mysql' or 'both'", file=sys.stderr)
        return None

    if config.error_logging.mysql is None:
        print("Error: MySQL configuration missing", file=sys.stderr)
        return None

    try:
        import mysql.connector

        # Build connection parameters
        conn_params = {
            'user': config.error_logging.mysql.user,
            'database': config.error_logging.mysql.database
        }

        # Use Unix socket if specified, otherwise use host/port
        if config.error_logging.mysql.unix_socket:
            conn_params['unix_socket'] = config.error_logging.mysql.unix_socket
        else:
            conn_params['host'] = config.error_logging.mysql.host
            conn_params['port'] = config.error_logging.mysql.port

        # Add password if provided
        if config.error_logging.mysql.password:
            conn_params['password'] = config.error_logging.mysql.password

        conn = mysql.connector.connect(**conn_params)
        return conn

    except ImportError:
        print("Error: mysql-connector-python not installed", file=sys.stderr)
        print("Install with: pip install mysql-connector-python", file=sys.stderr)
        return None

    except Exception as e:
        print(f"Error connecting to MySQL: {e}", file=sys.stderr)
        return None


def show_recent_errors(limit=50, unexpected_only=False, session_id=None):
    """Show recent error logs.

    Args:
        limit: Maximum number of errors to show
        unexpected_only: Show only unexpected errors
        session_id: Filter by session ID
    """
    conn = get_mysql_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id, timestamp, session_id, error_type, is_expected,
                   context, message, LEFT(stack_trace, 200) as stack_preview,
                   version
            FROM web_errors
            WHERE 1=1
        """

        params = []

        if unexpected_only:
            query += " AND is_expected = FALSE"

        if session_id:
            query += " AND session_id = %s"
            params.append(session_id)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        errors = cursor.fetchall()

        if not errors:
            print("No errors found.")
            return

        print(f"\n{'='*80}")
        print(f"Recent Errors (showing {len(errors)} of max {limit})")
        print(f"{'='*80}\n")

        for error in errors:
            print(f"ID: {error['id']}")
            print(f"Time: {error['timestamp']}")
            print(f"Session: {error['session_id']}")
            print(f"Type: {error['error_type']} {'[EXPECTED]' if error['is_expected'] else '[UNEXPECTED]'}")
            print(f"Context: {error['context']}")
            print(f"Message: {error['message']}")

            if error['stack_preview']:
                print(f"Stack: {error['stack_preview']}...")

            print(f"Version: {error['version']}")
            print("-" * 80 + "\n")

    finally:
        conn.close()


def show_error_detail(error_id):
    """Show full details of a specific error.

    Args:
        error_id: Error ID to show
    """
    conn = get_mysql_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM web_errors WHERE id = %s
        """, (error_id,))

        error = cursor.fetchone()

        if not error:
            print(f"Error ID {error_id} not found.")
            return

        print(f"\n{'='*80}")
        print(f"Error Details - ID {error_id}")
        print(f"{'='*80}\n")

        for key, value in error.items():
            if key == 'stack_trace' and value:
                print(f"{key}:")
                print(value)
            else:
                print(f"{key}: {value}")

    finally:
        conn.close()


def show_summary():
    """Show error summary statistics."""
    conn = get_mysql_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor(dictionary=True)

        # Error counts by type
        print("\n" + "="*80)
        print("Error Summary - Last 7 Days")
        print("="*80 + "\n")

        cursor.execute("""
            SELECT
                error_type,
                is_expected,
                COUNT(*) as count,
                COUNT(DISTINCT session_id) as affected_sessions
            FROM web_errors
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY error_type, is_expected
            ORDER BY count DESC
        """)

        print(f"{'Error Type':<30} {'Expected':<12} {'Count':<10} {'Sessions':<10}")
        print("-" * 80)

        for row in cursor.fetchall():
            expected = "Yes" if row['is_expected'] else "No"
            print(f"{row['error_type']:<30} {expected:<12} {row['count']:<10} {row['affected_sessions']:<10}")

        # Recent activity
        print("\n" + "="*80)
        print("Error Activity - Last 24 Hours by Hour")
        print("="*80 + "\n")

        cursor.execute("""
            SELECT
                DATE_FORMAT(timestamp, '%Y-%m-%d %H:00') as hour,
                COUNT(*) as total_errors,
                SUM(CASE WHEN is_expected = FALSE THEN 1 ELSE 0 END) as unexpected_errors
            FROM web_errors
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY hour
            ORDER BY hour DESC
        """)

        print(f"{'Hour':<20} {'Total':<10} {'Unexpected':<15}")
        print("-" * 80)

        for row in cursor.fetchall():
            print(f"{row['hour']:<20} {row['total_errors']:<10} {row['unexpected_errors']:<15}")

    finally:
        conn.close()


def clear_old_logs(days=30):
    """Clear error logs older than specified days.

    Args:
        days: Number of days to keep (default 30)
    """
    conn = get_mysql_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()

        # Count errors to delete
        cursor.execute("""
            SELECT COUNT(*) as count FROM web_errors
            WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days,))

        count = cursor.fetchone()[0]

        if count == 0:
            print(f"No errors older than {days} days found.")
            return

        print(f"Found {count} error(s) older than {days} days.")
        response = input("Delete these errors? (yes/no): ")

        if response.lower() != 'yes':
            print("Cancelled.")
            return

        cursor.execute("""
            DELETE FROM web_errors
            WHERE timestamp < DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days,))

        conn.commit()
        print(f"Deleted {cursor.rowcount} error log(s).")

    finally:
        conn.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='View and analyze MBASIC web error logs',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--all', action='store_true',
                       help='Show all errors (default: last 50)')
    parser.add_argument('--unexpected', action='store_true',
                       help='Show only unexpected errors')
    parser.add_argument('--session', type=str,
                       help='Filter by session ID')
    parser.add_argument('--summary', action='store_true',
                       help='Show error summary statistics')
    parser.add_argument('--detail', type=int, metavar='ID',
                       help='Show full details for specific error ID')
    parser.add_argument('--clear', action='store_true',
                       help='Clear old error logs (older than 30 days)')
    parser.add_argument('--limit', type=int, default=50,
                       help='Maximum number of errors to show (default: 50)')

    args = parser.parse_args()

    if args.summary:
        show_summary()
    elif args.detail:
        show_error_detail(args.detail)
    elif args.clear:
        clear_old_logs()
    else:
        limit = 999999 if args.all else args.limit
        show_recent_errors(
            limit=limit,
            unexpected_only=args.unexpected,
            session_id=args.session
        )


if __name__ == '__main__':
    main()
