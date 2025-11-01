10 :REMARK  DIVISION.BAS  Version 04.23.81
20 CLEAR 4000:E$=CHR$(27):F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
30 X1$=E$+"x1":Y1$=E$+"y1":Y5$=E$+"y5"+Q$:X5$=E$+"x5":J$=E$+"J":
40 CS$=E$+"H"+E$+"E"+P$+Y$+" 9 Division Quiz "+Q$+Y$+"# "
50 R=0:H=0:W=0
60 O1=0
70 D9=10::REMARK  Difficulty determinator
80 D8=100
90 V1=20
100 PRINT CS$Y$"#(I (the computer) am going to give you some MATH problems..."
110 PRINT Y$"%(If you do well enough on them, you'll get a reward."
120 PRINT Y$"'(If you don't do so well, we'll practice some more!!!"
130 PRINT Y$"-TGOOD LUCK!!!"
140 PRINT Y$"00What is your first name? "Y5$;:LINE  INPUT Z$:IF Z$=""  THEN Z$="SMARTY"
150 PRINT Y$"29Here we go, "Z$"..."X5$;
160 FOR I=1  TO 200:NEXT I
170 FOR V=1  TO V1
180 IF O1>0  THEN W=W+1
190 O1=0
200 GOSUB 490
210 PRINT CS$Y$"-0"IN$:GOSUB 330
220 NEXT V
230 PRINT CS$Y$"#(Well, I guess that's enough... Let's see how well you have done."
240 R=V1-W
250 PRINT Y$"%(You have answered"R"problems out of"V1"correctly..."
260 PRINT Y$"'(That gives you a score of" INT(100*R/V1)"percent..."
270 GOSUB 510
280 IF 100*R/V1>75  GOTO  PRINT CS$Y$"&0SUPER!! Let's have some FUN!":
 RUN"GAMES"
290 PRINT Y$"-0That's no\at good enough... So let's practice some more..."
300 GOSUB 510:GOTO 50
310 U1=F1-F2:GOTO 450
320 IN$="YES, That's correct... Next problem!!!":A=0:H=H+1:RETURN
330 F1=INT(D8*RND(J1))
340 F2=INT(D9*RND(J2))
350 IF F1<F2  GOTO 330
360 IF F2=0  THEN 330
370 IF  INT(F1/F2)<>F1/F2  GOTO 330
380 IF F2=0  GOTO 330
390 IF F1>20  AND F2<9  GOTO 330
400 IF F2=1  GOTO 330
410 PRINT CS$Y$"(?" USING " ###";F1:PRINT F$Y$")?j" USING "###";F2
420 PRINT Y$"*?aaaaa"G$Y$"-0"IN$Y$"+?"Y5$;
430 U2=0:INPUT "";U2:PRINT X5$;
440 U1=F1/F2
450 IF U1=U2  GOTO 320
460 IN$=P$+" \aNO!"+STR$(U2)+" \a\ais not correct\a\a... Try it again\a\a!! "+Q$
470 IF A=0  THEN O1=O1+1:A=1
480 GOTO 410
490 J1=ASC(Z$)
500 J2=ASC(MID$(Z$,2,1)):RETURN
510 PRINT X1$P$Y$"80 Hit any key to continue..... ";
520 PRINT Y5$;:A$=INPUT$(1):PRINT X5$Y1$;:RETURN
