#!/bin/bash
# Setup script for MBASIC usage tracking database
# Run this on your MySQL server (awohl4 droplet)

set -e

echo "========================================"
echo "MBASIC Usage Tracking Database Setup"
echo "========================================"
echo

# Check if mysql command is available
if ! command -v mysql &> /dev/null; then
    echo "Error: mysql command not found"
    echo "Please install MySQL client: apt-get install mysql-client"
    exit 1
fi

# Get credentials
read -p "MySQL username [mbasic]: " MYSQL_USER
MYSQL_USER=${MYSQL_USER:-mbasic}

read -sp "MySQL password: " MYSQL_PASSWORD
echo

read -p "MySQL host [localhost]: " MYSQL_HOST
MYSQL_HOST=${MYSQL_HOST:-localhost}

read -p "Database name [mbasic_logs]: " DATABASE
DATABASE=${DATABASE:-mbasic_logs}

echo
echo "Configuration:"
echo "  Host: $MYSQL_HOST"
echo "  User: $MYSQL_USER"
echo "  Database: $DATABASE"
echo

read -p "Continue with setup? [y/N]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Setup cancelled"
    exit 0
fi

echo
echo "Creating database and tables..."

# Run the schema script
MYSQL_PWD=$MYSQL_PASSWORD mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" < usage_tracking_schema.sql

if [ $? -eq 0 ]; then
    echo
    echo "✓ Usage tracking database setup complete!"
    echo
    echo "Tables created:"
    echo "  - page_visits"
    echo "  - ide_sessions"
    echo "  - program_executions"
    echo "  - feature_usage"
    echo "  - daily_usage_summary"
    echo
    echo "Next steps:"
    echo "1. Deploy updated ConfigMap: kubectl apply -f ../k8s_templates/mbasic-configmap.yaml"
    echo "2. Restart MBASIC pods: kubectl rollout restart deployment/mbasic-web -n mbasic"
    echo "3. Check logs: kubectl logs -f -l app=mbasic-web -n mbasic"
    echo
else
    echo
    echo "✗ Error: Database setup failed"
    exit 1
fi
