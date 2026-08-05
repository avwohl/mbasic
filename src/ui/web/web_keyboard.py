"""The keyboard of a BASIC program running in the web UI.

`INKEY$` and `INPUT$` read through the interpreter's I/O handler
(docs/dev/KEY_INPUT_ROUTING.md). This is what the nicegui backend puts behind
that seam, replacing `input_char()` returning `""` forever.

The web UI is the one backend that cannot solve this by waiting. The curses UI
reads its screen directly while the event loop is stopped; the Tk UI pumps its
loop by hand. Neither is possible here: a keypress arrives from the browser
over a websocket served by the very asyncio loop that ticks the interpreter, so
blocking that loop for a key means the key can never arrive. It is not slow -
it is a deadlock, and it takes every other session on the server with it.

So this handler does not wait. When it cannot answer, it raises
`KeyInputPending`, the interpreter leaves the statement where it is, and the
backend stops ticking until a key shows up. The statement then runs again -
which is exactly what CONT does after a Ctrl+C break in `INPUT$`, so it is a
resume model this interpreter already has rather than one invented here.

That is also why a short read is never returned and nothing is consumed on the
way out: `INPUT$(3)` with two keys queued takes neither of them and asks again
later, or the retry would be reading the third character into a variable that
already has none of the first two.
"""

from src.iohandler.base import KeyInputPending

#: Ctrl+C. What INPUT$ makes of it is BuiltinFunctions._raise_break's business.
INTERRUPT_CHAR = '\x03'

#: Browser key names (KeyboardEvent.key) that are not characters, mapped to
#: what a terminal sends - MBASIC has no notion of a named key. These are the
#: same sequences the Tk and Windows tables produce; the three are checked
#: against each other in tests/regression/ui/test_web_keyboard.py.
BROWSER_KEY_TO_ANSI = {
    'ArrowUp': '\x1b[A',
    'ArrowDown': '\x1b[B',
    'ArrowRight': '\x1b[C',
    'ArrowLeft': '\x1b[D',
    'Home': '\x1b[H',
    'End': '\x1b[F',
    'PageUp': '\x1b[5~',
    'PageDown': '\x1b[6~',
    'Insert': '\x1b[2~',
    'Delete': '\x1b[3~',
    'F1': '\x1bOP',
    'F2': '\x1bOQ',
    'F3': '\x1bOR',
    'F4': '\x1bOS',
    'F5': '\x1b[15~',
    'F6': '\x1b[17~',
    'F7': '\x1b[18~',
    'F8': '\x1b[19~',
    'F9': '\x1b[20~',
    'F10': '\x1b[21~',
    'F11': '\x1b[23~',
    'F12': '\x1b[24~',
}

#: Browser names for keys that do have an obvious character.
_BROWSER_NAMED_CHARS = {
    'Enter': '\r',          # CHR$(13), as a CP/M console sends
    'Tab': '\t',
    'Backspace': '\x08',
    'Escape': '\x1b',
    'Space': ' ',
}


class WebKeyboard:
    """Keys for a running program, collected from browser key events."""

    def __init__(self, on_key=None):
        """
        Args:
            on_key: optional callable invoked after a key is queued. The
                backend uses it to start ticking again, since a program parked
                on KeyInputPending has nothing else to wake it.
        """
        self._pending = []
        self._on_key = on_key

    # ------------------------------------------------------------------
    # Filling the queue
    # ------------------------------------------------------------------

    def push_browser_key(self, key, modifiers=()):
        """Queue a browser KeyboardEvent.key value. Returns True if taken.

        A single character is itself. Ctrl+letter becomes the control
        character, so a program can read Ctrl+C - the browser will not send
        one otherwise. Named keys are translated to terminal sequences, and
        anything left (Shift, Meta, dead keys) is not a keypress a program
        should see.
        """
        if not key:
            return False

        text = None
        if len(key) == 1:
            text = key
            if 'ctrl' in {str(m).lower() for m in modifiers}:
                code = ord(key.upper())
                if 64 < code < 96:          # @A-Z[\]^_ -> 0x00-0x1f
                    text = chr(code - 64)
        elif key in _BROWSER_NAMED_CHARS:
            text = _BROWSER_NAMED_CHARS[key]
        elif key in BROWSER_KEY_TO_ANSI:
            text = BROWSER_KEY_TO_ANSI[key]

        if text is None:
            return False

        self._pending.extend(text)
        if self._on_key is not None:
            self._on_key()
        return True

    def push(self, text):
        """Queue characters directly. For tests and for pasted input."""
        if not text:
            return
        self._pending.extend(text)
        if self._on_key is not None:
            self._on_key()

    def clear(self):
        """Drop queued keys.

        Called when a program starts: keys typed at the previous one are not
        input for this one, and half an escape sequence certainly is not.
        """
        self._pending.clear()

    def pending(self):
        """How many characters are waiting. For tests and status displays."""
        return len(self._pending)

    # ------------------------------------------------------------------
    # The IOHandler side
    # ------------------------------------------------------------------

    def input_char(self, blocking: bool = True) -> str:
        """One character - INKEY$ when non-blocking.

        INKEY$ is the case the web UI serves perfectly: it is defined to
        return "" when no key is pending, which is an answer this handler can
        always give.
        """
        if not blocking:
            return self._pending.pop(0) if self._pending else ""
        return self.input_chars(1)

    def input_chars(self, count: int, interrupted=None) -> str:
        """Up to count characters - or KeyInputPending if there are not enough.

        Raises rather than waits, and consumes nothing when it raises. See the
        module docstring.
        """
        if count <= 0:
            return ""

        if interrupted is not None and interrupted():
            return ""

        # A Ctrl+C anywhere in what is queued ends the read now, even if fewer
        # than count characters have arrived - waiting for the rest would
        # ignore the interrupt the user just asked for.
        head = self._pending[:count]
        if INTERRUPT_CHAR in head:
            cut = head.index(INTERRUPT_CHAR) + 1
            taken, self._pending = self._pending[:cut], self._pending[cut:]
            return ''.join(taken)

        if len(self._pending) < count:
            raise KeyInputPending(
                f"{count} characters wanted, {len(self._pending)} queued")

        taken, self._pending = self._pending[:count], self._pending[count:]
        return ''.join(taken)
