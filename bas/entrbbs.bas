5 '    ------------->> ENTERBBS V3.2 17/Jul/83 <<-------------
10 '
11 '  As run on Software Tools/RCPM, Australia (61-2)-997-1836)
12 '
13 '   : Entry/name-logging module of RBBS version 2.2,    :
14 '   : from Howard Moulton's original SJBBS (in Xitan    :
15 '   : Basic), converted to MBASIC and called RBBS or    :
16 '   : RIBBS by Bruce Ratoff, and extensively revised/   :
17 '   : expanded by Ron Fowler to become RBBS22.          :
18 '   :---------------------------------------------------:
19 '   : The Fowler version, RBBS22, was split into 2 mod- :
20 '   : ules, ENTERBBS and MINIRBBS, by Ben Bronson.      :
21 '   :---------------------------------------------------:
22 '   : Both were revised and given RBBS-compatible ver-  :
23 '   : sion nos. in 03/81 by Tim Nicholas, to incorporate:
24 '   : updates from his version 2.4 of RBBS.             :
25 '  ------------------------------------------------------
26 '	 Added test for "*" in CALLERS file (from RBBS) and
27 '	 if CALLERS file finds "*" in beginning of caller's
28 '	 name, it will not allow him system access, and log
29 '	 him off immediately. (For those who persist in log-
30 '	 ging in with fictitious names, e.g. BUG BYTE). Also
31 '	 added "PWDS" file (from RBBS) for "P2$" only. So
32 '	 Sysop can get msgs for "SYSOP" or his name.
33 '	 by Tim Nicholas  05/Mar/81
34 '	------------------------------------------------------
35 '	 Changed sequence of response to question "Did I mis-
36 '	 anything?", so that a response other than "Y" or "y"
37 '	 or "N"/"n" will re-ask the question. So in noisy line
38 '	 conditions it won't automaticaly default to "N"/"n".
39 '	 Added suggestion by Ben Bronson to move printing of
40 '	 "BULLETIN" file to after name-taking, and other sign
41 '	 in procedures.  by Tim Nicholas 12/Mar/81.
42 '	------------------------------------------------------ 
43 '  More modifications by BB (14/Mar/81): checking-for-msgs
44 '  code transferred from MINIRBBS, lines 810-965.  No new
45 '  version number.  AND sysop now drops direct to disk
46 '  without incrementing COUNTERS.
47 ' -------------------------------------------------------- 
48 '  Modifications by Bill Bolton (up to 01/Jun/82). Godbout
49 '  System Support 1 clock routines, DATA file read moved to
50 '  before menus and BULLETIN choice so it can be used to show
51 '  date of latest update to BULLETIN, code "structured" for
52 '  easier reading/maintenance (but now MUST use MBASIC editor).
53 '  MAGIC$ added for SYSOP password . Password no longer echoed for
54 '  more secure remote use. SUMMARY check for new callers
55 '  too. Numerous other small changes. Version to 2.7A (for Australia)
56 ' --------------------------------------------------------
57 '  Twit log out changed. Twits are written out to LASTCALR with
58 '  TW tag. Then logged out through EXITRBBS for consistancy. Note
59 '  that EXITRBBS and RBBSUTIL have been simultaneously updated to
60 '  make use of this TW status in LASTCALR. ST$ reset if something was
61 '  misspelled in name log to stop redundant info getting into CALLERS
62 '  If comma entered between town and state it is changed to a period
63 '  to make life easier for EXITRBBS. RESET statement added at
64 '  start to allow for changes to disk between calls without having
65 '  to cold boot. Version to 2.7D, Bill Bolton
66 '----------------------------------------------------------------------
67 '  10/Apr/81 additions: another PWD step for SYSOP to go
68 '	 thru, to discourage villians...
69 '  11/Apr/81: Change "SYSOP" to another word, to ditto..
70 '    (see lines 600-610)
71 '  02/May/81: add Y/N for skipping BULLETIN
72 '  09/May/81: add routine for reading special user messages (=SPECIAL) 
73 '  20/Jun/81: add putting P$ (SP or RG) into LASTCALR so user 
74 '    privilege status can be passed to MINIRBBS
75 '  08/Aug/81: change special user introduction
76 '  18/Aug/81: insert Bill Earnest's routines for counting
77 '    callers & putting times in USERS, CALLERS, & LASTCALR
78 '  01/Sep/81: add Brian Kantor's CHAIN MINIRBBS & system user quiz
79 '  07/Sep/81: drop re-caller straight to CP/M
80 '  09/Sep/81: CALL TIMEX added (Dummy routine compiled with M80 and
81 '    linked to the BASCOMed pgm with L80, calling an ASM
82 '    pgm above CP/M for reading the MH clock; other clocks
83 '  	can probably be handled with direct port reads)
84 '  19/Sep/81: Give special (SP) users a command menu 
85 '  10/Sep/81: Improve twit sign-out; POKE reset bits for PMMI
86 '  27/Sep/81: Add Hank Szyszka's time interval stuff.
87 '  9/Oct/81: Add 3rd user category, NW, without direct MINIRBBS access
88 '  10/Oct/81: And add cp/m knowledge test at 390 & 32000
89 '  24/Oct/81: Limited command menu for RG users too.
90 '  01/Jun/82: Numerous Aussie changes, see above. Bill Bolton
91 '  15/Jun/82: Twit logout changed, see above. Bill Bolton
92 '  26/Mar/83: More demanding user name check added. 24 hour elapsed
93 '  time bug fixed. Version 2.8 Bill Bolton
94 '  04/Apr/83: Added SYSOP access logging into DIRECT file, closing
95 '  of LASTCALR wasn't handled properly for SYSOP. Ver 2.8A. Bill Bolton
96 '  06/Apr/83: Added MAXTRY tests so that turkeys can't monopolise the
97 '  by writing programs that just send occasional carriage return as
98 '  endless answers to prompts (BYE 7.2K also fixed). Ver 2.9 Bill Bolton
99 '---------------------------------------------------------------------
100 ' 19/Jun/83: Added Code at 20000 to write current caller to status
101 ' line of terminal directly (bypassing BYE) so SYSOP can know who
102 ' is on the system and how long they have been there when not running
103 ' a hardcopy log. Very useful for deciding if you want to CHAT or
104 ' not. Put a RETURN at 20000 if you dont need this. Ver 3.0 Bill Bolton 
105 '---------------------------------------------------------------------
106 ' 02/Jul/83: Moved SYSOP password check to subroutine at 21000 and
107 ' added code to incorporate day of the month as part of the password
108 ' to be entered. Use line 20145 instead of 21040 if you dont have a
109 ' real time clock in your system.  Ver 3.1 Bill Bolton 
110 '---------------------------------------------------------------------
111 ' 17/Jul/83: Added code to New User Survey routine to count the number
112 ' of questions skipped. If more than 2 are <ommitted> the caller is
113 ' given a message about being co-operative and given temporary TW
114 ' (twit) status which gets them kicked off the system immediately.
115 ' The caller will have already been logged into USERS but the
116 ' USERS record counter is decremented and written back to USERS.
117 ' Decrementing the USERS record counter means that the last record in
118 ' the USERS file is effectively ignored by the whole ENTRBBS program.
119 ' The record for the next new caller will be written over the data in
120 ' the last record under these circumstances, effectively erasing the
121 ' entry for the unwelcome caller. The message displayed to the
122 ' unwelcome caller is contained in the GOODBYE file for easy customis-
123 ' ation. The New User Survey is now done straight after the display
124 ' of NEWCON (line 690) so that the status of the new caller can be
125 ' changed to TW if necessary before logging to CALLERS and LASTCALR
126 ' and can be processed (i.e. chucked off the system) by the TW trapping
127 ' routines. Vers 3.2 Bill Bolton
199 '---------------------------------------------------------------------
200 ' NOTE that user privilege status is read from the USERS file, where
201 ' the following characters are inserted (with an editor) in the first
202 ' space of the line:  * = 'Twit',  + = 'Special User',  - = 'Regular
203 ' User', and (space) = 'New User'
204 ' NOTE ALSO that the code for other clocks made to run with this program
205 ' will be welcomed.  Use similar line #s if you can but separate the
206 ' relevant lines and call the result RBBTIME1.BAS, RBBTIME2.BAS, etc.
207 '----------------------------------------------------------------------
208 ' Howard Booker's suggested additions at 13030 were removed as they
209 ' didn't work and even when corrected were no better than the INKEY$
210 ' when running under BYE. Bill Bolton
211 '----------------------------------------------------------------------
300 '
310	POKE 0,&HCD '<-- Change "JMP" to "CALL" to prevent Ctl-C
315	VERS$ = "3.2"  '<---- Current version number
320	DEFINT A-Z
325	MODEMPORT=&H5C:
	CONSOLEPORT=&H0:
	MAXTRY = 4
330	DIM A$(17),M(200,2),H(6),HT(6),HD(6),TOD(5),DOY(5)
335	RESET		'<----- In case disk was changed between calls
340	INC=1
350	ON ERROR GOTO 15000
355	XX=0:
	YY=0
358	MAGIC$="SUPER"	'The magic sysop pasword
360	'TIMEX=&HE800  -disabled Call to MHTIME.COM; unnecessary for most non-MH
365	'CALL TIMEX     clocks, but you'll have have to modify 14000- & 44000-.
370	 '	
372	GOSUB 14000:
	GOSUB 14200   'Set time counters (HK routine)
374	HT(1)=H(1):
	HT(2)=H(2):
	HT(3)=H(3):
	HT(4)=H(4):
	HT(5)=H(5):
	HT(6)=H(6)
376	M=74:
	FOR I=1 TO 6:
		POKE M,HT(I):
		M=M+1:
	NEXT I   'Save the time in lo memory
379	'
380	'  Signon Functions...
381	'
385	PRINT:
	PRINT "Version ";VERS$
390	GOSUB 32000    'CP/M familiarity test
400	MSGS=1:
	CALLS=MSGS+1:
	MNUM=CALLS+1
425	BK=0
430	OPEN "I",1,"A:P"+CHR$(&HD7)+"DS. "+CHR$(&HA0):
	IF EOF(1) THEN
		450  '<-- Password file
440	INPUT #1,P1$,P2$   'use editor to make the file. e.g.: BANANA,APPLE,COW
450	CLOSE #1
460	BEL=-1:
	XPR=0      ' (initial bell on, not expert)
470	GOSUB 13020
480	SAV$=""
510	OPEN "I",1,"A:LASTCALR":
	INPUT #1,Y$,Z$,F$:
	CLOSE
530	GOSUB 4050:
	GOSUB 13020   ' Print WELCOME File
540	BK = 0:
	A$ = "(Prompting bell means system is ready for input).":
	GOSUB 13020:
	GOSUB 13020:
	XX = 0:
	COUNT1 = 0:
	COUNT2 = 0
545	N$ = "":
	O$ = "":
	ST$ = "":
	COUNT2 = COUNT2 + 1:
	IF COUNT2 = MAXTRY THEN
		GOTO 18080
550	COUNT1 = COUNT1 + 1:
	IF COUNT1 = MAXTRY THEN
		GOTO 18080
560	A$ = "What is your FIRST name ?":
	GOSUB 13020:
	C = 1:
	GOSUB 13260:
	C = 0:
	N$ = B$:
	IF N$ = "" THEN
		GOTO 550
570	IF N$<"A" OR LEN(N$)=1 THEN 
		550
575	COUNT1 = 0
580	COUNT1 = COUNT1 + 1:
	IF COUNT1 = MAXTRY THEN
		GOTO 18080
585	A$ = "What is your LAST name ?":
	GOSUB 13020:
	C = 1:
	GOSUB 13260:
	C = 0:
	O$ = B$:
	IF O$ = "" THEN
		GOTO 580
590	IF O$<"A" OR LEN(O$)=1 THEN 
		580
591 '
595 '
598	IF N$<>MAGIC$ THEN 
		610  
600	IF N$=MAGIC$ AND O$<>P1$ THEN 
		GOTO 545
605	IF N$=MAGIC$ AND O$=P1$ THEN 
		GOSUB 21000:
		IF SYSOP = 1 THEN
			GOTO 730
		ELSE
			GOTO 545
610	IF INSTR(N$,"SYSOP") THEN 
		PRINT:
		PRINT "You know you're not the SYSOP!!!":
		PRINT:
		GOTO 545
612 '
620	A$="Checking user file...":
	GOSUB 13020:
	V=0:
	OPEN "R",1,"A:U"+CHR$(&HD3)+"ERS. "+CHR$(&HA0),62:
	FIELD#1,50 AS RZ$,4 AS NC$,6 AS DT$:
	GET#1,1:
	NU=VAL(RZ$)
625	FIELD #1,62 AS RR$
628	NT$ = N$ + " " + O$
630	FOR I=2 TO NU+1:
		GET#1,I:
		J = INSTR(RZ$,NT$):
		IF J  > 0 THEN 
			LENGTH = LEN(NT$):
			IF MID$(RZ$,J+LENGTH,1) = " " THEN
				MF$=LEFT$(RZ$,1):
				GOSUB 15990:
				PUT#1,I:
				CLOSE:
				GOSUB 13020:
				XX=1:
				GOTO 700
640	NEXT I   ' If recognized, caller is passed to CALLER-logging routine
649	' But a caller not in the USER file gets quizzed further...
650	V=1:
	A1$="Where (Suburb/Town AND State) are you calling from ?":
	GOSUB 13020:
	C=1:
	GOSUB 13260:
	C=0:
	ST$=B$:
	IF ST$="" THEN 
		545
655	POINTER = INSTR(ST$,","):
	IF POINTER THEN
		MID$(ST$,POINTER,1) = "."
660	A$="Hello "+N$+" "+O$+" from "+ST$:
	GOSUB 13020
662	A1$="Is any of this misspelled ?":
	GOSUB 13020:
	C=1:
	GOSUB 13260:
	C=0
665	IF LEFT$(B$,1) = "Y" THEN 
		GOTO 545
667	IF LEFT$(B$,1) <> "N" THEN 
		545
670	PRINT:
	A1$="This checking is only done the first time you call.":
	GOSUB 13020
680	LSET NC$ = MKI$(0):
	LSET RZ$="  "+N$+" "+O$+" "+ST$+SPACE$(44):
	GOSUB 15990:
	NU=NU+1:
	PUT#1,NU+1:
	S$=STR$(NU):
	GOSUB 16000:
	PUT#1,1:
	CLOSE
690	MF$ = " ":
	FIL$ = "NEWCOM":
	GOSUB 18000:
	PRINT:
	GOSUB 35000  '...and made to read the NEWCOMer file
695	PRINT
700	GOSUB 14200    '  Now everybody gets logged to CALLERS
705	A$="Logging "+N$+" "+O$+" to disk...":
	N=1:
	GOSUB 13020:
	OPEN "R",1,"A:C"+CHR$(&HC1)+"LLERS. "+CHR$(&HA0),60:
	FIELD#1,60 AS RR$:
	GET#1,1
710	RE=VAL(RR$)+1:
	S$=STR$(RE):
	RL=60:
	GOSUB 16000:
	PUT#1,1:
	RE=RE+1
715	S$=N$+" "+O$+" "+ST$+" "+TI$:
	GOSUB 16000:
	PUT#1,RE:
	CLOSE#1
720	'  Recallers (who are not "twits") go straight to CP/M
723	IF N$=Y$ AND O$=Z$ AND MF$ <> "*" AND XX<>0 THEN 
		GOSUB 13020:
		A$="Welcome back.  Since you just signed off, go straight to CP/M":
		GOSUB 13020:
		F$ = F$ + " Rentered":
		GOSUB 20000:
		GOTO 2240
724	'
725	'  User privilege level (from USERS) & date (DT$) is added to LASTCALR...
726	IF MF$="*" THEN
		F$="TW"
727	IF MF$="+" THEN 
		F$="SP"
728	IF MF$=" " THEN 
		F$="NW"
729	IF MF$="-" THEN 
		F$="RG"
730	OPEN "O",1,"A:L"+CHR$(&HC1)+"STCALR. "+CHR$(&HA0):
	PRINT #1,N$;",";O$;",";F$;",";DZ$:
	CLOSE#1:
	GOSUB 20000:
	IF N$=MAGIC$ THEN 
		GOSUB 19000:
		GOTO 2240
736	' Now log out the twits through exit routines
737	IF MF$="*" THEN
		PRINT:
		PRINT:
		PRINT "You have lost access privileges to this system":
		PRINT:
		CHAIN "BYE"
740	BK=0:
	GOSUB 13020:
	OPEN "R",1,"A:C"+CHR$(&HCF)+"UNTERS. "+CHR$(&HA0),5:
	FIELD#1,5 AS RR$
750	PRINT
760	A$="You are caller # : ":
	N=1:
	GOSUB 13020:
	GET#1,CALLS
770	CN=VAL(RR$)+INC:
	A$=STR$(CN):
	LSET RR$=A$:
	GOSUB 13020:
	PUT#1,CALLS
790	CLOSE:
	GOSUB 13020
792	'And now the user gets to choose whether to answer the survey at 35000,
793	IF XX=0 THEN 
		GOTO 800   'except that new users have no choice
795	A1$="Have you answered the user survey questions yet?":
	GOSUB 13020:
	C=1:
	GOSUB 13260:
	C=0
798	IF LEFT$(B$,1)="N" THEN 
		GOSUB 35000
799	'
800	' The SUMMARY file is now checked for messages to the caller
830	'
835	GOSUB 13020:
	A1$="Wait while I check to see if you have messages waiting ...":
	GOSUB 13020:
	GOSUB 13020
838	L=0
840	FT=1:
	MX=0:
	MZ=0:
	IU=0:	 ' (Flag first time for printing heading)
850	OPEN "R",1,"A:S"+CHR$(&HD5)+"MMARY. "+CHR$(&HA0),30:
	RE=1:
	FIELD#1,28 AS RR$
860	BK=0:
	GET#1,RE:
	IF EOF(1) THEN 
		960
870	G=VAL(RR$):
	MZ=MZ+1:
	M(MZ,1)=G:
	IF G=0 THEN 
		950
880	IF IU=0 THEN 
		IU=G
890	IF G>9998 THEN 
		MZ=MZ-1:
		GOTO 960
900	GET#1,RE+3:
	GOSUB 16500:
	IF INSTR(S$,N$)>0 AND INSTR(S$,O$)>0 THEN 
		930
910	IF N$<>MAGIC$ THEN 
		950  
920	IF INSTR(S$,"BILL")=0 THEN 
		950
930	IF FT THEN 
		L=L+1
931	IF FT THEN 
		A$="The following messages for "+N$+" "+O$+" are waiting in MINIRBBS: ":
		GOSUB 13020:
		FT=0
940	A$=STR$(G):
	N=1:
	GOSUB 13020:
	GOSUB 13020
950	GET#1,RE+5:
	M(MZ,2)=VAL(RR$):
	MX=MX+M(MZ,2)+6:
	RE=RE+6:
	GOTO 860
960	IF L=0 THEN 
		PRINT "No, there aren't any messages for you, "+N$+".":
		PRINT "But check MINIRBBS anyway for public messages.":
		GOSUB 13020
965	CLOSE
2000 '
2020 '  Everyone comes here, to get ready to go to CP/M
2040 '
2045	GOSUB 4070	'Everyone sees the DATA file before menus
2046 '
2049 '  They get menus according to their status....
2050 '
2051	IF MF$<>"+" THEN 
		2100
2052	GOSUB 13020:
	A$="As a special user, you have the following options:":
	GOSUB 13020:
	GOSUB 13020
2053	A$=" CON  Read CONFIDENTIAL msgs    MIN  Go to MINIRBBS":
	GOSUB 13020
2054	A$=" NEW  Latest system data        CPM  Go straight to CP/M":
	GOSUB 13020
2055	A$=" OFF  Log Off immediately":
	GOSUB 13020:
	COUNT1 = 0
2056	GOSUB 13020:
	A1$="Which ?":
	GOSUB 13020:
	C=1:
	GOSUB 13260:
	C=0
2060	IF B$="CON" THEN 
		4100   'the SPECIAL file
2065	IF B$="MIN" THEN 
		CHAIN "MINIRBBS"  'to the message module
2070	IF B$="NEW" THEN 
		2220   'the BULLETIN file
2075	IF B$="CPM" THEN 
		2230   'the DATA file, then CP/M
2076	IF B$="OFF" THEN 
		CHAIN "BYE"  'straight to log-off module
2078	COUNT1 = COUNT1 + 1:
	IF COUNT1 = MAXTRY THEN
		GOTO 18080
2080	GOTO 2056
2099	'
2100	IF MF$=" " THEN 
		2200    ' Note that new callers don't get a menu
2110	GOSUB 13020:
	A$="Now you can do one of the following:":
	GOSUB 13020:
	GOSUB 13020
2120	A$=" NEW  Latest system data         CPM  Go straight to CP/M":
	GOSUB 13020
2125	A$=" MIN  Go to message subsystem    OFF  Log Off immediately":
	GOSUB 13020
2127	COUNT1 = 0
2130	GOSUB 13020:
	A1$="Which do you want ?":
	GOSUB 13020:
	C=1:
	GOSUB 13260:
	C=0
2135	IF B$="MIN" THEN 
		CHAIN "MINIRBBS"
2140	IF B$="NEW" THEN 
		2220    ' RG callers can do everything SP callers can
2145	IF B$="CPM" THEN 
		2230    ' except read the SPECIAL file
2150	IF B$="OFF" THEN 
		CHAIN "BYE"
2155	COUNT1 = COUNT1 + 1:
	IF COUNT1 = MAXTRY THEN
		GOTO 18080
2160	GOTO 2130
2170 '
2197 ' To discourage new callers from thinking this is a bulletin board system,
2198 ' this is the only choice they get
2199 '
2200	COUNT1 = 0
2202	COUNT1 = COUNT1 + 1:
	IF COUNT1 = MAXTRY THEN
		GOTO 18080
2205	A1$ = "Want latest system information before entering CP/M ?":
	GOSUB 13020:
	C = 1:
	GOSUB 13260:
	C = 0
2210	IF LEFT$(B$,1) = "N" THEN 
		2230
2215	IF LEFT$(B$,1) <> "Y" THEN 
		2202
2220	GOSUB 3040 ' Print BULLETIN file
2225	IF MF$="+" THEN 
		2052
2226	IF MF$="-" THEN 
		2110
2230 '			Used to be DATA file read, moved to 2045
2235	CLOSE ' (just in case any files are still open)
2236	PRINT
2237	GOTO 44620  ' Then to the time-on-system routine, and then...
2240	GOSUB 13020:
	POKE 4,0:
	A$="Entering CP/M...":
	GOSUB 13020
2260	POKE 0,&HC3:
	SYSTEM ' we restore the "JMP" and go to CP/M.
3000 '
3010 ' The main program has now ended.  It's just subroutines from here on
3015 '
3020 ' The display BULLETIN file subroutine
3040 '
3050	PRINT:
	GOSUB 13000
3060	GOSUB 12220
3080	FIL$="BULLETIN":
	GOSUB 18000:
	PRINT:
	RETURN
4000 '
4020 ' The display WELCOME file subroutine
4030 '
4050	GOSUB 12220
4060	FIL$="WELCOME":
	GOSUB 18000:
	RETURN
4065 '
4070 ' The display DATA file subroutine*
4075 '
4080	GOSUB 12220
4090	FIL$="DATA":
	GOSUB 18000:
	RETURN
4095 '
4100 ' The display SPECIAL file subroutine*
4120 '
4140	GOSUB 12220
4160	FIL$="SPECIAL":
	GOSUB 18000:
	GOTO 2052
5000 '
12220	RETURN
12999 '
13000	A$="Use ctl-K to abort, ctl-S to pause."
13020 '
13040 ' Routine to print string from A$ on console
13060 '
13080	IF SAV$<>"" AND A1$<>"" THEN 
		A1$="":
		RETURN
13100	IF A1$<>"" THEN 
		A$=A1$:
		A1$=""
13120	IF RIGHT$(A$,1)="?" OR N=1 THEN 
		PRINT A$;:
		PP$=A$:
		GOTO 13180
13140	BI=ASC(INKEY$+" "):
	IF BI=19 THEN 
		BI=ASC(INPUT$(1))
13160	IF BI=11 THEN 
		BK=-1:
		GOTO 13220 
	ELSE 
		PRINT A$
13180	A=A+LEN(A$)
13220	A$="":
	N=0
13240	RETURN
13260 '
13280 ' Routine to accept string into B$ from console
13300 '
13320	IF BEL AND SAV$="" THEN 
		PRINT CHR$(7);
13340	B$="":
	BK=0
13360	IF SAV$="" THEN 
		LINE INPUT SAV$
13380	SP=INSTR(SAV$,";"):
	IF SP=0 THEN 
		B$=SAV$:
		SAV$="":
		GOTO 13420
13400	B$=LEFT$(SAV$,SP-1):
	SAV$=MID$(SAV$,SP+1)
13420	IF LEN(B$)=0 THEN 
		RETURN
13440	IF C=0 THEN 
		13480
13460	FOR ZZ=1 TO LEN(B$):
		MID$(B$,ZZ,1)=CHR$(ASC(MID$(B$,ZZ,1))+32*(ASC(MID$(B$,ZZ,1))>96)):
	NEXT ZZ
13480	IF LEN(B$)<63 THEN 
		13580
13500	A$="Input line too long - would be truncated to:":
	GOSUB 13020
13520	B$=LEFT$(B$,62):
	PRINT B$
13540	LINE INPUT "Retype line (Y/N)?";QQ$:
	GOSUB 35600:
	QQ$=LEFT$(QQ$,1)
13560	IF QQ$="Y" OR QQ$="y" THEN 
		PRINT PP$;:
		SAV$="":
		GOTO 13260
13580	D=D+LEN(B$):
	RETURN
13600	RETURN
13620 '
14000 ' Date getting subroutine
14010	BASEPORT = &H50
14013	CMDPORT = BASEPORT + 10
14016	DATAPORT = CMDPORT + 1
14019 '**********************************************************
14022 '*		READ THE DATE DIGITS			*
14025 '**********************************************************
14028	FOR DIGIT = 12 TO 7 STEP -1
14031		OUT CMDPORT,(&H10 + DIGIT)
14034		DOY(DIGIT - 7) = INP(DATAPORT)
14037	NEXT DIGIT
14040	YEAR= (DOY(5) * 10) + DOY(4)
14043	MONTH10 = DOY(3)
14046	MONTH1  = DOY(2)
14049	DAY10 = DOY(1)
14052	DAY1  = DOY(0)
14055 '**********************************************************
14058 '*		FORMAT THE FIRST DATE STRING		*
14061 '**********************************************************
14064	DATE1$="        "
14067	MID$(DATE1$,1,1) = RIGHT$(STR$(DAY10),1)
14070	MID$(DATE1$,2,1) = RIGHT$(STR$(DAY1),1)
14073	MID$(DATE1$,3,1) = "/"
14076	MID$(DATE1$,4,1) = RIGHT$(STR$(MONTH10),1)
14079	MID$(DATE1$,5,1) = RIGHT$(STR$(MONTH1),1)
14082	MID$(DATE1$,6,1) = "/"
14085	MID$(DATE1$,7,2) = RIGHT$(STR$(YEAR),2)
14088	DZ$ = DATE1$
14091	DT$ = LEFT$(DATE1$,5)
14093	DD$ = MID$(DATE1$,1,2)
14095	DM$ = MID$(DATE1$,4,2)
14100	RETURN
14190 '
14200 ' Time-finding subroutine
14205	FOR DIGIT = 5 TO 0 STEP -1
14210		OUT CMDPORT,(&H10 + DIGIT)
14215		TOD(DIGIT) = INP(DATAPORT)
14220		IF DIGIT = 5 THEN TOD(DIGIT) = TOD(DIGIT) AND 3
14225	NEXT DIGIT
14230	H(1) = TOD(5)
14235	H(2) = TOD(4)
14240	H(3) = TOD(3)
14245	H(4) = TOD(2)
14250	H(5) = TOD(1)
14255	H(6) = TOD(0)
14260	DH$ = "  ":
	DI$ = "  ":
	DS$ = "  "
14265	MID$(DH$,1,1) = RIGHT$(STR$(H(1)),1):
	MID$(DH$,2,1) = RIGHT$(STR$(H(2)),1):
	MID$(DI$,1,1) = RIGHT$(STR$(H(3)),1):
	MID$(DI$,2,1) = RIGHT$(STR$(H(4)),1):
	MID$(DS$,1,1) = RIGHT$(STR$(H(5)),1):
	MID$(DS$,2,1) = RIGHT$(STR$(H(6)),1)
14280	TI$=DD$+"-"+DH$+":"+DI$
14285	TD$=DH$+":"+DI$+":"+DS$
14290	RETURN
14999 '
15000 ' The ON-ERROR handler...
15001 '
15020	IF ERL=18030 THEN 
		RESUME 18050
15030	IF ERL=700 THEN 
		RE=0:
		RESUME 710
15100	RESUME NEXT
15887 '
15888 ' Small routine for writing date, etc., to USERS file (see lines 630 & 680))
15889 '
15990	S$=LEFT$(RZ$,50)+RIGHT$("   "+STR$(VAL(NC$)+1),4)+" "+RIGHT$("0"+DD$,2)
15992	S$=S$+"/"+RIGHT$("0"+DM$,2):RL=62   ' (now fall thru...).
16000 '
16010 ' Fill and store disk record...
16020 '
16030	LSET RR$=LEFT$(S$+SPACE$(RL-2),RL-2)+CHR$(13)+CHR$(10)
16040	RETURN
16500 '
16510 ' Unpack disk record...
16520 '
16530	ZZ=LEN(RR$)-2
16540	WHILE MID$(RR$,ZZ,1)=" "
16550		ZZ=ZZ-1:
		IF ZZ=1 THEN 
			16570
16560	WEND
16570	S$=LEFT$(RR$,ZZ)
16580	IF MID$(S$,ZZ,1)="?" THEN S$=S$+" "
16590	RETURN
17000 '
17010 ' Toggle expert user mode
17020 '
17030 ' XPR=NOT XPR:RETURN  (inactivated here but kept for future use)
17040 '
17050 ' Toggle bell prompt
17060 '
17070 ' BEL=NOT BEL:RETURN  (ditto)
18000 '
18010 ' Subroutine to print a file
18020 '
18030	OPEN "I",1,"A:"+FIL$:
	BK=0
18040	IF EOF(1) OR BK THEN 
		18050 
	ELSE 
		LINE INPUT #1,A$:
		GOSUB 13020:
		GOTO 18040
18050	CLOSE #1:
	RETURN
18060 '
18070 '
18080 ' Subroutine to log off an unwanted caller
18090 '
18100 '
18110	'POKE 0,&HC3	'<-----Restore "Jump" at BASE for CP/M (doesn't
			 really matter if this isn't done if you use BYE
			 to load this program
18120	RUN "A:SUPER.COM" 'Neatest log off is through BYE
18140	END
18150 '
19000	GOSUB 14200	'Now log SYSOP acceses for later check
19020	OPEN "R",1,"A:D"+CHR$(&HC9)+"RECT. "+CHR$(&HA0),40:
	FIELD#1,40 AS RR$:
	GET#1,1
19040	RE = VAL(RR$)+1:
	S$ = STR$(RE):
	RL = 40:
	GOSUB 16000:
	PUT#1,1:
	RE = RE + 1
19060	IF N$ = MAGIC$ THEN
		N$ = "SYSOP"
19080	S$ = N$ + " " + TI$ + " " + MID$(X$,7,2):
	GOSUB 16000:
	PUT#1,RE:
	CLOSE #1
19100	RETURN
19110 '
20000 '
20020 ' Optional HARDWARE DEPENDENT routine to write caller
20040 ' data to status line of your terminal if it has one
20060 ' This routine must access the console directly (bypassing
20080 ' BYE) so is necessarily hardware dependent
20100 '
20120	STATUS$ = CHR$(27) + "g" + CHR$(27) + "f" + N$ + " " + O$ + " " + ST$ + ", " + TD$ + ", " + DZ$ + ", " + F$ + CHR$(13) + CHR$(10)
20140	FOR I = 1 TO LEN(STATUS$)
20160		CHAR = ASC(MID$(STATUS$,I,1))
20180		WHILE (INP(CONSOLEPORT+1) AND &H1) <> 1
20200		WEND
20220		OUT CONSOLEPORT,CHAR
20240	NEXT I
20260	RETURN
20280 '
21000 '  SYSOP password check
21010 '
21020	O$ = "":
	A1$ = "2nd Codeword?":
	GOSUB 13020:
	C = 1:
	B$ = INPUT$(10):
	GOSUB 13420:
	C = 0:
	X$ = B$:
21030	PRINT
21040	IF INSTR(X$,P2$) THEN
		IF (MID$(DT$,1,1) = MID$(X$,10,1)) AND (MID$(DT$,2,1) = MID$(X$,9,1)) THEN
			F$ = "":
			SYSOP = 1:
			RETURN
21045	'Use this in place of 21040 if you dont have a real time clock
	IF INSTR(X$,P$) THEN
		F$ = "":
		SYSOP = 1:
		RETURN
21050	SYSOP = 0:
	RETURN
21060 '
32000 '  The CP/M familiarity testing routine  (feel free to make changes)
32001 '
32010	XX=0
32020	GOSUB 13020:
	A1$="What is the name of Digital Research's standard debugger?":
	GOSUB 13020:
	C=1:
	GOSUB 13260:
	C=0
32040	IF INSTR(B$,"DDT") THEN 
		32400
32050	IF INSTR(B$,"ddt") THEN 
		32400
32055	IF INSTR(B$,"SID") THEN
		PRINT "Not ";B$;", try the other one...":
		GOTO 32020
32060	XX=XX+1:
 	IF XX=3 THEN 
		18080   ' Log the caller off...
32070	IF XX=1 THEN
		PRINT "You only get 3 tries...":
		GOTO 32020
32080	IF XX=2 THEN
		PRINT "One last try...":
		GOTO 32020
32400	RETURN
32499 '
35000 '   BK's system user survey module  (again, make changes)
35001 '
35002	PRINT:
	PRINT "     ***   SYSTEM USER SURVEY  ***"
35005	OPEN "R",1,"A:S"+CHR$(&HD5)+"RVEY.B"+CHR$(&HC2)+"S",40:
	FIELD#1,40 AS RR$:
	GET#1,1
35006	RE = VAL(RR$)+1
35007	IF RE = 1 THEN 
		RE = 2
35008	S$=N$+" "+O$+" "+DZ$
35009	GOSUB 35200
35010	GOSUB 13020:
	GOSUB 13020:
	A$="Please answer all the following questions. The data"
35020	GOSUB 13020:
	A$="about what you are doing helps to ensure that this":
	GOSUB 13020:
	A$="system takes your needs into account as it develops.":
	GOSUB 13020
35023	NOANSW = 0
35025	PRINT:
	PRINT "(Keep each answer to 35 characters maximum.)"
35026	PRINT "(There are 8 questions in all)":
	PRINT
35030	PRINT "What kind of computer (or terminal) are you using? (S-100, Osborne,"
35035	PRINT "  NEC-APC, IBM-PC etc.; if S-100, which controller & CPU card?":
	GOSUB 35600:
	Q$=" 1":
	GOSUB 35100
35040	PRINT "With which operating systems? (CP/M-80?  CP/M-86?  CP/M-68K?"
35045	PRINT "  MSDOS, P-system?  More than one?)":
	GOSUB 35600:
	Q$=" 2":
	GOSUB 35100
35050	PRINT "How about the modem?  What brand & baud rate(s)?":
	GOSUB 35600:
	Q$=" 3":
	GOSUB 35100
35060	PRINT "Where did you learn of this system":
	PRINT " (If an RCPM or BBS, which one)? ":
	GOSUB 35600:
	Q$=" 4":
	GOSUB 35100
35070	PRINT "Do you work with computers professionally?  Which kind?":
	GOSUB 35600:
	Q$=" 5":
	GOSUB 35100
35080	PRINT "How long have you been involved with microcomputers?":
	GOSUB 35600:
	Q$=" 6":
	GOSUB 35100
35085	PRINT "If you write your own programs, which languages do you usually use?":
	GOSUB 35600:
	Q$=" 7":
	GOSUB 35100
35090	PRINT "Are you interested in 16/32 bit CPUs or other"
35091	PRINT "  leading-edge equipment & software?  Which?":
	GOSUB 35600:
	Q$=" 8":
	GOSUB 35100
35092	PRINT:
	PRINT "If you'd care to give further details, leave a msg in MINIRBBS"
35094	S$=STR$(RE)
35095	GOSUB 16000:
	PUT#1,1:
	CLOSE
35096	IF NOANSW >= 3 THEN
		GOSUB 35700:
		RETURN		'Get rid of the nusiance callers
35099	PRINT:
	PRINT "Thanks for the information.  Now back to the log-in routine...":
	PRINT:
	RETURN
35100 ' PUT IN FILE
35120	GOSUB 13280:
	IF B$="" THEN 
		S$="<omitted>":
		NOANSW = NOANSW + 1
	ELSE 
		S$=B$
35140	S$=Q$+": "+S$
35200	RL=40
35220	GOSUB 16000
35240	PUT#1,RE
35260	RE = RE + 1
35280	RETURN
35290 '
35300 ' Display a ruler line to show how long answer may be
35310 '
35600	PRINT "---------10---------20--------30----|"
35620	RETURN
35630 '
35640 ' Throw away callers who wont answer questions
35650 '
35700	FIL$ = "GOODBYE":
	GOSUB 18000
35710	OPEN "R",1,"A:U"+CHR$(&HD3)+"ERS. "+CHR$(&HA0),62:
	FIELD#1,50 AS RZ$:
	GET#1,1:
	NU = VAL(RZ$):
	NU = NU - 1:
	S$ = STR$(NU):
	RL = 62:
	GOSUB 16000:
	PUT#1,1:
	CLOSE:
	MF$ = "*":
	RETURN
35720 '
44620 '  Routines for printing the time & time-on-system 
44625 '   (for MH clock, but adaptable for other clocks)
44630 '    a. Print just time
44640	GOSUB 14200  
44650	PRINT "The time now is (Hrs:Mins:Secs).... "TD$
44659 '    b. Print elapsed time too
44660	GOSUB 44940
44670	GOTO 2240
44830 '    (calculate the time difference...)
44835	IF H(1) < HT(1) THEN
		H(1) = H(1) + 2:
		H(2) = H(2) + 4
44840	IF H(6)<HT(6) THEN 
		H(6)=H(6)+10:
		H(5)=H(5)-1
44850	IF H(5)<HT(5) THEN 
		H(5)=H(5)+6:
		H(4)=H(4)-1
44860	IF H(4)<HT(4) THEN 
		H(4)=H(4)+10:
		H(3)=H(3)-1
44870	IF H(3)<HT(3) THEN 
		H(3)=H(3)+6:
		H(2)=H(2)-1
44880	IF H(2)<HT(2) THEN 
		H(2)=H(2)+10:
		H(1)=H(1)-1
44890	HD(6)=H(6)-HT(6):
	HD(5)=H(5)-HT(5):
	HD(4)=H(4)-HT(4)
44900	HD(3)=H(3)-HT(3):
	HD(2)=H(2)-HT(2):
	HD(1)=H(1)-HT(1)
44910	RETURN
44920	INPUT "TIME= H,H,M,M,S,S ";HT(1),HT(2),HT(3),HT(4),HT(5),HT(6)
44930	INPUT "LATER TIME H,H,M,M,S,S ";H(1),H(2),H(3),H(4),H(5),H(6)
44940	GOSUB 44830
44950	PRINT "You've been on the system for...... ";
44960	TF$="#"
44970	FOR I=1 TO 6
44980		PRINT USING TF$;HD(I);
44990		IF I=2 THEN 
			PRINT ":";
45000		IF I=4 THEN 
			PRINT ":";
45010	NEXT I
45020	PRINT
45030	RETURN
G TF$;