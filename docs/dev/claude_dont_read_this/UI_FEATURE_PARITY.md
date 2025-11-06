# MBASIC UI Feature Parity Table

Comprehensive feature comparison across all MBASIC user interfaces (CLI, Curses, Tk, Web, Visual).

---

## Legend

- ✅ Implemented
- ❌ Not implemented
- ⚠️ Partial/Limited implementation
- 🔄 Planned/In development

---

## 1. FILE OPERATIONS

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| New Program | ✅ NEW | ✅ Ctrl+N | ✅ Ctrl+N | ✅ Ctrl+N | ✅ |
| Open/Load File | ✅ LOAD | ✅ Ctrl+O | ✅ Ctrl+O | ✅ Ctrl+O | ✅ |
| Save File | ✅ SAVE | ✅ Ctrl+S | ✅ Ctrl+S | ✅ Ctrl+S | ✅ |
| Save As | ❌ | ❌ | ✅ Ctrl+Shift+S | ✅ Custom name | ❌ |
| Recent Files | ❌ | ❌ | ✅ File menu | ⚠️ Browser storage | ❌ |
| Auto-Save | ❌ | ❌ | ⚠️ Configurable | ❌ | ❌ |
| Load from Examples | ❌ | ❌ | ❌ | ✅ File menu | ❌ |
| Load from Server | ❌ | ❌ | ❌ | ✅ File menu | ❌ |
| Clear Program | ✅ NEW | ✅ Ctrl+N | ✅ Ctrl+N | ✅ Ctrl+N | ✅ |
| Delete Line(s) | ✅ DELETE | ✅ Ctrl+D | ⚠️ Editor delete | ✅ | ✅ |
| Merge Files | ✅ MERGE | ❌ | ✅ cmd_merge() | ❌ | ❌ |
| Chain Files | ✅ CHAIN | ❌ | ❌ | ❌ | ❌ |

---

## 2. PROGRAM MANAGEMENT & EXECUTION

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Run Program | ✅ RUN | ✅ Ctrl+R | ✅ Ctrl+R | ✅ Ctrl+R | ✅ |
| Stop/Interrupt | ✅ Ctrl+C | ✅ Ctrl+X | ✅ Ctrl+Q | ✅ Ctrl+Q | ✅ |
| Continue Execution | ✅ CONT | ✅ Ctrl+G | ✅ Ctrl+G | ✅ Ctrl+G | ✅ |
| List Program | ✅ LIST | ✅ Ctrl+L | ✅ Display only | ✅ | ✅ |
| Edit Line | ✅ EDIT | ✅ In-place | ✅ In-place | ✅ In-place | ✅ In-place |
| Renumber Lines | ✅ RENUM | ✅ Ctrl+E | ✅ Ctrl+E dialog | ✅ Ctrl+E dialog | ✅ |
| Auto Line Numbering | ✅ AUTO | ✅ Auto-increment | ✅ Auto-increment | ⚠️ Limited | ✅ Auto-increment |

---

## 3. EDITING FEATURES

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Line-by-Line Editing | ✅ | ✅ | ✅ | ✅ | ✅ |
| In-Place Line Edit | ✅ EDIT | ✅ | ✅ | ✅ | ✅ |
| Multi-Line Editing | ❌ | ❌ | ✅ | ✅ | ⚠️ |
| Cut/Copy/Paste | ❌ | ❌ | ✅ Ctrl+X/C/V | ✅ Ctrl+C/V | ❌ |
| Select All | ❌ | ❌ | ✅ Ctrl+A | ✅ Ctrl+A | ❌ |
| Find Text | ❌ | ❌ | ⚠️ Not documented | ❌ | ❌ |
| Find & Replace | ❌ | ❌ | ⚠️ Not documented | ❌ | ❌ |
| Smart Insert Line | ❌ | ❌ | ✅ Ctrl+I | ❌ | ❌ |
| Sort Lines | ❌ | ❌ | ✅ | ✅ Sort button | ❌ |
| Syntax Checking | ❌ | ✅ Real-time | ✅ Real-time (100ms) | ✅ Real-time | ❌ |
| Context Menu | ❌ | ❌ | ✅ Right-click | ⚠️ Limited | ❌ |

---

