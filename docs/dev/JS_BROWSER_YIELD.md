# The browser build gives the page time to run

**Status:** Done (GitHub issue 25)
**Test:** `tests/regression/integration/test_js_browser_yield.py`

## Problem

The generated `main()` ran without a break, except while it waited at INPUT,
LINE INPUT or INPUT$. In a browser this caused two faults:

* A long loop froze the page. The page could not repaint, and the output of
  PRINT did not show until the program ended.
* A loop that polls `INKEY$` never saw a key. The `keydown` handler is a
  separate task, and it cannot run while `main()` runs.

Under Node, `INKEY$` did not read stdin at all, so a polling loop never ended.

## What the compiler does now

### Programs that can loop

A program "can loop" when it has FOR, NEXT, WHILE, WEND, ON ERROR or RESUME,
or a jump (GOTO, GOSUB, ON GOTO, ON GOSUB, IF ... THEN line) to the same
line or an earlier line. The code generator writes the program twice:

* `main()` is the copy that Node runs. It has no check, so its speed is the
  speed of the program before this change.
* `_run(pc)` is the copy for the browser. Before each jump back it counts
  down a budget of 2000 jumps. When the budget is empty it reads the clock.
  If 12 ms have gone by since the last break, `_run` returns the pc of the
  jump. The driver `_main_page()` waits for the page with `setTimeout(0)`
  and calls `_run` again at that pc.

The runtime chooses the copy with `_browser`, which is true when `window`
exists.

The check is not an `await` inside the loop. An `await` point inside the hot
loop made the loop 10 to 20 percent slower under Node, also when the `await`
never ran. The Node copy has no check.

A same-line `WHILE ... WEND` loop is a JavaScript loop and cannot return to
the driver. In the browser copy, WEND has the check with an `await`, and
`_run` is async for such a program.

A program that cannot loop has one `main()` as before. It runs from the
first line to the last line and cannot freeze the page.

### INKEY$

`_inkey()` is async. When the key buffer is empty:

* Browser: it waits for the page with `setTimeout(0)`, so the `keydown`
  handler can put a key in the buffer.
* Node: it reads what is waiting on stdin. It does not wait. A file on stdin
  is read from file descriptor 0. A pipe or a terminal is opened again as
  `/dev/stdin` with `O_NONBLOCK`, so a read with no data gives `EAGAIN`. At
  end of input `INKEY$` gives an empty string for ever, as a keyboard with
  no key pressed does.

A program that uses `INKEY$` has an async `main()` (and `_run`). The call is
`(await _inkey())`.

### DEF FN

A DEF FN is async only when its body calls `INPUT$` or `INKEY$`, or calls
another async DEF FN. Before this change every DEF FN was async in a
program with INPUT. Each call of an async function costs a microtask, so
now plain arithmetic functions stay plain functions.

## Also changed

* The scan for INPUT, LINE INPUT, WRITE, GOSUB, ON GOSUB and the other
  features now looks inside `IF ... THEN ... ELSE`. Before this change an
  `IF X THEN GOSUB 100` left out the GOSUB stack and an
  `IF X THEN INPUT A` made invalid JavaScript.

## Speed under Node

The test program counts 30 million passes through a `FOR` loop in a `FOR`
loop (about 1.6 s), and 30 million jumps of an `IF ... THEN line` loop
(about 0.29 s). Both differ from the code before this change by 5 percent
or less. The variation between runs is about 3 percent.

## Differences that remain

* The page gets time only at a jump back. One statement that takes long (for
  example `SPACE$(255)` in a very large string expression) still runs
  without a break.
* The unit of time is a jump back, not a statement. The budget and the 12 ms
  limit are in `JS_YIELD_BUDGET` and `JS_YIELD_MS`.
* WHILE and WEND across two lines still make invalid JavaScript (see
  `docs/dev/JS_CONTROL_FLOW.md`).
* In the vm stub the same program runs about 15 times slower than under
  plain Node (V8 handles globals of a new context slowly). A real browser
  does not have this limit.
