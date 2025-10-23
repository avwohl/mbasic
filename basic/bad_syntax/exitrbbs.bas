100	'  EXITRBBS.BAS, version 1.4
120	'  Routine to allow users to leave comments before logging off
140	'  Original by Brian Kantor & Skip Hansen 09/81 (?)
160	'  Minor text changes, bye call, and time-on-system stuff added
180	'            by Ben Bronson, 10/11/81
200	'     Note that this is meant to be compiled and called "BYE.COM"
220	'  Modified for Macrostore-R 10-18-81 -CAF
240	'  Main routine for users to leave comments before logging off
241	' --------------------------------------------------------
242	' 15/Jun/82 Added clock routines from ENTRBBS to allow exit
243	' time of caller to be recorded. Caller status is checked from
244	' and recorded in CALLERS along with out time. TWit status callers
245	' don't get a chance to leave comments. TWit status may be entered
246	' LASTCALR in ENTRBBS (from USERS) or by a password utility like
247	' UTIL that a user has tried to break into. SYSOP bypasses the
248	' out time recording as he never makes it into CALLERS. Added date
249	' and "exit" to COMMENTS enteries so you can tell when and where
250	' they were entered (MINIRBBS enters "Mini"). Bill Bolton
251	' --------------------------------------------------------
252	' 09/Aug/82 Added routine from MINIRBBS to give time on system.
253	' Bill Bolton
254	' --------------------------------------------------------
255	' 26/Mar/83 Fixed bug in elapsed time routine that gave weird
256	' results if login went over midnight. Bill Bolton
257	'---------------------------------------------------------
258	' 04/Apr/83 Added SYSOP logout recording in DIRECT file.
259	' Version 1.3 - Bill Bolton
260	'---------------------------------------------------------
261	' 15/May/83 Added error trap when exiting system with no
262	' pre-existing DIRECT or CALLERS file (i.e. after a general
263	' file purge and system maintenance). Must now be compiled
264	' with /X switch. Version message added. Version 1.4 - Bill Bolton
265	'---------------------------------------------------------
279	'
280	DEFINT A-Z
300	DIM H(6),HT(6),HD(6),TOD(5),DOY(5)
310	ON ERROR GOTO 4000
320	ERS$=CHR$(8)+" "+CHR$(8)
330	MAGIC$ = "SUPER"
340	OPEN "I",1,"A:LASTCALR":
	INPUT #1,N$,O$,F$,DT$:
	CLOSE
360	PRINT
370	IF F$ = "TW" THEN
		GOTO 720
375	PRINT "BYE Version 1.4"
376	PRINT
380	PRINT "Want to leave any comments (Y/N)? ";:
	C=1:
	GOSUB 1200:
	C=0
400	IF LEFT$(B$,1)="N" OR LEFT$(B$,1)="n" THEN
		720
420	IF LEFT$(B$,1)<>"Y" AND LEFT$(B$,1)<>"y" THEN
		380
440	PRINT
460	OPEN "R",1,"A:C"+CHR$(&HCF)+"MMENTS. "+CHR$(&HA0),65:
	FIELD#1,65 AS RR$
480	GET#1,1:
	RE=VAL(RR$)+1:
	RL=65
500	IF RE=1 THEN
		RE=2
520	S$="From: "+N$+" "+O$+" "+DT$+" (Exit)":
	GOSUB 1500
540	PUT#1,RE
560	PRINT "Enter comments, <return> to end, (16 lines max)"
580	PRINT
600	PRINT "-->";
620	GOSUB 1200
640	IF B$="" THEN
		700	
660	RE=RE+1:
	S$=B$:
	RL=65:
	GOSUB 1500:
	PUT#1,RE 
680	GOTO 600
700	S$=STR$(RE):
	RL=65:
	GOSUB 1500:
	PUT#1,1:
	CLOSE
720	GOSUB 2000:
	GOSUB 2700
730	IF N$ = MAGIC$ THEN
		GOSUB 1000:
		GOTO 920		'Record time off for SYSOP
740	OPEN "R",1,"A:C"+CHR$(&HC1)+"LLERS. "+CHR$(&HA0),60:
	FIELD#1, 60 AS RR$:
	GET #1,1
760	RE = VAL(RR$) + 1:
	RL = 60
780	GET #1,RE:
	INPUT#1,S$
