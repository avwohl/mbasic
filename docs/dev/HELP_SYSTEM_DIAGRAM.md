# Help System Architecture Diagram

## Three-Tier Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MBASIC Help System                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ┌───────────┐
                                    │   User    │
                                    └─────┬─────┘
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                    ┌─────────┐      ┌─────────┐      ┌─────────┐
                    │   CLI   │      │ Curses  │      │   Tk    │
                    │   UI    │      │   UI    │      │   UI    │
                    └────┬────┘      └────┬────┘      └────┬────┘
                         │                │                │
                         └────────────────┼────────────────┘
                                          ▼
                              ┌───────────────────────┐
                              │    HelpWidget/        │
                              │    HelpBrowser        │
                              │  (Multi-Context)      │
                              └───────────────────────┘
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                   ┌──────────┐    ┌───────────┐    ┌──────────┐
                   │  Tier 3  │    │  Tier 2   │    │  Tier 1  │
                   │    UI    │    │  MBASIC   │    │ Language │
                   │ Specific │    │   Impl    │    │   Ref    │
                   └──────────┘    └───────────┘    └──────────┘
```

## Directory Structure

```
docs/help/
│
├── ui/                          # TIER 3: UI-Specific Documentation
│   ├── cli/
│   │   ├── index.md            # CLI overview
│   │   ├── commands.md         # Direct mode commands
│   │   ├── editing.md          # AUTO, DELETE, EDIT, RENUM
│   │   └── running.md          # Running programs
│   │
│   ├── curses/
│   │   ├── index.md            # Curses UI overview
│   │   ├── keyboard-commands.md  # Ctrl+H, Ctrl+R, Ctrl+A, etc.
│   │   ├── editing.md          # Editor features
│   │   ├── running.md          # Running programs
│   │   ├── debugger.md         # Breakpoints, stepping, watch
│   │   ├── files.md            # Save/load
│   │   └── quick-reference.md  # Cheat sheet
│   │
│   └── tk/
│       ├── index.md            # Tk GUI overview
│       ├── menu-reference.md   # Menu commands
│       ├── toolbar.md          # Toolbar buttons
│       └── editor.md           # Editor features
│
├── mbasic/                      # TIER 2: MBASIC Implementation
│   ├── index.md                # MBASIC interpreter overview
│   ├── getting-started.md      # First steps with MBASIC
│   ├── features.md             # What's implemented
│   ├── compatibility.md        # Compatibility implementations
│   ├── not-implemented.md      # What's not implemented
│   ├── file-formats.md         # .BAS files, encoding
│   ├── examples/
│   │   ├── index.md
│   │   ├── hello-world.md
│   │   └── loops.md
│   └── tutorial/
│       ├── index.md
│       ├── basics.md           # Variables, operators
│       └── control-flow.md     # IF, FOR, WHILE
│
└── language/                    # TIER 1: BASIC-80 Language Reference
    ├── index.md                # Language reference landing
    ├── operators.md            # Operators reference
    ├── functions/
    │   ├── index.md            # Functions index (40 functions)
    │   ├── abs.md
    │   ├── atn.md
    │   └── ...
    ├── statements/
    │   ├── index.md            # Statements index (63 statements)
    │   ├── print.md
    │   ├── for-next.md
    │   └── ...
    └── appendices/
        ├── index.md
        ├── error-codes.md      # 68 error codes
        ├── ascii-codes.md      # ASCII table
        └── math-functions.md   # Derived math functions
```

## Content Flow Example: User Searches for PRINT

### Scenario: User in Curses UI presses Ctrl+A, types "PRINT"

```
1. User Interface Layer
   ┌─────────────────────────────┐
   │  Curses UI                  │
   │  User presses Ctrl+A        │
   └──────────┬──────────────────┘
              │
              ▼
2. Help Widget
   ┌─────────────────────────────┐
   │  HelpWidget initialized:    │
   │  - ui: docs/help/ui/curses  │
   │  - mbasic: docs/help/mbasic │
   │  - language: docs/help/lang │
   └──────────┬──────────────────┘
              │
              ▼
3. Context Resolution
   ┌─────────────────────────────┐
   │  User navigates:            │
   │  1. See UI index            │◄──── ui:index.md
   │  2. Click "Language Ref"    │
   │  3. Click "Statements"      │
   │  4. Click "PRINT"           │◄──── language:statements/print.md
   └──────────┬──────────────────┘
              │
              ▼
