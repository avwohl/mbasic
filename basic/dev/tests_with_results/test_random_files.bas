10 REM Test Random Access Files
20 PRINT "Testing Random Access Files"
30 PRINT "==========================="
40 PRINT
50 REM Test 1: FIELD, LSET, PUT, GET
60 PRINT "Test 1: FIELD, LSET, PUT, GET"
70 OPEN "R", 1, "TESTRND.DAT", 32
80 FIELD 1, 10 AS N$, 20 AS A$
90 LSET N$ = "John"
100 LSET A$ = "123 Main St"
110 PUT 1, 1
120 GET 1, 1
130 IF N$ = "John      " AND A$ = "123 Main St         " THEN PRINT "FIELD/LSET/PUT/GET: PASS" ELSE PRINT "FAIL"
140 CLOSE 1
150 PRINT
160 REM Test 2: RSET (right-justify)
170 PRINT "Test 2: RSET (right-justify)"
180 OPEN "R", 1, "TESTRND.DAT", 20
190 FIELD 1, 10 AS L$, 10 AS R$
200 LSET L$ = "LEFT"
210 RSET R$ = "RIGHT"
220 PUT 1, 1
230 GET 1, 1
240 IF L$ = "LEFT      " AND R$ = "     RIGHT" THEN PRINT "LSET/RSET alignment: PASS" ELSE PRINT "FAIL"
250 CLOSE 1
260 PRINT
270 REM Test 3: Multiple records
280 PRINT "Test 3: Multiple records"
290 OPEN "R", 1, "TESTRND.DAT", 15
300 FIELD 1, 10 AS NM$, 5 AS AGE$
310 LSET NM$ = "Alice"
320 LSET AGE$ = "25"
330 PUT 1, 1
340 LSET NM$ = "Bob"
350 LSET AGE$ = "30"
360 PUT 1, 2
370 LSET NM$ = "Carol"
380 LSET AGE$ = "35"
390 PUT 1, 3
400 REM Read back in different order
410 GET 1, 2
420 IF NM$ = "Bob       " THEN PRINT "Record 2 retrieval: PASS" ELSE PRINT "Record 2: FAIL"
430 GET 1, 1
440 IF NM$ = "Alice     " THEN PRINT "Record 1 retrieval: PASS" ELSE PRINT "Record 1: FAIL"
450 GET 1, 3
460 IF NM$ = "Carol     " THEN PRINT "Record 3 retrieval: PASS" ELSE PRINT "Record 3: FAIL"
470 CLOSE 1
480 PRINT
490 REM Test 4: Numeric fields
500 PRINT "Test 4: Numeric data in fields"
510 OPEN "R", 1, "TESTRND.DAT", 20
520 FIELD 1, 5 AS ID$, 10 AS AMOUNT$, 5 AS QTY$
530 LSET ID$ = "12345"
540 LSET AMOUNT$ = "99.99"
550 LSET QTY$ = "100"
560 PUT 1, 1
570 GET 1, 1
580 REM Convert strings back to numbers
590 I = VAL(ID$)
600 A = VAL(AMOUNT$)
610 Q = VAL(QTY$)
620 IF I = 12345 AND A = 99.99 AND Q = 100 THEN PRINT "Numeric field conversion: PASS" ELSE PRINT "FAIL"
630 CLOSE 1
640 PRINT
650 PRINT "Random access file tests complete!"
655 KILL "TESTRND.DAT"
660 END
