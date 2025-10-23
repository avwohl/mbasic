10 :REMARK \t\tSPELLING.BAS\tVersion 04.23.81
20 CLEAR 4000:ON ERROR GOTO 340
30 E$=CHR$(27):P$=E$+"p":Q$=E$+"q":Y$=E$+"Y"
40 X1$=E$+"x1":Y1$=E$+"y1":Y5$=E$+"y5"+Q$:X5$=E$+"x5":J$=E$+"J":
50 CS$=E$+"H"+E$+"E"+P$+Y$+" 0 Spelling Quiz "+Q$+Y$+"# "
60 PRINT CS$Y$"#(I will give you a sentence which has one word in it that"
70 PRINT "\tis not spelled correctly.  You must spell that word as it"
80 PRINT "\tshould be spelled.  If you do well enough, you may play a"
90 PRINT "\tgame.  Otherwise, more work !!!"
100 PRINT "\t\t\t\tHERE WE GO...":GOSUB 280
110 R=0:FOR Q=1 TO 1000:A1$=""
120 READ B$,C$
130 PRINT CS$Y$",+"B$"."
140 PRINT Y$"0&What word is spelled wrong in the above sentence? "Y5$;
150 GOSUB 300:IF A$=CHR$(13) THEN 180
160 IF A$=CHR$(127) OR A$=CHR$(8) THEN A1$="":\n\tPRINT Y$"0&"J$P$Y$"2C Try again! "Q$:GOTO 140
170 PRINT A$J$;:A1$=A1$+A$:GOTO 150
180 IF A1$=C$ THEN R=R+1:GOTO 200
190 PRINT P$Y$"2C Wrong\a\a\a "Q$:GOSUB 280
200 NEXT Q
210 P=INT(100*R/(Q-1))
220 IF P>70 GOTO 260
230 PRINT CS$Y$"#(I'm very sorry\a\a\a, but you have only gotten"P"per cent correct."
240 PRINT "\tYou need to get 70 percent or more to play a game.  Let's try"
250 PRINT "\tit again, OK!\a\a":GOSUB 280:GOTO 10
260 PRINT CS$Y$"#0HURRY!\a\a"Y$"(0You have gotten"P"per cent correct."
270 PRINT Y$"*0That is good enough to play a game or two!!!":GOSUB 280:RUN"GAMES"
280 PRINT X1$P$Y$"80 Hit any key to continue..... ";
290 PRINT Y5$" ";
300 PRINT Y5$;:A$=INPUT$(1):PRINT X5$Y1$;
310 IF ASC(A$)>96 AND ASC(A$)<123 THEN A$=CHR$(ASC(A$)-32)
320 RETURN
330 :REMARK \t\tERROR MESSEGES
340 IF ERR=4 THEN RESUME 210
350 PRINT "ERROR!!!!\a\a\a\a   #"ERR" in \a\aline #"ERL:STOP
360 :REMARK \t\tAdd your own sentences and words.\t\n\t\t\tUse this format.\t\n    DATA "SENTENCE FOLLOWED BY THE WORD THAT US SPELLED WRONG.","WORD"
370 DATA "THE YELLOW CAT JUMPED OWVER MY FOOT","OVER"
380 DATA "I WISH THAT I DIDN'T HAVE TO GO HOM","HOME"
390 DATA "WE AR GOING TO PLAY A GAME","ARE"
400 DATA "YOUR SISTER HAS A PRETY TURTLE","PRETTY"
410 DATA "GESS HOW OLD I AM","GUESS"
420 DATA "HIS NAM IS ROBIN","NAME"
430 DATA "IT IS GETTING VERRY LATE","VERY"
440 DATA "I WILL TEECH YOU HOW TO USE THE COMPUTER","TEACH"
450 DATA "I THINGK WE HAVE DONE ENOUGH","THINK"
460 DATA "I DON'T THINK WE HAVE DON ENOUGH","DONE"
470 DATA "OUR DOG HAS WITE FUR","WHITE"
480 DATA "WINTER WILL BE HEER SOON","HERE"
490 DATA "WE WILL BE ABLE TO PLAY IN THE SNOE","SNOW"
500 DATA "IN THE SPRING, THE FLOWERS WIL BLOOM","WILL"
510 DATA "THE LEAVES WILL BE GRENE","GREEN"
520 DATA "THIS IS THE LASD QUESTION FOR NOW","LAST"
