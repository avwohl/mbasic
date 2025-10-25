#!/usr/bin/env python3
"""Direct test of the notify_confirm_ctrl_c function."""

import sys
sys.path.insert(0, 'src')

from ui.curses_ui import notify_confirm_ctrl_c
import npyscreen
from src.ui.keybindings import HELP_CHAR

class TestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', TestForm, name='Test Help Popup')

class TestForm(npyscreen.Form):
    def create(self):
        self.add(npyscreen.TitleText, name=f'Press {HELP_CHAR!r} to test help popup')

    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers.update({
            ord(HELP_CHAR): self.test_help  # Help key
        })

    def test_help(self, *args):
        """Test the help popup."""
        try:
            notify_confirm_ctrl_c(
                "Help system not yet integrated.\nPress ^P for help (when implemented)",
                title="Help"
            )
            self.display()
        except Exception as e:
            import traceback
            npyscreen.notify_confirm(
                f"ERROR: {e}\n\n{traceback.format_exc()}",
                title="Error Testing Help"
            )

if __name__ == '__main__':
    app = TestApp()
    app.run()
