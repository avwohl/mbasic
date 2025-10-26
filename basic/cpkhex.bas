1 REM -- CP4HEX.BAS --
2 REM This program reads an Intel-format hex file and checks it for validity.
3 REM It discards blank lines, and if it finds any other lines that are bad,
4 REM either bacause the format is wrong or the checksum doesn't agree, it
5 REM prompts you to type in a replacement line.  Use this program to fix
6 REM hex files you have downloaded using a non-error-correcting method.
7 REM Written by F. da Cruz & C. Gianone, Columbia University, April 1986.
8 REM Used with success on Vector Graphic Model 3 CP/M-80 system.
9 REM
100  ON ERROR GOTO 9000
200  INPUT;"Input hex file "; F$
300  PRINT
400  OPEN "I",#1,F$
500  INPUT;"Output hex file"; O$
600  PRINT
700  OPEN "O",#2,O$
800  B = 0
900  REM Loop at 1000 for each line, B, of the input hex file, then...
901  REM   Discard blank lines.
902  REM   Look for colon that begins hex record
903  REM   Decode rest of record...
904  REM   L  = length of rest, in bytes (not hex characters!), 1 byte
905  REM   N  = address, 2 bytes
906  REM   T  = record type, 0 = data, 1 = EOF
907  REM   C% = 1-byte checksum
908  REM Record has negative of actual checksum, adding to C% should give 0.
909  REM Subroutine at 8000 converts pair of hex nibbles to 8-bit byte.
910  REM
1000 LINE INPUT #1, A$
1010 B = B + 1
1015 IF A$ = "" THEN GOTO 1000
1020 IF LEFT$(A$,1) = ":" THEN GOTO 2000
1030 X = INSTR(2,A$,":")
1033 IF X < 1 THEN GOTO 1040
1035 A$ = MID$(A$,X,LEN(A$)-X+1)
1037 GOTO 2000
1040 PRINT "Line";B;"has no colon"
1060 GOTO 3070
2000 C% = 0
2005 PRINT ".";
2010 X$ = MID$(A$,2,2)
2020 GOSUB 8000
2030 L = K
2040 X$ = MID$(A$,4,2)
2050 GOSUB 8000
2060 N = K
2070 X$ = MID$(A$,6,2)
2080 GOSUB 8000
2090 N = 256 * N + K
2100 X$ = MID$(A$,8,2)
2110 GOSUB 8000
2120 T = K
2125 IF T = 1 THEN PRINT "End of";F$;"at line";B : GOTO 9000
2130 IF T <> 0 THEN PRINT "Invalid record type"; T : GOTO 3070
2140 M = 10
3000 X$ = MID$(A$,M,2)
3002 GOSUB 8000
3005 M = M + 2
3010 L = L - 1
3020 IF L > 0 THEN GOTO 3000
3030 X$ = MID$(A$,M,2)
3050 GOSUB 8000
3060 IF (C% AND 255) = 0 THEN GOTO 3100
3065 PRINT "Bad Checksum"
3070 PRINT "Line";B
3075 PRINT "Bad: "; A$
3080 INPUT "New  "; A$
3090 PRINT
3100 PRINT #2,A$
4000 GOTO 1000
7999 REM Subroutine to convert pair of hex nibbles to one 8-bit byte.
8000 I = ASC(LEFT$(X$,1))
8005 K = 0
8010 IF I > 64 AND I < 71 THEN I = I - 7
8020 IF I < 48 OR I > 63 THEN K = -1
8030 J = ASC(MID$(X$,2,1))
8040 IF J > 64 AND J < 71 THEN J = J - 7
8050 IF J < 48 OR J > 63 THEN K = -1
8060 IF K < 0 THEN RETURN
8070 K = 16 * (I - 48) + J - 48
8080 C% = C% + K
8099 RETURN
8999 Program exit and error handler
9000 CLOSE #1
9010 CLOSE #2
9020 CLOSE
9030 PRINT "Records processed:";B
9999 END
