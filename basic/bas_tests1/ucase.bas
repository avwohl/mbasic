100 INPUT "Input any lower case character : ",Z$
105 DEF FNUCASE$(Z$,N)=CHR$(ASC(MID$(Z$,N,1)) AND &H5F)
110 PRINT "The character you typed was : ";Z$
120 Y$=FNUCASE$(Z$,1)
130 PRINT "and is ";Y$;" in upper case"
140 END
