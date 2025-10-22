REM	Adapated from September 1981 KILOBAUD/Microcomputing Magazine
REM	by Don Weir, 12/Jan/82
REM
REM	Use CBASIC compiler

        CL$=CHR$(12):PRINT CL$
        CODE$="NSCQ"
        BLANK$="                             "
        DASH$="                             "
        REC.SIZE%=110
                DIM DAY$(7),MONTH$(12),FIRST%(12),DAYS%(12)
                DIM LINE.1$(8),LINE.2$(8),LINE.3$(8),WK.DY$(8)
        FIRST%(1)=1:FIRST%(2)=32:FIRST%(3)=60:FIRST%(4)=91
       FIRST%(5)=121:FIRST%(6)=152:FIRST%(7)=182:FIRST%(8)=213
    FIRST%(9)=244:FIRST%(10)=274:FIRST%(11)=305:FIRST%(12)=335
        DAYS%(1)=31:DAYS%(2)=28:DAYS%(3)=31:DAYS%(4)=30
        DAYS%(5)=31:DAYS%(6)=30:DAYS%(7)=31:DAYS%(8)=31
        DAYS%(9)=30:DAYS%(10)=31:DAYS%(11)=30:DAYS%(12)=31
       DAY$(1)="Mon":DAY$(2)="Tue":DAY$(3)="Wed":DAY$(4)="Thu"
       DAY$(5)="Fri":DAY$(6)="Sat":DAY$(7)="Sun"
        MONTH$(1)="Jan":MONTH$(2)="Feb":MONTH$(3)="Mar"
        MONTH$(4)="Apl":MONTH$(5)="May":MONTH$(6)="Jun"
        MONTH$(7)="Jul":MONTH$(8)="Aug":MONTH$(9)="Sep"
        MONTH$(10)="Oct":MONTH$(11)="NOv":MONTH$(12)="Dec"
5       PRINT CL$:PRINT TAB(52);"Adapted from"
        PRINT TAB(52);"KILOBAUD"
        PRINT TAB(52);"Sept. 1981."
                FOR I%=1 TO 5:PRINT:NEXT I%
        INPUT "Year (i.e., 1981)";YEAR$
        PRINT "Is ";YEAR$;" correct "
        INPUT LINE Q$
        IF LEFT$(Q$,1)="N" THEN 5
        YEAR=VAL(YEAR$)
        A=YEAR/4:B=INT(A):C=A-B
        IF C<>0 THEN 10
        DAYS%(2)=29
        FOR X%=3 TO 12
                FIRST%(X%)=FIRST%(X%)+1
        NEXT X%
10      GOSUB 20
        ON T% GOSUB 100,200,300,400
        GOTO 10
20      PRINT CL$
        PRINT
        IF ERSW1% THEN ERSW1%=0:PRINT TAB(10);"Year not found.":PRINT
        IF ERSW2% THEN ERSW2%=0:PRINT TAB(10);YEAR$;" already exists";:PRINT
        PRINT TAB(24);"CALENDAR"
        PRINT TAB(24);"--------":PRINT:PRINT
        PRINT
        PRINT TAB(10);"N = Set up New Year":PRINT
        PRINT TAB(10);"Y = Change Year":PRINT
        PRINT TAB(10);"S = See":PRINT
        PRINT TAB(10);"C = Change Data":PRINT
        PRINT TAB(10);"Q = Quit":PRINT
        INPUT "Task ";T$
        T$=LEFT$(T$,1)
        IF T$="Y" THEN 5
        FOR T%=1 TO 5
                IF T$=MID$(CODE$,T%,1) THEN RETURN
        NEXT T%
        GOTO 10