800	IF INSTR(S$,":") THEN
		POINTER = INSTR(S$,":")
	ELSE
		POINTER = LEN(S$)
820	S$ = LEFT$(S$,POINTER + 2)  + " to " + TI$ + " " + F$ + MID$(S$,POINTER + 3)
840	GOSUB 1500
860	PUT #1,RE:
	CLOSE #1
880	'
920	PRINT
930	GOSUB 44000
940	RUN "A:SUPER.COM"
960	END
980	'
1000	OPEN "R",1,"A:D"+CHR$(&HC9)+"RECT. "+CHR$(&HA0),40:
	FIELD#1, 40 AS RR$:
	GET #1,1
1020	RE = VAL(RR$) + 1:
	RL = 40
1040	GET #1,RE:
	INPUT#1,S$
1060	IF INSTR(S$,":") THEN
		POINTER = INSTR(S$,":")
	ELSE
		POINTER = LEN(S$)
1080	S$ = LEFT$(S$,POINTER + 2)  + " to " + TI$ + " " + F$ + MID$(S$,POINTER + 3)
1100	GOSUB 1500
1120	PUT #1,RE:
	CLOSE #1
1140	RETURN
1200	'
1220	'  Accept string into B$ from console
1240	'
1260	GOSUB 1620
1280	B$=SAV$
1300	IF LEN(B$)=0 THEN
		RETURN
1320	IF C=0 THEN
		1400
1340	FOR ZZ=1 TO LEN(B$)
1360		MID$(B$,ZZ,1)=CHR$(ASC(MID$(B$,ZZ,1))+32*(ASC(MID$(B$,ZZ,1))>96))
1380	NEXT ZZ
1400	RETURN
1500	'
1520	'  Fill and store disk record
1540	'
1560	LSET RR$=LEFT$(S$+SPACE$(RL-2),RL-2)+CHR$(13)+CHR$(10)
1580	RETURN
1600	'
1620	CHC=0:
	SAV$=""
1640	NCH=ASC(INPUT$(1))
1660	IF NCH=127 THEN
		1800
1680	IF NCH<32 THEN
		1860
1700	IF CHC>=62 THEN
		PRINT CHR$(7);:
		GOTO 1640
1720	SAV$=SAV$+CHR$(NCH):
	CHC=CHC+1:
	PRINT CHR$(NCH);
1740	IF CHC=55 THEN
		PRINT CHR$(7);
1760	GOTO 1640
1780	'
1800	IF CHC=0 THEN
		1640
	ELSE
		PRINT RIGHT$(SAV$,1);:
		 GOTO 1840
1820	IF CHC=0 THEN
		1640
	ELSE
		PRINT ERS$;
1840	CHC=CHC-1:
	SAV$=LEFT$(SAV$,CHC):
	GOTO 1640
1860	IF NCH=8 THEN
		1820
1880	IF NCH=13 THEN
		PRINT:
		RETURN
1900	IF NCH=21 THEN
		PRINT " #":
		GOTO 1620
1920	IF NCH<>24 OR CHC=0 THEN
		1640
1940	FOR BCC=1 TO CHC:
		 PRINT ERS$;:
	NEXT BCC:
	GOTO 1620
