"""The exceptions a terminal raw-mode read can raise.

Four places put the terminal into raw mode to read from the keyboard -
``InteractiveMode._read_char`` (EDIT mode), ``BuiltinFunctions._read_console``
(INPUT$), the ``INKEY$`` builtin, and ``ConsoleIOHandler.input_char``. Each
grew its own idea of what to catch, they drifted apart, and one of them was
wrong in a way that reached users: ``EDIT`` on piped input died with
``?error: (25, 'Inappropriate ioctl for device')``. They now share this tuple.

(``ConsoleIOHandler.input_char`` was long described as the INPUT$ reader. It
is not, and never was: ``BuiltinFunctions`` is built without an I/O handler, so
INPUT$ has always read ``sys.stdin`` itself. Nothing reaches ``input_char`` at
all - its one call site in ``src/`` is ``web_io.py``'s own deprecated
``get_char()`` alias, which has no callers either. See
docs/dev/INPUT_DOLLAR_RAW_READ.md.)

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
