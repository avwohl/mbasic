#!/bin/bash
#
# Build script for MBASIC 2025 String System
#
# Usage:
#   ./build.sh              # Build library (native)
#   ./build.sh test         # Build and run tests (native)
#   ./build.sh clean        # Clean build artifacts
#   ./build.sh z80          # Cross-build for Z80/CP/M with uc80 + um80 + ul80
#   ./build.sh z80-run      # Cross-build and run it under cpmemu
#   ./build.sh z80-z88dk    # Cross-build with z88dk (alternate toolchain)
#
# uc80 + cpmemu are the preferred Z80/CP/M toolchain; z88dk + tnylpo remain
# supported alternates.  See ../../docs/dev/TOOLCHAIN_POLICY.md.

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
    z80-run)
        make z80-run
        ;;
    z80-z88dk)
        make z80-z88dk
        ;;
    *)
        make clean && make
        echo "Build complete. Run './build.sh test' to run tests."
        ;;
esac
