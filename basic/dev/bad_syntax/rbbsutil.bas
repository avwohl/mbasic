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
460 '
980	DEFINT A-Z
990	VERS$ = "Vers 2.4"
1000	ON ERROR GOTO 4500
1020	DIM M(200,2)
1040	SEP$ = "=============================================="
1060	CRLF$ = CHR$(13) + CHR$(10)
1080	PURGED = 0:
	BACKUP = 0
1120	GOSUB 4580		' BUILD MSG INDEX
1140	N$ = "SYSOP":
	O$ = "":
	MAGIC$ = "SUPER"
1160	GOSUB 5000		'Test for SYSOP
1180	PRINT:
	PRINT "             RCPM Utilty ";VERS$
1200	PRINT SEP$
1220	MSGS = 1:
	CALLS = MSGS + 1:
	MNUM = CALLS + 1
1240	PRINT:
	INPUT "Command? ",PROMPT$
1260	PRINT:
	PRINT:
	IF PROMPT$ = "" THEN
		1340
1280	B$ = MID$(PROMPT$,1,1):
	GOSUB 2720:
	SM$ = B$:
	SM = INSTR ("TFDPEB",SM$):
	GOSUB 1300:
	GOTO 1240
1300	IF SM = 0 THEN
		1340
1320	ON SM GOTO 1780,1720,1560,2840,1500,4200
1340	PRINT:
	PRINT "Commands allowed are:"
1360	PRINT "B   ==> build summary file from message file."
1380	PRINT "D   ==> display an ascii file"
1400	PRINT "E   ==> end the utility program."
1420	PRINT "F   ==> prints the disk directory."
1440	PRINT "P   ==> purge the message files"
1460	PRINT "T   ==> transfers a disk file to the message file."
1480	RETURN
1490 '
1500 ' END OF PROGRAM
1510 '
1520	PRINT:
	PRINT:
	END
1530 '
1540 ' DISPLAY A FILE
1550 '
1560	B$ = MID$(PROMPT$,2):
	PRINT:
	IF B$ = "" THEN
		INPUT "Filename? ",B$:
		PRINT
1570	GOSUB 2720:
	FILN$ = B$
1580	OPEN "I",1,FILN$
1600	IF EOF(1) THEN
		1660
1620	IF INKEY$ <> "" THEN
		CLOSE:
		PRINT:
		PRINT "++ Aborted ++":
		PRINT:
		RETURN
1640	LINE INPUT #1,LIN$:
	PRINT LIN$:
	GOTO 1600
1660	CLOSE:
	PRINT:
	PRINT:
	PRINT "++ END OF FILE ++":
	PRINT
1680	RETURN
1690 '
1700 ' DISPLAY DIRECTORY
1710 '
1720	IF LEN(PROMPT$) > 1 THEN
		SPEC$ = MID$(PROMPT$,2)
	ELSE
		SPEC$ = "*.*"
1740	FILES SPEC$:
	PRINT:
	RETURN
1750 '
1760 ' TRANSFER A DISK FILE
1770 '
1780	PRINT "Active # of msg's ";:
	OPEN "R",1,"COUNTERS",5:
	FIELD#1,5 AS RR$:
	GET#1,MSGS:
	M = VAL(RR$)
1800	PRINT STR"$(M) + " "
1820	PRINT "Last caller was # ";:
	GET#1,CALLS:
	PRINT STR$(VAL(RR$))
1840	PRINT "This msg # will be ";:
	GET#1,MNUM:
	U = VAL(RR$):
	PRINT STR$(U + 1):
	CLOSE
1860 '
1880 ' ***ENTER A NEW MESSAGE***
1900 '
1920	IF NOT PURGED THEN
		PRINT "Files must be purged before messages can be added":
		RETURN
1940	OPEN "R",1,"COUNTERS",5:
	PRINT "Msg # will be ";:
	FIELD#1,5 AS RR$:
	GET#1,MNUM:
	V = VAL(RR$)
