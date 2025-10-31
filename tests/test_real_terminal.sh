#!/bin/bash
# Test in a pseudo-terminal to catch real errors

cat > /tmp/test_help.bas << 'EOF'
10 PRINT "Test"
EOF

# Use script command to run in a real PTY and capture all output
script -q -c "python3 -u mbasic --backend curses /tmp/test_help.bas 2>&1" /tmp/curses_output.log &
SCRIPT_PID=$!

# Wait for it to start
sleep 3

# Send Ctrl+P to the process
sleep 1

# Kill it
kill -9 $SCRIPT_PID 2>/dev/null
wait $SCRIPT_PID 2>/dev/null

# Check for errors in output
echo "=== Checking for errors in output ==="
if grep -i "error\|exception\|traceback\|attribute" /tmp/curses_output.log; then
    echo ""
    echo "=== ERRORS FOUND ==="
    echo "Full output:"
    cat /tmp/curses_output.log
    exit 1
else
    echo "No Python errors found in startup"
fi
