#!/bin/bash
# Test MBASIC installation in a clean environment
# Simulates fresh Ubuntu install

set -e  # Exit on error

echo "=================================================="
echo "MBASIC Clean Environment Installation Test"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_passed() {
    echo -e "${GREEN}✓ $1${NC}"
    ((TESTS_PASSED++))
}

test_failed() {
    echo -e "${RED}✗ $1${NC}"
    ((TESTS_FAILED++))
}

test_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

echo "Step 1: Check Python availability"
echo "-----------------------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    test_passed "Python3 found: $PYTHON_VERSION"
else
    test_failed "Python3 not found"
    exit 1
fi
echo ""

echo "Step 2: Create clean virtual environment"
echo "-----------------------------------------"
TEST_DIR="/tmp/mbasic_test_$$"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

if python3 -m venv "$TEST_DIR/venv"; then
    test_passed "Virtual environment created"
else
    test_failed "Failed to create virtual environment"
    test_info "Install: sudo apt-get install python3-venv"
    exit 1
fi

# Activate virtual environment
source "$TEST_DIR/venv/bin/activate"
test_passed "Virtual environment activated"
echo ""

echo "Step 3: Check no dependencies installed initially"
echo "--------------------------------------------------"
pip list | grep -E "urwid|tkinter" && test_info "Some packages already present" || test_passed "Clean environment confirmed"
echo ""

echo "Step 4: Install MBASIC from local build (minimal)"
echo "--------------------------------------------------"
# Build the package first
test_info "Building package from source..."
cd "$(dirname "$0")"
rm -rf dist/ build/ *.egg-info 2>/dev/null || true

if python3 -m build 2>&1 | grep -q "Successfully built"; then
    test_passed "Package built successfully"
else
    test_info "Build tool not installed, installing..."
    pip install --quiet build
    if python3 -m build 2>&1 | grep -q "Successfully built"; then
        test_passed "Package built successfully (after installing build)"
    else
        test_failed "Package build failed"
        deactivate
        exit 1
    fi
fi

