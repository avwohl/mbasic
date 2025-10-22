10 ' "My Other Computer Is An...YKW" Version 1.1, courtesy of Kelly Smith, CP/M-Net
20 ' For Osborne I Computers ONLY!!!  (C) 1982, YKW - Void Where Prohibited By Law
30 TEST=1  ' Intensity flag initialization: Added by Dave Grenewetzki, 16-oct-82
40 E$=CHR$(27):'   Escape Character
50 CLS$=CHR$(27)+"*": ' Clear Screen
60 HOME$=CHR$(&H1E):'  Home cursor
70 DY$=E$+")":'   DIM Display On
80 DN$=E$+"(":'   DIM Display Off
90 UY$=E$+"G4":'   Start Underlining
100 UN$=E$+"G0":'   End Underlining
110 PRINT CLS$
120 PRINT:PRINT:PRINT:PRINT TAB(13);DY$;"My other computer is an...";DN$:PRINT:PRINT:PRINT
130 PRINT TAB(8);UY$;"     ";UN$;" ";UY$;"             ";UN$;"  ";UY$;"     ";UN$;"       ";UY$;"     ";UN$
140 PRINT TAB(8);UY$;"     ";UN$;" ";UY$;"              ";UN$;" ";UY$;"      ";UN$;"     ";UY$;"      ";UN$
150 PRINT TAB(8);" ";UY$;"   ";UN$;"   ";UY$;"   ";UN$;"       ";UY$;"   ";UN$;"  ";UY$;"      ";UN$;"   ";UY$;"      ";UN$
160 PRINT TAB(8);" ";UY$;"   ";UN$;"   ";UY$;"            ";UN$;"   ";UY$;"       ";UN$;" ";UY$;"       ";UN$
170 PRINT TAB(8);" ";UY$;"   ";UN$;"   ";UY$;"            ";UN$;"   ";UY$;"   ";UN$;" ";UY$;"       ";UN$;" ";UY$;"   ";UN$
180 PRINT TAB(8);" ";UY$;"   ";UN$;"   ";UY$;"   ";UN$;"       ";UY$;"   ";UN$;"  ";UY$;"   ";UN$;"  ";UY$;"     ";UN$;"  ";UY$;"   ";UN$
190 PRINT TAB(8);UY$;"     ";UN$;" ";UY$;"              ";UN$;" ";UY$;"     ";UN$;"  ";UY$;"   ";UN$;"  ";UY$;"     ";UN$
200 PRINT TAB(8);UY$;"     ";UN$;" ";UY$;"             ";UN$;"  ";UY$;"     ";UN$;"   ";UY$;" ";UN$;"   ";UY$;"     ";UN$
210 PRINT E$+"="+CHR$(57)+CHR$(32);   'move cursor off-screen
220 FOR I=1 TO 500:NEXT I
230 'Reverse definition of intensity every other time
240 IF TEST=1 THEN TEST=0:DY$=E$+"(":DN$=E$+")":GOTO 260
250 IF TEST=0 THEN TEST=1:DY$=E$+")":DN$=E$+"("
260 PRINT HOME$:GOTO 120
