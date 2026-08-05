"""Undo for a statement that has to be run again.

A statement that pauses for a key is re-executed from the start
(docs/dev/WEB_PROGRAM_KEYBOARD.md), so whatever it already did happens twice.
Most of a BASIC statement is safe to repeat - `execute_print` collects its
output and writes at the end, so nothing has been printed - and the keys it
read are given back by ``KeyReadTransaction``. This covers what is left: the
two things an *expression* can change that a second attempt would change again.

``RND`` advances the generator. `X$=STR$(RND)+INPUT$(1)` that pauses three
times draws four random numbers and uses the last, so a program that waits for
a key silently skips forward in the sequence - and a sequence is the only thing
a random number generator is for. MBASIC's sequence is reproduced exactly here,
which makes skipping forward in it visible rather than merely wrong.

``INPUT$(n,#f)`` advances the file. `X$=INPUT$(1,#1)+INPUT$(1)` that pauses
reads byte 1, pauses, then reads byte 2 on the retry and pairs it with the key.
The file is left one byte further on than the program ever saw.

Both are recorded the first time they happen in an attempt and restored if the
attempt is abandoned. Nothing is recorded when no attempt is in progress, which
is every statement on a terminal - those block for their key instead of pausing
and are never re-run.

Not covered, because a BASIC program cannot see it: ``EOF`` sets a flag when it
reaches the end of a file, and setting it twice is the same as setting it once.
"""


class StatementAttempt:
    """What one attempt at a statement changed, and how to put it back."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Begin a fresh attempt, forgetting the previous one's record."""
        self._rnd_state = None
        self._file_positions = {}

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def note_random(self, runtime):
        """About to draw a random number.

        Snapshotted once per attempt: the state saved is the one before the
        *first* draw, which is what the retry has to start from however many
        times the statement draws.

        MBASIC's generator keeps a seed and three counters and all four move
        together, so the whole lot is saved - see src/mbasic_rnd.py.
        """
        if self._rnd_state is None:
            rnd = getattr(runtime, 'rnd', None)
            if rnd is not None:
                self._rnd_state = rnd.state()

    def note_file_position(self, file_num, handle):
        """About to read from an open file.

        Once per file per attempt, for the same reason - and per *file*,
        because one statement can read two of them.
        """
        if file_num in self._file_positions:
            return
        try:
            self._file_positions[file_num] = handle.tell()
        except (OSError, ValueError, AttributeError):
            # A handle with no seekable position - nothing to restore, and a
            # keyboard read is not worth failing over.
            pass

    # ------------------------------------------------------------------
    # Undo
    # ------------------------------------------------------------------

    def rollback(self, runtime):
        """Put back everything this attempt changed."""
        if self._rnd_state is not None:
            rnd = getattr(runtime, 'rnd', None)
            if rnd is not None:
                rnd.restore(self._rnd_state)

        for file_num, position in self._file_positions.items():
            file_info = getattr(runtime, 'files', {}).get(file_num)
            if not file_info:
                continue                # closed since - nothing to rewind
            try:
                file_info['handle'].seek(position)
            except (OSError, ValueError, AttributeError, KeyError):
                pass
        self.reset()
