
10 81$Jt  43E=ERhg0aaaaRemote Bulle (tD rd Progra
20                                                  $o+saVersion 0C$Serforms The SignR) Functio I& 4dem I/O
V 03iSeOee 43  O.DOCC$0' Author - $ss Lane(=G: 21/82  -1s"D TTT2   2 -T
H1
40 81$o ipesHMRO+737OS, Sugge (gS" t:ModiT ations,1L35
EI A 
0$U(1111111111111111111111111111111111111111111111111111111111111111111111111111111111111:M  e Than Welcome.  +t'51-  LT-O$TOI:31(151-0168 (data))))       '
6B2 -ZFT$(DATE$,6)+R 50101 UaR(29(ERA=PRo dG1$i A8
80 DEF0T A-Z : CRiLQN11I:: $G:(10) TB$SV#1LR1 =0S,MLiLQNA
MSV#Ayn+CH0A
: R(iuG$(29)+CHR012)+CHR$(29)
95 G 0esN0 : GOTO 200
1               Write Record #, Msg , tSi ray -L

5Q)5sE #1,2 : DIM M(5,2)    'M(Record #,Msg #)         5 is max # of sgs.
1E$-hESO0R,00T01," OU :O)L  FIELD #1,128 AS R$
10S==COL :0at "$,CH01126))>THEBNSi=1$TiIf it's killed....3$0O oHR0h1C0B20I2 0318)) : IBNSie= $0350 ELSE IO d =0360
140 oGBB12$=K3AST 1E.:M(,t $1L)i-9 : (A0$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$5))2G=0O E2 .:DEAD=0 GOT120
1,FIRSTM 10$1I: LA:TiS0 N 2) RAv$N0 $o02FC-i$F$3EUB   to Ill --------------------------------------
21SO0R,"COM1:300,E,1" AS #3
220 PRINT "s$n-onO FoTBTOEO32"
20SiSZ I0A1YS F IR O$=CHR$(27) THENDFCIA"sop iu.":CLOSE  LOC5E(e G4s:78((S WEN
23OT O0G:6HAU#11,3L):BB"RRT)13) : WEN
24A"S)eOO
 $BI:$0,0,0,E MRH0F,:I$= ME$
760h"Do14u need line feeds ? ":CR=15sUB 1400:Z$=INPUT$(1,#3 GOSUB 560
255 IFP72o
4GmN LF=-1 ELSE IF Z$="N" THEN LF=0 EL:GO0s3400:GOTO 25'57 A$=Z$ : CR=2 GOS sYU8(S0 RET=1:"H=1B=T6Z$="WELC 0Re:GOSUB 6000000000000000000000000000000000'S  EnableS  ( rrupts (CtU-K)
-0OG':S =e FILEne0iETII GOSUB T 0TeN=o0"L0 Returno H:e From ^8
280 C'5sUB 1400:TRIES=0:STI=0 ATn nterT ts OffC$0:,2isTRSIlle$M0Ime ---------------------------------------------
305 I-+ ES>5 TH,120000 ' L oGNQ0BGUy
310 TRIES="=c
1:GOSUB 1400:An(8V6TuB0T=Te- RST Name":G 0esLlTC+N:0:h0 THEN 300 H  E=O :tA):GOSUB 560:E$B=Z$:IF Q=1HEN 34 130PV(2):GOSUB 50A=GB3  R dGo(8
340 A$="What is >Te  LtrName":GOSUB500
30HPVu(4O5s L7O,ti:=O
370 IG:$FIRST$L$9DSN(LA1  Oe= $0SN0
3,IF FIRSTn RASS" 0D LAS XTBMeTHEN 40$E0FRlace SysoTnaPasL1 $E53SFD H,NAhFIRST$+V#Ay
LAST$
400 IF INSTR0AM$,"SYL0DNSTn(+T 0$0 40GW0E")THEN250$.4g-OT"OCSeguy
410 FOR Q=1 TO LEN(NAM12=10 X=ASC(MID$(NAM$,Q,1N=6 F (X<65 OR X>90) 0D (X<>32 AND X<>39) THEN 300
440 NEXT : GOSUB 1400 : GOTO 500=H,FIRST$="RUSS":LA1 $OTI QM$="SYSOP":SYSOP3BOmLL=0:XPR=-15A $32
500             ' L0L0TSdS3-aller ---------------------------------------------
51SO0R,"I",#2,"LASTC5e: IRUTT(Q                                 0wO0 : CLOSE #2
520 IF NAM OIN-7O0 600
530 LA
)iP=-1 : A$="Welcome back, "+FIRST$ : CR=2 GOS sYUEFSH04410
600             ' Check UB   File ----------------------------------------------
610 LnM.T5 (tNlser FilLMS0" : CR==ELlB S0r1 O $#0T02,"USERS"
630:0:dln TO0 CLOSETe GOTO 700
60aNP$T02,N CI 3 0)0(,ST76 F NAM OIN-7O0 630
660  H rFN2
6,IF STATUn a"2=LAO$0TiCan AccessysG,8
6,GOTO 12530                Lo-Off We A l
700                                                  iGeRU wCTSF2s Background -------------------------------------
710 d)iP=-LT10 A$0A
6TRR0X4Ire you caUing f4m":GOSUB =0LU IF Q=0 THEN 300 H  E=O :tA) : GOSUB i AQXhZ$
740 A$="What STATE are14u calling from":GOSUB 15
750 mlEe= $0H)N H  E=O :tA) : GOSUB i AEB)0(PZ:R8
7,A$=TB$+NAMO5sU340 = -0hTB2 "=O$+", "B)0R=$B4$LSBU sYU<00 AnNB0B)= Ico  ect":GOSUB 15:GO0s3400:IFd40d=L,$$0LTLUH REN "A",#2,"USERS" : WRI:#2,NAM$,CITY$,STATE$,")" : CLOSE #2
L560h+=is is only done the f  st time you caU, "+FI (I: CR==ELlB S0DN0                                                  iLog To"sG0T7i(M# LnJ1RT ng "+NAM$+B)SH(sG0Tx60" CR=2 : GO0s3400
82SO0R,"O",2,"LtMN98e: Cc=CAL0+1C"#  
 TE #2,NAM CAP,: CLOSE #2 cREN "AFN2, "$OHHs"
H,PR0T #2,TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT  ";D$;"  ";TI$ : CLOSET"S0 IGB+)iH MOTMN9)c.nSGoGmN 1040 ' Bypass Searh For$3R
90r,2iSearch f   a+L0-sages to this aller -----------------------
920 AnNTeB0t ing if L0sFrare messaes  Ii$T1RFr you...."S$uhEsUB 1400
930 X=37:Y=31:F$=NAM$:T=0:DONE=043
50 GE1,R R =h1C0B20I2 "fMN=E$:4D/m
d4GmN5TTiVIF INS2+$ D$( 0SL00S"n,NtD)lEe= $0R"EcL5U5=AS F T THEN040 ELSE 103iP"6 F T TH,1020
990  A$="The following mess Nt "RcIs/were left for yTnONELSBU sYU8
10000 A$="Pl0B0r(K)ilSTLCT:tS Rd4uld not inteB 1-$RX7B   calle 12"#10 GOSUB 14:T=-1
100hLE30I,5):CR=O5sU340SH04g578
100h"NoTR SQiG,TS3Sees $R: you,T t'A $B4$hH t 100)0XBring 7BR 1S3See SubW1 1-L0R R  A/G 0esYU8
5US5
)0(=$L= 1:PRINT SPAC0A01 =RUn(+M"#));NAM$;"  ";TI$
1060 XPREFS S-1 : MARGIN= 8 =RET=0 GOSUB 400 S =i: GOSUB 1700+N0             ' Command Dispatcher -------------------------------------------
1210 "H=1BPE0 E ht+U1Interruptsn, eturn To HerP) $)T0 e 1+
:ON=ST1+1$5sUB 1400
1O,IF SYL>L,$5sUB 100000
1250 An0E<s on"
1S0 IFdnO >EN A$=A$+KH 0 C7O75U=),EO0 Q,R,S,X,Y,#,$)X8e-0SH tTS7,6 F =0 THEN 121;0: S)$O -oGoR8
1 =E$=B$(D ctTS5U013$00:   - NSTR("3R IS5," 5N$RSXY#$%^&*(",Z$)3)N IF FFEe=033,ELSE IF FF>15 0D NOT SYL>L,$1aA8
132$C 0
UMgE0Es$:C         G      H      K0
 0x$UIt8C3330 ON msUB 1700,T10,18,20A+NNNN,1740,  =FG200,250G(20, 4320, 
                  43 0G"AF 4UOLU30100,10120,1N0,GAF 10600,1"U"Y,'            S     X , Y     #                                                                                0$UI      ^0"Q*      (
G=0$  ="$$O0SH04s
N((0 IF PR THEN G=0:GO:ELSBUnS0
1370i: R1 AFa don't underst)d "+B$(J)5sUB 1400:GOTO 1200
1,'
+7F2)S00$R$9+FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF estrin -------------------------------------------------
140)ShIN:)SFaF LOCZ,$03430
140aF I0A0-7O0 1430
1410 Y$=INPUT$(1,#3)
140aF Y$=CHR$(19) THEN$P6Z EOA(N=EAI 
$E0F2 Ctrl-S
1430 I)ShCHR$(11) AN S  THEN 1480 +U1 Ctrl-8
140GPDUaE0  PRI$N0=6 F LO0h-7On:78
R=H 
 NT #3UA8
1450:0$BiTHEN :-1)U5CN$ i::0GPDT :TO0 1465
$9$+ NT6ARy : IF LF THEN PRINT #3,C 
LF$)56 F $uoGmNg :d 1S0
14,Y$="" A$=1/CR=FO0=AvT2)XN CLOSETi: A$="++1o4rtS4M": B 0esYUEFPAPo dGGTF 280
1490ETU,1200
15             ' Input string -------------------------------------------------
1510 A=0:U==0:Q=1H9l=)O7E B$=""2GO# A$=A$+" ? "
1530:0S, :m1 R$(""eR=1 : G 0esYUE0:0GPDT :THEN 0PUT "",B$ : GOTO 1575
150SiSZ I0A15$C4TQ EY$ : IF Y$<>"" THEN 151
1554$  2GVUR:A)70$00T$A 12GV$:AaFShCHR0)HEN 16T2GVR:ARINT Y$; : PR0T #3,#
1566 AaF Y$=C0-7O0 157( HS8    B$=B$+Y$ : GOTO 1550
1570 Hme= $0HD0i#3,CR$+LF$
5,V,T BB2Tu,nn : IF A=0 m3640
1,B$(1)Z30A,((22GP  TQ BB2+1,B ";")
1 Bs:r(0
1) IF C<1 THEN <:T3 : C=0Te7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF 4$res all rightmost characters
1590eiXR6)NA i0
1,C)
1U6 STu<>""HEN Q=Q+Ou(Q)=BB$
1#:0$ SiEOL mFSH04sL"310 IF:$0A i.)uN THEN A$="Try again, "  (PS0=ELSBU o00 : G4sLlT2asN RETURNa1O,B$(L t  IF B$y THEN Q=0
1650:0G:: (Ai03)="Y" OR LEFT$(B 1T1+
4GmN YES=-12arAE$ -0 T(0G6 F:$0A i.U=LASL5l"(
0ST -ZFT$(B$,LEA i3312a1 =0HD0$ iBK1$; : PR0T #3,R 
 : GOTO 1550
1700                                                                                      1 ? Type Funct4ns Supported ------------------------------------GT# FIL XELP02":G 0e4S60:=AvT X$lMTiTyT:Blletinsi =v
1730 6Z$="BULLETIN":B 0e4S0000:RE08T( uS0$UMTi"pe L0( 0hET$E: 
,7E (S$="O5R
  GOSUB0i A=O0=AvT2N0            ' Com" i(rH"(# GOSUB 14:A$n+:07=t2aare only readable by Sy4p. GOSUB 1400:MARGIF3O"(10 A$i "ou 0CS6T4 leave any":GOSUB 15
180aF NOT Y0-7O0 A$="No commen cesYU=O0=AvT2Y,LI=B
 M A$(31LlO50esYUULn0XB3ST  to 20 l)es. (loneL  R to end)5sUB 1400
1 AELSBU o00:GOSUB"AT23.Oi+  LI=LI+1:A$="    "+g$OEM"NF
A$(LI):IF LI<10 THEN A$=" "0'f0 CR=1 : GOSUB 1400 : GOSUB -013 =0aF A$(LI)="" TH,LI=LI-1:IFa<THE:ON=oPE08,ELSE 19402+7US Fa=18HEN A$="Two3 nS B8B+OrA)  B 0esYU8+dAS F LI=19 THEN Ln9Ist line. GOSUB 1400
1920:0Ga=20 0D NOT SYL>L,$0h"Comment =o,0
ONELSBU sYU=SH0S
cW1+H# GOTO 1870
1940 OP,"A"N2,"RCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC$ e11"b5lO5sUB 1400:An
TF" tS ,iIfor the comments)TE$iELSBU sYU8
1960 PR0T #2,T D$,TIME1+5E )=>1 TO LI:PRINT #2UA0>$  ="8(<80 FOR X=1 TO 2 :PR0T #2,V#1((oRF7Nr H rFN2:ERASE A$:RETURN
20000            ' EnB   A B 1Sege --------------2#10 B 0esYU=-h"":PAS$="":LI=G7E X=0:cIl8
2N DIM A$(3140 A$?B 1Sege will be # "+STR$(LAX(n : GOSUB 14
2050iXTT.$SX B9C/R  For 0 0
XFSH tTS3500#,IF LEA #1(C110 THEN A$010 L Irs ax.":GOSUB 1400:GOTO 20170 IF Q=0 THEN T$="ALL" ELSE Z$=B$(1)5sUB 50000:T$=Z$
2"60h"$bject"5sUB 1500
2090 IF:$0A #1(C14$L:THEN A$nL:Char7dRPnONELlB S0 ELSe$$N80
2100:0:h0 THENIH,ELSE Z$=B$(1)5sUB 50000:SUB$E$n"AS="ProGOSR                                 R,N,?>":mO GmN 213'120 Ln Q35sT ==)>ill, <RTOEOU:<4$S , <?517TTKX8$"(AO5sUB 1500:Z$=LEFT$(B$3tS14O50eLLLL:IFP72A27O0290nYE E$="?-7O0 FHP7N7O5R03":GOSUB 60A=Se$$10
210aF Z$="K" THEN 2170
2160 IHP7N8eTHEN 0 g="^READ^ GOTO290nIL=Se$v0
2T,A$="P 1d:d":B 0esL1;0aF LEN(B$3D)-L:THEN A$="15
=arsL0OQO1L
 cesYU=SH0R)L(v
2185 PAS$=B$(1)n
7ELSBUnS00:0=.D=EN 2212
2200 Ln0
STXB3SFTS36$e,3NA0rin lines
  GOSUB400
2$0h"O-H(00("pe lone C/R.    20 liB Imax.":GOSUB 14
22$h"Rihttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttrgin is set at"+g+$0S oO5sUB S01y2)C
S):#$CSh 4 chane iNELSBU sLlT2y26:0)S OEe= $0 SN=-1:GOTO 3100
2218 BEGIN=SH tTSS
N''''0 R$="" : LTdO2  A$="    "+S101 S )+": "+A$(LoS F KdA=L,S0h"y0'2y(CR=1 : GOSUB S0 ELSBU170'240 IF AiS )=1=LASOGa-1:GOTO 2310
2250 dH38 THEN Ln0
O$S=(tSaleft....":GOSUB400
2S0 IFa=19 THEN A$iO63-ine.":B 0esYU8y -0aF LI=0W0D NOT SYSOP THEN An
3SA ge full."5sUB 1400:GOSUB(AT2y;5A $$
600
200'Editing dispatcheri =T
#SH tTS3400
2310:0=.D=EN A$="Funct4n dC,D,EE0G S
$)XFSH04g1)S1(yAS0h"Functions : <A>bort, <C>ontine, <>elete, <EH(sUK  B 0esYU8((# A$=" ,H0)l2Sert,cUs3lFR  Irin, < 6 ve, <?>Help "2(nS5sUB 1500:IFL00-7O0 nN H  E=O :tA):GOSUB 560
2350 mo3 0D Z$<>"M" THEN L=NhA ARR:GO0sS20 'Te evaliity of lineT2((S0 FF=It "NMCIaLMS?",Z$):I:  OBo: nuZe= $0$10
237RA=ELSg00((F 7,aA,0$1
0 0SNNNN,3,0SY0$1+78
2380ce4yAEd 2250    'Con$T4 
2390 FHP7N7O5R04":GOSUB 60A=Se$$20nS0:,2n44rt --------------------------------------------------------nR$0SHU s000h"Do you onfirm 
RO-C 31I GO0s3500
2420 IFd40d=L,$3$01n-N GOSUB 14:A$#O B351  G 0esYU=
0BU4PE08,120'50r,2n+L011:AT B7i =v
25ELSTS30 6 F Q=1 THEN LnC273STBR0B43:GOSUB 1400:GOSUB 3300
2520 A$="LinT0"+ST01 OI: GOSUB 1400 : A$=A$(L) : CR$=ELSBBnS01eH# A$i  +:#$+S
irm Deleti)":GOSUB =01ecaF NOT YETHE)hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhBunbt 201 ODng SiDeB ( d.":GOSUB 14:GOC(#0
2550 FOR X=L TO LI0NIhA$(X+1):NEXT:LI=LI-1
2560 A$iuTA  "+STR$(L)+"" l-LS
FSH tT)S0 ELSe(#0(S00             'Edit A Line --------------1(S10 G 0esYU= 0:h1 TH,GOSUB 3300
2620iX$Xu0
STR$(L)2OTs :":G 0esYU=hA$(L CR=2:GOSUB 1400
2630iX,T1-sFESUdstring;Nee1uFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF $FQGFOt
oX change
  GOSUB400
2 SBU sYU=SH esLlT2(S50:0:h0 THEN 2300
2660 X=INS2$AS0NOtOu(1)) F X=0 m$LnN2(S8 O=LEA #1(C4Sc" THO0(B$(2oS F  2<>LB2 m$L(U"1LUR NB(A$(L),X)=B$(2):GOTO 2620
2700 Cn$ D$(AiOt72OR3CC$=/(N#1 Ot777777777777777777777777777777777777777777
2##OLi
+B$(C2 ELSg$N
2720 A$="Strin  '"+B$(1)+"' not fT0<1uTIliBR0
STR$(L):B 0esYU=SH04g1T2(UQE$"XB0s6T LiB7i =v
2810 DIM C$(30)
280SH tTS3400:IFL(4GN A$="Before  CR=1:GOSUB S0 ELSBU1300
2830 W=LI:7 S -L:FOR X=L TO L C$(X+1-hA$(X)0NIh"":N)i: LI=L
 OiX+  A BB10S "NF)E OKdA=L,$0h" "0'1<URS$-rGOSUB S0 ELSBU170'860:0N1 S )="-7O0 220(
=ASOE-OE
1(
0 IF E
K=18 m)0
 GUines left...."5sUB 1400
280 IF LI+K=19 THEN Ln9Ist line. GOSUB 1400
2900 IGa+K=20"B0OT SYSOPHEN A$="Messege full.":GOSUB 1400:GOTO 2920
210 GOTO 2840
2920 Fh>1 TO Ke A$(L>Mn=C$n> =  LI=W SeR1b0 ERASE C$ GOTO(ATC$i AQE$.$BeeLines -1
301LSBU sYU ctTSS
N0
3020 FOR X=1 TO LI:Ang60"BB10InM"NF)y0#In>aF X<10 THEN AnDT2USN30 GOSUB 14:NET:G 0esYU=Se$100
310r,2eA t RihtT66$) -08
3110 B 0esYU=aF Q<>THEST01(hB0 C4O5A n1$s""AS0h"SePight-Margin)ST0 16,24,32,40,48,S,64)  GOSUB500
3$0: S)=>8 TO 6O- Ho
6 F VAL(A'))=X THEN250LSE:="S"o0iX$  alid - Margin rema)s  y+S101C0 2OQ >SBU sYU=SH044nIAMnLlRQ N=VAL(B$(1)):Ln
T gin now set to"+STR?0 2$ O5sU340 1160 IF cA=L,$0118 ELSE 23
32             'Pri eTab Settingsi =T
nN B 0esYU=hTB$+"!" CR=1 : GOSUB400
3#cn: TO MARGIO- Ho
60h"--------
":C(  GOSUB400:NEXT:B 0esYU=O0=AvTC3$00$E0$2Test Line=oEberi 08
3310iX$================================= #":GOSUB =0 65 =)i-e#1 >TeRRINT B$31C"AS F L=3 AND TLGaHEN RETURN
  AUS FL00-7O0 =Av,2300
3340 IF 10tA'))<49 AND ASC #1 "o=4GmN RETURN 12
330h"No TR773 ne, " (P1 H t 10 ELSe$$1$0o00             'Sav)3S3Segei0sY# GOSUB S0 60hU0L6T$T1RRSg file.":CR=1:GOSUB S0sY10  H rFN2:OPEN "O",#2,"LASTCAe: LA:T6TM+1 : Lt oGBB1S>10 WRITE #2,NAM$,D$,TI$,STATUS,0wO0 : CLOSE #2
3440             '
=H,REC=0:Ln
S> R 0
T :BB1LASTM)+SPACE05TG:$0ItAiS0B8X$U11HMn:-0: $RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRNACo ONM0O0" ( =RUn(+T MN$1(S16
=0 T$=T$+SPACE011-LEA3 MN$F+t13T:L 1490UB$=SUB$+S0M0O0L7e=(SUB$))  
"176-100
3500 PAS$=0 g+SPA Re5( =RU0ON g))               '101nLR dA=EBC7iTOa:A$(JTUAnM"sV#1127):RECI$32HO0(A$(JoRF7NC R8
3520 IFEC MOD 128Ee=0$ hSTR$(REC128(N:GO:Q hSTR$(REC1281)
3530  H rFN1:OPEN 00T01,"MESSAGES" FIELD #1,12S0asL0 GET 1,LO1(9  128 : M(LASTR,1)=LOC(1)+1 : M(LASTR,2)O,t

355C3 STR,1)5
$1(C2$=K3$O,t N 2)=LASTM
3560 LSET R$=I0

FROM$+T$+D$+SUB$+PA 
C201125"IN=EO00isIAUR:,2eRO7-B"sG0)LS$R: ---------------------------------------------
36E )$OiTO LI0h".":CR=O5sU340 1620 FoR -oGCHT$0N1LCD8
360:R/"C0B2010#1LCt=611Ca1O,IF LEN(E14327 THEN L=J:R=HAUs R12ML=0$  ="$:"M(:=" RM(S70 ruOi:=HAUsrE$=""CaDN ERASE A$:RETURN
-00$UMT(0$EOGOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO:S 1O (r=v
3#49uG<
1 F LOCAL TH,X$=0PUT$(1) ELSE X$=INPUT$(1,3)
3720:0="CHR$(8) TH,3850 H  6 F X$=C201LR0-7O0 :O B01K
3730i:T10=QB43 : GOSUB400 : IF $=CHR$(9) m$G<uG<
(POS >L$"MeS0a="LiR$(3ITHEN 384 1750 I$G.o)$0$40$ TSCTA T1 uG:(32)HEN GOSUB400:GOTO&WsL00L $Co)2 1=ASQL<MARGIN+1 THEN uN
3780 mhC20A1ITO0 GOSUB400:GOTO&WsL=0H5n$0$4S1
00SiO0G:FR6)Ni0H7"9>" W0D 0B2R$,,1)<>"" ARDR6)NI2 031L)G:201L"M(# Z=Z-1:moU=LAOT0D ELSE GOSUB 1400:GOTO 3840
382049XR,2OQ 
1-Z : PR0T STRING$(R 29)+S"R6O01)7A8
3825:0$ SiLO0h-7OO $ $  S"R6O01)7O"4 e
  RsR = 32);
3830 A$(LhLEFT$(R$,Z)0N1 S +1)=RIGH0I2COL)5sUB 1400:RETURN
 N1 S )=AiS )+R$:COL=0:RAvS1lRSR H$G<TE$hLEFT$(R$,LEN(R4331C3"EO 
 NT BK1EFa$ s5
)iL,$0HD0$ i#3,BRT
C3.SH044euN
3900             'KillDBes ge ----------------------------------------------
 = GOSUB 1400
3910:0:2L)4GmN MM=NhA ARR:GOobO$s
P$0h"Ms # to KUl":B 0esL K+E)i-e#AC4O50esYUMbRaIIF MMEe=0O0=AAMbO$0:):h1 TO LASTR : IF M(Q,2)=MMHEN 395 GO:Q  ="8 1940 A$="No Msg # Y-T++TGOS sYU=O0=Av,1200
3950 GET 1,M(Q,1) RKiMID$( 0318)) IF SYSOP THEN 4N
360 Z=1 Z$ NB20I2 N1,15) : GO0sR00 PA :2C+PH,IF PAS$=RLNSi"RGe= $0aF INSTR2 0$(i"=LASS0 ELSE 4020
4000000000000000000000000000000000A$="P 1d:d":B 0esL110 IF#n=PAS$ THEN 4030
4020 A$="So  y Bc)O$ at, you lose
  GOSUB400:RAv+N0
4030 LSET R$=LEFT$(R$,115)+C201126)+MID$2 031"/00AS5
$1(22OTOE $>1 THEN GET 1,M(Q-1,1)
4050 M(Q,1)KiMID$(gEKi-
$ D$(R$,118))+R),2N=6O,t oGBB3
4AE  S):hQ TO Lt                                          3,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,1) 1 
1,1):M(Q,2)=2$1NEXT2OEE RSTM=M( 2) : Lt
En3$O,t N 22Ov0 An
$3T0 "+STR??????????????????????????????????????????????????????????????????????????????"2=)Uled.":GOSUB 1390:RETURN 12
4100             'Toggle LineT-HiI---------------------------------------------
4110 GOSUB 14:LF=NOT LF
4120 A$="Line FeSCK :0G:0= S0hA2I$"2=SH 0i-0C2I$T"2" $1$0SH tTS3400:RETURN
4150 ,2(+RRB4TBOSL0 01 
4160 GO0s3400:BELL=WOmLLOe-0h"Promptin Bell  IF BOZe=0hA$NR)" ELSE A(T 
"Of)G,GOSUB400:RAvG"A  ,2($$gle Experti01ON GOSUB S0 ETLC T0OT XPR2yAS F XPR TH,A$="Expert Mode" ELSE An"$
9BBR >O3R2O130 GOSUB 14:RETURN
4300 ,2(R=N9GLLGIXO=oEmary rRetrG al tL

431                                                 :T R00tE0LSe$G(o0 Qick Sca=XB$25O$T1X1=120 U=0 :RT=-1:SU=0:pRS-Y,'Retre a:Ent+LRoi 2=130tE0PT=0  0 E(iiiiiiiiiii'Summarize  Ent+LRoi 2=140dl=O05 4,E$O UFuRcIrd Flag, Reverse Fla, Read Protet FIg
476 F Q<>1 THEN MM=NhA ARR:GOC=190
4360iX+$3RFN  AY-$NA- RSTM"2SRAY-$$O,M)+" )":IF XPR THEN 438eTGT,IO0o0R,A$=A$+" toetreive ( C/R to end)"LSEiX6tartin at "+A$
(,G 0esLlE M:=)TTu(D" T+76 F V70tADlEe= $0O0 1200 EL:GO0s3400
4400 IONST$(A0 CtS="+"HEN FOW38e$R$ F RIGHT0tA0  03)=(2=L,$0O05 T3:pRSRA8
4420 FOR Q=1 TO LASTR
=10 IF CTA 
)3,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,2)=C=L,SROLU" )U6 TBaNne
:A1IOR QU OR SU) 0D M(Q,2T4)+L,$0Go90
47Q  ="  PRI$)"$S)$3RFN Y-T++TRETURN200
4S0 FOR Q=LADRSwTEP " $:-0a)3,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,2)7CC=LAS:A" $XN:="  A$="No Msg # Y-T++TGOS sYU=O0=Av,1200
4490 IFd=L,$0GUE GO:6 O0o0R,4530
4500 Q$ QA7 STR : QQQQQ=: pRS:N
4$0:::::::::::::::::::::::::::::::::::::=Q : QQQQ=1      Q, =-1=H1  S):hQQ TO QQQQ STE=$$$$$
4530 7sAR 1,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,1)
HeVE 0$ SiSYS)-7O0 Q BBR$,RLNSi"RT14AND INS2QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTL00-R,4590
4537:0::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::TO0 Z$=MID$2 0H,t5):Z=25:GOSUB 8100=H aF QU THEN L BB101C$,2))+"  "=O ELlB S0 ELSe$G (8
4550 GOSUBNNNN:IOl THEN 5- HS0 GO0s$$$$:IFT 0D (NOFOW AND NOT REV) TH,Q=15A $G(T2=5=ARF7NoR8
H,G 0esYU=h"End of M 2S.":G 0esYU=7008,1200
4590 IF FOLBJ HS)OH >$U mG 5-1= AUS0h"Sorry, "+FIRST$+"rMsg "+STR$(MM)+"Sarea protected."
4610 B 0esYU=:h05A $G(T2==A,,,,,,,,,,,,,'Y
=at --------------------------------------------------------
4710 GOSUB 14 :iX)+=ax60 Remote ConverItion Util (".=QB4$hELSBU sYU8
4720iXE+QR:am returns)SH ommand levelSithin" GOSUB 1400
4730iXT$0B0LS$S<1 Iif operatou unavail+73Re: CR==ELlB S01==o0 K=0 : A$="Alerting operatoXw" CR=1 : GOSUB400
4H,FOR I=1 TO 20
4760 BC T$-R5l,: NEXT J
47,K=K+1 : IF$ EY$=V#117)HEN 4830
4780 I:"RCCiTH,A$=CHR0=n CR=1 : GOSUB400
4LUS0h". =QB43 : G 0esYUEI ="$a GOSUB 1400
4800 A$="Sorry "+FC-C2AFT1 B4TSEItor available." GOSUB 1400
4810 An Rlease3OE1:a mess Nr) tT:board or in the comments."2=20 GOSUB 14 :ETUT2=30 GOSUB S00=60h"OpeItor is av$=0Ible." : GO0s3400
480h"GoR7GI................................... : C' GOSUB 1400
4850$P6Z EOA(N=60hINK 31=60 I$G:(8) THEN 4895 EL:IF A$=CHR$(27) THEN =Av,101=70 IF A$<)
4GN C(L  G 0esYUELSe$GfHTeT",WEND : A$=IN003(FNN=6 F A$=CHR0)HEN 4895
480 CR=: B 0esYUEFSH04sLl" T 5E $SpI"o3 THEN + NBK1$; : PRI$T03,BRT
2=97d 4817UR:,2'0 Conters ----------------------------------------------------
491LSBU sYU" )P$0h$UOou are calleu:A=nXTo e201DTO0):GOSUB400
430 A$eeeeee of Active msgs    -->"+STRiS0 24O5sUB S01OLGA$="0$O1-= BeNQh0U b=434)bt 2010B8X(n:GOSUB 1400:RETURN7$60             'Co ert  )OTSsIse to Upper Case ------------------------------
5010 FOR Z=1 TO LEN(Z$)9#$ $(Z$:3LiLQN10 1 2+$ D$(Z$,Z,1))+3:'$03 2+$ D$(Z$,Z,DiV"<$0$  ="$H  RE08T  A$6r,2?ommon RoutiBSTHMuT1-6eFiB7i =UrA3SO0R,"I",#2,FILE$
600aF EOF(2-7O0 CLOSE #2:RETURN
6N QS RUTT(60oO50esYU dGo$N
70000             'Commonoutine To Test                                                                             0 SC1 LTT$0S==COLC E:"$=1C)NI2118))
7N IF HiTO0 DONE=-PETURN- 10 R=oD<(GAF INSTR(MID$(R$,X,n,F$-7O0 RETURN- H dG9TT$
800000000000000000000000000000000000000000000'Proce IMSsage HeO3ST$UR",HO50esYUMT$0aF$ $(R 37(h"ALL" m-hT ":GOTON30C
'0 Z=31 : Z$=MR#I2 0=0 31) GOS 4#0 : T$E$6N Z=25 : Z$=MID$(R$,76,HN=ELSBU 
N0 S i:=ODN4=HS/Z$=MID$(R$, 6,31) GOS 4#0 : FROM$=Z$
E760hgNT0 " =T$( 05R 
" Date "+0B2R$,,8)+:e om "+FR 'C60 GOSUB 14 :iXU>F)10=EsUB 1400
80,A$="Re: "+SUB$ : GO0s3400 : RETURNT O =$R$DG4vOSeSTSaThat Pad Msg HeadeM#0 WHILE MID$(Z$,,1)=" ":Z=Z-1:0RTRL  Z$=LEFT$(Z$,Z) : RE08Ti=i AQUMT(T)pO7-B"sG0)LS$R: ---------------------------------------------
9005 GOSUB400
9010 Fh>1 TO V7?0B20I2 0318))-1
9020 <l60lEFSE00=QG01 = 10 GE1 A=INSTR(R$,CHR$(227)) A$=LEFT$(R$,A-1) : GOSUB 1400
9040 B=INSTR(A(E$RSV#1GUC1i= H,C=B-(A(N=6Qd =0$G HEOL3$TluT1Sures all rightmost haract:s
A60hMID$(R$,A(Q3I: I:P :THEN 908i= =AOSU340F:s=ELSe$$7GAHvs$-hELSBUnS0:NET GOS sYUEFO0=AA"#####             'Sysop's Util (t0=1  
$0(AS0h"Sysop's Uti$B3 es :":GOSUB400
10020 A$="   T(pQ+:07=t23I GOSUB 1400
10030iXB=+0E'NA0rCallers":B 0esYU8$0ehE :Purge FilI GOSUB S01$0 H,A$="  &  RenumberNh(  GOSUB 1400
10060 A$="  $E)4$rrect a$3RELSTS301$0 0h"  (  Print$3R3OEB  s":CR=2:G 0esYU=7008T2$(A  ,2((t81$(20 FIP72sRtO0n  GO0s:rA=O0=RN
10$0$E0$2% -81$((FILE$="CALLs":G 0e4S60:=AvTA100             'Purge --------------------------------------------------------$'10 CB  EQ(+,K
,OOL O)s0a"MES0L O)$0 "2=$=0 : B=0
1020cREN "R"N1,"MES0L O)$0 "N(=SM$(0 128 AS R$
10230 OPEN 00T02,"M 3U :O)gE0E(=SM$',128 AS RR$
$Y,GET 1
$LlS F$  "0$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$CHR$(225))>e= $030300
1IA6 F INS2QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQV#112724U=L,$N320
10270:0aNSTR(R$,CHR$(22M24U=L,$030330
102,GOSUB 14:A$(ARO8K$3RB0u NLSr:Y-TE$L>SH tT)S01$'85 A$="# of 

















































SaPurged :"BB1013
$1 =
1"o$5
$11:n
1"C4O5sUB400
10290 Ln =1P=Iding Msg FileMS0 GOSUB 1400:ERASE M:GOSUB 100:RETURN 1200$ US0:=)i-
$20I,11M22$ 110 An
$3T0"+LEFT$(R$,5)+" opie...................................:GOSUB 1400
1030GO:uO 2 :$N=EO0 2 : GOTO 10240
1030H15  R :iX+$3RFN" =T$( 05R 
" purged...." GOSUB 1400
1030S==CG 2$1D =)iMID$( 0318)) GOT10250
1040r,2e" numberie83E=0h"ReT +-B:sIrting with OLD msg #":GOSUB500:MM=VAL(B$(1))
10S0 IF++d4GmN4502$eET,A$="StartSith NEW #":GOSUB =0 KS:=)i-N1(CYY=Y F Y<1 THEN 1460
104,FOR Q=1 TO 1$e)76 F M(Q,2TD  =0O Tsssssssssssssssssssssssssssssssss1) GOT105102$ HUQ  0h60)"$S)$3RFNY-T++T  GOSUB 14 :ETUT2$ H# GCO H10 RR=VAL(MID$(R$,118N=6 F RR3 THEN 10290 )8 TR053 c uOi:BB1Y)+SPA R5TG:$0It 201onnnn+MID$(R$,6)
1SS0HAU0 LOC(1)$ =0)SXO+:  $CL d 1SN
10UQE0$2Resurretion -------------------------------------------------
10610 A$="Msg  to Resurrect":GOSUB500:MM=VAL(B$(1)):D 
d40R,145(I 1# R=1 : GOSUB 1400
10630 GCOL  4HR0h1C0B20I2 0318))
1sL:IO d =0h"No$3R0"+STR???????????????????????????????????LSBU sYUE$ -00
:1O,IF VAL(LEF0I25))<>MM TH,R=oD/GOTO 10630
10H,IF$  "0$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$CHR$(226))Ee=0306802$  rSH  uOi-ZFT$(R$,115)sV112C2g $(R 1UN=EO00i1,LO3(2I LT,An
$3T0"+ST01CC21uB2 )OEIlive )d welL  GOSUB S00=ELSe$'90
10680iX+$3RFN"BB101CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC1uB0T1 $TS+ d." : GO0s3400 : RETURN$ 00'P$T1-)$3REd aderi 08
1
N R=1
1082L u3,R : RR=VAL(MID$(R$,118N=6 F RR3 THEN RETURN$ #i:$NEFSH esYUEFO E2oD/GOTO0820
120AQE0$2Time --------------------------------------------------------
$(AO5sUB 1400
1200EZ =)i-9 (A0O 3DF=KE =)i-
$ D$(TI$,4(CI : S=Nh1C0B20A) $,7(C1"IH,=:=)i-9 : (A0n  R1)):MM=VA1C0#N),RR3D=L =)i-
D0n ME$,7,222+N60 IF S=<SS THEN SSSS=SSaELSE SSSS=E(a4OR1+N70 IF M=)+Ge= $0)S0=MM-M EL:MMMM=E(3333333333333333333333333333333333333333333333333333333333333333333331I0:05 TL5 O=EN HHHH==T5GO:)60=24-(H-HH2+N90 m:A)- TO0 HHHH=HHHH-12:P$="P2=SE h"AM"+"A,A$="It is 4w"R 0O0=QB4$hELlB S01+#iX+R4u have been on $R:" CR=1 : GOSUB S01+10 IFMS0U=L,$0hSTR0P  AR 
" Hours" : CR=1 GOSUB 1400
12130 A$=ST01C0 M"2R 1 nutS )d "+ST0I1  AR)LA conds.":CR=2:G 0esYU8
)Y,A$n+=arater count :  WHO CNdX F$B1:G 0esYU8
)LlS="TS ,iIfor callin, "+FIRST$ : C' GOSUB 1400 CLOSE #2,3
12:05MS0<OR SYS)-7O0 )1
1+=AH REN "A",#2,"LONG0980EAD0- 02,T D$,HHHH,MMMM:CLOSE #2
)1
0aF TRIES>-7O0 2 ErE$0"8
G=00$t$.4g-OfEA2O6p=iIrT8
12510 GOSUB 14 :iX)iB4B73 kS Rd$B-guy
L  CR=2 : GOSUB400
12520 Ln
R#re 4 l)ger w0 S$:0-Q=ere." GOSUB 1400 CLOSE #2,3 : GOTO 200+LO$0SBU sYUEFh"YT0S rS )40el." : CR==ELlB S00=ELSe+LR$13$i AQE0$O:ro=MOEA A0000000000000000000000000000000000000 rT8
130EG"BM10000,.5
13020G$+ NTyr=S6QR:";E2
"  ) l)e ";ERL
1'aF <u13
Ee= $0O0c0
,Q13((I10 IF ERL=1220 THENESU 6
0
$ =aF ERL=1560HEN CLOSE R0
$eaFRL=O,THEN RESUME 185((I0aF ERL=2030 m:ON=oPE QN30
13070:0:O9u1$0-7O0 ERASE C$:R 0
,Q1A"(80 IF ERL=3O,TO0 RESUM3550
13090 m9L010 THEN RESUME uN
13US F ERL=3800 THEN RESUME 3810
1)N IF ER61<U=EN R$y:COL=O0c0
OGT"(n
N m9
N0HEN Z$="" : RESUME NEXT
13$0a:O oSCF-7O0 c 0:1200
13G=a:O oHB0Ee= $0H 0
,Q  ="8((240 A$="You h e loated a s8B)Ore 71R)O2/GOSUB400
13150iXE( aB73Oe a com" eor 7OSg for SYSOP L It" : GOSUB 1400
13iX,BSR: "+STR$(ERR)+$:SH red ) Line "+S10AH<"/GOSUB 14
13170 An0
=ank You...." : G 0esYUEO $ FSH04s
LF0M$OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOIS31RS$-hELSBU sYU8
12130 A$=ST01C0 M"2R 1 nutS )d "+ST55555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555