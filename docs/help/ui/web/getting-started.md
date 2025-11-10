---
title: "Getting Started with Web UI"
description: "Quick start guide for the MBASIC Web UI interface"
category: web-ui
keywords: [web, browser, getting started, interface, quick start]
type: guide
---

# Getting Started with Web UI

Welcome to the MBASIC Web UI! This browser-based interface provides a BASIC programming environment accessible from any modern web browser.

## Launching the Web UI

### Starting the Server

From the command line:

```bash
mbasic --ui web
```

Then open your browser to: **http://localhost:8080**

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Interface Overview

The Web UI has a simple, vertical layout with these components from top to bottom:

### 1. Menu Bar

At the very top, three menus:

- **File** - New, Open, Save, Save As, Recent Files, Exit
- **Run** - Run Program, Stop, Step, Continue, List Program, Show Variables, Show Stack, Clear Output
- **Help** - Help Topics, About

### 2. Toolbar

Quick-access buttons below the menu bar for common operations:

- **Run** - Parse and execute the program (▶️ green button, {{kbd:run:web}})
- **Stop** - Stop running program (⏹️ red button, {{kbd:stop:web}})
- **Step** - Execute all statements on current line, then pause (⏭️ button, {{kbd:step_line:web}})
- **Stmt** - Execute one statement, then pause (↻ button, {{kbd:step:web}})
- **Cont** - Resume normal execution after stepping (▶️⏸️ button, {{kbd:continue:web}})

File operations (New, Open, Save, Save As) are available through the File menu.

### 3. Program Editor

**Large text area labeled "Program Editor"** - This is where you write your BASIC program.

**Key feature: Automatic line numbering**
- Type a statement and press Enter
- First line becomes: `10 <your statement>`
- Next line becomes: `20 <your statement>`
- Lines increment by 10 automatically

**Example:**
```
Type: PRINT "Hello"
Press Enter → becomes: 10 PRINT "Hello"

Type: END
Press Enter → becomes: 20 END
```

You can also type your own line numbers if you prefer:
```
Type: 100 PRINT "Custom number"
Press Enter → accepted as-is
```

### 4. Output

**Text area labeled "Output"** - Shows program results, error messages, and diagnostics.

