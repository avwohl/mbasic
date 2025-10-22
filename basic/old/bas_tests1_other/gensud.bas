10 REM SUDOKU GENERATOR - Altair/Microsoft BASIC
20 REM Produces a solved grid, then removes clues keeping uniqueness
30 DIM G(9,9), S(81), P(9)
40 RANDOMIZE
50 TARGET_CLUES = 30      : REM change this to how many clues you want to remain
60 CLS
70 REM ---------- entry ----------
80 FOR r = 1 TO 9: FOR c = 1 TO 9: G(r,c) = 0: NEXT c: NEXT r
90 SOLVED = 0
100 GOSUB 1000           : REM fill grid (creates one complete solution in G)
110 IF SOLVED = 0 THEN PRINT "FAILED TO GENERATE SOLVED GRID": END
120 REM copy solved grid to working puzzle
130 FOR i = 1 TO 81
140   r = INT((i-1)/9)+1
150   c = ((i-1) MOD 9) + 1
160   S(i) = G(r,c)
170 NEXT i
180 REM create a random order of cell indices for removal
190 FOR i = 1 TO 81: R(i) = i: NEXT i
200 FOR i = 81 TO 2 STEP -1
210   j = INT(RND * i) + 1
220   t = R(i): R(i) = R(j): R(j) = t
230 NEXT i
240 REM remove cells one-by-one subject to uniqueness check
250 clues = 81
260 for idx = 1 to 81
270   pos = R(idx)
280   r = INT((pos-1)/9)+1
290   c = ((pos-1) MOD 9) + 1
300   if S(pos) = 0 then goto 420
310   old = S(pos)
320   S(pos) = 0
330   REM copy S into G as starting puzzle for solver
340   FOR rr = 1 TO 9: FOR cc = 1 TO 9: G(rr,cc)=S((rr-1)*9+cc): NEXT cc: NEXT rr
350   solutions = 0
360   GOSUB 2000  : REM count solutions (stops after finding 2)
370   IF solutions <> 1 THEN
380     REM can't remove: restore
390     S(pos) = old
400   ELSE
410     clues = clues - 1
420   END IF
430   IF clues <= TARGET_CLUES THEN EXIT FOR
440 NEXT idx
450 REM print puzzle
460 PRINT "PUZZLE (";clues;" clues): 0 = blank"
470 FOR r = 1 TO 9
480   FOR c = 1 TO 9
490     v = S((r-1)*9 + c)
500     IF v = 0 THEN PRINT "."; ELSE PRINT v;
510     IF c < 9 THEN PRINT " ";
520   NEXT c
530   PRINT
540 NEXT r
550 PRINT
560 PRINT "SOLUTION (hidden):"
570 FOR r = 1 TO 9
580   FOR c = 1 TO 9
590     PRINT G(r,c);
600     IF c < 9 THEN PRINT " ";
610   NEXT c
620   PRINT
630 NEXT r
640 PRINT "DONE"
650 END

REM ---------------------------
REM Subroutine: Fill grid with a complete valid sudoku (randomized backtracking)
REM sets SOLVED=1 and G(r,c) filled if success
1000 REM Fill starting at pos 1
1010 SOLVED = 0
1020 GOSUB 1100
1030 RETURN

REM Recursive fill routine: uses subroutine recursion
1100 REM parameters: POS on stack, will use local via variables pos
1110 IF SOLVED = 1 THEN RETURN
1120 IF POS > 81 THEN SOLVED = 1: RETURN
1130 r = INT((POS-1)/9)+1
1140 c = ((POS-1) MOD 9) + 1
1150 IF G(r,c) <> 0 THEN POS = POS + 1: GOSUB 1100: POS = POS - 1: RETURN
1160 REM generate random permutation in P(1..9)
1170 FOR k = 1 TO 9: P(k) = k: NEXT k
1180 FOR k = 9 TO 2 STEP -1
1190   j = INT(RND * k) + 1
1200   t = P(k): P(k) = P(j): P(j) = t
1210 NEXT k
1220 FOR k = 1 TO 9
1230   v = P(k)
1240   IF VALID(r,c,v) THEN
1250     G(r,c) = v
1260     POS = POS + 1
1270     GOSUB 1100
1280     POS = POS - 1
1290     IF SOLVED = 1 THEN RETURN
1300     G(r,c) = 0
1310   END IF
1320 NEXT k
1330 RETURN

