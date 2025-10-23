        REM    DIR.BAS    * PROGRAM TO LOOK AT DIRECTORY FOR AMBIGUOUS
        REM               * FILENAMES OR UNAMBIGUOUS
        REM 01 25 83      * J.BUTLER
        REM SYSTEM CONTROL PROGRAM NUMBER    :
        REM FILES UNDER 'DBFM' CONTROL <Y/N> :N

        REM COMMONS GO HERE
        COMMON CLEAR$,NAME$,LINE$,DEMO$,CRSR$,FOCUS$,HIGH$,LOW$,PASSWORD$, \
               DATE$,EOL$,CLRFORE$,ROWOFF,COLOFF,SCRPARA,CONT

        REM ADD HARD SCREEN FUNCTIONS HERE IF NECESSARY

  REM SOROC.ADD * SOROC ATTRIBUTES
  CLEAR$=CHR$(27)+CHR$(42):CRSR$=CHR$(27)+CHR$(61):EOS$=CHR$(27)+CHR$(89)
  EOL$=CHR$(27)+CHR$(84):CLRFORE$=CHR$(27)+CHR$(59):CLRBACK$=CHR$(27)+CHR$(43)
  HIGH$=CHR$(27)+CHR$(40):LOW$=CHR$(27)+CHR$(41):HOME$=CHR$(30)
  ROWOFF=32:COLOFF=32:SCRPARA=1

        REM DIMENSIONS GO HERE
        DIM MONTHS$(12),MASK$(10),C$(65)
        NUM=64:REM DATAFIL$=""  

        MONTHS$(1)="JANUARY":MONTHS$(2)="FEBRUARY":MONTHS$(3)="MARCH"
        MONTHS$(4)="APRIL":MONTHS$(5)="MAY":MONTHS$(6)="JUNE"
        MONTHS$(7)="JULY":MONTHS$(8)="AUGUST":MONTHS$(9)="SEPTEMBER"
        MONTHS$(10)="OCTOBER":MONTHS$(11)="NOVEMBER":MONTHS$(12)="DECEMBER"

        C$="0123456789ABCDEF":TRUE%=-1:BLANK1$="          ":QUEST$="????????"
        BLANK$="..........":SCNO$="":ERR=5

7       GOTO 11
 
8       REM VERTICAL CURSOR POSITIONING ROUTINE
        FOR ZZ=1 TO VV:PRINT:NEXT ZZ:RETURN
 
9       REM DATE FORMATTING ROUTINE
        DATE$=MID$(P$,1,2)+"-"+MID$(P$,3,2)+"-"+MID$(P$,5,2)
        RETURN
 
10      REM CURSOR ADDRESS
        IF SCRPARA=1 THEN \
           PRINT CRSR$;CHR$(ROW+ROWOFF);CHR$(COLUMN+COLOFF);:RETURN
        PRINT CRSR$;CHR$(COLUMN+COLOFF);CHR$(ROW+ROWOFF);:RETURN

