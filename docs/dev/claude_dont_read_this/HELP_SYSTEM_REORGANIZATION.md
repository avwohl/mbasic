# Help System Three-Tier Reorganization

## Overview

Reorganize help documentation into three distinct, logically separated tiers:

1. **Language Reference** - BASIC-80 language documentation (universal)
2. **MBASIC Implementation** - This Python interpreter's features and behavior
3. **UI-Specific Documentation** - Per-backend interface help (cli, curses, tk, visual)

## Current Structure Problems

### Directory Layout Issues

```
docs/help/
├── common/                          # MIXED: implementation + UI-agnostic content
│   ├── getting-started.md          # Implementation-specific (about MBASIC)
│   ├── editor-commands.md          # UI-specific content (doesn't belong here)
│   ├── language.md                 # Duplicate of language/index.md
│   └── language/                   # Language reference (CORRECT)
│       ├── functions/              # 40 files
│       ├── statements/             # 63 files
│       └── appendices/             # 3 files
├── language/                        # ORPHANED: old structure?
│   └── functions/                  # 2 files (duplicates?)
└── ui/
    ├── cli/
    ├── curses/                     # UI-specific (CORRECT)
    └── tk/
```

### Conceptual Overlap

**Getting Started** (`common/getting-started.md`):
- Mixes: What is BASIC? (language) + How to enter programs (UI-specific)
- Should be split into language concepts vs UI tutorials

**Editor Commands** (`common/editor-commands.md`):
- Lists function keys and Ctrl shortcuts
- This is UI-specific, not common!

**Language.md** (`common/language.md`):
- Simplified language overview
- Duplicates content from `common/language/index.md`

### Integration Issues

Each backend hardcodes help root:
```python
# curses_ui.py
help_root = Path(__file__).parent.parent.parent / "docs" / "help"
help_widget = HelpWidget(str(help_root), "ui/curses/index.md")
```

**Problem**: Only shows one tree, doesn't integrate all three tiers.

## Proposed Three-Tier Structure

### Tier 1: Language Reference (Universal)

**Location**: `docs/help/language/`

**Content**: Pure BASIC-80 language documentation (already complete!)

```
docs/help/language/
├── index.md                    # Language reference landing page
├── operators.md                # Operators reference
├── functions/                  # 40 function references
│   ├── index.md
│   ├── abs.md
│   └── ...
├── statements/                 # 63 statement references
│   ├── index.md
│   ├── print.md
│   └── ...
└── appendices/                 # 3 appendices
    ├── index.md
    ├── error-codes.md
    ├── ascii-codes.md
    └── math-functions.md
```

**Characteristics**:
- No mention of Python, UIs, or implementation
- Pure BASIC-80 specification
- Same content shown in ALL backends
- Read-only reference material

**Sources**:
- MBASIC 5.21 manual (already extracted)
- Implementation notes (PEEK, INP, POKE, etc.)

### Tier 2: MBASIC Implementation Docs

**Location**: `docs/help/mbasic/`

**Content**: About THIS Python interpreter

```
docs/help/mbasic/
├── index.md                    # MBASIC interpreter overview
├── getting-started.md          # First steps with MBASIC
├── architecture.md             # Interpreter vs compiler architecture
├── features.md                 # What's implemented
├── differences.md              # Differences from MBASIC 5.21
├── compatibility.md            # Compatibility implementations (PEEK, etc.)
├── not-implemented.md          # What's not implemented (hardware, etc.)
├── file-formats.md             # .BAS files, encoding, line endings
├── optimizations.md            # Semantic analyzer and optimizations
├── examples/                   # Sample programs
│   ├── index.md
│   ├── hello-world.md
│   ├── loops.md
│   └── file-io.md
└── tutorial/                   # Learning BASIC with MBASIC
    ├── index.md
    ├── basics.md               # Variables, operators
    ├── control-flow.md         # IF, FOR, WHILE
    └── subroutines.md          # GOSUB, DEF FN
```

**Characteristics**:
- About the Python implementation
- Shared across ALL UIs
- Links to language reference
- Explains what works, what doesn't, why