REM VALID check: returns TRUE if placing v at G(r,c) is legal
1400 DEF_BOOLEAN = 0
1410 FUNCTION_VALID = 0
1420 REM but we will implement as GOSUB that sets variable OK
1430 REM We will call VALID as a GOSUB stub: uses r,c,v and sets OK=1/0 then RETURN
1440 RETURN

REM implement VALID as a line-numbered subroutine used via GOSUB 1500
1500 REM expects r,c,v and sets OK
1510 OK = 1
1520 FOR cc = 1 TO 9
1530   IF G(r,cc) = v THEN OK = 0: RETURN
1540 NEXT cc
1550 FOR rr = 1 TO 9
1560   IF G(rr,c) = v THEN OK = 0: RETURN
1570 NEXT rr
1580 br = INT((r-1)/3)*3 + 1
1590 bc = INT((c-1)/3)*3 + 1
1600 FOR rr = br TO br+2
1610   FOR cc = bc TO bc+2
1620     IF G(rr,cc) = v THEN OK = 0: RETURN
1630   NEXT cc
1640 NEXT rr
1650 RETURN

REM ---------------------------
REM Subroutine: solver that counts solutions up to 2: uses recursion similar to fill
2000 REM uses global variable solutions; grid G must be puzzle state (0 for blanks)
2010 IF solutions >= 2 THEN RETURN
2020 REM find first empty cell
2030 minpos = 0
2040 FOR pos = 1 TO 81
2050   rr = INT((pos-1)/9)+1
2060   cc = ((pos-1) MOD 9) + 1
2070   IF G(rr,cc) = 0 THEN minpos = pos: EXIT FOR
2080 NEXT pos
2090 IF minpos = 0 THEN solutions = solutions + 1: RETURN
2100 r = INT((minpos-1)/9)+1
2110 c = ((minpos-1) MOD 9) + 1
2120 REM generate candidates 1..9 in order
2130 FOR v = 1 TO 9
2140   IF CheckLegal(r,c,v) THEN
2150     G(r,c) = v
2160     GOSUB 2000
2170     G(r,c) = 0
2180     IF solutions >= 2 THEN RETURN
2190   END IF
2200 NEXT v
2210 RETURN

REM CheckLegal: faster local check for solver (no sub-array shuffling)
3000 REM returns 1 if legal (we implement as function-like via CALL)
3005 RETURN

REM We'll implement CheckLegal as line-numbered subroutine 4000 that sets CL=1/0
4000 CL = 1
4010 FOR cc = 1 TO 9
4020   IF G(r,cc) = v THEN CL = 0: RETURN
4030 NEXT cc
4040 FOR rr = 1 TO 9
4050   IF G(rr,c) = v THEN CL = 0: RETURN
4060 NEXT rr
4070 br = INT((r-1)/3)*3 + 1
4080 bc = INT((c-1)/3)*3 + 1
4090 FOR rr = br TO br+2
4100   FOR cc = bc TO bc+2
4110     IF G(rr,cc) = v THEN CL = 0: RETURN
4120   NEXT cc
4130 NEXT rr
4140 RETURN

REM Note: Because we used two check subroutines (1500 and 4000) they share names r,c,v and OK/CL;
REM to call VALID from fill use GOSUB 1500 then check OK; to call CheckLegal from solver use GOSUB 4000 then check CL.

REM To make calls consistent, add thin wrappers:
5000 REM Wrapper: VALID? (call before placing in fill)
5010 GOSUB 1500
5020 REM OK will be set
5030 RETURN

6000 REM Wrapper: CheckLegal? (call before placing in solver)
6010 GOSUB 4000
6020 REM CL will be set
6030 RETURN
