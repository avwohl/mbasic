"""Only the NEXT that FOR found can end the loop.

Every expected text was measured on MBASIC 5.21 (com/mbasic.com under cpmemu,
tests/HOW_TO_RUN_REAL_MBASIC.md). FOR scans the text for its NEXT (NXTSCN)
and keeps the text pointer of that NEXT in its stack entry. A NEXT at any other
place is "NEXT without FOR", even when the variable is the right one:

    FOR I=1 TO 3:PRINT I:IF I<3 THEN NEXT ELSE NEXT

The first NEXT (in the THEN part) belongs to the FOR. The NEXT in the ELSE part
is a second NEXT, so the third pass stops with NEXT without FOR. The same holds
for a NEXT that a jump reaches (GOTO 30 over the NEXT of line 20), and for a
FOR in a THEN or ELSE part. Skipping the THEN part does not change which NEXT
the FOR found: IF 0 THEN NEXT ELSE NEXT stops at the first pass.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from basic_runner import NODE, run_interpreter, run_javascript

try:
    import pytest
except ImportError:
    if __name__ == "__main__":
        print("pytest unavailable: NEXT matching tests skipped")
        sys.exit(2)  # tests/run_regression.py counts exit code 2 as a skip
    raise

ALL_THREE = " 1 \n 2 \n 3 \n"
CASES = {
    # the second NEXT of IF ... THEN NEXT ELSE NEXT, in a FOR that is in a THEN part
    "then_part_for_second_next": (
        '10 IF 1 THEN FOR I=1 TO 3:PRINT I:IF I<3 THEN NEXT ELSE NEXT\n20 PRINT "end"\n',
        ALL_THREE + "NEXT without FOR in 10\n"),
    "then_part_for_skipped_first_next": (
        '10 IF 1 THEN FOR I=1 TO 3:PRINT I:IF 0 THEN NEXT ELSE NEXT\n20 PRINT "end"\n',
        " 1 \nNEXT without FOR in 10\n"),
    "then_part_for_never_second_next": (
        '10 IF 1 THEN FOR I=1 TO 3:PRINT I:IF 1 THEN NEXT ELSE NEXT\n20 PRINT "end"\n',
        ALL_THREE + "end\n"),
    "else_part_for": (
        '10 IF 0 THEN PRINT "a" ELSE FOR I=1 TO 3:PRINT I:IF 0 THEN NEXT ELSE NEXT\n'
        '20 PRINT "end"\n',
        " 1 \nNEXT without FOR in 10\n"),
    "statement_after_skipped_next": (
        '10 IF 1 THEN FOR I=1 TO 2:PRINT I:IF 0 THEN NEXT ELSE NEXT:PRINT "p" ELSE PRINT "q"\n'
        '20 PRINT "end"\n',
        " 1 \nNEXT without FOR in 10\n"),
    "next_with_other_statement_in_else": (
        '10 IF 1 THEN FOR I=1 TO 2:PRINT I:IF 0 THEN NEXT ELSE PRINT "e":NEXT\n20 PRINT "end"\n',
        " 1 \ne\nNEXT without FOR in 10\n"),
    # a FOR that is not in a clause
    "top_level_for_skipped_first_next": (
        '10 FOR I=1 TO 3:PRINT I:IF 0 THEN NEXT ELSE NEXT\n20 PRINT "end"\n',
        " 1 \nNEXT without FOR in 10\n"),
    "top_level_for_named_second_next": (
        '10 FOR I=1 TO 3:PRINT I:IF 0 THEN NEXT ELSE NEXT I\n20 PRINT "end"\n',
        " 1 \nNEXT without FOR in 10\n"),
    "top_level_for_both_named": (
        '10 FOR I=1 TO 3:PRINT I:IF 0 THEN NEXT I ELSE NEXT I\n20 PRINT "end"\n',
        " 1 \nNEXT without FOR in 10\n"),
    "top_level_else_next_skipped": (
        '10 FOR I=1 TO 3:IF 0 THEN NEXT ELSE PRINT I\n20 NEXT\n30 PRINT "end"\n',
        " 1 \nNEXT without FOR in 20\n"),
    "next_on_the_next_line": (
        '10 FOR I=1 TO 3\n20 PRINT I:IF 0 THEN NEXT ELSE NEXT\n30 PRINT "end"\n',
        " 1 \nNEXT without FOR in 20\n"),
    "nested_if_next": (
        '10 FOR I=1 TO 3:PRINT I:IF 0 THEN IF 1 THEN NEXT ELSE PRINT "z" ELSE NEXT\n'
        '20 PRINT "end"\n',
        " 1 \nNEXT without FOR in 10\n"),
    # a NEXT in the ELSE part is the one that FOR found when the THEN part has none
    "else_next_is_the_first": (
        '10 FOR I=1 TO 3:PRINT I:IF 0 THEN PRINT "t" ELSE NEXT\n20 PRINT "end"\n',
        ALL_THREE + "end\n"),
    "else_next_then_second_else_next": (
        '10 FOR I=1 TO 3:PRINT I:IF 0 THEN PRINT "t" ELSE NEXT ELSE NEXT\n20 PRINT "end"\n',
        ALL_THREE + "end\n"),
    "then_next_is_the_first": (
        '10 FOR I=1 TO 3:PRINT I:IF 1 THEN NEXT ELSE NEXT\n20 PRINT "end"\n',
        ALL_THREE + "end\n"),
    "skipped_for_and_next_in_then_part": (
        '10 IF 1 THEN FOR I=1 TO 3:PRINT I:IF 0 THEN FOR J=1 TO 2:NEXT ELSE NEXT\n'
        '20 PRINT "end"\n',
        ALL_THREE + "end\n"),
    # a NEXT reached by a jump, or on a later line
    "second_next_on_a_later_line": (
        '10 FOR I=1 TO 3:PRINT I:IF I=2 THEN NEXT\n20 NEXT\n30 PRINT "end"\n',
        " 1 \nNEXT without FOR in 20\n"),
    "next_after_goto": (
        '10 FOR I=1 TO 2:PRINT I:GOTO 30\n20 NEXT\n30 NEXT\n40 PRINT "end"\n',
        " 1 \nNEXT without FOR in 30\n"),
    "next_after_goto_named": (
        '10 FOR I=1 TO 2:PRINT I:GOTO 30\n20 NEXT I\n30 NEXT I\n40 PRINT "end"\n',
        " 1 \nNEXT without FOR in 30\n"),
    "next_after_then_line_number": (
        '10 FOR I=1 TO 2:PRINT I:IF I=1 THEN 30\n20 NEXT I:GOTO 40\n30 NEXT I\n40 PRINT "end"\n',
        " 1 \nNEXT without FOR in 30\n"),
    "two_next_in_a_row": (
        '10 FOR I=1 TO 3:PRINT I:NEXT:NEXT\n20 PRINT "end"\n',
        ALL_THREE + "NEXT without FOR in 10\n"),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_interpreter(tmp_path, name):
    source, expected = CASES[name]
    assert run_interpreter(tmp_path, source) == expected


@pytest.mark.skipif(NODE is None, reason="Node.js is needed to execute generated JavaScript")
@pytest.mark.parametrize("name", sorted(CASES))
def test_javascript(tmp_path, name):
    source, expected = CASES[name]
    assert run_javascript(tmp_path, source) == expected


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
