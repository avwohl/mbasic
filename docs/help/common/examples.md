# Example Programs

## Hello World

```
10 PRINT "Hello, World!"
20 END
```

For a detailed walkthrough of this example, see [Hello World Tutorial](examples/hello-world.md).

## Simple Loop

```
10 FOR I = 1 TO 10
20 PRINT I
30 NEXT I
40 END
```

[See detailed tutorial](examples/loops.md)

## User Input

```
10 INPUT "What is your name"; N$
20 PRINT "Hello, "; N$; "!"
30 END
```

## Guess the Number

```
10 REM Number guessing game
20 X = INT(RND * 100) + 1
30 TRIES = 0
40 PRINT "Guess a number between 1 and 100"
50 INPUT "Your guess"; G
60 TRIES = TRIES + 1
70 IF G = X THEN GOTO 120
80 IF G < X THEN PRINT "Too low!"
90 IF G > X THEN PRINT "Too high!"
100 GOTO 50
120 PRINT "Correct! You got it in"; TRIES; "tries!"
130 END
```

## Multiplication Table

```
10 REM Multiplication table
20 INPUT "Which table (1-12)"; N
30 FOR I = 1 TO 12
40 PRINT N; " x "; I; " = "; N * I
50 NEXT I
60 END
```

[Back to main help](index.md)
