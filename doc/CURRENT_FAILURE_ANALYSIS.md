# Parser Failure Analysis - Current Status

**Date**: 2025-10-22
**Parser Success Rate**: 104/215 files (48.4%)
**Remaining Failures**: 111 files (51.6%)

## Executive Summary

The 111 remaining parser failures fall into these main categories:

1. **Missing MBASIC 5.21 Features** (~17 files, 15%) - Legitimate features to implement
2. **Non-MBASIC 5.21 Dialects** (~24 files, 22%) - Should move to bad_not521/
3. **Syntax Errors in Source** (~20 files, 18%) - Malformed/corrupted programs
4. **Complex Edge Cases** (~50 files, 45%) - Need individual investigation

---

## Category 1: Missing MBASIC 5.21 Features to Implement

### 1.1 EOF() Function - 7 files ⭐ HIGH PRIORITY

**Files**: direct.bas, genielst.bas, rbbent27.bas, rbbmin27.bas, rbspurge.bas, rbsutl31.bas, simcvt.bas

**Syntax**: `EOF(filenum)`

**Example**:
```basic
200 IF EOF(1) GOTO 240
150 WHILE NOT EOF(1)
```

**Current Error**: "Unexpected token in expression: EOF_FUNC"

**Implementation**: Add EOF as function token, handle in expression parser as built-in function

---

### 1.2 HEX$() Function - 3 files

**Files**: disasmb.bas, rsj.bas, xref.bas

**Syntax**: `HEX$(number)`

**Example**:
```basic
180 DEF FNZHEX2(I)=RIGHT$("00"+HEX$(I),2)
740 PRINT "configured for ";HEX$(P)
```

**Current Error**: "Unexpected token in expression: HEX"

**Implementation**: Add HEX$ as string function token

---

### 1.3 NAME Statement - 1 file

**Files**: pckget.bas

**Syntax**: `NAME oldfile$ AS newfile$`

**Example**:
```basic
NAME L$ AS L$
NAME "TEMP.DAT" AS "FINAL.DAT"
```

**Current Error**: "Expected COMMA, got AS"

**Implementation**: Parse AS keyword, two filename expressions

---

### 1.4 CHAIN Statement - 1 file

**Files**: e-sketch.bas

**Syntax**: `CHAIN filename$`

**Example**:
```basic
CHAIN "MENU"
CHAIN FIL$
```

**Current Error**: "Unexpected token in statement: CHAIN"

**Implementation**: Parse CHAIN keyword, filename expression

---

### 1.5 SAVE Statement - 1 file

**Files**: krakinst.bas

**Syntax**: `SAVE filename$`

**Example**:
```basic
SAVE "PROGRAM.BAS"
```

**Current Error**: "Unexpected token in statement: SAVE"

**Implementation**: Parse SAVE keyword, filename expression

---

### 1.6 ELSE Edge Cases - 3 files

**Files**: header6.bas, holtwint.bas, ozdot.bas

**Pattern**: ELSE without proper statement terminator

**Example**:
```basic
' Line from header6.bas:23
IF condition THEN stmt ELSE stmt2  ' No : before ELSE, complex pattern
```

**Current Error**: "Expected : or newline, got ELSE"

**Note**: Some ELSE patterns already implemented, these are remaining edge cases

---

## Category 2: Non-MBASIC 5.21 Dialects (Move to bad_not521/)

### 2.1 Multiline IF/THEN - 7 files ✗

**Files**: exitrbbs.bas, fprod.bas, fprod1.bas, mfil.bas, minirbbs.bas, timeout.bas, un-prot.bas

**Pattern**: Structured BASIC with multiline IF blocks

**Example**:
```basic
370 IF F$ = "TW" THEN
380     PRINT "Something"
390 END IF
```

**Why Non-MBASIC**: This is structured BASIC (QuickBASIC, GW-BASIC), not MBASIC 5.21

**Action**: MOVE to bad_not521/

---

### 2.2 Wrong Comparison Operators - 5 files ✗

