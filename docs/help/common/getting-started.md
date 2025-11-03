# Getting Started with MBASIC

Learn the basics of BASIC programming!

## What is BASIC?

BASIC (Beginner's All-purpose Symbolic Instruction Code) is an easy-to-learn programming language. MBASIC 5.21 is compatible with MBASIC from the 1980s.

## Your First Program

Every BASIC program is made of numbered lines:

```basic
10 PRINT "Hello, World!"
20 END
```

- Line **10** prints text to the screen
- Line **20** ends the program
- Line numbers tell BASIC the order to run lines

## How to Enter Programs

See your UI-specific help for how to type programs:

- [Curses UI](../ui/curses/editing.md) - Terminal interface
- [Tkinter UI](../ui/tk/index.md) - Graphical interface
- [CLI](../ui/cli/index.md) - Command-line REPL

## Basic Concepts

### Line Numbers

- Every line starts with a number: `10`, `20`, `30`
- Numbers can be 1-65535
- Lines execute in numerical order
- Common practice: increment by 10 (leaves room to insert lines)

### Printing Output

```basic
10 PRINT "Hello"
20 PRINT 42
30 PRINT "The answer is"; 42
```

See: [PRINT statement](language/statements/print.md)

### Variables

```basic
10 A = 5
20 B = 10
30 PRINT "Sum is"; A + B
```

See: [Variables and Data Types](language/data-types.md)

### Getting Input

```basic
10 INPUT "Enter your name: ", N$
20 PRINT "Hello, "; N$
```

See: [INPUT statement](language/statements/input.md)

## Program Flow

### Loops

```basic
10 FOR I = 1 TO 10
20   PRINT I
30 NEXT I
```

See: [FOR-NEXT loops](language/statements/for-next.md)

### Conditionals

```basic
10 INPUT "Enter a number: ", N
20 IF N > 10 THEN PRINT "Big!" ELSE PRINT "Small"
```

See: [IF-THEN-ELSE](language/statements/if-then-else-if-goto.md)

## Next Steps

- [Hello World Example](examples/hello-world.md)
- [Loop Examples](examples/loops.md)
- [BASIC Language Reference](language/statements/index.md)
- [Your UI's Help](index.md) - Choose your interface
