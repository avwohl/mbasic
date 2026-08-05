"""The exceptions a terminal raw-mode read can raise.

Four places put the terminal into raw mode to read from the keyboard, each grew
its own idea of what to catch, they drifted apart, and one of them was wrong in
a way that reached users: ``EDIT`` on piped input died with ``?error: (25,
'Inappropriate ioctl for device')``. They now share this tuple.

Two of the four are left. ``ConsoleIOHandler.input_char``/``input_chars``
(``src/iohandler/console.py``) is the keyboard: ``INKEY$`` and ``INPUT$`` read
through the I/O handler, so their inline copies are gone and the terminal
details live in one place - see docs/dev/KEY_INPUT_ROUTING.md.
``InteractiveMode._read_char`` (EDIT mode) is separate because it reads the
REPL's own terminal rather than a program's input.

The subtle one is ``termios.error``. It is a direct subclass of ``Exception``,
*not* of ``OSError``::

    >>> issubclass(termios.error, OSError)
    False

so ``except OSError`` does not catch "this file descriptor is not a terminal",
which is exactly what happens whenever stdin is a pipe or a file.

The rest:

``AttributeError``
    the stdin replacement has no ``fileno()`` at all.
``ValueError``
    ``fileno()`` on a closed file ("I/O operation on closed file").
``OSError``
    a real ioctl failure, and also ``io.UnsupportedOperation`` from
    ``StringIO.fileno()``, which subclasses it.

``KeyboardInterrupt`` is deliberately not covered: it derives from
``BaseException``, so Ctrl+C still interrupts a read rather than being mistaken
for a terminal problem.
"""

try:
    import termios
    _TERMIOS_ERRORS = (termios.error,)
except ImportError:
    # POSIX-only. On Windows there is no raw mode to fail, and callers fall
    # back to a cooked read.
    _TERMIOS_ERRORS = ()

#: Catch this around tcgetattr/setraw/tcsetattr and degrade to a cooked read.
TERMINAL_ERRORS = (AttributeError, ValueError, OSError) + _TERMIOS_ERRORS