1960	PRINT STR$(V + 1):
	CLOSE
1980	INPUT "Message file name? ",B$:
	GOSUB 2720:
	FIL$ = B$
2000	INPUT "Todays date (DD/MM/YY)?",B$:
	GOSUB 2720:
	IF B$ = "" THEN
		D$ = DT$
	ELSE
		D$ = B$
2020	INPUT "Who to (C/R for ALL)?";B$:
	GOSUB 2720:
	IF B$ = "" THEN
		T$ = "ALL"
	ELSE
		T$ = B$
2040	INPUT "Subject?",B$:
	GOSUB 2720:
	K$ = B$:
	INPUT "Password?",B$:
	GOSUB 2720:
	PW$ = B$
2060	F = 0			' F IS MESSAGE LENGTH
2080	PRINT "Updating counters":
	OPEN "R",1,"COUNTERS",5:
	FIELD#1,5 AS RR$
2100	GET#1,MNUM:
	LSET RR$ = STR$(VAL(RR$) + 1):
	PUT#1,MNUM
2120	GET#1,MSGS:
	LSET RR$ = STR$(VAL(RR$) + 1):
	PUT#1,MSGS:
	CLOSE#1
2140	PRINT "Updating msg file":
	OPEN "R",1,"MESSAGES",65:
	RL = 65
2160	FIELD#1,65 AS RR$
2180	RE = MX + 7:
	F = 0
2200	OPEN "I",2,FIL$:
	IF EOF(2) THEN
		PRINT "File empty.":
		CLOSE#1:
		CLOSE#2:
		END
2220	IF EOF(2) THEN
		S$ = "9999":
		GOSUB 2740:
		PUT #1,RE:
		CLOSE #2:
		GOTO 2300
2240	LINE INPUT #2,S$
2260	IF LEN(S$) > 63 THEN
		S$ = LEFT$(S$,63)
2280	PRINT S$:
	GOSUB 2740:
	PUT #1,RE:
	RE = RE + 1:
	F = F + 1:
	GOTO 2220
2300	RE = MX + 1
2320	S$ = STR$(V + 1):
	GOSUB 2740:
	PUT#1,RE
2340	RE = RE + 1:
	S$ = D$:
	GOSUB 2740:
	PUT#1,RE
2360	RE = RE + 1:
	S$ = N$ + " " + O$:
	GOSUB 2740:
	PUT#1,RE
2380	RE = RE + 1:
	S$ = T$:
	GOSUB 2740:
	PUT#1,RE
2400	RE = RE + 1:
	S$ = K$:
	GOSUB 2740:
	PUT#1,RE:
	RE = RE + 1:
	S$ = STR$(F):
	GOSUB 2740:
	PUT#1,RE
2420	CLOSE #1
2440	IF PW$ <> "" THEN
		PW$ = ";" + PW$
2460	PRINT "Updating summary file."
2480	OPEN "R",1,"SUMMARY",30:
	RE = 1:
	FIELD#1,30 AS RR$:
	RL = 30
2500	RE = MZ * 6 + 1:
	S$ = STR$(V + 1) + PW$:
	GOSUB 2740:
	PUT#1,RE
2520	RE = RE + 1:
	S$ = D$:
	GOSUB 2740:
	PUT#1,RE
2540	RE = RE + 1:
	S$ = N$ + " " + O$:
	GOSUB 2740:
	PUT#1,RE
2560	RE = RE + 1:
	S$ = T$:
	GOSUB 2740:
	PUT#1,RE
2580	RE = RE + 1:
	S$ = K$:
	GOSUB 2740:
	PUT#1,RE
2600	RE = RE + 1:
	S$ = STR$(F):
	GOSUB 2740:
	PUT#1,RE
2620	RE = RE + 1:
	S$ = " 9999":
	GOSUB 2740:
	PUT#1,RE
2640	CLOSE#1
2660	MX = MX + F + 6:
	MZ = MZ + 1:
	M(MZ,1) = V + 1:
	M(MZ,2) = F
