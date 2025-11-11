# Help System Integration Per Client

**Question**: How do we layer the three separate areas (UI-specific, MBASIC implementation, Language reference) into one complete picture in each client?

**Answer**: Each client presents a **unified help index** that integrates all three tiers, but shows them as logically separated sections.

## The Complete Picture

### What Users See in Each Client

Every client shows **one integrated help system** with three clearly labeled sections:

```
┌─────────────────────────────────────────────┐
│  MBASIC Help                                │
├─────────────────────────────────────────────┤
│                                             │
│  📘 [This UI Name] Guide                    │  ← Tier 3 (UI-specific)
│     Getting Started                         │
│     Keyboard Commands                       │
│     Running Programs                        │
│     ...                                     │
│                                             │
│  📗 MBASIC Interpreter                      │  ← Tier 2 (Implementation)
│     Getting Started with MBASIC             │
│     Architecture                            │
│     Features & Compatibility                │
│     Examples                                │
│     ...                                     │
│                                             │
│  📕 BASIC-80 Language Reference             │  ← Tier 1 (Language)
│     Statements (63)                         │
│     Functions (40)                          │
│     Operators                               │
│     Appendices                              │
│     ...                                     │
│                                             │
└─────────────────────────────────────────────┘
```

**Key principle**: One help system, three sections, clearly labeled.

## Implementation Per Client

### CLI Client Integration

**Entry Point**: `python3 mbasic --help` or in-REPL `HELP`

**Implementation**:

```python
# cli.py

class CLIHelp:
    """CLI help system - integrates three tiers."""

    def __init__(self):
        self.help_root = Path(__file__).parent.parent / "docs" / "help"

        # Three tier paths
        self.ui_help = self.help_root / "ui" / "cli"
        self.mbasic_help = self.help_root / "mbasic"
        self.language_help = self.help_root / "language"

        # Build unified index
        self.index = self._build_unified_index()

    def _build_unified_index(self):
        """Build index combining all three tiers."""
        from utils.frontmatter_utils import build_search_index

        return {
            'ui': build_search_index(self.ui_help),
            'mbasic': build_search_index(self.mbasic_help),
            'language': build_search_index(self.language_help)
        }

    def show_main_help(self):
        """Show main help index."""
        print("""
MBASIC Help
===========

CLI Interface Help
------------------
  commands     - CLI commands (AUTO, LIST, RUN, etc.)
  editing      - Line editing in direct mode

MBASIC Interpreter
------------------
  intro        - Getting started with MBASIC
  architecture - How MBASIC works
  features     - What's implemented
  examples     - Example programs

BASIC-80 Language Reference
---------------------------
  statements   - All BASIC statements (63)
  functions    - All BASIC functions (40)
  operators    - Arithmetic, logical, relational operators
  appendices   - Error codes, ASCII table, math functions

Type "HELP <topic>" for specific help.
Type "HELP SEARCH <keyword>" to search all help.
        """)

    def show_topic(self, topic: str):
        """Show help for specific topic."""
        # Search across all three tiers
        results = self._search_all_tiers(topic)

        if len(results) == 1:
            # Exact match, show it
            self._display_help_file(results[0])
        elif len(results) > 1:
            # Multiple matches, show list
            self._show_topic_list(results)
        else:
            print(f"No help found for '{topic}'")
            print("Type 'HELP' to see all available topics.")

    def _search_all_tiers(self, query: str) -> List[Path]:
        """Search all three tiers for query."""
        from utils.frontmatter_utils import search_help

        results = []

        # Search each tier
        for tier_name, tier_index in self.index.items():
            matches = search_help(query, tier_index)
            for match in matches:
                # Convert relative path to absolute
                if tier_name == 'ui':
                    results.append(self.ui_help / match)
                elif tier_name == 'mbasic':
                    results.append(self.mbasic_help / match)
                elif tier_name == 'language':
                    results.append(self.language_help / match)

        return results

    def _display_help_file(self, file_path: Path):
        """Display help file content."""
        import frontmatter

        with open(file_path, 'r') as f:
            post = frontmatter.load(f)

        # Show title from front matter or filename
        title = post.metadata.get('title', file_path.stem.upper())
        print(f"\n{title}")
        print("=" * len(title))
        print()

        # Show content (could use markdown renderer or plain text)
        print(post.content)

        # Show related topics if any
        related = post.metadata.get('related', [])
        if related:
            print("\nSee Also:")
            for topic in related:
                print(f"  - {topic}")
```

