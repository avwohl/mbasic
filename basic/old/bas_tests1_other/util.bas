160 '
180 ' RBBSUTIL.BAS ==> UTILITY PROGRAM FOR THE RBBS REMOTE BULLETIN BOARD SYS
200 ' BY RON FOWLER, WESTLAND, MICH RBBS (313)-729-1905 (RINGBACK)
220 ' Please report any problems, bugs, fixes, etc. to the above RBBS if
221 ' if in USA or to: 
230 ' Bill Bolton, "Software Tools" RCPM (02)997-1836 (modem)
235 ' if in Australia
240 '
260 ' 06/Jun/82
280 ' Passwords in messages were being killed during purges only if
300 ' the messages were renumbered, fixed now. Added code to 
320 ' read date from LASTCALR (lifted from MINIRBBS) and default
340 ' to current date if new date not specifically entered. Added
360 ' password check so that this utility can be left out for remote
380 ' use (but make it an unusual name, SYS and TAG as well).
400 ' Bill Bolton (Australia)
420 '
430 ' 14/Jun/82
440 ' Upper case conversion added to file name entered with D option
445 ' and UTIL status permanetly written to CALLERS for those who
446 ' find this file. Also TW status written to LASTCALR and 
447 ' immediate log out for those that ignore warning. Bill Bolton
450 '
460 ' 21/Mar/82
470 ' Added password check for "*" in messages to ALL. Version 2.5
480 ' Bill Bolton
490 '
500 ' 07/Jul/83
510 ' Added more stringent password check from ENTRBBS version 3.1
520 ' and fixed some bugs in the command processor code. Added freeze
530 ' and abort code to D option. Added uppercase conversion to F
540 ' option. Version 2.6 Bill Bolton
550 '
560 ' 13/Jul/83
570 ' Added file renaming and deletion options. Version 2.7 Bill Bolton
580 '
980	DEFINT A-Z
990	VERS$ = "Vers 2.7"
1000	ON ERROR GOTO 4030
1010	DIM M(200,2)
1020	SEP$ = "=============================================="
1030	CRLF$ = CHR$(13) + CHR$(10)
1040	PURGED = 0:
	BACKUP = 0
1050	GOSUB 4210		' BUILD MSG INDEX
1060	N$ = "SYSOP":
	O$ = "":
	MAGIC$ = "SUPER"
1070	GOSUB 4390		'Test for SYSOP
1080	PRINT:
	PRINT "             RCPM Utilty ";VERS$
1090	PRINT SEP$
1100	MSGS = 1:
	CALLS = MSGS + 1:
	MNUM = CALLS + 1
1110	PRINT:
	INPUT "Command? ",PROMPT$
1120	PRINT:
	PRINT:
	IF PROMPT$ = "" THEN
		GOSUB 1160:
		GOTO 1110
1130	B$ = MID$(PROMPT$,1,1):
	GOSUB 2330:
	SM$ = B$:
	SM = INSTR ("TFDPEBKRA",SM$):
	GOSUB 1140:
	GOTO 1110
1140	IF SM = 0 THEN
		1160
1150	ON SM GOTO 1730,1630,1430,2500,1300,3210,4800,4900
1160	PRINT:
	PRINT "Commands allowed are:"
1170	PRINT "B   ==> build summary file from message file"
1180	PRINT "D   ==> display an ascii file"
1190	PRINT "E   ==> end the utility program"
1200	PRINT "F   ==> prints the disk directory
1210	PRINT "K   ==> kill a file"
1220	PRINT "P   ==> purge the message files"
1230	PRINT "R   ==> rename a file"
1240	PRINT "T   ==> transfers a disk file to the message file"
1250	RETURN
1260 '
1300 ' END OF PROGRAM
1310 '
1320	PRINT:
	PRINT:
	END
1400 '
1410 ' DISPLAY A FILE
1420 '
1430	B$ = MID$(PROMPT$,2):
	IF B$ = "" THEN
		INPUT "Filename? ",B$:
		PRINT
