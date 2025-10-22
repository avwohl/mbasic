5 '    :---------->> MINIRBBS v. 2.7   10/31/81 <<---------:
10 '   : MINIRBBBS  					   :
15 '   : Message Module of RBBS version 2.2		   :
20 '   : from Howard Moulton's original SJBBS (in Xitan    :
25 '   : Basic), converted to MBASIC and called RBBS or    :
30 '   : RIBBS by Bruce Ratoff, and extensively revised/   :
35 '   : expanded by Ron Fowler to become RBBS22.          :
40 '   :---------------------------------------------------:
45 '   : The Fowler version, RBBS22, was split into 2 mod- :
50 '   : ules, ENTERBBS and MINIRBBS, by Ben Bronson.      :
55 '   :---------------------------------------------------:
60 '   : Both were revised and given RBBS-compatible ver-  :
65 '   : sion nos. in 3/81 by Tim Nicholas, to incorporate :
70 '   : updates from his version 2.4 of RBBS              :
75 '   :---------------------------------------------------:
80 '   : Bill Earnest's bell-at-line-end routine was added :
85 '   : from RBBS 2.5 (see lines 26000+), and the 'G'     :
90 '   : command changed to be compatible with MINICBBS--  :
95 '   : Now both 'G' & 'C' return the caller to CP/M      :
100 '  : and don't sign him off.  The RBBS22/24 line       :
105 '  : numbering has been preserved to facilitate adding :
110 '  : further changes     --Ben Bronson, 3/26           :
115 '  :---------------------------------------------------:
120 '  :(a) Lines 760 & 770 removed to stop double-counting: 
125 '  : of callers. (b) Comment-leaving routine no longer :
130 '  : says "Thanks for the comment" when you didn't     :
135 '  : leave one. 		--BB 4/2		   :
145 '  :---------------------------------------------------:
150 '  * Note that most lines are numbered in conformity   *
155 '  * with the line numbers of versions 24, 25, & 24    *
160 '  * to make it easier to pull routines out and insert *
165 '  * them into customized programs.                    *
170 '  -----------------------------------------------------
175 '  - Features & ideas added to version 26 come from Bill
180 '  - Earnest, Jim C., Hank Szyszka, Chuck Witbeck, Earl
185 '  - Bockenfeld, Brian Kantor, & Skip Hansen
190 '  -----------------------------------------------------
195 '  
200 '  - experimental addition of WDE features @ lines
205 '    6240-8020 (?), 12000, 1020-1195, & 26000->  BB, 06/14
210 '
215 '  - Lines 1000- altered to accept P$ info.  M, U, & O
220 '  - now only usable by sysops or other P$<>RG or NW people.
225 '  - (ENTBBS27 puts P$ and DT$ into LASTCALR & passes them
230 '  - here as key to privileged user routines)
235 ' 
240 '  - Put in auto date entry routines from WDE 
245 '  - Read-SURVEY.BBS stuff from BK added, for privileged users only
250 '    
255 '  - Time stuff from HS inserted, 10/02/81.
256 '  - B command added; also minor cosmetic improvements. 10/14/81
260 '  - Howard Booker's fix at lines 6340 & 13030 added 10/31/81
261 '  --------------------------------------------------------------
262 ' NOTE: Line 13030 contains a port address that has to be
263 ' configured to your system.  As the program will run without
264 ' this routine, it has been disabled in the distribution version
265 ' of RBBMIN27.  But it'll run better if you use the routine.)
265 '  ---------------------------------------------------------------
270 ' NOTE that time routine at 44000 (and the 'T' command) are set up
275 ' for a Mountain Hardware clock at ports 32-47.  These will have
280 ' to be either deleted or changed to run with your system clock.
290 '
300 DEFINT A-Z
330 VERS$="(MINIRBBS vers 2.7)"
340 DIM A$(19),M(200,2),H(6),HT(6),HD(6)
350 POKE 0,&HCD     'To disable ^C
360 INC=1: ERS$=CHR$(8)+" "+CHR$(8)
370 ON ERROR GOTO 15000
379 '
380 ' Signon functions...
381 '
400 MSGS=1:CALLS=MSGS+1:MNUM=CALLS+1
420 BK=0:GOSUB 13020:N=1:A$="Hyde Park/Chicago Remote CP/M Message Subsystem......":N=0:GOSUB 13020
460 BEL=-1:XPR=0'INITIAL BEL ON, NOT EXPERT
470 A$=VERS$:GOSUB 13020
480 SAV$=""
500 INC=0
507 '
508 ' Get name, status & date from LASTCALR
509 '
510 OPEN "I",1,"A:LASTCALR":INPUT #1,N$,O$,F$,DT$:CLOSE
740 BK=0:GOSUB 13020:A$="Active # of msg's: ":N=1:GOSUB 13020
745 OPEN "R",1,"A:COUNTERS",5:FIELD#1,5 AS RR$:GET#1,MSGS:M=VAL(RR$)
750 A$=STR$(M):GOSUB 13020
760 A$="You are caller # : ":N=1:GOSUB 13020:GET#1,CALLS
770 CN=VAL(RR$)+INC:A$=STR$(CN):LSET RR$=A$:GOSUB 13020:PUT#1,CALLS
780 A$="Next msg # will be:":N=1:GOSUB 13020:GET#1,MNUM:U=VAL(RR$)
790 A$=STR$(U+1):GOSUB 13020:CLOSE:GOSUB 13020
800 '
810 '  Look for messages for this caller
820 ' 
840 FT=1:MX=0:MZ=0:IU=0:'FLAG FIRST TIME FOR PRINTING HEADING
850 OPEN "R",1,"A:SUMMARY",30:RE=1:FIELD#1,28 AS RR$
860 BK=0:GET#1,RE:IF EOF(1) THEN 960
870 G=VAL(RR$):MZ=MZ+1:M(MZ,1)=G:IF G=0 THEN 950
880 IF IU=0 THEN IU=G
890 IF G>9998 THEN MZ=MZ-1:GOTO 960
900 GET#1,RE+3:GOSUB 16500:IF INSTR(S$,N$)>0 AND INSTR(S$,O$)>0 THEN 930
905 IF N$="XXXXX" THEN N$="SYSOP"
910 IF N$<>"SYSOP" THEN 950
920 IF INSTR(S$,"BEN")=0 THEN 950
930 IF FT THEN A$="The following message(s) was/were left for you.":GOSUB 13020
935 IF FT THEN A$="Please kill the ones that would not interest other callers.":FT=0:GOSUB 13020:GOSUB 13020
940 A$=STR$(G):N=1:GOSUB 13020
950 GET#1,RE+5:M(MZ,2)=VAL(RR$):MX=MX+M(MZ,2)+6:RE=RE+6:GOTO 860
960 CLOSE:GOSUB 13020:GOSUB 13020
970 IF N$="SYSOP" THEN N$="XXXXX"
1000 '
1020 '    *** Main Command Acceptor/Dispatcher ***
1025 '
1030 '  (Lines 1176-1198 deal with privileged (SP) user functions &
1035 '   with keeping them away from non-privileged (RG & NW) users
1040 '
1060 A1$="Function":IF NOT XPR THEN A1$=A1$+" [E,R,S,K,C,G,P,X,Q,T,B (or '?' if not known)]":
1080 A1$=A1$+"?":GOSUB 13020:C=1:GOSUB 13260:C=0
1100 IF B$="" THEN 1180
1120 FF=INSTR("ER?SKCGPXQTB",B$):GOSUB 1140:GOTO 1000
1140 IF FF=0 THEN 1175
1160 ON FF GOTO 6000,8000,5000,18060,11000,10000,2000,
     17040,17000,18080,44000,22500
