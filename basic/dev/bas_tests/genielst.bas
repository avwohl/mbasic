10 PRINT : PRINT "GENIELST.BAS by Keith Petersen, W8SDZ"
20 PRINT "Version 1.0 - June 6, 1988."
30 PRINT
40 PRINT "This program makes a list with one filename and a short description"
50 PRINT "on each line of the output file.  It is intended to be used with"
60 PRINT "an input file which was captured from a GEnie directory listing."
70 PRINT "The capture file must be edited to remove any non-directory"
80 PRINT "information at the head or tail.  There is a limit of 500 files in"
90 PRINT "the list.  It is not intended for a full directory list, only for"
100 PRINT "weekly or monthly updates using GEnie menu option 3."
110 PRINT
120 I=1:DIM F$(80),D$(80),A$(500)
130 OPEN "I",1,"CPM.LST" ' name of capture file
140 PRINT "Reading input file";
150 WHILE NOT EOF(1)
160     LINE INPUT #1,F$
170     LINE INPUT #1,D$
180     A$(I)=MID$(F$,7,12)+"   "+MID$(D$,12,(LEN(D$)-10))
190     PRINT ".";
200     I=I+1
210 WEND
220 CLOSE #1
230 ' Sort routine
240 I=I-1 : N=I : PRINT : PRINT
250 PRINT I "files in this list."
260 '
270 ' This starts the actual sort
280 '
290 PRINT: PRINT "Starting sort..."
300 J4=N
310 J4=J4\2
320 IF J4=0 THEN 450 'DONE
330 J2=N-J4
340 J=1
350 I=J
360 J3=I+J4
370 '
380 IF A$(I) <= A$(J3) THEN 420
390 SWAP A$(I),A$(J3)
400 I=I-J4
410 IF I>=1 THEN 360
420 J=J+1
430 IF J>J2 THEN 310
440 GOTO 350
450 PRINT "Sort completed.."
460 '
470 ' Print sorted list to output file
480 '
490 OPEN "O",2,"CPM.OUT" ' name of output file
500 FOR I=1 TO N
510 PRINT #2,A$(I)
520 NEXT I
530 CLOSE #2
540 PRINT : PRINT N "names written to output file." : PRINT
550 END