1440	IF B$ = "" THEN
		RETURN
	ELSE
		GOSUB 2330:
		FILN$ = B$
1450	OPEN "I",1,FILN$
1460	IF EOF(1) THEN
		1500
1470	BI = ASC(INKEY$+" "):
	IF BI = 19 THEN
		BI = ASC(INPUT$(1))
1480	IF BI = 11 THEN
		PRINT:
		PRINT "++ Aborted ++":
		PRINT:
		CLOSE:
		RETURN
1490	LINE INPUT #1,LIN$:
	PRINT LIN$:
	GOTO 1460
1500	CLOSE:
	PRINT:
	PRINT:
	PRINT "++ End Of File ++":
	PRINT
1510	RETURN
1600 '
1610 ' DISPLAY DIRECTORY
1620 '
1630	B$ = PROMPT$:
	GOSUB 2330:
	IF LEN(B$) > 1 THEN
		SPEC$ = MID$(B$,3)
	ELSE
		SPEC$ = "*.*"
1640	FILES SPEC$:
	PRINT:
	RETURN
1700 '
1710 ' TRANSFER A DISK FILE
1720 '
1730	PRINT "Active # of msg's ";:
	OPEN "R",1,"COUNTERS",5:
	FIELD#1,5 AS RR$:
	GET#1,MSGS:
	M = VAL(RR$)
1740	PRINT STR"$(M) + " "
1750	PRINT "Last caller was # ";:
	GET#1,CALLS:
	PRINT STR$(VAL(RR$))
1760	PRINT "This msg # will be ";:
	GET#1,MNUM:
	U = VAL(RR$):
	PRINT STR$(U + 1):
	CLOSE
1800 '
1810 ' ***ENTER A NEW MESSAGE***
1820 '
1830	IF NOT PURGED THEN
		PRINT "Files must be purged before messages can be added":
		RETURN
1840	OPEN "R",1,"COUNTERS",5:
	PRINT "Msg # will be ";:
	FIELD#1,5 AS RR$:
	GET#1,MNUM:
	V = VAL(RR$)
1850	PRINT STR$(V + 1):
	CLOSE
1860	INPUT "Message file name? ",B$:
	GOSUB 2330:
	FIL$ = B$
1870	INPUT "Todays date (DD/MM/YY)?",B$:
	GOSUB 2330:
	IF B$ = "" THEN
		D$ = DT$
	ELSE
		D$ = B$
1880	INPUT "Who to (C/R for ALL)?";B$:
	GOSUB 2330:
	IF B$ = "" THEN
		T$ = "ALL"
	ELSE
		T$ = B$
1890	INPUT "Subject?",B$:
	GOSUB 2330:
	K$ = B$
1900	INPUT "Password?",B$:
	GOSUB 2330:
	PW$ = B$:
	IF T$ = "ALL" AND LEFT$(PW$,1) = "*" THEN
		PRINT CHR$(7);"You CANNOT use '*' with ALL.":
		GOTO 1900
1910	F = 0			' F IS MESSAGE LENGTH
1920	PRINT "Updating counters":
	OPEN "R",1,"COUNTERS",5:
	FIELD#1,5 AS RR$
1930	GET#1,MNUM:
	LSET RR$ = STR$(VAL(RR$) + 1):
	PUT#1,MNUM
1940	GET#1,MSGS:
	LSET RR$ = STR$(VAL(RR$) + 1):
	PUT#1,MSGS:
	CLOSE#1
1950	PRINT "Updating msg file":
	OPEN "R",1,"MESSAGES",65:
	RL = 65
1960	FIELD#1,65 AS RR$
1970	RE = MX + 7:
	F = 0
1980	OPEN "I",2,FIL$:
	IF EOF(2) THEN
		PRINT "File empty.":
		CLOSE#1:
		CLOSE#2:
		END
1990	IF EOF(2) THEN
		S$ = "9999":
		GOSUB 2400:
		PUT #1,RE:
		CLOSE #2:
		GOTO 2030