100     PRINT CL$
        PRINT:PRINT YEAR$:PRINT
        INPUT "Jan 1 day number (Monday=1) ";LINE DAY.NUM$
        IF DAY.NUM$="" THEN RETURN
        DAY.NUM%=VAL(DAY.NUM$)
        IF DAY.NUM%<1 OR DAY.NUM%>7 THEN 100
        PRINT:PRINT "Writing...";
        READ%=0
                        GOSUB 1000
                        IF OLD.FILE% THEN ERSW2%=1:GOTO 110
                     LINE.1$=DASH$:LINE.2$=DASH$:LINE.3$=DASH$
                FOR X%=1 TO FIRST%(12)+DAYS%(12)
                        REC.NUM%=X%
                        DAY$=DAY$(DAY.NUM%)
                        GOSUB 1200
                        DAY.NUM%=DAY.NUM%+1
                        IF DAY.NUM%>7 THEN DAY.NUM%=1
                        PRINT ".";
                NEXT X%
110     PRINT "":CLOSE 1:RETURN

200     PRINT CL$:PRINT:PRINT
        INPUT "Starting date (mm,dd) ";NUM%,DATE%
        IF NUM%<1 OR NUM%>12 THEN 200
        IF DATE%<1 OR DATE%>DAYS%(NUM%) THEN 200
        START%=(FIRST%(NUM%)-1)+DATE%
        READ%=1:NEW%=0
        GOSUB 1000
        IF OLD.FILE%=0 THEN ERSW1%=1:RETURN
205             FOR X%=1 TO 7
                        REC.NUM%=START%
                        GOSUB 1100
                        DATE$=STR$(DATE%)
        IF NEW%=0 THEN WK.DY$(X%)=DAY$+" "+DATE$
        IF NEW% THEN NEW%=0:WK.DY$(X%)=DAY$+" "+DATE$+" "+"*"
                LINE.1$(X%)=LINE.1$
                LINE.2$(X%)=LINE.2$
                LINE.3$(X%)=LINE.3$
                DATE%=DATE%+1
                START%=START%+1
        IF DATE%>DAYS%(NUM%) THEN DATE%=1:NUM%=NUM%+1:NEW%=1
        IF START%>FIRST%(12)+30 THEN START%=1:NUM%=1
                NEXT X%
        PRINT CL$
210     IF TASK$="P" THEN PRINT:PRINT:PRINT:PRINT TAB(5);MONTH$(NUM%);" ";YEAR$:PRINT:GOTO 215
        PRINT TAB(25);MONTH$(NUM%);" ";YEAR$:PRINT
215     FOR X%=1 TO 7 STEP 2
                PRINT WK.DY$(X%);TAB(40);WK.DY$(X%+1)
                PRINT LINE.1$(X%);TAB(40);LINE.1$(X%+1)
                PRINT LINE.2$(X%);TAB(40);LINE.2$(X%+1)
                PRINT LINE.3$(X%);TAB(40);LINE.3$(X%+1)
        REM     PRINT
        NEXT X%
        IF TASK$="P" THEN CONSOLE
        PRINT TAB(5);"P = Print  Return-next  Q = Quit"
        PRINT TAB(5);"Task ";
        INPUT LINE TASK$:TASK$=LEFT$(TASK$,1)
        IF TASK$="Q" THEN 220
        IF TASK$="P" THEN LPRINTER WIDTH 80:GOTO 210
                GOTO 205
220     CLOSE 1:READ%=0
        RETURN
300     READ%=1
        GOSUB 1000
        IF OLD.FILE%=0 THEN ERSW1%=0:RETURN
310     PRINT CL$
        INPUT "Date (mm,dd) ";NUM%,DATE%
        IF NUM%<1 OR NUM%>12 THEN 310
        IF DATE%<1 OR DATE%>DAYS%(NUM%) THEN 310
320     REC.NUM%=(FIRST%(NUM%)-1)+DATE%
                        GOSUB 1100
