# Parser Failure Categorization - 123 Remaining Files

**Date**: 2025-10-22
**Context**: After reaching 92/215 (42.8%) success rate

## Executive Summary

Of 123 remaining failures:
- **~36 files** (29%): Legitimate MBASIC 5.21 features to implement
- **~20 files** (16%): Non-MBASIC 5.21 dialects to move
- **~40 files** (33%): Need individual review (syntax errors, malformed, uncertain)
- **~27 files** (22%): Platform-specific/various issues

## High-Impact MBASIC 5.21 Features to Implement

### 1. PRINT# Statement - 11 Files ⭐
**Priority: HIGH** - File output to devices/files

**Syntax**: `PRINT #filenum, expression [, expression...]`

**Examples**:
```basic
1290 A=80:PRINT#1,A
PRINT #2, "Hello", X, Y$
```

**Current Error**: "Expected EQUAL, got NUMBER"

**Files**: lst8085.bas, lstintel.bas, lsttdl.bas, rbbmin27.bas, rbspurge.bas, rbsutl31.bas, sfamove.bas, sfaobdes.bas, sfavoc.bas, sortuser.bas, xformer.bas

**Implementation**: Similar to PRINT but with file number

---

### 2. ELSE Statement Edge Cases - 11 Files ⭐
**Priority: HIGH** - Multiple ELSE patterns remain

**Patterns**:
```basic
' Pattern 1: Colon before ELSE in single-line IF
IF F2>F1 THEN S$="+" :ELSE S$="-"

' Pattern 2: No colon before ELSE
IF A$="N" THEN RUN"MENU" :ELSE 40

' Pattern 3: ELSE with line number (no colon)
IF PEEK(8220)=X9 THEN RETURN :ELSE 2110
```

**Current Errors**:
- "Unexpected in statement: ELSE" (8 files)
- "Expected : or newline, got ELSE" (3 files)

**Files**: ADDITION.bas, NUMBER.bas, POKER.bas, addition.bas, number.bas, poker.bas, survival.bas, tricks.bas, header6.bas, holtwint.bas, ozdot.bas

**Note**: Already implemented some ELSE patterns, these are remaining edge cases

---

### 3. NAME Statement - 6 Files
**Priority: MEDIUM** - File renaming

**Syntax**: `NAME oldfile$ AS newfile$`

**Example**:
```basic
440 NAME L$ AS L$
NAME "TEMP.DAT" AS "FINAL.DAT"
```

**Current Error**: "Expected EQUAL, got IDENTIFIER (AS)"

**Files**: mxref.bas, othello.bas, simcvt2.bas, tabzilog.bas, trade.bas, tvigammo.bas

**Implementation**: Parse AS keyword, two filename expressions

---

### 4. EOF() Function - 5 Files
**Priority: MEDIUM** - End-of-file testing

**Syntax**: `EOF(filenum)`

**Examples**:
```basic
200 IF EOF(1) GOTO 240
150 WHILE NOT EOF(1)
430 IF EOF(1) THEN 450
```

**Current Error**: "Unexpected in expression: EOF_FUNC"

**Files**: direct.bas, genielst.bas, rbbent27.bas, sink.bas, timeout.bas

**Implementation**: Add EOF as function token, handle in expression parser

---

### 5. HEX$() Function - 3 Files
**Priority: LOW** - Hexadecimal conversion

**Syntax**: `HEX$(number)`

**Examples**:
```basic
180 DEF FNZHEX2(I)=RIGHT$("00"+HEX$(I),2)
740 PRINT "configured for ";HEX$(P)
```

**Current Error**: "Unexpected in expression: HEX"

**Files**: disasmb.bas, rsj.bas, xref.bas

**Implementation**: Add HEX$ as string function

---

## Non-MBASIC 5.21 Files to Move (~20 Files)

### 1. Multiline IF/THEN - 7 Files ✗
**Structured BASIC** feature (not MBASIC 5.21)

**Pattern**: IF condition THEN followed by newline
```basic
370 IF F$ = "TW" THEN
380     PRINT "Something"
```

**Files**: exitrbbs.bas, fprod.bas, fprod1.bas, hanoi1.bas, ibmxfr.bas, minirbbs.bas, xref19.bas

**Action**: MOVE to bad_not521/ - This is structured BASIC

---

### 2. Wrong Comparison Operators - 5 Files ✗
**Syntax error** or non-standard dialect

**Pattern**: `=>` and `=<` instead of `>=` and `<=`
```basic
1070 IF MO => 25000 OR MO =< -25000 THEN 5900
900 IF W=> V GOTO 920
```

**Files**: ACEY.bas, acey.bas, birthday.bas, satelite.bas, unigrid2.bas

**Action**: MOVE to bad_not521/ - Invalid operator syntax

---

### 3. Decimal Line Numbers - 5 Files ✗
**Non-standard** - Line numbers must be integers

**Pattern**: Floating-point line numbers
```basic
1.02 NEXT NUM
5.2E1 R.REC%=R.REC%+1
90.01 REM COMMENT
```

**Files**: cbasedit.bas, cmprbib.bas, commo1.bas, fxparms.bas, journal.bas

**Action**: MOVE to bad_not521/ - Not valid BASIC

---

