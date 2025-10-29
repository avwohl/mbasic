#!/bin/bash
# Wrapper to run mbasic with debug output visible on terminal and logged
# This makes debug output visible to both user and Claude

# Clear previous debug log
> /tmp/mbasic_debug.log

# Run mbasic with stderr piped through tee (visible + logged)
./mbasic.py "$@" 2>&1 | tee /tmp/mbasic_debug.log