2000	LINE INPUT #2,S$
2010	IF LEN(S$) > 63 THEN
		S$ = LEFT$(S$,63)
2020	PRINT S$:
	GOSUB 2400:
	PUT #1,RE:
	RE = RE + 1:
	F = F + 1:
	GOTO 1990
2030	RE = MX + 1
2040	S$ = STR$(V + 1):
	GOSUB 2400:
	PUT#1,RE
2050	RE = RE + 1:
	S$ = D$:
	GOSUB 2400:
	PUT#1,RE
2060	RE = RE + 1:
	S$ = N$ + " " + O$:
	GOSUB 2400:
	PUT#1,RE
2070	RE = RE + 1:
	S$ = T$:
	GOSUB 2400:
	PUT#1,RE
2080	RE = RE + 1:
	S$ = K$:
	GOSUB 2400:
	PUT#1,RE:
	RE = RE + 1:
	S$ = STR$(F):
	GOSUB 2400:
	PUT#1,RE
2090	CLOSE #1
2100	IF PW$ <> "" THEN
		PW$ = ";" + PW$
2110	PRINT "Updating summary file."
2120	OPEN "R",1,"SUMMARY",30:
	RE = 1:
	FIELD#1,30 AS RR$:
	RL = 30
2130	RE = MZ * 6 + 1:
	S$ = STR$(V + 1) + PW$:
	GOSUB 2400:
	PUT#1,RE
2140	RE = RE + 1:
	S$ = D$:
	GOSUB 2400:
	PUT#1,RE
2150	RE = RE + 1:
	S$ = N$ + " " + O$:
	GOSUB 2400:
	PUT#1,RE
2160	RE = RE + 1:
	S$ = T$:
	GOSUB 2400:
	PUT#1,RE
2170	RE = RE + 1:
	S$ = K$:
	GOSUB 2400:
	PUT#1,RE
2180	RE = RE + 1:
	S$ = STR$(F):
	GOSUB 2400:
	PUT#1,RE
2190	RE = RE + 1:
	S$ = " 9999":
	GOSUB 2400:
	PUT#1,RE
2200	CLOSE#1
2210	MX = MX + F + 6:
	MZ = MZ + 1:
	M(MZ,1) = V + 1:
	M(MZ,2) = F
2220	U = U + 1
2230	RETURN
2300 '
2310 ' Convert the string B$ to upper case
2320 '
2330	FOR ZZ=1 TO LEN(B$):
		MID$(B$,ZZ,1) = CHR$(ASC(MID$(B$,ZZ,1)) + 32 * (ASC(MID$(B$,ZZ,1)) > 96)):
	NEXT ZZ:
	RETURN
2400 '
2410 ' FILL AND STORE DISK RECORD
2420 '
2430	LSET RR$ = LEFT$(S$ + SPACE$(RL - 2),RL - 2) + CHR$(13) + CHR$(10)
2440	RETURN
2500 '
2510 ' PURGE KILLED MESSAGES FROM FILES
2520 '
2530	IF PURGED THEN
		PRINT "Files already purged.":
		RETURN
2540	INPUT "Today's date (DD/MM/YY) ?",DATE$
2550	IF LEN(DATE$) > 8 THEN
		PRINT "Must be less then 8 characters.":
		GOTO 2540
2560	IF DATE$ = "" THEN
		DATE$ = DT$
2570	OPEN "R",1,DATE$+".ARC"
2580	IF LOF(1) > 0 THEN
		PRINT "Archive file: ";DATE$ + ".ARC";" exists.":
		CLOSE:
		RETURN
2590	CLOSE
2600	MSGN = 1:
	INPUT "Renumber messages?",PK$:
	PK$ = MID$(PK$,1,1)
2610	IF PK$ = "y" THEN
		PK$ = "Y"
2620	IF PK$ <> "Y" THEN
		2650
2630	INPUT "Message number to start (CR=1)?",MSG$:
	IF MSG$ = "" THEN
		MSG$="1"
