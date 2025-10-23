10 REM Test random file I/O - CP/M compatible
20 PRINT "Test 1: Create random file with records"
30 OPEN "R", 1, "TESTRAND.DAT", 32
40 FIELD #1, 10 AS N$, 5 AS A$, 17 AS D$
50 REM Write 3 records
60 LSET N$ = "John"
70 LSET A$ = "25"
80 LSET D$ = "Engineer"
90 PUT #1, 1
100 LSET N$ = "Jane"
110 LSET A$ = "30"
120 LSET D$ = "Manager"
130 PUT #1, 2
140 LSET N$ = "Bob"
150 LSET A$ = "45"
160 LSET D$ = "Director"
170 PUT #1, 3
180 PRINT "  Wrote 3 records"
190 PRINT
200 PRINT "Test 2: Read records back"
210 GET #1, 1
220 PRINT "  Record 1: "; N$; " Age:"; A$; " Job:"; D$
230 GET #1, 2
240 PRINT "  Record 2: "; N$; " Age:"; A$; " Job:"; D$
250 GET #1, 3
260 PRINT "  Record 3: "; N$; " Age:"; A$; " Job:"; D$
270 PRINT
280 PRINT "Test 3: LOC() and LOF() functions"
290 L = LOC(1)
300 PRINT "  LOC(1) ="; L; "(current record)"
310 S = LOF(1)
320 PRINT "  LOF(1) ="; S; "(file size in bytes)"
330 PRINT
340 PRINT "Test 4: Update record 2"
350 GET #1, 2
360 LSET A$ = "31"
370 PUT #1, 2
380 GET #1, 2
390 PRINT "  Updated record 2: "; N$; " Age:"; A$
400 PRINT
410 PRINT "Test 5: Test RSET (right-justify)"
420 RSET N$ = "Al"
430 PRINT "  RSET N$ = 'Al': ["; N$; "]"
440 PRINT
450 CLOSE #1
460 PRINT "All random file I/O tests passed!"
470 END
l"
430 PRINT "  RSET N$ = 'Al': ["; N$; "]"
440 PRINT
450 CLOSE #1
460 PRINT "All random file I/O tests passed!"