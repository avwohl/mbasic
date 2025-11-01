100	' TIMEOUT.BAS Version.TBH:I(TBHe	' Adapate from EXITRBBS.BAEr, M2N'FMR)
SBCs
1I,uY 04	' August 26,9Dn	=lGT+C	0f2o05	' ThiE B6,lBPu6
r(ed to RO8with a copy of BYE
106	R=T6h executes a COM file after0 2=(=SN6+$y" timeout
1$,"	MT=	$ 3oOCEYE 7.2 Rev I or later). It RG1R02 aller
108	R(Rd	nOHs6+0 the time off sRhG2 +t +	 :O2tSGP=Y 09	' arke:24E' R0 SGPNg)CALLE	rN*	 P SGP)SYSO =EH(o10	' easily tell0ho is 3
NH(g out 2gularly. Bill Boltonoooo2)DHY "' +Och Cn)O4, VCP+C	IHY 13	' Fixt =u=( elapse time rotine that gave $range
1TE"esults if R3=( went =D
C 
NHL(ight. ill olton2:TD2"6
117	' A6Nl16CIEC(4, TN	P+C ;
eo18	' Added timout logging into DIRECT fO SYSOP
119	' Bill BoltoTB 	'-------------------------------------------------------
1 ,"E0bCR	nC(4, Ver+C	IR
eo22	ROLL6trror trapping fO ca2 ItlOI2(ECT0 )Gi$LERS
1I,"MClS1lready exP$ N0T1after general f
	1C 	#	2 O
,"' mainte+	a".hE

0 Ru0i=	$
i$	ErI:P2d a =sC 6
6mY 25	' time. Bill Bolton
1	,e"6
204s
220	DETm	g-Z
240	DoH(6),HT(6),HD(6=6N8),DOY(5)TG=y3)CA(1GO	EmD, 
26ELOlER1c: tf""
 0BD	(""=:Iu(R$ASTCALR5$8Te<mN$,O41$,DT$S (	LOBmERC0B =A	0o,RfY 2 	
T==n,)$ = MA1G2c4
K(rSUB 	H"0o(rTO 480		'Reord t
Gs	f
t2#0BH'myB,N "R",1	A:C"+CHR$(&HC1)+"LLE00(:b(1	Y,
iF	3	0o 10G
H:	DgS RR$:
	GET #=R22=-T1CdM0 5S0  a()	0o)1c s
380	GET #1,RE:
	&UT#+L
400	IF INSTR(S$	:"THEN
		POINTER = INSTMt,": 
 dT0o(ReGEER = LEN(S$)
420	S$ = LEFT$(S$,PO=	G(c D  EH: s 	)a(,h  " " + F$ + Mh7POIN	aD EH: : EH:24E"TmyHGfY R$N
TNIiOs(0=:	oSrhE #11(r4s
500	Ct# 22s
52 fl(nE$f"GO*S:TTm-l0R2=VRe	EM:l(8s"=:Iu(R	=n17	Y,T	9)+"RECT. "+CHR$(&HA0),40S ,)1Mu	-m(0R1LS ,2c$
(E1
U, = VAL(RR$) + 1:
	RL =HPNn=yT 	G5$8Te<H:Mt
640	) MuE7V8" 2c4
K(rINTER = IN:Mt,":")
7/1(ReGE=	G(H LEN(S$)
66RL S1N(hnS$,POINTER +) 1" to " 24S a(" +R1a)Ueh	$,POINTER +   a(8 + "TPI5lDCGOSUB 740
700	PUT #1,RE:
	$OSE #17r =Y	#
740	'
760	'  3
21EH$ P1re disk record
780	'
800	LSET RR0tEFDMt+SP-(RL-2),RL-2)+17	HE6 +CHR$(102T 20	RYY	E=V
860	C,
















































 7O,t=""T O4OR/G	44UDH8	R2rU0	IF NCH=127 THEN
		1040
20	IF NCH<I2c4o(22R.T9(,)HC>=62 THEN
		PE=	E S0 71. 	0o(ERa  )	HPN9+7dSAV$+CHR$(NCH):
	T	=CHC)	0ou	0,=	E S0 
	R'TN* 0	IF CHC=R 1N=$8u	0,=	E S0 71.R2
	, EERa  )	HPBHO4s
aHn,) n/	I=EN
		880
	ELS$8u	NT RI0hnSAV$ ) 5$ C046)1080
10O24  nT	=0 THEN
	 	H0oL=$8u	0,=	 GdfIR	(rE V, y  5$8O,t=LEFT$LSDO(T	RS ,Ra  )	HPBIO24 EO(i(E1N		1060
11204 EO(i4 THES (R"0,=	5$8)=Y	#
 Nr1 	H=21 THEN
		PRINT "
8	0o(rTO 860
 iO1 	H<>24 OR C,
n,N
880
1 0 OR BCC=1O CHC: ("0,=	 GdfI:
	NEXT BCCS ,Ra2	2=PB 
U 'ES0gf
bE0 R"PHNM
#H(eo220	ASEPORT = &H50o240	CMTOR= BA&O	a(PB T+CDATAPORT = SGTO	a(Y80 '***********************************************************
1300 '*		REAI=Eg	62C
2My	*
132'*:
INr4R ,2TH )TORPEP 1
1360		OUT CMDPORT,(&H	a(E2Te o380		DOY(D2T"(7 )IN 0I$BrRT)
1U	NAT DIGI2o420	EAR= (DOY(  E	((
  a(	
a	R2o4OEA3=10 = DKi	R2o460	MOE
   6*Ke)
1480	DA10 = DOY(1)
1
r6gY1  = DOY(0)
1mECD)uY 5nIO,1OR0I(,1nI2 0t	6gTE STRING		*
156'*:
	HG	AHRiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiieo60E0e	Hu'RD=:H8 c C
'$$	7	Huet 	=8H 620	MID$(DATE1CD=8)RIGHTEt		Huet8	)
164E0e	Hu'RDN6c	 E1=PR2o660	MID$(i:HRDOD=8  HmDMh0 +rE
 0),1)
1680	MID$(i:HRD'D=E1 0,It(STR$(MONTH1),1)R7g(.2h	H'E1$,6,1) = "/"
1720	MID$(DATE1$,7,2) =IGHT$(STR$(YEA:	DB30	CR DAHR
eo760	DT$ = EFT$(DATE14H)o780	DD$ ED$(DATED=:	DR2o806E7 c Ueh	H'E1$,4,2) 	 
O TURNo840s
1860 ' Time-fining sbrRd60=Y 880	FOR2C
E1	2 0,P -1
1900		OUT CMDPORT,(&R	a TeIR)Oe0		TOD(DIGIT= INP(iRiT$IR)O30		IF DIG	c:1I=EN 4"H(,2Te  =OD(DIGI RH)aHY 960	NAT DITuY 80	H(1) = TOD0 I
N E e) = TOD( =e0	H(3) = TOD6 
2
OR6  = TO:-T'=rR		 E1IrD(R2T="Hn6) = TOD(0)
Rge( c:  : $:nh c:  :
	DS$ 	) 	5llrE0eh	H$,1,1) = RIGHTEt		bR )),1):
	MID$(
0E2,1) = E20hnSTR$(H(2:H8 5$8Ueh	H(h	=:HE1 0,It(STR$(H(3)),1):
	MID$(h6c	 E1 0,20hnSTR$(H(4)),1):
	MID$(DSc( )RIGHTEt		b2H)),1):
	MID$(D0E2,1) =IGHT$(STR$(H(6)),1)
 NrhG	$+)TES	H$+":"+DI$
2160	hn
0M2	+h":"+DS$F80	RE0RNT(=4s
2222'CLOCK ROUTINES
22nIP'(e=GTRINT:
	HTm		e1SND1CS 	6
18=o	+0H(s$I=R" w8O8:R'T'(( 0	TF$="#"
2300	CH THTO 6
2320	:
E USING TF$R	4	ReTOTmn   I=2 THEY	, RTRINT ":";
23O8TI 2cFI=nK,:	 $	0,=		)e	;
2380	NAT I

U	PE=s
2420 '  Now get hh/m
1o P$o2d C-2nterbbT',,(
2R )=PEEK(74RS (
2)=CNo(5):
	I6DE
TY7 HTIiORI13)=CNo(7RS (
5)=PEEK(78RS (
6)=PY71HlIF(D  And calculateGP)difference....
25024  0 	 R=I1	 2c4
K0   = H(1) + RS ( 0 e) = H(2) + 4
2520	) N	R=RI1N	 2c4DY( (D4-H4-M(Do( 0 TDETDI0 CR 
2540	IF H(5)<HT(  I=EN 
		H(5)=H(5)+6S ( 0 3TDa	E HR6H60	IF H(4)<Ia	c	Y( (Da	ETDa	ES:
H(3)=H(3)-1
25804  0 i	R=RI1iI=EY(D6DETD6DE(RS 0	ETD	-2Ter24  e)<HT(2) THEY(D	DETD	DES 0: ( 0 	E HRIDmn
	( =H(6)-HTC 	0o(
	(5)DI0 =T(5):
	HE6 =H(4)-HT( e,=n
	(3)=H(3)-HT(3): (		=H(E e:p5$88	ETDH8CT(1)
2660	HTm		(d1u've been on the system for........'e( 0	TF$	#"dr4E	H THTO 6
272:5Tm	MM'22lR

































.RY=n   I=2 THEY	, RTRINT ":";
2760	4  TH4 THEN 
				PRINT ":";TdT 0	NEXT
2800	PRINT:
	PRINT
2820	RETURN
2840 '
 60 '04+(O andler for File ErrOs
288'
3:	 n,) CiO1(DI==$8,'O +s
3020	IF ERL=620 THEN
		GOTStf2030	D Gn1GOTO 0
306 N=5lO2x 	=8 5$8eh	H(7V(E1) = RIGHTEt		b2H)),