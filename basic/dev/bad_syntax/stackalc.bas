1  ERASE : WSELECT 1: WINDOW 8,24,24,79
2  PRINT "STACKALC  by Slot 8"
3  PRINT : ' Developmental Revision 2.2, 11/7/85
4  PRINT "Copyright 1985"
5  PRINT "Slot Eight Associates":' Attn: Jim Lill
6  PRINT "PO Box 10098"
7  PRINT "Rochester, NY 14610"
8  WAIT 1000 
9  ' Written/Compiled using MTBASIC by Softaid POB 2214 Colombia MD 21045
10  STRING A$(30),E$,F$(30),S$,PR$(30),B$,H$(30),PRX$,PRLX$,E2$,PRY$,PRZ$
11  STRING PBX$(20,20),PBF$(20,20),PBLX$(20,20)
12  REAL J,Q,R,T,UL,UX,UY,UZ,UT,Z,O,Y,X,LX,U,V,E9,ABS,X3,ANG,X4,O2
13  INTEGER C,D,G,I,L,K,N,W,P,M,X2,HE,U2,PB,PBO,QC,U3
14   S$="Ready for New Entry":  HE=0:  E2$="":  M=0:  PB=0
15   IF  HE = 64 THEN  GOTO 19
16   P=32:  F$=S$:  E$="":  Q=1000000.0:  X2=1
17   W=0:  O=0.0:  M=0:  HE=0:  QC=0
18   X=0.0:  Y=0.0:  Z=0.0:  T=0.0:  LX=0.0:  L=1:  C=1:  R=0.0:  J=0
19  DEF ABS(X3)
20   IF  X3 < 0.0 THEN   X3=X3 * ( - 1)
21   ABS=X3
22  FNEND 
23  DEF ANG(X4)
24   IF  X4 < 360.0 THEN  GOTO 26
25   X4=X4 - 360: GOTO 24
26   IF  M = 1 THEN   X4=X4 * 57.29577951
27   ANG=X4: FNEND 
28  DEF PR$(O)
29   IF  O = 0.0  OR  O > .01  OR  O < -0.01 THEN  GOTO 38
30   W=0
31   W=W + 1:  O=O * 10
32   IF  O < 1.0  AND  O > -1.0 THEN  GOTO 31
33  GOSUB 46
34   B$=STR$(W)
35   IF  W < 10 THEN   B$=CONCAT$("0",B$)
36   B$=CONCAT$("-",B$)
37  GOTO 54
38   IF  O > Q  OR  O < ( - Q) THEN  GOTO 41
39  GOSUB 60
40   PR$=CONCAT$(H$,"    "): GOTO 65
41   W=0
42   W=W + 1:  O=O / 10.0
43   IF  O >= 10.0  OR  O <= -10.0 THEN  GOTO 42
44  GOSUB 46
45  GOTO 52
46   IF  MID$(STR$(O),1,6) = "9.9999" THEN   O=1.0:  W=W + 1
47   IF  MID$(STR$(O),1,7) = "-9.9999" THEN   O= - 1.0:  W=W + 1
48   IF  MID$(STR$(O),3,4) = "9999" THEN   O=VAL(MID$(STR$(O),1,1)) + 1
49   IF  O > 0.0 THEN  GOTO 51
50   IF  MID$(STR$(O),4,4) = "9999" THEN   O= - (VAL(MID$(STR$(O),2,1)) + 1)
51  RETURN 
52   B$=STR$(W)
53   IF  W < 10 THEN   B$=CONCAT$("0",B$)
54   B$=MID$(B$,1,LEN(B$) - 6)
55   IF  VAL(B$) > 0 THEN   B$=CONCAT$("+",B$)
56   IF  VAL(STR$(O)) = 0.0  AND  W < 0 THEN  GOTO 331
57   IF  W > 36  OR  W < -36 THEN  GOTO 331
58  GOSUB 60
59   PR$=CONCAT$(CONCAT$(H$,"E"),B$): GOTO 65
60   H$=STR$(O)
61  FOR U2=1 TO (14 - LEN(H$))
62   E2$=CONCAT$(E2$," ")
63  NEXT U2
64   H$=CONCAT$(E2$,H$):  E2$="": RETURN 
65  FNEND 
66   A$="                  ":  E9=2.3025850930
67  ERASE : WSELECT 0: WINDOW 0,0,21,79: WFRAME "_","|":WINDOW 0,0,21,44
68  WFRAME "_","|":WINDOW 2,4,20,43               
69  PRINT "       S  T  A  C  K  A  L  C  "
70  PRINT "HELP          ?      QUIT         ESC"
71  PRINT "4 Function: +-*/     QuiCalc      ^ ^"
72  PRINT "Backsp.  <Cursor     Ang.Tog. ^T  DEG"
73  PRINT "Enter      <sp>      Clr. X     <cr>X"
74  PRINT "Roll-Down     D      Clr. Mem.  <cr>M"
75  PRINT "Roll ^ stack  U      Clr. Stack <cr>S"
76  PRINT "X-Y Exchange XY      X-Mem. Exch   XM"
77  PRINT "Sto/Recall  M/R      Change Sign    ;"
78  PRINT "PI 3.14159    P      Recall Last X LX"
79  PRINT "Sq.Root X    SR      Square X      SQ"
80  PRINT "Log (10)     LG      Log (e)       LN"
81  PRINT "AntiLog (10) ^L      AntiLog (e)   ^N"
82  PRINT "Y to the Xth ^X      Xth Root Y    ^Y"
83  PRINT "Sine X       SI      ArcSine X     AS"
84  PRINT "Cosine X      C      ArcCosine X   AC"
85  PRINT "Tangent X     T      ArcTangent X  AT"
86  PRINT "1/X           I      Sci.Notation   E"
87  PRINT "Print Toggle ^I      Paper Advance ^J"
88   IF  QC = 1 THEN  GOTO 91
89  WINDOW 0,44,3,79: WFRAME "_","|": WINDOW 2,46,3,78: PRINT "T register="
90  WINDOW 3,44,6,79: WFRAME "_","|": WINDOW 5,46,6,78: PRINT "Z register="
91  WINDOW 6,44,9,79: WFRAME "_","|": WINDOW 8,46,9,78
92  IF QC=1 THEN PRINT "        QUICK  CALCULATOR":GOTO 96
93  PRINT "Y register="
94  WINDOW 15,44,18,79: WFRAME "_","|": WINDOW 17,46,18,78: PRINT "    last X="
95  WINDOW 18,44,21,79: WFRAME "_","|": WINDOW 20,46,21,78: PRINT "    memory="
96  WINDOW 9,44,12,79: WFRAME "_","|": WINDOW 11,46,12,78: PRINT "X register="
97  WINDOW 12,44,15,79: WFRAME "_","|": WINDOW 14,46,15,78: PRINT "function:"
98   IF  HE = 64 THEN  GOTO 100
99   C=0
100   UL=LX:  UX=X:  UY=Y:  UZ=Z:  UT=T
101   IF  QC = 1 THEN  GOTO 108
102  WINDOW 2,60,3,78: PRINT PR$(T)
103  WINDOW 5,60,6,78:  PRZ$=PR$(Z): PRINT PRZ$
104  WINDOW 8,60,9,78:  PRY$=PR$(Y): PRINT PRY$
105   IF  QC = 1 THEN  GOTO 108
106  WINDOW 17,60,18,78:  PRLX$=PR$(LX): PRINT PRLX$
107  WINDOW 20,60,21,78: PRINT PR$(R)
108  WINDOW 11,60,12,78:  PRX$=PR$(X): PRINT PRX$
109   IF  P = 32 THEN  GOTO 113
110   IF  MID$(F$,1,2) = "**" THEN  GOTO 113
111   IF  MID$(F$,1,3) = "PRI" THEN  GOTO 113
112   PB=PB + 1:  PBLX$(PB)=(PRLX$):  PBX$(PB)=PRX$:  PBF$(PB)=F$
113  WINDOW 14,58,15,78: PRINT "                    "
114  WINDOW 14,58,15,78: PRINT F$
115   L=C
116  WINDOW 14,56,15,58: CURSOR 0,0
117   K=KEY
118   IF  K = 0 THEN  GOTO 117
119   IF  K > 96  AND  K < 123 THEN   K=K - 32
120  WINDOW 14,58,15,78: PRINT "New Entry in Process"
121   IF  K = 44 THEN  GOTO 330
122   IF  K = 46 THEN  GOTO 124
123   IF  K < 48  OR  K > 57 THEN  GOTO 131
124  WINDOW 11,60,12,78: PRINT A$
125  GOTO 131
126  WINDOW 11,60,12,78: PRINT E$: CURSOR 0,LEN(E$)
127   K=KEY
128   IF  K = 0 THEN  GOTO 127
129   IF  K > 96  AND  K < 123 THEN   K=K - 32
130   IF  K = 44 THEN  GOTO 330
131   IF  K >< 46 THEN  GOTO 134
132   IF  D = 1 THEN  GOTO 127
133   D=1: GOTO 135
134   IF  K < 48  OR  K > 57 THEN   L=C: GOTO 144
135   E$=CONCAT$(E$,CHR$(K))
136   IF  J = 1  OR  L = 2 THEN  GOTO 140
137   T=Z:  Z=Y:  Y=X:  J=1
138   IF  QC = 1 THEN  GOTO 140
139  WINDOW 2,60,3,78: PRINT PRZ$: WINDOW 5,60,6,78: PRINT PRY$: WINDOW 8,60,9,78: PRINT PRX$
140   IF  LEN(E$) < 18 THEN  GOTO 143
141   E$="":  F$="** Use 'E' Key **"
142   LX=UL:  X=UX:  Y=UY:  Z=UZ:  T=UT: GOTO 101
143   C=1: GOTO 126
144   U=V:  V=VAL(E$)
145   IF  K >< 8 THEN  GOTO 155
146   IF  L >< 1 THEN  GOTO 113
147   F$="Backspace Entry      ":  U3=LEN(E$) - 1
148   IF  U3 < 1 THEN   E$="":  F$=S$: WINDOW 11,60,12,78:  D=0:  C=2:  U=0.0: PRINT U: GOTO 113
149   H$=MID$(E$,(U3 + 1),1)
150   IF  H$ = "." THEN   D=0
151   E$=MID$(E$,1,U3)
152  WINDOW 11,60,12,78: PRINT "                    "
153  WINDOW 14,58,15,78: PRINT F$
154  GOTO 126
155   E$="":  J=0:  H$="":  D=0
156   IF  C = 3 THEN  GOTO 158
157   IF  C = 1 THEN   X=V
158   IF  K >< 32 THEN  GOTO 161
159   T=Z:  Z=Y:  Y=X:  V=X:  C=2:  F$="ENTER, X=>Y=>Z=>T"
160   IF  PB < 18 THEN  GOTO 100
161   IF  PB = 0  OR  K = 30 THEN  GOTO 168
162  FILE  - 1
163  FOR PBO=1 TO PB
164  PRINT PBLX$(PBO);" | ";PBX$(PBO);" | ";PBF$(PBO)
165  NEXT PBO
166   PB=0: FILE 0
167   IF  K = 32 THEN  GOTO 100
168   IF  K >< 9 THEN  GOTO 178
169   IF  P = 32 THEN  GOTO 171
170   P=32:  F$="PRINTER OFF": GOTO 101
171   P=64:  F$="PRINTER ON": FILE  - 1
172  PRINT " STACKALC                                            by SLOT 8"
173  PRINT "---------------------------------------------------------------"
174  PRINT "      Last   X     |          X         |     Function"
175  PRINT "---------------------------------------------------------------"
176  PRINT "                   |                    |  "
177  FILE 0: GOTO 99
178   IF  K > 65 THEN  GOTO 258
179   IF  K >< 13 THEN  GOTO 188
180  WINDOW 14,56,15,78: PRINT "  1st. Keystroke= <cr> ": CURSOR 0,0
181   K=KEY
182   IF  K = 0 THEN  GOTO 181
183   IF  K = 77  OR  K = 109 THEN   F$="Clear MEMORY":  R=0.0: GOTO 99
184   IF  K >< 83  AND  K >< 115 THEN  GOTO 186
185   F$="Clear STACK":  LX=0.0:  X=0.0:  Y=0.0:  Z=0.0:  T=0.0: GOTO 99
186   IF  K = 88  OR  K = 120 THEN   F$="Clear X":  C=2:  X=0.0: GOTO 108
187   IF  K >< 27 THEN  GOTO 330
188   IF  K >< 30 THEN  GOTO 193
189   IF  QC = 1 THEN   HE=64:  QC=0: WINDOW 8,46,9,78: WCLEAR : GOTO 89
190  WINDOW 2,45,8,78: WCLEAR 
191  WINDOW 6,44,9,79: WFRAME "_","|": WINDOW 8,46,9,78: PRINT "        QUICK  CALCULATOR"
192  WINDOW 16,45,20,78: WCLEAR :  QC=1: GOTO 100
193   IF  K >< 43 THEN  GOTO 197
194   IF  X = 0.0  OR  Y = 0.0 THEN  GOTO 196
195   IF  LOG(ABS(X / 10) + ABS(Y / 10)) > 80.590 THEN  GOTO 331
196   F$="ADDITION":  LX=X:  X=Y + X:  Y=Z:  Z=T: GOTO 99
197   IF  K = 45 THEN   F$="SUBTRACTION":  LX=X:  X=Y - X:  Y=Z:  Z=T: GOTO 99
198   IF  K >< 42 THEN  GOTO 202
199   IF  Y = 0.0  OR  X = 0.0 THEN  GOTO 201
200   IF  LOG(ABS(Y)) + LOG(ABS(X)) > 82.893 THEN  GOTO 331
201   F$="MULTIPLICATION":  LX=X:  X=Y * X:  Y=Z:  Z=T: GOTO 99
202   IF  K = 35  OR  K = 63 THEN  GOTO 339
203   IF  K >< 59 THEN  GOTO 207
204   F$="Change Sign of X"
205   IF  X = 0.0 THEN  GOTO 108
206   X=( - X):  UX=X:  C=0: GOTO 108
207   IF  K >< 47 THEN  GOTO 210
208   IF  X = 0.0 THEN  GOTO 331
209   F$="DIVISION":  LX=X:  X=Y / X:  Y=Z:  Z=T: GOTO 99
210   IF  K >< 12 THEN  GOTO 213
211   IF  X > 36.0 THEN  GOTO 331
212   F$="anti-LOG(10)":  LX=X:  X=EXP(E9 * X): GOTO 99
213   IF  K >< 20 THEN  GOTO 217
214   IF  M = 0 THEN   M=1: WINDOW 5,38,6,40: PRINT "RAD": GOTO 216
215   IF  M = 1 THEN   M=0: WINDOW 5,38,6,40: PRINT "DEG"
216   F$="Ready for New Entry": GOTO 113
217   IF  K = 10 THEN  FILE  - 1: PRINT : FILE 0: GOTO 113
218   IF  K = 27 THEN  GOTO 336
219   IF  K >< 14 THEN  GOTO 223
220   IF  X > 82.893 THEN  GOTO 331
221   F$="anti-LOG(e)"
222   LX=X:  X=EXP(1 * X): GOTO 99
223   IF  K >< 24 THEN  GOTO 236
224   F$="Y Raised to the X":  I=X:  LX=X:  U=1
225   IF  X = 0.5 THEN   X=SQR(Y): GOTO 235
226   IF  Y = 0.0 THEN   X=0: GOTO 235
227   IF  X = 0.0 THEN   X=1: GOTO 235
228   IF  X * LOG(ABS(Y)) > 82.893 THEN  GOTO 331
229   IF  X >< I  OR  X < 1 THEN   X=EXP(LOG(Y) * X): GOTO 235
230   IF  X = 1 THEN   X=Y: GOTO 235
231   X=Y
232   IF  U = LX THEN  GOTO 235
233   X=X * Y:  U=U + 1
234  GOTO 232
235   Y=Z:  Z=T: GOTO 99
236   IF  K >< 25 THEN  GOTO 242
237   IF  X <= 0.0  OR  Y = 0.0 THEN  GOTO 331
238   F$="Xth Root of Y":  LX=X
239   IF  X = 2 THEN   X=SQR(Y): GOTO 241
240   U=LOG(Y) / X:  X=EXP(1 * U): GOTO 241
241   Y=Z:  Z=T: GOTO 99
242   IF  K >< 65 THEN  GOTO 258
243  WINDOW 14,56,15,78: PRINT "  1st. Keystroke= A    ": CURSOR 0,0
244   K=KEY
245   IF  K = 0 THEN  GOTO 244
246   IF  K = 27 THEN  GOTO 336
247   IF  K = 84  OR  K = 116 THEN   F$="arc TANGENT":  LX=X:  X=ATAN(X): GOTO 256
248   IF  K >< 67  AND  K >< 99 THEN  GOTO 253
249   F$="arc COSINE"
250   IF  X = 0.0 THEN   LX=X:  X=90.0: GOTO 256
251   IF  ABS(X) > 1.0 THEN  GOTO 331
252   LX=X:  X=ACOS(X): GOTO 256
253   IF  K >< 83  AND  K >< 115 THEN  GOTO 330
254   IF  ABS(X) > 1.0 THEN  GOTO 331
255   F$="arc SINE":  LX=X:  X=ASIN(X)
256   IF  M = 1 THEN   X=X / 57.29577951
257  GOTO 105
258   IF  K = 67  OR  K = 99 THEN   F$="COSINE":  LX=X:  X=COS(ANG(X)): GOTO 99
259   IF  K = 68  OR  K = 100 THEN   F$="Roll-Down Stack":  U=X:  X=Y:  Y=Z:  Z=T:  T=U: GOTO 99
260   IF  K >< 69 THEN  GOTO 282
261  WINDOW 14,58,15,78: PRINT "Enter Exponent      ":WINDOW 11,60,12,78: PRINT A$
262  IF X = 0.0 THEN  X = 1.0
263  WINDOW 11,60,12,73: PRINT X:  O2=1
264  WINDOW 11,74,12,78: PRINT "E": CURSOR 0,1
265   K=KEY
266   IF  K = 0 THEN  GOTO 265
267   IF  K = 8 THEN   H$="": WINDOW 11,75,12,78: PRINT "   ": GOTO 264
268   IF  K < 48  OR  K = 58 OR K > 59 THEN  GOTO 274
269   IF  K = 59 THEN   H$=CONCAT$("-",H$): GOTO 272
270   H$=CONCAT$(H$,CHR$(K))
271   IF  LEN(H$) = 3 THEN  GOTO 331
272   G=VAL(H$): WINDOW 11,75,12,78: PRINT G
273  CURSOR 0,LEN(H$): GOTO 265
274   IF  LOG(ABS(X)) + ABS(G) > 37  OR  ABS(G) > 35 THEN  GOTO 331
275   IF  G = 0 THEN   O2=1: GOTO 279
276  FOR U=1 TO ABS(G)
277   O2=O2 * 10
278  NEXT U
279   IF  G >= 0 THEN   X=X * O2
280   IF  G < 0 THEN   X=X / O2
281   C=3:  G=0: GOTO 155
282   IF  K >< 73 THEN  GOTO 285
283   IF  X = 0.0 THEN  GOTO 331
284   F$="RECIPROCAL":  LX=X:  X=1 / X: GOTO 99
285   IF  K >< 76 THEN  GOTO 298
286  WINDOW 14,56,15,78: PRINT "  1st. Keystroke= L    ": CURSOR 0,0
287   K=KEY
288   IF  K = 0 THEN  GOTO 287
289   IF  K = 88  OR  K = 120 THEN   F$="Recall Last X":  U=LX: GOTO 333
290   IF  K >< 71  AND  K >< 103 THEN  GOTO 293
291   IF  X <= 0.0 THEN  GOTO 331
292   F$="LOG(10)":  LX=X:  X=(LOG(X) / E9): GOTO 99
293   IF  K >< 78  AND  K >< 110 THEN  GOTO 296
294   IF  X <= 0.0 THEN  GOTO 331
295   F$="LOG(e)":  LX=X:  X=LOG(X): GOTO 99
296   IF  K = 27 THEN  GOTO 336
297  GOTO 330
298   IF  K = 77 THEN   F$="Store in Memory":  R=X: GOTO 99
299   IF  K = 80 THEN   F$="PI, 3.141592":  U=3.141592654: GOTO 333
300   IF  K = 82 THEN   F$="Recall Memory":  U=R: GOTO 333
301   IF  K >< 83 THEN  GOTO 319
302  WINDOW 14,56,15,78: PRINT "  1st. Keystroke= S    ": CURSOR 0,0
303   K=KEY
304   IF  K = 0 THEN  GOTO 303
305   IF  K = 73  OR  K = 105 THEN   F$="SINE":  LX=X:  X=SIN(ANG(X)): GOTO 99
306   IF  K >< 81  AND  K >< 113 THEN  GOTO 309
307   IF  2 * LOG(ABS(X)) > 82.893 THEN  GOTO 331
308   F$="SQUARE":  LX=X:  X=X * X: GOTO 99
309   IF  K >< 82  AND  K >< 114 THEN  GOTO 317
310   IF  X < 0.0 THEN  GOTO 331
311   IF  X = 0.0 THEN  GOTO 99
312   F$="SQUARE-ROOT":  LX=X
313   IF  X < 20 THEN   X=10000 * X:  X=SQR(X):  X=X / 100: GOTO 99
314   IF  X < 625 THEN   X=100 * X:  X=SQR(X):  X=X / 10: GOTO 99
315   IF  LOG(X) > 35 THEN   X=EXP(1 * (LOG(X) / 2)): GOTO 99
316   X=SQR(X): GOTO 99
317   IF  K = 27 THEN  GOTO 336
318  GOTO 330
319   IF  K >< 84 THEN  GOTO 322
320   IF  X = 90.0 THEN  GOTO 331
321   F$="TANGENT":  LX=X:  X=TAN(ANG(X)): GOTO 99
322   IF  K = 85 THEN   F$="Roll-Up Stack":  U=T:  T=Z:  Z=Y:  Y=X:  X=U: GOTO 99
323   IF  K >< 88 THEN  GOTO 330
324  WINDOW 14,56,15,78: PRINT "  1st. Keystroke= X    ": CURSOR 0,0
325   K=KEY
326   IF  K = 0 THEN  GOTO 325
327   IF  K = 89  OR  K = 121 THEN   F$="Exchange X and Y":  U=X:  X=Y:  Y=U: GOTO 99
328   IF  K = 77  OR  K = 109 THEN   F$="Exchange X and MEM":  U=X:  X=R:  R=U: GOTO 99
329   IF  K = 27 THEN  GOTO 336
330   F$="** FUNCTION ERROR **": GOTO 332
331   F$="** OUT-OF-RANGE **"
332   LX=UL:  X=UX:  Y=UY:  Z=UZ:  T=UT:GOTO 100
333   IF  L = 2 THEN   X=U: GOTO 99
334   IF  L = 1 THEN   T=Y:  Z=X:  Y=X:  X=U: GOTO 99
335   T=Z:  Z=Y:  Y=X:  X=U: GOTO 99
336  ERASE : PRINT "STACKALC by Slot 8"
337  WAIT 50  
338  STOP 
339  ' START OF HELP
340  ERASE : WSELECT 11
341  PRINT "FUNCTION LIST                    KEYSTROKES      NOTES": PRINT 
342  PRINT "Calculative:": PRINT 
343  PRINT "Simple Math, +   -   *   /              +   -   *   /"
344  PRINT "Square Root of X                        SR    X must be +"
345  PRINT "X Squared                               SQ"
346  PRINT "Log (base 10) of X                      LG"
347  PRINT "antiLog of above                  ctrl 'L'"
348  PRINT "Log (natural) of X                      LN    X must be >0"
349  PRINT "antiLog of above                  ctrl 'N'"
350  PRINT "Y to the Xth Power                ctrl 'X'         "
351  PRINT "Xth Root of Y                     ctrl 'Y'    use Y -Xth for best accuracy"
352  PRINT "Reciprocal, 1/X                         I"
353  PRINT "Cosine of X                             C"
354  PRINT "Sine of X                              SI"
355  PRINT "Tangent of X                            T"
356  PRINT "Arc Functions of above           AC,AS,AT"
357  PRINT 
358  PRINT "hit any key to continue..... Q to quit"
359   K=KEY
360   IF  K = 0 THEN  GOTO 359
361   IF  K = 81 OR K= 113 THEN  GOTO 432
362  ERASE : PRINT "Manipulative:": PRINT 
363  PRINT "Quit                                   ESC"
364  PRINT "Enter X=>Y=>Z=>T                      <sp>"
365  PRINT "Backspace New Entry               < cursor"
366  PRINT "Roll Down Stack                          D"
367  PRINT "Roll Up Stack                            U"
368  PRINT "Clear Stack                          <cr>S"
369  PRINT "Clear X                              <cr>X"
370  PRINT "Clear Memory                         <cr>M"
371  PRINT "Exchange X and Y                        XY"
372  PRINT "Exchange X and Memory                   XM"
373  PRINT "Store X in Memory                        M"
374  PRINT "Recall X from Memory                     R"
375  PRINT "Recall Last X                           LX"
376  PRINT "Change Sign of X or Exponent (semicolon) ;    see example that follows"
377  PRINT "PI, 3.14159                              P"
378  PRINT "Degrees/Radians In/Out              ctrl T"
379  PRINT "Scientific Notation Input                E    see example that follows"
380  PRINT "Printer Toggle (on/off)             ctrl I"
381  PRINT "Advance Paper/Dump Buffer           ctrl J    see note that follows"
382  PRINT : PRINT "hit any key to continue..... Q to quit"
383   K=KEY
384   IF  K = 0 THEN  GOTO 383
385   IF  K = 81 OR K=113 THEN  GOTO 432
386  ERASE 
387  PRINT "The entry of very large or very small numbers is best accomplished"
388  PRINT "using scientific notation.  This is easily implemented in STACKALC"
389  PRINT "with the 'E' key.  For a very large number such as:"
390  PRINT "          35"
391  PRINT "  1.2 X 10      simply type:  1 . 2 E 3 5"
392  PRINT 
393  PRINT "The change sign key (;) must be used for the entry of negative numbers"
394  PRINT "and exponents. For Example....."
395  PRINT 
396  PRINT "To enter a negative number such as -12.2, type the following sequence:"
397  PRINT 
398  PRINT "       1 2 . 2 ;"
399  PRINT "                                   -6"
400  PRINT "To enter a number such as 12.2 X 10    type:"
401  PRINT 
402  PRINT "       1 2 . 2 E 6 ;"
403  PRINT "                                                        -6"
404  PRINT "Likewise, in combination for a number such as -12.2 X 10"
405  PRINT 
406  PRINT "       1 2 . 2 ; E 6 ;"
407  PRINT : PRINT 
408  PRINT "hit any key to continue..... Q to quit"
409   K=KEY
410   IF  K = 0 THEN  GOTO 409
411   IF  K = 81 OR K=113 THEN  GOTO 432
412  ERASE 
413  PRINT "The Paper Advance Key (ctrl J) may be used to send linefeeds to the"
414  PRINT "printer.  It is also used to empty the print buffer at the end of"
415  PRINT "a series of calculations."
416  PRINT 
417  PRINT 
418  PRINT "Experts may use the Quick Calculator feature which limits the display"
419  PRINT "to the X register and function.  This assures fastest keyboard response"
420  PRINT "for string calculations..... It may be toggled with ctrl ^"
421  PRINT "                             (ctrl shift N on some computers)"
422  PRINT : PRINT 
423  PRINT "ERROR MESSAGES consist of:"
424  PRINT 
425  PRINT "**OUT-OF-RANGE**, for inputs or outputs that exceed approximately"
426  PRINT " 1 in 10 to the 36th."
427  PRINT 
428  PRINT "**FUNCTION ERROR**, for key sequences that are not legal."
429  PRINT
430  PRINT "Although it will cause a FUNCTION ERROR, two-keystroke functions"
431  PRINT "may be cancelled after the first keystroke by hitting the spacebar."
432  PRINT : PRINT : PRINT "..... hit any key to start calculating!"
433   K=KEY
434   IF  K = 0 THEN  GOTO 433
435   HE=64: GOTO 15
END
