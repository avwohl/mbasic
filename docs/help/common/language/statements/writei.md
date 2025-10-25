# WRITEi

## Syntax

```basic
WRITEi<fi1e number>,<list of expressions>
ASS (X)
ASC (X$)
ATN(X)
COBL(X)
CHR$(I)
CINT(X)
COS (X)
CSNG (X)
CVI«2-byte string»
CVS«4-byte string»
CVD«8-byte string»
EOF«file number»
EXP(X)
FIX (X)
FRE(O)
FRE (X$)
HEX$ (X)
Versionsr     Extended, Disk
Action:       Returns    a  string   which   represents   the
hexadecimal value of the decimal argument. X is
rounded to an integer      before   HEX$(X)  is
evaluated.
INKEY$
Action:         Returns either a one-character string cont~ining
a character read from the terminal or a null
string if no character is pending at          the
terminal.    No characters will be echoed and all
characters are passed through tto the program
except    for Contro1-C, which terminates the
program.   (With the BASIC Compiler, Contro1-C is
also passed through to the program.)
INP (I)
INPUT$(X[,[#]Y])
INSTR ( [I, ] X$, Y$)
INT (X)
Versions,:     8K, Extended, Disk
Action:        Returns the largest integer <=X.
LEFT$ (X$, I)
LEN (X$)
LOC«file number»
LOG (X)
LPOS(X)
MID$ (X$, I [ ,J] )
MKI$«integer expression»
MKS$«single precision expression»
MKD$«double precision expression»
OCT$ (X)
PEEK (I)
POS (I)
RIGHT$(X$,I)
RND [ (X) ]
SGN(X)
SIN(X)
SPACE$(X)
SPC (I)
SQR(X)
STR$(X)
TAB (I)
TAN (X)
VAL (X$)
FILES[<filename>]
RESET
LOF«file number»
Action:        Returns the number of records present in the
last extent read or written. If the file does
not exceed one extent (128 records), then LOF
returns the true length of the file.
```

