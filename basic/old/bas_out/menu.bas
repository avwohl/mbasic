10 :REMARK  MENU.BAS Demo Menu Version 05.26.81
20 CLEAR 2000:WIDTH 255:F=200:DIM FL$(F):ON  ERROR  GOTO 250
30 E$=CHR$(27):E1$=E$+"E":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q"
40 A$=E$+"A":B$=E$+"B":D$=E$+"D"
50 Y$=E$+"Y":X5$=E$+"x5":Y5$=E$+"y5":C$=STRING$(80,"^")
60 PRINT E1$X5$;
70 FOR I=1  TO F:READ FL$(I):NEXT I:I1=I
80 PRINT F$C$Y$"! ";:FOR I=1  TO 20:PRINT "^^"B$D$D$;:NEXTI
90 PRINT C$D$;:FOR I=1  TO 22:PRINT A$"^^"D$;:NEXT I
100 PRINT Y$"!'s s s s fac    sac sac scfs fac    sac sac fac f"
 "ac sac fac scfs fac"
110 PRINT Y$CHR$(34)"'vat ` ` ` c    ` ` va  ```` ` `    vad vs"
 "d ` ` ` c vsd vat ```` eac"
120 PRINT Y$"#'u u ead ead    uad uad uedu ead    u   uu  ead e"
 "ad uu  u u uedu ead"G$
130 I2=INT((I1-1)/3)+1:IF I1>26  THEN I2=INT((I1-1)/6)+1:I8=I2:I9=1
140 FOR I=1  TO I1:PRINT Y$CHR$(I+37)"9" CHR$(I+64)". "FL$(I):NEXT I
150 PRINTY$"35Your choice? (Enter a letter) <END>"Y5$;:A$=INPUT$(1):PRINT X5$;
160 IF A$=CHR$(13)  THEN  PRINT E1$Y1$"You are in HDOS"Y5$;:SYSTEM
170 IF A$>"`"  AND A$<"{"  THEN A$=CHR$(ASC(A$)-32)
180 IF A$>CHR$(64)  AND A$<CHR$(65+I1)  THEN 200
190 PRINT "\a\a\a\a\a";:GOTO 150
200 FL$=FL$(ASC(A$)-64):GOTO 210
210 PRINT E1$Y$"+2Loading......."FL$Y1$Y5$;:IN=INSTR(FL$," ")
220 FL$=LEFT$(FL$,IN-1)
230 IF  LEN(FL$)>8  THEN FL$=LEFT$(FL$,8)
240 RUN FL$
250 IF  ERR=4  AND  ERL=70  THEN I1=I-1:I=200:NEXT I:RESUME 80
260 PRINT P$Y$"50 Error #" ERR" in line #\a\a\a\a\a" ERL" "Q$:STOP
270 DATA "Spelling Quiz","Addition & Subtraction","Multiplication Tables",
 "Division Tables"
280 DATA "Number Guessing","Correct Word Usage"
290 DATA "Word Guessing","Ratio Problems","ADD & SUBTRACT Multiple-Digit"
300 DATA "Multiply Using Multiple-Digit"
