0  ' Revision 1.2 10/23/84
10 ' MTIMER10.BAS by Lawrence Davis 9/25/84
12 ' Insert your own clock routine at line 190
13 ' Clear screen string currently CHR$(26) - ^Z
15 ' This program must be compiled using BASCOM
16 ' Compile as follows: BASCOM in A drive   MTIMER.BAS in B drive
17 ' A>BASCOM =B:MTIMER12 /O
18 ' A>L80 B:MTIMER12,B:MTIMER/N/E
19 DIM L$(128)
20 PRINT CHR$(26);TAB(20)"Mex Timer Program - Version 1.2
25 PRINT TAB(27);"For Epson QX-10
30 PRINT:PRINT:PRINT
40 INPUT "Set the STARTUP TIME:  (Enter as HH:MM) ",A$
45 PRINT:PRINT"Enter the Mex COMMAND LINE (eg. LOAD PHONE.PHN;READ BBS) "
47 INPUT "MEX>",M$
50 PRINT CHR$(26);"The STARTUP TIME is set for ";A$
55 PRINT:PRINT;"The Mex COMMAND LINE is <"+M$+">"
60 PRINT:PRINT;"You must leave the computer and modem ON"
80 GOSUB 190		'read clock
90 IF TM$=A$ THEN 164 	'Is it time?  Yes, then run MEX
100 OLDTM$=TM$		'If not, then try again
110 GOSUB 190		'Read clock
120 IF TM$>OLDTM$ THEN 80 
130 GOTO 110
164 L=LEN(M$)+1		'Length of command line + space (20h)
165 POKE &H80,L		'Poke length into default buffer
166 POKE &H81,&H20	'poke space (20h)
168 J=130		'Decimal equivalent of 82h
169 FOR I%=1 TO LEN(M$)	'Loop times number of chars in command line
170   L$(I%)=MID$(M$,I%,1)'Assign a string variable to each char in comm. line
171   POKE J,ASC(L$(I%)) 'Poke command line into default buffer addresses
172   J=J+1		'Increment address counter
175 NEXT I%		'Do it again
180 PRINT CHR$(26):RUN "MEX"
190 OUT &H3D,4:TH=INP(&H3C):GOSUB 220:DH$=TH$	'Clock routine for
200 OUT &H3D,2:TH=INP(&H3C):GOSUB 220:DI$=TH$	'Epson QX-10
210 TM$=DH$+":"+DI$:RETURN
220 TH$=""
230 IF TH<10 THEN TH$="0"
240 TH$=TH$+HEX$(TH)				'End clock routine
250 RETURN