**User Experience**:
```bash
$ python3 mbasic
MBASIC 5.21

Ok
HELP                          # Shows unified index
HELP PRINT                    # Finds language/statements/print.md
HELP commands                 # Finds ui/cli/commands.md
HELP architecture             # Finds mbasic/architecture.md
HELP SEARCH loop              # Searches all three tiers
```

### Curses Client Integration

**Entry Point**: Press `Ctrl+A` (already implemented)

**Implementation**:

```python
# curses_ui.py

def setup_help(self):
    """Set up integrated help system."""
    help_root = Path(__file__).parent.parent.parent / "docs" / "help"

    # Create HelpWidget with three contexts
    self.help_widget = HelpWidget(
        ui_docs=str(help_root / "ui" / "curses"),
        mbasic_docs=str(help_root / "mbasic"),
        language_docs=str(help_root / "language"),
        initial_topic="index.md"  # Start with unified index
    )

# help_widget.py

class HelpWidget(urwid.WidgetWrap):
    """Integrated help browser for three-tier help system."""

    def __init__(self, ui_docs: str, mbasic_docs: str, language_docs: str,
                 initial_topic: str = "index.md"):
        """
        Initialize help widget with three-tier integration.

        Args:
            ui_docs: Path to UI-specific help
            mbasic_docs: Path to MBASIC implementation help
            language_docs: Path to BASIC-80 language reference
            initial_topic: Starting page (relative to ui_docs)
        """
        self.contexts = {
            'ui': Path(ui_docs),
            'mbasic': Path(mbasic_docs),
            'language': Path(language_docs)
        }

        # Build search indexes for each tier
        from utils.frontmatter_utils import build_search_index
        self.indexes = {
            name: build_search_index(path)
            for name, path in self.contexts.items()
        }

        # Start with unified index from UI docs
        self.current_context = 'ui'
        self.current_file = self.contexts['ui'] / initial_topic
        self.history = []

        # ... rest of widget setup

    def load_unified_index(self):
        """
        Load or generate unified index page.

        Looks for ui/curses/index.md which should contain
        links to all three tiers.
        """
        index_file = self.contexts['ui'] / 'index.md'

        if index_file.exists():
            # Use existing index
            self.load_file(index_file)
        else:
            # Generate unified index on the fly
            self.show_generated_index()

    def show_generated_index(self):
        """Generate unified help index dynamically."""
        content = """
# MBASIC Help

## 📘 Curses UI Guide

Learn how to use the terminal interface:

- [Getting Started](getting-started.md)
- [Keyboard Commands](keyboard-commands.md)
- [Editing Programs](editing.md)
- [Running Programs](running.md)
- [Debugger](debugger.md)

## 📗 MBASIC Interpreter

About this BASIC interpreter:

- [Getting Started](../../mbasic/getting-started.md)
- [Architecture](../../mbasic/architecture.md)
- [Features](../../mbasic/features.md)
- [Examples](../../mbasic/examples/index.md)

## 📕 BASIC-80 Language Reference

Complete BASIC-80 documentation:

- [Statements](../../language/statements/index.md) - All 63 statements
- [Functions](../../language/functions/index.md) - All 40 functions
- [Operators](../../language/operators.md)
- [Appendices](../../language/appendices/index.md)

---

**Navigation**: Tab (next link) | Enter (follow) | U (back) | / (search) | ESC (close)
        """
        self.display_markdown(content)

    def navigate_to(self, link: str):
        """
        Navigate to a help topic (handles cross-tier links).

        Supports:
        - Relative links: "getting-started.md"
        - Cross-tier relative: "../../mbasic/features.md"
        - Explicit context: "mbasic:features.md" (future)
        """
        if ':' in link and not link.startswith('http'):
            # Explicit context syntax: "language:statements/print.md"
            context, path = link.split(':', 1)
            target = self.contexts[context] / path
            self.current_context = context
        elif link.startswith('..'):
            # Cross-tier relative link
            target = (self.current_file.parent / link).resolve()
            # Determine which context this falls under
            self.current_context = self._get_context_from_path(target)
        else:
            # Same-context relative link
            target = self.current_file.parent / link

        # Load the file
        self.history.append((self.current_context, self.current_file))
        self.current_file = target
        self.load_file(target)

    def _get_context_from_path(self, path: Path) -> str:
        """Determine which context a path belongs to."""
        path_str = str(path)
        for context, context_path in self.contexts.items():
            if str(context_path) in path_str:
                return context
        return self.current_context  # Default to current

    def search_all(self, query: str) -> List[Dict]:
        """
        Search across all three tiers.

        Returns list of results with context labels.
        """
        from utils.frontmatter_utils import search_help

        results = []

        for context, index in self.indexes.items():
            matches = search_help(query, index)
            for match_path in matches:
                # Get metadata
                full_path = self.contexts[context] / match_path
                post = frontmatter.load(full_path)

                results.append({
                    'context': context,
                    'path': match_path,
                    'full_path': full_path,
                    'title': post.metadata.get('title', ''),
                    'description': post.metadata.get('description', ''),
                    'type': post.metadata.get('type', '')
                })

        return results

    def show_search_results(self, results: List[Dict]):
        """Display search results with context labels."""
        if not results:
            self.show_message("No results found")
            return

        # Group by context
        by_context = {
            'ui': [],
            'mbasic': [],
            'language': []
        }

        for result in results:
            by_context[result['context']].append(result)

        # Format results
        content = "# Search Results\n\n"

        if by_context['language']:
            content += "## 📕 Language Reference\n\n"
            for r in by_context['language']:
                content += f"- [{r['title']}]({r['full_path']})"
                if r['description']:
                    content += f" - {r['description']}"
                content += "\n"
            content += "\n"

        if by_context['mbasic']:
            content += "## 📗 MBASIC Interpreter\n\n"
            for r in by_context['mbasic']:
                content += f"- [{r['title']}]({r['full_path']})"
                if r['description']:
                    content += f" - {r['description']}"
                content += "\n"
            content += "\n"

        if by_context['ui']:
            content += "## 📘 Curses UI\n\n"
            for r in by_context['ui']:
                content += f"- [{r['title']}]({r['full_path']})"
                if r['description']:
                    content += f" - {r['description']}"
                content += "\n"

        self.display_markdown(content)

    def keypress(self, size, key):
        """Handle keypresses."""
        if key == '/':
            # Show search dialog
            self.show_search_dialog()
            return None
        elif key == 'u' or key == 'U':
            # Go back
            if self.history:
                context, file_path = self.history.pop()
                self.current_context = context
                self.current_file = file_path
                self.load_file(file_path)
            return None
        # ... rest of keypress handling
```

