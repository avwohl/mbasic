# INPUT and INPUT # rules

The interpreter follows MBASIC 5.21. Each rule was measured on the real
binary under cpmemu. The code is in `src/input_fields.py` and
`execute_input` in `src/interpreter.py`.

## Keyboard INPUT

- The prompt ends with "? " unless a comma follows the prompt string.
- A semicolon after the INPUT keyword keeps the cursor on the line after the
  answer. The "? " stays.
- A field can be in quotes. A quoted field can hold commas. The closing quote
  can be missing. Text after a closing quote gives "?Redo from start".
- Blanks around a field are ignored. Blanks inside a number are ignored.
- An empty field is 0 or an empty string.
- `&H` and `&O` numbers are accepted. A value over 16 bits gives the error
  "Overflow".
- A bad number, a quoted number, or a wrong number of fields prints
  "?Redo from start". The prompt shows again. No variable changes.
- A single or double value over 1.7014118E+38 prints "Overflow" and then
  "?Redo from start".
- An integer variable rounds the value (halves away from zero). A value
  outside -32768 to 32767 gives the error "Overflow". There is no Redo.

The Redo uses the same pause as the first prompt: the interpreter sets
`input_prompt` again. No UI needs special code for the Redo.

## INPUT #

The fields come from the file stream, not from one line.

- A line end ends a field. A blank line is an empty field.
- A quoted string runs to the closing quote, also over line ends.
- A number ends at a blank, a comma, or a line end.
- A bad number is read as 0 (as VAL does). There is no Redo.
- A single or double value over the maximum prints "Overflow" and the
  maximum is stored. An integer variable gives the error "Overflow".
- No data left gives the error "Input past end".
