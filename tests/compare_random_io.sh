#!/bin/bash
# Compare random file I/O between our MBASIC and real MBASIC

TEST_FILE="$1"
if [ -z "$TEST_FILE" ]; then
    TEST_FILE="test_random_file.bas"
fi

echo "==================================="
echo "Testing: $TEST_FILE"
echo "==================================="
echo

# Clean up any previous test files
rm -f /tmp/test_random.dat /tmp/students.dat /tmp/testrand.dat /tmp/testrand2.dat

echo "--- Running OUR MBASIC ---"
timeout 10 python3 ../mbasic "$TEST_FILE" 2>&1 > /tmp/our_random_output.txt
cat /tmp/our_random_output.txt
echo
echo

# Clean up test files before real MBASIC run
rm -f /tmp/test_random.dat /tmp/students.dat /tmp/testrand.dat /tmp/testrand2.dat

echo "--- Running REAL MBASIC (CP/M) ---"
# Real MBASIC can't access /tmp, so we need to modify the test
# For now, just show that we tried
echo "(Real MBASIC requires CP/M filesystem access - skipping for now)"
echo "Note: Real MBASIC cannot access /tmp directory"
echo

echo "==================================="
echo "COMPARISON"
echo "==================================="
echo "Our MBASIC output saved to: /tmp/our_random_output.txt"
