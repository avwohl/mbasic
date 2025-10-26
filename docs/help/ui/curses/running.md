---
description: NEEDS_DESCRIPTION
keywords:
- NEEDS_KEYWORDS
title: Running Programs in Curses UI
type: guide
---

# Running Programs in Curses UI

How to execute your BASIC programs.

## Running a Program

1. Press **F2** or **Ctrl+R**
2. Program executes in the output window
3. Output appears below the editor

### Example

```basic
10 PRINT "Hello, World!"
20 END
```

Press **F2** → Output window shows:
```
Hello, World!
```

## Output Window

The bottom part of the screen shows program output:

- Program output (PRINT statements)
- Runtime errors
- INPUT prompts

## Interactive Programs

Programs can prompt for input:

```basic
10 INPUT "Enter your name: ", N$
20 PRINT "Hello, "; N$
30 END
```

When run:
1. Prompt appears in output window
2. Type your response
3. Press **Enter**
4. Program continues

## Stopping a Program

Programs normally run until:
- END statement
- Last line reached
- STOP statement
- Runtime error

**Note**: Currently no way to interrupt running programs (use Ctrl+C to exit entirely).

## Listing Programs

Press **F3** or **Ctrl+L** to list the program to the output window.

This shows all program lines with line numbers.

## Clearing Output

Output window clears automatically when you:
- Run a new program
- Load a new program

## Common Issues

### "Syntax Error"

Check your BASIC syntax:
- Line numbers must be first
- Commands must be valid BASIC keywords
- Strings need quotes

See: [BASIC Language Reference](../../language/statements/index.md)

### "Runtime Error"

Program has a logic error:
- Division by zero
- Invalid GOTO target
- Type mismatch

Error message shows line number where error occurred.

### No Output

Check if:
- Program has PRINT statements
- Program reached those statements
- Program didn't hit an error first

## See Also

- [Editing Programs](editing.md) - Write code
- [Keyboard Commands](keyboard-commands.md) - All shortcuts
- [BASIC Statements](../../language/statements/index.md) - Language reference