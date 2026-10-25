# PRINT columns, line width and WIDTH

Real MBASIC 5.21 counts the column of each character it sends to the screen or
to a file. PRINT uses the count for TAB, for the comma zones and for the line
wrap. POS(0) shows the count. The interpreter and the JavaScript output
(`--compile-js`) follow the same rules. Issues 20 and 23 are the bug reports.

The rules come from measurements of the real interpreter under cpmemu. The
test programs and the real output are in
`tests/regression/integration/fixtures/print_columns/`. The test is
`tests/regression/integration/test_print_columns.py`.

## Rules for the screen

The default width is 80. `WIDTH n` changes the width. The range is 1 to 255.
The column is 0-based inside the code. POS(0) shows the column plus 1.

* A line wraps late. A line that is exactly full stays as it is until a
  printable character arrives. A newline then does not leave an empty line.
* An item (a string, or a number with its spaces) that does not fit in the
  rest of the line goes whole to the next line. A number counts its leading
  and trailing space. The printer splits an item that is longer than the
  width at the width. If such an item starts in the middle of a line, it
  starts on the next line first.
* `TAB(n)` goes to column n (1-based). If n is more than the width, subtract the width
  until n fits (`TAB(90)` at width 80 is `TAB(10)`). If the
  cursor is already past the target column, a new line starts first. If the
  cursor is at the target column, nothing moves. `TAB(0)` is `TAB(1)`.
* `SPC(n)` prints n spaces. The count is a byte (n modulo 256) and then n
  modulo the width. The spaces wrap one at a time.
* A comma goes to the next multiple of 14. A zone that does not fit
  completely in the line is not used. A comma in the last zone starts a new
  line. At width 80 the last zone starts at column 56, so a comma at column
  56 or more starts a new line.
* After INPUT and LINE INPUT the column is 0, because the user typed Enter.
* A tab character moves to the next multiple of 8. A carriage return sets
  the column to 0. A backspace moves left. The other control characters do
  not move the cursor.

## Rules for files

A file has a width of 255 and these rules are different:

* An item is split at the width. It does not go whole to the next line.
* A comma pads to the next multiple of 14 and wraps. There is no last-zone
  rule.
* TAB and SPC follow the screen rules.

## Where the code is

* `src/print_column.py` has the rules (column, wrap, TAB, comma).
* `Interpreter.execute_print` lays out each item from the real column. It
  evaluates the items one at a time, so `POS(0)` sees the items before it.
* `ColumnTracker` in `src/iohandler/base.py` keeps the cursor column of each
  output handler. It wraps `output`, `input`, `input_line`, `clear_screen`
  and `locate` of every subclass, so the CLI, curses, Tk, web and capturing
  handlers all track the column. A handler that does not use these methods
  to draw text must update `column` itself. The handler has `width` too.
* `Interpreter._screen_line_ended` sets the column to 0 when the program
  receives a keyboard line, and when an interpreter starts. The UIs read
  INPUT answers, so the interpreter does not call `input()` of the handler.
* A file keeps its column in `file_info['col']`.
* The JavaScript runtime has `_col`, `_width`, `_wrap_text` and `_print_list`
  (`JS_PRINT_RUNTIME` in `src/codegen_js_backend.py`). A PRINT item that
  reads POS is a function, so the runtime evaluates it when its turn comes.

## Differences that remain

* The interpreter writes a newline as one `\n`. Real MBASIC writes CR LF and
  an LF alone does not reset the column. `PRINT "ab";CHR$(10);"c"` gives
  POS 4 in real MBASIC and 2 here.
* A tab character in a string goes to the terminal unchanged. Real MBASIC
  sends spaces. The column is the same.
* In a file, real MBASIC counts one column less after a wrap at column 255.
  This affects TAB and POS-like layout in lines longer than 255 characters.
* Real MBASIC accepts `WIDTH 0`. This implementation gives an error.
* The prompt of INPUT does not wrap at the width.
* `WIDTH LPRINT n` and `WIDTH #n, w` are not parsed, and LPRINT does not
  exist. This implementation ignores `WIDTH n, device`.
* The CLS statement does not clear the screen, so it does not touch the
  column.
* PRINT USING does not wrap. It updates the column of the screen or file.
* When an error stops a PRINT in the middle, the items before the error
  appear, as in real MBASIC. Real MBASIC then starts a new line before it
  prints the error message. The error messages of this implementation do
  not check the column, so the message follows the text on the same line.
