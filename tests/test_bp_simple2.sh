#!/bin/bash

# Simple test to check if breakpoints work at all

cat > /tmp/test_bp.bas << 'EOF'
10 PRINT "Before breakpoint"
20 PRINT "At breakpoint"
30 PRINT "After breakpoint"
EOF

echo "Test program:"
cat /tmp/test_bp.bas
echo
echo "This test will add DEBUG output to see if breakpoints are being checked"
echo

# Run with debug enabled
DEBUG=1 python3 mbasic /tmp/test_bp.bas <<< 'RUN
' 2>&1 | tee /tmp/bp_test_output.txt

echo
echo "Checking output..."
if grep -q "Before breakpoint" /tmp/bp_test_output.txt && \
   grep -q "At breakpoint" /tmp/bp_test_output.txt && \
   grep -q "After breakpoint" /tmp/bp_test_output.txt; then
    echo "✓ Program executed all lines"
else
    echo "✗ Program did not execute all lines"
fi
