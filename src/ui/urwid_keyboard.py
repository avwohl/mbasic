"""The keyboard of a BASIC program running inside the urwid UI.

`INKEY$` and `INPUT$` read through the interpreter's I/O handler
(docs/dev/KEY_INPUT_ROUTING.md). This is what the curses backend puts behind
that seam, so a program gets the keys urwid collected instead of racing urwid
for the same file descriptor.

Two problems have to be solved at once, and they pull in opposite directions.

**Keys typed while a program runs.** The interpreter is ticked from an urwid
alarm every 10ms, so between ticks urwid is reading the terminal itself and
handing keys to the editor widget. A key meant for `INKEY$` would be typed into
the program listing instead. `CursesBackend` installs `divert_keys` as urwid's
``input_filter``, which routes raw bytes here while a program is running, so
they are waiting when the program next asks.

**Keys typed while INPUT$ blocks.** `INPUT$` is an expression, evaluated deep
inside `execute_statement`, so unlike the `INPUT` statement it cannot return to
the event loop and resume - it has to block inside the tick callback, which
means urwid is not reading anything. So this reads the screen directly. That is
safe precisely because the main loop is stopped: nothing else is touching the
fd, and `screen.get_input()` is the same call urwid itself makes.

Blocking inside a tick also means the UI is frozen for the duration, which is
why `on_wait` exists: program output sits in a buffer that the tick only drains
after it returns, so without flushing and repainting first, a program that
prints "PRESS A KEY";  and waits would show nothing at all.
"""

#: Ctrl+C. What INPUT$ makes of it is BuiltinFunctions._raise_break's business,
#: not this module's - here it is just a byte to deliver.
INTERRUPT_CHAR = '\x03'

#: How long each poll of the screen waits. Short enough that an interrupt is
#: noticed promptly, long enough not to spin: the read returns the moment a key
#: arrives, so this is only the idle cost.
_POLL_SECONDS = 0.05


class UrwidKeyboard:
    """Keys for a running program, collected from urwid's terminal."""

    def __init__(self, get_loop, on_wait=None, stop_chars=()):
        """
        Args:
            get_loop: zero-argument callable returning the urwid MainLoop, or
                None before it exists. A callable because the keyboard is
                built alongside the I/O handler, which the UI creates before
                the loop.
            on_wait: optional zero-argument callable invoked once before a
                blocking read settles in to wait. The UI uses it to flush
                pending program output and repaint, so the program's prompt is
                on screen before the user is asked to answer it.
            stop_chars: characters that mean "stop the program" in this UI -
                its stop key, typically ^X. They are delivered to the caller as
                CHR$(3), so the interrupt the user asked for is the same one
                MBASIC already understands. Without this a program blocked in
                INPUT$ could not be stopped at all: the UI is not reading the
                keyboard, this is.
        """
        self._get_loop = get_loop
        self._on_wait = on_wait
        self._stop_chars = set(stop_chars)
        self._pending = []

    # ------------------------------------------------------------------
    # Filling the queue
    # ------------------------------------------------------------------

    def divert_keys(self, keys, raw):
        """urwid ``input_filter``: take raw bytes for the program.

        Returns the keys urwid should still process - empty when the program
        took them. Call only while a program is running; the UI decides that,
        because whether the editor or the program owns the keyboard is a UI
        question, not a keyboard one.
        """
        self.push_raw(raw)
        return []

    def push_raw(self, raw):
        """Queue raw input bytes as characters.

        latin-1 by construction: urwid hands back the byte values it read, and
        one byte becomes one character, so ASC() means the same here as it does
        under the console handler and on Windows. An arrow key arrives as the
        three bytes the terminal sent, which is what a CP/M program polling
        INKEY$ would have seen.
        """
        for byte in raw or ():
            self._pending.append(chr(byte & 0xFF))

    def clear(self):
        """Drop queued keys.

        Called when a program starts and stops: keys typed at one program are
        not input for the next one, and half of an escape sequence certainly is
        not.
        """
        self._pending.clear()

    def pending(self):
        """How many characters are waiting. For tests and status displays."""
        return len(self._pending)

    # ------------------------------------------------------------------
    # The IOHandler side
    # ------------------------------------------------------------------

    def input_char(self, blocking: bool = True) -> str:
        """One character - INKEY$ when non-blocking."""
        if not blocking:
            self._collect(0)
            return self._take()
        got = self.input_chars(1)
        return got

    def input_chars(self, count: int, interrupted=None) -> str:
        """Up to count characters, waiting for them. See IOHandler.

        Returns early on the interrupt character, on `interrupted()`, or if
        there is no screen to read from - never blocks forever, because the
        only thing that could rescue it is the event loop this is standing in
        front of.
        """
        if count <= 0:
            return ""

        chars = ""
        waited = False
        while len(chars) < count:
            if not self._pending:
                if interrupted is not None and interrupted():
                    break
                if not waited:
                    # Once, and only when actually about to wait: the prompt
                    # the user is answering is still sitting in the output
                    # buffer, and the tick that would flush it has not
                    # returned yet.
                    self._notify_wait()
                    waited = True
                if not self._collect(_POLL_SECONDS):
                    break               # no screen: nothing can ever arrive
                continue
            char = self._take()
            chars += char
            if char == INTERRUPT_CHAR:
                break
        return chars

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _take(self):
        """Pop one queued character, mapping a UI stop key to Ctrl+C."""
        if not self._pending:
            return ""
        char = self._pending.pop(0)
        if char in self._stop_chars:
            return INTERRUPT_CHAR
        return char

    def _notify_wait(self):
        if self._on_wait is None:
            return
        try:
            self._on_wait()
        except Exception:       # noqa: BLE001 - a repaint must never lose a key
            pass

    def _collect(self, timeout):
        """Read whatever the terminal has, waiting up to `timeout` seconds.

        Returns False when there is no usable screen, which is the caller's
        signal to give up rather than spin.
        """
        screen = self._screen()
        if screen is None:
            return False
        try:
            screen.set_input_timeouts(max_wait=timeout)
            keys, raw = screen.get_input(True)
        except Exception:       # noqa: BLE001
            # A screen that is stopped, or an urwid that disagrees about the
            # signature, must not turn into a BASIC error. Reporting "no
            # screen" leaves the program with a short read, the same as EOF.
            return False
        self.push_raw(raw)
        return True

    def _screen(self):
        loop = self._get_loop() if self._get_loop is not None else None
        screen = getattr(loop, 'screen', None)
        if screen is None or not getattr(screen, 'started', False):
            return None
        return screen