1960 '
2000 ' Date getting subroutine
2020	BASEPORT = &H50
2040	CMDPORT = BASEPORT + 10
2060	DATAPORT = CMDPORT + 1
2080 '**********************************************************
2100 '*		READ THE DATE DIGITS			*
2120 '**********************************************************
2140	FOR DIGIT = 12 TO 7 STEP -1
2160		OUT CMDPORT,(&H10 + DIGIT)
2180		DOY(DIGIT - 7) = INP(DATAPORT)
2200	NEXT DIGIT
2220	YEAR= (DOY(5) * 10) + DOY(4)
2240	MONTH10 = DOY(3)
2260	MONTH1  = DOY(2)
2280	DAY10 = DOY(1)
2300	DAY1  = DOY(0)
2320 '**********************************************************
2340 '*		FORMAT THE FIRST DATE STRING		*
2360 '**********************************************************
2380	DATE1$="        "
2400	MID$(DATE1$,1,1) = RIGHT$(STR$(DAY10),1)
2420	MID$(DATE1$,2,1) = RIGHT$(STR$(DAY1),1)
2440	MID$(DATE1$,3,1) = "/"
2460	MID$(DATE1$,4,1) = RIGHT$(STR$(MONTH10),1)
2480	MID$(DATE1$,5,1) = RIGHT$(STR$(MONTH1),1)
2500	MID$(DATE1$,6,1) = "/"
2520	MID$(DATE1$,7,2) = RIGHT$(STR$(YEAR),2)
2540	DZ$ = DATE1$
2560	DT$ = LEFT$(DATE1$,5)
2580	DD$ = MID$(DATE1$,1,2)
2600	DM$ = MID$(DATE1$,4,2)
2620	RETURN
2700 '
2720 ' Time-finding subroutine
2740	FOR DIGIT = 5 TO 0 STEP -1
2760		OUT CMDPORT,(&H10 + DIGIT)
2780		TOD(DIGIT) = INP(DATAPORT)
2800		IF DIGIT = 5 THEN TOD(DIGIT) = TOD(DIGIT) AND 3
2820	NEXT DIGIT
2840	H(1) = TOD(5)
2860	H(2) = TOD(4)
2880	H(3) = TOD(3)
2900	H(4) = TOD(2)
2920	H(5) = TOD(1)
2940	H(6) = TOD(0)
2960	DH$ = "  ":
	DI$ = "  ":
	DS$ = "  "
2980	MID$(DH$,1,1) = RIGHT$(STR$(H(1)),1):
	MID$(DH$,2,1) = RIGHT$(STR$(H(2)),1):
	MID$(DI$,1,1) = RIGHT$(STR$(H(3)),1):
	MID$(DI$,2,1) = RIGHT$(STR$(H(4)),1):
	MID$(DS$,1,1) = RIGHT$(STR$(H(5)),1):
	MID$(DS$,2,1) = RIGHT$(STR$(H(6)),1)
3000	TI$=DD$+"-"+DH$+":"+DI$
3020	TD$=DH$+":"+DI$+":"+DS$
3040	RETURN
4000	IF ERL=780 THEN
		RESUME 860
4010	IF ERL=1040 THEN
		RESUME 1120
4020	ON ERROR GOTO 0
4030	'
4040	'
44000 '
44020 'CLOCK ROUTINES
44040 '
44060	PRINT:
	PRINT "The time now is (Hrs:Mins:Secs).... ";
44080	TF$="#"
44100	FOR I=1 TO 6
44120		PRINT USING TF$;H(I);
44140		IF I=2 THEN 
			PRINT ":";
44160		IF I=4 THEN 
			PRINT ":";
44180	NEXT I
44200	PRINT
44220 '  Now get hh/mm/ss stored by enterbbs
44240	HT(1)=PEEK(74):
	HT(2)=PEEK(75):
	HT(3)=PEEK(76)
44260	HT(4)=PEEK(77):
	HT(5)=PEEK(78):
	HT(6)=PEEK(79)
44280 '  And calculate the difference...
44300	IF H(1) < HT(1) THEN
		H(1) = H(1) + 2:
		H(2) = H(2) + 4
44320	IF H(6)<HT(6) THEN 
		H(6)=H(6)+10:
		H(5)=H(5)-1
44340	IF H(5)<HT(5) THEN 
		H(5)=H(5)+6:
		H(4)=H(4)-1
44360	IF H(4)<HT(4) THEN 
		H(4)=H(4)+10:
		H(3)=H(3)-1
44380	IF H(3)<HT(3) THEN 
		H(3)=H(3)+6:
		H(2)=H(2)-1
44400	IF H(2)<HT(2) THEN 
		H(2)=H(2)+10:
		H(1)=H(1)-1
44420	HD(6)=H(6)-HT(6):
	HD(5)=H(5)-HT(5):
	HD(4)=H(4)-HT(4)
44440	HD(3)=H(3)-HT(3):
	HD(2)=H(2)-HT(2):
	HD(1)=H(1)-HT(1)
44460	PRINT "You've been on the system for...... ";
44480	TF$="#"
44500	FOR I=1 TO 6
44520		PRINT USING TF$;HD(I);
44540		IF I=2 THEN 
			PRINT ":";
44560		IF I=4 THEN 
			PRINT ":";
44580	NEXT I
44600	PRINT:
	PRINT
44620	RETURN
