#!/bin/bash
#
# Build script for MBASIC 2025 String System
#
# Usage:
#   ./build.sh          # Build library
#   ./build.sh test     # Build and run tests
#   ./build.sh clean    # Clean build artifacts
#   ./build.sh z80      # Build for Z80 target (requires z88dk)

case "$1" in
    test)
        make clean && make test
        ;;
    clean)
        make clean
        ;;
    z80)
        make z80
        ;;
    *)
        make clean && make
        echo "Build complete. Run './build.sh test' to run tests."
        ;;
esac