# Install the built package
WHEEL_FILE=$(ls dist/*.whl 2>/dev/null | head -1)
if [ -f "$WHEEL_FILE" ]; then
    test_passed "Found wheel: $(basename $WHEEL_FILE)"

    if pip install --quiet "$WHEEL_FILE"; then
        test_passed "MBASIC installed (minimal - no optional deps)"
    else
        test_failed "Installation failed"
        deactivate
        exit 1
    fi
else
    test_failed "No wheel file found in dist/"
    deactivate
    exit 1
fi
echo ""

echo "Step 5: Verify MBASIC command is available"
echo "-------------------------------------------"
if command -v mbasic &> /dev/null; then
    test_passed "mbasic command found in PATH"
else
    test_failed "mbasic command not found"
fi

# Try python -m method as well
if python3 -m mbasic --help &> /dev/null; then
    test_passed "python3 -m mbasic works"
else
    test_failed "python3 -m mbasic failed"
fi
echo ""

echo "Step 6: Test --list-backends"
echo "-----------------------------"
BACKENDS_OUTPUT=$(python3 -m mbasic --list-backends 2>&1)
if echo "$BACKENDS_OUTPUT" | grep -q "cli.*Available"; then
    test_passed "CLI backend available"
else
    test_failed "CLI backend not shown as available"
fi

if echo "$BACKENDS_OUTPUT" | grep -q "visual.*Available"; then
    test_passed "Visual backend available"
else
    test_failed "Visual backend not shown as available"
fi

if echo "$BACKENDS_OUTPUT" | grep -q "curses.*Not available"; then
    test_passed "Curses shown as not available (expected - urwid not installed)"
elif echo "$BACKENDS_OUTPUT" | grep -q "curses.*Available"; then
    test_info "Curses available (urwid was already installed)"
fi

if echo "$BACKENDS_OUTPUT" | grep -q "tk.*Available"; then
    test_passed "Tkinter shown as available"
elif echo "$BACKENDS_OUTPUT" | grep -q "tk.*Not available"; then
    test_info "Tkinter not available (python3-tk not installed)"
fi
echo ""

echo "Step 7: Test CLI backend (should work with zero deps)"
echo "------------------------------------------------------"
cat > "$TEST_DIR/test.bas" << 'EOF'
10 PRINT "Hello from MBASIC!"
20 X = 5 + 3
30 PRINT "5 + 3 ="; X
40 END
EOF

if echo -e "LOAD \"$TEST_DIR/test.bas\"\nRUN\nEXIT" | python3 -m mbasic --backend cli 2>&1 | grep -q "Hello from MBASIC"; then
    test_passed "CLI backend executes programs correctly"
else
    test_failed "CLI backend execution failed"
fi
echo ""

echo "Step 8: Test imports work correctly"
echo "------------------------------------"
if python3 -c "import mbasic; print('OK')" 2>&1 | grep -q "OK"; then
    test_passed "Can import mbasic module"
else
    test_failed "Cannot import mbasic module"
fi

# Check that tkinter is NOT imported by default
if python3 << 'PYEOF' 2>&1 | grep -q "tkinter NOT loaded"
import sys
import mbasic
if 'tkinter' in sys.modules:
    print("tkinter WAS loaded")
else:
    print("tkinter NOT loaded")
PYEOF
then
    test_passed "tkinter is NOT imported by default (lazy loading works!)"
else
    test_info "tkinter was imported (may have been pre-loaded)"
fi
echo ""

echo "Step 9: Install with curses support"
echo "------------------------------------"
if pip install --quiet "mbasic[curses]" 2>&1; then
    test_passed "Installed mbasic[curses] successfully"

    # Check if urwid is now installed
    if pip list | grep -q urwid; then
        test_passed "urwid dependency installed"
    else
        test_failed "urwid not installed despite mbasic[curses]"
    fi
else
    test_failed "Failed to install mbasic[curses]"
fi

# Check backends again
BACKENDS_OUTPUT2=$(python3 -m mbasic --list-backends 2>&1)
if echo "$BACKENDS_OUTPUT2" | grep -q "curses.*Available"; then
    test_passed "Curses backend now available after installing urwid"
else
    test_failed "Curses backend still not available"
fi
echo ""

echo "Step 10: Test package metadata"
echo "-------------------------------"
PKG_INFO=$(pip show mbasic)
if echo "$PKG_INFO" | grep -q "Name: mbasic"; then
    test_passed "Package metadata accessible"
fi

VERSION=$(echo "$PKG_INFO" | grep "Version:" | cut -d' ' -f2)
if [ -n "$VERSION" ]; then
    test_passed "Version: $VERSION"
fi

LICENSE=$(echo "$PKG_INFO" | grep "License:" | cut -d' ' -f2)
if [ "$LICENSE" = "0BSD" ]; then
    test_passed "License: 0BSD (correct)"
else
    test_info "License: $LICENSE"
fi
echo ""

echo "Step 11: Check file structure"
echo "------------------------------"
SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])")
if [ -f "$SITE_PACKAGES/mbasic" ]; then
    test_passed "mbasic installed"
else
    test_failed "mbasic not found"
fi

if [ -d "$SITE_PACKAGES/src" ]; then
    test_passed "src/ package installed"
else
    test_failed "src/ package not found"
fi

# Check for key modules
for module in runtime parser interpreter lexer; do
    if [ -f "$SITE_PACKAGES/src/${module}.py" ]; then
        test_passed "src/${module}.py present"
    else
        test_failed "src/${module}.py missing"
    fi
done
echo ""

echo "Step 12: Cleanup"
echo "----------------"
deactivate
rm -rf "$TEST_DIR"
test_passed "Test environment cleaned up"
echo ""

echo "=================================================="
echo "TEST SUMMARY"
echo "=================================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed! MBASIC is ready for PyPI.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Review output above.${NC}"
    exit 1
fi