**Examples**:
- "Getting Started with MBASIC" (vs "Getting Started with BASIC language")
- "File Format Support" (.BAS files, unsqueezing, etc.)
- "Compatibility Notes" (PEEK returns random, POKE is no-op)
- "Tutorial Programs" (working examples to run in MBASIC)

### Tier 3: UI-Specific Documentation

**Location**: `docs/help/ui/{backend}/`

**Content**: How to use each specific interface

```
docs/help/ui/cli/
├── index.md                    # CLI REPL overview
├── commands.md                 # Direct mode commands
├── editing.md                  # Line editing (AUTO, DELETE, EDIT, RENUM)
└── running.md                  # Running programs from CLI

docs/help/ui/curses/
├── index.md                    # Curses UI overview
├── keyboard-commands.md        # Ctrl+H, Ctrl+R, Ctrl+A, etc.
├── editing.md                  # Editor features
├── running.md                  # Running and debugging
├── debugger.md                 # Breakpoints, stepping, watch
├── files.md                    # Save/load in curses UI
└── quick-reference.md          # Keyboard shortcut cheat sheet

docs/help/ui/tk/
├── index.md                    # Tkinter GUI overview
├── menu-reference.md           # Menu commands
├── toolbar.md                  # Toolbar buttons
├── editor.md                   # Text editor features
├── debugger.md                 # Visual debugger
└── preferences.md              # Settings and configuration

docs/help/ui/visual/
├── index.md                    # Visual Studio Code integration
└── ...                         # (future)
```

**Characteristics**:
- Backend-specific keyboard shortcuts, menus, features
- How to accomplish tasks in THIS UI
- NO language reference (link to tier 1)
- NO implementation details (link to tier 2)

## Integration: Three-Context Help System

### Unified Help Browser

Each backend should integrate all three tiers into a unified help experience:

```
┌─────────────────────────────────────┐
│ MBASIC Help                         │
├─────────────────────────────────────┤
│ 📘 Curses UI Guide                  │  ← Tier 3: UI-specific
│   ├─ Getting Started                │
│   ├─ Keyboard Commands              │
│   ├─ Editing Programs                │
│   └─ Debugging                       │
│                                      │
│ 📗 MBASIC Interpreter                │  ← Tier 2: Implementation
│   ├─ About MBASIC                    │
│   ├─ Features & Compatibility        │
│   ├─ File Formats                    │
│   └─ Examples & Tutorials            │
│                                      │
│ 📕 BASIC-80 Language Reference       │  ← Tier 1: Language
│   ├─ Statements (63)                 │
│   ├─ Functions (40)                  │
│   ├─ Operators                       │
│   └─ Appendices                      │
└─────────────────────────────────────┘
```

### Implementation Changes

**Current**:
```python
# Each UI hardcodes one help root
help_widget = HelpWidget(str(help_root), "ui/curses/index.md")
```

**Proposed**:
```python
# Each UI provides three contexts
help_widget = HelpWidget(
    ui_docs="docs/help/ui/curses",
    mbasic_docs="docs/help/mbasic",
    language_docs="docs/help/language",
    initial_topic="index.md"  # From ui_docs
)
```

### HelpWidget Changes

**New class structure**:

```python
class HelpWidget(urwid.WidgetWrap):
    def __init__(self, ui_docs: str, mbasic_docs: str, language_docs: str,
                 initial_topic: str):
        """
        Three-tier help browser.

        Args:
            ui_docs: Path to UI-specific help (e.g., "docs/help/ui/curses")
            mbasic_docs: Path to MBASIC implementation docs
            language_docs: Path to BASIC-80 language reference
            initial_topic: Starting page (relative to ui_docs)
        """
        self.contexts = {
            'ui': Path(ui_docs),
            'mbasic': Path(mbasic_docs),
            'language': Path(language_docs)
        }
        self.current_context = 'ui'
        self.history = []

    def navigate(self, target: str):
        """
        Navigate to a help topic.

        Supports cross-context links:
        - "../../mbasic/getting-started.md"  # Relative path
        - "mbasic:getting-started.md"         # Explicit context
        - "language:functions/print.md"       # Explicit context
        - "files.md"                          # Current context
        """
        if ':' in target:
            # Explicit context: "language:functions/print.md"
            context, path = target.split(':', 1)
            full_path = self.contexts[context] / path
        elif target.startswith('../../'):
            # Cross-context relative path
            # Parse to determine context
            full_path = self._resolve_relative(target)
        else:
            # Current context
            full_path = self.contexts[self.current_context] / target

        self._load_and_display(full_path)
```

