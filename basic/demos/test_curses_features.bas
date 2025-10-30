10 REM Test curses UI features
20 REM - Variable sorting (all modes)
30 REM - Array cell tracking
40 REM - Step line vs step statement
50 REM
60 REM Create various types of variables
70 A% = 100: B% = 200: C% = 300
80 X = 1.5: Y = 2.5: Z = 3.5
90 NAME$ = "Alice": CITY$ = "Boston": STATE$ = "MA"
100 REM
110 REM Create and access arrays
120 DIM A%(10, 10)
130 DIM VALUES(5)
140 DIM NAMES$(3)
150 REM
160 REM Access array cells in different patterns
170 A%(5, 3) = 42
180 A%(1, 1) = 10
190 A%(9, 9) = 99
200 REM
210 VALUES(0) = 100: VALUES(1) = 200: VALUES(2) = 300
220 NAMES$(0) = "First": NAMES$(1) = "Second"
230 REM
240 REM Multi-statement lines for step testing
250 I% = 0: J% = 0: K% = 0
260 FOR I% = 1 TO 3: PRINT I%;: NEXT I%
270 PRINT
280 REM
290 REM Variables with different access patterns
300 TEMP1 = 111: TEMP2 = 222: TEMP3 = 333
310 X = TEMP1: Y = TEMP2: Z = TEMP3
320 REM
330 REM Read some variables
340 PRINT "A% ="; A%
350 PRINT "X ="; X
360 PRINT "NAME$ ="; NAME$
370 REM
380 REM Access arrays again
390 PRINT "A%(5,3) ="; A%(5, 3)
400 VALUES(2) = 999
410 PRINT "VALUES(2) ="; VALUES(2)
420 REM
430 REM Write to some variables
440 A% = A% + 1
450 X = X * 2
460 NAME$ = NAME$ + " Jones"
470 REM
480 REM Final multi-statement line
490 PRINT "Done": PRINT "A%="; A%: PRINT "X="; X
500 END