**Files**: ACEY.bas, acey.bas, birthday.bas, rose.bas, unigrid2.bas

**Pattern**: Using `=>` and `=<` instead of `>=` and `<=`

**Example**:
```basic
1070 IF MO => 25000 OR MO =< -25000 THEN 5900
900 IF W=> V GOTO 920
```

**Current Error**: "Unexpected token in expression: GREATER_THAN"

**Why Non-MBASIC**: Invalid operator syntax

**Action**: MOVE to bad_not521/

---

### 2.3 Decimal Line Numbers - 6 files ✗

**Files**: airmiles.bas, cbasedit.bas, cmprbib.bas, commo1.bas, journal.bas, voclst.bas

**Pattern**: Floating-point line numbers

**Example**:
```basic
1.02 NEXT NUM
5.2E1 R.REC%=R.REC%+1
90.01 REM COMMENT
```

**Current Error**: "Unexpected token in statement: NUMBER"

**Why Non-MBASIC**: Line numbers must be integers in MBASIC 5.21

**Action**: MOVE to bad_not521/

---

### 2.4 Atari OPEN Syntax - 4 files ✗

**Files**: aut850.bas, auto850.bas, gammonb.bas, pckexe.bas

**Pattern**: Atari BASIC file I/O syntax

**Example**:
```basic
20 OPEN #1,8,0,"D:AUTORUN.SYS"  ' Atari syntax
' vs MBASIC 5.21:
OPEN "I",#1,"FILENAME"
```

**Current Error**: "Unexpected token in expression: HASH"

**Why Non-MBASIC**: Atari BASIC specific syntax

**Action**: MOVE to bad_not521/

---

### 2.5 INPUT; Syntax - 3 files ⚠️

**Files**: cpkhex.bas, rc5%.bas, rc5.bas

**Pattern**: INPUT with semicolon instead of comma for prompt

**Example**:
```basic
200 INPUT;"Input hex file "; F$
1640 PRINT I$;I;"=":INPUT; V(I)
```

**Current Error**: "Expected IDENTIFIER, got SEMICOLON"

**Note**: Need to verify if this is valid MBASIC 5.21 or dialect-specific

**Action**: RESEARCH - Check MBASIC 5.21 manual, may be valid syntax

---

## Category 3: Syntax Errors in Source Files

### 3.1 Malformed/Corrupted Source - 6 files

**Files**: bibbld.bas, digiklok.bas, doodle.bas, scenecar.bas, tankie.bas, vocbld.bas

**Examples**:
```basic
' bibbld.bas:30 - REM without line number
30 REM  (incomplete)

' digiklok.bas:111 - Unexpected EOF
111 A=     ' Statement cut off

' doodle.bas:2 - Invalid assignment
2 A=B-     ' Expression incomplete
```

**Current Errors**: Various ("Expected EQUAL, got REM", "Expected EQUAL, got EOF", etc.)

**Action**: MOVE to bad_not521/ - Not valid parseable code

---

### 3.2 Concatenated Keywords (GOTO/CLEAR) - 7 files

**Files**: ONECHECK.bas, aircraft.bas, directry.bas, hangman.bas, m100lf.bas, onecheck.bas, simcvt2.bas

**Pattern**: Keywords run together without spaces (typos)

**Examples**:
```basic
GOTO1500          ' Missing space (should be GOTO 1500)
CLEAR1000         ' Missing comma (should be CLEAR ,1000)
IF...GOTO1500     ' Concatenated
```

**Current Error**: "Expected EQUAL, got NEWLINE"

**Note**: Lexer already splits some concatenated keywords (NEXTI → NEXT I), but not all patterns

**Action**: Could implement broader keyword splitting, or treat as malformed source

---

### 3.3 GOTO Syntax Errors - 2 files

**Files**: DIVISION.bas, division.bas

**Pattern**: GOTO followed by invalid target

**Example**:
```basic
GOTO PRINT ...    ' GOTO followed by statement instead of line number
```

**Current Error**: "Expected line number after GOTO"