### Link Syntax

**Within same tier**:
```markdown
See: [PRINT statement](statements/print.md)
```

**Cross-tier (relative)**:
```markdown
See: [MBASIC Getting Started](../../mbasic/getting-started.md)
See: [PRINT statement](../../language/statements/print.md)
```

**Cross-tier (explicit context)**:
```markdown
See: [PRINT statement](language:statements/print.md)
See: [Compatibility Notes](mbasic:compatibility.md)
See: [Curses Keyboard Commands](ui:keyboard-commands.md)
```

## Migration Plan

### Phase 1: Reorganize Directory Structure

**Move language reference**:
```bash
# Already correct! Just rename
mv docs/help/common/language docs/help/language
```

**Create MBASIC docs**:
```bash
mkdir -p docs/help/mbasic/{examples,tutorial}

# Move implementation-specific content
mv docs/help/common/getting-started.md docs/help/mbasic/
mv docs/help/common/examples.md docs/help/mbasic/

# Create new files
touch docs/help/mbasic/index.md
touch docs/help/mbasic/features.md
touch docs/help/mbasic/compatibility.md
touch docs/help/mbasic/not-implemented.md
```

**Clean up UI-specific**:
```bash
# Remove UI-specific content from common/
rm docs/help/common/editor-commands.md  # Move to each UI
rm docs/help/common/shortcuts.md         # UI-specific

# Keep only the common index as a redirect
```

**Remove duplicates**:
```bash
# Remove old language/ directory (orphaned)
rm -rf docs/help/language/functions  # Already have common/language/functions
```

### Phase 2: Update HelpWidget

1. **Add multi-context support**
   - Accept three paths instead of one
   - Parse context prefixes in links
   - Maintain separate history per context

2. **Update link resolution**
   - Support `context:path` syntax
   - Handle cross-context relative paths
   - Update markdown renderer if needed

3. **Add context switcher UI** (optional)
   - Show current context in header
   - Allow quick jump between contexts

### Phase 3: Update Each Backend

**CLI** (`cli.py`):
```python
help_docs = HelpDocs(
    ui_docs="docs/help/ui/cli",
    mbasic_docs="docs/help/mbasic",
    language_docs="docs/help/language"
)
# CLI can print help to console or open in pager
```

**Curses** (`curses_ui.py`):
```python
help_widget = HelpWidget(
    ui_docs="docs/help/ui/curses",
    mbasic_docs="docs/help/mbasic",
    language_docs="docs/help/language",
    initial_topic="index.md"
)
```

**Tkinter** (`tk_ui.py`):
```python
help_browser = HelpBrowser(
    ui_docs="docs/help/ui/tk",
    mbasic_docs="docs/help/mbasic",
    language_docs="docs/help/language"
)
# Tk can use HTML browser or custom widget
```

### Phase 4: Update All Help Content