## 4. DEBUGGING FEATURES

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Breakpoints | ❌ | ✅ Ctrl+B (●) | ✅ Ctrl+B or click | ✅ Ctrl+B or click | ❌ |
| Step Statement | ❌ | ✅ Ctrl+T | ✅ Ctrl+T | ✅ Ctrl+T | ❌ |
| Step Line | ❌ | ❌ | ✅ Ctrl+T labeled | ✅ | ❌ |
| Continue Execution | ✅ CONT | ✅ Ctrl+G | ✅ Ctrl+G | ✅ Ctrl+G | ✅ |
| Clear Breakpoints | ❌ | ✅ Ctrl+Shift+B | ✅ | ❌ | ❌ |
| Multi-Statement Debug | ❌ | ✅ Highlight per stmt | ✅ Yellow highlight | ✅ Status bar | ❌ |
| Current Line Highlight | ❌ | ✅ Status bar | ✅ Yellow background | ✅ Status bar | ❌ |

---

## 5. VARIABLES & STATE INSPECTION

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Variables Window | ❌ | ✅ Ctrl+W | ✅ Ctrl+V | ✅ Ctrl+V | ❌ |
| Watch Variables | ❌ | ✅ Sort/filter | ✅ Multiple sort modes | ✅ Sort by column | ❌ |
| Edit Variable Value | ❌ | ⚠️ Limited | ✅ Double-click | ✅ Double-click | ❌ |
| Variable Filtering | ❌ | ✅ Ctrl+F in vars | ✅ Search box | ✅ Search | ❌ |
| Variable Sorting | ❌ | ✅ Name/accessed/written/read/type | ✅ Multiple modes | ✅ By column | ❌ |
| Execution Stack | ❌ | ✅ Ctrl+K | ✅ Ctrl+K | ✅ Ctrl+K | ❌ |
| Resource Usage | ❌ | ⚠️ Limited | ✅ Memory/GOSUB/FOR/WHILE | ❌ | ❌ |
| Type Display | ❌ | ✅ (Suffix shown) | ✅ (String/Integer/Single/Double) | ✅ | ❌ |

---

## 6. USER INTERFACE & DISPLAY

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Terminal UI | ✅ Line-based | ✅ Full-screen | ❌ | ❌ | ❌ |
| GUI Windows | ❌ | ❌ | ✅ Tkinter | ✅ Browser | ⚠️ Stub |
| Menu Bar | ❌ | ✅ Ctrl+U | ✅ File/Edit/Run/View/Help | ✅ Menu buttons | ❌ |
| Toolbar | ❌ | ❌ | ✅ With buttons | ✅ Button toolbar | ❌ |
| Status Bar | ✅ | ✅ Bottom | ✅ | ✅ | ❌ |
| Output Window | ✅ Stdout | ✅ Bottom pane | ✅ Bottom pane | ✅ Bottom pane | ✅ |
| Editor Pane | ✅ | ✅ Top | ✅ Left side | ✅ Top | ✅ |
| Resizable Panes | ❌ | ❌ | ✅ Vertical/Horizontal split | ✅ Responsive | ❌ |
| Line Numbers | ⚠️ Implicit | ✅ Auto-format | ✅ Gutter display | ✅ Line display | ⚠️ |
| Color Syntax | ❌ | ⚠️ Limited colors | ✅ Keywords highlighted | ⚠️ Basic | ❌ |
| Dark/Light Theme | ❌ | ❌ | ❌ | ⚠️ Browser theme | ❌ |

---

## 7. KEYBOARD & INPUT HANDLING

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Ctrl+letter shortcuts | ✅ | ✅ All Ctrl+* | ✅ All Ctrl+* | ✅ All Ctrl+* | ❌ |
| Function Keys | ❌ Policy: NO | ❌ Policy: NO | ❌ Policy: NO | ❌ Policy: NO | ❌ |
| Alt+Key | ❌ | ❌ | ❌ | ❌ | ❌ |
| Configurable Keys | ❌ | ✅ curses_keybindings.json | ✅ tk_keybindings.json | ❌ Hardcoded | ❌ |
| INPUT Statement | ✅ Terminal | ✅ Output window | ✅ Input row popup | ✅ Input field | ✅ |
| LINE INPUT | ✅ | ✅ | ✅ | ✅ | ✅ |
| Screen Positioning | ❌ | ✅ Cursor control | ❌ | ❌ | ❌ |

---