**User Experience**:
1. Press `Ctrl+A` → Shows unified index (ui/curses/index.md)
2. See three clearly labeled sections
3. Navigate with Tab/Enter (same as before)
4. Cross-tier navigation is seamless (relative links work)
5. Press `/` → Search all three tiers at once
6. Results grouped by context (Language, MBASIC, UI)

### Tkinter Client Integration

**Entry Point**: Help menu or F1 key

**Implementation**:

```python
# tk_ui.py

class TkHelpBrowser(tk.Toplevel):
    """Integrated help browser for Tkinter UI."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("MBASIC Help")
        self.geometry("900x700")

        # Three-tier help paths
        help_root = Path(__file__).parent.parent.parent / "docs" / "help"
        self.contexts = {
            'ui': help_root / "ui" / "tk",
            'mbasic': help_root / "mbasic",
            'language': help_root / "language"
        }

        # Build indexes
        from utils.frontmatter_utils import build_search_index
        self.indexes = {
            name: build_search_index(path)
            for name, path in self.contexts.items()
        }

        # Create UI
        self._create_widgets()
        self.show_index()

    def _create_widgets(self):
        """Create help browser widgets."""
        # Top toolbar
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="← Back",
                  command=self.go_back).pack(side=tk.LEFT)

        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(toolbar, width=30)
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind('<Return>', lambda e: self.search())

        ttk.Button(toolbar, text="Search",
                  command=self.search).pack(side=tk.LEFT)

        # Main layout: sidebar + content
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left sidebar: Table of contents
        sidebar_frame = ttk.Frame(paned)
        paned.add(sidebar_frame, weight=1)

        ttk.Label(sidebar_frame, text="Contents",
                 font=('TkDefaultFont', 12, 'bold')).pack(pady=5)

        # Treeview for hierarchical TOC
        self.toc_tree = ttk.Treeview(sidebar_frame)
        self.toc_tree.pack(fill=tk.BOTH, expand=True)
        self.toc_tree.bind('<<TreeviewSelect>>', self.on_toc_select)

        # Right content area
        content_frame = ttk.Frame(paned)
        paned.add(content_frame, weight=3)

        # Text widget with scrollbar for help content
        scroll = ttk.Scrollbar(content_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.content_text = tk.Text(content_frame, wrap=tk.WORD,
                                    yscrollcommand=scroll.set)
        self.content_text.pack(fill=tk.BOTH, expand=True)
        scroll.config(command=self.content_text.yview)

        # Configure text tags for formatting
        self.content_text.tag_config('h1', font=('TkDefaultFont', 16, 'bold'))
        self.content_text.tag_config('h2', font=('TkDefaultFont', 14, 'bold'))
        self.content_text.tag_config('code', font=('Courier', 10))
        self.content_text.tag_config('link', foreground='blue', underline=True)
        self.content_text.tag_bind('link', '<Button-1>', self.on_link_click)

    def show_index(self):
        """Show unified help index."""
        # Populate TOC tree with three-tier structure
        self.toc_tree.delete(*self.toc_tree.get_children())

        # Tier 3: Tkinter UI
        ui_node = self.toc_tree.insert('', 'end', text='📘 Tkinter UI Guide')
        for file_info in self.indexes['ui']['files']:
            self.toc_tree.insert(ui_node, 'end',
                               text=file_info['title'],
                               values=('ui', file_info['path']))

        # Tier 2: MBASIC
        mbasic_node = self.toc_tree.insert('', 'end', text='📗 MBASIC Interpreter')
        for file_info in self.indexes['mbasic']['files']:
            self.toc_tree.insert(mbasic_node, 'end',
                               text=file_info['title'],
                               values=('mbasic', file_info['path']))

        # Tier 3: Language (with sub-nodes)
        lang_node = self.toc_tree.insert('', 'end', text='📕 BASIC-80 Language')

        # Group language docs by type
        statements_node = self.toc_tree.insert(lang_node, 'end',
                                              text='Statements (63)')
        functions_node = self.toc_tree.insert(lang_node, 'end',
                                             text='Functions (40)')

        for file_info in self.indexes['language']['files']:
            if file_info['type'] == 'statement':
                self.toc_tree.insert(statements_node, 'end',
                                   text=file_info['title'],
                                   values=('language', file_info['path']))
            elif file_info['type'] == 'function':
                self.toc_tree.insert(functions_node, 'end',
                                   text=file_info['title'],
                                   values=('language', file_info['path']))

        # Expand all
        self.toc_tree.item(ui_node, open=True)
        self.toc_tree.item(mbasic_node, open=True)
        self.toc_tree.item(lang_node, open=True)

        # Show welcome page
        self.show_welcome()

    def show_welcome(self):
        """Show welcome/index page."""
        content = """
MBASIC Help System
==================

Welcome to the MBASIC help system. Choose a topic from the left sidebar,
or use the search box above.

📘 Tkinter UI Guide
   Learn how to use the graphical interface

📗 MBASIC Interpreter
   About this BASIC interpreter

📕 BASIC-80 Language Reference
   Complete BASIC language documentation

Use the search box to find topics quickly.
        """
        self.display_content(content)

    def search(self):
        """Search across all three tiers."""
        query = self.search_entry.get()
        if not query:
            return

        from utils.frontmatter_utils import search_help

        results = []
        for context, index in self.indexes.items():
            matches = search_help(query, index)
            for match in matches:
                # Get file info
                for file_info in index['files']:
                    if file_info['path'] == match:
                        results.append({
                            'context': context,
                            **file_info
                        })

        self.show_search_results(results)
```