2680	U = U + 1
2700	RETURN
2705 '
2710 ' Convert the string B$ to upper case
2715 '
2720	FOR ZZ=1 TO LEN(B$):
		MID$(B$,ZZ,1) = CHR$(ASC(MID$(B$,ZZ,1)) + 32 * (ASC(MID$(B$,ZZ,1)) > 96)):
	NEXT ZZ:
	RETURN
2740 '
2760 ' FILL AND STORE DISK RECORD
2780 '
2800	LSET RR$ = LEFT$(S$ + SPACE$(RL - 2),RL - 2) + CHR$(13) + CHR$(10)
2820	RETURN
2840 '
2860 ' PURGE KILLED MESSAGES FROM FILES
2880 '
2900	IF PURGED THEN
		PRINT "Files already purged.":
		RETURN
2920	INPUT "Today's date (DD/MM/YY) ?",DATE$
2940	IF LEN(DATE$) > 8 THEN
		PRINT "Must be less then 8 characters.":
		GOTO 2920
2960	IF DATE$ = "" THEN
		DATE$ = DT$
2980	OPEN "R",1,DATE$+".ARC"
3000	IF LOF(1) > 0 THEN
		PRINT "Archive file: ";DATE$ + ".ARC";" exists.":
		CLOSE:
		RETURN
3020	CLOSE
3040	MSGN = 1:
	INPUT "Renumber messages?",PK$:
	PK$ = MID$(PK$,1,1)
3060	IF PK$ = "y" THEN
		PK$ = "Y"
3080	IF PK$ <> "Y" THEN
		3140
3100	INPUT "Message number to start (CR=1)?",MSG$:
	IF MSG$ = "" THEN
		MSG$="1"
3120	MSGN = VAL(MSG$):
	IF MSGN = 0 THEN
		PRINT "Invalid msg #.":
		RETURN
3140	PRINT "Purging summary file...":
	OPEN "R",1,"SUMMARY",30
3160	FIELD#1,30 AS R1$
3180	R1 = 1
3200	OPEN "R",2,"$SUMMARY.$$$",30
3220	FIELD#2,30 AS R2$
3240	R2 = 1
3260	PRINT SEP$:
	GET#1,R1:
	IF EOF(1) THEN
		3520
3280	IF VAL(R1$) = 0 THEN
		R1 = R1 + 6:
		PRINT "Deletion":
		GOTO 3260
3300	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		IF INSTR(R1$,";") THEN
			PASS$ = MID$(R1$,INSTR(R1$,";"),27)
		ELSE
			PASS$ = SPACE$(28)
3320	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		LSET R2$ = LEFT$(STR$(MSGN) + PASS$,28) + CHR$(13) + CHR$(10):
		MSGN = MSGN + 1:
		GOTO 3360
3340	LSET R2$ = R1$
3360	PUT #2,R2
3380	PRINT LEFT$(R2$,28)
3400	IF VAL(R1$) > 9998 THEN
		3520
3420	FOR I = 1 TO 5
3440		R1 = R1 + 1:
		R2 = R2 + 1:
		GET#1,R1:
		LSET R2$ = R1$:
		PUT#2,R2
3460		PRINT LEFT$(R2$,28)
3480	NEXT I
3500	R1 = R1 + 1:
	R2 = R2 + 1:
	GOTO 3260
3520	CLOSE:
	OPEN "O",1,"SUMMARY.BAK":
	CLOSE:
	KILL "SUMMARY.BAK":
	NAME "SUMMARY" AS "SUMMARY.BAK":
	NAME "$SUMMARY.$$$" AS "SUMMARY"
3540	PRINT "Purging message file...":
	MSGN = VAL(MSG$)
3560	OPEN "R",1,"MESSAGES",65:
	FIELD #1,65 AS R1$
3580	OPEN "R",2,"$MESSAGS.$$$",65:
	FIELD #2,65 AS R2$