## 8. HELP & DOCUMENTATION

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Help System | ✅ HELP command | ✅ Ctrl+H | ✅ F1/Ctrl+H | ✅ Menu button | ❌ |
| Integrated Docs | ✅ Language/MBASIC | ✅ Full markdown | ✅ Full markdown | ✅ Tabbed browser | ❌ |
| Keyword Help | ✅ HELP PRINT | ✅ Search | ✅ Search | ✅ Search | ❌ |
| Search Help | ✅ HELP SEARCH | ✅ Full text search | ✅ Full text search | ✅ Full text search | ❌ |
| Quick Reference | ❌ | ✅ Status bar | ✅ In help | ✅ In help | ❌ |
| About Dialog | ❌ | ❌ | ✅ Help→About | ✅ Help→About | ❌ |

---

## 9. IMMEDIATE MODE (Direct Commands)

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Immediate Execution | ✅ Direct mode | ⚠️ Limited | ✅ Command entry | ⚠️ Limited | ✅ |
| PRINT Expression | ✅ Direct | ⚠️ Limited | ✅ | ⚠️ | ✅ |
| Variable Inspection | ✅ Direct | ⚠️ Limited | ✅ | ⚠️ | ✅ |
| Quick Calculation | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |

---

## 10. SETTINGS & CONFIGURATION

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Settings Dialog | ❌ | ✅ Ctrl+P | ✅ Ctrl+P | ❌ | ❌ |
| Variable Case | ❌ | ⚠️ Config | ✅ Settings | ❌ | ❌ |
| Keyword Case | ❌ | ⚠️ Config | ✅ Settings | ❌ | ❌ |
| Tab Size | ❌ | ❌ | ⚠️ Config | ❌ | ❌ |
| Auto-Save Config | ❌ | ✅ Config file | ✅ settings.json | ❌ | ❌ |
| Theme Settings | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 11. ERROR HANDLING & DISPLAY

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Parse Errors | ✅ Display | ✅ ? indicator + list | ✅ ? in gutter + output | ✅ ? indicator | ✅ |
| Runtime Errors | ✅ Display | ✅ Display | ✅ Display | ✅ Display | ✅ |
| Error Line Numbers | ✅ | ✅ | ✅ | ✅ | ✅ |
| Error Messages | ✅ | ✅ | ✅ | ✅ | ✅ |
| Syntax Highlighting | ❌ | ✅ Real-time | ✅ Real-time | ✅ Real-time | ❌ |
| Error Popup | ❌ | ❌ | ✅ Dialog | ⚠️ In output | ❌ |

---

## 12. SPECIAL FEATURES BY UI

### CLI (Command Line Interface)
- ✅ Traditional BASIC REPL experience
- ✅ File operations (LOAD, SAVE, MERGE, CHAIN)
- ✅ Line management (DELETE, RENUM, EDIT, AUTO)
- ✅ Immediate mode expressions
- ✅ Help system with search
- ❌ No visual debugger
- ❌ No breakpoints
- ❌ No graphical output
- ⚠️ Limited to text I/O

### Curses (Terminal UI)
- ✅ Full-screen terminal interface
- ✅ Split editor/output panes
- ✅ Real-time syntax checking
- ✅ Breakpoints with ● indicator
- ✅ Step debugging (Ctrl+T)
- ✅ Variables window (Ctrl+W)
- ✅ Execution stack (Ctrl+K)
- ✅ Settings dialog (Ctrl+P)
- ✅ Help system with markdown
- ✅ Multi-statement statement highlighting
- ⚠️ No file dialogs (prompts instead)
- ❌ No mouse support
- ❌ No syntax highlighting (colors)

### Tk (Graphical UI)
- ✅ Full graphical interface (Tkinter)
- ✅ Menu bar with all operations
- ✅ Toolbar with quick buttons
- ✅ Line number gutter with click breakpoints
- ✅ Real-time syntax checking (100ms)
- ✅ Variables window with full sorting
- ✅ Execution stack window
- ✅ Smart Insert (Ctrl+I)
- ✅ Multi-statement statement highlighting (yellow)
- ✅ Recent files menu
- ✅ Auto-save capability
- ✅ Settings dialog (Ctrl+P)
- ✅ File dialogs (native)
- ✅ Context menus (right-click)
- ✅ Mouse support throughout
- ✅ Immediate mode command entry
- ❌ Find/Replace (not documented as implemented)
- ❌ Syntax highlighting colors

### Web (NiceGUI)
- ✅ Web-based interface (browser)
- ✅ Responsive design
- ✅ Editor and output panes
- ✅ Menu buttons
- ✅ Breakpoints (click line number)
- ✅ Step debugging (Ctrl+T)
- ✅ Variables window (Ctrl+V)
- ✅ Execution stack (Ctrl+K)
- ✅ Renumber dialog
- ✅ Recent files in localStorage
- ✅ Example programs
- ✅ Server file browser
- ⚠️ Session-based files only
- ⚠️ Limited persistence
- ❌ No debugger advanced features
- ❌ No find/replace
- ❌ No offline mode