**User Experience**:
1. Click Help menu or press F1 → Help window opens
2. Left sidebar shows three-tier TOC (expandable tree)
3. Click any topic → Content loads on right
4. Search box at top searches all tiers
5. Results grouped by context
6. Professional GUI with proper formatting

### Web Deployment Integration

**Entry Point**: https://yoursite.github.io/mbasic/

**Implementation**: MkDocs configuration (already covered in HELP_SYSTEM_WEB_DEPLOYMENT.md)

```yaml
# mkdocs.yml

nav:
  - Home: README.md

  # Tier 2: MBASIC (First because most users start here)
  - User Guide:
    - Getting Started: docs/help/mbasic/getting-started.md
    - Architecture: docs/help/mbasic/architecture.md
    - Features: docs/help/mbasic/features.md
    - Examples: docs/help/mbasic/examples/index.md

  # Tier 1: Language Reference
  - Language Reference:
    - Overview: docs/help/language/index.md
    - Statements: docs/help/language/statements/index.md
    - Functions: docs/help/language/functions/index.md
    - Operators: docs/help/language/operators.md
    - Appendices: docs/help/language/appendices/index.md

  # Tier 3: UI Guides (Multiple)
  - UI Guides:
    - CLI: docs/help/ui/cli/index.md
    - Curses (Terminal): docs/help/ui/curses/index.md
    - Tkinter (GUI): docs/help/ui/tk/index.md
```

