10 :REMARK \t      WINNING.BAS
20 :REMARK    Written by Evan J. Callahan
30 :REMARK    Date Completed:\tAugust 1981
40 :REMARK 
50 :REMARK    E. Callahan
60 :REMARK    2514 169th N.E.
70 :REMARK    Bellevue, WA 98008
80 :REMARK 
90 :REMARK \t  *** GAME BEGINS ***
100 :REMARK 
110 :REMARK Set variables
120 E$=CHR$(27):F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q":Y$=E$+"Y":D$=CHR$(95)
130 :REMARK Set up screen
140 PRINTE$+"x5":OX=RND(-PEEK(8219))
150 PRINTE$+"E"Y$" 8***WINNING***"
160 PRINTY$;CHR$(34);" *PLAYER:";Y$"- *COMPUTER:"
170 PRINTY$"#G# # # # # # # #"
180 PRINTY$"$G#  1=Paper    #"Y$"%G#  2=Well     #"Y$"&G#  3=Rock     #"
190 PRINTY$"'G#  4=Scissors #"Y$"(G# # # # # # # #"
200 PRINTY$"-B"F$"^^^^^^^^^^^^^^^^^^^^^^^^^"Y$".B`"Y$".Z`"
210 PRINTY$"/B^^^^^^^^^^^^^^^^^^^^^^^^^"G$
220 PRINTY$".C  Hit <ESC> to quit...";:FORX=1TO500:NEXTX
230 :REMARK 
240 :REMARK \t  Start playing
250 :REMARK Update score and erase pictures
260 PRINTY$;CHR$(34);"+";PP;Y$"-+";CP
270 PRINTY$"$ ";:FORX=1TO5:PRINT"                    ":NEXTX
280 PRINTY$"/ ";:FORX=1TO5:PRINT"                    ":NEXTX
290 :REMARK Computer gets random guess
300 CG=INT(RND(1)*6)+1:IFCG=5THENCG=1:ELSEIFCG=6THENCG=2
310 PRINTY$".C      I'm ready...    ";:OX=OL:OL=G
320 I$=INPUT$(1):IFASC(I$)=27THEN940:ELSEG=VAL(I$):IFG<1ORG>4THEN320
330 :REMARK Paint player's guess
340 PRINT Y$"$ ";:IF OX=1 AND OL=1 AND G=1 THEN CG=4
350 ON G GOSUB 680,740,810,860
360 :REMARK Paint computers guess
370 PRINTY$"/ ";
380 ON CG GOSUB680,740,810,860
390 WF=0
400 ON G GOTO 420,430,440
410 ONCGGOTO530,570,590,470
420 ONCGGOTO470,490,510,530
430 ONCGGOTO490,470,550,570
440 ONCGGOTO510,550,470,590
450 :REMARK 
460 :REMARK Print guess messages and figure who wins
470 GM$="     It's a tie...    ":WF=2
480 GOTO600
490 GM$="  Paper beats well... ":IFG=1THENWF=1
500 GOTO600
510 GM$="  Paper beats rock... ":IFG=1THENWF=1
520 GOTO600
530 GM$=" Scissors beats paper.":IFG=4THENWF=1
540 GOTO600
550 GM$="  Well beats rock...  ":IFG=2THENWF=1
560 GOTO600
570 GM$=" Well beats scissors. ":IFG=2THENWF=1
580 GOTO600
590 GM$=" Rock beats scissors. ":IFG=3THENWF=1
600 PRINTY$".C";GM$
610 FORX=1TO800:NEXTX
620 :REMARK Add point to winners score
630 IFWF=2THEN260:ELSEIFWF=1THENPP=PP+1:ELSECP=CP+1
640 GOTO260
650 :REMARK 
660 :REMARK \t  Subroutines to paint charachters
670 :REMARK paints paper
680 PRINTF$"   "P$"r       "Q$"r"
690 PRINT"  "P$"r       "Q$"r"
700 PRINT" "P$"r       "Q$"r"
710 PRINTP$"r       "Q$"r"
720 PRINTG$:RETURN
730 :REMARK paints well
740 PRINTF$" "P$"rl"Q$"pppp"P$"m"D$
750 PRINT"r"Q$"r      "D$;P$;D$;Q$"fa"
760 PRINTP$" "Q$"aaabbaaa"P$" "Q$"d"
770 PRINTD$;P$;D$;Q$"      "P$"r"Q$"r"
780 PRINT" "D$;P$"oppppn"Q$"r"
790 PRINTG$:RETURN
800 :REMARK paints rock
810 PRINTF$"  "P$"r    "D$
820 PRINTQ$"  "P$"      "
830 PRINTQ$"  "D$;P$"    "Q$"r"
840 PRINTG$:RETURN
850 :REMARK paints scissors
860 PRINTF$"   "P$;D$;Q$"  "P$"r"
870 PRINTQ$"   "D$;P$;D$"r"Q$"r"
880 PRINT"    "P$"  "
890 PRINTQ$"  {"P$"r"Q$"r"D$;P$;D$;Q$"{"
900 PRINT"  "P$"on"Q$"  "P$"on"Q$
910 PRINTG$:RETURN
920 :REMARK 
930 :REMARK End game messages
940 IFPP=CPTHENGR$="   It's a tie game!!  "
950 IFPP<CPTHENGR$="    I win the game!!  "
960 IFPP>CPTHENGR$="   You win the game!! "
970 PRINTY$".C";GR$:FORX=1TO1000:NEXTX
980 PRINTE$+"E"+E$+"y5"
990 END
