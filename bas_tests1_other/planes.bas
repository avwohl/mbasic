10 :REMARK \t\tPLANES.BAS\t\tVersion 05.02.81
20 :REMARK 
30 :REMARK Description:\tA video game of target shooting.
40 :REMARK 
50 :REMARK Author:\tTerry L. Perrino\tClaremont High School
60 :REMARK 
70 :REMARK \t\tModifications by H.U.G.
80 CLEAR 5000:WIDTH 255:DEFINT A-Z:GOSUB 890
90 E$=CHR$(27):E1$=E$+"E":Y$=E$+"Y":F$=E$+"F":G$=E$+"G":P$=E$+"p":Q$=E$+"q"
100 Y5$=E$+"y5":X5$=E$+"x5"
110 P$(0)=" oaxa":P$(1)="ayan ":P$(2)="     "
120 FOR R=0 TO 5:READ G$(R):NEXT R
130 DATA "3^y^0","2^y^0","1^y^0","0^`^0","0^x^1","0^x^2","0^x^3"
140 FOR R=0 TO 9:READ GS$(R):NEXT R
150 DATA "4*y*0","3*y*0","2*y*0","1*y*0","0*`*0","0*x*1","0*x*2","0*x*3","0*x*4"
160 H$=E$+"H"
170 GOSUB 660
180 PRINT E1$Y$"+7Type any character to begin play"Y5$;:A$=INPUT$(1):PRINT X5$;
190 PRINT E1$Y$". "F$;
200 PRINT "       (zzzzzz)                                            (zzzzzz)"
210 PRINT "     (zz      zz)                                        (zz      zz)"
220 PRINT "      zzzzzzzzzz                                          zzzzzzzzzz"
230 PRINT E$"x1"Y$"8 ";
240 PRINT "HITS: 0 bwbwbwbwbwbwbwbwbwbwbwbwbwbwb0^`^"\n\t"0bwbwbwbwbwbwbwbwbwbwbwbwbwbwbwbwbwbwb"
250 IF INT(RND(1)*15)+1<>10 THEN 300
260 IF S>2 THEN 300
270 :REMARK \t\tMAKE NEW PLANE
280 S=S+1:IF INT(RND(1)*2)=1 THEN PX(S)=3:PD(S)=1:PSD(S)=0::ELSE PX(S)=73:\n\tPD(S)=-1:PSD(S)=1
290 PY(S)=INT(RND(1)*3)+2
300 IF S=0 THEN 280
310 :REMARK \t\tDELETE OLD PLANES
320 FOR F=1 TO S:PX(F)=PX(F)+PD(F):IF PX(F)>=74 OR PX(F)<=2 THEN 370::ELSE\n\tIF B=0 THEN 350::ELSE FOR F1=1 TO B:IF BY(F1)<>PY(F) THEN 340
330 IF BX(F1)>=PX(F) AND BX(F1)<=PX(F)+4 THEN 380
340 NEXT F1
350 IF PY(F)<>SY THEN 360::ELSE IF SX=>PX(F) AND SX<=PX(F)+4 THEN SY=0:SX=0:\n\tSB=0:GOTO 390
360 NEXT F:GOTO 410
370 PRINT Y$CHR$(PY(F)+31)CHR$(PX(F)+31)P$(2);:S=S-1:IF S=0 THEN 420:\n\t:ELSE FOR Z=F TO S:PX(Z)=PX(Z+1):PY(Z)=PY(Z+1):PD(Z)=PD(Z+1):\n\tPSD(Z)=PSD(Z+1):NEXT Z:GOTO 360
380 B=B-1:FOR F2=F1 TO B:BX(F2)=BX(F2+1):BD(F2)=BD(F2+1):BY(F2)=BY(F2+1):NEXT F2
390 PRINT Y$CHR$(PY(F)+31)CHR$(PX(F)+31)"\a*BOOM*"Y$CHR$(PY(F)+31)\n\tCHR$(PX(F)+31);"       ";:H0=H0+1:PRINT Y$;"8 HITS:";H0;H$;:GOTO 370
400 :REMARK \t\t\tPRINT SHIPS
410 FOR F=1 TO S:PRINT Y$;CHR$(PY(F)+31);CHR$(PX(F)+31);P$(PSD(F));:NEXT F
420 IF B=0 THEN 480
430 :REMARK \t\t\tPRINT BULLETS
440 FOR F=1 TO B:PRINT Y$;CHR$(BY(F)+31);CHR$(BX(F)+31);" ";
450 BY(F)=BY(F)-1:BX(F)=BX(F)+BDX(F):\n\tIF BX(F)<=0 OR BY(F)<=0 OR BX(F)>=80 THEN 460:\n\t:ELSE PRINT Y$;CHR$(BY(F)+31);CHR$(BX(F)+31);"^";:NEXT F:GOTO 480
460 B=B-1:FOR Z=F TO B:BX(Z)=BX(Z+1):BY(Z)=BY(Z+1):BDX(Z)=BDX(Z+1):NEXT Z:NEXT F
470 :REMARK \t\t\tPRINT GUIDED MISSILE
480 IF SB=0 THEN 500
490 PRINT Y$CHR$(SY+31)CHR$(SX+31)" ";:SX=SX+SD:SY=SY-1:\n\tIF SX<=0 OR SY<=0 OR SX>=80 THEN SX=0:SY=0:SB=0:\n\t:ELSE PRINT Y$;CHR$(SY+31);CHR$(SX+31);"*";
500 REM
510 :REMARK \t\t\t INPUT ROUTINE
520 DEF USR0=VARPTR(U0(0)):G=USR0(0)
530 IF G=69 OR G=101 THEN 650
540 IF G>58 OR G<52 THEN 300
550 ON G-51 GOTO 570,580,590,600,610,620
560 GOTO 300
570 IF BDX<=-2 THEN 630::ELSE BDX=BDX-1:GOTO 630
580 IF B>2 THEN 250::ELSE B=B+1:BX(B)=40:BY(B)=23:BDX(B)=BDX:GOTO 630
590 IF BDX>=2 THEN 250::ELSE BDX=BDX+1:GOTO 630
600 IF SD<=-4 THEN 640::ELSE SD=SD-1:GOTO 640
610 IF SB>0 THEN 640::ELSE SB=1:SX=40:SY=23:GOTO 640
620 IF SD>=4 THEN 640::ELSE SD=SD+1:GOTO 640
630 PRINT Y$"8E"F$G$(BDX+3)H$;:GOTO 250
640 PRINT Y$"8E"GS$(SD+5)H$;:GOTO 250
650 PRINT E1$Y$"+?"G$"* End of session *"E$"y1";:GOSUB 900:RUN"MENU"
660 :REMARK \t\t\tINSTRUCTIONS
670 PRINTE1$X5$Y$" 9* Planes *"
680 PRINT Y$"##The game of PLANES is a target game in which you try to hit"
690 PRINT "as many planes as you can with your missile launcher.  A maximum"
700 PRINT "of three planes will fly randomly accross the screen.  You are"
710 PRINT "given a maximum of three regular missiles and one guided missile"
720 PRINT "to shoot at one time.  The commands to shoot the missiles are as"
730 PRINT "follows:"
740 PRINT Y$"))Regular Missile"Y$")OGuided Missile"
750 PRINT Y$"+'4-TURN GUN LEFT"Y$"+M7-TURN GUN LEFT"
760 PRINT Y$",'6-TURN GUN RIGHT"Y$",M9-TURN GUN RIGHT"
770 PRINT Y$"-'5-SHOOT MISSILE"Y$"-M8-SHOOT MISSILE"
780 PRINT Y$"/'(NOTE: GUIDED MISSILE IN MANIPULATED ABOUT THE SCREEN
790 PRINT Y$"0.BY MOVING GUIDED MISSILE GUN AROUND)."
800 PRINT:PRINT "WARNING:  Do *NOT* get your guns mixed up!  The regular gun is surrounded"
810 PRINT "by solid circles, and the guided missile gun by asterisks."
820 PRINT:PRINT "To exit the program, type 'E'.  Happy shooting!"
830 PRINT Y$"70Hit any key to continue. "Y5$;:A$=INPUT$(1):RETURN
840 END
850 DEF USR0=VARPTR(U0(0)):X=USR0(0)
860 IF X>96 AND X<123 THEN X=X-32
870 I$=CHR$(X)
880 :REMARK \t\tReal Time Function for MBASIC
890 DIM U0(3):U0(0)=&H36:U0(1)=&H1FF:U0(2)=&H77D8:U0(3)=&HC9
900 DEF USR0=VARPTR(U0(0))::REMARK \t\tClear Buffer
910 IF USR0(0)<>0 THEN 910
920 RETURN