**User Experience**:
1. Visit website
2. Top navigation shows: User Guide | Language Reference | UI Guides
3. Sidebar shows full hierarchy
4. Search box searches all content
5. Mobile-friendly responsive design

## Unified Index Files

Each UI needs a unified index at `docs/help/ui/{backend}/index.md`:

### Template: ui/curses/index.md

```markdown
---
title: MBASIC Curses UI Help
type: guide
ui: curses
---

# MBASIC Curses UI Help

Welcome to the MBASIC terminal-based IDE.

## 📘 Curses UI Guide

How to use this interface:

- [Getting Started](getting-started.md) - First steps
- [Keyboard Commands](keyboard-commands.md) - All shortcuts
- [Editing Programs](editing.md) - Using the editor
- [Running Programs](running.md) - Execute and debug
- [Debugger](debugger.md) - Breakpoints and stepping
- [File Operations](files.md) - Save and load

## 📗 MBASIC Interpreter

About the BASIC interpreter:

- [Getting Started](../../mbasic/getting-started.md) - First BASIC program
- [Architecture](../../mbasic/architecture.md) - How it works
- [Features](../../mbasic/features.md) - What's implemented
- [Compatibility](../../mbasic/compatibility.md) - MBASIC 5.21 differences
- [Examples](../../mbasic/examples/index.md) - Sample programs

## 📕 BASIC-80 Language Reference

Complete BASIC language documentation:

- [Language Overview](../../language/index.md)
- [Statements](../../language/statements/index.md) - All 63 statements
- [Functions](../../language/functions/index.md) - All 40 functions
- [Operators](../../language/operators.md) - Arithmetic, logical, relational
- [Appendices](../../language/appendices/index.md) - Error codes, ASCII, etc.

---

**Help Navigation**: ↑/↓ scroll | Tab (next link) | Enter (follow) | U (back) | / (search) | ESC (close)
```

