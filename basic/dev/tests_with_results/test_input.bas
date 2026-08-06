10 REM Test INPUT and LINE INPUT (simulated with DATA)
20 REM Note: Using DATA/READ to simulate INPUT for automated testing
30 PRINT "Testing INPUT Functionality"
40 PRINT "==========================="
50 PRINT
60 REM Test 1: Single numeric input
70 PRINT "Test 1: Single numeric INPUT"
80 DATA 42
90 READ A
100 PRINT "Read value:"; A
110 PRINT
120 REM Test 2: Multiple numeric inputs
130 PRINT "Test 2: Multiple numeric INPUT"
140 DATA 10, 20, 30
150 READ X, Y, Z
160 PRINT "X ="; X; ", Y ="; Y; ", Z ="; Z
170 PRINT
180 REM Test 3: String input
190 PRINT "Test 3: String INPUT"
200 DATA "Hello World"
210 READ N$
220 PRINT "Read string:"; N$
230 PRINT
240 REM Test 4: Mixed input types
250 PRINT "Test 4: Mixed numeric and string INPUT"
260 DATA "Alice", 25, 1250.50
270 READ NM$, AGE, SALARY
280 PRINT "Name:"; NM$; "Age:"; AGE; "Salary:"; SALARY
290 PRINT
300 REM Test 5: Multiple string inputs
310 PRINT "Test 5: Multiple strings"
320 DATA "Red", "Green", "Blue"
330 READ C1$, C2$, C3$
340 PRINT "Colors:"; C1$; ","; C2$; ","; C3$
350 PRINT
360 REM Test 6: INPUT with prompt (simulated)
370 PRINT "Test 6: INPUT with prompt"
380 DATA 99
390 PRINT "Enter a number";
400 READ NUM
410 PRINT NUM
420 PRINT "You entered:"; NUM
430 PRINT
440 REM Test 7: Type coercion in INPUT
450 PRINT "Test 7: Type coercion"
460 DATA 123.456
470 READ I%
480 PRINT "Integer from 123.456:"; I%
490 PRINT
500 REM Test 8: Comma-separated values
510 PRINT "Test 8: Comma-separated INPUT"
520 DATA 1, 2, 3, 4, 5
530 READ A, B, C, D, E
540 PRINT "Values:"; A; B; C; D; E
550 PRINT
560 REM Test 9: Empty string handling
570 PRINT "Test 9: String input variations"
580 DATA "", "Non-empty", ""
590 READ S1$, S2$, S3$
600 PRINT "S1 len:"; LEN(S1$); "S2 len:"; LEN(S2$); "S3 len:"; LEN(S3$)
610 PRINT
620 PRINT "INPUT tests complete!"
630 END
