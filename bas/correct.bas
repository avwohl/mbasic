10 :REMARK \t\tCORRECT.BAS\t\tVersion 04.23.81
20 CLEAR 4000:WIDTH 255:ON ERROR GOTO 400
30 E$=CHR$(27):E1$=E$+"E":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
40 X1$=E$+"x1":Y1$=E$+"y1":Y5$=E$+"y5"+Q$:X5$=E$+"x5":J$=E$+"J":
50 CS$=E$+"H"+E1$+P$+Y$+" 0 Correct Word Usage "+Q$+Y$+"# "
60 PRINT CS$
70 K0=70:INPUT "Enter the passing percentage <70>";K0
80 RESTORE
90 PRINT CS$Y$"#(I will give you some sentences that may (or may not) have"
100 PRINT "\twords in them that are not uesd correctly.  If a word is"
110 PRINT "\tNOT used correctly, type the correct word.  If the sentence"
120 PRINT "\thas no errors, just hit the RETURN key."
130 GOSUB 340
140 FOR Q=1 TO 100:READ B$,C$:A1$=""
150 PRINT E$"H"CS$:PRINT Y$",+"B$
160 PRINT Y$"00What is wrong? <OK>";
170 GOSUB 360:IF A$=CHR$(13) THEN 200
180 IF A$=CHR$(127) OR A$=CHR$(8) THEN A1$="":\n\tPRINT Y$"0&"J$P$Y$"2C Try again!\a "Q$:GOTO 160
190 PRINT A$J$;:A1$=A1$+A$:GOTO 170
200 IF A1$="" THEN A1$="OK"
210 IF A1$=C$ THEN R=R+1:GOTO 230
220 PRINT "\t"P$" Wron\a\a\ag ":GOSUB 340
230 NEXT Q
240 PRINT CS$
250 TM=INT((100*R)/(Q-1)):IF TM>K0 THEN GOTO 300
260 PRINT "\tSORRY\a\a... But you only received a score of"TM"per"
270 PRINT "\tcent.  Please go ask mom or dad to give you a hand, and try"
280 PRINT "\tthis quiz again."
290 GOSUB 340:R=0:GOTO 80
300 PRINT "\tVery good... You received a score of"TM"per cent."
310 PRINT "\tThat makes you eligible for the GRAND PRIZE. (A GAME.)"
320 PRINT "\tHang on a minute while I set things up..."
330 RUN"GAMES"
340 PRINT X1$P$Y$"80 Hit any key to continue..... ";
350 PRINT Y5$" ";
360 PRINT Y5$;:A$=INPUT$(1):PRINT X5$Y1$;
370 IF ASC(A$)>96 AND ASC(A$)<123 THEN A$=CHR$(ASC(A$)-32)
380 RETURN
390 :REMARK \t\tERROR MESSEGES
400 IF ERR=4 THEN RESUME 240
410 PRINT "ERROR!!!!\a\a\a\a   #"ERR" in \a\aline #"ERL:STOP
420 DATA "The computer is to smart for me!","TOO" 
430 DATA "If I get a turtle, then I will have two pets.","OK" 
440 DATA "I can hardly wait too go to the pet store!","TO" 
450 DATA "You're my favorite person.","OK" 
460 DATA "We have now finished five questions.","OK" 
470 DATA "My turtle will have it's very own box.","ITS" 
480 DATA "You're turtle should have a girl's name.","YOUR" 
490 DATA "Do you think your turtle would like a apple?","AN" 
500 DATA "I wish you wood hurry up so we can play!","WOULD" 
510 DATA "This must be question number ten.","OK" 
520 DATA "I don't like two think of hard questions.","TO" 
530 DATA "Witch game would you like to play?","WHICH" 
540 DATA "This is much better than sitting in school!","OK" 
550 DATA "We will be finished after too more questions.","TWO" 
560 DATA "Will you be too tired to play with me?","OK" 
570 DATA "Their are no more questions.","THERE" 