2640	MSGN = VAL(MSG$):
	IF MSGN = 0 THEN
		PRINT "Invalid msg #.":
		RETURN
2650	PRINT "Purging summary file...":
	OPEN "R",1,"SUMMARY",30
2660	FIELD#1,30 AS R1$
2670	R1 = 1
2680	OPEN "R",2,"$SUMMARY.$$$",30
2690	FIELD#2,30 AS R2$
2700	R2 = 1
2710	PRINT SEP$:
	GET#1,R1:
	IF EOF(1) THEN
		2840
2720	IF VAL(R1$) = 0 THEN
		R1 = R1 + 6:
		PRINT "Deletion":
		GOTO 2710
2730	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		IF INSTR(R1$,";") THEN
			PASS$ = MID$(R1$,INSTR(R1$,";"),27)
		ELSE
			PASS$ = SPACE$(28)
2740	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		LSET R2$ = LEFT$(STR$(MSGN) + PASS$,28) + CHR$(13) + CHR$(10):
		MSGN = MSGN + 1:
		GOTO 2760
2750	LSET R2$ = R1$
2760	PUT #2,R2
2770	PRINT LEFT$(R2$,28)
2780	IF VAL(R1$) > 9998 THEN
		2840
2790	FOR I = 1 TO 5
2800		R1 = R1 + 1:
		R2 = R2 + 1:
		GET#1,R1:
		LSET R2$ = R1$:
		PUT#2,R2
2810		PRINT LEFT$(R2$,28)
2820	NEXT I
2830	R1 = R1 + 1:
	R2 = R2 + 1:
	GOTO 2710
2840	CLOSE:
	OPEN "O",1,"SUMMARY.BAK":
	CLOSE:
	KILL "SUMMARY.BAK":
	NAME "SUMMARY" AS "SUMMARY.BAK":
	NAME "$SUMMARY.$$$" AS "SUMMARY"
2850	PRINT "Purging message file...":
	MSGN = VAL(MSG$)
2860	OPEN "R",1,"MESSAGES",65:
	FIELD #1,65 AS R1$
2870	OPEN "R",2,"$MESSAGS.$$$",65:
	FIELD #2,65 AS R2$
2880	OPEN "O",3,DATE$+".ARC":
	R1 = 1:
	KIL = 0
2890	R1 = 1:
	R2 = 1
2900	PRINT SEP$:
	GET #1,R1:
	IF EOF(1) THEN
		 3100
2910	IF VAL(R1$) = 0 THEN
		KIL = -1:
		PRINT "Archiving message":
		GOTO 2970
2920	KIL = 0
2930	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		IF INSTR(R1$,";") THEN
			PASS$ = MID$(R1$,INSTR(R1$,";"),62)
		ELSE
			PASS$ = SPACE$(62)
2940	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		LSET R2$ = LEFT$(STR$(MSGN) + PASS$,63) + CHR$(13) + CHR$(10):
		MSGN = MSGN + 1:
		PRINT LEFT$(R2$,63):
		GOTO 2960
2950	LSET R2$ = R1$:
	PRINT LEFT$(R2$,6)
2960	PUT #2,R2
2970	IF KIL THEN
		GOSUB 4310:
		PRINT #3,KL$
2980	IF VAL(R1$) > 9998 THEN
		3100
2990	FOR I = 1 TO 5
3000		R1 = R1 + 1:
		IF NOT KIL THEN
			R2 = R2 + 1
3010		GET #1,R1:
		IF KIL THEN
			GOSUB 4310:
			PRINT #3,KL$:
			GOTO 3030
3020		LSET R2$ = R1$:
		PUT #2,R2:
		PRINT LEFT$(R2$,63)
3030	NEXT I
3040	FOR I = 1 TO VAL(R1$):
		R1 = R1 + 1:
		IF NOT KIL THEN
			R2 = R2 + 1
3050		GET #1,R1:
		IF KIL THEN
			GOSUB 4310:
			PRINT #3,KL$:
			GOTO 3070
