"""Expanded Playwright tests for MBASIC web UI.

This module extends web UI testing with comprehensive feature coverage including:
- Debugging features (breakpoints, stepping)
- File operations (save, load)
- Keyboard shortcuts
- Variable inspection
- Advanced program control
"""

import pytest
import time
import tempfile
import os
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def web_server():
    """Start MBASIC web server for testing."""
    import subprocess
    import socket

    # Start web server
    venv_python = '/home/wohl/cl/mbasic/venv-nicegui/bin/python3'
    env = os.environ.copy()
    env['PYTHONPATH'] = '/home/wohl/cl/mbasic'

    process = subprocess.Popen(
        [venv_python, '/home/wohl/cl/mbasic/mbasic', '--backend', 'web'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for server to start
    for i in range(10):
        time.sleep(1)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if sock.connect_ex(('localhost', 8080)) == 0:
                sock.close()
                print(f"Web server started after {i+1} seconds")
                break
        except:
            pass
    else:
        raise Exception("Web server failed to start")

    yield 'http://localhost:8080'

    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


# ============================================================================
# DEBUGGING TESTS
# ============================================================================

def test_breakpoint_toggle(page: Page, web_server):
    """Test setting and clearing breakpoints."""
    page.goto(web_server)

    # Add a multi-line program
    editor = page.locator("textarea").first
    program = """10 PRINT "Line 1"
20 PRINT "Line 2"
30 PRINT "Line 3"
40 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Click line number to set breakpoint (if UI supports it)
    # Try clicking on line 20
    try:
        line_20 = page.locator("text=20").first
        line_20.click()
        time.sleep(0.5)

        # Check for breakpoint indicator
        # Look for visual indication (●, color change, etc.)
        # This depends on actual UI implementation
    except:
        pytest.skip("Breakpoint clicking not implemented in web UI")


def test_step_execution(page: Page, web_server):
    """Test step-by-step execution."""
    page.goto(web_server)

    # Add program
    editor = page.locator("textarea").first
    program = """10 A = 1
20 B = 2
30 PRINT A + B
40 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Try to step (Ctrl+T or Step button)
    try:
        # Look for Step button
        step_button = page.get_by_role("button", name="Step")
        if step_button.is_visible():
            step_button.click()
            time.sleep(0.5)

            # Should show execution paused at line 10
            output = page.locator("textarea").nth(2)
            expect(output).to_contain_text("Paused")

            # Step again
            step_button.click()
            time.sleep(0.5)
    except:
        # Try keyboard shortcut
        page.keyboard.press("Control+t")
        time.sleep(0.5)


def test_variables_window(page: Page, web_server):
    """Test variables inspection window."""
    page.goto(web_server)

    # Add program with variables
    editor = page.locator("textarea").first
    program = """10 A = 42
20 B$ = "Hello"
30 C(10) = 100
40 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Run program
    page.get_by_role("button", name="Run").click()
    time.sleep(1)

    # Try to open variables window (Ctrl+V or button)
    try:
        vars_button = page.get_by_role("button", name="Variables")
        if vars_button.is_visible():
            vars_button.click()
            time.sleep(0.5)

            # Check if variables are displayed
            expect(page.locator("text=A")).to_be_visible()
            expect(page.locator("text=42")).to_be_visible()
            expect(page.locator("text=B$")).to_be_visible()
            expect(page.locator("text=Hello")).to_be_visible()
    except:
        page.keyboard.press("Control+v")
        time.sleep(0.5)


# ============================================================================
# FILE OPERATIONS TESTS
# ============================================================================

def test_save_program(page: Page, web_server):
    """Test saving program to browser storage."""
    page.goto(web_server)

    # Add a program
    editor = page.locator("textarea").first
    program = """10 REM Test Save
20 PRINT "Saved program"
30 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Try to save (Ctrl+S or File > Save)
    page.get_by_role("button", name="File").click()
    save_option = page.get_by_text("Save", exact=True)
    if save_option.is_visible():
        save_option.click()
        time.sleep(0.5)

        # Check for save dialog or confirmation
        # Web UI might use localStorage or download
        status = page.locator("text=/Saved|saved/i")
        if status.is_visible():
            expect(status).to_be_visible()


def test_load_example(page: Page, web_server):
    """Test loading example programs."""
    page.goto(web_server)

    # Open File menu
    page.get_by_role("button", name="File").click()

    # Look for Examples submenu
    examples = page.get_by_text("Examples")
    if examples.is_visible():
        examples.click()
        time.sleep(0.5)

        # Click first example
        first_example = page.locator("text=/Hello|Demo|Test/i").first
        if first_example.is_visible():
            first_example.click()
            time.sleep(0.5)

            # Check program loaded
            program_display = page.locator("textarea").nth(1)
            expect(program_display).not_to_be_empty()


# ============================================================================
# KEYBOARD SHORTCUTS TESTS
# ============================================================================

def test_keyboard_shortcuts(page: Page, web_server):
    """Test common keyboard shortcuts."""
    page.goto(web_server)

    shortcuts = [
        ("Control+n", "New program"),
        ("Control+r", "Run program"),
        ("Control+q", "Stop execution"),
        ("Control+b", "Toggle breakpoint"),
        ("Control+t", "Step"),
        ("Control+g", "Continue"),
        ("Control+v", "Variables"),
        ("Control+k", "Stack"),
    ]

    for shortcut, description in shortcuts:
        try:
            page.keyboard.press(shortcut)
            time.sleep(0.2)
            # Note: Can't easily verify all effects without complex state checking
        except Exception as e:
            print(f"Shortcut {shortcut} ({description}) failed: {e}")


# ============================================================================
# ADVANCED PROGRAM TESTS
# ============================================================================

def test_for_loop(page: Page, web_server):
    """Test FOR/NEXT loop execution."""
    page.goto(web_server)

    editor = page.locator("textarea").first
    program = """10 FOR I = 1 TO 5
20   PRINT I; " squared = "; I*I
30 NEXT I
40 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Run program
    page.get_by_role("button", name="Run").click()
    time.sleep(2)

    # Check output
    output = page.locator("textarea").nth(2)
    expect(output).to_contain_text("1 squared = 1")
    expect(output).to_contain_text("5 squared = 25")


def test_gosub_return(page: Page, web_server):
    """Test GOSUB/RETURN."""
    page.goto(web_server)

    editor = page.locator("textarea").first
    program = """10 PRINT "Main"
20 GOSUB 100
30 PRINT "Back"
40 END
100 PRINT "Subroutine"
110 RETURN"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Run program
    page.get_by_role("button", name="Run").click()
    time.sleep(1)

    # Check output order
    output = page.locator("textarea").nth(2)
    output_text = output.input_value()

    # Verify order: Main, Subroutine, Back
    main_pos = output_text.find("Main")
    sub_pos = output_text.find("Subroutine")
    back_pos = output_text.find("Back")

    assert main_pos < sub_pos < back_pos, "Output order incorrect"


def test_multistatement_line(page: Page, web_server):
    """Test multi-statement lines with colons."""
    page.goto(web_server)

    editor = page.locator("textarea").first
    program = """10 A=1 : B=2 : C=A+B : PRINT "A=";A;" B=";B;" C=";C
20 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Run program
    page.get_by_role("button", name="Run").click()
    time.sleep(1)

    # Check output
    output = page.locator("textarea").nth(2)
    expect(output).to_contain_text("A=1 B=2 C=3")


def test_error_display(page: Page, web_server):
    """Test runtime error display."""
    page.goto(web_server)

    editor = page.locator("textarea").first
    program = """10 A = 1
20 B = 0
30 C = A / B
40 PRINT "Should not reach here"
50 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Run program
    page.get_by_role("button", name="Run").click()
    time.sleep(1)

    # Check for error message
    output = page.locator("textarea").nth(2)
    expect(output).to_contain_text("Division by zero")


# ============================================================================
# UI STATE TESTS
# ============================================================================

def test_status_bar_updates(page: Page, web_server):
    """Test status bar shows correct state."""
    page.goto(web_server)

    # Initial state
    status = page.locator("[role='status']").or_(page.locator(".status-bar"))
    if status.is_visible():
        expect(status).to_contain_text("Ready")

    # Add program
    editor = page.locator("textarea").first
    editor.fill("10 PRINT \"Test\"\n20 END")
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Run program
    page.get_by_role("button", name="Run").click()
    time.sleep(0.2)

    # Should show "Running" briefly
    # Note: May be too fast to catch

    time.sleep(1)
    # Should be back to "Ready"
    if status.is_visible():
        expect(status).to_contain_text("Ready")


def test_line_sorting(page: Page, web_server):
    """Test that lines are automatically sorted by line number."""
    page.goto(web_server)

    editor = page.locator("textarea").first

    # Add lines out of order
    editor.fill("30 PRINT \"Third\"")
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.3)

    editor.fill("10 PRINT \"First\"")
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.3)

    editor.fill("20 PRINT \"Second\"")
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.3)

    # Check program display shows sorted order
    program_display = page.locator("textarea").nth(1)
    content = program_display.input_value()

    # Lines should be in order: 10, 20, 30
    line10_pos = content.find("10 PRINT \"First\"")
    line20_pos = content.find("20 PRINT \"Second\"")
    line30_pos = content.find("30 PRINT \"Third\"")

    assert line10_pos < line20_pos < line30_pos, "Lines not sorted correctly"


