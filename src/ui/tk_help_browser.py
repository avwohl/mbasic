"""
Tkinter-based help browser for navigating markdown documentation.

Provides:
- Scrollable help content display with markdown rendering
- Clickable links with navigation history (back button and home button)
- Search across multi-tier help system with ranking and fuzzy matching
- Search result display with tier markers (Language/MBASIC/UI)
- In-page search (Ctrl+F) with match highlighting and navigation
- Context menu with copy operations and 'Open in New Window' for links
- Table formatting for markdown tables
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import json
import re
from .help_macros import HelpMacros


class TkHelpBrowser(tk.Toplevel):
    """Tkinter window for browsing help documentation."""

    def __init__(self, parent, help_root: str, initial_topic: str = "index.md"):
        """
        Initialize help browser window.

        Args:
            parent: Parent Tk widget
            help_root: Path to help documentation root (e.g., "docs/help")
            initial_topic: Initial topic to display (relative to help_root)
        """
        super().__init__(parent)

        self.title("MBASIC Help")
        self.geometry("900x700")

        self.help_root = Path(help_root)
        self.current_topic = initial_topic
        self.history = []  # Stack of previous topics
        self.macros = HelpMacros('tk', help_root)
        self.link_counter = 0  # Counter for unique link tags
        self.link_urls = {}  # Map link tags to URLs

        # Search state
        self.search_indexes = self._load_search_indexes()

        # In-page search state
        self.inpage_search_visible = False
        self.inpage_search_query = ""
        self.inpage_search_matches = []  # List of (start, end) positions
        self.inpage_search_current = -1  # Current match index

        # Create UI
        self._create_widgets()

        # Load initial topic
        self._load_topic(initial_topic)

        # Focus on window
        self.focus()

    def _create_widgets(self):
        """Create all widgets for the help browser."""

        # Toolbar frame
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Back button
        self.back_button = ttk.Button(toolbar, text="← Back", command=self._go_back, width=10)
        self.back_button.pack(side=tk.LEFT, padx=2)
        self.back_button.config(state=tk.DISABLED)

        # Home button
        ttk.Button(toolbar, text="⌂ Home", command=self._go_home, width=10).pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Search frame
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(toolbar, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind('<Return>', lambda e: self._execute_search())

        ttk.Button(toolbar, text="🔍 Search", command=self._execute_search, width=10).pack(side=tk.LEFT, padx=2)

        # In-page search bar (hidden by default)
        self.inpage_search_bar = ttk.Frame(self)

        ttk.Label(self.inpage_search_bar, text="Find in page:").pack(side=tk.LEFT, padx=5)

        self.inpage_search_entry = ttk.Entry(self.inpage_search_bar, width=30)
        self.inpage_search_entry.pack(side=tk.LEFT, padx=2)
        # Return key in search box navigates to next match (local widget binding)
        # Note: This binding is specific to the in-page search entry widget and is not
        # documented in tk_keybindings.json, which only documents global application
        # keybindings. Local widget bindings are documented in code comments only.
        self.inpage_search_entry.bind('<Return>', lambda e: self._inpage_find_next())
        # ESC key closes search bar (local widget binding, not in tk_keybindings.json)
        self.inpage_search_entry.bind('<Escape>', lambda e: self._inpage_search_close())

        ttk.Button(self.inpage_search_bar, text="▲ Prev", command=self._inpage_find_prev, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.inpage_search_bar, text="▼ Next", command=self._inpage_find_next, width=8).pack(side=tk.LEFT, padx=2)

        self.inpage_match_label = ttk.Label(self.inpage_search_bar, text="")
        self.inpage_match_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(self.inpage_search_bar, text="✕ Close", command=self._inpage_search_close, width=8).pack(side=tk.LEFT, padx=2)

        # Main content frame with scrollbar
        content_frame = ttk.Frame(self)
        content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Text widget for displaying help content
        self.text_widget = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            width=100,
            height=35,
            font=("TkDefaultFont", 10),
            cursor="arrow"
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure tags for styling
        self.text_widget.tag_config("title", font=("TkDefaultFont", 16, "bold"), foreground="#2c3e50")
        self.text_widget.tag_config("heading1", font=("TkDefaultFont", 14, "bold"), foreground="#34495e", spacing1=10)
        self.text_widget.tag_config("heading2", font=("TkDefaultFont", 12, "bold"), foreground="#7f8c8d", spacing1=8)
        self.text_widget.tag_config("code", font=("Courier", 10), background="#f4f4f4")
        self.text_widget.tag_config("link", foreground="#3498db", underline=1)
        self.text_widget.tag_config("link_hover", foreground="#2980b9", underline=1)
        self.text_widget.tag_config("tier_language", foreground="#c0392b")  # 📕
        self.text_widget.tag_config("tier_mbasic", foreground="#27ae60")    # 📗
        self.text_widget.tag_config("tier_ui", foreground="#2980b9")        # 📘
        self.text_widget.tag_config("search_highlight", background="#ffff00")  # Yellow highlight
        self.text_widget.tag_config("search_current", background="#ffa500")    # Orange for current match

        # Raise search tags so they appear above other formatting
        self.text_widget.tag_raise("search_highlight")
        self.text_widget.tag_raise("search_current")

        # Bind link clicks
        self.text_widget.tag_bind("link", "<Button-1>", self._on_link_click)
        self.text_widget.tag_bind("link", "<Enter>", lambda e: self.text_widget.config(cursor="hand2"))
        self.text_widget.tag_bind("link", "<Leave>", lambda e: self.text_widget.config(cursor="arrow"))

        # Make text read-only but allow copy (Ctrl+C) and find (Ctrl+F)
        def readonly_key_handler(event):
            # Allow Ctrl+C (copy), Ctrl+A (select all), Ctrl+F (find)
            if event.state & 0x4:  # Control key
                if event.keysym in ('c', 'C', 'a', 'A'):  # Ctrl+C, Ctrl+A
                    return  # Allow these
                elif event.keysym in ('f', 'F'):  # Ctrl+F
                    self._inpage_search_show()
                    return "break"
            return "break"  # Block all other keys

        self.text_widget.bind("<Key>", readonly_key_handler)

        # Also bind Ctrl+F globally to the window
        self.bind("<Control-f>", lambda e: self._inpage_search_show())

        # Enable right-click context menu for copy
        self._create_context_menu()

        # Status bar
        self.status_label = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_search_indexes(self) -> Dict:
        """Load pre-built merged search index for this UI."""
        merged_index_path = self.help_root / 'ui/tk/merged_index.json'

        try:
            if merged_index_path.exists():
                with open(merged_index_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass

        # Return empty index if load fails
        return {'files': []}

    def _load_topic(self, relative_path: str) -> bool:
        """Load and render a help topic."""
        full_path = self.help_root / relative_path

        if not full_path.exists():
            self._display_error(f"Help topic not found: {relative_path}\n(Full path: {full_path})")
            return False

        try:
            with open(full_path, 'r') as f:
                content = f.read()

            # Skip YAML front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            # Expand macros
            content = self.macros.expand(content)

            # Update current topic
            self.current_topic = relative_path

            # Update status
            topic_name = relative_path.rsplit('/', 1)[-1].replace('.md', '').replace('-', ' ').title()
            self.status_label.config(text=f"Viewing: {topic_name}")

            # Render content
            self._render_markdown(content)

            return True

        except Exception as e:
            self._display_error(f"Error loading help: {str(e)}")
            return False

    def _render_markdown(self, markdown: str):
        """Render markdown content to the text widget."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)

        # Reset link counter and URL mapping for new page
        self.link_counter = 0
        self.link_urls = {}

        # Simple markdown rendering
        lines = markdown.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                self.text_widget.insert(tk.END, "\n")
                i += 1
                continue

            # Headers
            if line.startswith('# '):
                self.text_widget.insert(tk.END, line[2:] + "\n", "title")
            elif line.startswith('## '):
                self.text_widget.insert(tk.END, line[3:] + "\n", "heading1")
            elif line.startswith('### '):
                self.text_widget.insert(tk.END, line[4:] + "\n", "heading2")

            # Code blocks
            elif line.startswith('```'):
                # Read until closing ```
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                self.text_widget.insert(tk.END, '\n'.join(code_lines) + "\n\n", "code")

            # Tables - format properly
            elif '|' in line and line.strip().startswith('|'):
                formatted = self._format_table_row(line)
                if formatted:  # Skip separator rows
                    self.text_widget.insert(tk.END, formatted + "\n", "code")

            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                self._render_line_with_links(line + "\n")

            # Regular text (may contain links)
            else:
                self._render_line_with_links(line + "\n")

            i += 1

        self.text_widget.config(state=tk.DISABLED)

    def _render_line_with_links(self, line: str):
        """Render a line that may contain markdown links."""
        # Find all [text](url) patterns
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        last_end = 0
        for match in re.finditer(link_pattern, line):
            # Insert text before link
            self.text_widget.insert(tk.END, line[last_end:match.start()])

            # Insert link
            link_text = match.group(1)
            link_url = match.group(2)

            # Create unique tag for this link using counter
            self.link_counter += 1
            tag_name = f"link_{self.link_counter}"
            self.link_urls[tag_name] = link_url  # Store URL for context menu
            self.text_widget.insert(tk.END, link_text, (tag_name, "link"))

            # Bind click to this specific link
            self.text_widget.tag_bind(tag_name, "<Button-1>",
                lambda e, url=link_url: self._follow_link(url))

            last_end = match.end()

        # Insert remaining text
        self.text_widget.insert(tk.END, line[last_end:])

    def _follow_link(self, target: str):
        """Follow a link to another help topic.

        Handles both absolute and relative link paths:
        - Absolute paths: Start with '/', 'common/', or contain ':/' or ':\\'
        - Relative paths: Resolved from current topic's directory using Path operations

        All paths are normalized to forward slashes for consistency.

        Note: Path normalization logic is duplicated in _open_link_in_new_window().
        Both methods use similar approach: resolve relative paths, normalize to help_root,
        handle path separators. If modification needed, update both methods consistently.
        """
        # Check if target is an absolute path (starts with / or contains :/)
        # OR starts with common/ (common help paths should always be absolute)
        # Absolute paths are relative to help root
        if target.startswith('/') or target.startswith('common/') or ':/' in target or ':\\' in target:
            # This is an absolute path relative to help root
            new_topic = target.lstrip('/').replace('\\', '/')
        else:
            # Resolve relative path from current topic's directory
            # This includes both "./" prefixed and simple filenames like "getting-started.md"
            current_dir = Path(self.current_topic).parent
            if str(current_dir) == '.':
                new_topic_path = Path(target)
            else:
                new_topic_path = current_dir / target

            # Normalize path (resolve .. and .)
            # Convert to absolute, resolve, then make relative to help_root
            abs_path = (self.help_root / new_topic_path).resolve()

            try:
                new_topic = str(abs_path.relative_to(self.help_root.resolve()))
            except ValueError:
                # Path is outside help_root, use as-is
                new_topic = str(new_topic_path)

            # Normalize path separators
            new_topic = new_topic.replace('\\', '/')

        # Save current topic to history
        self.history.append(self.current_topic)
        self.back_button.config(state=tk.NORMAL)

        # Load new topic
        self._load_topic(new_topic)

    def _on_link_click(self, event):
        """Handle link click event."""
        # Get the clicked position
        index = self.text_widget.index(f"@{event.x},{event.y}")

        # Find which link tag is at this position
        tags = self.text_widget.tag_names(index)
        for tag in tags:
            if tag.startswith("link_"):
                # Link already has its own binding
                return

    def _go_back(self):
        """Go back to previous topic."""
        if self.history:
            previous_topic = self.history.pop()
            self._load_topic(previous_topic)

            if not self.history:
                self.back_button.config(state=tk.DISABLED)

    def _go_home(self):
        """Go to help home page."""
        if self.current_topic != "index.md":
            self.history.append(self.current_topic)
            self.back_button.config(state=tk.NORMAL)
            self._load_topic("index.md")

    def _execute_search(self):
        """Execute search and display results."""
        query = self.search_entry.get().strip()

        if not query:
            return

        # Perform search
        results = self._search_indexes(query)

        # Display results
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)

        # Reset link counter and URL mapping for search results
        self.link_counter = 0
        self.link_urls = {}

        if not results:
            self.text_widget.insert(tk.END, f"No results found for '{query}'\n\n", "title")
            self.text_widget.insert(tk.END, "Try:\n")
            self.text_widget.insert(tk.END, "• Different keywords (e.g., 'loop', 'array', 'file')\n")
            self.text_widget.insert(tk.END, "• Statement names (e.g., 'print', 'for', 'if')\n")
            self.text_widget.insert(tk.END, "• Function names (e.g., 'left$', 'abs', 'int')\n")
        else:
            self.text_widget.insert(tk.END, f"Search results for '{query}' ({len(results)} found):\n\n", "title")

            for tier, path, title, desc in results:
                # Tier marker with color
                tier_tag = None
                if '📕' in tier:
                    tier_tag = "tier_language"
                elif '📗' in tier:
                    tier_tag = "tier_mbasic"
                elif '📘' in tier:
                    tier_tag = "tier_ui"

                self.text_widget.insert(tk.END, f"{tier} ", tier_tag)

                # Title as link - use counter for unique tag
                self.link_counter += 1
                tag_name = f"result_link_{self.link_counter}"
                self.link_urls[tag_name] = path  # Store path for context menu
                self.text_widget.insert(tk.END, title + "\n", (tag_name, "link"))
                self.text_widget.tag_bind(tag_name, "<Button-1>",
                    lambda e, p=path: self._follow_link(p))

                # Description
                if desc and desc != 'NEEDS_DESCRIPTION':
                    desc_short = desc[:100] + '...' if len(desc) > 100 else desc
                    self.text_widget.insert(tk.END, f"  {desc_short}\n")

                self.text_widget.insert(tk.END, f"  → {path}\n\n")

        self.text_widget.config(state=tk.DISABLED)
        self.status_label.config(text=f"Search: {query} ({len(results)} results)")

    def _fuzzy_match(self, query: str, target: str, max_distance: int = 2) -> bool:
        """
        Check if query fuzzy matches target using simple edit distance.

        Args:
            query: Search query (already lowercase)
            target: Target string (already lowercase)
            max_distance: Maximum edit distance to consider a match

        Returns:
            True if fuzzy match within max_distance
        """
        # Only apply fuzzy matching to words >= 4 chars
        if len(query) < 4:
            return False

        # Quick exact match check
        if query in target:
            return True

        # Check each word in target
        target_words = target.split()
        for word in target_words:
            if len(word) < 4:
                continue

            # Simple Levenshtein distance calculation
            if len(query) > len(word) + max_distance or len(word) > len(query) + max_distance:
                continue

            # Create distance matrix
            d = [[0] * (len(word) + 1) for _ in range(len(query) + 1)]

            for i in range(len(query) + 1):
                d[i][0] = i
            for j in range(len(word) + 1):
                d[0][j] = j

            for i in range(1, len(query) + 1):
                for j in range(1, len(word) + 1):
                    cost = 0 if query[i-1] == word[j-1] else 1
                    d[i][j] = min(
                        d[i-1][j] + 1,      # deletion
                        d[i][j-1] + 1,      # insertion
                        d[i-1][j-1] + cost  # substitution
                    )

            if d[len(query)][len(word)] <= max_distance:
                return True

        return False

    def _search_indexes(self, query: str) -> List[Tuple[str, str, str, str]]:
        """
        Search the merged index with ranking and fuzzy matching.

        Returns list of (tier, path, title, description) tuples, sorted by relevance.
        """
        scored_results = []
        query_lower = query.lower()

        # Merged index has pre-built structure with all files and metadata
        if 'files' not in self.search_indexes:
            return []

        # Map tier to labels
        tier_labels = {
            'language': '📕 Language',
            'mbasic': '📗 MBASIC',
        }

        for file_info in self.search_indexes['files']:
            # Get searchable fields
            title = file_info.get('title', '').lower()
            desc = file_info.get('description', '').lower()
            file_type = file_info.get('type', '').lower()
            category = file_info.get('category', '').lower()
            keywords = [kw.lower() for kw in file_info.get('keywords', [])]

            score = 0

            # Exact matches (higher scores)
            if query_lower == title:
                score += 100  # Exact title match
            elif query_lower in title:
                score += 10   # Title contains query

            # Check exact keyword matches
            if query_lower in keywords:
                score += 50   # Exact keyword match
            elif any(query_lower in kw for kw in keywords):
                score += 5    # Keyword contains query

            # Check description match
            if query_lower in desc:
                score += 2

            # Check type/category match
            if query_lower in file_type or query_lower in category:
                score += 1

            # Fuzzy matching on title and keywords (only if no exact matches)
            if score == 0:
                if self._fuzzy_match(query_lower, title):
                    score += 8  # Fuzzy title match

                for kw in keywords:
                    if self._fuzzy_match(query_lower, kw):
                        score += 4  # Fuzzy keyword match
                        break

            # If we have any score, add to results
            if score > 0:
                # Determine tier label from tier field or path
                tier_name = file_info.get('tier', '')
                if tier_name.startswith('ui/'):
                    tier_label = '📘 UI'
                else:
                    tier_label = tier_labels.get(tier_name, '📙 Other')

                scored_results.append((
                    score,
                    tier_label,
                    file_info.get('path', ''),
                    file_info.get('title', ''),
                    file_info.get('description', '')
                ))

        # Sort by score descending, then by title
        scored_results.sort(key=lambda x: (-x[0], x[3].lower()))

        # Return without scores (drop first element)
        return [(tier, path, title, desc) for _, tier, path, title, desc in scored_results]

    def _inpage_search_show(self):
        """Show the in-page search bar and focus on it."""
        if not self.inpage_search_visible:
            self.inpage_search_bar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2, after=self.children['!frame'])
            self.inpage_search_visible = True

        self.inpage_search_entry.focus()
        self.inpage_search_entry.select_range(0, tk.END)

    def _inpage_search_close(self):
        """Close the in-page search bar and clear highlights."""
        if self.inpage_search_visible:
            self.inpage_search_bar.pack_forget()
            self.inpage_search_visible = False

        # Clear all search highlights
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        self.text_widget.tag_remove("search_current", "1.0", tk.END)

        # Reset search state
        self.inpage_search_matches = []
        self.inpage_search_current = -1
        self.inpage_search_query = ""
        self.inpage_match_label.config(text="")

    def _inpage_find_matches(self):
        """Find all matches for the current in-page search query."""
        query = self.inpage_search_entry.get().strip()

        # If query is empty or unchanged, don't re-search
        if not query:
            return

        # If query changed, clear old highlights and find new matches
        if query != self.inpage_search_query:
            self.inpage_search_query = query
            self.inpage_search_matches = []
            self.inpage_search_current = -1

            # Clear old highlights
            self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
            self.text_widget.tag_remove("search_current", "1.0", tk.END)

            # Find all matches using text widget's search method
            start_pos = "1.0"
            while True:
                pos = self.text_widget.search(query, start_pos, stopindex=tk.END, nocase=True)
                if not pos:
                    break

                end_pos = f"{pos}+{len(query)}c"
                self.inpage_search_matches.append((pos, end_pos))

                # Highlight this match
                self.text_widget.tag_add("search_highlight", pos, end_pos)

                start_pos = end_pos

            # Update match count label
            if self.inpage_search_matches:
                self.inpage_match_label.config(text=f"{len(self.inpage_search_matches)} matches")
            else:
                self.inpage_match_label.config(text="No matches")

    def _inpage_find_next(self):
        """Find and highlight the next match."""
        self._inpage_find_matches()

        if not self.inpage_search_matches:
            return

        # Move to next match
        self.inpage_search_current = (self.inpage_search_current + 1) % len(self.inpage_search_matches)

        # Update highlights
        self._inpage_highlight_current()

    def _inpage_find_prev(self):
        """Find and highlight the previous match."""
        self._inpage_find_matches()

        if not self.inpage_search_matches:
            return

        # Move to previous match
        self.inpage_search_current = (self.inpage_search_current - 1) % len(self.inpage_search_matches)

        # Update highlights
        self._inpage_highlight_current()

    def _inpage_highlight_current(self):
        """Highlight the current match and scroll to it."""
        if not self.inpage_search_matches or self.inpage_search_current < 0:
            return

        # Remove old current highlight
        self.text_widget.tag_remove("search_current", "1.0", tk.END)

        # Add current highlight
        pos, end_pos = self.inpage_search_matches[self.inpage_search_current]
        self.text_widget.tag_add("search_current", pos, end_pos)

        # Scroll to make current match visible
        self.text_widget.see(pos)

        # Update match count label
        self.inpage_match_label.config(
            text=f"{self.inpage_search_current + 1}/{len(self.inpage_search_matches)}"
        )

    def _display_error(self, message: str):
        """Display an error message in the text widget."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "Error\n\n", "title")
        self.text_widget.insert(tk.END, message)
        self.text_widget.config(state=tk.DISABLED)
        self.status_label.config(text="Error")

    def _create_context_menu(self):
        """Create right-click context menu for copy operations and links."""
        def show_context_menu(event):
            # Create a new menu each time based on context
            menu = tk.Menu(self.text_widget, tearoff=0)

            # Check if we're on a link
            # Note: Both "link_" (from _render_line_with_links) and "result_link_"
            # (from _execute_search) prefixes are checked. Both types are stored
            # identically in self.link_urls, but the prefixes distinguish their origin.
            index = self.text_widget.index(f"@{event.x},{event.y}")
            tags = self.text_widget.tag_names(index)
            link_tag = None

            for tag in tags:
                if tag.startswith("link_") or tag.startswith("result_link_"):
                    link_tag = tag
                    break

            if link_tag:
                # We're on a link - offer to open in new window
                menu.add_command(label="Open in New Window",
                                command=lambda: self._open_link_in_new_window(link_tag))
                menu.add_separator()

            # Always offer copy if there's a selection
            try:
                if self.text_widget.tag_ranges(tk.SEL):
                    menu.add_command(label="Copy", command=self._copy_selection)
            except tk.TclError:
                pass

            # Always offer select all
            menu.add_command(label="Select All", command=self._select_all)

            # Note: tk_popup() handles menu dismissal automatically (ESC key,
            # clicks outside menu, selecting items). Explicit bindings for
            # FocusOut/Escape are not needed and may not fire reliably since
            # Menu widgets have their own event handling for dismissal.
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                # Release grab after menu is shown. Note: tk_popup handles menu interaction,
                # but we explicitly release the grab to ensure clean state.
                menu.grab_release()

        self.text_widget.bind("<Button-3>", show_context_menu)  # Right-click

    def _copy_selection(self):
        """Copy selected text to clipboard."""
        try:
            selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection

    def _select_all(self):
        """Select all text in the widget."""
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END)
        self.text_widget.mark_set(tk.INSERT, "1.0")
        self.text_widget.see(tk.INSERT)

    def _open_link_in_new_window(self, link_tag: str):
        """Open a link in a new help browser window.

        Note: Path normalization logic is duplicated from _follow_link().
        Both methods resolve paths relative to help_root with similar logic.
        If modification needed, update both methods consistently.
        """
        # Get the URL from our stored mapping
        url = self.link_urls.get(link_tag)
        if url:
            # Check if URL is already an absolute path (from search results)
            if not url.startswith('.'):
                # Already a help-root-relative path
                resolved_url = url.replace('\\', '/')
            else:
                # Resolve the relative path based on current topic
                current_dir = Path(self.current_topic).parent
                if str(current_dir) == '.':
                    new_topic_path = Path(url)
                else:
                    new_topic_path = current_dir / url

                # Convert to absolute path and back to relative from help_root
                abs_path = (self.help_root / new_topic_path).resolve()
                try:
                    resolved_url = str(abs_path.relative_to(self.help_root.resolve()))
                except ValueError:
                    # If it can't be made relative, use the original
                    resolved_url = str(new_topic_path)

                resolved_url = resolved_url.replace('\\', '/')

            # Create new browser window with the resolved topic
            new_browser = TkHelpBrowser(self.master, str(self.help_root), resolved_url)

    def _format_table_row(self, line: str) -> str:
        """Format a markdown table row for display.

        Note: This implementation may be duplicated in src/ui/markdown_renderer.py.
        If both implementations exist and changes are needed to table formatting logic,
        consider extracting to a shared utility module to maintain consistency.
        """
        # Strip and split by |
        parts = [p.strip() for p in line.strip().split('|')]
        parts = [p for p in parts if p]

        # Skip separator rows (|---|---|)
        if all(set(p) <= set('-: ') for p in parts):
            return ''  # Skip separator lines entirely

        # Format columns with consistent spacing (15 chars each)
        formatted_parts = []
        for part in parts:
            # Clean up any remaining markdown in cells
            part = re.sub(r'\*\*([^*]+)\*\*', r'\1', part)  # Bold
            part = re.sub(r'`([^`]+)`', r'\1', part)        # Code
            formatted_parts.append(part.ljust(15))

        return '  '.join(formatted_parts)