3600	OPEN "O",3,DATE$+".ARC":
	R1 = 1:
	KIL = 0
3620	R1 = 1:
	R2 = 1
3640	PRINT SEP$:
	GET #1,R1:
	IF EOF(1) THEN
		 4020
3660	IF VAL(R1$) = 0 THEN
		KIL = -1:
		PRINT "Archiving message":
		GOTO 3780
3680	KIL = 0
3700	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		IF INSTR(R1$,";") THEN
			PASS$ = MID$(R1$,INSTR(R1$,";"),62)
		ELSE
			PASS$ = SPACE$(62)
3720	IF PK$ = "Y" AND VAL(R1$) < 9999 THEN
		LSET R2$ = LEFT$(STR$(MSGN) + PASS$,63) + CHR$(13) + CHR$(10):
		MSGN = MSGN + 1:
		PRINT LEFT$(R2$,63):
		GOTO 3760
3740	LSET R2$ = R1$:
	PRINT LEFT$(R2$,6)
3760	PUT #2,R2
3780	IF KIL THEN
		GOSUB 4740:
		PRINT #3,KL$
3800	IF VAL(R1$) > 9998 THEN
		4020
3820	FOR I = 1 TO 5
3840		R1 = R1 + 1:
		IF NOT KIL THEN
			R2 = R2 + 1
3860		GET #1,R1:
		IF KIL THEN
			GOSUB 4740:
			PRINT #3,KL$:
			GOTO 3900
3880		LSET R2$ = R1$:
		PUT #2,R2:
		PRINT LEFT$(R2$,63)
3900	NEXT I
3920	FOR I = 1 TO VAL(R1$):
		R1 = R1 + 1:
		IF NOT KIL THEN
			R2 = R2 + 1
3940		GET #1,R1:
		IF KIL THEN
			GOSUB 4740:
			PRINT #3,KL$:
			GOTO 3980
3960		LSET R2$ = R1$:
		PUT #2,R2:
		PRINT LEFT$(R2$,63)
3980	NEXT I:
	R1 = R1 + 1:
	IF NOT KIL THEN
		R2 = R2 + 1
4000	GOTO 3640
4010 '
4020	CLOSE:
	OPEN "O",1,"MESSAGES.BAK":
	CLOSE:
	KILL "MESSAGES.BAK":
	NAME "MESSAGES" AS "MESSAGES.BAK":
	NAME "$MESSAGS.$$$" AS "MESSAGES"
4040	PRINT "Updating counters..."
4060	OPEN "O",1,"COUNTERS.BAK":
	CLOSE:
	KILL "COUNTERS.BAK"
4080	OPEN "R",1,"COUNTERS",15:
	FIELD #1,10 AS C1$,5 AS C2$
4100	OPEN "R",2,"COUNTERS.BAK",15:
	FIELD #2,15 AS R2$
4120	GET #1,1:
	LSET R2$ = C1$ + C2$:
	PUT #2,1
4140	IF PK$ = "Y" THEN
		LSET C2$ = STR$(MSGN - 1):
		PUT #1,1
4160	CLOSE
4180	PURGED = -1:
	GOSUB 4580:
	RETURN
4190 '
4200 ' BUILD SUMMARY FILE FROM MESSAGE FILE
4210 '
4220	PRINT "Building summary file..."
4240	OPEN "O",1,"SUMMARY.BAK":
	CLOSE:
	KILL "SUMMARY.BAK"
4260	OPEN "R",1,"MESSAGES",65:
	FIELD #1,65 AS R1$:
	R1 = 1
4280	OPEN "R",2,"SUMMARY.$$$",30:
	FIELD #2,30 AS R2$:
	R2 = 1
4300	PRINT SEP$
4320	FOR I = 1 TO 6
4340		GET #1,R1:
		IF EOF(1) THEN
			4440
4360		LSET R2$ = LEFT$(R1$,28) + CRLF$:
		PUT #2,R2