330     PRINT CL$
        PRINT:PRINT:PRINT
        PRINT TAB(20);MONTH$(NUM%);" ";YEAR$:PRINT
        PRINT TAB(20);DAY$;DATE%
        PRINT TAB(20);LINE.1$
        PRINT TAB(20);LINE.2$
        PRINT TAB(20);LINE.3$
        PRINT
    PRINT TAB(2);"(B-Blank  W-Write  S-Switch  N-New date)";
    PRINT "  RETURN-next  Q-Quit)"
        PRINT TAB(5);"Task";
        INPUT LINE TASK$:TASK$=LEFT$(TASK$,1)
        IF TASK$="N" OR TASK$="" THEN 350
        IF TASK$="Q" THEN 360
        IF TASK$="B" THEN GOSUB 1300
        IF TASK$="W" THEN GOSUB 1400
        IF TASK$="S" THEN 340
                GOTO 330
340 INPUT "Switch date (mm,dd) ";SM%,SD%
        IF SM%<1 OR SM%>12 THEN 340
        IF SD%<1 OR SD%>DAYS%(SM%) THEN 340
        REC.1%=REC.NUM%
        DAY.1$=DAY$
        HOLD.1$=LINE.1$:HOLD.2$=LINE.2$:HOLD.3$=LINE.3$
        REC.NUM%=(FIRST%(SM%)-1)+SD%
                GOSUB 1100
                DAY.2$=DAY$
                REC.2%=REC.NUM%
                DAY$=DAY.1$
                REC.NUM%=REC.1%
                GOSUB 1200
        DAY$=DAY.2$
        LINE.1$=HOLD.1$
        LINE.2$=HOLD.2$
        LINE.3$=HOLD.3$
                REC.NUM%=REC.2%
                GOSUB 1200
                REC.NUM%=REC.1%
                GOSUB 1100
                GOTO 330
350     GOSUB 1200
        IF TASK$="N" THEN 310
        DATE%=DATE%+1
        IF DATE%>DAYS%(NUM%) THEN DATE%=1:NUM%=NUM%+1
        IF NUM%>12 THEN NUM%=1
        GOTO 320
360     GOSUB 1200
                CLOSE 1:READ%=0
                RETURN
400     PRINT CL$
                        STOP
1000    OLD.FILE%=0
        IF END #1 THEN 1010
        FILE$=YEAR$+".DAT"
        OPEN FILE$ RECL REC.SIZE% AS 1
        OLD.FILE%=1
        GOTO 1020
1010    IF READ% THEN 1020
        CREATE FILE$ RECL REC.SIZE% AS 1
1020    RETURN

1100    END.FILE%=0
        IF END # 1 THEN 1110
        READ # 1,REC.NUM%;DAY$,LINE.1$,LINE.2$,LINE.3$
                RETURN
1110    END.FILE%=1
                RETURN
1200    PRINT # 1,REC.NUM%;DAY$,LINE.1$,LINE.2$,LINE.3$
                RETURN
1300    PRINT TAB(5);"Line 1, 2, 3  or all";
        INPUT LINE LN.NUM$
        IF LN.NUM$="" THEN 1310
        LN.NUM$=LEFT$(LN.NUM$,1)
        IF LN.NUM$="A" THEN LINE.1$=DASH$:LINE.2$=DASH$:LINE.3$=DASH$
        IF LN.NUM$="1" THEN LINE.1$=DASH$
        IF LN.NUM$="2" THEN LINE.2$=DASH$
        IF LN.NUM$="3" THEN LINE.3$=DASH$
1310            RETURN
1400 PRINT "Line #1 ";"------------------------------*"
     INPUT "       ";LINE LN$
        IF LN$="" THEN 1410
        LINE.1$=LEFT$(LN$+BLANK$,30)
1410 PRINT "Line #2 ";"------------------------------*"
     INPUT "       ";LINE LN$
        IF LN$="" THEN 1420
        LINE.2$=LEFT$(LN$+BLANK$,30)
1420 PRINT "Line #3 ";"------------------------------*"
     INPUT "       ";LINE LN$
        IF LN$="" THEN 1430
        LINE.3$=LEFT$(LN$+BLANK$,30)
1430 RETURN
