#!/bin/bash
# Test all games in alphabetical order

cd /home/wohl/cl/mbasic

echo "Testing games directory..."
echo

for game in games/*.bas; do
    basename=$(basename "$game" .bas)
    output=$(timeout 2 python3 mbasic "$game" 2>&1)

    if echo "$output" | grep -q "Syntax error\|RuntimeError\|Error:"; then
        error=$(echo "$output" | grep "Syntax error\|RuntimeError\|Error:" | head -1)
        echo "❌ $basename - $error"
    else
        echo "✓ $basename"
    fi
done
