#!/usr/bin/env python3
"""
Browser test: a program running in the web UI receives real keystrokes.

The unit and interpreter halves of this live in
tests/regression/ui/test_web_keyboard.py, which needs neither a browser nor
nicegui. What only a browser can show is the part in between: nicegui's
`ui.keyboard` delivering an event of the shape `_handle_program_key` expects,
and the tick timer being cancelled when a program parks on `waiting_for_key`
and recreated when a key arrives. Both are thin, and both are exactly the kind
of thing a nicegui upgrade breaks silently.

Deliberately not under tests/regression/: it starts a server and a browser, so
it takes about half a minute - past the 30-second budget run_regression.py
gives a test, whose timeout handler discards the output.

    python3 tests/playwright/test_web_keyboard_browser.py

Needs `pip install nicegui playwright` and `playwright install chromium`.
"""

import socket
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

#: Exit code 2 tells a caller the test could not run, rather than passing.
SKIP = 2
PORT = 8531

results = []


def check(condition, label):
    results.append(bool(condition))
    print(f"{'PASS' if condition else 'FAIL'}: {label}")


def wait_for_port(port, timeout=45):
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', port)) == 0:
                return True
        time.sleep(0.5)
    return False


def set_program(page, lines):
    """Put a program in the editor through CodeMirror's own API.

    Typing it races the editor's auto-numbering and line sorting, which is not
    what is under test - and loses characters doing it.
    """
    page.evaluate(
        '''(text) => {
            const cm = document.querySelector('.CodeMirror');
            cm.CodeMirror.setValue(text);
            cm.CodeMirror.getInputField().dispatchEvent(
                new Event('input', {bubbles: true}));
        }''', '\n'.join(lines) + '\n')
    page.wait_for_timeout(700)


def run_program(page):
    """Press the toolbar's Run, not the menu bar's RUN (which only opens)."""
    buttons = page.get_by_role('button', name='RUN')
    if buttons.count() > 1:
        buttons.nth(1).click(timeout=10000)
    else:
        buttons.first.click(timeout=10000)
        page.wait_for_timeout(300)
        item = page.get_by_text('Run Program', exact=True)
        if item.count():
            item.first.click()
    page.wait_for_timeout(1200)


def main():
    from playwright.sync_api import sync_playwright

    server = subprocess.Popen(
        [sys.executable, 'mbasic', '--ui', 'web', '--port', str(PORT)],
        cwd=str(PROJECT_ROOT), stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True)
    try:
        if not wait_for_port(PORT):
            print("SKIP: the web server never came up")
            return SKIP
        time.sleep(2)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page()
            page.goto(f'http://127.0.0.1:{PORT}', timeout=30000)
            page.wait_for_timeout(3500)
            output = page.locator('textarea[readonly]').first

            # Output is built with CHR$ so nothing expected can match the
            # program text itself.
            print("\nINPUT$ pauses the program until a key is pressed")
            print("-" * 60)
            set_program(page, [
                '10 PRINT CHR$(80)+CHR$(82)+CHR$(69)+CHR$(83)+CHR$(83);',
                '20 A$=INPUT$(1)',
                '30 PRINT CHR$(71)+CHR$(79)+CHR$(84);ASC(A$)'])
            run_program(page)

            before = output.input_value()
            body = page.inner_text('body')
            check('PRESS' in before,
                  f"the program ran up to the read (got {before[-40:]!r})")
            check('GOT' not in before, "and stopped there")
            check('Waiting for a keypress' in body,
                  "the status bar says what it is waiting for")

            page.keyboard.press('q')
            page.wait_for_timeout(1500)
            after = output.input_value()
            check('GOT 113' in after or 'GOT113' in after,
                  f"pressing q resumed it with CHR$(113) (got {after[-40:]!r})")

            print("\nINKEY$ sees a key typed while the program runs")
            print("-" * 60)
            set_program(page, [
                '10 FOR I=1 TO 200000',
                '20 A$=INKEY$',
                '30 IF A$<>"" THEN 60',
                '40 NEXT I',
                '50 PRINT CHR$(78)+CHR$(79)+CHR$(78)+CHR$(69):END',
                '60 PRINT CHR$(71)+CHR$(79)+CHR$(84);ASC(A$)'])
            run_program(page)
            page.keyboard.press('z')
            page.wait_for_timeout(2500)
            polled = output.input_value()
            check('GOT 122' in polled or 'GOT122' in polled,
                  f"the polling loop got CHR$(122) (got {polled[-40:]!r})")
            check('NONE' not in polled.split('GOT')[-1],
                  "rather than running to the end without a key")

            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except Exception:
            server.kill()

    failed = results.count(False)
    print("\n" + "=" * 60)
    print(f"Results: {results.count(True)} passed, {failed} failed")
    if failed:
        print("❌ Some tests failed")
        return 1
    print("✅ All tests passed!")
    return 0


if __name__ == '__main__':
    print("The web UI's keyboard, in a browser")
    print("=" * 60)
    try:
        import nicegui        # noqa: F401
    except ImportError:
        print('SKIP: nicegui not installed (pip install "mbasic[web]")')
        sys.exit(SKIP)
    try:
        import playwright     # noqa: F401
    except ImportError:
        print("SKIP: playwright not installed (pip install playwright)")
        sys.exit(SKIP)

    try:
        sys.exit(main())
    except Exception as exc:
        message = str(exc)
        if 'Executable doesn' in message or 'playwright install' in message:
            print(f"SKIP: no browser installed (playwright install chromium)")
            sys.exit(SKIP)
        raise
