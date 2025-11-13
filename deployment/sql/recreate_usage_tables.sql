-- Recreate MBASIC usage tracking tables (without touching existing error logging tables)
USE mbasic_logs;

CREATE TABLE IF NOT EXISTS page_visits (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    page_path VARCHAR(255) NOT NULL,
    referrer VARCHAR(512),
    user_agent VARCHAR(512),
    ip_address VARCHAR(45),
    session_id VARCHAR(64),
    INDEX idx_timestamp (timestamp),
    INDEX idx_page_path (page_path),
    INDEX idx_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS ide_sessions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME,
    end_time DATETIME,
    duration_seconds INT,
    user_agent VARCHAR(512),
    ip_address VARCHAR(45),
    programs_run INT DEFAULT 0,
    lines_executed BIGINT DEFAULT 0,
    errors_encountered INT DEFAULT 0,
    INDEX idx_session_id (session_id),
    INDEX idx_start_time (start_time),
    INDEX idx_duration (duration_seconds)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS program_executions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    program_lines INT,
    execution_time_ms INT,
    lines_executed BIGINT,
    success BOOLEAN,
    error_message TEXT,
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (session_id) REFERENCES ide_sessions(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS feature_usage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    feature_name VARCHAR(64) NOT NULL,
    feature_data JSON,
    INDEX idx_session_id (session_id),
    INDEX idx_feature_name (feature_name),
    INDEX idx_timestamp (timestamp),
    FOREIGN KEY (session_id) REFERENCES ide_sessions(session_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS daily_usage_summary (
    date DATE PRIMARY KEY,
    page_visits INT DEFAULT 0,
    unique_visitors INT DEFAULT 0,
    ide_sessions INT DEFAULT 0,
    programs_run INT DEFAULT 0,
    total_lines_executed BIGINT DEFAULT 0,
    avg_session_duration_seconds INT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
