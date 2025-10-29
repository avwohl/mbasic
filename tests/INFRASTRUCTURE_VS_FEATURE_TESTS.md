# Infrastructure Tests vs Feature Tests

## Infrastructure Tests
These test that the UI backend can be instantiated and has basic structure. They are NOT part of the 38 canonical features.

### All UIs
- **UI Creation** - Tests that the UI class exists and can be imported
- **Menu System** (GUI UIs only) - Tests that menu structure exists
- **Editor Area** (GUI UIs only) - Tests that text editing area exists

## Feature Tests (37 Features)
These test actual user-facing functionality from ALL_FEATURES_CANONICAL_NAMES.txt

### 1. FILE OPERATIONS (8 features)
1. New Program
2. Open/Load File
3. Save File
4. Save As
5. Recent Files
6. Auto-Save
7. Delete Lines
8. Merge Files

### 2. EXECUTION & CONTROL (6 features)
9. Run Program
10. Stop/Interrupt
11. Continue
12. List Program
13. Renumber
14. Auto Line Numbers

### 3. DEBUGGING (6 features)
15. Breakpoints
16. Step Statement
17. Step Line
18. Clear All Breakpoints
19. Multi-Statement Debug
20. Current Line Highlight

### 4. VARIABLE INSPECTION (6 features)
21. Variables Window
22. Edit Variable Value
23. Variable Filtering
24. Variable Sorting
25. Execution Stack
26. Resource Usage

### 5. EDITOR FEATURES (7 features)
27. Line Editing
28. Multi-Line Edit
29. Cut/Copy/Paste
30. Find/Replace
31. Smart Insert
32. Sort Lines
33. Syntax Checking

### 6. HELP SYSTEM (4 features)
34. Help Command
35. Integrated Docs
36. Search Help
37. Context Help

## Test Counts by UI

### CLI
- Infrastructure: 0
- Features: 16/37

### Curses
- Infrastructure: 5 (UI Creation, Input Handlers, Program Parsing, Run Program, pexpect Integration)
- Features: 37/37 (all features tested)

### Tkinter
- Infrastructure: 2 (UI Creation, Menu System)
- Features: 37/37 (all features tested)

### Web
- Infrastructure: 2 (UI Creation, Editor Area)
- Features: 23/37

## Total Test Count Breakdown

| UI | Infrastructure | Features | Total |
|----|---------------|----------|-------|
| CLI | 0 | 16 | 16 |
| Curses | 5 | 37 | 42 |
| Tkinter | 2 | 37 | 39 |
| Web | 2 | 23 | 25 |
| **TOTAL** | **9** | **113** | **122** |

**Note:** Infrastructure tests are necessary to verify the UI can launch, but only the 37 feature tests count toward "feature coverage".