11      REM ASM FUNCTION HERE
        A$="":PRINT CLEAR$
        GET.DIR$ = \
        CHR$(11H)+CHR$(0)+CHR$(28H)      +\ SETDMA:     LXI D,2800
        CHR$(0EH)+CHR$(01AH)             +\             MVI C,1A
        CHR$(0CDH)+CHR$(05H)+CHR$(0)     +\             CALL 5
        CHR$(11H)+CHR$(05CH)+CHR$(0)     +\ STRG:       LXI D,005C
        CHR$(21H)+".."                   +\             LXI H,STRG ADDRESS
        CHR$(01H)+CHR$(21H)+CHR$(0)      +\             LXI B,0021
        CHR$(0EDH)+CHR$(0B0H)            +\             LDIR
        CHR$(01EH)+"."                   +\ LDDRIVE:    LD E,DRIVE
        CHR$(0EH)+CHR$(0EH)              +\             MVI C,E
        CHR$(0CDH)+CHR$(05H)+CHR$(0)     +\             CALL 5
        CHR$(0E5H)                       +\ GETDIR:     PUSH H
        CHR$(0D5H)                       +\             PUSH D
        CHR$(0C5H)                       +\             PUSH B
        CHR$(011H)+CHR$(05CH)+CHR$(0)    +\             LXI D,005C
        CHR$(0EH)+CHR$(011H)             +\             MVI C,FIND DIR/SH NEXT
        CHR$(0CDH)+CHR$(05H)+CHR$(0)     +\             CALL 5
        CHR$(032H)+".."                  +\             STA MEMLOC%
        CHR$(0C1H)                       +\             POP B
        CHR$(0D1H)                       +\             POP D
        CHR$(0E1H)                       +\             POP H
        CHR$(0C9H)+"."                    \             RET;MEMLOC%

        GET.DIR% = SADD(GET.DIR$) + 1  REM      POINT TO FIRST DATA BYTE
        REM  RELOCATE ADDRESSES WITHIN STRING
        STRG.ADDR%=SADD(GET.DIR$)+13:DRIVE%=SADD(GET.DIR$)+21
        GTONE%=SADD(GET.DIR$)+34:CHKGOOD%=SADD(GET.DIR$)+45
        POKE SADD(GET.DIR$)+39,CHKGOOD%
        POKE SADD(GET.DIR$)+40,((CHKGOOD%) AND 0FF00H) / 100H

        REM INITIALIZE THE ASM SUBROUTINE
        REM HEX VALUE HERE
        B9$=STR$(GET.DIR%):B9=GET.DIR%:B8$=""
        FOR X%=LEN(B9$)-1 TO 1 STEP -1
        Z=16^X%-(16^(X%-1)):R=16^(X%-1):Y=(B9 AND Z)/R
        B8$=B8$+MID$(C$,INT(Y)+1,1)
        NEXT X%
        PRINT CLEAR$:PRINT "GET.DIR%=";GET.DIR%,B8$

15      REM SCREEN GENERATION HERE
        PRINT CLEAR$:SCRN=4:GOSUB 3000:PRINT " SIZE of DISK (k):";TAB(29);
        PRINT "DIRECTORY ATTRIBUTES  SPACE LEFT (Sectors):"
        PRINT " 1.";TAB(20);"17.";TAB(39);"33.";TAB(58);"49."
        PRINT " 2.";TAB(20);"18.";TAB(39);"34.";TAB(58);"50."
        PRINT " 3.";TAB(20);"19.";TAB(39);"35.";TAB(58);"51."
        PRINT " 4.";TAB(20);"20.";TAB(39);"36.";TAB(58);"52."
        PRINT " 5.";TAB(20);"21.";TAB(39);"37.";TAB(58);"53."
        PRINT " 6.";TAB(20);"22.";TAB(39);"38.";TAB(58);"54."
        PRINT " 7.";TAB(20);"23.";TAB(39);"39.";TAB(58);"55."
        PRINT " 8.";TAB(20);"24.";TAB(39);"40.";TAB(58);"56."
        PRINT " 9.";TAB(20);"25.";TAB(39);"41.";TAB(58);"57."
        PRINT "10.";TAB(20);"26.";TAB(39);"42.";TAB(58);"58."
        PRINT "11.";TAB(20);"27.";TAB(39);"43.";TAB(58);"59."
        PRINT "12.";TAB(20);"28.";TAB(39);"44.";TAB(58);"60."
        PRINT "13.";TAB(20);"29.";TAB(39);"45.";TAB(58);"61."
        PRINT "14.";TAB(20);"30.";TAB(39);"46.";TAB(58);"62."
        PRINT "15.";TAB(20);"31.";TAB(39);"47.";TAB(58);"63."
        PRINT "16.";TAB(20);"32.";TAB(39);"48.";TAB(58);"64."
        IF SECOND=1 THEN SECOND=0:RETURN