### Template: ui/cli/index.md

```markdown
---
title: MBASIC CLI Help
type: guide
ui: cli
---

# MBASIC CLI Help

Command-line interface for MBASIC.

## 📘 CLI Interface

How to use the CLI:

- [Commands](commands.md) - All CLI commands
- [Line Editing](editing.md) - AUTO, DELETE, EDIT, RENUM
- [Running Programs](running.md) - Direct and program mode

## 📗 MBASIC Interpreter

- [Getting Started](../../mbasic/getting-started.md)
- [Architecture](../../mbasic/architecture.md)
- [Features](../../mbasic/features.md)
- [Examples](../../mbasic/examples/index.md)

## 📕 BASIC-80 Language Reference

- [Statements](../../language/statements/index.md)
- [Functions](../../language/functions/index.md)
- [Operators](../../language/operators.md)

---

Type `HELP <topic>` for specific help.
```

### Template: ui/tk/index.md

```markdown
---
title: MBASIC Tkinter GUI Help
type: guide
ui: tk
---

# MBASIC Tkinter GUI Help

Graphical user interface for MBASIC.

## 📘 Tkinter GUI

Using the graphical interface:

- [Getting Started](getting-started.md)
- [Menu Reference](menu-reference.md) - All menu commands
- [Toolbar](toolbar.md) - Toolbar buttons
- [Editor](editor.md) - Text editor features
- [Visual Debugger](debugger.md) - Debugging tools

## 📗 MBASIC Interpreter

- [Getting Started](../../mbasic/getting-started.md)
- [Architecture](../../mbasic/architecture.md)
- [Features](../../mbasic/features.md)
- [Examples](../../mbasic/examples/index.md)

## 📕 BASIC-80 Language Reference

- [Statements](../../language/statements/index.md)
- [Functions](../../language/functions/index.md)
- [Operators](../../language/operators.md)

---

Press F1 for context-sensitive help.
```

## Summary: The Complete Picture

### Three Tiers, One Experience

```
┌────────────────────────────────────────────────────┐
│         User opens help in any client              │
└──────────────────┬─────────────────────────────────┘
                   │
                   ▼
       ┌───────────────────────┐
       │  Unified Help Index   │
       │  (ui/{client}/index.md)│
       └───────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    ┌───────┐ ┌────────┐ ┌──────────┐
    │Tier 3 │ │Tier 2  │ │ Tier 1   │
    │ UI    │ │MBASIC  │ │Language  │
    │Specific│ │  Impl │ │Reference │
    └───────┘ └────────┘ └──────────┘
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
       All seamlessly linked via
         relative markdown links
```

### Key Integration Points

1. **Entry**: Each client shows unified index first
2. **Navigation**: Relative links work across tiers
3. **Search**: Searches all three tiers, groups results
4. **Context**: Users always know which tier they're in (icons/labels)
5. **Consistency**: Same structure in every client

### What Makes It Work

✅ **Relative links**: `../../language/statements/print.md` works everywhere
✅ **Front matter**: Metadata enables smart search and navigation
✅ **Index files**: Each tier has index.md, each UI has unified index
✅ **Clear labeling**: 📘 📗 📕 icons distinguish tiers visually
✅ **Search integration**: Single search across all content

The three separate areas are **always presented together**, making it feel like one cohesive help system while maintaining logical separation.