- Read-only (you can't type here)
- Shows what your program prints
- Displays error messages if program fails
- Shows "Ready" when program completes

### 5. Input Area (appears when needed)

When your program uses `INPUT`, a blue row appears with:
- Prompt text (what the program is asking for)
- Input field (where you type your answer)
- Submit button (click or press Enter to send)

**Example:**
```basic
10 INPUT "Your name"; N$
```
When this runs, the blue input area appears with "Your name" as the prompt.

### 6. Command Area

**Small text area labeled "Command"** at the bottom with an **Execute** button.

Use this for immediate commands that **don't get added to your program**:

**Try these:**
```
Type: PRINT 2+2
Click Execute → Output shows: 4

Type: X=10: PRINT X*X
Click Execute → Output shows: 100
```

**Important:** The Command area does **NOT** auto-number. It executes immediately.

### 7. Status Bar

Bottom row shows:
- Current status (Ready, Running, Stopped, etc.)
- Version number (v1.0.xxx)

## Your First Program

Let's write a simple program:

### Step 1: Type in the Program Editor

Click in the **Program Editor** area (top) and type:

```
PRINT "Hello, World!"
```

Press **Enter**. It becomes:
```
10 PRINT "Hello, World!"
```

Type:
```
END
```

Press **Enter**. It becomes:
```
20 END
```

### Step 2: Run It

Click the green **Run** button (or use Run menu → Run Program).

### Step 3: See Output

The **Output** area shows:
```
Hello, World!
Ready
```

Congratulations! You've run your first program.

## Example: Interactive Input

Try a program that asks for input:

**In the Program Editor, type:**
```
INPUT "What's your name"; N$
PRINT "Hello, "; N$
INPUT "Enter your age"; A
PRINT "You are"; A; "years old"
END
```

**Remember:** Press Enter after each line, and line numbers are added automatically.

**Your program becomes:**
```basic
10 INPUT "What's your name"; N$
20 PRINT "Hello, "; N$
30 INPUT "Enter your age"; A
40 PRINT "You are"; A; "years old"
50 END
```

**Click Run**, then:
1. The blue input area appears with "What's your name" prompt
2. Type your name and press Enter
3. The program greets you
4. Input area appears again with "Enter your age" prompt
5. Type your age and press Enter
6. The program tells you your age

## File Operations

### Opening a File

1. Click **Open** button (or File → Open)
2. A dialog appears with a file picker
3. Click to select a .BAS or .TXT file from your computer
4. Click "Open" or just select it (depending on browser)
5. File contents load into the Program Editor

### Saving a File

**First time saving:**
1. Click **Save** button (or File → Save)
2. Browser download dialog appears
3. Enter a filename (default: `program.bas`)
4. File downloads to your Downloads folder

**Note:** The Web UI uses browser downloads for saving program files to your computer. Auto-save of program code to browser localStorage is planned for a future release. (Note: Your editor settings ARE already saved to localStorage - see [Settings](settings.md))

**Save As:**
- Use **Save As** to download with a different filename
- File → Save As opens browser save dialog

### Recent Files

File → Recent Files shows recently opened files (saved in localStorage, persists across browser sessions).

## Using the Command Area

The **Command** area is perfect for quick tests and calculations **without modifying your program**.

### Quick Math
```
Type in Command: PRINT 5 * 12
Click Execute
Output shows: 60
```

### Testing Variables
```
Type: X = 100
Click Execute

Type: PRINT X * 2
Click Execute
Output shows: 200
```

### Quick Loops
```
Type: FOR I=1 TO 5: PRINT I: NEXT I
Click Execute
Output shows: 1 2 3 4 5
```

**When to use Command vs Editor:**
- **Program Editor** - Write programs you want to save and run repeatedly
- **Command area** - Quick calculations, testing ideas, checking values

## Debugging Features

### Breakpoints

Set breakpoints to pause execution at specific lines:
1. Use **Run → Toggle Breakpoint** menu option
2. Enter the line number
3. Program will pause when reaching that line
4. Use **Run → Clear All Breakpoints** to remove all

### Step Execution

The Web UI provides two types of stepping:

**Step Statement** - Execute one statement at a time:
1. Click **Step Stmt** button
2. Program executes one statement and pauses
3. Click **Step Stmt** again for next statement
4. Useful for debugging complex lines with multiple statements

**Step Line** - Execute all statements on one line, then pause:
1. Click **Step Line** button
2. Program executes all statements on current line and pauses
3. Click **Step Line** again for next line
4. Faster than statement stepping for most debugging

**Example:**
```basic
10 PRINT "Step 1"
20 X=1: Y=2: PRINT X+Y
30 PRINT "Step 2"
40 END
```

**Using Step Stmt:**
- Click **Step Stmt** → Output shows "Step 1", pauses
- Click **Step Stmt** → X=1 executes, pauses (still on line 20)
- Click **Step Stmt** → Y=2 executes, pauses (still on line 20)
- Click **Step Stmt** → PRINT X+Y executes, shows "3", pauses at line 30

**Using Step Line:**
- Click **Step Line** → Output shows "Step 1", pauses at line 20
- Click **Step Line** → All three statements execute, shows "3", pauses at line 30
- Click **Step Line** → Output shows "Step 2", pauses at line 40

**Continue:** Click **Continue** to resume normal execution from any paused state

### Show Variables

While program is paused or after it runs:
- Click Run → Show Variables
- A popup shows all defined variables and their values

### Show Stack

See the current execution stack:
- Click Run → Show Stack
- Shows function/subroutine call stack

### List Program

Want to see your program with line numbers?
- Click Run → List Program
- Output area shows formatted program listing

## Browser Compatibility

The Web UI works with modern browsers:

**Recommended:**
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

**Required browser features:**
- JavaScript enabled
- Modern HTML5 support

## Tips and Tricks

1. **Auto-numbering:** Press Enter in Program Editor to get automatic line numbers
2. **Quick test:** Use Command area to test expressions without changing your program
3. **Clear output:** Run → Clear Output to empty the output area
4. **Save often:** Use File → Save to download your program regularly (auto-save of program code to localStorage is planned for a future release)
5. **Check errors:** Red error messages in output show what went wrong

## Common Issues

### Line numbers aren't being added

**Problem:** You're typing in the Command area (bottom), not the Program Editor (top).

**Solution:** Click in the large **Program Editor** area at the top.

### Can't stop a program

**Problem:** Infinite loop or program won't stop.

**Solution:** Click the red **Stop** button (or Run → Stop).

### Lost my program

**Problem:** Refreshed browser and program is gone.

**Solution:** Auto-save of program code to localStorage is planned for a future release. Currently, you need to manually save your programs using File → Save. Make sure to save your work regularly to avoid losing changes. (Note: Your editor settings are automatically saved to localStorage.)

### Input area not appearing

**Problem:** Program has `INPUT` but nothing happens.

**Solution:** Make sure program is running (click Run first). Input area appears when program needs input.

## Next Steps

Now that you know the basics:

- [Web UI Index](index.md) - Complete feature overview
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Quick reference
- [Debugging Guide](debugging.md) - Advanced debugging
- [Language Reference](../../common/language/index.md) - BASIC language syntax

## Getting Help

- Click Help → Help Topics to browse documentation
- See error messages in Output area
- Check the [Language Reference](../../common/language/index.md) for BASIC commands
- Visit [MBASIC documentation](../../mbasic/index.md) for implementation details