4. Display
   ┌─────────────────────────────────────────────────────┐
   │  # PRINT                                            │
   │                                                     │
   │  ## Syntax                                          │
   │  PRINT [expression] [;|,] ...                       │
   │                                                     │
   │  ## Purpose                                         │
   │  Outputs data to the screen.                        │
   │                                                     │
   │  ## See Also                                        │
   │  - [INPUT](input.md)                  ◄──── Same tier
   │  - [PRINT USING](print-using.md)      ◄──── Same tier
   │  - [Implementation Notes](../../mbasic/features.md)  ◄──── Cross-tier
   └─────────────────────────────────────────────────────┘
```

## Cross-Tier Navigation Example

### From UI Docs → Language Reference

**File**: `docs/help/ui/curses/editing.md`
```markdown
## Editing Programs

Type BASIC code line by line. Each line starts with a line number.

For BASIC language syntax, see the [Language Reference](../../language/index.md).

Common statements:
- [PRINT](../../language/statements/print.md) - Output text
- [INPUT](../../language/statements/input.md) - Get user input
- [FOR-NEXT](../../language/statements/for-next.md) - Loops
```

### From Language Reference → MBASIC Implementation

**File**: `docs/help/language/functions/peek.md`
```markdown
# PEEK

## Implementation Note

ℹ️ **Compatibility Implementation**: PEEK returns a random value between 0-255.

See [MBASIC Compatibility Notes](../../mbasic/compatibility.md) for details.

**Historical Reference**: The documentation below is preserved from the
original MBASIC 5.21 manual.

---

## Syntax
...
```

### From MBASIC Docs → UI Documentation

**File**: `docs/help/mbasic/getting-started.md`
```markdown
# Getting Started with MBASIC

## Choose Your Interface

MBASIC supports multiple user interfaces:

- [CLI Interface](../ui/cli/index.md) - Command-line REPL
- [Curses Interface](../ui/curses/index.md) - Terminal-based IDE
- [Tk Interface](../ui/tk/index.md) - Graphical IDE

## Your First Program

For language basics, see [BASIC-80 Language Tutorial](tutorial/basics.md).

For how to enter and run programs, see your UI's documentation.
```

## Link Resolution Logic

```python
class HelpWidget:
    def navigate(self, target: str):
        """
        Link resolution:

        1. Explicit context:
           "language:statements/print.md"
           → docs/help/language/statements/print.md

        2. Relative path (same tier):
           "print.md"
           → docs/help/{current_context}/print.md

        3. Cross-tier relative:
           "../../mbasic/features.md"
           → Parse ../ to determine context

        4. Absolute path (avoid):
           "/help/language/statements/print.md"
        """
```

## Help Index Structure Per Backend

### Curses UI Help (Entry Point: ui/curses/index.md)

```markdown
# MBASIC Curses UI Help

## 📘 Curses UI Guide
- [Getting Started](getting-started.md)              # Tier 3
- [Keyboard Commands](keyboard-commands.md)          # Tier 3
- [Editing Programs](editing.md)                     # Tier 3
- [Running and Debugging](running.md)                # Tier 3

## 📗 MBASIC Interpreter
- [About MBASIC](../../mbasic/index.md)              # Tier 2
- [Features](../../mbasic/features.md)               # Tier 2
- [Examples](../../mbasic/examples/index.md)         # Tier 2
- [Tutorial](../../mbasic/tutorial/index.md)         # Tier 2

## 📕 BASIC-80 Language Reference
- [Language Overview](../../language/index.md)       # Tier 1
- [Statements](../../language/statements/index.md)   # Tier 1
- [Functions](../../language/functions/index.md)     # Tier 1
- [Appendices](../../language/appendices/index.md)   # Tier 1
```

### CLI Help (Entry Point: ui/cli/index.md)

```markdown
# MBASIC CLI Help

## 📘 CLI Interface Guide
- [Getting Started](getting-started.md)              # Tier 3
- [Commands](commands.md)                            # Tier 3
- [Line Editing](editing.md)                         # Tier 3

## 📗 MBASIC Interpreter
- [About MBASIC](../../mbasic/index.md)              # Tier 2
- [Features](../../mbasic/features.md)               # Tier 2

