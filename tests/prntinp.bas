10 PRINT "=== Test 1: Normal INPUT ==="
20 INPUT A
30 PRINT "Got:";A
40 PRINT ""
50 PRINT "=== Test 2: INPUT with ; (no ?) ==="
60 INPUT;B
70 PRINT "Got:";B
80 PRINT ""
90 PRINT "=== Test 3: INPUT with prompt ==="
100 INPUT "Enter X";X
110 PRINT "X=";X
120 PRINT ""
130 PRINT "=== Test 4: INPUT prompt with ; (no ?) ==="
140 INPUT "Enter Y";Y
150 PRINT "Y=";Y
160 PRINT ""
170 PRINT "=== Test 5: PRINT then INPUT ==="
180 PRINT "Value: ";
190 INPUT Z
200 PRINT "Z=";Z
210 PRINT ""
220 PRINT "=== Test 6: PRINT then INPUT; ==="
230 PRINT "Number: ";
240 INPUT;N
250 PRINT "N=";N
260 PRINT ""
270 PRINT "=== Test 7: String INPUT normal ==="
280 INPUT S$
290 PRINT "S$=";S$
300 PRINT ""
310 PRINT "=== Test 8: String INPUT; ==="
320 INPUT;T$
330 PRINT "T$=";T$
340 PRINT ""
350 PRINT "=== Test 9: PRINT; then INPUT ==="
360 PRINT "Name: ";
370 INPUT N$
380 PRINT "Hello ";N$
390 PRINT ""
400 PRINT "=== Test 10: PRINT; then INPUT; ==="
410 PRINT "Code: ";
420 INPUT;C
430 PRINT "Code=";C
440 PRINT ""
450 PRINT "=== Test 11: Multiple vars INPUT ==="
460 INPUT A1,B1,C1
470 PRINT A1;B1;C1
480 PRINT ""
490 PRINT "=== Test 12: Multiple vars INPUT; ==="
500 INPUT;A2,B2,C2
510 PRINT A2;B2;C2
520 PRINT ""
530 PRINT "=== All tests complete ==="
540 END