**Versions:** Disk 8K, Extended, Disk Action:     Returns the absolute value of the expression X. 8K, Extended, Disk Action:     Returns a numerical value that is the ASCII code of the first character of the string X$.    (See Appendix M for ASCII codes.) If X$ is null, an "Illegal function call" error is returned. SK, Extended, Disk Action:      Returns the arctangent of X in radians.   Result is in the range -pi/2 to pi/2. The expression X may be any numeric type, but the evaluation of ATN is always performed in single precision. Extended, Disk Action:      Converts X to a double precision number. 8K, Extended, Disk Action:      Returns a string whose one element has ASCII code I.   (ASCII codes are listed in Appendix M.) CHR$ is commonly used to send         a   special character to the terminal. For instance, the BEL character could be sent (CHR$(7»        as a preface to an error message, or a form feed could be sent (CRR$(12»   to clear a CRT screen and return the cursor to the home position. Extended, Disk Action:      Converts X to an integer by rounding         the fractional portion.    If X is not in the range -32768 to 32767, an "Overflow" error occurs. SK, Extended, Disk Action:      Returns the cosine of X in radians.       The calculation of COS (X) is performed in single precision. Extended, Disk Action:      Converts X to a single precision number. Disk Action:       Convert string values     to   numeric   values. Numeric values that are read in from a random disk file must be converted from strings back into numbers.    CVI converts a 2-byte string to an integer. CVS converts a 4-byte string to a single precision number. CVD converts an 8-byte string to a double precision number. Disk Action:       Returns -1 (true) if the end of a sequential file has been reached.     Use EOF to test for end-of-file while INPUTting,  to avoid "Input past end" errors. 8K, Extended, Disk Action:       Returns e to the power of X.      X must be <=87.3365.   If EXP overflows, the "Overflown error message is displayed, machine infinity with the appropriate sign is supplied as the result, and execution continues. Extended, Disk Action:       Returns the truncated integer part of X. FIX(X) is equivalent to SGN(X)*INT(ABS(X». The major difference between FIX and INT is that FIX does not return the next lower number for negative X. 8K, Extended, Disk Action:       Arguments to FRE are dummy arguments.       FRE returns the number of bytes in memory not being used by BASIC-80. FRE("") forGes a garbage collection       before returning   the   number   of free bytes.     BE PATIENT: garbage collection may take 1 to 1-1/2 minutes.    BASIC   will not initiate garbage collection until all free memory has been used up.   Therefore, using FRE("") periodically will result in shorter delays for each        garbage collection. 8K, Extended, Disk Action:         Returns the byte read from port I.  I must be in the range 0 to 255. INP is the complementary function to the OUT statement, Section 2.47. Disk Action:         Returns a string of X characters, read from the terminal or from file number Y. If the terminal is used for input, no characters will be echoed and all control characters are passed through except Control-C, which is used to interrupt the execution of the INPUT$ function. Example 1:      5 ~LIST THE CONTENTS OF A SEQUENTIAL FILE IN HEXADECIMAL 10 OPEN"I",l,"DATA" 20 IF EOF(l) THEN 50 30 PRINT HEX$(ASC(INPUT$(l,#l»); 40 GOTO 20 50 PRINT 60 END Example 2: • 100 PRINT "TYPE P TO PROCEED OR S TO STOP" 110 X$=INPUT$(l) 120 IF X$="P" THEN 500 130 IF X$="S" THEN 700 ELSE 100 BASIC-80 FUNCTIONS                                      Page 3-11 3.18    INSTR Extended, Disk Action:         Searches for the first occurrence of string Y$ in X$ and returns the position at which the match is found.   Optional offset I sets the position for starting the search.   I must be in the range 1 to 255.  If I>LEN(X$) or if X$ is null or if Y$ cannot be found, INSTR returns O. If Y$ is null, INSTR returns I or 1. X$ and Y$ may be string variables, string expressions or string literals. 8K, Extended, Disk Action:        Returns a string comprised of the leftmost I characters of X$. I must be in the range 0 to 255. If I is greater than LEN (X$), the. entire string (X$) will be returned. If I=O, the null string (length zero) is returned. 8R, Extended, Disk Action:      Returns the number of      characters   in   X$. Non-printing characters and blanks are counted. Disk Action:      With random disk files, LOC returns the next record number to be used if a GET or PUT (without a record number)   is executed.  With sequential files, LOC returns the number of sectors (128 byte blocks) read from or written to the file since it was OPENed. 8K, Extended, Disk Action:       Returns the-natural logarithm of X.   X must     be greater than zero. Extended, Disk Action:       Returns the current position of the line printer print head within the line printer buffer. Does not necessarily give the physical position of the print head. X is a dummy argument. 8K, Extended, Disk Action:        Returns a string of length J characters from X$ beginning with the Ith character. I and J must be in the range 1 to 255. If J is omitted or if there are fewer than J characters to the right of the Ith character, all rightmost characters beginning with the Ith character are returned. If I>LEN(X$), MID$ returns a null string. Disk Action:        Convert numeric values to string values.    Any numeric value that is plac'ed in a random file buffer with an LSET or RSET statement must be converted to a string. MKI$ converts an integer to a 2-byte string.    MKS$ converts a single precision number to a 4-byte string.       MKD$ converts a double precision number to an 8-byte string. Extended, Disk Action:       Returns a string which represents the octal value of the decimal argument. X is rounded to an integer before OCT$(X) is evaluated. SK, Extended, Disk Action:       Returns the byte (decimal integer in the range a to 255)   read from memory location I. With the SK version of BASIC-SO, I must be less than 3276S.   To PEEK at a memory location above 3276S, subtract 65536 from the desired address. With Extended and Disk BASIC-SO, I must be in the range a to 65536. PEEK is the complementary function to the POKE statement, Section 2.4S. 8K, Extended, Disk Action:         Returns the current cursor     position.    The leftmost position is 1. X is a dummy argument. 8K, Extended, Disk Action:         Returns the rightmost I characters of string X$. If I=LEN{X$), returns X$.      If I=O, the null string (length zero) is returned. SK, Extended, Disk Action:      Returns a random number between 0 and 1.    The same sequence of random numbers is generated each time the program is RUN unless the random number generator is reseeded     (see RANDOMIZE, Section 2.53). However, X<O always restarts the same sequence for any given X. X>O or X omitted generates the next random number in the sequence. x=o repeats the last number generated. SK, Extended, Disk Action: .    If X>O, SGN(X) returns 1. If X=O, SGN(X) returns O. If X<O, SGN(X) returns -1. 8K, Extended, Disk Action:         Returns the sine of X in radians.   SIN (X) is calculated       in       single    precision. COS(X)=SIN(X+3.l4l59/2) • Extended, Disk Action:         Returns a string of spaces of length X.    The expression X is rounded to an integer and must be in the range 0 to 255. 8K, Extended, Disk Action:      Prints I blanks on the terminal. SPC may only be used with PRINT and LPRINT statements.   I must be in the range 0 to 255. 8K, Extended, Disk Action:      Returns the square root of X.   X must be >=0. 8K, Extended, Disk Action:       Returns a string representation of the value   of X. Extended, Disk- Action:       Returns a string of length I whose characters all have ASCII code J or the first character of X$. 8K, Extended, Disk Action:      Spaces to position I on the terminal.   If the current print position is already beyond space I, TAB goes to that position on the next line. Space 1 is the leftmost position, and the rightmost position is the width minus one.   I must be in the range 1 to 255. TAB may only be used in PRINT and LPRINT statements. 8K, Extended, Disk Action:      Returns the tangent of X in radians. TAN (X)  is calculated   in   single    preclslon.   If TAN overflows,  the "Overflow" error message      is displayed, machine infinity with the appropriate sign is supplied as the . result, and execution continues. 8K, Extended, Disk Action:      Calls the user's assembly language subroutine with the argument X. <digit> is allowed in the Extended and Disk versions only. <digit> is in the range 0 to 9 and corresponds to the digit supplied with the DEF USR statement for that routine.    If   <digit> is omitted, USRO is assumed. See Appendix x. 8K, Extended, Disk Action:      Returns the numerical value of string X$.  The VAL function also strips leading blanks, tabs, and linefeeds from the argument string.    For example, VAL (" -3) returns -3. Extended, Disk Format 2:        VARPTR(t<file number» Disk Action:      Format 1: Returns the address of the first byte of data identified with <variable name>. A value must be assigned to <variable name> prior to execution of VARPTR. Otherwise an "Illegal function call" error results. Any type variable name may be used (numeric, string, array), and the address returned will be an integer in the range 32767 to -32768. If a negative address is returned, add it to 65536 to obtain the actual address. VARPTR is usually used to obtain the address of a variable or array so it may be passed to an assembly language subroutine. A function call of the form VARPTR(A(O»       is usually specified when   passing   an    array,     so    that   the lowest-addressed    element    of    the array is returned. NOTE:        All simple variables should be assigned before calling   VARPTR   for an array, because the addresses of the arrays change whenever a new simple variable is assigned. Format 2: For sequential files,     returns the starting address of the disk I/O buffer assigned to <file number>. For random fles, returns the address of the FIELD buffer assigned to <file number>. In Standalone Disk BASIC, VARPTR(t<file number» returns the first byte of the file block. See Appendix H.

## Purpose

To write data to a sequential file. To print the names   of   files   residing   on   the current disk. To close all disk files and write the directory information to a diskette before it is removed ,from a disk drive.

## Remarks

<file number> is the number under which the file was OPENed in "0" mode. The expressions in the list are string or numeric expressions, and they must be separated by commas. The difference between WRITEi and PRINTi is that WRITEi inserts commas between the the items as they are written to disk and delimits strings with quotation marks.      Therefore, it is not necessary for the     user    to   put  explicit delimiters in the list. A carriage return/line feed sequence is inserted after the last item in the list is written to disk. If <filename> is omitted, all the files on the currently   selected   drive   will be listed. <filename> is a string formula which may contain question marks (?) to match any character in the filename or extension. An asterisk (*)   as the first character of the filename or extension will match any file or any extension. Always execute a RESET command before removing a diskette from a disk drive. Otherwise, when the diskette is used again, it will not have the current directory information written on the directory track. RES~T closes all open files on all drives and writes the directory track to every diskette with open files. Page 0-4 0.5   LOF FUNCTION

## Example

```basic
Let   A$="CAMERA"     and   B$="93604-1".       The
                statement:
                WRITEi1,A$,B$
                writes the following image to disk:
                "CAMERA", "93604-1"
                A subsequent INPUTi statement, such as:
                INPUTi1,A$,B$
                would input "CAMERA" to A$ and "93604-1" to BS.
                                                     Paae 3-1
                         CHAPTER 3
                     BASIC-80 FUNCTIONS
The intrinsic functions provided by BASIC-80 are presented
in this chapter.     The functions may be called from any
program without further definition.
Arguments to functions are always enclosed in parentheses.
In the formats given for the functions in this chapter, the
arguments have been abbreviated as follows:
   X and Y       Represent any numeric expressions
   I and J       Represent integer expressions
   X$ and Y$     Represent string expressions
If a floating point value is supplied where an integer is
required, BASIC-80 will round the fractional portion and use
the resulting integer.
                            NOTE
               With the BASIC-80 and BASIC-86
               interpreters, only integer and
               single precision resullts are
               returned by funtions.   Double
               precision    functions     are
               supported only by the BASIC
               compiler.
BASIC-80 FUNCTIONS                                      Page 3-2
3.1   ABS
PRINT ABS(7*(-5»
             35
            Ok
3.2   ASC
10 X$ = "TEST"
            20 PRINT ASC (X$)
            RUN
             84
            Ok
            See the CHR$        function   for   ASClI-to-string
            conversion.
BASIC-SO FUNCTIONS                                      Page 3-3
3.3   ATN
10 INPUT X
             20 PRINT ATN (X)
             RUN
             ? 3
              1.24905
             Ok
3.4   COBL
10 A = 454.67
             20 PRINT A:COBL(A)
             RUN
              454.67 454.6700134277344
             Ok
BASIC-80 FUNCTIONS                                      Page 3-4
3.5   CRR$
PRINT CHR$ (66)
             B
             Ok
             See the ASC       function   for   ASClI-to-numeric
             conversion.
3.6   CINT
PRINT CINT(45.67)
              46
             Ok
             See the CDBL and CSNG functions for converting
             numbers to the double precision and single
             precision data type. See also the FIX and INT
             functions, both of which return integers.
BASIC-SO FUNCTIONS                                      Page 3-5
3.7   COS
10 X = 2 *COS ( .4)
             20 PRINT X
             RUN
              1.S42l2
             Ok
3.S   CSNG
10 Ai = 975.3421#
             20 PRINT A#; CSNG{Ai)
             RUN
              975.3421 975.342
             Ok
             See the CINT and CDBL functions for converting
             numbers to the integer and double precision data
             types.
BASIC-80 FUNCTIONS                                        Page 3-6
3.9    CVI, CVS, CVD
              70 FIELD #1,4 AS N$, 12 AS B$, •••
              80 GET #1
              90 Y=CVS (N$)
              See also MKI$r   MKS$,   MKD$,   Section   3.25   and
              Appendix B.
3.10    EOF
10 OPEN "I",l,"DATA"
              20 C=O
              30 IF EOF(l) THEN 100
              40 INPUT #l,M(C)
              50 C=C+l:GOTO 30
BASIC-80 FUNCTIONS                                    Page 3-7
3.11   ~
10 X = 5
              20 PRINT EXP (X-I)
              RUN
               54.5982
              Ok
3.12
       -FIX
PRINT FIX(58.75)
               58
              Ok
              PRINT FIX(-58.75)
              -58
              Ok
BASIC-80 FUNCTIONS                                       Page 3-8
3.13   FRE
PRINT FRE(O)
               14542
              Ok
3.14   HEX$
10 INPUT X
              20 A$ = HEX$ (X)
              30 PRINT X "DECIMAL IS II A$ " HEXADECIMAL II
              RUN
              ? 32
               32 DECIMAL IS 20 HEXADECIMAL
              Ok
              See the OCT$ function for octal conversion.
BASIC-80 FUNCTIONS                                      Page 3-9
3.15   INKEY$
1000 ~TlMED INPUT SUBROUTINE
                1010 RESPONSE$=""
                1020 FOR I%=l TO TIMELIMIT%
                1030 A$=INKEY$ : IF LEN(A$)=O THEN 1060
                1040 IF ASC(A$)=13 THEN TIMEOUT%=O : RETURN
                1050 RESPONSE$=RESPONSE$+A$
                1060 NEXT I%
                1070 TIMEOUT%=l : RETURN
3.16   INP
100 A=INP(255)
BASIC-SO FUNCTIONS                                     Page 3-10
3.17   INPUT$
10 X$ = "ABCDEB"
                20 Y$ = "B"
                30 PRINT INSTR(X$,Y$) ;INSTR(4,X$,Y$)
                RUN
                 2 6
                Ok
NOTE:           If I=O is specified, error message "ILLEGAL
                ARGUMENT IN <line number>" will be returned.
BASIC-80 FUNCTIONS                                       Page 3-12
3.19   INT
PRINT INT ( 99. 89)
                99
               Ok
               PRINT INT(-12.ll}
               -13
               Ok
               See the FIX and CINT functions which also return
               integer values.
3.20   LEFT$
10 A$ = "BASIC-80"
               20 B$ = LEFT$(A$,5}
               30 PRINT B$
               BASIC
               Ok
               Also see the MID$ and RIGHT$ functions.
BASIC-80 FUNCTIONS                                  Page 3-13
3.21   LEN
10 X$ = "PORTLAND, OREGON"
             20 PRINT LEN (X$)
              16
             Ok
3.22   LOC
200 IF LOC(l) >50 THEN STOP
BASIC-80 FUNCTIONS                                      Page 3-14
3.23   LOG
PRINT LOG ( 45/7 )
               1.86075
              Ok
3.24   LPOS
100 IF LPOS(X) >60 THEN LPRINT CHR$(13)
BASIC-80 FUNCTIONS                                    Page 3-15
3.25    MID$
LIST
               10 A$=nGOOD n
               20 B$=nMORNING EVENING AFTERNOON"
               30 PRINT A$;MID$(B$,9,7)
               Ok
               RUN
               GOOD EVENING
               Ok
               Also see the LEFT$ and RIGHT$ functions.
NOTE:          If I=O is specified, error message "ILLEGAL
               ARGUMENT IN <line number>" will be returned.
3.26    MKI$, MKS$, MKD$
90 AMT= (K+T)
               100 FIELD #1, 8 AS D$, 20 AS N$
               110 LSET D$ = MKS$(AMT)
               120 LSET N$ = A$
               130 PUT #1
               See also CVI, CVS, CVD, Section 3.9 and Appendix
               B.
BASIC-SO FUNCTIONS                                    Page 3-16
              3.27   OCT$
PRINT OCT$ (24)
               30
              Ok
              See   the   HEX $    function   for   hexadecimal
              conversion.
3.2S   PEEK
A=PEEK (&H5AOO)
BASIC-80 FUNCTIONS                                       Page 3-17
3.29   POS
IF POS(X) >60 THEN PRINT CHR$(13)
                Also see the LPOS function.
3.30   RIGHT$
10 A$="DISK BASIC-80"
                20 PRINT RIGHT$(A$,8)
                RUN
                BASIC-80
                Ok
                Also see the MID$ and LEFT$ functions.
BASIC-SO FUNCTIONS                                  Page 3-1S
3.31   RND
10 FOR I=l TO 5
             20 PRINT INT(RND*100);
             30 NEXT
             RUN
              24 30 31 51 5
             Ok
3.32   SGN
ON SGN(X)+2 GOTO 100,200,300 branches to 100 if
             X is negative, 200 if X is 0 and 300 if X is
             positive.
BASIC-80 FUNCTIONS                                   Page 3-19
3.33   SIN
PRINT SIN(1.5)
                 .997495
                Ok
3.34   SPACES
10 FOR I = 1 TO 5
                20 X$ = SPACE$(I)
                30 PRINT X$;I
                40 NEXT I
                RUN
                     1
                         2
                             3
                                 4
                                     5
                Ok
                Also see the SPC function.
BASIC-80 FUNCTIONS                                   Page 3-20
3.35   SPC
PRINT "OVER" SPC(15) "THERE"
             OVER               ~ERE
             Ok
             Also see the SPACE$ function.
3.36   SQR
10 FOR X = 10 TO 25 STEP 5
             20 PRINT X, SQR(X)
             30 NEXT
             RUN
              10            3.16228
              15            3.87298
              20            4.47214
              25            5
             Ok
BASIC-80 FUNCTIONS                                   Page 3-21
3.37   STR$
5 REM ARITHMETIC FOR KIDS
              10 INPUT "TYPE A NUMBER";N
              20 ON LEN(STR$(N» GOSUB 30,100,200,300,400,500
              Also see the VAL function.
3.38   STRING$
Formats:      STRING$(I,J)
              STRING$(I,X$)
10 X$ = STRING$(10,45)
              20 PRINT X$ "MONTHLY REPORT" X$
              RUN
              ----------MONTHLY REPORT----------
              Ok
BASIC-80 FUNCTIONS                                   Page 3-22
3.39   TAB
10 PRINT "NAME" TAB (25) "AMOUNT" : PRINT
             20 READ A$ ,B$
             30 PRINT A$ TAB (25) B$
             40 DATA "G. T. JONES","$25.00"
             RUN
             NAME                     AMOUNT
             G. T. JONES             $25.00
             Ok
3.40   TAN
10 Y = Q*TAN(X)/2
BASIC-80 FUNCTIONS                                      Page 3-23
3.41   USR
Format :     USR[<digit>] (X)
40 B = T*SIN (Y)
             50 C = USR (B/2)
             60 D = USR(B/3)
3.42   VAL
10 READ NAME$,CITY$,STATE$,ZIP$
             20 IF VAL(ZIP$) <90000 OR VAL(ZIP$) >96699 THEN
             PRINT NAME$ TAB(25) "OUT OF STATE"
             30 IF VAL(ZIP$) >=90801 AND VAL(ZIP$) <=90815 THEN
             PRINT NAME$ TAB(25) "LONG BEACH"
             See the STR$   function   for   numeric   to   string
             conversion.
BASIC-80 FUNCTIONS                                   Page 3-24
3.43    VARPTR
Format 1:    VARPTR«variable name»
100 X=USR(VARPTR(Y»
                                                   Page A-l
                        APPENDIX A
           New Features in BASIC-SO, Release 5.0
The execution of BASIC programs written under Microsoft
BASIC, release 4.51 and earlier may be affected by some of
the new features in release 5.0. Before attempting to run
such programs, check for the following:
    1.   New reserved words: CALL, CHAIN, COMMON,     WHILE,
         WEND, WRITE, OPTION BASE, RANDOMIZE.
    2.   Conversion from floating point to integer values
         results in rounding, as opposed to truncation.
         This affects not only assignment statements (e.g.,
         I%=2.5 results in I%=3) , but also affects function
         and stat~ment evaluations (e.g., TAB(4.5) goes to
         the 5th position, A(1.5) yeilds A(2), and X=11.5
         MOD 4 yields 0 for X).
    3.   The body of a FOR ••• NEXT loop is skipped if the
         initial value of the loop times the sign of the
         step exceeds the final value times the sign of the
         step. See Section 2.22.
    4.   Division by zero and overflow no longer     produce
         fatal errors. See Section 1.S.1.2.
    5.   The RND function has been changed so that RND with
         no argument is the same as RND with a positive
         argument. The RND function generates the same
         sequence of random numbers with each RUN, unless
         RANDOMIZE is used. See Sections 2.53 and 3.31.
    6.   The rules for PRINTing single preclslon and double
         precision numbers have been changed. See Section
         2.49.
    7.   String space is allocated dynamically, and the
         first argument in a two-argument CLEAR statement
         sets the end of memory. The second argument sets
         the amount of stack space. See Section 2.4.
                                                       Page A-2
 8.   Responding to INPUT with too many or too few items,
      or with non-numeric characters instead of digits,
      causes the message "?Redo from start" to         be
      printed.   If a single variable is requested, a
      carriage return may be entered to indicate the
      default values of 0 for numeric input or null for
      string input. However, if more than one variable
      is requested, entering a carriage return will cause
      the "?Redo from start" message to be printed
      because too few items were entered. No assignment
      of input values is made until an         acceptable
      response is given.
 9.   There are two new field formatting characters for
      use with PRINT USING.      An ampersand is used for
      variable length string fields, and an underscore
      signifies a literal character in a format string.
10.   If the expression supplied with the WIDTH statement
      is 255, BASIC uses an "infinite" line width, that
      is, it does not insert carriage returns.       WIDTH
      LPRINT may be used to set the line width at the
      line printer. See Section 2.66.
11.   The at-sign and underscore are no    longer     used   as
      editing characters.
12.   Variable names are significant up to 40 characters
      and can contain embedded reserved words. However,
      reserved words must now be delimited by spaces. To
      maintain compatibility with earlier versions of
      BASIC, spaces will be      automatically   inserted
      between   adjoining reserved words and variable
      names.   WARNING: This insertion of spaces may
      cause the end of a line to be truncated if the line
      length is close to 255 characters.
13.   BASIC programs may be saved in a    protected     binary
      format.  See SAVE, Section 2.60.
                                                           Page B-1
                           APPENDIX B
                        BASIC-80 Disk I/O
Disk I/O procedures for the beginning BASIC-80 user are
examined in this appendix. If you are new to BASIC-80 or if
you~re getting  disk related errors, read through these
procedures and program examples to make sure you~re using
all the disk statements correctly.
Wherever a filename is required in a disk command or
statement, use a name that conforms to your operating
system~s requirements for  filenames.   The CP/M operating
system will append a default extension .BAS to the filename
given in a SAVE, RUN, MERGE or LOAD command.
B.l   PROGRAM FILE COMMANDS
Here is a review of the commands        and   statements   used   in
program file manipulation.
SAVE' <filename> [,A]    Writes to disk the program that is
                         currently     residing   in     memory.
                         Optional A writes the program as a
                         series     of      ASCII    characters.
                         (Otherwise, BASIC uses a compressed
                         binary format.)
LOAD <filename>[,R]     Loads the program from disk       into
                        memory.   Optional R runs the program
                        immediately. LOAD always deletes the
                        current contents of memory and closes
                        all files before LOADing.    If R is
                        included, however, open data files are
                        kept open.    Thus programs can     be
                        chained or loaded in sections and
                        access the same data files.
                                                      Page B-2
RUN <filename>[,R]      RUN <filename> loads the program from
                        disk into memory and runs it. RUN
                        deletes the current contents of memory
                        and closes all files before loading
                        the program.    If the R option is
                        included, however, all open data files
                        are kept open.
MERGE <filename>        Loads the program from disk       into
                        memory but does not delete the current
                        contents of memory. The program line
                        numbers on disk are merged with the
                        line numbers in memory.  If two lines
                        have the same number, only the line
                        from the disk program is saved. After
                        a MERGE command, the "merged" 'progr am
                        resides in memory, and BASIC returns
                        to command level.
KILL <filename>         Deletes the file from      the   disk.
                        <filename> may be a program file, or a
                        sequential or random access data file.
NAME <old filename>     To change the name of a disk file,
   AS<new filename>     execute the NAME     statement,   NAME
                        <oldfile> AS <newfile>. NAME may be
                        used with program files, random files,
                        or sequential files.
B.2   PROTECTED FILES
If you wish to save a program in an encoded binary format,
use the "Protect" option with the SAVE command.        For
example:
      SAVE "MYPROG",P
A program saved this way cannot be listed or edited.     You
may also want to save an unprotected copy of the program for
listing and editing purposes.
B.3   DISK DATA FILES ~ SEQUENTIAL AND RANDOM I/O
There are two types of disk data files that may be created
and accessed by a BASIC-80 program: sequential files and
random access files.
                                                               Page B-3
B.3.l       Sequential Files
Sequential files are easier to create than random files but
are limited in flexibility and speed when it comes to
accessing the data.     The data that is written to       a
sequential    file  is   stored,   one item after another
(sequentially), in the order it is sent and is read back in
the same way.
The statements and functions that are used            with   sequential
files are:
     OPEN     PRINTi           INPUTt        WRITEt
              PRINTt USING     LINE INPUTI
     CLOSE      EOF   LOC
The following program steps are required to                  create   a
sequential file and access the data in the file:
1.    OPEN the file in "0" mode.               OPEN "0", 11, "DATA"
2.   Write data to the file                    PRINTil,A$;B$;C$
     using the PRINTI statement.
     (WRITEt may be used instead.)
3.    To access the data in the                CLOSE 11
      file, you must CLOSE the file            OPEN "I", 11, "DATA"
      and reOPEN it in "I" mode.
4.    Use theINPUTt statement to               INPUTI1,X$,Y$,Z$
      read data from the sequential
      file into the program.
Program B-1 is a short program that creates a sequential
file, "DATA", from information you input at the terminal.
                                                      Page B-4
10 OPEN "0", *1, "DATA"
20 INPUT "NAME";N$
25 IF N$="DONE" THEN END
30 INPUT "DEPARTMENT";D$
40 INPUT "DATE HIRED";H$
50 PRINT*1,N$;",";D$1","1H$
60 PRINT:GOTO 20
RUN
NAME? MICKEY MOUSE
DEPARTMENT? AUDIO/VISUAL AIDS
DATE HIRED? 01/12/72
NAME? SHERLOCK HOLMES
DEPARTMENT? RESEARCH
DATE HIRED? 12/03/65
NAME? EBENEEZER SCROOGE
DEPARTMENT? ACCOUNTING
DATE HIRED? 04/27/78
NAME? SUPER MANN
DEPARTMENT? MAINTENANCE
DATE HIRED? 08/16/78
NAME? etc.
        PROGRAM B-1 - CREATE A SEQUENTIAL DATA FILE
                                                     Page B-5
Now look at Program B-2. It accesses the file "DATA" that
was created in Program B-1 and displays the name of everyone
hir~d in 1978.
10 OPEN "I",tl,"DATA"
20 INPUTtl,N$,D$,H$
30 IF RIGHT$(H$,2)="78" THEN PRINT N$
40 GOTO 20
R~
EBENEEZER SCROOGE
SUPER MANN
Input past end in 20
Ok
         PROGRAM B-2 - ACCESSING A SEQUENTIAL FILE
Program B-2 reads, sequentially, every item in the file.
When all the data has been read, line 20 causes an "Input
past end" error. To avoid getting this error, insert line
15 which uses the EOF function to test for end-of-file:
15 IF EOF(l) THEN END
and change line 40 to GOTO 15.
A program that creates a sequential file can also write
formatted data to the disk with the PRINTt USING statement.
For example, the statement
     PRINTtl,USING"tttt.tt,";A,B,C,D
could be used to write numeric data to disk without explicit
delimiters.   The comma at the end of the format string
serves to separate the items in the disk file.
The LOC function, when used with a sequential file, returns
the number of sectors that have been written to or read from
the file since it was OPENed. A sector is a l28-byte block
of data.
B.3.l.l Adding ~ To A Sequential File -
If you have a sequential file residing on disk and later
want to add more data to the end of it, you cannot simply
open the file in "0" mode and start writing data. As soon
as you open a sequential file in "0" mode, you destroy its
current contents. The following procedure can be used to
add data to an existing file called "NAMES".
                                                    Page B-6
    1.   OPEN "NAMES" in "I" mode.
    2.   OPEN a second file called "COPY" in "0" mode.
    3.   Read in the data in "NAMES" and write it to "COPY".
    4.   CLOSE "NAMES" and KILL it.
    5.   Write the new information to "COPY".
    6.   Rename "COPY" as "NAMES" and CLOSE.
    7.   Now there is a file on disk called "NAMES" that
         includes all the previous data plus the new data
         you just added.
Program B-3 illustrates this technique. It can be used to
create or add onto a file called NAMES. This program also
illustrates the use of LINE INPUT# to read strings with
embedded commas from the disk file. Remember, LINE INPUT#
will read in characters from the disk until it sees a
carriage return (it does not stop at quotes or commas) or
until it has read 255 characters.
                                                     Page B-7
10 ON ERROR GOTO 2000
20 OPEN "I",tl,"NAMES"
30 REM IF FILE EXISTS, WRITE IT TO "COPY"
40 OPEN "O",t2,"COPY"
SO IF EOF(l) THEN 90
60 LINE INPUTtl,A$
70 PRINTt2,A$
80 GOTO SO
90 CLOSE #1
100 KILL "NAMES"
110 REM ADD NEW ENTRIES TO FILE
120 INPUT "NAME";N$
130 IF N$="" THEN 200 ~CARRIAGE RETURN EXITS INPUT LOOP
140 LINE INPUT "ADDRESS? ";A$
150 LINE INPUT "BIRTHDAY? ";B$
160 PRINTt2,N$
170 PRINTt2,A$
180 PRINT#2,B$
190 PRINT:GOTO 120
200 CLOSE
205 REM CHANGE FILENAME BACK TO "NAMES"
210 NAME "COPY" AS "NAMES"
2000 IF ERR=53 AND ERL=20 THEN OPEN "O",#2,"COPY":RESUME 120
2010 ON ERROR GOTO 0
        PROGRAM B-3 - ADDING DATA TO A SEQUENTIAL FILE
The error trapping routine in line 2000 traps a "File does
not   exist" error in line 20.       If this happens, the
statements that copy the file are skipped, and "COPY" is
created as if it were a new file.
B.3.2   Random Files
Creating and accessing random files requires more program
steps than sequential files,      but there are advantages to
using random files. One advantage is that random files
require less room on the disk, because BASIC stores them in
a packed binary format.   (A sequential file is stored as a
series of ASCII characters.)
The biggest advantage to random files is that data can be
accessed randomly,   i.e., anywhere on the disk -- it is not
necessary to read through all the information, as with
sequential files. This is possible because the information
is stored and accessed in distinct units called records and
each record is numbered.
The statements and functions that are used with random files
are:
                                                          page B-8
     OPEN    FIELD   LSET/RSET   GET
     PUT     CLOSE   Loe
     MI<I$   CVI
     MKS$    CVS
     MKD$    CVD
B.3.2.l Creating A Random File -
The following program steps-are required to create a        random
file.
1.    OPEN the file for random        OPEN "R",il,"FILE",32
      access ("R" mode). This example
      specifies a record length of 32
      bytes. If the record length is
      omitted, the default is 128
      bytes.
2.    Use the FIELD statement to       FIELD il 20 AS N$,
      allocate space in the random      '4 AS A$, 8 AS P$
      buffer for the variables that
      will be written to the random
      file.
3.    Use LSET to move the data       LSET N$=X$
      into the random buffer.         LSET A$=MKS$(AMT)
      Numeric values must be made     LSET P$=TEL$
      into strings when placed in
      the buffer. To do this, use the
      "make" functions: MKI$ to
      make an integer value into a
      string, MKS$ for a single
      precision value, and MKD$ for
      a double precision value.
4.    Write the data from              PUT il,CODE%
      the buffer to the disk
      using the PUT statement.
Look at Program B-4. It takes information that is input at
the terminal and writes it to a random file. Each time the
PUT statement is executed, a record is written to the file.
The two-digit code that is input in line 30 becomes the
record number.
                                                       Page B-9
                             NOTE
                Do not use a FIELDed string
                variable in an INPUT or LET
                statement.   This causes the
                pointer for that variable to
                point   into   string   space
                instead of the random file
                buffer.
10 OPEN "R",ll,"FILE",32
20 FIELD 11,20 AS N$, 4 AS A$, 8 AS p$
30 INPUT "2-DIGIT CODE"1CODE%
40 INPUT nNAME"1X$
50 INPUT "AMOUNT";AMT
60 INPUT "PHONE";TEL$:PRINT
70 LSET N$=X$
80 LSET A$=MKS$(AMT)
90 LSET P$=TEL$
100 PUT Il,CODE%
110 GOTO 30
              PROGRAM B-4 - CREATE A RANDOM FILE
B.3.2.2 Access A Random File -
The following program steps are required to access a     random
file:
1.   OPEN the file in "R" mode.       OPEN "R",ll,"FILE",32
2.   Use the FIELD statement to       FIELD 11 20 AS N$,
     allocate space in the random            4 AS A$, 8 AS p$
     buffer for the variables that
     will be read from the file.
NOTE:
In a program that performs both
input and output on the same random
file, you can often use just one
OPEN statement and one FIELD
statement.
                                                           Page B-10
3.   Use the GET statement to move        GET il,CODE%
     the desired record into the
     random buffer.
4.   The data in the buffer ma'y          PRINT N$
     now be accessed by the program.      PRINT CVS (A$)
     Numeric values must be converted
     back to numbers using the
     "convert" functions: CVI for
     integers, CVS for single
     precision values, and CVD
     for double precision values.
Program B-5 accesses the random file "FILE" that was created
in Program B-4.     By inputting the three-digit code at the
terminal, the information associated with that code is read
from the file and displayed.
10 OPEN "R",il,"FILE",32
20 FIELD iI, 20 AS N$, 4 AS A$, 8 AS p$
30 INPUT "2-DIGIT CODE"1CODE%
40 GET tl, CODE%
50 PRINT N$
60 PRINT USING· "$$tti.ii"1CVS(A$)
70 PRINT P$:PRINT          .
80 GOTO 30
              PROGRAM B-5 - ACCESS A RANDOM FILE
The LOC function, with random files, returns the "current
record number." The current record number is one plus the
last record number that was used in a GET or PUT statement.
For example, the statement
      IF LOC(l) >50 THEN END
ends program execution if      the   current   record    number   in
filetl is higher than 50.
Program B-6 is an inventory program that illustrates random
file access. In this program, the record number is used as
the part number, and it is assumed the inventory will
contain no more than 100 different part numbers. Lines
900-960 initialize the data file by writing CHR$(255) as the
first character of each record. This is used later (line
270 and line 500) to determine whether an entry already
exists for that part number.
Lines 130-220 display the different inventory functions that
the program performs. When you type in the desired function
number, line 230 branches to the appropriate subroutine.
                                                   Page B-11
120 OPEN"R",#1,"INVEN.DAT",39
125 FIELD#l,l AS F$,30 AS D$, 2 AS Q$,2 AS R$,4 AS P$
130 PRINT:PRINT "FUNCTIONS:":PRINT
135 PRINT 1,"INITIALIZE FILE"
140 PRINT 2,"CREATE A NEW ENTRY"
150 PRINT 3,"DISPLAY INVENTORY FOR ONE PART"
160 PRINT 4,"ADD TO STOCK"
170 PRINT 5,"SUBTRACT FROM STOCK"
180 PRINT 6, "DISPLAY ALL ITEMS BELOW REORDER LEVEL"
220 PRINT:PRINT:INPUT"FUNCTION";FUNCTION
225 IF (FUNCTION<l) OR (FUNCTION>6) THEN PRINT
          "BAD FUNCTION NUMBER":GO TO 130
230 ON FUNCTION GOSUB 900,250,390,480,560,680
240 GOTO 220
250 REM BUILD NEW ENTRY
260 GOSUB 840
270 IF ASC(F$) <>255 THEN INPUT"OVERWRITE";A$:
          IF A$<>"Y" THEN RETURN
280 LSET F$=CHR$(O)
290 INPUT "DESCRIPTION";DESC$
300 LSET D$=DESC$
310 INPUT "QUANTITY IN STOCK";Q%
320 LSET Q$=MKI$(Q%)
330 INPUT "REORDER LEVEL";R%
340 LSET R$=MKI$(R%)
350 INPUT "UNIT PRICE";P
360 LSET P$=MKS$(P)
370 POT#l,PART%
380 RETURN
390 REM DISPLAY ENTRY
400 GOSUB 840
410 IF ASC(F$) =255 THEN PRINT "NULL ENTRY." : RETURN
420 PRINT USING "PART NUMBER iii";PART%
430 PRINT 0$
440 PRINT USING "QUANTITY ON HAND #i#ii";CVI(Q$)
450 PRINT USING "REORDER LEVEL iiiii";CVI(R$)
460 PRINT USING "UNIT PRICE $$i#.ii";CVS(P$)
470 RETURN
480 REM ADD TO STOCK
490 GOSUB 840
500 IF ASC(F$) =255 THEN PRINT "NULL ENTRY":RETURN
510 PRINT D$:INPUT "QUANTITY TO ADD ":A%
520 Q%=CVI(Q$)+A%
530 LSET Q$=MKI$(Q%)
540 PUTi1,PART%
550 RETURN
560 REM REMOVE FROM STOCK
570 GOSUB 840
580 IF ASC(F$)=255 THEN PRINT "NULL ENTRY":RETURN
590 PRINT 0$
600 INPUT "QUANTITY TO SUBTRACT";S%
610 Q%=CVI(Q$)
620 IF (Q%-S%)<O THEN PRINT "ONLY";Q%;" IN STOCK":GOTO 600
630 Q%=Q%-S%
                                                     Page B-12
640 IF Q%=<CVI(R$) THEN PRINT "QUANTITY NOW":Q%:
          " REORDER LEVEL":CVI(R$)
650 LSET Q$=MKI$(Q%)
660 PUTt1,PART%
670 RETURN
680 DISPLAY ITEMS BELOW REORDER LEVEL
690 FOR 1=1 TO 100
710 GETt1,I
720 IF CVI(Q$) <CVI(R$) THEN PRINT 0$:" QUANTITY":
           CVI(Q$) TAB (50) "REORDER LEVEL":CVI(R$)
730 NEXT I
740 RETURN
840 INPUT "PART NUMBER":PART%
850 IF (PART%<l) OR(PART%>100) THEN PRINT "BAD PART .NUMBER":
          GOTO 840 ELSE GETt1,PART%:RETURN
890 END
900 REM INITIALIZE FILE
910 INPUT "ARE YOU SURE":B$:IF B$<>"Y" THEN RETURN
920 LSET F$=CHR$(255)
930 FOR 1=1 TO 100
940 PUTt1,I
950 NEXT I
960 RETURN
PROGRAM B-6 - INVENTORY
                                                    Page C-l
                          APPENDIX C
                Assembly Language Subroutines
All versions of BASIC-80 have prov~s~ons for interfacing
with assembly language subroutines. The OSR function allows
assembly language subroutines to be called in the same way
BASIC~s intrinsic functions are called.
                             NOTE
               The addresses of the DEINT,
               GIVABF,   MAKINT   and FRCINT
               routines   are    stored   in
               locations    that    must  be
               supplied   individually   for
               different implementations of
               BASIC.
C.l   MEMORY ALLOCATION
Memory space must be set aside for an assembly language
subroutine before it can be loaded. During initialization,
enter the highest memory location minus the amount of memory
needed for the assembly language subroutine(s). BASIC uses
all memory available from its starting location up, so only
the topmost locations in memory can be set aside for user
subroutines.
When an assembly language subroutine is called, the stack
pointer is set up for 8 levels (16 bytes) of stack storage.
If more stack space is needed, BASIC~s stack can be saved
and a new stack set up for use by the assembly language
subroutine. BASIC~s stack must be restored, however, before
returning from the subroutine.
                                                         Page C-2
The assembly language subroutine may be loaded into memory
by means of the system monitor, or the BASIC POKE statement,
or (if the user has the MACRO-80 or FORTRAN-80 package)
routines may be assembled with MACRO-80 and loaded using
LINK-80.
C.2   USR FUNCTION CALLS - 8K BASIC
The starting address of the assembly language subroutine
must be stored in USRLOC, a two-byte location in memory that
is supplied individually with different implementations of
BASIC-80.   With 8K BASIC, the starting address may be POKEd
into USRLOC. Store the low order byte first, followed by
the high order byte.
The function USR will call the routine whose address is in
USRLOC.   Initially USRLOC contains the address of ILLFUN,
the routine that gives the "Illegal function call" error.
Therefore, if USR is called without changing the address in
USRLOC, an "Illegal function call" error results.
The format of a USR function call is
      USR (argument)
where the argument is a numeric expression. To obtain the
argument, the assembly language subroutine must call the
routine DEINT. DEINT places the argument into the D,E
register pair as a 2-byte, 2~s complement integer. (If the
argument is not in the range -32768 to 32767, an "Illegal
function call" error occurs.)
To pass the result back from        an   assembly   language
subroutine, load the value in register pair [A,B], and call
the routine GIVABF.  If GIVABF is not called, USR(X) returns
X.   To return to BASIC, the assembly language subroutine
must execute a RET instruction.
For example, here is an assembly      language   subroutine   that
mUltiplies the argument by 2:
USRSUB: CALL DEINT       ;put arg in D,E
        XCHG             ;move arg to H, L
         DAD H           ;H,L=H,L+H,L
         MOV A,H         ;move result to A,B
         MOV B,L
         JMP GIVABF      ;pass result back and RETurn
Note that valid results will be obtained from this routine
for arguments in the range -16384<=x<=16383. The single
instruction JMP GIVABF has the same effect as:
                                                                    Page C-3
              CALL GIVABF
              RET
To return additional values to the program, load                  them    into
memory and read them with the PEEK function.
There are several methods by which a program may call more
than one USR routine. For example, the starting address of
each routine may be POKEd into USRLOC prior to each USR
call, or the argument to USR could be an index into a table
of USR routines.
C.3        USR FUNCTION CALLS - EXTENDED !!Q DISK BASIC
In the Extended and Disk versions, the              format   of     the   USR
function is
           USR[<digit>] (argument)
where DIGIT> is from 0 to 9 and the argument is any numeric
or string expression. <digit> specifies which USR routine
is being called, and corresponds with the digit supplied in
the DEF USR statement for that routine. If <digit> is
omitted, USRO is assumed. The address given in the DEF USR
statement determines the starting address of the subroutine.
When the USR function call is made, register A contains a
value that specifies the type of argument that was given.
The value in A may be one of the following:
Value in A           ~      of Argument
       2             Two-byte integer     (two~s   complement)
       3             String
       4             Single precision floating point number
       8             Double precision floating point number
If the argument is a number, the [H,L] register pair points
to the Floating Point Accumulator (FAC) where the argument
is stored.
If the argument is an integer:
      FAC-3 contains the lower 8 bits of the argument and
      FAC-2 contains the upper 8 bits of the argument.
If the argument is a single precision floating point number:
      FAC-3, contains the lowest 8 bits of mantissa and
                                                      Page C-4
   FAC-2 contains the middle 8 bits of mantissa and
   FAC-l contains the highest 7 bits of mantissa
   with leading 1 suppressed (implied). Bit 7 is
   the sign of the number (O=positive, l=negative).
   FAC is the exponent minus 128, and the binary
   point is to the left of the most significant
   bit of the mantissa.
If the argument is a double precision floating point number:
   FAC-7 through FAC-4 contain four more bytes
   of mantissa (FAC-7 contains the lowest 8 bits).
If the argument is a string, the [D,E] register pair points
to 3 bytes called the nstring descriptor. n Byte 0 of the
string descriptor contains the length of the string (0 to
255) •  Bytes 1 and 2, respectively, are the lower and upper
8 bits of the string starting address in string space.
CAUTION: If the argument is a string literal in the
program, the string descriptor will point to program text.
Be careful not to alter or destroy your program this way.
To avoid unpredictable results, add +"n to the string
literal in the program. Example:
     A$ = nBASIC-80 n+ nn
This will copy the strin~ literal into string space and will
prevent alteration of program text during a subroutine call.
Usually, the value returned by a USR function is the same
type (integer, string, single precision or double precision)
as the argument that was passed to it. However, calling the
MAKINT . routine returns the integer in [H,L] as the value of
the function, forcing the value returned by the function to
be integer.     To execute MAKINT, use the following sequence
to return from the subroutine:
   PUSH     H       ;save value to be returned
   LHLD    xxx      ;get address of MAKINT routine
   XTHL             ;save return on stack and
                    ;get back [H,L]
   RET              ;return
Also, the argument of the function, regardless of its type,
may be forced to an integer by calling the FRCINT routine to
get the integer value of the argument in [H,L]. Execute the
following routine:
   LXI       H       ;get address of subroutine
                     ;continuation
  PUSH      H        ;place on stack
  LHLD     xxx       ;get address of FRCINT
  PCHL
SUBl:    .....
                                                      Page C-S
C.4   CALL STATEMENT
Extended and Disk BASIC-80 user function calls may also be
made with the CALL statement. The calling sequence used is
the same as that in Microsoft's FORTRAN, COBOL and BASIC
compilers.
A CALL statement with no arguments generates a simple "CALL"
instruction. The corresponding subroutine should return via
a simple "RET." (CALL and RET are 8080 opcodes - see an 8080
reference manual for details.)
A subroutine CALL with arguments results in a somewhat more
complex calling sequence.     For each argument in the CALL
argument list, a parameter is passed to the subroutine.
That parameter is the address of the low byte of the
argument. Therefore, parameters always occupy two bytes
each, regardless of type.
The method of passing the parameters depends upon the number
of parameters to pass:
      1.   If the number of parameters is less than or equal
           to 3, they are passed in the registers. Parameter
           1 will be in HL, 2 in DE (if present), and 3 in BC
           (if present).
      2.   If the number of parameters is greater than 3, they
           are passed as follows:
           1.   Parameter 1 in HL.
           2.   Parameter 2 in DE.
           3.   Parameters 3 through n in a contiguous data
                block.   BC will point to the low byte of this
                data block (i.e., to the low byte of parameter
                3) •
Note that, with this scheme, the subroutine must know how
many   parameters    to  expect   in order to find them.
Conversely, the calling program is responsible for passing
the correct number of parameters. There are no checks for
the correct number or type of parameters.
If the subroutine expects more than 3 parameters, and needs
to transfer them to a local data area, there is a system
subroutine which will perform this transfer. This argument
transfer routine is named $AT (located in the FORTRAN
library, FORLIB.REL), and is called with HL pointing to the
local data area, BC pointing to the third parameter, and A
containing the number of arguments to transfer    (i.e., the
total number of arguments minus 2).        The subroutine is
                                                                    Page C-6
responsible for saving the first two parameters before
calling $AT.    For example, if a subroutine expects 5
parameters, it should look like:
SUBR: SHLD           PI           iSAVE PARAMETER 1
      XCHG
      SHLD           P2           iSAVE PARAMETER 2
      MVI            A,3          iNO. OF PARAMETERS LEFT
      LXI            H,P3         iPOINTER TO LOCAL AREA
      CALL           $AT          iTRANSFER THE OTHER 3 PARAMETERS
        .[Body of subroutine]
        RET                       i RETURN TO CALLER
PI:     DS           2            iSPACE FOR PARAMETER 1
P2:     DS           2            iSPACE FOR PARAMETER 2
P3:     DS           6            iSPACE FOR PARAMETERS 3-5
A listing of the argument transfer routine $AT follows.
00100     .,               ARGUMENT TRANSFER
00200     i [B, C]        POINTS TO 3RD PARAM.
00300     i [H, L]        POINTS TO LOCAL STORAGE FOR PARAM 3
00400     i [A]           CONTAINS THE t OF PARAMS TO XFER (TOTAL-2)
00500
00600
00700                     ENTRY     $AT
00800     $AT:            XCHG                  iSAVE [H,L] IN [D,E]
00900                     MOV       H,B
01000                     MOV       L,C         i [H,L]   = PTR TO PARAMS
01100     ATl:            MOV       C,M
01200                     INX       H
01300                     MOV       B,M
01400                     INX       H           i[B,C]    = PARAM ADR
01500                     XCHG                  i [H,L]   POINTS TO LOCAL STORAGE
01600                     MOV      M,C
01700                     INX      H
01800                     MOV      M,B
01900                     INX      H            iSTORE PARAM IN LOCAL AREA
02000                     XCHG                  iSINCE GOING BACK TO ATI
02100                     DCR       A           iTRANSFERRED ALL PARAMS?
02200                     JNZ       ATI         iNO, COPY MORE
02300                     RET                   i YES, RETURN
                                                    Page C-7
When accessing parameters in a subroutine, don~t forget that
they are pointers to the actual arguments passed.
                             NOTE
                It is entirely up to       the
                programmer to see to it that
                the arguments in the calling
                program match in number, ~,
                and length with the parameters
                expected by the subroutine.
                This    applies    to    BASIC
                subroutines, as well as those
                written in assembly language.
C. 5   INTERRUPTS
Assembly language subroutines can be written to handle
interrupts. All interrupt handling routines should save the
stack, register A-L and the PSW. Interrupts should always
be re-enabled before returning from the subroutine., since
an interrupt automatically disables all further interrupts
once it is received.      The user should be aware of which
interrupt vectors are free in the particular version of
BASIC that has been supplied.  (Note to CP/M users: In CP/M
BASIC, all interrupt vectors are free.)
                                                             Page D-l
                           APPENDIX D
            BASIC-~O   with the CP/M Operating System
The CP/M version of BASIC-80   (MBASIC)  is supplied on a
standard size 3740 single density diskette. The name of the
file is MBASIC.COM.    (A 28K or larger CP/M system is
recommended. )
To run MBASIC, bring up CP/M and type the following:
      A>MBASIC <carriage return>
The system will reply:
      xxxx Bytes Free
      BASIC-80 Version 5.0
      (CP/M Version)
      Copyright 1978 (C) by Microsoft
      Created: dd-mmm-yy
      Ok
MBASIC is the same as Disk BASIC-80 as      described   in   this
manual, with the following exceptions:
D.l   INITIALIZATION
The initialization dialog has been replaced by a set of
options which are placed after the MBASIC command to CP/M.
The format of the command line is:
A>MBASIC [<filename>] [/F:<number of files>] [/M:<highest memory location>]
      [/S:<maximum record size>]
If <filename> is present, MBASIC proceeds as if a RUN
<filename>   command were typed after initialization is
complete. A default extension of .BAS is used if none is
supplied and the filename is less than 9 characters long.
This allows BASIC programs to be executed in batch mode
using the SUBMIT facility of CP/M. Such programs should
include a SYSTEM statement (see below) to return to CP/M
when they have finished, allowing the next program in the
                                                           Page 0-2
batch stream to execute.
If /F:<number of files> is present, it sets the number of
disk data files that may be open at anyone time during the
execution of a BASIC program.       Each file data     block
allocated in this fashion requires 166 bytes of memory.   If
the /F option is omitted, the number of files defaults to 3.
The /M:<highest memory location> option sets the highest
memory location that will be used by MBASIC.   In some cases
it is desirable to set the amount of memory well below the
CP/M~s   FOOS   to   reserve space for assembly language
subroutines. In all cases, <highest memory location> should
be below the start of FOOS . (whose address is contained in
locations 6 and 7). If the 1M option is omitted, all memory
up to the start of FOOS is used.
/S:<maximum record size> may be added at the end of the
command line to set the maximum record size for use with
random files. The default record size is 128 bytes.
                               NOTE
               <number of files>, <highest
               memory location>, and <maximum
               record size> are numbers that
               may be either decimal, octal
               (preceded    by     &0)      or
               hexadecimal (preceded by &H) •
A>MBASIC PAYROLL. BAS      Use all memory and 3 files,
                           load and execute PAYROLL. BAS.
A>MBASIC INVENT/F:6        Use all memory and 6 files,
                           load and execute INVENT. BAS.
A>MBASIC /M:32768          Use first 32K of memory and
                           3 files.
A>MBASIC OATACK/F:2/M:&H9000
                        Use first 36K of memory, 2
                        files, and execute OATACK.BAS.
0.2   DISK FILES
Disk filenames follow the normal CP/M naming conventions.
All filenames may include A:       or B:    as the first two
characters to specify a disk drive, otherwise the currently
selected drive is assumed. A default extension of .BAS is
                                                          Page D-3
used on LOAD, SAVE, MERGE and RUN <filename> commands if no
"." appears in the filename and the filename is less than 9
characters long.
For systems with CP/M 2.x, large random files are supported.
The maximum logical record number is 32767. If a record
size of 256 is specified, then files up to 8 megabytes can
be accessed.
D.3   FILES COMMAND
FILES
             FILES "*.BAS"
             FILES "B:*.*"
             FILES "TEST?BAS"
D.4   RESET COMMAND
110 IF NUM%>LOF(~} THEN PRINT "INVALID ENTRY"
0.6   EOF
With CP/M, the EOF function may be used with random files.
If a GET is done past the end of file, EOF will return -1.
This may be used to find the size of a file using a binary
~earch or other algorithm.
0.7   MISCELLANEOUS
      1.    CSAVE and CLOAD are not implemented.
      2.    To return to CP/M, use the SYSTEM command or
            statement.   SYSTEM closes all files and then
            performs a CP/M warm start.     Control-C always
            returns to MBASIC, not to CP/M.
      3.    FRCINT is at 103 hex and MAKINT is at 105 hex.
            (Add 1000 hex for ADDS versions, 4000 for SBC CP/M
            versions.)
                                                          Page E-1
                           APPENDIX E
               Converting Programs to BASIC-80
If you have programs written in a BASIC other than BASIC-80,
some minor adjustments may be necessary before running them
with BASIC-80. Here are some specific things to look for
when converting BASIC programs.
E.1    STRING DIMENSIONS
Delete all statements that are used to declare the length of
strings.   A statement such as DIM A$(I,J), which dimensions
a string array for J elements of length I, should be
converted to the BASIC-80 statement DIM A$(J).
Some BASICs use a        comma   or  ampersand   for string
concatenation.    Each of these must be changed to a plus
sign, which    is    the    operator  for   BASIC-80 string
concatenation.
In BASIC-80, the MID$, RIGHT$, and LEFT$ functions are used
to take substrings of strings.       Forms such as A$(I) to
access the Ith character in A$, or A$(I,J)       to take a
substring of A$ from position I to position J, must be
changed as follows:
      Other BASIC          BASIC-80
       X$=A$ (I)       X$=MID$ (A$, 1,1)
       X$=A$(I,J)      X$=MID$(A$,I,J-I+l)
If the substring reference is on the left side of an
assignment and X$ is used to replace characters in A$,
convert as follows:
      Other BASIC          8K BASIC-80
       A$(I)=X$            A$=LEFT$ (A$,I-l) +X$+MID$(A$,I+l)
       A$(I,J)=X$          A$=LEFT$(A$,I-l) ;X$;MID$(A$,J+l)
                           Ext. and Disk BASIC-80
                           ------
       A$(I)=X$            MID$(A$,l,l)=X$
       A$(I,J9=X$          MID$(A$,I,J-I+l)=X$
                                                 Page E-2
E.2   MULTIPLE ASSIGNMENTS
Some BASICs allow statements of the form:
      10 LET B=C=O
to set Band C equal to zero. BASIC-80 would interpret the
second equal sign as a logical operator and set B equal to
-1 if C equaled O. Instead, convert this statement to two
assignment statements:
      10 C=O:B=O
E.3   MULTIPLE STATEMENTS
Some BASICs use a backs1ash (\)       to separate multiple
statements on a line. With BASIC-80, be sure all statements
on a line are separated by a colon (:).
E.4   MAT FUNCTIONS
Programs using the MAT functions available in some BASICs
must   be   rewritten using FOR ••• NEXT loops to execute
properly.
                                                           Page F-l
                          APPENDIX F
         Summary of Error Codes and Error Messages
Code   Number                          Message
 NF       1     NEXT without FOR
                A variable in a NEXT statement            does not
                correspond   to    any  previously        executed,
                unmatched FOR statement variable.
 SN       2     Syntax error
                A line is encountered that contains some
                incorrect sequence of characters (such as
                unmatched parenthesis, misspelled command or
                statement, incorrect punctuation, etc.).
 RG       3     Return without GOSUB
                A RETURN statement is encountered for         which
                there   is    no  previous, unmatched         GOSUB
                statement.
 OD       4     Out of data
                A READ statement is executed when there are
                no DATA statements with unread data remaining
                in the program.
 FC       5     Illegal function call
                A parameter that is out of range is passed to
                a math or string function. An FC error may
                also occur as the result of:
                1.   a   negative   or     unreasonably       large
                     subscript
                2.   a negative or zero argument with LOG
                3.   a negative argument to SQR
                4.   a negative mantissa    with   a   non-integer
                     exponent
                                                  Page F-2
          5.   a call to a USR function for which the
               starting address has not yet been given
          6.   an improper argument to MID$, LEFT$,
               RIGHT$,    INP, OUT, WAIT, PEEK, POKE, TAB,
               SPC,     STRING$,   SPACES,    INSTR,    or
               ON ••• GOTO.
OV    6   OVerflow
          The result of a calculation is too large to
          be represented in BASIC-80"'s n,umber format.
          If underflow occurs, the result is zero and
          execution continues without an error.
OM    7   Out of memory
          A program is too large, has too many FOR
          loops or GOSUBs, too many variables, or
          expressions that are too complicated.
UL    8   Undefined line
          A line       reference    in   a    GOTO,   GOSUB,
          IF ••• THEN ••• ELSE   or    DELETE    is   to   a
          nonexistent line.
BS    9   Subscript out of range
          An array element is referenced either with a
          subscript that is outside the dimensions of
          the array, or with the wrong number of
          subscripts.
DD   10   Redimensioned array
          Two DIM statements are given for the same
          array, or a DIM statement is given for an
          array after the default dimension of 10 has
          been established for that array.
/0   11   Division by zero
          A division by zero is encountered in an
          expression, or the operation of involution
          results in zero being rai.sed to a negative
          power. Machine infinity with the sign of the
          numerator is supplied as the result of the
          division, or positive machine infinity is
          supplied as the result of the involution, and
          execution continues.
ID   12   Illegal direct
          A statement that is illegal in direct mode is
          entered as a direct mode command.
TM   13   Type mismatch
          A string variable name is assigned a numeric
          value or vice versa; a function that expects
          a numeric argument is given a string argument
          or vice versa.
                                                          Page F-3
os   14   Out of string space
          String variables have caused BASIC to exceed
          the amount of free memory remaining. BASIC
          will allocate string space dynamically, until
          it runs out of memory.
LS   15   String too long
          An attempt is made to create     a     string          more
          than 255 characters long.
ST   16   String formula too complex
          A string expression is too long or too
          complex.   The expression should be broken
          into smaller expressions.
CN   17   Can~t continue
          An attempt is made     to   continue       a     program
          that:
          1.   has halted due to an error,
          2.   has been modified      during     a       break     in
               execution, or
          3.   does not exist.
UF   18   Undefined user function
          A USR function is called before the function
          definition (DEF statement) is given.
          Extended and Disk Versions Only
     19   No RESUME
          An error trapping routine is           entered          but
          contains no RESUME statement.
     20   RESUME without error
          A RESUME statement is encountered before                 an
          error trapping routine is entered.
     21   Unprintable error
          An error message is not available fur ~e
          error   condition   which exists.   This is
          usually caused by an ERROR with an undefined
          error code.
     22   Missing operand
          An expression contains an     operator         with      no
          operand following it.
     23   Line buffer overflow
          An attempt is made to input a line             that    has
          too many characters.
                                             Page F-4
26   FOR without NEXT
     A FOR was encountered    without    a    matching
     NEXT.
29   WHILE without WEND
     A WHILE statement does not   have   a-- matching
     WEND.
30   WEND without WHILE
     A WEND was encountered   without    a    matching
     WHILE.
     Disk Errors
50   Field overflow
     A FIELD statement is attempting to allocate
     more bytes than were specified for the record
     length of a random file.
51   Internal error
     An internal malfunction has occurred in      Disk
     BASIC-80.
52   Bad file number
     A statement or command references a file with
     a file number that is not OPEN or is out of
     the range of file numbers specified        at
     initialization.
53   File not found
     A LOAD, KILL or OPEN statement references a
     file that does not exist on the current disk.
54   Bad file mode
     An attempt is made to use PUT, GET, or LOF
     with a sequential file, to LOAD a random file
     or to execute an OPEN with a file mode other
     than I, 0, or R.
55   File already open
     A sequential output mode OPEN is issued for a
     file that is already open1       or a KILL is
     given for a file that is open.
57   Disk I/O error
     An I/O error occurred on     a   disk     I/O
     operation.   It is a fatal error, i. e. , the
     operating system cannot recover from the
     error.
                                         Page F-5
58   File already exists
     The filename specified in a NAME statement is
     identical to a filename already in use on the
     disk.
61   Disk full
     All disk storage space is in use.
62   Input past end
     An INPUT statement is exeucted after all the
     data in the file has been INPUT, or for a
     null. (empty) file. To avoid this error, use
     the EOF function to detect the end of file.
63   Bad record number
     In a PUT or GET statement, the record number
     is either greater than the maximum allowed
     (32767) or equal to zero.
64   Bad file name
     An illegal form is used for the filename with
     LOAD, SAVE, KILL, or OPEN (e.g., a filename
     with too many characters).
66   Direct statement in file
     A direct statement is encountered   while
     LOADing an ASCII-format file. The LOAD is
     terminated.
67   Too many files
     An attempt is made to create a new file
     (using SAVE or OPEN) when all 255 directory
     entries are full.
                                                         Page G-l
                         APPENDIX G
                    Mathematical Functions
Derived Functions
Functions that are not     intrinsic   to    BASIC-80   may   be
calculated as follows.
Function               BASIC-80 Equivalent
SECANT                 SEC(X)=l/COS(X)
COSECANT               CSC(X)=l/SIN(X)
COTANGENT              COT(X)=l/TAN(X)
INVERSE SINE           ARCSIN(X)=ATN(X/SQR(-X*X+l»
INVERSE COSINE         ARCCOS(X)=-ATN (X/SQR(-X*X+l»+1.5708
INVERSE SECANT         ARCSEC(X)=ATN(X/SQR(X*X-l»
                           +SGN(SGN(X)-l) *1.5708
INVERSE COSECANT       ARCCSC(X)=ATN(X/SQR(X*X-l»
                           +(SGN(X)-l) *1.5708
INVERSE COTANGENT      ARCCOT(X) =ATN(X) +1.5708
HYPERBOLIC SINE        SINH(X)=(EXP(X)-EXP(-X»/2
HYPERBOLIC COSINE      COSH(X)=(EXP(X)+EXP(-X»/2·
HYPERBOLIC TANGENT     TANH(X)=EXP(-X)/EXP(X)+EXP(-X»*2+1
HYPERBOLIC SECANT      SECH(X)=2/(EXP(X)+EXP(-X»
HYPERBOLIC COSECANT    CSCH(X)=2/(EXP(X)-EXP(-X»
HYPERBOLIC COTANGENT   COTH(X)=EXP(-X)/(EXP(X)-EXP(-X»*2+1
INVERSE HYPERBOLIC
SINE                   ARCSINH(X)=LOG(X+SQR(X*X+1»
INVERSE HY~ERBOLIC
COSINE                 ARCCOSH(X)=LOG(X+SQR(X*X-1)
INVERSE HYPERBOLIC
TANGENT                ARCTANH(X)=LOG«1+X)/(1-X»/2
INVERSE HYPERBOLIC
SECANT                 ARCSECH(X)=LOG«SQR(-X*X+1)+1)/X)
INVERSE HYPERBOLIC
COSECANT               ARCCSCH(X)=LOG«SGN(X)*SQR(X*X+1)+1)/X
INVERSE HYPERBOLIC
COTANGENT              ARCCOTH(X)=LOG«X+1)/(X-l»/2
                                                       Page H-l
                            APPENDIX H
                    ASCII Character Codes
ASCII                 ASCII                 ASCII
Code    Character     Code      Character   Code    Character
000        NUL        043          +        086         V
001        SOH        044          ,        087         W
002        STX        045                   088         X
                                   /·
003        ETX        046                   089         Y
004        EOT        047                   090         Z
005        ENQ        048          0        091         {
006        ACK        049          1        092         \
007        BEL        050          2        093         ]
                                                        A
008        BS         051          3        094
009        HT         052          4        095         <
                                                        ~
010        LF         053          5        096
011        VT         054          6        097         a
012        FF         055          7        098         b
013        CR         056          8        099         c
014        50         057          9        100         d
                                   ·
                                   ·,·
015        SI         058                   101         e
016        DLE        059                   102        f
017        DC1        060          <        103        9
018        DC2        061          =        104        h
019        DC3        062          >        105        i
020        DC4        063          ?        106        j
021        NAK        064          @        107        k
022        SYN        065          A        108        1
023        ETB        066          B        109        m
024        CAN        067          C        110        n
025        EM         068          D        111         0
026        SUB        069          E        112        P
027        ESCAPE     070          F        113         q
028        FS         071          G        114         r
029        GS         072          H        115         s
030        R5         073          I        116         t
031        US         074          J        117         u
032        SPACE      075          K        118         v
033        !          076          L        119         w
           n
034                   077          M        120         x
035        t          078          N        121         Y
036        $          079          0        122         z
037        %          080          P        123         {
038        &          081          Q        124
039        ~
                      082          R        125         }
040        (          083          5        126
041        )          084          T        127         DEL
042        *          085          U
ASCII codes are in decimal.
LF=Line Feed, FF=Form Feed, CR=Carriage Return, DEL=Rubout
                                                                      Page I-I
                                                    INDEX
ABS    • •.               .   • • • • • • .   3-2
Addition •                • • • • • • • . 1-10
ALL    .   ..   • .   .   • .   • • .     . 2-4, 2-9
Arctangent • • ••       • • • • 3-3
Array variables • • • • • • • 1-7,                  2-9, 2-18
Arrays • • • • • • • • • • • • 1-7,                 2-7, 2-11, 2-24
Ase • • • • • • • • • • • • • 3-2
ASCII codes • • • • • • • • • 3-2,                  3-4
ASCII format • • • • • • • • • 2-4,                 2-49, 2-77
Assembly language subroutines 2-3,                  2-16, 2-59, 3-23 to 3-24,
                                C-1
ATN             .......   • • • 3-3
AUTO   .........                        • • 1-2, 2-2
Boolean operators                         • 1-12
CALL • • • • • • . . . . . . . 2-3, C-5
Carriage return . . . . . . . 1-3, 2-36, 2-41 to 2-42,
                                2-83 to 2-85
Cassette tape • • • • • • • • 2-7, 2-11
COBL • • • • ••      •• • • • 3-3
CHAIN • • • • • • • •       •• 2-4, 2-9
Character set • • • •       •• 1-3
CHR$ • • • • • • • • • • • • • 3-4
CINT • • • • • • • • • • • • • 3-4
CLEAR • • • • • • • • ••        2-6, A-l
CLOAO • • • • •       •• • • • 2-7
CLOAD* • • • • • . • • • • • • 2-7
CLOAD? • • • •          • • • • 2-7
CLOSE • • •      • • • •      • 2-8, B-3, B-8
Command level • • ••        •• 1-1
COMMON • • • • • • • • • • • • 2-4, 2-9
Concatenation • • • • • • • • 1-15
Constants      • • • • ••       1-4
CONT • • • • • • • • • • • • • 2-10, 2-41
Control characters • • • • • • 1-4.
Contro1-A • • • • • • • • • • 2-22
COS • • • • • • • • • • • • • 3-5
CP/M • • • • • • • • • • • • • 2-46, 2-49, 2-76 to 2-77,
                                B-1, 0";'1
CSAVE • • • • • • • • • • • • 2-11
CSAVE* • • • • • • • • • • • • 2-11
CSNG •     • • • •          • • 3-5
CVD  • ••      •• • • ••        3-6, B-8
CVI          • • • • • • • • • 3-6, B-8
CVS              • • • • • • • 3-6, B-8
                                                                         Page I-2
DATA
DEF FN·.·                                          2-12, 2-74
                                                   2-13
DEF OSR                                            2-~6, 3-23
DEFDBL •                                           1-7, 2~15
DEFINT
DEFSNG      ··   •
                                 •       •         1-7, 2-15
                                                   1-7, 2-15
DEFSTR
DEINT       ·                                    ·
                                                   1-7, 2-15
                                                   C-1.
DELETE
DIM         ·                            •
                                                   1-2, 2-4, 2-17
                                                   2-18
Direct mode                                        1-1, 2-34, 2-54
Division •                                         1-10
Double precision
                         ·                       • 1-5, 2-15, 2-60, 3-3, A-1,
EDIT
        ·
Edit mode
                                 • •
                                 • •
                                                     1-2, 2-19
                                                     1-4, 2-19
END                                                  2-8, 2-10, 2-23, 2-3/
EOF     • .. •     •                 •     3-6, B-3, B-5, D-4
ERASE        •   • •             •     •   2-24
ERL                              •       • 2-25
ERR            •                           2-25
ERROR                              • • •   2-26
Error codes      •                   •     1-16, 2-25 to 2-26
Error messages
Error trapping •
                   • ·           • •
                                     •     1-16
                                         • 2-25 to 2-26, 2-54, 2-75,
                                           B-7
Escape
EXP    •
         •  ·                    •   •
                                       •
                                         • 1-3, 2-19
                                           3-7
Exponentiation
Expressions          ·•            • •
                                   •
                                         • 1-10 to 1-11
                                           1-9
FIELD                                              2-28, B-8
FILES
FIX
                             •
                                 •
                                         •       · D-3
                                                   3-7
FOR ••• NEXT
                 ·                   •           • 2-29, A-1
FRCINT
FRE         ·                •               •
                                                 · C-1,
                                                   3-8
                                                        C-4, D-4
Functions                        •                   1-14, 2-13, 3-1
GET                                  • • • • 2-28, 2-31, B-8, D-4
GIVABF •                                 •       · C-1 to C-2
GOSUB                                            • 2-32
GOTO
        ·                •                   •       2-32 to 2-33
HEX$ •                                   •           3-8
Hexadecimal                                          1-5, 3-8
IF ••• GOTO                          •               2-34
IF ••• THEN                                          2-25, 2-34
IF ••• T.HEN ••• ELSE
                         ·                           2-34
Indirect mode • • • • • • • • 1-1                                   Fage I-3
INKEY$ •     . • • • • • • • • 3-9
INP     • .   • .   .   .   .   .   .   • • • . 3-9
INPUT     • • •                     • • • • • 2-10, 2-28, 2-36, A-2,
                                              B-9
INPUT$ •            .   . . . .         .   .   .   . 3-10
INPUTt • • • • •            •   •   •   • •     • . 8-.. 3
INPUTt • • • • •            •   •   •   ••          2-38
INSTR • • • • •             •   •   •   • •     • • 3-11
INT • • • • • •             •   •   •   • •     • • 3-7, 3-12
Integer •• • .                            •     •• 3-4, 3-7, 3-12
Inreaer division            •                   • • 1-10
Interrupts • • • • • • • • • • C-7
ISIS-II • • • • • • • • • • • 2-76
KILL ••                                         • • 2-39, B-2
LEFT$ • • • • •     • • • • • 3-12
LEN • • • • • • • • • • • • • 3-13
LET • • • • • • • • • • • • • 2-28, 2-40, B-9
Line feed      • • • • • • • • 1-2, 2-36, 2-41 to 2-42,
                                2-84 to 2-85
LINE INPUT     ••••         • • 2-41
LINE INPUTt • • • • • • • • • B-3
LINE INPUTt • • •      •• • • 2-42
Line numbers • • • • • • • • • 1-1 to 1-2, 2-2, 2-73
Line printer • • • • • • • • • 2-45, 2-47, 2-83, 3-14,
                                A-2
Lines      • • • • • •      •• 1-1
LIST • • • • • • • • • • • • • 1-2, 2-43
LLIST • • • • • • • • • • • • 2-45
LOAD • • • • • • • • • • • • • 2-46, 2-77, B-1
LOC • • • • • •      • • • • • 3-13, B-3, B-5, B-8
LOF • • • • • • •       • • • • D-4
LOG • • • • • • •       • • • • 3-1,*
Logical operators • • • • • • 1-12
Loops • • ••       • • • • • • 2-29, 2-82
LPOS • • • • • • • • • • • • • 2-83, 3-14
LPRINT • • • • • • • • • • • • 2-47, 2-83
LPRINT USING     .••        • • 2-47
LSET • • • • • • • ••       •• 2-48, B-8
MAKINT                      • • • • • • • C-1, C-4, D-4,
MBASIC                      • • • • • • • D-1
MERGE • • • • • •                           • • 2-4, 2-49, B-2
MID$ •      • • • •                         • • 2-50, 3-15
MKD$ • • • • • • •              •   •   • • • • 3-15, B-8
MKI$ • • • • • • •              •   •       •• 3-15, B-8
MKS$ •      ••• •               •   •   • • • • 3-15, B-8
MOD operator • • •              .   •       •• 1-11 .
Modulus arithmetic              •               1-11
Multiplication • •                      . . . • 1-10
                                                          Page I-4
NAME • •       ••   • • •   •
                            · 2-51
Negation . • . • • • • •    · 1-10
NEW          • • • . • •    • 2-8, 2-52
NULL • • • • • • • • • •    • 2-53
Numeric constants . • • · • • 1-4
Numeric variables • • •     • 1-7
OCT$ • • • ••        • • • • • • 3-16
Octal • • . .            . • • • 1-5" 3-16
ON ERROR GOTO        . •.       • 2-54
ON ••• GOSUB • • • • • ••       • 2-55
ON ••• GOTO • • • • • • ~ • • • 2-55
OPEN • . • •                    • 2-8, 2-28, 2-56, B-3,
                                  B-8
Operators     ·..·...           • 1-9, 1-11 to 1-13, 1-15
OPTION BASE      • • • • • • • 2-57
OUT      • • • • . • • • • • • 2-58
Overflow • • • • • • • ••      1-11, 3-7, 3-22, A-1,
Overlay                           • 2-4
Paper tape
PEEK
      ·     ·         ·  · · · · ·  · 2-53
             · · · · · · · · · · 2-59, 3-16
                                      2-59, 3-16
     ·· · · ·· ·· ·· ·· ·· · · · · ·· 2-83,
POKE
POS
       •  ·                                 3-17
PRINT
        · · · · · ·· · · · · ·· ·· 2-62, A-2
PRINT USING
                                      2-60, A-1
PRINTi USING • •    • • • • •  • • B-5
PRINTi USING • •    • •     • • • B-3
PRINTi • • • • •    • • • •      • B-3
PRINTi USING .            • •  . • 2-66
PRINTi • • • • •    • • • • •  • • 2-66
Protected files                  • 2-77, A-2, B-2
PUT • • • • •         • • • • • • 2-28, 2-68, B-8
Random files •                 • 2-28, 2-31, 2-39, 2-48,
                                 2-56, 2-68, 3-13, 3-15,
                                 B-7, D-4
Random numbers                 • 2-69, 3-18
RANDOMIZE ••            • • . • 2-69, 3-18, A-1
READ • ••      ••••         · • 2-70, 2-74
Relational operators      • . • 1-11
REM   • • ••     • • • • • • • 2-72
RE~UM      • • • • • • • • • • 2-4, 2-25, 2-73
RESET • • • • • • . • • • • • D-3
RESTORE • • •           • • • • 2-74
RESUME • • • • • • • • • • • • 2-75
RETURN • • • • • • • • • • • • 2-32
RIGHT$ • • • • •     • • • • • 3-17
RND • ••       .• •       • • • 2-69, 3-18, A-1
RSET •     •• • . • • ••        2-48, B-8
Rubout • • • • • • • • • • • • 1-3, 1-15, 2-20
RUN • • • • . • • • • • • • • 2-76 to 2-77, B-2
SAVE •                          • • 2-46, 2-76 to 2-77, B-1
                                                                          Page I-S
SBC • • • • • • • • •
Sequential files • • •
                                           ·· .. • • G-1
                                                     2-38 to 2-39, 2-42, 2-56,
                                                     2-66, 2-85, 3-6, 3-13,
                                                   B-3
SGN
S-IN
       •
       •
           •
           •
               •   •   •
               • • • • •
                           •   •   •
                                   • •
                                       •   ·· .. .. •• 3-18
                                                       3-19
Single precision •                          · . . . 1-5, 2-15, 2-60, 3-5, A-1
SPACES •     • • • • •                         • • 3-19
SPC    •   •   •   •   •   •   •   •   •   • • • • 3-20
SQR"   •   •   •   •   •   •   •   •   •   • • • • 3-20
STOP.      · . . . . . . . · . . • 2-10, 2-23, 2-32, 2-78,
STR$ •      • • • • • • • • • • 3-21
String constants •      • • • • 1-4
String functions •          • • 3-6, 3-11 to 3-13, 3-15,
                                3-17, 3-21, 3-23
String operators • • • • • • • 1-15
Str ing space • • • • • • • • • 2-6, 3-8, A-1, B-9
String variables • • • • • • • 1-7, 2-15, 2-41 to 2-42
STRING$ • • • • •       •• • • 3-21
Subroutines • • • • • • • • • 2-3, 2-32, 2-55, C-1
Subscripts • • • • • • • • • • 1-7, 2-18, 2-57
Subtraction • • • • • • • • • 1-10
SWAP • • • • • • • • • • • • • 2-79
SYSTEM • • • • • • • • • • • • 0-4
TAB
Tab
     ·· .. .. .. .. .. .. .. . • •• •• •• 1-3
                                          3-22
                                               to 1-4
TAN   · .......                  • • •             3-2~
TROFF • • • • • • • • · . . • 2-80
TRON • • • • • • • • • · . . • 2-80
OSR • • • • • • •      • • • • 2-16, 3-23, C-1
OSRLOC • • • • • • • · . . . . C-2
VAL  • • • • • • • • • • • • • 3-23
Variables          ·.·...  • • 1-6
VARPTR •• • • • • • • • • • • 3-24
WAIT •
           ·· ·· · ·• •• ·• ·· •• • ·• •• 2-81
             •
WEND •
WHILE
           • •
               · · · ·   · ·  ·  ·  ·•  · ·
                                             2-82
                                             2-82
WIDTH
            · · · ·• · • ·· · · ·· · 2-83, A-2
             •
WIDTH LPRINT •
                         •  •     •  •     • 2-83, A-2
WRITE •
WRITE# • •
           •
             •
               · · · •• ·• ·• ·• ·• ·• ·· •• B-3
                                             2-84
WRITE#     •· · · • • • · · · • · 2-85
```

## See Also

*Related statements will be linked here*
