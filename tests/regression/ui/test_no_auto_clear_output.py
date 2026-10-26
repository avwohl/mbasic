"""No UI clears the output pane on its own (docs/dev/RANDOM_FIXES_TODO.md).

The output scrolls on like a teletype.  Tk used to clear it at RUN, LIST and NEW.
Tk and curses cannot run here (no display, no urwid), so this test reads the
source: the only call of the clear function is the menu item.

This encodes a design goal, not a measurement of real MBASIC 5.21 (which has no
output pane; its terminal output scrolls on).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def calls(path, name):
    text = (ROOT / path).read_text()
    return [m.start() for m in re.finditer(r"self\." + name + r"\(\)", text)]


def test_tk_has_no_automatic_clear():
    assert calls("src/ui/tk_ui.py", "_menu_clear_output") == []


def test_curses_has_no_automatic_clear():
    assert calls("src/ui/curses_ui.py", "_clear_output") == []


def test_web_has_no_automatic_clear():
    assert calls("src/ui/web/nicegui_backend.py", "_clear_output") == []


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
