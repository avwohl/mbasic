10 :REMARK \tGAMES.BAS
20 E$=CHR$(27):Y$=E$+"Y":X5$=E$+"x5"
30 PRINT E$"H"E$"E"X5$E$"F"Y$"#8faaaaaaaaaaaaaaaaaaaac"Y$"$8`fac fac fcfc fac fac`"
40 PRINTY$"%8`` c vat ```` va  eac`"Y$"'8`"Y$"(8`"Y$")8`"Y$"*8`"
50 PRINTY$"&8`ead u u uedu ead ead`"Y$"+8eaaaaaaaaaaaaaaaaaaaad"
60 PRINTY$"'M`"Y$"(M`"Y$")M`"Y$"*M`"E$"G"Y$"';1. Scenic Drive"\n\tY$"(;2. Hangman"Y$");3. Tic Tac Toe"Y$"*;4. Lunar Lander"
70 PRINTY$"35Your choice? (1 to 4) <END>"E$"y5";:A$=INPUT$(1):PRINTX5$;
80 IFA$=CHR$(13)THENPRINTE$"E":RUN"MENU"
90 ONVAL(A$)GOTO120,130,140,150
100 PRINT"\a\a";:GOTO 70
110 PRINTE$"E"Y$"+2Loading..."
120 RUN"SCENECAR
130 RUN"HANGMAN
140 RUN"TIC
150 RUN"LUNAR