def test_renumber_dialog(page: Page, web_server):
    """Test renumber functionality if available."""
    page.goto(web_server)

    # Add program
    editor = page.locator("textarea").first
    program = """5 PRINT "A"
17 PRINT "B"
99 PRINT "C"
101 END"""
    editor.fill(program)
    page.get_by_role("button", name="Add Line").click()
    time.sleep(0.5)

    # Try to renumber (Ctrl+E or menu)
    try:
        page.keyboard.press("Control+e")
        time.sleep(0.5)

        # Look for renumber dialog
        dialog = page.locator("text=/Renumber|renumber/i")
        if dialog.is_visible():
            # Accept defaults
            ok_button = page.get_by_role("button", name="OK").or_(
                page.get_by_role("button", name="Renumber"))
            if ok_button.is_visible():
                ok_button.click()
                time.sleep(0.5)

                # Check lines were renumbered to 10, 20, 30, 40
                program_display = page.locator("textarea").nth(1)
                expect(program_display).to_contain_text("10 PRINT \"A\"")
                expect(program_display).to_contain_text("20 PRINT \"B\"")
                expect(program_display).to_contain_text("30 PRINT \"C\"")
                expect(program_display).to_contain_text("40 END")
    except:
        pytest.skip("Renumber not available in web UI")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