### Visual (Stub)
- ⚠️ Template for custom UI
- ✅ Basic command structure
- ✅ Documentation for implementation
- ❌ No actual implementation
- ❌ No UI framework
- ❌ No features beyond template

---

## 13. RESOURCE MONITORING

| Feature | CLI | Curses | Tk | Web | Visual |
|---------|-----|--------|----|----|--------|
| Memory Usage | ❌ | ❌ | ✅ In vars window | ❌ | ❌ |
| GOSUB Depth | ❌ | ❌ | ✅ In vars window | ❌ | ❌ |
| FOR Loop Depth | ❌ | ❌ | ✅ In vars window | ❌ | ❌ |
| WHILE Depth | ❌ | ❌ | ✅ In vars window | ❌ | ❌ |
| Resource Limits Shown | ❌ | ❌ | ✅ Max values | ❌ | ❌ |

---

## 14. KEYBOARD SHORTCUT SUMMARY

### Common Shortcuts (All UIs)
- **Ctrl+N** - New Program
- **Ctrl+O** - Open/Load
- **Ctrl+S** - Save
- **Ctrl+R** - Run
- **Ctrl+Q** - Quit/Stop
- **Ctrl+B** - Toggle Breakpoint
- **Ctrl+T** - Step Statement
- **Ctrl+G** - Continue (Go)
- **Ctrl+V** - Variables Window
- **Ctrl+K** - Stack Window

### Curses-Only Shortcuts
- **Ctrl+H** - Help
- **Ctrl+U** - Menu
- **Ctrl+W** - Variables (alt to Ctrl+V)
- **Ctrl+L** - List (context-sensitive)
- **Ctrl+E** - Renumber
- **Ctrl+D** - Delete Line
- **Ctrl+I** - Insert Line
- **Ctrl+X** - Stop
- **Ctrl+Y** - Clear Output
- **Ctrl+P** - Settings

### Tk-Only Shortcuts
- **Ctrl+I** - Smart Insert
- **Ctrl+E** - Renumber
- **Ctrl+F** - Find
- **Ctrl+H** - Find & Replace
- **Ctrl+Shift+S** - Save As
- **F1** - Help (or Ctrl+H)
- **Mouse clicks** - Line breakpoints

### Web-Only Shortcuts
- All Ctrl+* shortcuts supported
- Sort button (no shortcut)
- Mouse clicks on line numbers

---

## 15. IMPLEMENTATION STATUS SUMMARY

### Mature & Fully Featured
- **Tk (Graphical)**: Comprehensive feature set, recommended for interactive use
- **Curses (Terminal)**: Full-screen terminal with most features
- **CLI**: Classic REPL, stable but limited

### Growing
- **Web (Browser)**: Modern interface, missing some advanced features
- **Visual (Stub)**: Template for custom implementations

### Architecture Quality
- All UIs inherit from `UIBackend` base class
- Pluggable architecture allows new backends
- Consistent keyboard binding system
- Shared help and resource management

---

## 16. FEATURE RANKING BY UI

### Best for Debugging
1. **Tk** - Yellow statement highlighting, real-time vars, full stack
2. **Curses** - Good debugging, terminal-native
3. **Web** - Basic debugging, browser-based
4. **CLI** - No debugging
5. **Visual** - Template only

### Best for Development
1. **Tk** - Smart Insert, Find, full editing
2. **Web** - Modern UI, responsive
3. **Curses** - Fast, efficient
4. **CLI** - Classic but limited
5. **Visual** - Not functional

### Best for Learning
1. **Tk** - Visual, comprehensive
2. **Web** - Accessible, examples included
3. **Curses** - Educational, shows internals
4. **CLI** - Pure BASIC experience
5. **Visual** - Not for learning

---

## Notes

- **CLI** uses InteractiveMode (legacy, works well)
- **Curses** requires urwid library (`pip install mbasic[curses]`)
- **Tk** built into Python, no extra dependencies
- **Web** requires nicegui (`pip install nicegui`)
- **Visual** is a reference implementation stub
- **No function keys** by policy (No F1-F12, use Ctrl combinations)
- **All UIs** support multi-statement lines with `:` separator and statement-level debugging

