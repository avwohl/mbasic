# Control flow in the generated JavaScript

**Status:** Done (GitHub issues 13, 14)
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

## Differences that remain

* The interpreter stops with `FOR Without NEXT` for
  `IF X=1 THEN FOR I=1 TO 3:PRINT I;:NEXT I:PRINT "a"`. Real MBASIC and the
  JavaScript run the loop.
* WHILE and WEND in the JavaScript are a `while` block. They work only when
  both are in the same case, that is on one line.
* NEXT pairs with FOR by position in the text. A program that jumps into a
  loop with GOTO and a FOR that has no NEXT in the text can behave
  differently from real MBASIC.
