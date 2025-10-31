#!/bin/bash
# Automated test of Ctrl+R functionality

rm -f /tmp/mbasic_output_debug.txt

# Use expect to automate the interaction
expect << 'EOF'
set timeout 10
spawn python3 mbasic --backend curses test_program.bas

# Wait for UI to load
sleep 3

# Send Ctrl+R
send "\x12"

# Wait for execution
sleep 2

# Exit with Ctrl+C
send "\x03"

expect eof
EOF

echo ""
echo "=== Debug output file ==="
if [ -f /tmp/mbasic_output_debug.txt ]; then
    cat /tmp/mbasic_output_debug.txt
else
    echo "Debug file not created - Ctrl+R handler may not have been called"
fi
