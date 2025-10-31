#!/bin/bash
# Test breakpoint with debug output

cat > /tmp/test_bp_dbg.bas << 'EOF'
10 PRINT "Line 10"
20 PRINT "Line 20"
30 PRINT "Line 30"
EOF

# Manually add breakpoint to line 20 in the file
cat > /tmp/test_bp_dbg_with_bp.bas << 'EOF'
●20 PRINT "Line 20"
EOF

echo "Testing breakpoint with DEBUG_BP enabled..."
echo ""
DEBUG_BP=1 timeout 10 expect << 'EXPECT_EOF' 2>&1 | tee /tmp/bp_debug_test.log
log_user 1
set timeout 5

spawn python3 mbasic --backend curses /tmp/test_bp_dbg.bas
sleep 1

# Move to line 2 (line 20)
send "\033\[B"
sleep 0.3

# Toggle breakpoint
send "b"
sleep 0.5

# Run program
send "\x12"
sleep 3

# If breakpoint dialog appears, press 'c' to continue
send "c"
sleep 1

# Exit
send "\x11"

expect eof
EXPECT_EOF

echo ""
echo "=== Debug output ==="
grep -i "breakpoint\|checking line" /tmp/bp_debug_test.log | head -20