1175 IF N$+O$="XXXXX" THEN 1190
1176 IF F$<>"SP" THEN 1200 ELSE 1190
1180 IF F$="RG" THEN 1000   '<CR> brings all except SP back to main menu
1181 IF F$="NW" THEN 1000   'ditto
1184 A1$="Or one of the additional functions for special users (O,M,U,Z) (or ? if not known)":
1186 A1$=A1$+"?":GOSUB 13020:C=1:GOSUB 13260:C=0
1188 IF B$="?" THEN GOSUB 23500:GOTO 1000
1190 IF B$="O" THEN GOSUB 19000:GOTO 1000
1192 IF B$="M" THEN GOSUB 27000:GOTO 1000
1194 IF N$+O$="XXXXX" THEN IF B$="9" THEN GOSUB 22000:GOTO 1000
1196 IF B$="U" THEN GOSUB 12000:GOTO 1000
1197 IF B$="Z" THEN GOSUB 23000
1198 GOTO 1000
1200 A$="I don't understand '"+B$+"', "+N$+".":GOSUB 13020:GOSUB 13020:
     SAV$="":RETURN
1201 GOTO 1000
2000 '
2020 '   Exit to CP/M
2220 ' 
2230 GOSUB 13020:GOTO 10265
2237 GOSUB 44000
2240 GOSUB 13020:POKE 4,0:A$="Now, back to CP/M...":GOSUB 13020:POKE 0,&HC3:SYSTEM
3000 '
5000 '
5020 ' *** Display Menu of Functions ***
5040 '
5060 GOSUB 13020:A$="Functions supported:":GOSUB 13020:IF BK THEN RETURN
5080 A$="S--> Scan messages      R--> Retrieve message":GOSUB 13020:
     IF BK THEN RETURN
