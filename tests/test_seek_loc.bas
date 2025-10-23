10 REM Test LOC, LOF, and sequential PUT/GET
20 PRINT "=== Testing LOC, LOF, PUT, GET ==="
30 OPEN "R", 1, "TEST.DAT", 20
40 FIELD #1, 10 AS A$, 10 AS B$
50 PRINT "After OPEN: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
60 LSET A$ = "REC1-A"
70 LSET B$ = "REC1-B"
80 PUT #1, 1
90 PRINT "After PUT #1,1: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
100 LSET A$ = "REC2-A"
110 LSET B$ = "REC2-B"
120 PUT #1, 2
130 PRINT "After PUT #1,2: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
140 LSET A$ = "REC3-A"
150 LSET B$ = "REC3-B"
160 PUT #1, 3
170 PRINT "After PUT #1,3: LOC(1)="; LOC(1); " LOF(1)="; LOF(1)
180 GET #1, 1
190 PRINT "After GET #1,1: LOC(1)="; LOC(1); " A$=["; A$; "]"
200 GET #1, 3
210 PRINT "After GET #1,3: LOC(1)="; LOC(1); " A$=["; A$; "]"
220 GET #1, 2
230 PRINT "After GET #1,2: LOC(1)="; LOC(1); " A$=["; A$; "]"
240 PRINT
250 PRINT "Testing sequential PUT (no record number)"
260 LSET A$ = "REC4-A"
270 LSET B$ = "REC4-B"
280 PUT #1
290 PRINT "After PUT #1: LOC(1)="; LOC(1); " (should be 3)"
300 PRINT
310 PRINT "Testing sequential GET (no record number)"
320 GET #1, 1
330 PRINT "First GET #1,1: LOC(1)="; LOC(1)
340 GET #1
350 PRINT "Then GET #1: LOC(1)="; LOC(1); " A$=["; A$; "]"
360 GET #1
370 PRINT "Then GET #1: LOC(1)="; LOC(1); " A$=["; A$; "]"
380 CLOSE #1
390 END
