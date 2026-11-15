#!/usr/bin/env python3
"""
Test that the MySQL code gives PyMySQL the arguments PyMySQL knows.

The web UI used mysql-connector-python. That package names
``ssl.PROTOCOL_TLSv1`` when it is imported. A Python that is linked against
OpenSSL 4 has no such name, so the import fails there. In November 2026 that
was Homebrew's Python on macOS; the Docker image, which is Debian with
OpenSSL 3, still worked. PyMySQL is pure Python and names no old TLS protocol.

The two drivers take different names for the same thing
(``connection_timeout`` and ``connect_timeout``, ``is_connected()`` and
``open``, ``cursor(dictionary=True)`` and ``DictCursor``). A wrong name is a
TypeError only when a server is there to connect to, so these tests put a
recorder in the place of the driver and check the names without a server.

A test against a real MySQL server is not here: it needs Docker.
"""

import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

# The arguments of pymysql.connect that this code is allowed to use.
PYMYSQL_CONNECT_ARGS = {
    'host', 'port', 'unix_socket', 'user', 'password', 'database',
    'autocommit', 'charset', 'connect_timeout', 'ssl_disabled',
}

DRIVER_FILES = [
    'src/error_logger.py',
    'src/usage_tracker.py',
    'src/ui/web/nicegui_backend.py',
    'utils/view_error_logs.py',
]


class FakeCursor:
    lastrowid = 7

    def execute(self, query, params=None):
        self.query = query

    def fetchone(self):
        return (1,)

    def close(self):
        pass


class FakeConnection:
    open = True

    def cursor(self, *args, **kwargs):
        return FakeCursor()

    def close(self):
        self.open = False


@pytest.fixture
def fake_pymysql(monkeypatch):
    """Put a recorder where the driver is, and return the list of calls."""
    calls = []

    def connect(**kwargs):
        calls.append(kwargs)
        return FakeConnection()

    module = types.ModuleType('pymysql')
    module.connect = connect
    monkeypatch.setitem(sys.modules, 'pymysql', module)
    return calls


def test_usage_tracker_arguments(fake_pymysql):
    from src.usage_tracker import UsageTracker

    tracker = UsageTracker({
        'enabled': True,
        'mysql': {'host': 'db', 'port': 3306, 'user': 'mbasic',
                  'password': 'pw', 'database': 'mbasic_logs',
                  'disable_ssl': True},
    })

    assert tracker.db_connection is not None
    (kwargs,) = fake_pymysql
    assert set(kwargs) <= PYMYSQL_CONNECT_ARGS
    assert kwargs['connect_timeout'] == 10
    assert kwargs['ssl_disabled'] is True
    assert kwargs['autocommit'] is True
    assert kwargs['charset'] == 'utf8mb4'
    assert (kwargs['host'], kwargs['port']) == ('db', 3306)


def test_usage_tracker_keeps_tls_when_not_disabled(fake_pymysql):
    """With no disable_ssl, the driver default stays: TLS if the server has it."""
    from src.usage_tracker import UsageTracker

    UsageTracker({'enabled': True, 'mysql': {'host': 'db', 'user': 'mbasic'}})

    (kwargs,) = fake_pymysql
    assert 'ssl_disabled' not in kwargs


def test_error_logger_arguments(fake_pymysql, monkeypatch):
    from src import error_logger
    from src.multiuser_config import ErrorLoggingConfig, MySQLConfig

    config = types.SimpleNamespace(error_logging=ErrorLoggingConfig(
        type='mysql',
        mysql=MySQLConfig(host='db', port=3307, user='mbasic', password='pw'),
    ))
    monkeypatch.setattr(error_logger, 'get_config', lambda: config)

    logger = error_logger.ErrorLogger()
    assert logger._ensure_mysql_connection() is True

    (kwargs,) = fake_pymysql
    assert set(kwargs) <= PYMYSQL_CONNECT_ARGS
    assert kwargs['autocommit'] is True
    assert (kwargs['host'], kwargs['port']) == ('db', 3307)
    assert kwargs['password'] == 'pw'

    # __del__ closes the connection and must not use a mysql.connector name.
    connection = logger._mysql_connection
    logger.__del__()
    assert connection.open is False


@pytest.mark.parametrize('path', DRIVER_FILES)
def test_no_mysql_connector_names(path):
    """The names that only mysql-connector-python has must not come back."""
    text = (PROJECT_ROOT / path).read_text()
    for name in ('mysql.connector', 'connection_timeout',
                 'is_connected(', 'dictionary=True'):
        assert name not in text, f"{path} uses {name}"


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