4380		R1 = R1 + 1:
		R2 = R2 + 1:
		PRINT LEFT$(R2$,28):
		IF EOF(1) THEN
			4440
4400		IF I = 1 THEN
			IF VAL(R1$) > 9998 THEN
				4440
4420	NEXT I:
	R1 = R1 + VAL(R1$):
	GOTO 4300
4440	CLOSE:
	NAME "SUMMARY" AS "SUMMARY.BAK":
	NAME "SUMMARY.$$$" AS "SUMMARY"
4460	PRINT "Summary file built.":
	RETURN
4470 '
4475 ' Error handlers
4478 '
4480	PRINT "Error number: ";ERR;" occurred at line number:";ERL
4500	IF ERL = 1740 AND ERR = 53 THEN
		PRINT "File not found.":
		RETURN
4520	IF ERL = 1580 AND ERR = 53 THEN
		PRINT "File not found.":
		CLOSE:
		RESUME 1680
4540	PRINT "Error number ";ERR;" in line number ";ERL
4560	RESUME 1240
4570 '
4580 ' build message index
4590 '
4600	MX = 0:
	MZ = 0
4620	OPEN "R",1,"SUMMARY",30:
	RE = 1:
	FIELD#1,28 AS RR$
4640	GET#1,RE:
	IF EOF(1) THEN
		4720
4660	G = VAL(RR$):
	MZ = MZ + 1:
	M(MZ,1) = G:
	IF G = 0 THEN
		4700
4680	IF G > 9998 THEN
		MZ = MZ - 1:
		GOTO 4720
4700	GET#1,RE + 5:
	M(MZ,2) = VAL(RR$):
	MX = MX + M(MZ,2) + 6:
	RE = RE + 6:
	GOTO 4640
4720	CLOSE:
	RETURN
4730 '
4740 ' unpack record
4750 '
4760	ZZ = LEN(R1$) - 2
4780	WHILE MID$(R1$,ZZ,1) = " "
4800	ZZ = ZZ - 1:
	IF ZZ = 1 THEN
		4840
4820	WEND
4840	KL$ = LEFT$(R1$,ZZ)
4860	RETURN
5000 '
5020 ' Test to only allow the SYSOP to use UTIL remotely
5040 '
5060	OPEN "I",1,"A:LASTCALR":
	INPUT #1,N$,O$,F$,DT$:
	CLOSE
5120	OPEN "I",1,"A:PWDS":
	INPUT #1,P1$,P2$:
	CLOSE #1
5180	PRINT
5200	IF N$ = MAGIC$ AND O$ = "" THEN
		PRINT "What is the second codeword ? ";:
		B$ = INPUT$(8):
		PRINT:
		GOSUB 2720:
		IF INSTR(B$,P2$) THEN
			RETURN
5220	PRINT
5360	OPEN "R",1,"A:CALLERS",60:
	FIELD #1, 60 AS RR$:
	GET #1,1
5380	RE = VAL(RR$) + 1:
	RL = 60
5400	GET #1,RE:
	INPUT# 1,S$
5410	IF INSTR(S$,"UTIL") THEN
		GOTO 6000
5420	S$ = S$ + " UTIL":
	GOSUB 2740:
	PUT #1,RE:
	CLOSE #1
5440	PRINT "You know you're not the SYSOP, what are you doing here??"
5460	PRINT
5480	PRINT "Go away, your name has been logged for further action!"
5500	PRINT
5520	END
5540 '
6000	F$ = "TW"		'User has achieved temporary twit status
6020	OPEN "O",2,"A:LASTCALR. " + CHR$(&HA0):
	PRINT#2,N$;",";O$;",";F$;",";DZ$:
	CLOSE
6030	PRINT "You were warned to stay out of the SYSOP's domain"
6040	PRINT
6050	PRINT "You are being logged off this system IMMEDIATELY"
6060	PRINT
6070	CHAIN "BYE"
6080	END
