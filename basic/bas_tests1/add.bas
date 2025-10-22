10 :REMARK  ADD.BAS  Version 04.22.81
20 CLEAR 4000:WIDTH 255:ON  ERROR  GOTO 520
30 E$=CHR$(27):E1$=E$+"E":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
40 X1$=E$+"x1":Y1$=E$+"y1":Y5$=E$+"y5"+Q$:X5$=E$+"x5":J$=E$+"J":
50 CS$=E$+"H"+E1$+P$+Y$+" 3 Addition and Subtraction Quiz "+Q$+Y$+"# "
60 PRINT CS$
70 R=0:H=0:W=0
80 O1=0
90 D9=1000::REMARK D9 IS DIFFICULTY DETERMINATOR
100 V1=20::REMARK V1 is the number of problems
110 PRINT " I (THE COMPUTER) AM GOING TO GIVE YOU SOME MATH PROBLEMS..."
120 PRINT " IF YOU DO WELL ENOUGH ON THEM, YOU'LL GET A REWARD.  IF"
130 PRINT " YOU DON'T DO SO WELL, WE'LL PRACTICE SOME MORE !!!"
140 PRINT "    GOOD LUCK!!!"
150 PRINT "    HERE WE GO..."
160 GOSUB 460
170 PRINT CS$
180 IN$="Let's start with an easy one.":FOR V=1  TO V1:IF O1>0  THEN W=W+1
190 O1=0
200 GOSUB 330
210 NEXT V
220 PRINT CS$Y$"(0Well, I guess that's enough... "
 Y$")5Let's ee how well you have done."
230 R=V1-W
240 PRINT Y$"-0You have answered"R"problems out of 20 correctly..."
250 PRINT Y$".0That gives you a score of " INT(100*R/V1)"percent..."
260 GOSUB 460
270 IF 100*R/V1>75  GOTO 450
280 PRINT Y$"-0That's not good enough... So let's practice some more..."
290 GOSUB 460:GOTO 60
300 U1=F1-F2:GOTO 430
310 IN$="YES, that's correct... Next problem!!!":H=H+1:RETURN
320 H=H+1:RETURN
330 F1=INT(D9*RND(1))
340 F2=INT(D9*RND(2))
350 IF F2<=F1  THEN S$="-"
360 IF F2>F1  THEN S$="+"
370 PRINT CS$
380 PRINT Y$"(?" USING " ###";F1:PRINT Y$")?"S$USING "###";F2
390 PRINT Y$"-0"IN$F$Y$"*?aaaaa"G$Y$"+="Y5$;
400 INPUT "";U2:PRINT X5$;
410 IF F2<=F1  GOTO 300
420 U1=F1+F2
430 IF U1=U2  GOTO 310
440 IN$=P$+"\a\a\a NO!!"+STR$(U2)+" is NOT correct\a\a... Try it again\a\a!! "+Q$:
 O1=O1+1:GOTO 370
450 PRINT CS$Y$"/0SUPER!  Let's have some fun!":RUN"GAMES"
460 PRINT X1$P$Y$"80 Hit any key to continue..... ";
470 PRINT Y5$" ";
480 PRINT Y5$;:A$=INPUT$(1):PRINT X5$Y1$;
490 IF  ASC(A$)>96  AND  ASC(A$)<123  THEN A$=CHR$(ASC(A$)-32)
500 RETURN
510 :REMARK  ERROR MESSEGES
520 PRINT Y$"70ERROR!!!!\a\a\a\a   #" ERR" in \a\aline #" ERL:STOP