1. **Create MBASIC documentation**
   - Write index.md (overview of MBASIC)
   - Write features.md (what's implemented)
   - Write compatibility.md (PEEK, INP, etc.)
   - Move NOT_IMPLEMENTED.md to mbasic/not-implemented.md

2. **Update cross-references**
   - Update links in UI docs to reference other tiers
   - Update language docs to link to MBASIC docs (for impl notes)
   - Ensure consistent navigation

3. **Create UI-specific content**
   - Expand curses/ docs (already mostly done)
   - Create cli/ docs (commands, editing)
   - Create tk/ docs (menus, toolbar)

### Phase 5: Testing

1. **Test navigation**
   - Verify cross-tier links work
   - Test back button across contexts
   - Test all three tiers accessible

2. **Test each backend**
   - CLI shows all three tiers
   - Curses shows all three tiers
   - Tk shows all three tiers

3. **Verify content**
   - No broken links
   - No duplicate content
   - Clear separation of concerns

## Content Guidelines

### Language Reference (Tier 1)

**DO**:
- Document BASIC-80 language syntax
- Include MBASIC 5.21 manual content
- Note historical features (cassette, hardware)
- Provide examples of language features

**DON'T**:
- Mention Python, the interpreter, or implementation
- Describe UI-specific commands
- Explain file formats or program storage
- Include implementation-specific behavior

### MBASIC Implementation (Tier 2)

**DO**:
- Explain what's implemented in THIS interpreter
- Document file formats (.BAS, .LSQ, etc.)
- Explain compatibility implementations (PEEK)
- Note differences from original MBASIC 5.21
- Provide working example programs
- Link to language reference for syntax

**DON'T**:
- Duplicate language syntax documentation
- Include UI-specific keyboard shortcuts
- Describe backend-specific features
- Duplicate content from tier 1

### UI-Specific Docs (Tier 3)

**DO**:
- Document keyboard shortcuts for THIS UI
- Explain editor features
- Describe debugger usage
- Show menu/toolbar commands
- Provide UI-specific workflows

**DON'T**:
- Document BASIC language syntax
- Explain interpreter features (not UI-specific)
- Duplicate content from other tiers
- Include content for other UIs

## Benefits

### Clear Separation of Concerns

1. **Language reference** is universal, never changes
2. **MBASIC docs** are about the implementation, shared across UIs
3. **UI docs** are backend-specific, focused on interface

### Easier Maintenance

- Update language docs once, affects all UIs
- Update implementation docs once, affects all UIs
- Update UI docs independently per backend

### Better User Experience

- Users can jump directly to what they need
- Clear navigation between related topics
- No confusion about "which help is this?"

### Scalability

- Easy to add new UIs (just create ui/{backend}/)
- Easy to update language reference (one place)
- Easy to document new features (implementation tier)

### Web Deployment Ready

- **Already web-compatible**: All markdown files work on web as-is
- **No changes needed**: Standard markdown with relative links
- **MkDocs integration**: Add mkdocs.yml for professional website
- **GitHub Pages**: Free hosting with automatic deployment
- **Search**: Full-text search on web (via MkDocs)
- **Same content**: Single source for in-UI and web docs

See [HELP_SYSTEM_WEB_DEPLOYMENT.md](HELP_SYSTEM_WEB_DEPLOYMENT.md) for details.

## Open Questions

1. **Should we use explicit context syntax (`language:functions/print.md`) or relative paths (`../../language/functions/print.md`)?**
   - Explicit is clearer but less standard
   - Relative is standard markdown but harder to read

2. **Should HelpWidget show all three tiers in one index, or separate tabs/sections?**
   - Unified index is simpler
   - Separate sections is clearer organization

3. **Should we generate a combined index.md at runtime, or maintain separate indexes?**
   - Combined requires logic in HelpWidget
   - Separate requires more manual work

4. **How to handle search across all three tiers?**
   - Search all three, tag results by tier?
   - Search within current tier only?

## Next Steps

1. **Create design document** (this file)
2. **Discuss with user**: Get feedback on approach
3. **Prototype HelpWidget changes**: Test multi-context navigation
4. **Reorganize directory structure**: Move files to new locations
5. **Update one backend**: Test with curses UI first
6. **Create MBASIC tier content**: Write implementation docs
7. **Update remaining backends**: CLI, Tk
8. **Update all cross-references**: Fix links throughout

## See Also

- [HELP_MIGRATION_STATUS.md](HELP_MIGRATION_STATUS.md) - Language reference migration
- [HELP_INDEXING_OPTIONS.md](HELP_INDEXING_OPTIONS.md) - Future search capability
- [NOT_IMPLEMENTED.md](NOT_IMPLEMENTED.md) - Implementation status tracking
