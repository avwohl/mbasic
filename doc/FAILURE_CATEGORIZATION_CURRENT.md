# Current Parser Failure Categorization

**Date**: 2025-10-22 (Latest)
**Test Run**: After all cleanup and reorganization
**Success Rate**: 104/215 files (48.4%)
**Remaining Failures**: 111 files (51.6%)

---

## Executive Summary

The 111 remaining parser failures break down as follows:

| Category | Count | Percentage | Action |
|----------|-------|------------|--------|
| **Implement MBASIC 5.21 Features** | 16 files | 14% | Implement missing features |
| **Non-MBASIC 5.21 Dialects** | 25 files | 23% | Move to bad_not521/ |
| **Source File Errors** | 25 files | 23% | Fix or move to bad_not521/ |
| **Complex/Needs Investigation** | 45 files | 40% | Individual review needed |

---

## Category 1: MBASIC 5.21 Features to Implement (16 files)

### 1.1 EOF() Function - 7 files ⭐ **HIGHEST PRIORITY**

**Files**:
- direct.bas
- genielst.bas
- rbbent27.bas
- rbbmin27.bas
- rbspurge.bas
- rbsutl31.bas
- simcvt.bas

**Syntax**: `EOF(filenum)` - Returns -1 if at end of file, 0 otherwise

**Example**:
```basic
200 IF EOF(1) GOTO 240
150 WHILE NOT EOF(1)
430 IF EOF(1) THEN 450
```

**Error**: "Unexpected token in expression: EOF_FUNC"

**Implementation**: Add EOF as built-in function token, handle in expression parser

**Impact**: 7 files → would reach 111/215 (51.6%)

---

### 1.2 HEX$() Function - 3 files

**Files**:
- disasmb.bas
- rsj.bas
- xref.bas

**Syntax**: `HEX$(number)` - Converts number to hexadecimal string

**Example**:
```basic
180 DEF FNZHEX2(I)=RIGHT$("00"+HEX$(I),2)
740 PRINT "configured for ";HEX$(P)
```

**Error**: "Unexpected token in expression: HEX"

**Implementation**: Add HEX$ as string function token

**Impact**: +3 files → would reach 114/215 (53.0%)

---

### 1.3 ELSE Edge Cases - 3 files

**Files**:
- header6.bas
- holtwint.bas
- ozdot.bas

**Issue**: Complex ELSE patterns not yet handled

**Example** (header6.bas line 23):
```basic
IF condition THEN stmt ELSE stmt2  ' Specific pattern causing issue
```

**Error**: "Expected : or newline, got ELSE"

**Implementation**: Extend IF parser for remaining edge cases

**Impact**: +3 files → would reach 117/215 (54.4%)

---

### 1.4 NAME Statement - 1 file

**Files**: pckget.bas

**Syntax**: `NAME oldfile$ AS newfile$` - Rename file

**Example**:
```basic
NAME L$ AS L$
NAME "TEMP.DAT" AS "FINAL.DAT"
```

**Error**: "Expected COMMA, got AS"

**Implementation**: Parse AS keyword with two filename expressions

---

### 1.5 CHAIN Statement - 1 file

**Files**: e-sketch.bas

**Syntax**: `CHAIN filename$` - Chain to another program

**Example**:
```basic
CHAIN "MENU"
CHAIN FIL$
```

**Error**: "Unexpected token in statement: CHAIN"

**Implementation**: Parse CHAIN keyword with filename expression

---

### 1.6 SAVE Statement - 1 file

**Files**: krakinst.bas

**Syntax**: `SAVE filename$` - Save program to disk

**Example**:
```basic
SAVE "PROGRAM.BAS"
```

**Error**: "Unexpected token in statement: SAVE"

**Implementation**: Parse SAVE keyword with filename expression

---

## Category 2: Non-MBASIC 5.21 Dialects (25 files)

### 2.1 Multiline IF/THEN - 7 files ✗

**Files**:
- exitrbbs.bas
- fprod.bas
- fprod1.bas
- mfil.bas
- minirbbs.bas
- timeout.bas
- un-prot.bas

