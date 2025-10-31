# NiceGUI Web UI Test Instructions

## Prerequisites

The NiceGUI tests require nicegui to be installed. Since the system uses an externally-managed Python environment, you need to use a virtual environment.

## Setup Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv-nicegui

# Activate virtual environment
source venv-nicegui/bin/activate

# Install dependencies
pip install nicegui>=3.2.0 pytest>=8.0.0 pytest-asyncio>=1.0.0
```

## Running Tests

```bash
# Make sure virtual environment is activated
source venv-nicegui/bin/activate

# Run all tests
python3 -m pytest tests/nicegui/test_mbasic_web_ui.py -v

# Run specific test
python3 -m pytest tests/nicegui/test_mbasic_web_ui.py::test_input_statement -v
```

## Test Coverage

The test suite includes:

1. **test_ui_loads** - Verify UI loads without errors
2. **test_add_program_line** - Test adding BASIC program lines
3. **test_new_program** - Test File > New clears program
4. **test_clear_output** - Test Clear Output button
5. **test_list_program** - Test List Program functionality
6. **test_run_program** - Test program execution with output
7. **test_input_statement** - Test INPUT statement with inline input field

## Manual Testing

If you prefer to test manually:

```bash
# Launch web UI
python3 mbasic --backend web

# Navigate to http://localhost:8080

# Test INPUT statement:
# 1. Type these lines:
#    10 PRINT "Enter your name:"
#    20 INPUT N$
#    30 PRINT "Hello, "; N$
#    40 END
# 2. Click "Add Line" for each
# 3. Click "Run"
# 4. INPUT field should appear below output
# 5. Type your name and press Enter or click Submit
# 6. Verify greeting appears with your name
```

## Expected Results

All 7 tests should pass:
- ✅ UI initialization works
- ✅ Program lines can be added
- ✅ File > New clears program
- ✅ Clear Output works
- ✅ List Program shows lines
- ✅ Program execution produces output
- ✅ INPUT statement shows inline input field

## Troubleshooting

**ModuleNotFoundError: No module named 'nicegui'**
- Make sure you activated the virtual environment
- Run: `source venv-nicegui/bin/activate`
- Verify: `pip list | grep nicegui`

**Tests hang or timeout**
- NiceGUI tests use async/await
- Increase timeout if needed: `pytest -v --timeout=120`

**Import errors**
- Ensure all dependencies are installed
- Run: `pip install -r requirements.txt` in venv
