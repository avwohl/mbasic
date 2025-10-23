#!/bin/bash

cd "$(dirname "$0")"

echo "======================================"
echo "Running with mbasic.py"
echo "======================================"
python3 ../mbasic.py printsep.bas

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