**Pattern**: Structured BASIC with multiline IF blocks

**Example**:
```basic
370 IF F$ = "TW" THEN
380     PRINT "Something"
390 END IF
```

**Why Non-MBASIC**: This is QuickBASIC/GW-BASIC structured syntax, not MBASIC 5.21

**Action**: **MOVE to bad_not521/**

---

### 2.2 Wrong Comparison Operators - 5 files ✗

**Files**:
- ACEY.bas
- acey.bas
- birthday.bas
- rose.bas
- unigrid2.bas

**Pattern**: Using `=>` and `=<` instead of `>=` and `<=`

**Example**:
```basic
1070 IF MO => 25000 OR MO =< -25000 THEN 5900
900 IF W=> V GOTO 920
```

**Error**: "Unexpected token in expression: GREATER_THAN"

**Why Non-MBASIC**: Invalid operator syntax (some BASIC dialects allowed this)

**Action**: **MOVE to bad_not521/**

---

### 2.3 Decimal Line Numbers - 6 files ✗

**Files**:
- airmiles.bas
- cbasedit.bas
- cmprbib.bas
- commo1.bas
- journal.bas
- voclst.bas

**Pattern**: Floating-point line numbers

**Example**:
```basic
1.02 NEXT NUM
5.2E1 R.REC%=R.REC%+1
90.01 REM COMMENT
```

**Error**: "Unexpected token in statement: NUMBER"

**Why Non-MBASIC**: Line numbers must be integers (0-65529) in MBASIC 5.21

**Action**: **MOVE to bad_not521/**

---

### 2.4 Atari OPEN Syntax - 4 files ✗

**Files**:
- aut850.bas
- auto850.bas
- gammonb.bas
- pckexe.bas

**Pattern**: Atari BASIC file I/O syntax

**Example**:
```basic
20 OPEN #1,8,0,"D:AUTORUN.SYS"  ' Atari syntax
' vs MBASIC 5.21:
OPEN "I",#1,"FILENAME"
```

**Error**: "Unexpected token in expression: HASH"

**Why Non-MBASIC**: Atari BASIC specific

**Action**: **MOVE to bad_not521/**

---

### 2.5 INPUT; Syntax - 3 files ⚠️

**Files**:
- cpkhex.bas
- rc5%.bas
- rc5.bas

**Pattern**: INPUT with semicolon for prompt separator

**Example**:
```basic
200 INPUT;"Input hex file "; F$
1640 PRINT I$;I;"=":INPUT; V(I)
```

**Error**: "Expected IDENTIFIER, got SEMICOLON"

**Status**: **NEEDS RESEARCH** - Verify if valid MBASIC 5.21 syntax

**Action**: Check MBASIC 5.21 manual, then decide: implement or move

---

## Category 3: Source File Errors (25 files)

### 3.1 Corrupted/Malformed Source - 14 files

**Files**:
- bibbld.bas
- digiklok.bas
- doodle.bas
- scenecar.bas
- tankie.bas
- vocbld.bas
- (8 more)

**Examples**:
```basic
' bibbld.bas:30
30 REM    ' Incomplete REM statement

' digiklok.bas:111
111 A=     ' Expression cut off mid-line

' doodle.bas:2
2 A=B-     ' Missing right operand
```

**Errors**: Various ("Expected EQUAL, got REM", "Expected EQUAL, got EOF", etc.)

**Action**: **MOVE to bad_not521/** - Not valid parseable code

---

### 3.2 Invalid DEF Syntax - 3 files

**Files**:
- sink.bas
- surround.bas
- tanks.bas

**Pattern**: DEF statement without FN prefix

**Example**:
```basic
DEF SOMETHING(X) = X+1  ' Invalid
' Should be:
DEF FNSOMETHING(X) = X+1  ' Valid MBASIC 5.21
```

**Error**: "DEF function name must start with FN"

**Why Invalid**: MBASIC 5.21 requires FN prefix for user-defined functions

**Action**: **MOVE to bad_not521/** - Source syntax error

---

### 3.3 Concatenated Keywords - 8 files

**Files**:
- ONECHECK.bas
- aircraft.bas
- bigtime.bas
- directry.bas
- hangman.bas
- m100lf.bas
- onecheck.bas
- simcvt2.bas

**Pattern**: Keywords without proper spacing (typos)

**Examples**:
```basic
GOTO1500          ' Should be: GOTO 1500
CLEAR1000         ' Should be: CLEAR ,1000
IF...GOTO1500     ' Should be: IF...GOTO 1500
```

**Error**: "Expected EQUAL, got NEWLINE"

**Note**: Lexer already handles some cases (NEXTI → NEXT I)

**Action**: **Could implement broader splitting** OR treat as syntax errors

---

## Category 4: Complex/Need Investigation (45 files)

These files have various unique errors that need individual examination:

**Major subcategories**:
- Expression/statement boundary errors: ~10 files
- Unknown statement/keyword errors: ~10 files
- Function call syntax errors: ~3 files
- Various unique patterns: ~22 files

**Examples**:
- BACKGAMM.bas: Expected EQUAL, got COLON
- OTHELLO.bas: Expected THEN or GOTO after IF
- battle.bas: Expected EQUAL, got IDENTIFIER
- etc.

**Action**: Requires individual file review and analysis

---

## Quick Win Analysis

### Implementing Top 3 Features (13 files)

1. EOF() function: 7 files
2. HEX$() function: 3 files
3. ELSE edge cases: 3 files

**Impact**: 104 → **117/215 (54.4%)** success rate

---

### Cleaning Non-MBASIC Dialects (22 files certain + 3 uncertain)

Moving definite non-MBASIC 5.21 files:
- Multiline IF/THEN: 7 files
- Wrong operators: 5 files
- Decimal line numbers: 6 files
- Atari OPEN: 4 files

**New corpus**: 215 - 22 = 193 files
**Success rate**: 104/193 = **53.9%** (before implementing features)

With features implemented:
**Success rate**: 117/193 = **60.6%**

---

## Recommended Action Plan

### Phase 1: Quick Wins (High Impact, Low Effort)

1. **Implement EOF() function** - 7 files
2. **Implement HEX$() function** - 3 files
3. **Fix ELSE edge cases** - 3 files

**Estimated time**: 2-3 hours
**Result**: 117/215 (54.4%)

---

### Phase 2: Corpus Cleanup

1. **Move non-MBASIC dialects** - 22 files definite
   - Multiline IF/THEN
   - Wrong operators
   - Decimal line numbers
   - Atari OPEN

2. **Research INPUT; syntax** - 3 files (move if not valid)

**Result**: 117/193 (60.6%) on clean corpus

---

### Phase 3: Low-Hanging Fruit

1. **Implement NAME statement** - 1 file
2. **Implement CHAIN statement** - 1 file
3. **Implement SAVE statement** - 1 file

**Result**: 120/193 (62.2%)

---

### Phase 4: Source Error Cleanup

1. **Move corrupted files** - 14 files
2. **Move invalid DEF files** - 3 files
3. **Handle/move concatenated keyword files** - 8 files

**New corpus**: 193 - 25 = 168 files
**Result**: 120/168 (71.4%)

---

### Phase 5: Deep Dive

Investigate remaining 45 complex cases individually

**Potential result**: 70-75% success rate

---

## Statistics

**Current State**:
- Total files: 215
- Parsing: 104 (48.4%)
- Failing: 111 (51.6%)

**After Quick Wins (Phase 1)**:
- Parsing: 117 (54.4%)

**After Cleanup (Phases 1-2)**:
- Total: 193 files (clean corpus)
- Parsing: 117 (60.6%)

**After Phase 3**:
- Parsing: 120/193 (62.2%)

**After Phase 4**:
- Total: 168 files (very clean corpus)
- Parsing: 120 (71.4%)

**Realistic Goal**: 70-75% on clean MBASIC 5.21 corpus
