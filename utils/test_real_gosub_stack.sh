#!/bin/bash
# Test GOSUB stack depth in real MBASIC 5.21

SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
cd "${SCRIPT_DIR}/../basic/bas_tests"

echo "Testing GOSUB stack depth in MBASIC 5.21"
echo "========================================"
echo ""

for depth in 10 20 30 40 50 60 70; do
    testfile="gosub${depth}.bas"
    echo "Testing depth ${depth}..."
    echo "Running: ${testfile}"
    echo "---"

    # Run with timeout in case it hangs
    # Capture output and look for error messages
    output=$(timeout 30s ../../utils/mbasic521 "${testfile}" 2>&1)
    exit_code=$?

    # Show just the last few lines of output to avoid clutter
    echo "$output" | tail -20

    # Check for GOSUB stack overflow or similar errors
    if echo "$output" | grep -qi "out of memory\|overflow\|stack"; then
        echo "*** STACK OVERFLOW at depth ${depth} ***"
    elif [ $exit_code -eq 124 ]; then
        echo "*** TIMEOUT at depth ${depth} ***"
    else
        # Count the depth lines to see how far it got
        depth_count=$(echo "$output" | grep -c "Depth:")
        max_depth=$(echo "$output" | grep "Maximum depth reached:" | awk '{print $NF}')
        echo "Completed ${depth_count} GOSUB calls, max depth: ${max_depth}"
    fi

    echo ""
    echo "========================================"
    echo ""
done
