10 REM  **********************************************************************
20 REM  Program:  HEX2DATA.BAS
30 REM	Author:  Ian Cottrell, Ottawa, Ontario  (613)-829-1650
40 REM  Language:  MICROSOFT BASIC-80  VER. 5.XX
50 REM  Date:  December, 1983
60 REM  Remarks:  This program will convert data files from Intel Hex Format
70 REM            to a series of BASIC 'DATA' statements.  The DATA statements
80 REM            are numbered starting with 10,000 and incrementing by 10
90 REM            although this can easily be changed if desired (NUM).
100 REM           This program can be very useful for building assembly
110 REM           language sub-routines into your BASIC programs.  Once the
120 REM           sub-routine is written, assembled, and debugged, use this
130 REM           routine to convert the output of the assembler into a series
140 REM           of DATA statements.  The resultant file is saved in ASCII
150 REM           format so it can be CHAIN MERGEd with your main program.
160 REM           Then you need only write a loop to read the data and POKE it
170 REM           into memory at the desired location.
180 REM  *********************************************************************
190 DIM B$(50),Z(50),Z$(50)
200 NUM=10000:NUM$=STR$(NUM)+" ":F=0
210 CLS$=CHR$(4):PRINT CLS$
220 INPUT "What is the INPUT filename (extension must be 'HEX')";I$
230 PRINT:INPUT "What is the OUTPUT filename (extension will be 'BAS')";O$
240 FOR I=1 TO LEN(I$)
250	IF MID$(I$,I,1)="." THEN I$=LEFT$(I$,I-1):GOTO 270
260 NEXT I
270 I$=I$+".HEX"
280 FOR I=1 TO LEN(O$)
290	IF MID$(O$,I,1)="." THEN O$=LEFT$(O$,I-1):GOTO 310
300 NEXT I
310 O$=O$+".BAS"
320 OPEN "I",#1,I$
330 OPEN "O",#2,O$
340 LINE INPUT#1,A$
350 IF MID$(A$,2,2)="00" THEN CLOSE:PRINT "ENDING ADDRESS  : "ADDR$:END
360 ADDR$=MID$(A$,4,4):IF F=0 THEN PRINT:PRINT  "STARTING ADDRESS: "ADDR$:F=1
370 A$=RIGHT$(A$,LEN(A$)-9)
380 A$=LEFT$(A$,LEN(A$)-2)
390 FOR I=1 TO (LEN(A$)/2)
400	B$(I)=MID$(A$,2*I-1,2)
410	X$=LEFT$(B$(I),1):Y$=RIGHT$(B$(I),1)
420	X=ASC(X$):Y=ASC(Y$)
430	IF X>57 THEN X=16*(10+(X-65)) ELSE X=16*(X-48)
440	IF Y>57 THEN Y=10+(Y-65) ELSE Y=Y-48
450	Z(I)=X+Y:Z$(I)=STR$(Z(I))
460 NEXT I
470 PRINT#2,NUM$;"DATA ";RIGHT$(Z$(1),LEN(Z$(1))-1);
480 FOR I=2 TO (LEN(A$)/2)
490	PRINT#2,",";RIGHT$(Z$(I),LEN(Z$(I))-1);
500 NEXT I
510 PRINT#2,CHR$(13);CHR$(10)
520 NUM=NUM+10
530 NUM$=STR$(NUM)+" "
540 GOTO 340
