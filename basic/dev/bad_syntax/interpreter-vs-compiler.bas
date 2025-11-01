REM =====================================================
REM MBASIC Interpreter vs Compiler Behavior Examples
REM =====================================================

REM -----------------------------------------------------
REM Example 1: DEFINT Control Flow Dependency
REM -----------------------------------------------------
REM In MBASIC Interpreter:
REM   X will be 5.5, then 6 after DEFINT executes
REM In Compiler:
REM   X will be 6 in both places (DEFINT applies globally)
REM -----------------------------------------------------

10 REM Interpreter behavior
20 X = 5.5
30 PRINT "Before DEFINT: X = "; X    ' Prints 5.5 in interpreter
40 DEFINT X
50 X = 5.5
60 PRINT "After DEFINT: X = "; X     ' Prints 6 in both
70 REM Compiler: Both print 6 (DEFINT is global)

REM -----------------------------------------------------
REM Example 2: Dynamic Array Sizing
REM -----------------------------------------------------
REM In MBASIC Interpreter:
REM   Works fine - arrays dimensioned at runtime
REM In Compiler (without $DYNAMIC):
REM   COMPILE ERROR - array dimension must be constant
REM -----------------------------------------------------

100 REM This works in interpreter but NOT in compiler
110 INPUT "How many elements"; N
120 DIM A(N)                         ' ERROR in compiler!
130 FOR I = 1 TO N
140   A(I) = I * 10
150 NEXT I

200 REM Compiler-compatible version
210 CONST MAXSIZE = 100
220 DIM B(MAXSIZE)                   ' OK - constant dimension
230 INPUT "How many elements (max 100)"; M
240 IF M > MAXSIZE THEN M = MAXSIZE
250 FOR I = 1 TO M
260   B(I) = I * 10
270 NEXT I

REM -----------------------------------------------------
REM Example 3: ERASE Statement
REM -----------------------------------------------------
REM In MBASIC Interpreter:
REM   ERASE frees array memory
REM In Compiler (static mode):
REM   ERASE not supported - compile error
REM -----------------------------------------------------

300 DIM C(50)
310 FOR I = 1 TO 50
320   C(I) = I
330 NEXT I
340 REM ERASE C                      ' Works in interpreter, ERROR in compiler

REM -----------------------------------------------------
REM Example 4: Variable Type Changes
REM -----------------------------------------------------
REM In MBASIC Interpreter:
REM   Variable type can change during execution
REM In Compiler:
REM   Each variable has fixed type throughout program
REM -----------------------------------------------------

400 REM Problematic for compiler
410 RESULT = 10 / 3                  ' RESULT is single-precision
420 PRINT "Result as float: "; RESULT
430 DEFINT R
440 RESULT = 10 / 3                  ' In compiler, RESULT was ALWAYS integer
450 PRINT "Result as integer: "; RESULT

REM -----------------------------------------------------
REM Example 5: String Variable Type Inference
REM -----------------------------------------------------
REM Works same in both, but shows importance of $ suffix
REM -----------------------------------------------------

500 REM Correct - explicit type markers
510 NAME$ = "John"                   ' String variable
520 COUNT% = 10                      ' Integer variable
530 PRICE! = 19.99                   ' Single-precision
540 TOTAL# = 1234.5678               ' Double-precision
550 PRINT NAME$; " bought "; COUNT%; " items"

REM -----------------------------------------------------
REM Example 6: DEFSTR with String Functions
REM -----------------------------------------------------
REM Compiler applies DEFSTR globally
REM -----------------------------------------------------

600 DEFSTR S
610 S1 = "Hello"                     ' S1 is string (no $ needed)
620 S2 = "World"                     ' S2 is string
630 RESULT = S1 + " " + S2          ' RESULT starts with R (not string!)
640 REM Above may fail in compiler due to type mismatch
650 REM Better approach:
660 S3$ = S1 + " " + S2             ' Explicit $ suffix

REM -----------------------------------------------------
REM Example 7: Constant Expressions in DIM
REM -----------------------------------------------------
REM Compiler can evaluate constant expressions at compile time
REM -----------------------------------------------------

700 CONST ROWS = 10
710 CONST COLS = 20
720 DIM MATRIX(ROWS, COLS)           ' OK - constants
730 DIM MATRIX2(ROWS * 2, COLS / 2)  ' OK - constant expression
740 REM DIM MATRIX3(ROWS + X, COLS)  ' ERROR - X is variable

REM -----------------------------------------------------
REM Example 8: Label Usage (Extended Compilers)
REM -----------------------------------------------------
REM Some compilers allow alphanumeric labels
REM Standard MBASIC uses only line numbers
REM -----------------------------------------------------

800 REM Traditional MBASIC style
810 GOTO 850
820 PRINT "Skipped"
850 PRINT "Target reached"

REM Modern compiler might support:
REM MainLoop:
REM   INPUT X
REM   IF X < 0 THEN GOTO EndProgram
REM   PRINT X
REM   GOTO MainLoop
REM EndProgram:
REM   PRINT "Done"

REM -----------------------------------------------------
REM Example 9: DEF FN Scope
REM -----------------------------------------------------
REM Both work similarly, but compiler may optimize
REM -----------------------------------------------------

900 DEF FN SQUARE(X) = X * X
910 DEF FN CUBE(Y) = Y * Y * Y
920 PRINT "5 squared = "; FN SQUARE(5)
930 PRINT "3 cubed = "; FN CUBE(3)
940 REM Compiler may inline these functions

REM -----------------------------------------------------
REM Example 10: Metacommands (Compiler Only)
REM -----------------------------------------------------
REM These are ignored by interpreter
REM -----------------------------------------------------

REM $STATIC
REM Arrays are statically allocated (default)

REM $DYNAMIC
REM Arrays can be dynamically sized
REM DIM ARRAY(N) now works where N is variable
REM ERASE now works

REM $INCLUDE: 'COMMON.BAS'
REM Include another source file

1000 END

REM =====================================================
REM MIGRATION TIPS: Interpreter b Compiler
REM =====================================================
REM
REM 1. Move all DEFINT/DEFSNG/DEFDBL/DEFSTR to top of program
REM 2. Use explicit type suffixes ($, %, !, #) on variables
REM 3. Replace dynamic DIM with fixed dimensions
REM 4. Remove ERASE statements (or use $DYNAMIC mode)
REM 5. Remove interactive commands (LIST, SAVE, LOAD, etc.)
REM 6. Ensure all GOTO/GOSUB targets exist
REM 7. Test with constant array dimensions
REM 8. Add REM $COMPILED marker at top
REM
REM =====================================================