**Action**: Likely malformed source

---

### 3.4 Malformed IF Statements - 5 files

**Files**: OTHELLO.bas, batnum.bas, fndtble.bas, poker.bas, sortuser.bas

**Pattern**: IF without proper THEN/GOTO

**Example**: Various malformed IF syntaxes

**Current Error**: "Expected THEN or GOTO after IF condition"

**Action**: Need individual review - may be fixable or may be syntax errors

---

### 3.5 Invalid DEF Syntax - 3 files

**Files**: sink.bas, surround.bas, tanks.bas

**Pattern**: DEF without FN prefix

**Example**:
```basic
DEF SOMETHING(X) = X+1  ' Should be DEF FNSOMETHING(X) = X+1
```

**Current Error**: "DEF function name must start with FN"

**Action**: Source syntax error, programs are invalid

---

## Category 4: Complex Edge Cases (Need Investigation)

### 4.1 Expression/Statement Boundary Errors - 10 files

**Files**: handplot.bas, ic-timer.bas, oldroute.bas, qubic.bas, sdir.bas, search.bas, survival.bas, tab8085.bas, tabintel.bas, trade.bas

**Pattern**: Parser confusion about where expression ends and statement begins

**Current Errors**: Various "or newline, got X"

**Action**: Need individual file review to understand patterns

---

### 4.2 Unknown Statement/Keyword - 6 files

**Files**: battle.bas, mxref.bas, othello.bas, qsolist.bas, unpro2.bas, xref19.bas

**Pattern**: "Expected EQUAL, got IDENTIFIER" - unrecognized statement starts

**Example**:
```basic
' Possibly platform-specific statements or syntax errors
RESET
SWAP
WIDTH LPRINT 255
```

**Action**: Individual review needed

---

### 4.3 Syntax Error in Function Call - 3 files

**Files**: bigcal2.bas, budget.bas, wordpuzl.bas

**Pattern**: "Expected COMMA, got LPAREN"

**Example**: Malformed function call syntax

**Action**: Review specific lines

---

### 4.4 Various Other Errors - 22 files

Individual files with unique errors that need case-by-case investigation.

---

## Recommended Action Plan

### Phase 1: Implement High-Value Features (12 files, ~11%)
1. EOF() function - 7 files
2. HEX$() function - 3 files
3. ELSE edge cases - 3 files
4. NAME statement - 1 file
5. CHAIN statement - 1 file
6. SAVE statement - 1 file

**Estimated Impact**: Could reach 116/215 (54.0%)

---

### Phase 2: Clean Corpus - Move Non-5.21 (22 files, ~20%)
1. Multiline IF/THEN - 7 files
2. Wrong operators (=> =<) - 5 files
3. Decimal line numbers - 6 files
4. Atari OPEN - 4 files

**New Success Rate**: 104/193 (53.9%) after removing invalid files

---

### Phase 3: Handle Malformed Source (14 files, ~13%)
1. Corrupted source - 6 files
2. Concatenated keywords - 7 files (could implement broader splitting)
3. Invalid DEF syntax - 3 files

**Action**: Move to bad_not521/ or attempt fixes

---

### Phase 4: Research and Edge Cases (63 files, ~57%)
Individual investigation needed for complex cases.

---

## Statistics

**Total Failures**: 111 files

**Breakdown by Action**:
- Implement features: ~17 files (15%)
- Move to bad_not521: ~24 files (22%)
- Malformed source: ~14 files (13%)
- Need investigation: ~56 files (50%)

**Potential Maximum Success Rate**:
- After Phase 1 features: ~54% (116/215)
- After Phase 2 cleanup: ~60% (116/193)
- After Phase 3 fixes: ~65% (125/193)
- With all investigations: potentially 70-75%

---

## Notes

- Some files may have multiple issues
- "Other" category contains 22 files with unique errors needing individual review
- INPUT; syntax needs verification - may be valid MBASIC 5.21
- Concatenated keywords could be handled by extending lexer's keyword splitting logic
