#!/bin/bash

# Test script to compare PRINT USING between mbasic and mbasic521

TEST_FILE="tests/print_using_test.bas"

echo "======================================"
echo "Running with mbasic"
echo "======================================"
python3 mbasic "$TEST_FILE"

echo ""
echo ""
echo "======================================"
echo "Running with mbasic521"
echo "======================================"
mbasic521 "$TEST_FILE"

echo ""
echo ""
echo "======================================"
echo "Comparison complete"
echo "======================================"