20      PRINT HIGH$;CLRFORE$;
        COLUMN=10:ROW=22:GOSUB 10:PRINT EOL$;
        PRINT "FILENAME TO FIND ON DIRECTORY   :";:INPUT "";LINE C8$
        IF C8$="" OR C8$="STOP" OR C8$="END" THEN 9990
        IF LEN(C8$)>12 THEN 20
        R=MATCH(".",C8$,1):R1=MATCH("*",C8$,1)
        IF R=0 THEN 20
        D8$=LEFT$(C8$,R-1):D9$=RIGHT$(C8$,LEN(C8$)-R)
        IF R1=0 THEN 22
        IF R1<R THEN D8$=LEFT$(D8$,R1-1)+LEFT$(QUEST$,8-R1+1)
        IF R1>R THEN D9$=LEFT$(QUEST$,3):GOTO 22
        R2=MATCH("*",C8$,R1+1)
        IF R2=0 THEN 22
        D9$=LEFT$(QUEST$,3)

22      C8$=D8$+D9$

23      COLUMN=10:ROW=22:GOSUB 10:PRINT EOL$;
        PRINT "DRIVE WHERE PROGRAM RESIDES     :";:INPUT "";LINE DR$
        DR=ASC(DR$)
        IF DR<65 OR DR>72 THEN 23
        DR=DR-65:DR$=CHR$(0)

24      REM MORE THAN ONE OCCURANCE
        D$="":IT$="Y":IT=(LEFT$(IT$,1)="Y")*TRUE%
        FOR Y=1 TO 21:D$=D$+CHR$(0):NEXT Y
        C7$=DR$+C8$+D$:C7%=SADD(C7$)+1:Y=1:POKE DRIVE%,DR
        POKE STRG.ADDR%,C7%:POKE STRG.ADDR%+1,(C7% AND 0FF00H)/0100H

25      IF Y>1 AND IT=1 THEN POKE GTONE%,18
        IF Y>1 AND IT=0 THEN 9991
        C9$="":CALL GET.DIR%:CHK=PEEK(CHKGOOD%)
        IF CHK=255 THEN 30
        Z9=(CHK AND 3)*32+10240
        FOR X=Z9 TO Z9+11:C9$=C9$+CHR$(PEEK(X)):NEXT X
        D8$=LEFT$(C9$,LEN(C9$)-3):D9$=RIGHT$(C9$,3):C9$=D8$+"."+D9$
        COLUMN=INT((Y-1)/16)*19+5:ROW=Y-(INT((Y-1)/16)*16)+5:GOSUB 10
        C$(Y)=C9$:PRINT C$(Y):Y=Y+1
        IF Y>64 THEN 3002
        GOTO 25

30      PRINT LOW$;:COLUMN=10:ROW=22:GOSUB 10:PRINT EOL$;
        PRINT "IS THIS DATA CORRECT <Y/N> :";:INPUT "";LINE DATA$
        GOSUB 10:PRINT EOL$;
        IF DATA$="" OR LEFT$(DATA$,1)="Y" THEN 15
        IF DATA$="STOP" OR DATA$="END" THEN 9990
        GOTO 9990
        
40      REM ERROR CHECKING STATEMENT HERE
        RECUR$="":COLUMN=11:ROW=22:GOSUB 10
        PRINT EOL$;"'S'TOP, 'D'ELETE, 'R'ECUR @, FIELD #  :";
        INPUT "";LINE CHANGE$
        IF LEFT$(CHANGE$,1)="S" THEN GOSUB 2001:GOTO 9990
        IF CHANGE$="" THEN GOSUB 2001:SECOND=1:GOSUB 15:GOTO 20
        IF CHANGE$="D" THEN 8900
        IF MID$(CHANGE$,1,1)="R" THEN RECUR$="R" \
           :CHANGE$=MID$(CHANGE$,2,LEN(CHANGE$)-1)
        IF VAL(CHANGE$)=0 THEN 15

50      IF VAL(CHANGE$)<1 OR VAL(CHANGE$)>NUM THEN 40
        GOSUB 7010
        IF RECUR$="R" AND VAL(CHANGE$)<=NUM THEN \
           CHANGE$=STR$(VAL(CHANGE$)+1):GOTO 50
        REM GOSUB 2001
        SECOND=1:GOSUB 15:GOTO 20