## 📕 BASIC-80 Language Reference
- [Language Overview](../../language/index.md)       # Tier 1
- [Statements](../../language/statements/index.md)   # Tier 1
- [Functions](../../language/functions/index.md)     # Tier 1
```

### Tk UI Help (Entry Point: ui/tk/index.md)

```markdown
# MBASIC Tkinter GUI Help

## 📘 Tkinter GUI Guide
- [Getting Started](getting-started.md)              # Tier 3
- [Menu Reference](menu-reference.md)                # Tier 3
- [Toolbar](toolbar.md)                              # Tier 3
- [Visual Debugger](debugger.md)                     # Tier 3

## 📗 MBASIC Interpreter
- [About MBASIC](../../mbasic/index.md)              # Tier 2
- [Features](../../mbasic/features.md)               # Tier 2

## 📕 BASIC-80 Language Reference
- [Language Overview](../../language/index.md)       # Tier 1
- [Statements](../../language/statements/index.md)   # Tier 1
- [Functions](../../language/functions/index.md)     # Tier 1
```

## Implementation Pseudocode

```python
class HelpWidget:
    """Multi-context help browser."""

    def __init__(self, ui_docs: str, mbasic_docs: str, language_docs: str,
                 initial_topic: str = "index.md"):
        self.contexts = {
            'ui': Path(ui_docs),
            'mbasic': Path(mbasic_docs),
            'language': Path(language_docs)
        }
        self.current_context = 'ui'
        self.current_path = self.contexts['ui'] / initial_topic
        self.history = []

    def navigate_to(self, link: str):
        """Navigate to a help topic."""
        # Determine target context and path
        if ':' in link:
            # Explicit: "language:statements/print.md"
            context, rel_path = link.split(':', 1)
            target = self.contexts[context] / rel_path
        elif link.startswith('../'):
            # Relative: "../../mbasic/features.md"
            target = self.current_path.parent / link
            target = target.resolve()
            # Determine context from resolved path
            context = self._get_context_from_path(target)
        else:
            # Same context: "editing.md"
            target = self.current_path.parent / link
            context = self.current_context

        # Load and display
        self.current_path = target
        self.current_context = context
        self.history.append((context, target))
        self._load_and_display(target)

    def go_back(self):
        """Navigate back in history."""
        if len(self.history) > 1:
            self.history.pop()  # Remove current
            context, path = self.history[-1]
            self.current_context = context
            self.current_path = path
            self._load_and_display(path)
```

## Benefits Visualization

```
┌───────────────────────────────────────────────────────────────┐
│  BEFORE: Single Context                                       │
├───────────────────────────────────────────────────────────────┤
│  docs/help/ui/curses/index.md                                 │
│    ├─ UI-specific content                                     │
│    ├─ Implementation details (mixed)                          │
│    └─ Language reference (mixed)                              │
│                                                                │
│  Problems:                                                     │
│  ❌ Duplicated content across UIs                             │
│  ❌ Hard to maintain consistency                              │
│  ❌ Unclear what's UI vs language vs implementation           │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│  AFTER: Three-Tier Structure                                  │
├───────────────────────────────────────────────────────────────┤
│  Tier 1: Language Reference (Universal)                       │
│    ✅ One source of truth for BASIC-80                        │
│    ✅ Shared across ALL UIs                                   │
│    ✅ Never duplicated                                        │
│                                                                │
│  Tier 2: MBASIC Implementation (Shared)                       │
│    ✅ One place for implementation docs                       │
│    ✅ Shared across ALL UIs                                   │
│    ✅ Clear separation from language spec                     │
│                                                                │
│  Tier 3: UI-Specific (Per Backend)                            │
│    ✅ Each UI maintains own docs                              │
│    ✅ No cross-contamination                                  │
│    ✅ Easy to add new UIs                                     │
└───────────────────────────────────────────────────────────────┘
```

## Summary

The three-tier help system provides:

1. **Clear organization**: Language, implementation, and UI separated
2. **No duplication**: Each piece of content has exactly one home
3. **Easy navigation**: Cross-tier links connect related topics
4. **Maintainability**: Update once, affects all UIs appropriately
5. **Scalability**: Easy to add new UIs or update existing ones
6. **User clarity**: Users know which help they're reading

Each tier serves a distinct purpose and audience, with clear boundaries and well-defined relationships.
