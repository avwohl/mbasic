#!/bin/bash
# MBASIC Package Build and Test Script
#
# This script builds the MBASIC package and optionally tests it.
# Requires: python3-venv, build, twine
#
# Usage:
#   ./utils/build_package.sh                # Build only
#   ./utils/build_package.sh --test         # Build and test locally
#   ./utils/build_package.sh --test-pypi    # Build and upload to TestPyPI
#   ./utils/build_package.sh --help         # Show help

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Parse arguments
ACTION="build"
if [ "$1" = "--test" ]; then
    ACTION="test"
elif [ "$1" = "--test-pypi" ]; then
    ACTION="testpypi"
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    cat << 'EOF'
MBASIC Package Build and Test Script

Usage:
  ./utils/build_package.sh [OPTIONS]

Options:
  (none)        Build package only
  --test        Build and test installation locally
  --test-pypi   Build and upload to TestPyPI
  --help        Show this help message

Examples:
  # Build package
  ./utils/build_package.sh

  # Build and test locally
  ./utils/build_package.sh --test

  # Upload to TestPyPI for testing
  ./utils/build_package.sh --test-pypi

Notes:
  - Requires python3-venv package
  - For --test-pypi, requires ~/.pypirc with testpypi credentials
  - See docs/dev/DISTRIBUTION_TESTING.md for complete guide

EOF
    exit 0
fi

echo -e "${GREEN}=== MBASIC Package Build Script ===${NC}"
echo

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! python3 -c "import venv" 2>/dev/null; then
    echo -e "${RED}Error: python3-venv not available${NC}"
    echo "Install with: sudo apt install python3-venv"
    exit 1
fi

# Get version
VERSION=$(grep "^VERSION = " src/version.py | cut -d'"' -f2)
echo -e "${GREEN}Building MBASIC version: $VERSION${NC}"
echo

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info
echo "✓ Clean"
echo

# Create build environment
echo -e "${YELLOW}Creating build environment...${NC}"
if [ ! -d "venv-build" ]; then
    python3 -m venv venv-build
    source venv-build/bin/activate
    pip install --quiet --upgrade pip
    pip install --quiet build twine
    echo "✓ Build environment created"
else
    source venv-build/bin/activate
    echo "✓ Using existing build environment"
fi
echo

# Build package
echo -e "${YELLOW}Building package...${NC}"
python3 -m build
echo "✓ Package built"
echo

# Check package
echo -e "${YELLOW}Checking package...${NC}"
python3 -m twine check dist/*
echo

# List dist contents
echo -e "${GREEN}Built packages:${NC}"
ls -lh dist/
echo

# Deactivate build venv
deactivate

if [ "$ACTION" = "build" ]; then
    echo -e "${GREEN}=== Build Complete ===${NC}"
    echo
    echo "Next steps:"
    echo "  1. Test locally:     ./utils/build_package.sh --test"
    echo "  2. Upload to TestPyPI: ./utils/build_package.sh --test-pypi"
    echo "  3. See docs/dev/DISTRIBUTION_TESTING.md for publishing to PyPI"
    exit 0
fi

# Test installation
if [ "$ACTION" = "test" ]; then
    echo -e "${YELLOW}Testing local installation...${NC}"

    # Create test environment
    rm -rf venv-test
    python3 -m venv venv-test
    source venv-test/bin/activate

    echo "Installing package..."
    pip install --quiet dist/mbasic-${VERSION}-py3-none-any.whl

    echo "Testing entry point..."
    if ! command -v mbasic &> /dev/null; then
        echo -e "${RED}Error: mbasic command not found${NC}"
        exit 1
    fi

    echo "Testing --list-backends..."
    mbasic --list-backends

    echo "Testing simple program..."
    cat > /tmp/mbasic_test.bas << 'EOF'
10 PRINT "Package test successful!"
20 FOR I = 1 TO 3
30   PRINT "Count:"; I
40 NEXT I
50 END
EOF

    if mbasic --backend=cli /tmp/mbasic_test.bas; then
        echo -e "${GREEN}✓ Test program executed successfully${NC}"
    else
        echo -e "${RED}✗ Test program failed${NC}"
        deactivate
        exit 1
    fi

    deactivate
    rm -rf venv-test
    rm -f /tmp/mbasic_test.bas

    echo
    echo -e "${GREEN}=== All Tests Passed ===${NC}"
    echo
    echo "Package is ready!"
    echo "See docs/dev/DISTRIBUTION_TESTING.md for publishing instructions."
fi

# Upload to TestPyPI
if [ "$ACTION" = "testpypi" ]; then
    echo -e "${YELLOW}Uploading to TestPyPI...${NC}"

    if [ ! -f "$HOME/.pypirc" ]; then
        echo -e "${RED}Error: ~/.pypirc not found${NC}"
        echo "Create ~/.pypirc with testpypi credentials"
        echo "See docs/dev/DISTRIBUTION_TESTING.md for instructions"
        exit 1
    fi

    source venv-build/bin/activate
    python3 -m twine upload --repository testpypi dist/*
    deactivate

    echo
    echo -e "${GREEN}=== Upload Complete ===${NC}"
    echo
    echo "Test installation from TestPyPI:"
    echo "  python3 -m venv venv-testpypi"
    echo "  source venv-testpypi/bin/activate"
    echo "  pip install --index-url https://test.pypi.org/simple/ mbasic"
    echo "  mbasic --version"
fi
