# Compact source and reserved words

This document tells how the lexer reads source text that has few spaces.
The rules come from the MBASIC 5.21 tokenizer (CRUNCH in `bintrp.mac`).
The tests in `tests/regression/lexer/test_compact_source.py` agree with the
real MBASIC 5.21 binary. We ran each case in the real binary.

## The rule

MBASIC 5.21 does not split a reserved word off the front of a name.

A reserved word is a reserved word only when the next character is not a
letter, a digit or a dot. `TAB(`, `SPC(`, `FN` and `USR` need no delimiter.

A letter that does not start a delimited reserved word starts a name. The
name continues over all letters, digits and dots.

Results in real MBASIC 5.21:

- `PRINTX`, `GOTO30`, `PRINT1`, `IFA=1`, `NEXTI` and `FORI=1TO3` are names.
  A statement that starts with one of them is a syntax error.
- `FORTUNE`, `TOTAL`, `TOX` and `NOTE` are valid variable names.
- `PRINT"A"`, `PRINT(1)` and `PRINT-1` are valid.
- A reserved word directly after a number is valid: `IF A=1THEN 40`,
  `IF A=1AND B=2 THEN 40`, `PRINT 7MOD 3`.
- `1TO3` is the number 1 followed by the name `TO3`. It is a syntax error.
- `FNA(1)` and `DEF FNA(X)` are valid. `PRINTFNA(2)` is the name `PRINTFNA`.

The lexer follows this rule. It does not split `NEXTI` into `NEXT I`. An
earlier attempt did this (see `docs/history/KEYWORD_IDENTIFIER_SPLITTING.md`).
We removed the attempt, because real MBASIC 5.21 does not accept those
programs. Old BASIC dialects that accept them need a conversion script.

## Forms that real MBASIC accepts

- No space after the line number: `10PRINT 1`. The program loaders
  (`ProgramManager.load_from_file`, `merge_from_file`, and the loaders in
  `src/interactive.py`) accept this.
- `1ELSE`: the E of `ELSE` does not start an exponent. The same applies to
  `EQV`. Any other `E` or `D` after a number starts an exponent, and the
  exponent can have no digits (`1E` is 1). `5.E2` is 500.
- `GO TO 30` and `GO SUB 30` (one space, then a delimiter) mean `GOTO` and
  `GOSUB`.

Real MBASIC mishandles `GO  TO` (two spaces: it becomes `GOSUB`), `GO  SUB`
(two spaces: it is not joined) and `GO TO30` (syntax error). The lexer does
not copy these faults. It joins only the form that works.

## Known differences that remain

- Relational operators with spaces or reversed: real MBASIC reads `=>`,
  `=<`, `> =`, `< >` and `> <` as `>=`, `<=`, `>=`, `<>` and `<>`. The lexer
  reads only `>=`, `<=`, `<>` and `><`.
- `1E 5`: real MBASIC skips spaces inside a number and reads 100000.
- Real MBASIC accepts a PRINT list without separators (`PRINT 1 2`,
  `PRINT"A""B"`). The parser rejects some forms.
- `REMARK` is not a keyword in MBASIC 5.21 but the lexer accepts it.
