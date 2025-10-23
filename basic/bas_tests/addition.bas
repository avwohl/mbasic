10 :REMARK  ADDITION.BAS  Version 04.23.81
20 CLEAR 4000:E$=CHR$(27):F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
30 X1$=E$+"x1":Y1$=E$+"y1":Y5$=E$+"y5"+Q$:X5$=E$+"x5":J$=E$+"J":
40 CS$=E$+"H"+E$+"E"+P$+Y$+" 3 Addition and Subtraction Quiz "+Q$+Y$+"# "
50 R=0:H=0:W=0:O1=0
60 D9=10::REMARK DIFFICULTY DETERMINATOR
70 V1=20::REMARK Number of problems
80 PRINT CS$Y$"#(I (the computer am going to give you some MATH problems..."
90 PRINT Y$"%(If you do well enough on them, you'll get a reward."
100 PRINT Y$"'(If you don't do so well, we'll practice some more!!!"
110 PRINT Y$")MGOOD LUCK!!!"Y$"*MHere we go...":GOSUB 360
120 PRINT CS$
130 IN$="Let's start with an easy one.":FOR V=1  TO V1:IF O1>0  THEN W=W+1
140 O1=0:GOSUB 220:NEXT V
150 PRINT CS$Y$"(0Well, I guess that's enough... "
 Y$")5Let's see how well you have done."
160 R=V1-W:PRINT Y$"-0You have answered"R"problems out of"V1"correctly..."
170 PRINT Y$".0That gives you a score of" INT(100*R/V1)"percent..."
180 GOSUB 360:IF 100*R/V1>75  THEN 350
190 PRINT Y$"-0That's not good enough... So let's practice some more..."
200 GOSUB 360:GOTO 50
210 IN$="YES, that's correct... Next problem!!!":H=H+1:A=0:RETURN
220 F1=INT(D9*RND(1))
230 F2=INT(D9*RND(2))
240 IF F2>F1  THEN S$="+" :ELSE S$="-"
250 IF S$="-"  AND V/2=INT(V/2)  THEN S$="+"
260 PRINT CS$Y$"(?" USING " ###";F1:PRINT Y$")?"S$USING "###";F2
270 PRINT Y$"-0"IN$F$Y$"*?aaaaa"G$Y$"+?"Y5$;
280 U2=0:INPUT "";U2:PRINT X5$;
290 IF S$="-"  THEN U1=F1-F2:GOTO 310
300 U1=F1+F2
310 IF U1=U2  GOTO 210
320 IN$=P$+"\a\a\a NO!!"+STR$(U2)+" is NOT correct\a\a... Try it again\a\a!! "+Q$
330 IF A=0  THEN O1=O1+1:A=1
340 GOTO 260
350 PRINT Y$"10That's good enough to play a game.":RUN"GAMES"
360 PRINT X1$P$Y$"80 Hit any key to continue..... "Y5$;:A$=INPUT$(1)
370 PRINT X5$Y1$;:RETURN