### 4. Atari OPEN Syntax - 3 Files ✗
**Atari BASIC** file syntax

**Pattern**: `OPEN #n,mode,aux,"file"` vs MBASIC `OPEN "mode",#n,"file"`
```basic
20 OPEN #1,8,0,"D:AUTORUN.SYS"
```

**Files**: aut850.bas, auto850.bas, pckexe.bas

**Action**: MOVE to bad_not521/ - Atari BASIC

---

## Files Needing Research/Review (~40 Files)

### 1. GOTO Syntax Errors - 9 Files
**Mixed**: Some are typos, some might be non-5.21

**Patterns**:
```basic
GOTO1500          ' Missing space (typo)
GOTO PRINT ...    ' GOTO followed by statement (invalid)
IF ... THEN PRINT E1$:GOTO1500   ' Concatenated
```

**Files**: ONECHECK.bas, aircraft.bas, directry.bas, old.bas, satelit.bas, spcwrtrm.bas, unigrid.bas, DIVISION.bas, division.bas

**Action**: Review individually - some may be fixable with better tokenization, others are genuine errors

---

### 2. Malformed Source Files - 8 Files
**Corrupted or incomplete** source code

**Examples**:
```basic
6 Monterey Cir.     ' Comment without line number
RE                   ' Incomplete statement
R                    ' Incomplete statement
```

**Files**: battle.bas, othello.bas, unpro2.bas, digiklok.bas, tankie.bas, bibbld.bas, vocbld.bas, doodle.bas (partial)

**Action**: MOVE to bad_not521/ - Not valid parseable code

---

### 3. INPUT; Syntax - 3 Files
**Uncertain** - Need to verify if valid MBASIC 5.21

**Pattern**: `INPUT;` with semicolon instead of comma
```basic
200 INPUT;"Input hex file "; F$
1640 PRINT I$;I;"=":INPUT; V(I)
```

**Files**: cpkhex.bas, rc5%.bas, rc5.bas

**Action**: RESEARCH - Check MBASIC 5.21 manual for INPUT; syntax

---

### 4. CLEAR Syntax - 5 Files
**Likely typo**: Missing comma in CLEAR statement

**Pattern**: `CLEAR1000` should be `CLEAR ,1000`
```basic
60 CLEAR1000:PK=12      ' Should be: CLEAR ,1000
```

**Files**: BACKGAMM.bas, asm2mac.bas, backgamm.bas, hangman.bas, unpro2.bas

**Action**: These are probably user syntax errors, but verify

---

### 5. Various Platform-Specific - 15 Files
**Mixed bag** of features needing individual review

**Examples**:
- `RESET` - Device reset command
- `POKE 0A000H,0` - Hex address (should be &HA000)
- `SWAP EA(I),EB(I)` - SWAP statement
- `READ #1,D7;D4` - Non-standard file read
- `NULL(30)` - Null printer control
- `DEF USR0=` - Machine language subroutine (valid in MBASIC 5.21)
- `WIDTH LPRINT 255` - Printer width (valid syntax?)
- `CHAIN FIL$` - Chain to program (valid in MBASIC 5.21)
- `ON...GO TO` (with space) vs `ON...GOTO`

**Files**: Multiple (see detailed list)

**Action**: Review each individually to determine if MBASIC 5.21 or not

---

## Recommended Implementation Priority

### Phase 1 - High Impact (22 files)
1. **PRINT# Statement** (11 files) - Critical for file I/O
2. **ELSE Edge Cases** (11 files) - Control flow completion

### Phase 2 - Medium Impact (11 files)
3. **NAME Statement** (6 files) - File operations
4. **EOF() Function** (5 files) - File testing

### Phase 3 - Low Impact (3 files)
5. **HEX$() Function** (3 files) - Utility function

### Phase 4 - Cleanup (20+ files)
6. **Move non-5.21 dialects** (20 files minimum)
7. **Move malformed files** (8 files)
8. **Research uncertain cases** (40 files)

---

## Implementation Notes

### PRINT# vs PRINT
PRINT# is file output, syntax: `PRINT #n, data`
- Similar to PRINT but outputs to file/device
- Supports TAB(), SPC(), semicolon/comma separators
- Already have LPRINT (printer), PRINT# is file version

### ELSE Patterns in MBASIC 5.21
Valid patterns:
```basic
IF cond THEN stmt1 : ELSE stmt2        ' Colon before ELSE
IF cond THEN stmt1 ELSE stmt2           ' No colon (sometimes valid?)
IF cond THEN linenum ELSE linenum       ' Line number targets
IF cond THEN stmt :ELSE linenum         ' Mixed
```

Need to handle all variations carefully.

### NAME Statement
```basic
NAME oldfile$ AS newfile$
```
Used to rename files on disk. Essential file operation in MBASIC 5.21.

---

## Statistics

**Total Remaining**: 123 failures

**Breakdown**:
- Implement MBASIC 5.21: ~36 files (29%)
- Move non-5.21: ~20 files (16%)
- Review/research: ~40 files (33%)
- Platform-specific: ~27 files (22%)

**Potential improvement from Phase 1+2**: +22 files → 114/215 (53.0%)

**After all cleanup**: Could reach ~65-70% with full implementation