3060		LSET R2$ = R1$:
		PUT #2,R2:
		PRINT LEFT$(R2$,63)
3070	NEXT I:
	R1 = R1 + 1:
	IF NOT KIL THEN
		R2 = R2 + 1
3080	GOTO 2900
3090 '
3100	CLOSE:
	OPEN "O",1,"MESSAGES.BAK":
	CLOSE:
	KILL "MESSAGES.BAK":
	NAME "MESSAGES" AS "MESSAGES.BAK":
	NAME "$MESSAGS.$$$" AS "MESSAGES"
3110	PRINT "Updating counters..."
3120	OPEN "O",1,"COUNTERS.BAK":
	CLOSE:
	KILL "COUNTERS.BAK"
3130	OPEN "R",1,"COUNTERS",15:
	FIELD #1,10 AS C1$,5 AS C2$
3140	OPEN "R",2,"COUNTERS.BAK",15:
	FIELD #2,15 AS R2$
3150	GET #1,1:
	LSET R2$ = C1$ + C2$:
	PUT #2,1
3160	IF PK$ = "Y" THEN
		LSET C2$ = STR$(MSGN - 1):
		PUT #1,1
3170	CLOSE
3180	PURGED = -1:
	GOSUB 4210:
	RETURN
3200 '
3210 ' BUILD SUMMARY FILE FROM MESSAGE FILE
3220 '
3230	PRINT "Building summary file..."
3240	OPEN "O",1,"SUMMARY.BAK":
	CLOSE:
	KILL "SUMMARY.BAK"
3250	OPEN "R",1,"MESSAGES",65:
	FIELD #1,65 AS R1$:
	R1 = 1
3260	OPEN "R",2,"SUMMARY.$$$",30:
	FIELD #2,30 AS R2$:
	R2 = 1
3270	PRINT SEP$
3280	FOR I = 1 TO 6
3290		GET #1,R1:
		IF EOF(1) THEN
			3340
3300		LSET R2$ = LEFT$(R1$,28) + CRLF$:
		PUT #2,R2
3310		R1 = R1 + 1:
		R2 = R2 + 1:
		PRINT LEFT$(R2$,28):
		IF EOF(1) THEN
			3340
3320		IF I = 1 THEN
			IF VAL(R1$) > 9998 THEN
				3340
3330	NEXT I:
	R1 = R1 + VAL(R1$):
	GOTO 3270
3340	CLOSE:
	NAME "SUMMARY" AS "SUMMARY.BAK":
	NAME "SUMMARY.$$$" AS "SUMMARY"
3350	PRINT "Summary file built.":
	RETURN
4000 '
4010 ' Error handlers
4020 '
4030	IF (ERL = 1640) AND (ERR = 53) THEN
		PRINT "File not found.":
		RESUME 1110
4040	IF (ERL = 1450) AND (ERR = 53) THEN
		PRINT "File not found.":
		CLOSE:
		RESUME 1510
4050	IF (ERL = 4970) AND (ERR = 53) THEN
		PRINT "You cannot rename a file that doesn't already exist":
		RESUME 1110
4060	IF (ERL = 4850) AND (ERR = 53) THEN
		PRINT "That file doesn't exist so you can't erase it":
		RESUME 1110
4070	PRINT "Error number ";ERR;" in line number ";ERL
4080	RESUME 1110
4200 '
4210 ' build message index
4220 '
4230	MX = 0:
	MZ = 0
4240	OPEN "R",1,"SUMMARY",30:
	RE = 1:
	FIELD#1,28 AS RR$
4250	GET#1,RE:
	IF EOF(1) THEN
		4290
4260	G = VAL(RR$):
	MZ = MZ + 1:
	M(MZ,1) = G:
	IF G = 0 THEN
		4280
4270	IF G > 9998 THEN
		MZ = MZ - 1:
		GOTO 4290
