10 :REMARK  NUMBER.BAS Version 04.22.81
20 E$=CHR$(27):P$=E$+"p":Q$=E$+"q":Y$=E$+"Y":Y5$=E$+"y5":X5$=E$+"x5"
30 CS$=E$+"E"+P$+Y$+" 0 Guess a Number "+Q$+Y$+"# "
40 Q=0:PRINT CS$Y$"#(I am thinking of a number between 1 and 1000."
50 G=INT(1000*RND(11))
60 PRINT Y$"-0"Y5$;:INPUT "Your Guess=";A:PRINT Y$"-0"X5$E$"l":IF A<>G  GOTO 110
70 Q=Q+1:N$="("+RIGHT$(STR$(G),LEN(STR$(G))-1)+")"
80 PRINT Y$"0-You guessed my number "P$N$Q$" in"Q"tries!!"
90 PRINT Y$"2-Do you wish to play again? (Y or N) <Y>"Y5$;:A$=INPUT$(1)
100 PRINT X5$;:IF A$="N"  OR A$="n"  THEN  RUN"MENU" :ELSE 40
110 Q=Q+1:IF A<G  THEN H$=" LESS  " :ELSE H$="GREATER"
120 PRINT Y$"+(" USING "####";A;
130 PRINT " is "P$H$Q$" than my number\a\a... Try again!  "P$USING " ### ";Q
140 PRINT Q$Y$"% "E$"M":GOTO 60