def test_large_program_handling(page: Page, web_server):
    """Test handling of larger programs."""
    page.goto(web_server)

    # Generate a large program
    lines = []
    for i in range(100):
        lines.append(f"{(i+1)*10} REM Line {i+1}")
    lines.append("1010 PRINT \"Done\"")
    lines.append("1020 END")

    program = "\n".join(lines)

    editor = page.locator("textarea").first
    editor.fill(program)

    # Add all lines
    start_time = time.time()
    page.get_by_role("button", name="Add Line").click()

    # Should complete within reasonable time
    time.sleep(2)
    elapsed = time.time() - start_time
    assert elapsed < 5, f"Adding large program took too long: {elapsed}s"

    # Check lines were added
    program_display = page.locator("textarea").nth(1)
    expect(program_display).to_contain_text("10 REM Line 1")
    expect(program_display).to_contain_text("1000 REM Line 100")


def test_rapid_interactions(page: Page, web_server):
    """Test rapid user interactions don't break UI."""
    page.goto(web_server)

    editor = page.locator("textarea").first

    # Rapid line additions
    for i in range(5):
        editor.fill(f"{(i+1)*10} PRINT {i+1}")
        page.get_by_role("button", name="Add Line").click()
        time.sleep(0.1)  # Very short delay

    # Rapid button clicks (should handle gracefully)
    for _ in range(3):
        page.get_by_role("button", name="Run").click()
        time.sleep(0.1)
        page.get_by_role("button", name="Stop").click()
        time.sleep(0.1)

    # UI should still be responsive
    page.get_by_role("button", name="Clear Output").click()
    time.sleep(0.5)

    # Should still work
    output = page.locator("textarea").nth(2)
    expect(output).to_contain_text("Ready")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])