4280	GET#1,RE + 5:
	M(MZ,2) = VAL(RR$):
	MX = MX + M(MZ,2) + 6:
	RE = RE + 6:
	GOTO 4250
4290	CLOSE:
	RETURN
4300 '
4310 ' unpack record
4320 '
4330	ZZ = LEN(R1$) - 2
4340	WHILE MID$(R1$,ZZ,1) = " "
4350	ZZ = ZZ - 1:
	IF ZZ = 1 THEN
		4370
4360	WEND
4370	KL$ = LEFT$(R1$,ZZ)
4380	RETURN
4390 '
4400 ' Test to only allow the SYSOP to use UTIL remotely
4410 '
4420	OPEN "I",1,"A:LASTCALR":
	INPUT #1,N$,O$,F$,DT$:
	CLOSE
4430	OPEN "I",1,"A:PWDS":
	INPUT #1,P1$,P2$:
	CLOSE #1
4440	PRINT
4450	IF N$ = MAGIC$ AND O$ = "" THEN
			GOSUB 4610:
			IF SYSOP = 1 THEN
				RETURN
4460	PRINT
4470	OPEN "R",1,"A:CALLERS",60:
	FIELD #1, 60 AS RR$:
	GET #1,1
4480	RE = VAL(RR$) + 1:
	RL = 60
4490	GET #1,RE:
	INPUT# 1,S$
4500	IF INSTR(S$,"UTIL") THEN
		GOTO 4690
4510	S$ = S$ + " UTIL":
	GOSUB 2400:
	PUT #1,RE:
	CLOSE #1
4520	PRINT "You know you're not the SYSOP, what are you doing here??"
4530	PRINT
4540	PRINT "Go away, your name has been logged for further action!"
4550	PRINT
4560	END
4600 '
4610 '  SYSOP password check
4620 '
4630	PRINT "2nd Codeword? ";:
	B$ = INPUT$(10):
	GOSUB 2330:
	X$ = B$:
4640	PRINT
4650	IF INSTR(X$,P2$) THEN
		IF (MID$(DT$,1,1) = MID$(X$,10,1)) AND (MID$(DT$,2,1) = MID$(X$,9,1)) THEN
			F$ = "":
			SYSOP = 1:
			RETURN
4660	'Use this in place of 5680 if you dont have a real time clock
	IF INSTR(X$,P$) THEN
		F$ = "":
		SYSOP = 1:
		RETURN
4670	SYSOP = 0:
	RETURN
4680	'
4690	F$ = "TW"		'User has achieved temporary twit status
4700	OPEN "O",2,"A:LASTCALR. " + CHR$(&HA0):
	PRINT#2,N$;",";O$;",";F$;",";DZ$:
	CLOSE
4710	PRINT "You were warned to stay out of the SYSOP's domain"
4720	PRINT
4730	PRINT "You are being logged off this system IMMEDIATELY"
4740	PRINT
4750	CHAIN "BYE"
4760	END
4800	'
4810	' Kill (Erase) a file
4820	'
4830	B$ = MID$(PROMPT$,3):
	IF B$ = "" THEN
		INPUT "Filename? ",B$:
		PRINT
4840	IF B$ = "" THEN
		RETURN
	ELSE
		GOSUB 2330:
		FILN$ = B$
4850	KILL FILN$
4860	PRINT
4870	RETURN
4900	'
4910	' Rename a file
4920	'
4930	INPUT "Existing Filename? ",B$:
	PRINT
4940	IF B$ = "" THEN
		RETURN
	ELSE
		GOSUB 2330:
		EFILN$ = B$
4950	PRINT:
	INPUT "New Filename? ",B$:
	PRINT
4960	IF B$ = "" THEN
		RETURN
	ELSE
		GOSUB 2330:
		NFILN$ = B$
4970	NAME EFILN$ AS NFILN$
4980	PRINT:
	RETURN
	PRINT
4960	IF B$ = "" THEN
		RETURN
	ELSE
		GOSUB 2330:
		NFILN$ = B$
4970	NAME