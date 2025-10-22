1 :REMARK    ONECHECK
2 :REMARK
3 :REMARK  Converted to MBASIC and the H19 Terminal
4 :REMARK   BY: Thomas C. Kyle
5 :REMARK       4600 Franklin Av
6 :REMARK       Western Springs, IL 60558
7 :REMARK       312-246-2874
8 :REMARK
9 :REMARK
10 :REMARK
100 DIM A$(64)
200 GOSUB 10800:PRINT E1$ NC$
300 PRINT CP$"(=O N E   C H E C K"
400 PRINT CP$"*:Solitare checker puzzle"
500 PRINT CP$",:Want instructions (Y/N) "YC$;:A$=INPUT$(1):PRINT A$
600 IF A$="N"  OR A$="n"  THEN  PRINT E1$:GOTO 1500
700 IF  A$="y"  OR A$="Y"  THEN 800 :ELSE  PRINT NC$  CHR$(7) CP$"-:Y or N, Please":PRINT CP$",:" E$"K":GOTO 500
800 PRINT NC$ E1$ CP$"$.48 Checkers are placed on the 2 outside spaces of a"
900 PRINT CP$"%.standard 64-square checkerboard. The object is to remove"
1000 PRINT CP$"&.as many checkers as possible by DIAGONAL jumps (as in"
1100 PRINT CP$"'.standard checkers). Use the numbers UNDER the squares to"
1200 PRINT CP$"(.indicate the square you wish to jump FROM and TO."
1300 PRINT CP$",.To end the game, input 0 (zero) in response to FROM."
1400 PRINT CP$"..Tap the ";YR$ "RETURN" NR$" key to start." YC$;:A$=INPUT$(1):PRINT E1$
1500 FOR J=1  TO 64
1600 A$(J)=" ^"
1700 NEXT J
1800 FOR J=19  TO 43  STEP 8
1900 FOR I=J  TO J+3
2000 A$(I)="  "
2100 NEXT I
2200 NEXT J
2300 M=0
2400 GOSUB 5200
2450 PRINTCP$"* TYPE 0 (ZERO) WHEN OUT OF MOVES"
2500 PRINT CP$".#JUMP FROM " YC$;NG$;:INPUT F:PRINT NC$:IF F=0  THEN 4000
2600 PRINT CP$".3TO ";YC$;:INPUT T:PRINT NC$ CP$".:" E$"o" YG$
2700 F1=INT((F-1)/8)
2800 F2=F-8*F1
2900 T1=INT((T-1)/8)
3000 T2=T-8*T1
3100 IF F1>7  OR T1>7  OR F2>8  OR T2>8  THEN 3400
3200 IF  ABS(F1-T1)<>2  OR  ABS(F2-T2)<>2  OR A$((T+F)/2)=" "  OR A$(F)=" "  OR A$(T)="^"  THEN 3400
3300 GOTO 3500
3400 PRINT  CHR$(7) YR$ CP$"0#ILLEGAL MOVE. TRY AGAIN..." NR$:FOR A=1  TO 800:NEXT:PRINT CP$"0>" E$"o":GOTO 2500
3500 A$(T)=" ^"
3600 A$(F)="  "
3700 A$((T+F)/2)="  "
3800 M=M+1
3900 GOSUB 7000:PRINT NG$:GOTO 2500
4000 PRINT NG$:S=0
4100 FOR I=1  TO 64
4200 IF  MID$(A$(I),2,1)="^"  THEN S=S+1
4300 NEXT I
4400 PRINT CP$". You made" M "jumps and had" S "pieces"
4500 PRINT CP$"/ remaining on the board."
4600 PRINT  CHR$(7);CP$"52Want to play again? (Y/N) " YC$;:A$=INPUT$(1):PRINT A$
4700 IF A$="Y"  OR A$="y"  THEN  PRINT E1$:GOTO1500
4800 IF A$="n"  OR A$="N"  THEN 5000
4900 PRINT  CHR$(7);NC$;CP$"62Y or N, PLEASE":PRINT CP$"52" E$"K":GOTO 4600
5000 PRINT NC$ E1$ YR$ CP$")=STAY LOOSE!"
5100 PRINT NG$ YC$ NR$:FOR X=1  TO 1500:NEXT:PRINT CHR$(27)"z":FORX=1TO500:NEXT:END
5200 PRINT YG$ NC$ YR$
5300 PRINT CP$  CHR$(34)"Dfaaasaaasaaasaaasaaasaaasaaasaaac"
5400 PRINT CP$"#D`   `   `   `   `   `   `   `   `"
5500 PRINT CP$"$Dva1aba2aba3aba4aba5aba6aba7aba8at"
5600 PRINT CP$"%D`   `   `   `   `   `   `   `   `"
5700 PRINT CP$"&Dva9ab10ab11ab12ab13ab14ab15ab16at"
5800 PRINT CP$"'D`   `   `   `   `   `   `   `   `"
5900 PRINT CP$"(Dv17ab18ab19ab20ab21ab22ab23ab24at"
6000 PRINT CP$")D`   `   `   `   `   `   `   `   `"
6100 PRINT CP$"*Dv25ab26ab27ab28ab29ab30ab31ab32at"
6200 PRINT CP$"+D`   `   `   `   `   `   `   `   `"
6300 PRINT CP$",Dv33ab34ab35ab36ab37ab38ab39ab40at"
6400 PRINT CP$"-D`   `   `   `   `   `   `   `   `"
6500 PRINT CP$".Dv41ab42ab43ab44ab45ab46ab47ab48at"
6600 PRINT CP$"/D`   `   `   `   `   `   `   `   `"
6700 PRINT CP$"0Dv49ab50ab51ab52ab53ab54ab55ab56at"
6800 PRINT CP$"1D`   `   `   `   `   `   `   `   `"
6900 PRINT CP$"2De57au58au59au60au61au62au63au64ad"
7000 PRINT YR$ YG$ CP$"#E"A$(1) CP$"#I"A$(2) CP$"#M"A$(3) CP$"#Q"A$(4) CP$"#U"A$(5)
7100 PRINT CP$"#Y"A$(6) CP$"#]"A$(7) CP$"#a"A$(8)
7200 PRINT CP$"%E"A$(9) CP$"%I"A$(10) CP$"%M"A$(11) CP$"%Q"A$(12) CP$"%U"A$(13)
7300 PRINT CP$"%Y"A$(14) CP$"%]"A$(15) CP$"%a"A$(16)
7400 PRINT CP$"'E"A$(17) CP$"'I"A$(18) CP$"'M"A$(19) CP$"'Q"A$(20) CP$"'U"A$(21)
7500 PRINT CP$"'Y"A$(22) CP$"']"A$(23) CP$"'a"A$(24)
7600 PRINT CP$")E"A$(25) CP$")I"A$(26) CP$")M"A$(27) CP$")Q"A$(28) CP$")U"A$(29)
7700 PRINT CP$")Y"A$(30) CP$")]"A$(31) CP$")a"A$(32)
7800 PRINT CP$"+E"A$(33) CP$"+I"A$(34) CP$"+M"A$(35) CP$"+Q"A$(36) CP$"+U"A$(37)
7900 PRINT CP$"+Y"A$(38) CP$"+]"A$(39) CP$"+a"A$(40)
8000 PRINT CP$"-E"A$(41) CP$"-I"A$(42) CP$"-M"A$(43) CP$"-Q"A$(44) CP$"-U"A$(45)
8100 PRINT CP$"-Y"A$(46) CP$"-]"A$(47) CP$"-a"A$(48)
8200 PRINT CP$"/E"A$(49) CP$"/I"A$(50) CP$"/M"A$(51) CP$"/Q"A$(52) CP$"/U"A$(53)
8300 PRINT CP$"/Y"A$(54) CP$"/]"A$(55) CP$"/a"A$(56)
8400 PRINT CP$"1E"A$(57) CP$"1I"A$(58) CP$"1M"A$(59) CP$"1Q"A$(60) CP$"1U"A$(61)
8500 PRINT CP$"1Y"A$(62) CP$"1]"A$(63) CP$"1a"A$(64)
8600 PRINT NR$:RETURN
8700 :REMARK
8800 :REMARK   H19.SUBROUTINE
8900 :REMARK
10800 E$=CHR$(27):E1$=E$+"E":YG$=E$+"F":NG$=E$+"G"
10900 YR$=E$+"p":NR$=E$+"q":YC$=E$+"y5":NC$=E$+"x5"
11000 CP$=E$+"Y":Y25$=E$+"x1":N25$=E$+"y1"
11100 RETURN
11200 :REMARK   E1$  = ERASE SCREEN
11210 :REMARK   YG$  = ENTER GRAPHICS MODE
11220 :REMARK   NG$  = EXIT GRAPHICS MODE
11230 :REMARK   YR$  = ENTER REVERSE VIDEO MODE
11240 :REMARK   NR$  = EXIT REVERSE VIDEO MODE
11250 :REMARK   YC$  = CURSOR ON
11260 :REMARK   NC$  = CURSOR OFF
11270 :REMARK   CP$  = POSITION CURSOR
11280 :REMARK   Y25$ = ENABLE 25th LINE
11290 :REMARK   N25$ = DISABLE 25th LINE
