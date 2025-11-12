-- MBASIC Web UI Error Logging Database Setup
-- Run this script to create the database and tables for error logging
--
-- Usage:
--   mysql -u root -p < config/setup_mysql_logging.sql
--   or
--   mariadb -u root -p < config/setup_mysql_logging.sql

-- Create database
CREATE DATABASE IF NOT EXISTS mbasic_logs
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE mbasic_logs;

-- Create user (optional - comment out if user already exists)
-- CREATE USER IF NOT EXISTS 'mbasic'@'localhost' IDENTIFIED BY 'your_password_here';
-- GRANT SELECT, INSERT, UPDATE ON mbasic_logs.* TO 'mbasic'@'localhost';
-- FLUSH PRIVILEGES;

-- Create error logging table
CREATE TABLE IF NOT EXISTS web_errors (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    -- Timestamp and session info
    timestamp DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),
    session_id VARCHAR(255),

    -- Error classification
    error_type VARCHAR(100),
    is_expected BOOLEAN DEFAULT FALSE COMMENT 'True for syntax/lexical errors, False for unexpected errors',

    -- Error details
    context VARCHAR(500) COMMENT 'Function/method where error occurred',
    message TEXT COMMENT 'Error message',
    stack_trace TEXT COMMENT 'Full stack trace (for unexpected errors)',

    -- Request context
    user_agent TEXT,
    request_path VARCHAR(500),

    -- Additional metadata
    version VARCHAR(50),
    created_at DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),

    -- Indexes for efficient querying
    INDEX idx_timestamp (timestamp),
    INDEX idx_session (session_id),
    INDEX idx_type (error_type),
    INDEX idx_expected (is_expected),
    INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- Create summary view for monitoring
CREATE OR REPLACE VIEW error_summary AS
SELECT
    DATE(timestamp) as error_date,
    error_type,
    is_expected,
    COUNT(*) as error_count,
    COUNT(DISTINCT session_id) as affected_sessions
FROM web_errors
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(timestamp), error_type, is_expected
ORDER BY error_date DESC, error_count DESC;

-- Create recent errors view
CREATE OR REPLACE VIEW recent_errors AS
SELECT
    id,
    timestamp,
    session_id,
    error_type,
    is_expected,
    context,
    LEFT(message, 200) as message_preview,
    version
FROM web_errors
WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY timestamp DESC
LIMIT 100;

SHOW TABLES;
SELECT 'Database setup complete!' as status;
