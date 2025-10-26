"""
Tkinter-based help browser for navigating markdown documentation.

Provides:
- Scrollable help content display
- Clickable links
- Search across three-tier help system
- Navigation history (back button)
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

    def __init__(self, parent, help_root: str, initial_topic: str = "ui/tk/index.md"):
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

        # Bind link clicks
        self.text_widget.tag_bind("link", "<Button-1>", self._on_link_click)
        self.text_widget.tag_bind("link", "<Enter>", lambda e: self.text_widget.config(cursor="hand2"))
        self.text_widget.tag_bind("link", "<Leave>", lambda e: self.text_widget.config(cursor="arrow"))

        # Make text read-only but allow copy (Ctrl+C)
        def readonly_key_handler(event):
            # Allow copy operations
            if event.state & 0x4:  # Control key
                if event.keysym in ('c', 'C', 'a', 'A'):  # Ctrl+C, Ctrl+A
                    return  # Allow these
            return "break"  # Block all other keys

        self.text_widget.bind("<Key>", readonly_key_handler)

        # Enable right-click context menu for copy
        self._create_context_menu()

        # Status bar
        self.status_label = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_search_indexes(self) -> Dict[str, Dict]:
        """Load all three search indexes (language, mbasic, ui)."""
        indexes = {}

        index_paths = [
            ('language', self.help_root / 'common/language/search_index.json'),
            ('mbasic', self.help_root / 'mbasic/search_index.json'),
            ('ui', self.help_root / 'ui/tk/search_index.json'),
        ]

        for name, path in index_paths:
            try:
                if path.exists():
                    with open(path, 'r') as f:
                        indexes[name] = json.load(f)
            except Exception:
                pass

        return indexes

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
        """Follow a link to another help topic."""
        # Check if target is already an absolute path (from search results)
        # Absolute paths don't start with . or ..
        if not target.startswith('.'):
            # This is already a help-root-relative path (e.g., from search results)
            new_topic = target.replace('\\', '/')
        else:
            # Resolve relative path from current topic
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
        if self.current_topic != "ui/tk/index.md":
            self.history.append(self.current_topic)
            self.back_button.config(state=tk.NORMAL)
            self._load_topic("ui/tk/index.md")

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

    def _search_indexes(self, query: str) -> List[Tuple[str, str, str, str]]:
        """
        Search across all loaded indexes.

        Returns list of (tier, path, title, description) tuples.
        """
        results = []
        query_lower = query.lower()

        for tier_name, index in self.search_indexes.items():
            # Map tier names to paths
            tier_prefix = {
                'language': 'common/language/',
                'mbasic': 'mbasic/',
                'ui': 'ui/tk/',
            }.get(tier_name, '')

            tier_label = {
                'language': '📕 Language',
                'mbasic': '📗 MBASIC',
                'ui': '📘 UI',
            }.get(tier_name, tier_name)

            # Search in keywords
            if 'keywords' in index:
                for keyword, paths in index['keywords'].items():
                    if query_lower in keyword.lower():
                        if isinstance(paths, list):
                            for path in paths:
                                file_info = self._find_file_info(index, path)
                                if file_info:
                                    results.append((
                                        tier_label,
                                        tier_prefix + path,
                                        file_info.get('title', path),
                                        file_info.get('description', '')
                                    ))
                        else:
                            file_info = self._find_file_info(index, paths)
                            if file_info:
                                results.append((
                                    tier_label,
                                    tier_prefix + paths,
                                    file_info.get('title', paths),
                                    file_info.get('description', '')
                                ))

            # Search in aliases
            if 'aliases' in index:
                for alias, path in index['aliases'].items():
                    if query_lower in alias.lower():
                        file_info = self._find_file_info(index, path)
                        if file_info:
                            results.append((
                                tier_label,
                                tier_prefix + path,
                                file_info.get('title', path),
                                file_info.get('description', '')
                            ))

            # Search in titles and descriptions
            if 'files' in index:
                for file_info in index['files']:
                    title = file_info.get('title', '').lower()
                    desc = file_info.get('description', '').lower()

                    if query_lower in title or query_lower in desc:
                        results.append((
                            tier_label,
                            tier_prefix + file_info.get('path', ''),
                            file_info.get('title', ''),
                            file_info.get('description', '')
                        ))

        # Deduplicate by path (keep first occurrence)
        seen_paths = set()
        deduped_results = []
        for result in results:
            path = result[1]  # path is the second element
            if path not in seen_paths:
                seen_paths.add(path)
                deduped_results.append(result)

        return deduped_results

    def _find_file_info(self, index: Dict, path: str) -> Optional[Dict]:
        """Find file info in index by path."""
        if 'files' in index:
            for file_info in index['files']:
                if file_info.get('path') == path:
                    return file_info
        return None

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

            # Allow menu to be dismissed
            def dismiss_menu():
                try:
                    menu.unpost()
                except:
                    pass

            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                # Release grab after a short delay to allow menu interaction
                menu.grab_release()

            # Bind ESC and clicks outside to dismiss
            menu.bind("<FocusOut>", lambda e: dismiss_menu())
            menu.bind("<Escape>", lambda e: dismiss_menu())

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
        """Open a link in a new help browser window."""
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
        """Format a markdown table row for display."""
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
