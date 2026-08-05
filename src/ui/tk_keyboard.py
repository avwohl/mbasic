"""The keyboard of a BASIC program running inside the Tk UI.

`INKEY$` and `INPUT$` read through the interpreter's I/O handler
(docs/dev/KEY_INPUT_ROUTING.md). This is what the Tk backend puts behind that
seam, replacing a modal "Enter a single character:" dialog per character - the
only thing `TkIOHandler` had, and unreachable until the routing landed.

The shape of the problem is the same as the curses UI's
(docs/dev/CURSES_PROGRAM_KEYBOARD.md) because the cause is the same: `INPUT$`
is an expression, so unlike the `INPUT` statement it cannot suspend the tick
and resume - it blocks inside a `root.after` callback, with Tk's event loop
stopped behind it.

So a blocking read pumps the event loop itself, with `root.update()`. That is
what keeps keys arriving, the window repainting and the menus alive while a
program waits. The backend sets a flag while this is happening so a tick
scheduled by something the pump ran - Run > Run, say - cannot re-enter the
interpreter underneath us.
"""

#: Ctrl+C. What INPUT$ makes of it is BuiltinFunctions._raise_break's business.
INTERRUPT_CHAR = '\x03'

#: How long each pump waits before looking again. Tk has no "wait for an event
#: with a timeout", so this is a real sleep between updates: short enough to
#: feel immediate, long enough not to spin a core.
_PUMP_SECONDS = 0.02

#: What a terminal sends for the keys Tk reports by name rather than character.
#:
#: MBASIC has no notion of a named key: a CP/M console is a byte stream, and an
#: arrow is whatever escape sequence the terminal transmits. The Windows path
#: already translates scan codes into these same sequences - see
#: _WIN_KEY_TO_ANSI in src/win_console.py - and the two tables are checked
#: against each other in tests/regression/ui/test_tk_keyboard.py, so a change
#: to one cannot quietly disagree with the other.
KEYSYM_TO_ANSI = {
    'Up': '\x1b[A',
    'Down': '\x1b[B',
    'Right': '\x1b[C',
    'Left': '\x1b[D',
    'Home': '\x1b[H',
    'End': '\x1b[F',
    'Prior': '\x1b[5~',     # Page Up
    'Next': '\x1b[6~',      # Page Down
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

#: Keys that only modify the next one. Queueing them would hand a program a
#: keypress nobody made.
_MODIFIERS = frozenset({
    'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R',
    'Meta_L', 'Meta_R', 'Super_L', 'Super_R', 'Caps_Lock', 'Num_Lock',
    'Scroll_Lock', 'Mode_switch', 'ISO_Level3_Shift',
})


class TkKeyboard:
    """Keys for a running program, collected from Tk key events."""

    def __init__(self, get_root, on_wait=None, still_running=None,
                 pump_seconds=_PUMP_SECONDS):
        """
        Args:
            get_root: zero-argument callable returning the Tk root window, or
                None before it exists.
            on_wait: optional zero-argument callable invoked once before a
                blocking read settles in to wait. The backend uses it to make
                sure the program's prompt is on screen before the user is
                asked to answer it.
            still_running: optional zero-argument callable answering "is the
                program still meant to be running". Run > Stop makes this
                False, which is the only way to end a blocking read from the
                UI - so the read reports it as Ctrl+C, the interrupt INPUT$
                already understands.
            pump_seconds: how long to sleep between event-loop pumps.
        """
        self._get_root = get_root
        self._on_wait = on_wait
        self._still_running = still_running
        self._pump_seconds = pump_seconds
        self._pending = []

    # ------------------------------------------------------------------
    # Filling the queue
    # ------------------------------------------------------------------

    def push_from_event(self, event):
        """Queue a Tk <Key> event. Returns True if it was taken.

        A modifier on its own is ignored - the program should see the
        character it modifies, not the shift that made it. Anything Tk gives a
        character for is queued as that character; the rest are translated
        through KEYSYM_TO_ANSI, so an arrow key reaches the program as the
        bytes a terminal would have sent.
        """
        keysym = getattr(event, 'keysym', '') or ''
        if keysym in _MODIFIERS:
            return False

        char = getattr(event, 'char', '') or ''
        if char:
            self._pending.extend(char)
            return True

        sequence = KEYSYM_TO_ANSI.get(keysym)
        if sequence:
            self._pending.extend(sequence)
            return True
        return False

    def push(self, text):
        """Queue characters directly. For tests and for pasted input."""
        self._pending.extend(text)

    def clear(self):
        """Drop queued keys.

        Called when a program starts: keys typed at the previous one are not
        input for this one, and half of an escape sequence certainly is not.
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
            return self._pending.pop(0) if self._pending else ""
        return self.input_chars(1)

    def input_chars(self, count: int, interrupted=None) -> str:
        """Up to count characters, waiting for them. See IOHandler.

        Ends early on the interrupt character, on `interrupted()`, when the UI
        says the program is no longer running, or if there is no window left to
        pump - never blocks forever, because the event loop it is standing in
        front of is the only thing that could rescue it.
        """
        if count <= 0:
            return ""

        chars = ""
        waited = False
        while len(chars) < count:
            if not self._pending:
                if interrupted is not None and interrupted():
                    break
                if self._stopped():
                    # Run > Stop while the program waits. Reported as Ctrl+C so
                    # it becomes the break INPUT$ already knows how to do.
                    chars += INTERRUPT_CHAR
                    break
                if not waited:
                    # Once, and only when actually about to wait: the prompt
                    # the user is answering is still in the output pane's
                    # pending text, and the tick that would flush it has not
                    # returned yet.
                    self._notify_wait()
                    waited = True
                if not self._pump():
                    break               # no window: nothing can ever arrive
                continue
            char = self._pending.pop(0)
            chars += char
            if char == INTERRUPT_CHAR:
                break
        return chars

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _stopped(self):
        if self._still_running is None:
            return False
        try:
            return not self._still_running()
        except Exception:       # noqa: BLE001 - never turn this into an error
            return False

    def _notify_wait(self):
        if self._on_wait is None:
            return
        try:
            self._on_wait()
        except Exception:       # noqa: BLE001 - a repaint must not lose a key
            pass

    def _pump(self):
        """Let Tk deliver events, including the keypress being waited for.

        Returns False when there is no window to pump, which is the caller's
        signal to give up rather than spin.
        """
        import time

        root = self._get_root() if self._get_root is not None else None
        if root is None:
            return False
        try:
            root.update()
        except Exception:       # noqa: BLE001
            # TclError once the window is destroyed - the program outlived its
            # UI, so there is nothing left to read from.
            return False
        if not self._pending:
            time.sleep(self._pump_seconds)
        return True
