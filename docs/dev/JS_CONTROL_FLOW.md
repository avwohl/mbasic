# Control flow in the generated JavaScript

**Status:** Done (GitHub issues 13, 14, 57)
**Test:** `tests/regression/integration/test_js_for_next.py`

## Problem

The generated `main()` is a `switch` on the program counter `_pc`. A case
label was only available for a whole line. These faults followed:

* `10 FOR I=1 TO 3:PRINT I:NEXT I` ran for ever. The loop-back jump went to
  the start of the line, and the FOR statement set the variable again.
* `GOSUB` and `ON GOSUB` in the middle of a line had the same fault.
* A loop that runs zero times skipped the rest of the line that holds the
  NEXT.
* A statement after `GOSUB` or `ON GOSUB` was not written at all.
* `NEXT J,I` stopped the semantic analyzer.
* A bare `NEXT` did not find a loop with an INTEGER variable.

## What the compiler does now

* `_plan_lines` divides each line into steps. These statements need a
  resume point: FOR, GOSUB, ON GOSUB, and a NEXT that closes a FOR. The next
  step gets its own case label when more steps follow on the line. The label is a number from
  100000 up (`CONT_LABEL_BASE`), so the `switch` keeps only integer cases.
  Line numbers end at 65529.
* FOR uses the label as the loop-back target. GOSUB and ON GOSUB use it as
  the return address. A FOR that runs zero times jumps to the label after the
  matching NEXT.
* A statement at the end of the line has no label. The target is the next
  line, as before.
* `_match_for_next` pairs NEXT with FOR by position in the text. It looks
  inside `IF ... THEN ... ELSE` too. A bare NEXT takes the JavaScript name
  of the FOR variable, with the type suffix and the DEFINT type.
* Some IF statements have one of these statements inside, and not at the
  end. The code generator writes jumps and labels for such an IF, not a
  JavaScript `if` block. A case label cannot stand inside a block.
* After GOTO, GOSUB, RETURN, END, SYSTEM and RESUME the code generator
  does not write the code up to the next label, because no jump can reach that code.
* `IF c THEN n ELSE m` jumps to `m` when the condition is false. The
  JavaScript ignored the `ELSE` line number before.
* `SYSTEM` stops the program as `END` does.
* `SemanticAnalyzer._analyze_next` reads the innermost loop again for each
  variable, so `NEXT J,I` passes.

## WHILE and WEND

`_match_while_wend` pairs WEND with WHILE by position in the text, as
`_match_for_next` does for NEXT. WHILE tests the condition and jumps to the
statement after the WEND when the condition is false. WEND jumps back to the
WHILE step. A WHILE that is not the first statement on its line gets a case
label (`while_target`). A WHILE inside an IF makes the IF a flat IF. In the
browser copy the jump back of WEND has the yield check. A WHILE with no WEND
stops with `WHILE without WEND` when the WHILE runs, whatever the condition is. The semantic
analyzer refuses a WEND with no WHILE when the program is compiled.
Test: `tests/regression/integration/test_js_while_wend.py`.

## RESUME and RESUME NEXT

The binary does both at the level of a statement. `RESUME` runs
the statement that failed again, not the line. `RESUME NEXT` goes on with
the next statement, which can be on the same line.

In an IF line, the binary starts the first statement of a THEN or ELSE part
from the IF. It keeps the text pointer of the last statement that it started
(the one behind a colon, or the line start). `RESUME` runs from there, and
`RESUME NEXT` scans from there to the next colon. There is a colon before
each ELSE. So:

* After an error in the condition, or in the first statement of a THEN or
  ELSE part, `RESUME` runs the IF again, condition included. `RESUME NEXT`
  goes on behind the first statement of the THEN part. If that part has one
  statement, the next thing is an ELSE, which skips the rest of the line.
* After an error in a later statement of a part, `RESUME` runs that
  statement, and `RESUME NEXT` goes on with the next statement of the part.
* `WIDTH n,x` fails after it ran, so it counts as a later statement.

`_plan_statement_labels` does this with `clause_tail_after` (in
`src/ast_nodes.py`, the interpreter uses it too). A step in the first place of
a part reports the label of the IF as its program counter
(`LinePlan.pc_override`).

When the program has `RESUME` or `RESUME NEXT` (or `ON ERROR GOSUB`),
`track_statements` is on:

* Each step of a multi-statement line gets a case label (`_plan_statement_labels`)
  and the code sets `_pc` to that label when the step starts.
* The error handler gets `_pc` as the place of the error. `RESUME` jumps
  there. `RESUME NEXT` reads the table `_next_lines`, which maps a line or a
  label to the place to go on.
* An IF with more than one statement in its THEN or ELSE part is a flat IF,
  so that each statement has its own label.
* A program with no `RESUME` gets no extra labels and no extra code.
* A THEN or ELSE part with one statement stays a JavaScript `if`. `RESUME`
  after an error in that statement runs the whole IF again, condition
  included. The binary does the same, because the IF starts that statement.

Test: `tests/regression/integration/test_js_resume_next.py`.

## Line of an error

A fatal error prints `<message> in <line>`. The `catch` block in the program
loop notes the line that ran (`_line_of` maps a case label inside a line back
to its line). ERL uses the same line.

## Differences that remain

* A FOR in a THEN or ELSE part runs its body to the end of the line in the
  interpreter and in the JavaScript, as in real MBASIC. This includes a NEXT
  on a later line. `IF c THEN NEXT ELSE NEXT` inside such a loop can differ
  from real MBASIC (the binary gives NEXT without FOR).
* NEXT pairs with FOR by position in the text. A program that jumps into a
  loop with GOTO and a FOR that has no NEXT in the text can behave
  differently from real MBASIC.

* A NEXT with no loop for its variable is `NEXT without FOR` (error 1) at run
  time, as on the binary. A FOR whose start, end or step is a string, or a
  string loop variable with a number start, is `Type mismatch` (error 13) and
  leaves no loop, so the NEXT after a trapped error gives error 1. The FOR
  runs start, end and step in the order of the text. See section 11 of
  `MBASIC_521_DIVERGENCES_TODO.md`.
