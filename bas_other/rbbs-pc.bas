
10      ' RBBS-I/O.BAS   Remote Bullettin Board Program
20      ' This Version Also Performs The Sign-On Functions & Modem I/O
35      ' See RBBS-I/O.DOC
30      ' Author - Russ Lane  - 6/21/82  -  (C)Copyright  1982
40      ' Gripes, Problems, Suggestions, Modifications, And Praise
50      ' Are More Than Welcome.  312-251-3067 (voice) -  312-251-0168 (data)
60      '
65 D$=LEFT$(DATE$,6)+RIGHT$(DATE$,2)
70 ON ERROR GOTO 13000
80 DEFINT A-Z : CR$=CHR$(13) : LF$=CHR$(10) : TB$=CHR$(9)
90 BK$=CHR$(8)+CHR$(32)+CHR$(8) : BK1$=CHR$(29)+CHR$(32)+CHR$(29)
95 GOSUB 100 : GOTO 200
100             ' Write Record #, Msg #, to Array -----------------------------
105 CLOSE #1,2 : DIM M(500,2)   'M(Record #,Msg #)        500 is max # of msgs.
110 R=1 : OPEN "R",#1,"MESSAGES" : FIELD #1,128 AS R$
120 GET 1,R : IF INSTR(R$,CHR$(226))>1 THEN DEAD=-1 ' If it's killed...
130 RR=VAL(MID$(R$,118)) : IF DEAD THEN 150 ELSE IF RR<1 THEN 160
140 LASTR=LASTR+1 : M(LASTR,1)=R : M(LASTR,2)=VAL(LEFT$(R$,5))
150 R=R+RR : DEAD=0 : GOTO 120
160 FIRSTM=M(1,2) : LASTM=M(LASTR,2) : RETURN
200             ' Wait for Caller to Call -------------------------------------
210 OPEN "COM1:300,N,8,1" AS #3
220 PRINT "Sign-on module ready."
230 WHILE EOF(3)
234 IF INKEY$=CHR$(27) THEN PRINT "Sysop is in.":CLOSE 3:LOCAL=-1:GOTO 450
236 WEND
238 WHILE INPUT$(2,3)<>STRING$(2,13) : WEND
240 WIDTH 80:SCREEN 0,0,0:KEY OFF : TI$=TIME$
250 A$="Do you need line feeds ? ":CR=1:GOSUB 1400:Z$=INPUT$(1,#3):GOSUB 5000
255 IF Z$="Y" THEN LF=-1 ELSE IF Z$="N" THEN LF=0 ELSE GOSUB 1400:GOTO 250
257 A$=Z$ : CR=2 : GOSUB 1400
260 RET=1:STI=-1:FILE$="WELCOME" :GOSUB 6000 'STI Enables Interrupts (Ctrl-K)
270 RET=2:STI=-1:FILE$="BULLETIN":GOSUB 6000 'RET Will Return To Here From ^K
280 CR=2:GOSUB 1400:TRIES=0:STI=0   'Interrupts Off
300            ' Get Caller's Name --------------------------------------------
305 IF TRIES>5 THEN 12000 ' Log-Off Nicely
310 TRIES=TRIES+1:GOSUB 1400:A$="What is your FIRST Name":GOSUB 1500
320 IF Q=0 THEN 300 ELSE Z$=B$(1):GOSUB 5000:FIRST$=Z$:IF Q=1 THEN 340
330 Z$=B$(2):GOSUB 5000:LAST$=Z$:GOTO 370
340 A$="What is your LAST  Name":GOSUB 1500
350 Z$=B$(1):GOSUB 5000:LAST$=Z$
370 IF LEN(FIRST$)<2 OR LEN(LAST$)<2 THEN 300
380 IF FIRST$="PASS" AND LAST$="WORD" THEN 450    'Place Sysop's Password Here
390 NAM$=FIRST$+CHR$(32)+LAST$
400 IF INSTR(NAM$,"SYSOP")OR INSTR(NAM$,"RUSS LANE")THEN 12500 'Log-Off Wiseguy
410 FOR Q=1 TO LEN(NAM$)
430 X=ASC(MID$(NAM$,Q,1)) : IF (X<65 OR X>90) AND (X<>32 AND X<>39) THEN 300
440 NEXT : GOSUB 1400 : GOTO 500
450 FIRST$="RUSS":LAST$="LANE":NAM$="SYSOP":SYSOP=-1:BELL=0:XPR=-1:GOTO 1200
500            ' Check Last Caller --------------------------------------------
510 OPEN "I",#2,"LASTCALR" : INPUT #2,N$,CALLN : CLOSE #2
520 IF NAM$<>N$ THEN 600
530 LASTCALR=-1 : A$="Welcome back, "+FIRST$ : CR=2 : GOSUB 1400 : GOTO 820
600            ' Check User File ---------------------------------------------
610 A$="Checking User File..." : CR=2 : GOSUB 1400
620 OPEN "I",#2,"USERS"
630 IF EOF(2) THEN CLOSE #2:GOTO 700
640 INPUT #2,N$,CITY$,STATE$,STATU$
650 IF NAM$<>N$ THEN 630
660 CLOSE #2
670 IF STATU$="OK" THEN 810 ' Can Access System
680 GOTO 12530              ' Log-Off Weasel
700            ' Get New User's Background ------------------------------------
710 NEWCALR=-1
720 A$="What CITY  are you calling from":GOSUB 1500
730 IF Q=0 THEN 300 ELSE Z$=B$(1) : GOSUB 5000 : CITY$=Z$
740 A$="What STATE are you calling from":GOSUB 1500
750 IF Q=0 THEN 720 ELSE Z$=B$(1) : GOSUB 5000 : STATE$=Z$
760 A$=TB$+NAM$:GOSUB 1400
770 A$=TB$+CITY$+", "+STATE$:CR=2:GOSUB 1400
780 A$="Is this correct":GOSUB 1500:GOSUB 1400:IF NOT YES THEN 300
790 OPEN "A",#2,"USERS" : WRITE #2,NAM$,CITY$,STATE$,"OK" : CLOSE #2
795 A$="This is only done the first time you call, "+FIRST$ : CR=2 : GOSUB 1400
800            ' Log To Disk -------------------------------------------------
810 A$="Logging "+NAM$+" to disk..." : CR=2 : GOSUB 1400
820 OPEN "O",#2,"LASTCALR" : CALLN=CALLN+1
830 WRITE #2,NAM$,CALLN : CLOSE #2
840 OPEN "A",#2,"CALLERS"
850 PRINT #2,NAM$;"  ";D$;"  ";TI$ : CLOSE #2
860 IF LASTCALR OR NEWCALR OR SYSOP THEN 1040 ' Bypass Search For Msgs
900            ' Search for any messages to this caller ----------------------
920 A$="I'm seeing if there are messages waiting for you...":CR=2 : GOSUB 1400
930 X=37:Y=31:F$=NAM$:T=0:DONE=0:R=1
950 GET 1,R : RR=VAL(MID$(R$,118)) : R=R+RR : IF RR<1 THEN 970
960 IF INSTR(MID$(R$,37,31),NAM$)>0 THEN 980 ELSE 950
970 IF T THEN 1040 ELSE 1030
980 IF T THEN 1020
990  A$="The following message(s) was/were left for you.":GOSUB 1400
1000 A$="Please (K)ill those that would not interest other callers."
1010 GOSUB 1400:T=-1
1020 A$=LEFT$(R$,5):CR=1:GOSUB 1400:GOTO 950
1030 A$="Nope.  No messeges for you, "+FIRST$
1040 CR=2 : GOSUB 1400 : A$="Entering The Messege Sub-System..." : GOSUB 1400
1050 LOCATE 25,1:PRINT SPACE$(80-(LEN(NAM$)+10));NAM$;"  ";TI$
1060 XPR=0 : BELL=-1 : MARGIN=64
1070 RET=0 : GOSUB 4900 : STI=-1 : GOSUB 1700
1200            ' Command Dispatcher ------------------------------------------
1210 STI=-1:RET=0:Q=0           'Interrupts On,  Return To Here On A Ctrl-K
1220 ERASE B$
1230 GOSUB 1400
1240 IF SYSOP THEN GOSUB 10000
1250 A$="Function"
1260 IF NOT XPR THEN A$=A$+"  <B,C,E,G,H,K,L,P,Q,R,S,X,Y,#,? >"
1270 GOSUB 1500:IF Q=0 THEN 1250
1280 FOR J=1 TO Q
1290 Z$=B$(J):GOSUB 5000
1300 FF=INSTR("?BCEGHKLPQRSXY#$%^&*(",Z$)
1310 IF FF=0 THEN 1360 ELSE IF FF>15 AND NOT SYSOP THEN 1360
1320 '           ?    B    C    E    G     H     K     L     P     Q     R
1330 ON FF GOSUB 1700,1720,1800,2000,12000,1740, 3900, 4100, 4150, 4310, 4320, 
                 4330,4200,4700,4900,10100,10120,10200,10400,10600,10800
1340 '           S    X    Y    #    $     %     ^     &     *     (
1350 NEXT J : GOTO 1200
1360 IF XPR THEN 1250 ELSE GOSUB 1400
1370 A$=FIRST$+", I don't understand "+B$(J):GOSUB 1400:GOTO 1200
1380 '
1390 '
1400            ' Print string ------------------------------------------------
1402 Y$=INKEY$ : IF LOCAL THEN 1430
1405 IF EOF(3) THEN 1430
1410 Y$=INPUT$(1,#3)
1420 IF Y$=CHR$(19) THEN WHILE EOF(3) : WEND    ' Ctrl-S
1430 IF Y$=CHR$(11) AND STI THEN 1480           ' Ctrl-K
1440 LOCATE ,,1 : PRINT A$; : IF LOCAL THEN 1450
1445 PRINT #3,A$;
1450 IF CR=1 THEN 1470
1460 PRINT : IF LOCAL THEN 1465
1462 PRINT #3,"" : IF LF THEN PRINT #3,CR$+LF$
1465 IF CR=2 THEN CR=0 : GOTO 1460
1470 Y$="" : A$="" : CR=0 : RETURN
1480 CLOSE #2 : A$="++ Aborted ++" : GOSUB 1400 : ON RET GOTO 270,280
1490 RETURN 1200
1500            ' Input string ------------------------------------------------
1510 A=0:B=0:C=0:Q=1:EOL=0:YES=0:B$=""
1520 A$=A$+" ? "
1530 IF BELL THEN A$=A$+CHR$(7)
1540 CR=1 : GOSUB 1400 : IF LOCAL THEN INPUT "",B$ : GOTO 1575
1550 WHILE EOF(3)
1552 Y$=INKEY$ : IF Y$<>"" THEN 1562
1554 WEND
1560   Y$=INPUT$(1,#3)
1562   IF Y$=CHR$(8) THEN 1670
1564   PRINT Y$; : PRINT #3,Y$;
1566   IF Y$=CR$ THEN 1570
1568   B$=B$+Y$ : GOTO 1550
1570 IF LF THEN PRINT #3,CR$+LF$
1575 A=INSTR(B$,";") : IF A=0 THEN 1640
1580 B$(1)=LEFT$(B$,A-1)
1582 B=INSTR(A+1,B$,";")
1584 C=B-(A+1) : IF C<1 THEN EOL=-1 : C=50 '50 insures all rightmost characters
1590 BB$=MID$(B$,A+1,C)
1600 IF BB$<>"" THEN Q=Q+1:B$(Q)=BB$
1610 IF NOT EOL THEN A=B:GOTO 1582
1620 IF LEN(B$)=>20 THEN A$="Try again, ";FIRST$ : GOSUB 1400 : GOTO 1500
1630 RETURN
1640 B$(1)=B$ : IF B$="" THEN Q=0
1650 IF LEFT$(B$,1)="Y" OR LEFT$(B$,1)="y" THEN YES=-1
1660 RETURN
1670 IF LEN(B$)=0 THEN 1550
1680 B$=LEFT$(B$,LEN(B$)-1)
1690 PRINT BK1$; : PRINT #3,BK$; : GOTO 1550
1700           ' ? Type Functions Supported -----------------------------------
1710 FILE$="HELP02":GOSUB 6000:RETURN
1720           ' Type Bulletins -----------------------------------------------
1730 FILE$="BULLETIN":GOSUB 6000:RETURN
1740           ' Type Help File -----------------------------------------------
1750 FILE$="HELP01":GOSUB 6000:RETURN
1800           ' Comments -----------------------------------------------------
1810 GOSUB 1400:A$="Comments are only readable by Sysop.":GOSUB 1400:MARGIN=64
1820 A$="Do you wish to leave any":GOSUB 1500
1830 IF NOT YES THEN A$="No comment.":GOSUB 1400:RETURN
1840 LI=0:DIM A$(30)
1850 GOSUB 1400:A$="Enter up to 20 lines. (lone C/R to end):GOSUB 1400
1860 GOSUB 1400:GOSUB 3200
1870 R$="":LI=LI+1:A$="   "+STR$(LI)+": "+A$(LI):IF LI<10 THEN A$=" "+A$
1880 CR=1 : GOSUB 1400 : GOSUB 3700
1890 IF A$(LI)="" THEN LI=LI-1:IF LI<1 THEN ERASE A$:RETURN ELSE 1940
1900 IF LI=18 THEN A$="Two lines left...":GOSUB 1400
1910 IF LI=19 THEN A$="Last line.":GOSUB 1400
1920 IF LI=20 AND NOT SYSOP THEN A$="Comment full.":GOSUB 1400:GOTO 1940
1930 GOTO 1870
1940 OPEN "A",#2,"COMMENTS"
1950 GOSUB 1400:A$="Many thanks for the comments, "+FIRST$:GOSUB 1400
1960 PRINT #2,NAM$,D$,TIME$
1970 FOR X=1 TO LI:PRINT #2,A$(X):NEXT
1980 FOR X=1 TO 2 :PRINT #2,CHR$(13):NEXT:CLOSE #2:ERASE A$:RETURN
2000           ' Enter A Messege --------------------------------------------
2010 GOSUB 1400:T$="":PAS$="":LI=0:L=0:X=0:BEGIN=0
2030 DIM A$(30)
2040 A$="Messege will be # "+STR$(LASTM+1) : GOSUB 1400
2050 A$="Who To <C/R  For All>":GOSUB 1500
2060 IF LEN(B$(1))>30 THEN A$="30 Chars max.":GOSUB 1400:GOTO 2050
2070 IF Q=0 THEN T$="ALL" ELSE Z$=B$(1):GOSUB 5000:T$=Z$
2080 A$="Subject":GOSUB 1500
2090 IF LEN(B$(1))>25 THEN A$="25 Chars max.":GOSUB 1400:GOTO 2080
2100 IF Q=0 THEN 2050 ELSE Z$=B$(1):GOSUB 5000:SUB$=Z$
2110 A$="Protect  <K,R,N,?>":IF XPR THEN 2130
2120 A$="Protect  < <K>ill, <R>ead, <N>one, <?>Help >"
2130 GOSUB 1500:Z$=LEFT$(B$(1),1):GOSUB 5000:IF Z$="N" THEN 2190
2140 IF Z$="?" THEN FILE$="HELP03":GOSUB 6000:GOTO 2120
2150 IF Z$="K" THEN 2170
2160 IF Z$="R" THEN PAS$="^READ^":GOTO 2190
2165 GOTO 2080
2170 A$="Password":GOSUB 1500
2180 IF LEN(B$(1))>15 THEN A$="15 Chars. max.":GOSUB 1400:GOTO 2170 
2185 PAS$=B$(1)
2190 GOSUB 1400:IF XPR THEN 2212
2200 A$="To enter message, type in lines.":GOSUB 1400
2210 A$="To edit, type lone C/R.   20 lines max.":GOSUB 1400
2212 A$="Right-Margin is set at"+STR$(MARGIN):GOSUB 1400
2214 A$="Do you wish to change it":GOSUB 1500
2216 IF YES THEN BEGIN=-1:GOTO 3100
2218 BEGIN=0:GOSUB 3200
2220 R$="" : LI=LI+1 : A$="   "+STR$(LI)+": "+A$(LI):IF LI<10 THEN A$=" "+A$
2230 CR=1 : GOSUB 1400:GOSUB 3700
2240 IF A$(LI)="" THEN LI=LI-1:GOTO 2310
2250 IF LI=18 THEN A$="Two lines left...":GOSUB 1400
2260 IF LI=19 THEN A$="Last line.":GOSUB 1400
2270 IF LI=20 AND NOT SYSOP THEN A$="Messege full.":GOSUB 1400:GOSUB 2300
2280 GOTO 2220
2300            'Editing dispatcher ------------------------------------------
2305 GOSUB 1400
2310 IF XPR THEN A$="Function  <A,C,D,E,I,L,M,S,? >":GOTO 2340
2320 A$="Functions : <A>bort, <C>ontinue, <D>elete, <E>dit,":GOSUB 1400
2330 A$="            <I>nsert, <L>ist, <M>argin, <S>ave, <?>Help "
2340 GOSUB 1500:IF Q=0 THEN 2310 ELSE Z$=B$(1):GOSUB 5000
2350 IF Q>1 AND Z$<>"M" THEN L=VAL(B$(Q)):GOSUB 3320 'Test validity of line #
2360 FF=INSTR("ACDEILMS?",Z$):IF FF<1 OR FF>9 THEN 2310
2370 ON FF GOTO 2400,2380,2500,2600,2800,3000,3100,3400,2390
2380 GOSUB 3200:GOTO 2250   'Continue
2390 FILE$="HELP04":GOSUB 6000:GOTO 2320
2400            'Abort -------------------------------------------------------
2410 GOSUB 1400:A$="Do you confirm Abortion":GOSUB 1500
2420 IF NOT YES THEN 2300
2430 GOSUB 1400:A$="Aborted.":GOSUB 1400:ERASE A$:RETURN 1200
2500            'Delete A Line -----------------------------------------------
2510 GOSUB 1400:IF Q=1 THEN A$="Delete ":CR=1:GOSUB 1400:GOSUB 3300
2520 A$="Line #"+STR$(L) : GOSUB 1400 : A$=A$(L) : CR=2 : GOSUB 1400
2530 A$="Do You Confirm Deletion":GOSUB 1500
2540 IF NOT YES THEN A$="Line #"+STR$(L)+" NOT Deleted.":GOSUB 1400:GOTO 2300
2550 FOR X=L TO LI:A$(X)=A$(X+1):NEXT:LI=LI-1
2560 A$="Line #"+STR$(L)+" Deleted.":GOSUB 1400:GOTO 2300
2600            'Edit A Line -------------------------------------------------
2610 GOSUB 1400:IF Q=1 THEN GOSUB 3300
2620 A$="Line # "+STR$(L)+" Was :":GOSUB 1400:A$=A$(L):CR=2:GOSUB 1400
2630 A$="Enter  Oldstring;Newstring  or  C/R for no change.":GOSUB 1400
2640 GOSUB 1400:GOSUB 1500
2650 IF Q=0 THEN 2300
2660 X=INSTR(1,A$(L),B$(1)):IF X=0 THEN 2720
2680 LB1=LEN(B$(1)):LB2=LEN(B$(2)):IF LB1<>LB2 THEN 2700
2690 MID$(A$(L),X)=B$(2):GOTO 2620
2700 C$=MID$(A$(L),X+LB1):CC$=LEFT$(A$(L),X-1)
2710 A$(L)=CC$+B$(2)+C$:GOTO 2620
2720 A$="String  '"+B$(1)+"' not found in line "+STR$(L):GOSUB 1400:GOTO 2300
2800            'Insert A Line -----------------------------------------------
2810 DIM C$(30)
2820 GOSUB 1400:IF Q=1 THEN A$="Before ":CR=1:GOSUB 1400:GOSUB 3300
2830 W=LI:K=LI-L:FOR X=L TO LI:C$(X+1-L)=A$(X):A$(X)="":NEXT : LI=L
2840 R$="":A$=STR$(LI)+": ":IF LI<10 THEN A$=" "+A$
2850 CR=1:GOSUB 1400:GOSUB 3700
2860 IF A$(LI)="" THEN 2920
2870 LI=LI+1
2880 IF LI+K=18 THEN A$="Two lines left...":GOSUB 1400
2890 IF LI+K=19 THEN A$="Last line.":GOSUB 1400
2900 IF LI+K=20 AND NOT SYSOP THEN A$="Messege full.":GOSUB 1400:GOTO 2920
2910 GOTO 2840
2920 FOR X=1 TO K+1:A$(LI+X-1)=C$(X):NEXT:LI=W+LI-L
2930 ERASE C$ : GOTO 2300
3000            'List Lines --------------------------------------------------
3010 GOSUB 1400:GOSUB 3200
3020 FOR X=1 TO LI:A$="   "+STR$(X)+": "+A$(X):IF X<10 THEN A$=" "+A$
3030 GOSUB 1400:NEXT:GOSUB 1400:GOTO 2300
3100            'Set Right Margin --------------------------------------------
3110 GOSUB 1400:IF Q<>1 THEN B$(1)=B$(Q):GOTO 3130
3120 A$="Set Right-Margin to (8,16,24,32,40,48,56,64) ":GOSUB 1500
3130 FOR X=8 TO 64 STEP 8:IF VAL(B$(1))=X THEN 3150 ELSE NEXT
3140 A$="Invalid - Margin remains at"+STR$(MARGIN):GOSUB 1400:GOTO 3160
3150 MARGIN=VAL(B$(1)):A$="Margin now set to"+STR$(MARGIN):GOSUB 1400
3160 IF BEGIN THEN 2218 ELSE 2300
3200            'Print Tab Settings ------------------------------------------
3210 GOSUB 1400:A$=TB$+"!" : CR=1 : GOSUB 1400
3220 FOR X=8 TO MARGIN STEP 8:A$="-------!":CR=1:GOSUB 1400:NEXT:GOSUB 1400:RETURN
3300            'Test Line Number --------------------------------------------
3310 A$="Line #":GOSUB 1500:L=VAL(B$(1)):'PRINT B$(1)
3320 IF L=>1 AND L=<LI THEN RETURN
3330 IF Q=0 THEN RETURN 2300
3340 IF ASC(B$(1))<49 AND ASC(B$(1))>57 THEN RETURN 1200
3350 A$="No such line, "+FIRST$:GOSUB 1400:GOTO 2300
3400            'Save Messege ------------------------------------------------
3410 GOSUB 1400:A$="Updating Msg file.":CR=1:GOSUB 1400
3420 CLOSE #2:OPEN "O",#2,"LASTCALR" : LASTM=LASTM+1 : LASTR=LASTR+1
3430 WRITE #2,NAM$,D$,TI$,STATUS,CALLN : CLOSE #2
3440            '
3450 REC=0:N$=""
3460 MNUM$=STR$(LASTM)+SPACE$(5-LEN(STR$(LASTM)))'1-5
3470 FROM$=NAM$+SPACE$(31-LEN(NAM$))             '6-36
3480 T$=T$+SPACE$(31-LEN(T$))                    '37-67
3490 SUB$=SUB$+SPACE$(25-LEN(SUB$))              '76-100
3500 PAS$=PAS$+SPACE$(15-LEN(PAS$))              '101-115
3510 FOR J=1 TO LI:A$(J)=A$(J)+CHR$(227):REC=REC+LEN(A$(J)):NEXT J
3520 IF REC MOD 128=0 THEN N$=STR$(REC\128+1) ELSE N$=STR$(REC\128+2)
3530 CLOSE #1:OPEN "R",#1,"MESSAGES" : FIELD #1,128 AS R$
3540 GET 1,LOF(1)/128 : M(LASTR,1)=LOC(1)+1 : M(LASTR,2)=LASTM
3550 M(LASTR,1)=LOC(1)+1 : M(LASTR,2)=LASTM
3560 LSET R$=MNUM$+FROM$+T$+D$+SUB$+PAS$+CHR$(225)+N$ : PUT 1
3600            'Pack Disk Record --------------------------------------------
3610 FOR J=1 TO LI:A$=".":CR=1:GOSUB 1400
3620 FOR K=1 TO LEN(A$(J))
3630 E$=E$+MID$(A$(J),K,1)
3640 IF LEN(E$)>127 THEN LSET R$=E$:PUT 1:E$=""
3650 NEXT K
3660 NEXT J
3670 LSET R$=E$:PUT 1:E$=""
3680 ERASE A$:RETURN
3700           'Word Processor -----------------------------------------------
3710 COL=COL+1:IF LOCAL THEN X$=INPUT$(1) ELSE X$=INPUT$(1,3)
3720 IF X$=CHR$(8) THEN 3850 ELSE IF X$=CHR$(9) THEN P=POS(0)
3730 A$=X$ : CR=1 : GOSUB 1400 : IF X$=CHR$(9) THEN COL=COL+(POS(0)-P)
3740 IF X$=CHR$(13) THEN 3840
3750 IF COL>MARGIN-3 AND X$=CHR$(32) THEN GOSUB 1400:GOTO 3840
3760 R$=R$+X$
3770 IF COL<MARGIN+1 THEN 3710
3780 IF X$=CHR$(32) THEN GOSUB 1400:GOTO 3840
3790 Z=MARGIN+1
3800 WHILE (MID$(R$,Z,1)<>" " AND MID$(R$,Z,1)<>"" AND MID$(R$,Z,1)<>CHR$(9))
3810 Z=Z-1:IF Z>0 THEN WEND ELSE GOSUB 1400:GOTO 3840
3820 COL=MARGIN+1-Z : PRINT STRING$(COL,29)+STRING$(COL,0);
3825 IF NOT LOCAL THEN PRINT #3,STRING$(COL,8)+STRING$(COL,32);
3830 A$(LI)=LEFT$(R$,Z):A$(LI+1)=RIGHT$(R$,COL):GOSUB 1400:RETURN
3840 A$(LI)=A$(LI)+R$:COL=0:RETURN
3850 COL=COL-2:R$=LEFT$(R$,LEN(R$)-1)
3860 PRINT BK1$; : IF NOT LOCAL THEN PRINT #3,BK$;
3870 GOTO 3710
3900            'Kill A Message ---------------------------------------------
3905 GOSUB 1400
3910 IF Q<>1 THEN MM=VAL(B$(Q)):GOTO 3930
3920 A$="Msg # to Kill":GOSUB 1500:MM=VAL(B$(Q)):GOSUB 1400
3926 IF MM=0 THEN RETURN
3930 FOR Q=1 TO LASTR : IF M(Q,2)=MM THEN 3950 ELSE NEXT
3940 A$="No Msg # "+STR$(MM):GOSUB 1400:RETURN 1200
3950 GET 1,M(Q,1) : R=VAL(MID$(R$,118)) : IF SYSOP THEN 4030
3960 Z=15:Z$=MID$(R$,101,15) : GOSUB 8100 : PAS$=Z$
3990 IF PAS$="^READ^" THEN IF INSTR(R$,NAM$) THEN 4030 ELSE 4020
4000 A$="Password":GOSUB 1500
4010 IF B$(1)=PAS$ THEN 4030
4020 A$="Sorry Buckwheat, you lose.":GOSUB 1400:RETURN 1200
4030 LSET R$=LEFT$(R$,115)+CHR$(226)+MID$(R$,117) : PUT 1,LOC(1)
4040 IF Q>1 THEN GET 1,M(Q-1,1)
4050 M(Q,1)=VAL(MID$(STR$(VAL(MID$(R$,118))+R),2)) : LASTR=LASTR-1
4060 FOR Q=Q TO LASTR:M(Q,1)=M(Q+1,1):M(Q,2)=M(Q+1,2):NEXT
4070 FIRSTM=M(1,2) : LASTM=M(LASTR,2)
4080 A$="Msg # "+STR$(MM)+" Killed.":GOSUB 1390:RETURN 1200
4100            'Toggle Line Feeds --------------------------------------------
4110 GOSUB 1400:LF=NOT LF
4120 A$="Line Feeds ":IF LF THEN A$=A$+"On" ELSE A$=A$+"Off"
4130 GOSUB 1400:RETURN
4150            'Toggle Bell --------------------------------------------------
4160 GOSUB 1400:BELL=NOT BELL
4170 A$="Prompting Bell ":IF BELL THEN A$=A$+"On" ELSE A$=A$+"Off"
4180 GOSUB 1400:RETURN
4200            'Toggle Expert ------------------------------------------------
4210 GOSUB 1400:XPR=NOT XPR
220 IF XPR THEN A$="Expert Mode" ELSE A$="Novice Mode"
4230 GOSUB 1400:RETURN
4300            'Quick Scan & Summary & Retrieval -----------------------------
4310 QU=-1:RT=0 :SU=0:GOTO 4340 'Quick Scan Entry Point
4320 QU=0 :RT=-1:SU=0:GOTO 4340 'Retreival  Entry Point
4330 QU=0 :RT=0 :SU=-1          'Summarize  Entry Point
4340 FOW=0:REV=0:RP=0 'Forward Flag, Reverse Flag, Read Protect Flag
4350 IF Q<>1 THEN MM=VAL(B$(Q)):GOTO 4390
4360 A$="Msg #  ("+STR$(FIRSTM)+" to"+STR$(LASTM)+" )":IF XPR THEN 4380
4370 IF RT THEN A$=A$+" to Retreive ( C/R to end)" ELSE A$="Starting at "+A$
4380 GOSUB 1500:MM=VAL(B$(1))
4390 IF VAL(B$(Q))=0 THEN RETURN 1200 ELSE GOSUB 1400
4400 IF RIGHT$(B$(Q),1)="+" THEN FOW=-1
4410 IF RIGHT$(B$(Q),1)="-" THEN REV=-1:GOTO 4460
4420 FOR Q=1 TO LASTR
4430 IF RT AND M(Q,2)=MM THEN 4490
4440 IF ( (RT AND FOW) OR QU OR SU) AND M(Q,2)=>MM THEN 4490
4450 NEXT : PRINT "No Msg # "+STR$(MM):RETURN 1200
4460 FOR Q=LASTR TO 1 STEP -1
4470 IF M(Q,2)<=MM THEN 4510
4480 NEXT : A$="No Msg # "+STR$(MM):GOSUB 1400:RETURN 1200
4490 IF FOW THEN 4500 ELSE IF RT THEN 4530
4500 QQ=Q : QQQ=LASTR : QQQQ=1 : GOTO 4520
4510 QQ=Q : QQQ=1     : QQQQ=-1
4520 FOR Q=QQ TO QQQ STEP QQQQ
4530 GET 1,M(Q,1)
4535 IF NOT SYSOP THEN IF INSTR(R$,"^READ^")>0 AND INSTR(R$,NAM$)=0 THEN 4590
4537 IF QU THEN Z$=MID$(R$,76,25):Z=25:GOSUB 8100
4540 IF QU THEN A$=STR$(M(Q,2))+"  "+Z$:GOSUB 1400:GOTO 4570
4550 GOSUB 8000:IF SU THEN 4570
4560 GOSUB 9000:IF RT AND (NOT FOW AND NOT REV) THEN Q=1:GOTO 4340
4570 NEXT Q
4580 GOSUB 1400:A$="End of Msgs.":GOSUB 1400:RETURN 1200
4590 IF FOW OR REV OR SU OR QU THEN 4570
4600 A$="Sorry, "+FIRST$+".  Msg #"+STR$(MM)+" is read protected."
4610 GOSUB 1400:Q=0:GOTO 4340
4700            'Y Chat -------------------------------------------------------
4710 GOSUB 1400 : A$="Chat... Remote Conversation Utility." : CR=2 : GOSUB 1400
4720 A$="Program returns to command level within" : GOSUB 1400
4730 A$="30 seconds if operator is unavailable" : CR=2 : GOSUB 1400
4740 K=0 : A$="Alerting operator now" : CR=1 : GOSUB 1400
4750 FOR I=1 TO 20
4760 FOR J=1 TO 500 : NEXT J
4770 K=K+1 : IF INKEY$=CHR$(27) THEN 4830
4780 IF K MOD 2 THEN A$=CHR$(7) : CR=1 : GOSUB 1400
4790 A$=". " : CR=1 : GOSUB 1400 : NEXT I : GOSUB 1400
4800 A$="Sorry "+FIRST$+", no operator available." : GOSUB 1400
4810 A$="Please leave a message on the board or in the comments."
4820 GOSUB 1400 : RETURN
4830 GOSUB 1400 : A$="Operator is available." : GOSUB 1400
4840 A$="Go ahead..." : CR=2 : GOSUB 1400
4850 WHILE EOF(3) : A$=INKEY$
4860 IF A$=CHR$(8) THEN 4895 ELSE IF A$=CHR$(27) THEN RETURN 1200
4870 IF A$<>"" THEN CR=1 : GOSUB 1400 : GOTO 4850
4880 WEND : A$=INPUT$(1,#3) : IF A$=CHR$(8) THEN 4895
4890 CR=1 : GOSUB 1400 : GOTO 4850
4895 IF POS(0)>1 THEN PRINT BK1$; : PRINT #3,BK$;
4897 GOTO 4850
4900            '# Counters ---------------------------------------------------
4910 GOSUB 1400
4920 A$="     You are caller #   -->"+STR$(CALLN):GOSUB 1400
4930 A$="     # of Active msgs   -->"+STR$(LASTR):GOSUB 1400
4940 A$="     Next msg # will be -->"+STR$(LASTM+1):GOSUB 1400:RETURN
5000            'Convert Lower Case to Upper Case -----------------------------
5010 FOR Z=1 TO LEN(Z$)
5020 MID$(Z$,Z,1)=CHR$(ASC(MID$(Z$,Z,1))+32*(ASC(MID$(Z$,Z,1))>96))
5030 NEXT Z : RETURN
6000            'Common Routine to Print  A File ------------------------------
6010 OPEN "I",#2,FILE$
6020 IF EOF(2) THEN CLOSE #2:RETURN
6030 LINE INPUT #2,A$:GOSUB 1400:GOTO 6020
7000            'Common Routine To Test Fields --------------------------------
7010 GET 1,R : RR=VAL(MID$(R$,118))
7020 IF RR<1 THEN DONE=-1:RETURN
7030 R=R+RR
7040 IF INSTR(MID$(R$,X,Y),F$) THEN RETURN
7050 GOTO 7010
8000           'Process Message Header ----------------------------------------
8005 GOSUB 1400
8010 IF MID$(R$,37,3)="ALL" THEN T$="ALL":GOTO 8030
8020 Z=31 : Z$=MID$(R$,37,31) : GOSUB 8100 : T$=Z$
8030 Z=25 : Z$=MID$(R$,76,25) : GOSUB 8100 : SUB$=Z$
8040 Z=31 : Z$=MID$(R$, 6,31) : GOSUB 8100 : FROM$=Z$
8050 A$="Msg # "+LEFT$(R$,5)+" Dated "+MID$(R$,68,8)+" From : "+FROM$
8060 GOSUB 1400 : A$="To: "+T$ : GOSUB 1400
8070 A$="Re: "+SUB$ : GOSUB 1400 : RETURN
8099            'Remove Spaces That Pad Msg Header
8100 WHILE MID$(Z$,Z,1)=" ":Z=Z-1:WEND : Z$=LEFT$(Z$,Z) : RETURN
9000           'Unpack Disk Record --------------------------------------------
9005 GOSUB 1400
9010 FOR X=1 TO VAL(MID$(R$,118))-1
9020 EOL=0 : A=0 : B=0 : C=0
9030 GET 1 : A=INSTR(R$,CHR$(227)) : A$=LEFT$(R$,A-1) : GOSUB 1400
9040 B=INSTR(A+1,R$,CHR$(227))
9050 C=B-(A+1) : IF C<1 THEN C=50:EOL=-1 '50 insures all rightmost characters
060 A$=MID$(R$,A+1,C) : IF EOL THEN 9080
9070 GOSUB 1400 : A=B : GOTO 9040
9080 CR=1 : GOSUB 1400 : NEXT : GOSUB 1400 : RETURN
10000            'Sysop's Utilities -------------------------------------------
10010 A$="Sysop's Utilities :":GOSUB 1400
10020 A$="  $  Type Comments":GOSUB 1400
10030 A$="  %  Type Callers":GOSUB 1400
10040 A$="  ^  Purge File":GOSUB 1400
10050 A$="  &  Renumber file":GOSUB 1400
10060 A$="  *  Resurrect a Msg":GOSUB 1400
10070 A$="  (  Print Msg Headers":CR=2:GOSUB 1400:RETURN
10100            '$ -----------------------------------------------------------
10110 FILE$="COMMENTS":GOSUB 6000:RETURN
10120            '% -----------------------------------------------------------
10130 FILE$="CALLERS":GOSUB 6000:RETURN
10200            'Purge -------------------------------------------------------
10210 CLOSE :NAME "MESSAGES" AS "MESSAGES.BAK" : Q=0 : B=0
10220 OPEN "R",#1,"MESSAGES.BAK":FIELD #1,128 AS R$
10230 OPEN "R",#2,"MESSAGES"    :FIELD #2,128 AS RR$
10240 GET 1
10250 IF INSTR(R$,CHR$(225))>0 THEN 10300
10260 IF INSTR(R$,CHR$(227))>0 THEN 10320
10270 IF INSTR(R$,CHR$(226))>0 THEN 10330
10280 GOSUB 1400:A$="# of Msgs Purged  :"+STR$(PG):GOSUB 1400
10285 A$="# of Bytes Purged :"+STR$((LOC(1)*128)-(LOC(2)*128)):GOSUB 1400
10290 A$="Re-Loading Msg File...":GOSUB 1400:ERASE M:GOSUB 100:RETURN 1200
10300 A=VAL(MID$(R$,118))
10310 A$="Msg #"+LEFT$(R$,5)+" copied...":GOSUB 1400
10320 LSET RR$=R$ : PUT 2 : GOTO 10240
10330 PG=PG+1 : A$="Msg #"+LEFT$(R$,5)+" purged..." : GOSUB 1400
10340 GET 1,LOC(1)+VAL(MID$(R$,118)) : GOTO 10250
10400            'Renumber ----------------------------------------------------
10450 A$="Renumber starting with OLD msg #":GOSUB 1500:MM=VAL(B$(1))
10460 IF MM<1 THEN 1450
10470 A$="Start with NEW #":GOSUB 1500:Y=VAL(B$(1)):YY=Y:IF Y<1 THEN 1460
10480 FOR Q=1 TO LASTR
10490 IF M(Q,2)=MM THEN R=M(Q,1) : GOTO 10510
10500 NEXT : A$="No Msg #"+STR$(MM) : GOSUB 1400 : RETURN
10510 GET 1,R
10520 RR=VAL(MID$(R$,118)) : IF RR<1 THEN 10290  'Done
10530 LSET R$=STR$(Y)+SPACE$(5-LEN(STR$(Y)))+MID$(R$,6)
10540 PUT 1,LOC(1)
10550 Y=Y+1 : R=R+RR : GOTO 10510
10600            'Resurrection ------------------------------------------------
10610 A$="Msg # to Resurrect":GOSUB 1500:MM=VAL(B$(1)):IF MM<1 THEN 1450
10620 R=1 : GOSUB 1400
10630 GET 1,R : RR=VAL(MID$(R$,118))
10635 IF RR<1 THEN A$="No Msg #"+STR$(MM) :GOSUB 1400 : RETURN
10640 IF VAL(LEFT$(R$,5))<>MM THEN R=R+RR : GOTO 10630
10650 IF INSTR(R$,CHR$(226))=0 THEN 10680
10660 LSET R$=LEFT$(R$,115)+CHR$(225)+MID$(R$,117) : PUT 1,LOC(1)
10670 A$="Msg #"+STR$(MM)+" is now alive and well." : GOSUB 1400 : GOTO 10290
10680 A$="Msg #"+STR$(MM)+" is not Dead." : GOSUB 1400 : RETURN
10800            'Print Msg Header --------------------------------------------
10810 R=1
10820 GET 1,R : RR=VAL(MID$(R$,118)) : IF RR<1 THEN RETURN
10830 A$=R$  : GOSUB 1400 : R=R+RR : GOTO 10820
12000            'Time -------------------------------------------------------
12010 GOSUB 1400
12040  H=VAL(LEFT$(TI$,2))  : M=VAL(MID$(TI$,4,2))  : S=VAL(MID$(TI$,7,2))
12050 HH=VAL(LEFT$(TIME$,2)):MM=VAL(MID$(TIME$,4,2)):SS=VAL(MID$(TIME$,7,2))
12060 IF S=<SS THEN SSS=SS-S ELSE SSS=60-(S-SS)
12070 IF M=<MM THEN MMM=MM-M ELSE MMM=60-(M-MM)
12080 IF H=<HH THEN HHH=HH-H ELSE HHH=24-(H-HH)
12090 IF HHH>12 THEN HHH=HHH-12:P$="PM" ELSE P$="AM"
12100 A$="It is now "+TIME$ : CR=2 : GOSUB 1400
12110 A$="You have been on for" : CR=1 : GOSUB 1400
12120 IF HHH>0 THEN A$=STR$(HHH)+" Hours" : CR=1 : GOSUB 1400
12130 A$=STR$(MMM)+" Minutes and "+STR$(SSS)+" Seconds.":CR=2:GOSUB 1400
12140 A$="Character count :  WHO CARES ?":CR=2:GOSUB 1400
12150 A$="Thanks for calling, "+FIRST$ : CR=2 : GOSUB 1400 : CLOSE #2,3
12160 IF HHH<1 OR SYSOP THEN 12180
12170 OPEN "A",#2,"LONGCALR":WRITE #2,NAM$,D$,HHH,MMM:CLOSE #2
12180 IF TRIES>5 THEN 200 ELSE RUN
12500           'Log-Off Weasels ---------------------------------------------
12510 GOSUB 1400 : A$="No one likes a wise-guy." : CR=2 : GOSUB 1400
12520 A$="You are no longer welcome here." : GOSUB 1400 : CLOSE #2,3 : GOTO 200
12530 GOSUB 1400 : A$="You are a Weasel." : CR=2 : GOSUB 1400 : GOTO 12520
13000            'Error Trapping ---------------------------------------------
13010 SOUND 2000,.5
13020 'PRINT "+++ Error";ERR;"  in line ";ERL
13025 IF ERL=238  THEN RESUME 238
13030 IF ERL=1220 THEN RESUME 1230
13035 IF ERL=1560 THEN CLOSE : RUN
13040 IF ERL=1840 THEN RESUME 1850
13060 IF ERL=2030 THEN ERASE A$:RESUME 2030
13070 IF ERL=2810 THEN ERASE C$:RESUME 2810
13080 IF ERL=3540 THEN RESUME 3550
13090 IF ERL=3730 THEN RESUME 3710
13100 IF ERL=3800 THEN RESUME 3810
13110 IF ERL=3850 THEN R$="":COL=0:RESUME 3700
13120 IF ERL=8100 THEN Z$="" : RESUME NEXT
13130 IF ERR=3    THEN RESUME 1200
13135 IF ERR=7    THEN RESUME NEXT
13140 A$="You have located a software bug." : GOSUB 1400
13150 A$="Please leave a comment or a msg for SYSOP that" : GOSUB 1400
13160 A$="Error "+STR$(ERR)+" occured in Line "+STR$(ERL) : GOSUB 1400
13170 A$="Thank You..." : GOSUB 1400 : PRINT : GOTO 1200