5100 A$="E--> Enter message      K--> Kill message":GOSUB 13020:IF BK THEN RETURN
5120 A$="P--> Prompt (bel) togl  X--> eXpert user mode":GOSUB 13020:IF BK THEN RETURN
5140 A$="Q--> Quick summary      C--> Comment before exit to CP/M":GOSUB 13020:IF BK THEN RETURN
5160 A$="G--> Go direct to C/PM  T--> Time on system":GOSUB 13020:IF BK THEN RETURN
5180 A$="B--> Read bulletin on latest software":
5195 GOSUB 13020:IF BK THEN RETURN
5200 GOSUB 13020:A$="Commands may be strung together, separated by semicolons.":GOSUB 13020:
5205 A$="For example, 'R;123' retrieves message # 123.":GOSUB 13020:IF BK THEN RETURN
5210 A$="For forward sequential retrieval, use  '+' after Msg #.":GOSUB 13020:GOSUB 13020
5280 GOSUB 13020:RETURN
6000 '  Date-entry routine for sysop (who may not pass thru ENTERBBS)
6010 IF N$<>"XXXXX" THEN 6060
6015 GOSUB 13020:A1$="Todays date (MM/DD/YY)?":GOSUB 13020:GOSUB 13260:DT$=B$
6019 '
6020 '  Enter a new message
6040 '
6060 F=0:GOSUB 13020:OPEN "R",1,"A:COUNTERS",5:A$="Msg # will be: ":N=1:GOSUB 13020:FIELD#1,5 AS RR$:GET#1,MNUM:V=VAL(RR$)
6080 A$=STR$(V+1):GOSUB 13020:CLOSE
6089 '  ** Read date from LASTCALR
6100 GOSUB 13020: A$="Today is "+DT$:GOSUB 13020
6120 A1$="Who to (C/R for ALL)?":GOSUB 13020:C=1:GOSUB 13260:C=0:IF B$="" THEN T$="ALL" ELSE T$=B$
6130 ' --- RBBS25 routine substituted here ---
6140 A1$="Subject (26 chars. max.):":GOSUB 13020:C=1:GOSUB 13260:C=0:K$=B$
6150 IF LEN(K$)>30 THEN GOTO 6140
6160 A1$="Password?":GOSUB 13020:C=1:GOSUB 13260:C=0:PW$=B$:GOSUB 13020
6170 A1$="Type in up to 16 lines.  A bell sounds near the end of each.":GOSUB 13020
6180 A1$="To edit or end, hit 2 C/Rs.  Don't use semicolons.":GOSUB 13020:GOSUB 13020:F=0
6185 A1$=STRING$(62,45):A1$="  |"+A1$+"|":GOSUB 13020
6190 IF F=16 THEN A$="Msg full.":GOSUB 13020:GOTO 6240
6200 F=F+1:A1$=STR$(F)+" ":N=1:GOSUB 13020:GOSUB 13260:IF B$="" THEN F=F-1:GOTO 6240
6205 IF F=13 THEN PRINT "(3 lines left. . . .)"
6215 IF F=15 THEN PRINT "(Last line. . . .)"
6220 A$(F)=B$+" ":GOTO 6190
6240 GOSUB 13020:A1$="Choose: (L)ist, (E)dit, (A)bort, (C)ontinue, or (S)ave -- ":IF XPR THEN A1$="L,E,A,C,S: ?"
6260 GOSUB 13020:C=1:GOSUB 13260:C=0
6271 '  WDE edit routines begin here
6280 IF B$<>"L" THEN 6360
6290 GOSUB 12220
6300 GOSUB 13020:FOR L=1 TO F:A$=STR$(L)+" "+A$(L)
6320 IF BK THEN 6240 ELSE GOSUB 13020:NEXT L
6340 GOSUB 13020:CLOSE:GOTO 6240    'this CLOSE is from HB's FIX file
6360 IF B$="A" THEN A$="Aborted":GOSUB 13020:RETURN
6380 IF B$="C" AND FM=0 THEN 6190
6400 IF B$="E" THEN 6460    ' Note that EDIT only works after compiling
6420 IF B$="S" AND FM=0 THEN 6560
6430 IF B$="S" AND FM=1 THEN 27150
6440 GOTO 6240
6460 GOSUB 13020:A1$="Line #?":GOSUB 13020:GOSUB 13260:L=VAL(B$)
6480 IF L=0 OR L>F THEN 6240 ELSE A$="Was:":GOSUB 13020:A$=A$(L):GOSUB 13020
6500 A1$="Enter new line":IF NOT XPR THEN A1$=A1$+" (C/R for no change)"
6501 GOSUB 13020:A1$="or  /oldstring/newstring/  to substitute"
6520 A1$=A1$+":":GOSUB 13020:GOSUB 13260
6521 IF LEFT$(B$,1)="/" THEN 6541
6540 IF B$="" THEN 6240 ELSE A$(L)=B$+" ":GOTO 6480
6541 IF RIGHT$(B$,1)="/" THEN B$=LEFT$(B$,LEN(B$)-1)
6542 B$=MID$(B$,2,99)
6543 FOR Q=LEN(B$) TO 1 STEP -1
6544 IF MID$(B$,Q,1)="/" THEN FROM$=LEFT$(B$,Q-1):TO$=MID$(B$,Q+1,99)
6545 NEXT Q:TEMP$=A$(L)
6546 FOR Q=1 TO LEN(TEMP$)-LEN(FROM$)+1
6547 IF MID$(TEMP$,Q,LEN(FROM$))=FROM$ THEN 6550
6548 NEXT Q: A1$="String not found!":GOSUB 13020:GOTO 6480
6550 A$(L)=""
6551 IF Q<>1 THEN A$(L)=LEFT$(TEMP$,Q-1)
6552 A$(L)=A$(L)+TO$+MID$(TEMP$,Q+LEN(FROM$),99): GOTO 6480
6560 '
6580 IF PW$<>"" THEN PW$=";"+PW$
6600 A$="Updating summary file, ":N=1:GOSUB 13020
6620 OPEN "R",1,"A:SUMMARY",30:RE=1:FIELD#1,30 AS RR$:RL=30
6640 RE=MZ*6+1:S$=STR$(V+1)+PW$:GOSUB 16000:PUT#1,RE
6660 RE=RE+1:S$=DT$:GOSUB 16000:PUT#1,RE
6668 IF N$="XXXXX" THEN N$="SYSOP"
6680 RE=RE+1:S$=N$+" "+O$:GOSUB 16000:PUT#1,RE
6682 IF N$="SYSOP" THEN N$="XXXXX"
6700 RE=RE+1:S$=T$:GOSUB 16000:PUT#1,RE
6720 RE=RE+1:S$=K$:GOSUB 16000:PUT#1,RE
6740 RE=RE+1:S$=STR$(F):GOSUB 16000:PUT#1,RE
6760 RE=RE+1:S$=" 9999":GOSUB 16000:PUT#1,RE
6780 CLOSE#1
6800 A$="next msg #, ":N=1:GOSUB 13020:OPEN "R",1,"A:COUNTERS",5:FIELD#1,5 AS RR$
6820 GET#1,MNUM:LSET RR$=STR$(VAL(RR$)+1):PUT#1,MNUM
6840 A$="active msg's, ":N=1:GOSUB 13020
6860 GET#1,MSGS:LSET RR$=STR$(VAL(RR$)+1):PUT#1,MSGS:CLOSE#1
6880 A$="and msg file.":N=1:GOSUB 13020:OPEN "R",1,"A:MESSAGES",65:RL=65
6900 FIELD#1,65 AS RR$
6920 RE=MX+1
6940 S$=STR$(V+1)+PW$:GOSUB 16000:PUT#1,RE
6960 RE=RE+1:S$=DT$:GOSUB 16000:PUT#1,RE
6978 IF N$="XXXXX" THEN N$="SYSOP"
6980 RE=RE+1:S$=N$+" "+O$:GOSUB 16000:PUT#1,RE
6982 IF N$="SYSOP" THEN N$="XXXXX"
7000 RE=RE+1:S$=T$:GOSUB 16000:PUT#1,RE
7020 RE=RE+1:S$=K$:GOSUB 16000:PUT#1,RE
7040 RE=RE+1:S$=STR$(F):GOSUB 16000:PUT#1,RE
7060 RE=RE+1
7080 FOR P=1 TO F:S$=A$(P):GOSUB 16000:PUT#1,RE:RE=RE+1:NEXT P
7090 S$=" 9999":GOSUB 16000:PUT#1,RE:CLOSE#1:MX=MX+F+6:MZ=MZ+1:M(MZ,1)=V+1:M(MZ,2)=F
7100 GOSUB 13020:GOSUB 13020:U=U+1:RETURN
7200 RETURN
8000 '
8020 '  Retrieve a message
8040 '
8060 GOSUB 13020:A1$="MSG # ("+STR$(IU)+" -"+STR$(U)+" )":IF NOT XPR THEN A1$=A1$+" to retrieve (C/R to end)"
8080 A1$=A1$+"?":GOSUB 13020:GOSUB 13260:GOSUB 13020
8100 IF LEN(B$)=0 THEN M=0 ELSE M=VAL(B$)
8120 IF M<1 THEN GOSUB 13020:RETURN
8140 IF M>U THEN A$="There aren't that many msg's, "+N$+".":GOSUB 13020:SAV$="":GOTO 8060
8160 GOSUB 12220:GOSUB 13020
8180 OPEN "R",1,"A:MESSAGES",65:RE=1:FIELD#1,64 AS RR$:MI=0
8200 MI=MI+1:IF (MI>MZ) OR BK THEN 8540 ELSE G=M(MI,1)
8220 IF G<M THEN RE=RE+M(MI,2)+6:GOTO 8200
8240 IF G>M THEN 8480
8260 GOSUB 19100:IF OK THEN 8280 ELSE RE=RE+M(MI,2):GOTO 8200
8280 RE=RE+1:GET#1,RE:GOSUB 16500:D$=S$
8300 RE=RE+1:GET#1,RE:GOSUB 16500:NO$=S$
8320 RE=RE+1:GET#1,RE:GOSUB 16500:T$=S$
8340 RE=RE+1:GET#1,RE:GOSUB 16500:GOSUB 19200:K$=S$
8360 RE=RE+1:GET#1,RE:J=VAL(RR$):GOSUB 13020
8380 A$="Msg # "+STR$(G)+"  Date entered: "+D$+"  From: "+NO$:GOSUB 13020
8400 A$="To: "+T$+"  About: "+K$:GOSUB 13020:GOSUB 13020
8420 RE=RE+1:FOR P=1 TO J:GET#1,RE:GOSUB 16500:A$=S$:GOSUB 13020
8440 IF BK THEN 8540
8460 RE=RE+1:NEXT P:GOSUB 13020
8480 IF RIGHT$(B$,1)<>"+" THEN CLOSE:GOTO 8020
8500 M=M+1:MI=0:RE=1
8520 IF M<=U AND NOT BK THEN 8200
8540 CLOSE:A$="** End of messages **":GOSUB 13020:GOSUB 13020:D$="":NO$="":RETURN
9000 '
9020 '   Summarize messages
9040 '  (common code for S and Q commands)
9060 '
9080 GOSUB 13020
9090 A1$="Msg # ("+STR$(IU)+" -"+STR$(U)+" ) to start (C/R to end)?"
9095 GOSUB 13020:C=1:GOSUB 13260:C=0:GOSUB 13020 
9100 IF LEN(B$)=0 THEN M=0 ELSE M=VAL(B$):GOSUB 13220
9120 IP=INSTR(B$,","):IF IP>0 THEN B$=MID$(B$,IP+1) ELSE ST=0:GOTO 9220
9140 IF LEN(B$)<3 THEN RETURN
9160 IF MID$(B$,2,1)<>"=" THEN RETURN
9180 SV$=MID$(B$,3):B$=LEFT$(B$,1):ST=INSTR("FTS",B$)
9200 IF ST=0 THEN RETURN
9220 IF M<1 THEN RETURN
9240 IF M>U THEN A$="There ain't that many msg's, "+N$+".":GOSUB 13020:SAV$="":RETURN
9260 IF NOT QU THEN GOSUB 12220:GOSUB 13020
9280 OPEN "R",1,"A:SUMMARY",30:RE=1:FIELD #1,28 AS RR$
9300 GET #1,RE
9320 IF EOF(1) OR BK THEN 9660 ELSE G=VAL(RR$)
9340 IF G>9998 THEN 9660
9360 IF G<M THEN RE=RE+6:GOTO 9300
9380 GOSUB 19100:IF OK THEN 9400 ELSE RE=RE+6:GOTO 9300
9400 GET #1,RE+ST+1:IF ST=0 THEN 9420 ELSE GOSUB 16500:IF INSTR(S$,SV$)=0 THEN RE=RE+6:GOTO 9300
9420 IF NOT QU THEN 9500
9430 '
9440 '  Quick summary only
9450 '
9460 GET #1,RE+4:GOSUB 16500:GOSUB 19200:A$=SPACE$(4-LEN(STR$(G)))+STR$(G)+" "+S$:GOSUB 13020
9480 IF U=G OR BK THEN 9660 ELSE RE=RE+6:GOTO 9300
9500 ' full summary
9501 ' Routine changed to print info on 2 instead of 4 lines --BB
9502 '
9520 RE=RE+1:GET#1,RE:GOSUB 16500:D$=S$
9540 RE=RE+1:GET#1,RE:GOSUB 16500:NO$=S$
9560 RE=RE+1:GET#1,RE:GOSUB 16500:T$=S$
9580 RE=RE+1:GET#1,RE:GOSUB 16500:GOSUB 19200:K$=S$
9600 RE=RE+1:GET#1,RE:GOSUB 16500:SZ$=S$
9610 ZS$=SZ$
9620 A$="#"+STR$(G)+" ="+ZS$+" lines, dated "+D$+"  From: "+NO$:GOSUB 13020
9630 A$="To: "+T$+"   Re: "+K$:GOSUB 13020
9640 GOSUB 13020:IF U=G OR BK THEN 9660 ELSE RE=RE+1:GOTO 9300
9660 GOSUB 13020:A$="** End of summary **":GOSUB 13020:GOSUB 13020:GOSUB 13020:CLOSE:RETURN
10000 '
10020 '  The goodbye routine (exit to CP/M is back at 2237)
10040 '
10055 GOSUB 13020:GOSUB 13020
10060 A$="'Comments' are not readable to anyone except the SYSOP...":GOSUB 13020
10065 A1$=" Want to leave any?":GOSUB 13020:C=1:GOSUB 13260:C=0
10070 IF LEFT$(B$,1)="N" THEN 10260
10080 IF LEFT$(B$,1)<>"Y" THEN 10060
10100 OPEN "R",1,"A:COMMENTS",65:FIELD#1,65 AS RR$:GET#1,1:RE=VAL(RR$)+1:RL=65
10120 IF RE=1 THEN RE=2
10140 S$="From: "+N$+" "+O$:GOSUB 16000
10160 PUT#1,RE
10180 A$=" Enter comments, C/R to end:  (16 lines max)":GOSUB 13020
10200 A$="-->":N=1:GOSUB 13020:GOSUB 13260
10220 IF B$="" THEN 10240 ELSE RE=RE+1:S$=B$:RL=65:GOSUB 16000:PUT#1,RE:GOTO 10200
10240 S$=STR$(RE):RL=65:GOSUB 16000:PUT#1,1:CLOSE
10250 GOSUB 13020
10251 A$="Many thanks for the comment, "+N$+".":GOSUB 13020:GOTO 10265
10260 GOSUB 13020:A$=" No comment, then.":GOSUB 13020
10265 GOSUB 13020:A$=" Character count:  "+STR$(A)+" typed by system - "+STR$(D)+ " typed by you.":GOSUB 13020
10280 GOSUB 13020:GOSUB 13020:GOTO 2237
10285 '  
10286 ' (note: to have the 'G' command disconnect rather than return the
10287 '  the user to CP/M, delete the above GOTO 2237 and restore the
10288 '  following lines, using the port number for your own modem)
10290 '  
10295 ' OUT 53,37  ' turn off DTR bit in modem control port.
10296 ' POKE &H0,&HC3:SYSTEM ' restore jump at BASE, RET to OS.
11000 '
11020 '  Routine to kill a message
11040 '
11060 GOSUB 13020:A1$="Message # to kill?":GOSUB 13020:GOSUB 13260
11080 IF LEN(B$)=0 THEN M=0 ELSE M=VAL(B$)
11100 IF M<1 THEN GOSUB 13020:RETURN
11120 IF M>U THEN A$="There aren't that many msg's, "+N$+".":GOSUB 13020:SAV$="":GOTO 11040
11140 A$="Scanning summary file....":GOSUB 13020:OPEN "R",1,"A:SUMMARY",30:RE=1:FIELD#1,30 AS RR$:RL=30
11160 GET#1,RE
11180 IF EOF(1) THEN 11520 ELSE G=VAL(RR$)
11200 IF G>9998 THEN 11520
11220 IF G<M THEN RE=RE+6:GOTO 11160
11240 IF G>M THEN 11520
11260 GOSUB 19100:IF NOT OK THEN 11520
11280 GOSUB 16500:PW=INSTR(S$,";"):PW$=""
11300 IF PW=0 OR N$+O$="XXXXX" OR PERS THEN PERS=0:GOTO 11340
11320 PW$=MID$(S$,PW+1)
11330 A1$="Password ?":GOSUB 13020:C=1:GOSUB 13260:C=0:IF B$<>PW$ THEN A$="Incorrect.":GOSUB 13020:GOSUB 13020:CLOSE:RETURN
11340 S$=" 0"+":"+STR$(G):GOSUB 16000:PUT#1,RE:CLOSE
11360 A$="Updating message file....":GOSUB 13020
11380 OPEN "R",1,"A:MESSAGES",65:RE=1:FIELD#1,65 AS RR$:MI=0
11400 MI=MI+1:IF MI>MZ THEN 11520 ELSE G=M(MI,1)
11420 IF G<M THEN RE=RE+M(MI,2)+6:GOTO 11400
11440 IF G=M THEN S$="0"+":"+STR$(G)+":"+N$+","+O$:RL=65:GOSUB 16000:PUT#1,RE:M(MI,1)=0
11460 CLOSE#1:A$="Updating message count...":GOSUB 13020
11480 OPEN "R",1,"A:COUNTERS",5:FIELD#1,5 AS RR$:GET#1,MSGS:LSET RR$=STR$(VAL(RR$)-1):PUT#1,MSGS:CLOSE
11500 GOSUB 13020:A$="Message killed.":GOSUB 13020:GOSUB 13020:RETURN
11520 CLOSE:A$="Message not found.":GOSUB 13020:GOSUB 13020:RETURN
12000 '
12020 GOSUB 13020:A$="The (U)SERS File (a sysops-only command)--":GOSUB 13020
12040 A$="    [use ^K when you've seen enough]":GOSUB 13020
12060 OPEN "R",1,"A:USERS",62:FIELD#1,62 AS RR$:FIELD#1,10 AS NN$
12070 GET#1,1:NU=VAL(NN$)
12080 FOR I=NU+1 TO 2 STEP -1: GET#1,I:GOSUB 16500:A$=S$:GOSUB 13020
12100 IF BK THEN 12140
12120 NEXT I
12140 CLOSE: GOSUB 13020: RETURN
12160 '
12180 '  Print control-char info
12200 '
12220 GOSUB 13020
13000 A$="Use Ctl-S to Pause, Repeated Ctl-K's to Abort."
13020 '
13026 ' In the following lines, substitute the &HC1 and &H01 for your
13027 ' modem and keyboard data input ports respectively 
13028 ' (REMOVE THE ' IN THE NEXT 2 LINES IF YOU WANT TO USE THEM)
13029 '
13030 ' IF INP(&HC1) AND 127=11 THEN BK=-1    'here, the PMMI data port
13032 ' IF INP(&H01) AND 127=11 THEN BK=-1
13033 '
13040 '  Print string from A$ on console
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
13280 '  Accept string into B$ from console 
13300 '
13320 IF BEL AND SAV$="" THEN PRINT CHR$(7);
13340 B$="":BK=0
13360 IF SAV$="" THEN GOSUB 26000
13380 SP=INSTR(SAV$,";"):IF SP=0 THEN B$=SAV$:SAV$="":GOTO 13420
13400 B$=LEFT$(SAV$,SP-1):SAV$=MID$(SAV$,SP+1)
13420 IF LEN(B$)=0 THEN RETURN
13440 IF C=0 THEN 13480
13460 FOR ZZ=1 TO LEN(B$):MID$(B$,ZZ,1)=CHR$(ASC(MID$(B$,ZZ,1))+32*(ASC(MID$(B$,ZZ,1))>96)):NEXT ZZ
13480 IF LEN(B$)<63 THEN 13580
13500 A$="Input line too long - would be truncated to:":GOSUB 13020
13520 B$=LEFT$(B$,62):PRINT B$
13540 LINE INPUT "Retype line (Y/N)?";QQ$:QQ$=LEFT$(QQ$,1)
13560 IF QQ$="Y" OR QQ$="y" THEN PRINT PP$;:SAV$="":GOTO 13260
13580 D=D+LEN(B$):RETURN
13600 RETURN
15000 ' ***ON ERROR HANDLER***
15020 IF ERL=18030 THEN RESUME 18050
15040 IF ERL=740 THEN M=0:RESUME 750
15050 IF ERL=760 THEN C=0:RESUME 770
15060 IF ERL=780 THEN U=0:RESUME 790
15070 IF ERL=6060 THEN V=0:RESUME 6080
15080 IF ERL=6800 THEN C=0:RESUME 6820
15090 IF ERL=6840 THEN C=0:RESUME 6860
15100 RESUME NEXT
16000 '
16010 ' Fill and store disk record
16020 '
16030 LSET RR$=LEFT$(S$+SPACE$(RL-2),RL-2)+CHR$(13)+CHR$(10)
16040 RETURN
16500 '
16510 ' Unpack disk record
16520 '
16530 ZZ=LEN(RR$)-2
16540 WHILE MID$(RR$,ZZ,1)=" "
16550 ZZ=ZZ-1:IF ZZ=1 THEN 16570
16560 WEND
16570 S$=LEFT$(RR$,ZZ)
16580 IF MID$(S$,ZZ,1)="?" THEN S$=S$+" "
16590 RETURN
17000 '
17010 ' *** Toggle EXPERT USER mode
17020 '
17030 XPR=NOT XPR:RETURN
17040 '
17050 ' *** Toggle BELL prompt
17060 '
17070 BEL=NOT BEL:RETURN
18000 '
18010 ' Subroutine to print a file
18020 '
18030 OPEN "I",1,"A:"+FIL$:BK=0
18040 IF EOF(1) OR BK THEN 18050 ELSE LINE INPUT #1,A$:GOSUB 13020:GOTO 18040
18050 CLOSE #1:RETURN
18060 ' FULL SUMMARY
18070 QU=0:GOSUB 9000:RETURN
18080 ' QUICK SUMMARY
18090 QU=-1:GOSUB 9000:RETURN
19000 GOSUB 13020:A$="The (O)THER CALLERS File (a sysops-only command)--":GOSUB 13020
19010 GOSUB 13020
19020 IF F$="RG" THEN 1200' IF NOT SYSOP, SAY "I DON'T UNDERSTAND".
19030 OPEN "R",1,"A:CALLERS",60:FIELD #1,60 AS RR$:GET #1,1:SIZ=VAL(RR$)
19040 CA=CN
19050 FOR CNT=SIZ+1 TO 2 STEP -1
19060 GET #1,CNT:GOSUB 16500:A$=SPACE$(5-LEN(STR$(CA)))+STR$(CA)+" "+S$:GOSUB 13020:IF BK THEN 19090
19070 CA=CA-1
19080 NEXT CNT
19090 CLOSE:A$= "END OF CALLERS.":GOSUB 13020:GOSUB 13020:RETURN
19100 ' TEST FOR PERSONAL MESSAGES
19110 PERS=0:OK=-1:GET #1,RE:IF INSTR(RR$,";*")=0 THEN 19160
19120 PERS=-1
19130 IF N$+O$="XXXXX" THEN 19160
19140 GET #1,RE+3:GOSUB 19170:IF OK THEN 19160
19150 GET #1,RE+2:GOSUB 19170
19160 RETURN
19170 ' TEST 'FROM' OR 'TO' FIELD FOR USER'S NAME
19180 IF INSTR(RR$,N$)>0 AND I
19150 GET #1,RE+2:GOSUB 19170
19160 RETURN
19170 ' TEST 'FROM' OR 'TO' FIELD FOR USER'S NAME
19180 IF INSTR(RR$,N$)>0 AND INSTR(RR$,O$)>0 THEN OK=-1 ELSE OK=0
19190 RETURN
19200 IF PERS THEN S$="("+S$:S$=S$+")":PERS=0
19210 RETURN
22000 '  Subroutine to print COMMENTS file (for sysop only)
22020 '
22030 OPEN "I",1,"A:COMMENTS":BK=0
22040 IF EOF(1) OR BK THEN 22050 ELSE LINE INPUT #1,A$:GOSUB 13020:GOTO 22040
22050 CLOSE #1:A$="End of comments.":GOSUB 13020:GOSUB 13020:RETURN
22500 '  Subroutine to print BULLETIN (new programs) file...
22510 '
22520 OPEN "I",1,"A:BULLETIN":BK=0
22540 IF EOF(1) OR BK THEN 22560 ELSE LINE INPUT #1,A$:GOSUB 13020:GOTO 22540
22560 CLOSE #1:A$="End of New Program Bulletin":GOSUB 13020:GOSUB 13020:RETURN
23000 '  Subroutine to print SURVEY.BBS file for special users
23010 '
23030 OPEN "I",1,"A:SURVEY.BBS":BK=0
23040 IF EOF(1) OR BK THEN 23050 ELSE LINE INPUT #1,A$:GOSUB 13020:GOTO 23040
23050 CLOSE #1:A$="End of the survey data currently on this disk.":GOSUB 13020:GOSUB 13020:RETURN
23060 '
23500 '  Sub. for special user command menu
23510 GOSUB 13020:A$="Special Users can also use these commands:":GOSUB 13020:GOSUB 13020
23520 A$=" M = alter old MESSAGE     O = view OTHER CALLERS file":GOSUB 13020
23540 A$=" U = view USERS file       Z = view USER SURVEY file":GOSUB 13020:GOSUB 13020
23560 A$=" [note that USERS is very long.  Be prepared to use":GOSUB 13020
23580 A$="  ^K to exit from it.  And M will not allow changes":GOSUB 13020
23600 A$="  that mean adding extra lines to old messages...]":GOSUB 13020:GOSUB 13020
23620 RETURN
25999 '  Subroutine to replace LPRINT & make line-end bell
26000 CHC=0: SAV$=""
26010 NCH=ASC(INPUT$(1))
26020 IF NCH=127 THEN 26080
26030 IF NCH<32 THEN 26110
26040 IF CHC>=63 THEN 26010
26050 SAV$=SAV$+CHR$(NCH): CHC=CHC+1: PRINT CHR$(NCH);
26060 IF CHC=55 THEN PRINT CHR$(7);
26070 GOTO 26010
26080 IF CHC=0 THEN 26010 ELSE PRINT RIGHT$(SAV$,1);: GOTO 26100
26090 IF CHC=0 THEN 26010 ELSE PRINT ERS$;
26100 CHC=CHC-1: SAV$=LEFT$(SAV$,CHC): GOTO 26010
26110 IF NCH=8 THEN 26090
26120 IF NCH=13 THEN PRINT: RETURN
26130 IF NCH=21 THEN PRINT " #": GOTO 26000
26140 IF NCH<>24 OR CHC=0 THEN 26010
26150 FOR BCC=1 TO CHC: PRINT ERS$;: NEXT BCC: GOTO 26000
27000 GOSUB 13020:A$="Old message-modifying function, currently available only for sysops.":GOSUB 13020
27005 GOSUB 13020:A1$="MSG # TO MODIFY?":GOSUB 13020:GOSUB 13260:GOSUB 13020
27007 IF B$="" THEN 1000
27010 IF LEN(B$)=0 THEN M=0 ELSE M=VAL(B$)
27020 IF M<1 THEN GOSUB 13020:RETURN
27030 IF M>U THEN A$="There aren't that many msgs, "+N$+".":GOSUB 13020:
SAV$="":GOTO 27000
27040 GOSUB 13020
27050 OPEN "R",1,"A:MESSAGES",65:RE=1:FIELD#1,64 AS RR$:MI=0
27060 MI=MI+1:IF (MI>MZ) OR BK THEN GOTO 27090 ELSE G=M(MI,1)
27070 IF G<M THEN RE=RE+M(MI,2)+6:GOTO 27060
27080 IF G=M THEN 27100
27090 CLOSE: RETURN
27100 GOSUB 19100:IF NOT OK THEN RE=RE+M(MI,2):GOTO 27060
27101 GOSUB 16500:PW=INSTR(S$,";"):PW$=""
27102 IF PW=0 OR N$+O$="SYSOP" OR PERS THEN PERS=0:GOTO 27110
27103 PW$=MID$(S$,PW+1):A1$="Password ?":GOSUB 13020:C=1:GOSUB 13260:C=0
27104 IF B$<>PW$ THEN A$="Incorrect.":GOSUB 13020:CLOSE:RETURN
27110 RE=RE+5:GET#1,RE:F=VAL(RR$):RE=RE+1:ORE=RE:LF=F
27120 FOR QP = 1 TO LF
27125 GET#1,RE:GOSUB 16500:A$(QP)=S$:RE=RE+1:NEXT QP
27130 FM=1: GOTO 6290
27150 OPEN "R",1,"A:MESSAGES",65:RL=65:FIELD#1,65 AS RR$:RE=ORE
27160 FOR QP = 1 TO LF
27165 S$=A$(QP):GOSUB 16000:PUT#1,RE:RE=RE+1:NEXT QP
27170 CLOSE:FM=0:RETURN
44000 ' Clock routine from HK, modified
44010 '  Print present time first
44210 C=32 : ' C=CLOCK PORT (20H)
44220 ' Note that this is a Mountain Hardware 100,000 DAY Clock 
44230 H(1)=INP(C+9) AND 15:H(2)=INP(C+8) AND 15
44240 H(3)=INP(C+7) AND 15:H(4)=INP(C+6) AND 15
44250 H(5)=INP(C+5) AND 15:H(6)=INP(C+4) AND 15
44260 '
44270 PRINT:PRINT "The time now is (Hrs:Mins:Secs).... ";
44280 TF$="#"
44290 FOR I=1 TO 6
44300 PRINT USING TF$;H(I);
44310 IF I=2 THEN PRINT ":";
44320 IF I=4 THEN PRINT ":";
44330 NEXT I
44340 PRINT
44700 '  Now get hh/mm/ss stored by enterbbs
44710 HT(1)=PEEK(74):HT(2)=PEEK(75):HT(3)=PEEK(76)
44720 HT(4)=PEEK(77):HT(5)=PEEK(78):HT(6)=PEEK(79)
44730 '  And calculate the difference...
44740 IF H(6)<HT(6) THEN H(6)=H(6)+10:H(5)=H(5)-1
44750 IF H(5)<HT(5) THEN H(5)=H(5)+6:H(4)=H(4)-1
44760 IF H(4)<HT(4) THEN H(4)=H(4)+10:H(3)=H(3)-1
44770 IF H(3)<HT(3) THEN H(3)=H(3)+6:H(2)=H(2)-1
44780 IF H(2)<HT(2) THEN H(2)=H(2)+10:H(1)=H(1)-1
44790 HD(6)=H(6)-HT(6):HD(5)=H(5)-HT(5):HD(4)=H(4)-HT(4)
44800 HD(3)=H(3)-HT(3):HD(2)=H(2)-HT(2):HD(1)=H(1)-HT(1)
44810 PRINT "You've been on the system for...... ";
44820 TF$="#"
44830 FOR I=1 TO 6
44840 PRINT USING TF$;HD(I);
44850 IF I=2 THEN PRINT ":";
45860 IF I=4 THEN PRINT ":";
45870 NEXT I
45880 PRINT:PRINT
45890 RETURN
  