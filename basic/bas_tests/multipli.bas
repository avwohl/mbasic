10 :REMARK  MULTIPLI.BAS  Version 04.23.81
20 CLEAR 4000:E$=CHR$(27):F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
30 X1$=E$+"x1":Y1$=E$+"y1":Y5$=E$+"y5"+Q$:X5$=E$+"x5":J$=E$+"J":
40 CS$=E$+"H"+E$+"E"+P$+Y$+" 0 Math Quiz "+Q$+Y$+"# "
50 R=0:H=0:W=0
60 O1=0
70 D9=10::REMARK DIFFICULTY DETERMINATOR
80 PRINT CS$Y$"#(I (the computer) am going to give you some MATH problems..."
90 PRINT Y$"%(If you do well enough on them, you'll get a reward."
100 PRINT Y$"'(If you don't do so well, we'll practice some more!!!"
110 PRINT Y$")MGOOD LUCK!!!"Y$"*MHere we go...":GOSUB 340
120 IN$="Let's start some really easy.":FOR V=1  TO 40
130 IF O1>0  THEN W=W+1
140 O1=0:GOSUB 240:NEXT V
150 PRINT CS$Y$"#(Well, I guess that's enough..."
 Y$"$(Let's see how well you have done."
160 R=40-W
170 PRINT Y$"00You have answered"R"problems out of 40 correctly..."
180 PRINT Y$"10That gives you a score of" INT(100*R/40)"percent...":GOSUB 340
190 IF 100*R/40>75  GOTO 330
200 PRINT Y$"-0That's not good enough... so let's practice some more..."
210 GOSUB 340:GOTO 50
220 U1=F1-F2:GOTO 290
230 IN$="Yes, that's correct... Next problem!!!":A=0:H=H+1:RETURN
240 F1=INT(D9*RND(1))
250 F2=INT(D9*RND(2))
260 PRINT CS$Y$"(?" USING " ###";F1:PRINT Y$")?" USING "X###";F2:
 PRINT F$Y$"*?aaaaa"G$Y$"/0"IN$Y$"+?"Y5$;
270 U2=0:INPUT "";U2:PRINT X5$;
280 U1=F1*F2
290 IF U1=U2  GOTO 230
300 IN$=P$+" NO!\a\a"+STR$(U2)+" is not correct\a\a\a... Try it again\a\a!! "+Q$
310 IF A=0  THEN O1=O1+1:A=1
320 GOTO 260
330 PRINT CS$Y$"-0Pretty good... Let's play some games!!":RUN"GAMES"
340 PRINT X1$P$Y$"80 Hit any key to continue..... ";
350 PRINT Y5$;:A$=INPUT$(1):PRINT X5$Y1$;:RETURN
