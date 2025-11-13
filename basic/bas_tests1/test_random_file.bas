10 REM Test random file access - FIELD, LSET, RSET, GET, PUT
20 PRINT "Creating random file..."
30 OPEN "R", 1, "testrand.dat", 50
40 FIELD 1, 20 AS NAME$, 10 AS ADDR$, 5 AS ZIP$, 15 AS CITY$
50 REM Write record 1
60 LSET NAME$ = "John Smith"
70 LSET ADDR$ = "123 Main"
80 LSET ZIP$ = "12345"
90 RSET CITY$ = "Boston"
100 PUT 1, 1
110 REM Write record 2
120 LSET NAME$ = "Jane Doe"
130 LSET ADDR$ = "456 Oak"
140 LSET ZIP$ = "67890"
150 RSET CITY$ = "Seattle"
160 PUT 1, 2
170 PRINT "Records written"
180 PRINT ""
190 REM Read records back
200 PRINT "Reading record 1:"
210 GET 1, 1
220 PRINT "Name: "; NAME$
230 PRINT "Address: "; ADDR$
240 PRINT "ZIP: "; ZIP$
250 PRINT "City: "; CITY$
260 PRINT ""
270 PRINT "Reading record 2:"
280 GET 1, 2
290 PRINT "Name: "; NAME$
300 PRINT "Address: "; ADDR$
310 PRINT "ZIP: "; ZIP$
320 PRINT "City: "; CITY$
330 CLOSE 1
340 PRINT ""
350 PRINT "Done!"
360 END
