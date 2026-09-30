# Example Programs

## Factorial Calculator

```basic
10 REM Factorial calculator
20 INPUT "Enter a number"; N
30 F = 1
40 FOR I = 1 TO N
50 F = F * I
60 NEXT I
70 PRINT "Factorial of"; N; "is"; F
80 END
```

## Prime Number Checker

```basic
10 INPUT "Enter a number"; N
20 IF N < 2 THEN PRINT "Not prime" : END
30 FOR I = 2 TO SQR(N)
40 IF N MOD I = 0 THEN PRINT "Not prime" : END
50 NEXT I
60 PRINT "Prime!"
70 END
```

## Fibonacci Sequence

```basic
10 INPUT "How many numbers"; N
20 A = 0
30 B = 1
40 FOR I = 1 TO N
50 PRINT A;
60 C = A + B
70 A = B
80 B = C
90 NEXT I
100 END
```

## Hardware Access (Compiler Only)

These features work in the compiler and generate real 8080/Z80 machine code:

```basic
10 REM Hardware access example - works in compiled code!
20 REM Memory operations
30 A = PEEK(100)          ' Read byte from memory address 100
40 POKE 100, 42           ' Write byte 42 to address 100
50 REM Port I/O
60 B = INP(255)           ' Read from I/O port 255
70 OUT 255, 1             ' Write 1 to I/O port 255
80 WAIT 255, 1            ' Wait until port 255 bit 0 is set
90 REM Machine language interface
100 ADDR = VARPTR(A)      ' Get address of variable A
110 RESULT = USR(16384)   ' Call machine code at address 16384
120 CALL 16384            ' Execute machine code routine
130 END
```

Compile this with:
```bash
cd test_compile
python3 test_compile.py hardware.bas
# Generates hardware.com - runs on 8080 or Z80 CP/M systems!
```