60      REM SCREEN PRINT HERE
        FOR X=1 TO NUM
        COLUMN=INT((X-1)/16)*19+7:ROW=X-(INT((X-1)/16)*16)+4:GOSUB 10
        IF C$(X)="" THEN PRINT BLANK$ ELSE PRINT C$(X)
        NEXT X:RETURN

1000    IF END #1 THEN 6000

1001    READ #1,REC1+1;A1$,B1$,C1$,D1$
        RETURN

2001    REM PRINT #1,REC1+1;A1$,B1$,C1$,D1$
        RETURN

3000    PRINT TAB(40-(LEN(COMPANY$)/2));COMPANY$
        PRINT TAB(5);"SCREEN:";SCRN;TAB(64);"DATE:";DATE$
        PRINT TAB(27);"Direct I/O Data Transfer":PRINT:RETURN

3002    COLUMN=10:ROW=22:GOSUB 10:PRINT EOL$;
        PRINT "Directory Too LARGE! .. Will wrap around now"
        PRINT " if other than 'RETURN' depressed ...  ... :";:INPUT "";LINE CH$
        COLUMN=10:ROW=22:GOSUB 10:PRINT EOS$;
        IF CH$="" OR CH$=CHR$(13) THEN SECOND=1:GOSUB 15:GOTO 30
        Y=1:GOTO 24

6000    COLUMN=2:ROW=22:GOSUB 10
        PRINT EOL$;"RECORD #";REC1; \
        " HAS NOT BEEN ESTABLISHED FOR ";DATAFIL$;" ";CHR$(7);
        PRINT ": PRESS 'RETURN' :";:Y%=CONCHAR%
        COLUMN=1:GOSUB 10:PRINT EOL$;

6100    COLUMN=2:ROW=22:GOSUB 10
        PRINT EOL$;"DO YOU WANT TO CREATE THIS RECORD <Y/N> : ";
        INPUT "";LINE Y$
        IF LEFT$(Y$,1)<>"Y" THEN 6102
        SECOND=1:GOSUB 8900:GOSUB 10:PRINT EOL$;:GOTO 25

6102    GOSUB 10:PRINT EOL$;:REC1=0:GOTO 15

7010    REM SCREEN INPUT FUNCTIONS HERE
        DUM$="":HOLDIT$=C$(VAL(CHANGE$)):Y1=0
        COLUMN=INT((VAL(CHANGE$)-1)/16)*19+7
        ROW=VAL(CHANGE$)-(INT((VAL(CHANGE$)-1)/16)*16)+4
        GOSUB 10:PRINT BLANK$
        REM COLUMN=COLUMN-1
        GOSUB 10

7015    Y%=CONCHAR%
        IF Y%=24 THEN 7010
        IF Y%=27 THEN Y1=0:RECUR$="":GOTO 7020
        IF Y%=8 OR Y%=127 AND Y1>0 THEN Y1=Y1-1:PRINT CHR$(8);".";CHR$(8);: \
           DUM$=LEFT$(DUM$,Y1):GOTO 7015
        IF Y%=13 THEN 7020
        IF Y%<32 OR Y%>123 THEN 7015
        Y1=Y1+1
        IF Y1>10 THEN PRINT CHR$(8);" ";CHR$(7);:GOTO 7010
        DUM$=DUM$+CHR$(Y%):GOTO 7015

7020    IF Y1<1 THEN C$(VAL(CHANGE$))=HOLDIT$:GOSUB 10:PRINT HOLDIT$:RETURN
        IF DUM$=" " THEN C$(VAL(CHANGE$))="" \
           ELSE C$(VAL(CHANGE$))=DUM$
        RETURN

8900    REM DELETE RECORD FUNCTION HERE
        PRINT #1,REC1+1;"","","",""
        IF SECOND=1 THEN SECOND=0:RETURN
        GOTO 15

9990    REM STOP HERE

9991    STOP
 
9992    FOR X=1 TO 24:PRINT:NEXT X
        PRINT TAB(20);"ACCESS NOT PERMITTED! SEE YOUR SYSTEM SUPERVISOR..";ERR
        Y%=CONCHAR%
        IF Y%=5EH THEN 9999
        GOTO 9992
 
9999   STOP

