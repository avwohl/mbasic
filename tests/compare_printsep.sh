#!/bin/bash

cd "$(dirname "$0")"

echo "======================================"
echo "Running with mbasic"
echo "======================================"
python3 ../mbasic printsep.bas

echo ""
echo ""
echo "======================================"
echo "Running with mbasic521"
echo "======================================"
../utils/mbasic521 printsep.bas

echo ""
echo "======================================"
echo "Comparison complete"
echo "======================================"
