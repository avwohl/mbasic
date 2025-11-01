5 '  ------------->> ENTERBBS V2.7 10/31/81 <<-------------
9 '
10 '         (As run on HP/RCPM  312-955-4493,)
11 '        (slightly cleaned up by Ben Bronson)
12 '
15 '   : Entry/name-logging module of RBBS version 2.2,    :
20 '   : from Howard Moulton's original SJBBS (in Xitan    :
25 '   : Basic), converted to MBASIC and called RBBS or    :
30 '   : RIBBS by Bruce Ratoff, and extensively revised/   :
35 '   : expanded by Ron Fowler to become RBBS22.          :
40 '   :---------------------------------------------------:
45 '   : The Fowler version, RBBS22, was split into 2 mod- :
50 '   : ules, ENTERBBS and MINIRBBS, by Ben Bronson.      :
55 '   :---------------------------------------------------:
60 '   : Both were revised and given RBBS-compatible ver-  :
65 '   : sion nos. in 03/81 by Tim Nicholas, to incorporate:
70 '   : updates from his version 2.4 of RBBS.             :
75 '  ------------------------------------------------------
80 '	 Added test for "*" in CALLERS file (from RBBS) and
85 '	 if CALLERS file finds "*" in beginning of caller's
90 '	 name, it will not allow him system access, and log
95 '	 him off immediately. (For those who persist in log-
100 '	 ging in with fictitious names, e.g. BUG BYTE). Also
105 '	 added "PWDS" file (from RBBS) for "P2$" only. So
110 '	 Sysop can get msgs for "SYSOP" or his name.
115 '	 by Tim Nicholas  3/05/81
120 '	------------------------------------------------------
125 '	 Changed sequence of response to question "Did I mis-
130 '	 anything?", so that a response other than "Y" or "y"
135 '	 or "N"/"n" will re-ask the question. So in noisy line
140 '	 conditions it won't automaticaly default to "N"/"n".
145 '	 Added suggestion by Ben Bronson to move printing of
150 '	 "BULLETIN" file to after name-taking, and other sign
155 '	 in procedures.  by Tim Nicholas 3/12/81.
180 '	------------------------------------------------------ 
185 '  More modifications by BB (3/14/81): checking-for-msgs
190 '  code transferred from MINIRBBS, lines 810-965.  No new
195 '  version number.  AND sysop now drops direct to disk
200 '  without incrementing COUNTERS.
205 ' ------------------------------------------------------ 
210 '  4/10/81 additions: another PWD step for SYSOP to go
215 '	 thru, to discourage villians...
220 '  4/11/81: Change "SYSOP" to another word, to ditto..
225 '    (see lines 600-610)
230 '  5/02/81: add Y/N for skipping BULLETIN
240 '  5/09/81: add routine for reading special user messages (=SPECIAL) 
245 '  6/20/81: add putting P$ (SP or RG) into LASTCALR so user 
246 '    privilege status can be passed to MINIRBBS
250 '  8/08/81: change special user introduction
255 '  8/18/81: insert Bill Earnest's routines for counting
260 '    callers & putting times in USERS, CALLERS, & LASTCALR
265 '  9/01/81: add Brian Kantor's CHAIN MINIRBBS & system user quiz
270 '  9/07/81: drop re-caller straight to CP/M
275 '  9/09/81: CALL TIMEX added (Dummy routine compiled with M80 and
280 '     linked to the BASCOMed pgm with L80, calling an ASM
285 '  	  pgm above CP/M for reading the MH clock; other clocks
286 '  	  can probably be handled with direct port reads)
287 '  9/19/81: Give special (SP) users a command menu 
288 '  9/10/81: Improve twit sign-out; POKE reset bits for PMMI
289 '  9/27/81: Add Hank Szyszka's time interval stuff.
290 '  10/9/81: Add 3rd user category, NW, without direct MINIRBBS access
291 '  10/10/81: And add cp/m knowledge test at 390 & 32000
292 '  10/24/81: Limited command menu for RG users too.
293 '---------------------------------------------------------------------
294 ' NOTE that user privilege status is read from the USERS file, where
295 ' the following characters are inserted (with an editor) in the first
296 ' space of the line:  * = 'Twit',  + = 'Special User',  - = 'Regular
297 ' User', and (space) = 'New User'
298 ' NOTE ALSO that the code for other clocks made to run with this program
299 ' will be welcomed.  Use similar line #s if you can but separate the
300 ' relevant lines and call the result RBBTIME1.BAS, RBBTIME2.BAS, etc.
301 '----------------------------------------------------------------------
302 ' Howard Booker's suggested additions at 13030 are included but in a
303 ' disabled state.  The pgm will run without them.  But if you set
304 ' the equates and remove the ', it'll run better...
305 '----------------------------------------------------------------------
310 POKE 0,&HCD '<-- Change "JMP" to "CALL" to prevent Ctl-C
320 DEFINT A-Z
330 DIM A$(17),M(200,2),H(6),HT(6),HD(6)
340 INC=1
350 ON ERROR GOTO 15000
355 XX=0:YY=0
360 'TIMEX=&HE800  -disabled Call to MHTIME.COM; unnecessary for most non-MH
365 'CALL TIMEX     clocks, but you'll have have to modify 14000- & 44000-.
370 '	
372 GOSUB 14000:GOSUB 14200   'Set time counters (HK routine)
374 HT(1)=H(1):HT(2)=H(2):HT(3)=H(3):HT(4)=H(4):HT(5)=H(5):HT(6)=H(6)
376 M=74:FOR I=1 TO 6:POKE M,HT(I):M=M+1:NEXT I   'Save the time in lo memory
379 '
380 '  Signon Functions...
381 '
390 GOSUB 32000    'CP/M familiarity test
400 MSGS=1:CALLS=MSGS+1:MNUM=CALLS+1
425 BK=0
430 OPEN "I",1,"A:PWDS":IF EOF(1) THEN 450  '<-- Password file
440 INPUT #1,P1$,P2$   'use editor to make the file. e.g.: BANANA,APPLE,COW
450 CLOSE #1
460 ' BEL=-1:XPR=0 (initial bel on, not expert -- not used here but left for future development)
470 GOSUB 13020
480 SAV$=""
510 OPEN "I",1,"A:LASTCALR":INPUT #1,Y$,Z$:CLOSE
530 GOSUB 4050:GOSUB 13020   ' Print WELCOME File
540 BK=0:A$="(Prompting bell means system is ready for input).":GOSUB 13020:GOSUB 13020:XX=0
550 A$="What is your FIRST name ?":GOSUB 13020:C=1:GOSUB 13260:C=0:N$=B$:IF N$="" THEN 550
570 IF N$<"A" OR LEN(N$)=1 THEN 550
580 A1$="What is your LAST name ?":GOSUB 13020:C=1:GOSUB 13260:C=0:O$=B$:IF O$="" THEN 550
590 IF O$<"A" OR LEN(O$)=1 THEN 550
591 ' Note that the XXXXX below should be replaced with a codeword of your own.
592 ' It gets passed thru LASTCALR to MINIRBBS, which replaces it with "SYSOP",
593 ' a paranoid precaution which could probably be dispensed with....
595 IF N$<>"XXXXX" THEN 610  
600 IF N$="XXXXX" AND O$<>P1$ THEN XX=XX+1:IF XX=3 THEN 18100 ELSE 550
605 IF N$="XXXXX" AND O$=P1$ THEN O$="":A1$="2nd codeword?":GOSUB 13020:C=1:GOSUB 13260:C=0:X$=B$:IF X$=P2$ THEN 730 ELSE 550
610 IF N$="SYSOP" THEN PRINT:PRINT "You know you're not the SYSOP!!!":PRINT:XX=XX+1:IF XX=3 THEN 18100 ELSE 550   ' pseudo-SYSOP gets logged off on 3rd try
612 '
620 A$="Checking user file...":GOSUB 13020:V=0:OPEN "R",1,"A:USERS",62:FIELD#1,50 AS RZ$,4 AS NC$,6 AS DT$:GET#1,1:NU=VAL(RZ$)
625 FIELD #1,62 AS RR$
630 FOR I=2 TO NU+1:GET#1,I:IF INSTR(RZ$,N$)>0 AND INSTR(RZ$,O$)>0 THEN MF$=LEFT$(RZ$,1):GOSUB 15990:PUT#1,I:CLOSE:GOSUB 13020:XX=1:GOTO 700
640 NEXT I   ' If recognized, caller is passed to CALLER-logging routine
649 ' But a caller not in the USER file gets quizzed further...
650 V=1:A1$="Where (City,State) are you calling from ?":GOSUB 13020:C=1:GOSUB 13260:C=0:ST$=B$:IF ST$="" THEN 580
660 A$="Hello "+N$+" "+O$+" from "+ST$:GOSUB 13020
662 A1$="Is any of this misspelled ?":GOSUB 13020:C=1:GOSUB 13260:C=0
665 IF LEFT$(B$,1)="Y" THEN 550
667 IF LEFT$(B$,1)<>"N" THEN 662
670 A1$="This checking is only done the first time you call.":GOSUB 13020:LSET NC$=MKI$(0)
680 LSET RZ$="  "+N$+" "+O$+" "+ST$+SPACE$(44):GOSUB 15990:NU=NU+1:PUT#1,NU+1:S$=STR$(NU):GOSUB 16000:PUT#1,1:CLOSE
690 FIL$="NEWCOM":GOSUB 18000:MF$=" "   '...and made to read the NEWCOMer file
700 GOSUB 14200    '  Now everybody gets logged to CALLERS
705 A$="Logging "+N$+" "+O$+" to disk...":N=1:GOSUB 13020:OPEN "R",1,"A:CALLERS",60:FIELD#1,60 AS RR$:GET#1,1
710 RE=VAL(RR$)+1:S$=STR$(RE):RL=60:GOSUB 16000:PUT#1,1:RE=RE+1
715 S$=N$+" "+O$+" "+ST$+" "+TI$:GOSUB 16000:PUT#1,RE:CLOSE#1
719 '  Then twits (with *'s before their names in USERS) get logged off...
720 IF MF$="*" THEN A$="Goodbye.  Thanks for calling,  "+N$+" "+O$:GOSUB 13020:GOSUB 13020:GOTO 18080
722 '  while recallers go straight to CP/M.
723 IF N$=Y$ AND O$=Z$ THEN GOSUB 13020:A$="Welcome back.  Since you just signed off, go straight to CP/M":GOSUB 13020:GOTO 2240
724 '
726 '  User privilege level (from USERS) & date (DT$) is added to LASTCALR...
727 IF MF$="+" THEN F$="SP"
728 IF MF$=" " THEN F$="NW"
729 IF MF$="-" THEN F$="RG"
730 OPEN "O",1,"A:LASTCALR. "+CHR$(&HA0):PRINT #1,N$;",";O$;",";F$;",";DZ$:IF N$="XXXXX" THEN 2240
739 CLOSE
740 BK=0:GOSUB 13020:OPEN "R",1,"A:COUNTERS",5:FIELD#1,5 AS RR$
750 PRINT
760 A$="You are caller # : ":N=1:GOSUB 13020:GET#1,CALLS
770 CN=VAL(RR$)+INC:A$=STR$(CN):LSET RR$=A$:GOSUB 13020:PUT#1,CALLS
790 CLOSE:GOSUB 13020
792 '  And now the user gets to choose whether to answer the survey at 35000,
793 IF XX=0 THEN GOSUB 35000:GOTO 2200   'except that new users have no choice
795 A1$="Have you answered the user survey questions yet?":GOSUB 13020:C=1:GOSUB 13260:C=0
798 IF LEFT$(B$,1)="N" THEN GOSUB 35000
799 '
800 ' The SUMMARY file is now checked for messages to all except new users
830 '
835 A1$="Wait a second while I check to see if you have messages waiting ...":GOSUB 13020:GOSUB 13020
838 L=0
840 FT=1:MX=0:MZ=0:IU=0: ' (Flag first time for printing heading)
850 OPEN "R",1,"A:SUMMARY",30:RE=1:FIELD#1,28 AS RR$
860 BK=0:GET#1,RE:IF EOF(1) THEN 960
870 G=VAL(RR$):MZ=MZ+1:M(MZ,1)=G:IF G=0 THEN 950
880 IF IU=0 THEN IU=G
890 IF G>9998 THEN MZ=MZ-1:GOTO 960
900 GET#1,RE+3:GOSUB 16500:IF INSTR(S$,N$)>0 AND INSTR(S$,O$)>0 THEN 930
910 IF N$<>"XXXXX" THEN 950  
920 IF INSTR(S$,"BEN")=0 THEN 950
930 IF FT THEN L=L+1
931 IF FT THEN A$="The following messages for "+N$+" "+O$+" are waiting in MINIRBBS: ":GOSUB 13020:FT=0
940 A$=STR$(G):N=1:GOSUB 13020:GOSUB 13020
950 GET#1,RE+5:M(MZ,2)=VAL(RR$):MX=MX+M(MZ,2)+6:RE=RE+6:GOTO 860
960 IF L=0 THEN PRINT "Nope.  No message addressed to you, "+N$+".":PRINT "But check MINIRBBS anyway for public messages.":GOSUB 13020
965 CLOSE
2000 '
2020 '  Everyone comes here, to get ready to go to CP/M
2040 '
2049 '  They get menus according to their status....
2050 '
2051 IF MF$<>"+" THEN 2100
2052 GOSUB 13020:A$="As a special user, you have the following options:":GOSUB 13020:GOSUB 13020
2053 A$=" CON  Read CONFIDENTIAL msgs    MIN  Go to MINIRBBS":GOSUB 13020
2054 A$=" NEW  Read NEW program data     CPM  Go straight to CP/M":GOSUB 13020
2055 A$=" OFF  Log Off immediately":GOSUB 13020
2056 GOSUB 13020:A1$="Which?":GOSUB 13020:C=1:GOSUB 13260:C=0
2060 IF B$="CON" THEN 4100   'the SPECIAL file
2065 IF B$="MIN" THEN CHAIN "MINIRBBS"  'to the message module
2070 IF B$="NEW" THEN 2220   'the BULLETIN file
2075 IF B$="CPM" THEN 2230   'the DATA file, then CP/M
2076 IF B$="OFF" THEN CHAIN "EXITBBSB"  'straight to log-off module
2080 GOTO 2056
2099 '
2100 IF MF$=" " THEN 2200    ' Note that new callers don't get a menu
2110 GOSUB 13020:A$="Now you can do one of the following:":GOSUB 13020:GOSUB 13020
2120 A$=" NEW  Read about NEW programs    CPM  Go straight to CP/M":GOSUB 13020
2125 A$=" MIN  Go to message subsystem    OFF  Log Off immediately":GOSUB 13020
2130 GOSUB 13020:A1$="Which do you want? ":GOSUB 13020:C=1:GOSUB 13260:C=0
2135 IF B$="MIN" THEN CHAIN "MINIRBBS"
2140 IF B$="NEW" THEN 2220    ' RG callers can do everything SP callers can
2145 IF B$="CPM" THEN 2230    ' except read the SPECIAL file
2150 IF B$="OFF" THEN CHAIN "EXITBBSB"
2160 GOTO 2130
2170 '
2197 ' To discourage new callers from thinking this is a bulletin board system,
2198 ' this is the only choice they get
2199 '
2200 GOSUB 13020:A1$="Want data on the latest programs before entering CP/M?":GOSUB 13020:C=1:GOSUB 13260:C=0
2210 IF LEFT$(B$,1)="N" THEN 2230
2215 IF LEFT$(B$,1)<>"Y" THEN 2200
2220 GOSUB 3040 ' Print BULLETIN file
2225 IF MF$="+" THEN 2052
2226 IF MF$="-" THEN 2110
2230 GOSUB 4070 ' Print DATA file for everyone, including SP & RG callers
2235 CLOSE ' (just in case any files are still open)
2237 GOTO 44620  ' Then to the time-on-system routine, and then...
2240 GOSUB 13020:POKE 4,0:A$="Entering CP/M...":GOSUB 13020
2260 POKE 0,&HC3:SYSTEM ' we restore the "JMP" and go to CP/M.
3000 '
3010 ' The main program has now ended.  It's just subroutines from here on
3015 '
3020 ' The display BULLETIN file subroutine
3040 '
3060 GOSUB 12220
3080 FIL$="BULLETIN":GOSUB 18000:RETURN
4000 '
4020 ' The display WELCOME file subroutine
4030 '
4050 GOSUB 12220
4060 FIL$="WELCOME":GOSUB 18000:RETURN
4065 '
4070 ' The display DATA file subroutine*
4075 '
4080 GOSUB 12220
4090 FIL$="DATA":GOSUB 18000:RETURN
4095 '
4100 ' The display SPECIAL file subroutine*
4120 '
4140 GOSUB 12220
4160 FIL$="SPECIAL":GOSUB 18000:GOTO 2052
5000 '
12220 RETURN
12999 '
13000 A$="Use ctl-K to abort, ctl-S to pause."
13020 '
13026 ' In the following lines, substitute the &HC1 and &H01 for your
13027 ' modem and keyboard data input ports respectively 
13028 ' (REMOVE THE ' IN THE NEXT 2 LINES IF YOU WANT TO USE THEM)
13029 '
13030 ' IF INP(&HC1) AND 127=11 THEN BK=-1    'here, the PMMI data port
13032 ' IF INP(&H01) AND 127=11 THEN BK=-1
13033 '
13040 ' Routine to print string from A$ on console
13060 '
13080 IF SAV$<>"" AND A1$<>"" THEN A1$="":RETURN
13100 IF A1$<>"" THEN A$=A1$:A1$=""
13120 IF RIGHT$(A$,1)="?" OR N=1 THEN PRINT A$;:PP$=A$:GOTO 13180
13140 BI=ASC(INKEY$+" "):IF BI=19 THEN BI=ASC(INPUT$(1))
13160 IF BI=11 THEN BK=-1:GOTO 13220 ELSE PRINT A$
13180 A=A+LEN(A$)
13220 A$="":N=0
13240 RETURN
13260 '
13280 ' Routine to accept string into B$ from console
13300 '
13320 IF BEL AND SAV$="" THEN PRINT CHR$(7);
13340 B$="":BK=0
13360 IF SAV$="" THEN LINE INPUT SAV$
13380 SP=INSTR(SAV$,";"):IF SP=0 THEN B$=SAV$:SAV$="":GOTO 13420
13400 B$=LEFT$(SAV$,SP-1):SAV$=MID$(SAV$,SP+1)
13420 IF LEN(B$)=0 THEN RETURN
13440 IF C=0 THEN 13480
13460 FOR ZZ=1 TO LEN(B$):MID$(B$,ZZ,1)=CHR$(ASC(MID$(B$,ZZ,1))+32*(ASC(MID$(B$,ZZ,1))>96)):NEXT ZZ
13480 IF LEN(B$)<63 THEN 13580
13500 A$="Input line too long - would be truncated to:":GOSUB 13020
13520 B$=LEFT$(B$,62):PRINT B$
13540 LINE INPUT "Retype line (Y/N)?";QQ$:GOSUB 35600:QQ$=LEFT$(QQ$,1)
13560 IF QQ$="Y" OR QQ$="y" THEN PRINT PP$;:SAV$="":GOTO 13260
13580 D=D+LEN(B$):RETURN
13600 RETURN
13620 '
14000 ' Date getting subroutine
14010 ' (being read from MHTIME.COM running at E800H; you may be able to
14020 '  read the date directly from your clock's ports)
14030 '
14040 DM$=MID$(STR$(PEEK(&HEB13)),2)
14045 DD$=MID$(STR$(PEEK(&HEB14)),2)
14055 DT$=DM$+"/"+DD$
14060 DZ$=DM$+"/"+DD$+"/"+RIGHT$(STR$(81),2)
14090 RETURN
14100 ' 
14200 ' Time-finding subroutine
14205 '
14210 C=32 : ' C=CLOCK PORT (20H)
14220 ' This is a mountain hardware clock with ports for each time digit
14230 H(1)=INP(C+9) AND 15:H(2)=INP(C+8) AND 15
14240 H(3)=INP(C+7) AND 15:H(4)=INP(C+6) AND 15
14250 H(5)=INP(C+5) AND 15:H(6)=INP(C+4) AND 15
14255 '
14257 DS=(H(5)*10)+H(6) 
14260 DH=(H(1)*10)+H(2)
14265 DM=(H(3)*10)+H(4)
14269 DH$=STR$(DH)
14270 DI$=STR$(DM)
14275 DS$=STR$(DS)
14280 TI$=DD$+"-"+RIGHT$(DH$,2)+":"+RIGHT$(DI$,2)
14285 TD$=DH$+":"+RIGHT$(DI$,2)+":"+RIGHT$(DS$,2)
14290 RETURN
14999 '
15000 ' The ON-ERROR handler...
15001 '
15020 IF ERL=18030 THEN RESUME 18050
15030 IF ERL=700 THEN RE=0:RESUME 710
15100 RESUME NEXT
15887 '
15888 ' Small routine for writing date, etc., to USERS file (see lines 630 & 680))
15889 '
15990 S$=LEFT$(RZ$,50)+RIGHT$("   "+STR$(VAL(NC$)+1),4)+" "+RIGHT$("0"+DM$,2)
15992 S$=S$+"/"+RIGHT$("0"+DD$,2):RL=62   ' (now fall thru...).
16000 '
16010 ' Fill and store disk record...
16020 '
16030 LSET RR$=LEFT$(S$+SPACE$(RL-2),RL-2)+CHR$(13)+CHR$(10)
16040 RETURN
16500 '
16510 ' Unpack disk record...
16520 '
16530 ZZ=LEN(RR$)-2
16540 WHILE MID$(RR$,ZZ,1)=" "
16550 ZZ=ZZ-1:IF ZZ=1 THEN 16570
16560 WEND
16570 S$=LEFT$(RR$,ZZ)
16580 IF MID$(S$,ZZ,1)="?" THEN S$=S$+" "
16590 RETURN
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
18030 OPEN "I",1,"A:"+FIL$:BK=0
18040 IF EOF(1) OR BK THEN 18050 ELSE LINE INPUT #1,A$:GOSUB 13020:GOTO 18040
18050 CLOSE #1:RETURN
18060 '
18070 '
18080 ' Subroutine to log off an unwanted caller (=twit)
18090 '
18100 '
18120 OUT 195,0 '<-- Turn off PMMI to disconnect the line.
18130 POKE 0,&HC3 '<-- Restore the "jump" at BASE for CP/M.
18140 SYSTEM
19000 '  
32000 '  The CP/M familiarity testing routine  (feel free to make changes)
32001 '
32010 XX=0
32020 GOSUB 13020: A1$="What is the name of Digital Research's standard debugger?":GOSUB 13020:C=1:GOSUB 13260:C=0
32040 IF B$="DDT" THEN 32400
32050 IF B$="ddt" THEN 32400
32060 XX=XX+1:IF XX=2 THEN 18080   ' Log the caller off...
32080 PRINT "One more try...":GOTO 32020
32400 RETURN
32499 '
35000 '   BK's system user survey module  (again, make changes)
35001 '
35002 PRINT:PRINT "     ***   SYSTEM USER SURVEY  ***"
35005 OPEN "R",1,"A:SURVEY.BBS",40:FIELD#1,40 AS RR$:GET#1,1
35006 RE=VAL(RR$)+1
35007 IF RE=1 THEN RE=2
35008 S$=N$+" "+O$+" "+DZ$
35009 GOSUB 35200
35010 GOSUB 13020:GOSUB 13020:A$="Skip questions you don't feel like answering.  But more data"
35020 GOSUB 13020:A$="about your system will help make this system better":GOSUB 13020
35025 PRINT:PRINT "(Keep each answer to 34 chars. max.)"
35026 PRINT "(There are 8 questions in all)":PRINT
35030 PRINT "What kind of computer (or terminal) are you using? (S-100, Apple,"
35035 PRINT "  TRS-80, etc.; if S-100, which controller & CPU card?":GOSUB 35600:Q$=" 1":GOSUB 35100
35040 PRINT "With which operating systems? (CP/M 1.4?  CP/M 2.x?  TRS-DOS?"
35045 PRINT "  PASCAL?  More than one?)":GOSUB 35600:Q$=" 2":GOSUB 35100
35050 PRINT "How about the modem?  What brand & baud rate(s)?":GOSUB 35600:Q$=" 3":GOSUB 35100
35060 PRINT "Where did you learn of this system":PRINT " (If a BBS, which one)? ":GOSUB 35600:Q$=" 4":GOSUB 35100
35070 PRINT "Do you work with computers professionally?  Which kind?":GOSUB 35600:Q$=" 5":GOSUB 35100
35080 PRINT "How long have you been involved with microcomputers?":GOSUB 35600:Q$=" 6":GOSUB 35100
35085 PRINT "If you write your own programs, which languages do you usually use?":GOSUB 35600:Q$=" 7":GOSUB 35100
35090 PRINT "Are you interested in 16-bit CPUs or other"
35091 PRINT "  leading-edge equipment & software?  Which?":GOSUB 35600:Q$=" 8":GOSUB 35100
35092 PRINT "If you'd care to give details, leave a msg in MINIRBBS"
35094 S$=STR$(RE)
35095 GOSUB 16000
35096 PUT#1,1
35097 CLOSE
35098 PRINT:PRINT "Thanks for the information.  Now back to the log-in routine...":PRINT:RETURN
35100 ' PUT IN FILE
35120 GOSUB 13280:IF B$="" THEN S$="<omitted>" ELSE S$=B$
35140 S$=Q$+": "+S$
35200 RL=40
35220 GOSUB 16000
35240 PUT#1,RE
35260 RE=RE+1
35280 RETURN
35600 PRINT "----------------------------------|"
35620 RETURN
44620 '  Routines for printing the time & time-on-system 
44625 '   (for MH clock, but adaptable for other clocks)
44630 '    a. Print just time
44640 GOSUB 14200  
44650 PRINT "The time now is (Hrs:Mins:Secs)...."TD$
44659 '    b. Print elapsed time too
44660 GOSUB 44940
44670 GOTO 2240
44830 '    (calculate the time difference...)
44840 IF H(6)<HT(6) THEN H(6)=H(6)+10:H(5)=H(5)-1
44850 IF H(5)<HT(5) THEN H(5)=H(5)+6:H(4)=H(4)-1
44860 IF H(4)<HT(4) THEN H(4)=H(4)+10:H(3)=H(3)-1
44870 IF H(3)<HT(3) THEN H(3)=H(3)+6:H(2)=H(2)-1
44880 IF H(2)<HT(2) THEN H(2)=H(2)+10:H(1)=H(1)-1
44890 HD(6)=H(6)-HT(6):HD(5)=H(5)-HT(5):HD(4)=H(4)-HT(4)
44900 HD(3)=H(3)-HT(3):HD(2)=H(2)-HT(2):HD(1)=H(1)-HT(1)
44910 RETURN
44920 INPUT "TIME= H,H,M,M,S,S ";HT(1),HT(2),HT(3),HT(4),HT(5),HT(6)
44930 INPUT "LATER TIME H,H,M,M,S,S ";H(1),H(2),H(3),H(4),H(5),H(6)
44940 GOSUB 44830
44950 PRINT "You've been on the system for...... ";
44960 TF$="#"
44970 FOR I=1 TO 6
44980 PRINT USING TF$;HD(I);
44990 IF I=2 THEN PRINT ":";
45000 IF I=4 THEN PRINT ":";
45010 NEXT I
45020 PRINT
45030 RETURN
 