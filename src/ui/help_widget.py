"""
Urwid-based help browser widget for navigating markdown documentation.

Provides:
- Up/Down scrolling through help content
- Enter to follow links
- ESC/Q to exit
- Navigation breadcrumbs
- Search across three-tier help system (/)
"""

import urwid
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import json
from .markdown_renderer import MarkdownRenderer
from .help_macros import HelpMacros


class HelpWidget(urwid.WidgetWrap):
    """Urwid widget for browsing help documentation."""

    def __init__(self, help_root: str, initial_topic: str = "ui/curses/index.md"):
        """
        Initialize help browser widget.

        Args:
            help_root: Path to help documentation root (e.g., "docs/help")
            initial_topic: Initial topic to display (relative to help_root)
        """
        self.help_root = Path(help_root)
        self.renderer = MarkdownRenderer()
        self.macros = HelpMacros('curses', help_root)

        # Navigation state
        self.current_topic = initial_topic
        self.history = []  # Stack of previous topics
        self.current_links = []  # List of (line_num, text, target) for current page
        self.link_positions = []  # List of line numbers with links (for navigation)
        self.current_link_index = 0  # Which link is selected

        # Search state
        self.search_indexes = self._load_search_indexes()
        self.search_mode = False
        self.search_query = ""
        self.search_results = []
        self.search_result_index = 0

        # Create display widgets
        self.text_widget = urwid.Text("")
        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker([self.text_widget]))

        # Create frame with title and footer
        self.title = urwid.Text("")
        self.footer = urwid.Text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search U=Back ESC/Q=Exit ")

        frame = urwid.Frame(
            self.listbox,
            header=urwid.AttrMap(self.title, 'header'),
            footer=urwid.AttrMap(self.footer, 'footer')
        )

        # Wrap in line box
        box = urwid.LineBox(frame, title="Help")

        super().__init__(box)

        # Load initial topic
        self._load_topic(initial_topic)

    def _load_search_indexes(self) -> Dict[str, Dict]:
        """Load all three search indexes (language, mbasic, ui)."""
        indexes = {}

        # Try to load each search index
        index_paths = [
            ('language', self.help_root / 'common/language/search_index.json'),
            ('mbasic', self.help_root / 'mbasic/search_index.json'),
            ('ui', self.help_root / 'ui/curses/search_index.json'),
        ]

        for name, path in index_paths:
            try:
                if path.exists():
                    with open(path, 'r') as f:
                        indexes[name] = json.load(f)
            except Exception:
                # If index can't be loaded, continue without it
                pass

        return indexes

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
                'ui': 'ui/curses/',
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
                        # Keyword match - add all files with this keyword
                        if isinstance(paths, list):
                            for path in paths:
                                # Find file info
                                file_info = self._find_file_info(index, path)
                                if file_info:
                                    results.append((
                                        tier_label,
                                        tier_prefix + path,
                                        file_info.get('title', path),
                                        file_info.get('description', '')
                                    ))
                        else:
                            # Single path (alias)
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

    def _show_search_prompt(self):
        """Show search input prompt."""
        self.search_mode = True
        self.search_query = ""
        self.footer.set_text(" Search: _ (type query, Enter to search, ESC to cancel)")
        self.title.set_text(" MBASIC Help: Search ")

    def _execute_search(self):
        """Execute search and display results."""
        if not self.search_query:
            self.search_mode = False
            self.footer.set_text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search U=Back ESC/Q=Exit ")
            self._load_topic(self.current_topic)
            return

        # Perform search
        self.search_results = self._search_indexes(self.search_query)
        self.search_result_index = 0

        # Display results
        if not self.search_results:
            result_text = f"No results found for '{self.search_query}'\n\n"
            result_text += "Try:\n"
            result_text += "- Different keywords (e.g., 'loop', 'array', 'file')\n"
            result_text += "- Statement names (e.g., 'print', 'for', 'if')\n"
            result_text += "- Function names (e.g., 'left$', 'abs', 'int')\n"
            result_text += "\nPress ESC to return, / to search again"
            self.text_widget.set_text(result_text)
            self.current_links = []
            self.search_mode = False
            self.footer.set_text(" /=New Search ESC=Back ")
        else:
            # Format results
            result_text = f"Search results for '{self.search_query}' ({len(self.search_results)} found):\n\n"

            self.current_links = []
            for i, (tier, path, title, desc) in enumerate(self.search_results):
                result_text += f"{tier} {title}\n"
                if desc and desc != 'NEEDS_DESCRIPTION':
                    result_text += f"  {desc[:70]}{'...' if len(desc) > 70 else ''}\n"
                result_text += f"  → {path}\n\n"

                # Add as link
                self.current_links.append((i * 4, title, path))

            self.text_widget.set_text(result_text)
            self.link_positions = [link[0] for link in self.current_links]
            self.current_link_index = 0
            self.search_mode = False
            self.footer.set_text(" ↑/↓=Scroll Tab=Next Result Enter=Open /=New Search ESC=Back ")

        self.title.set_text(f" Search: {self.search_query} ")

    def _cancel_search(self):
        """Cancel search and return to previous topic."""
        self.search_mode = False
        self.search_query = ""
        self.footer.set_text(" ↑/↓=Scroll Tab=Next Link Enter=Follow /=Search U=Back ESC/Q=Exit ")
        self._load_topic(self.current_topic)

    def _create_text_markup_with_links(self, lines: List[str]) -> List:
        """
        Convert plain text lines to urwid markup with link highlighting.

        Links are marked with [text] in the rendered output. This method
        converts them to use the 'link' attribute for highlighting.

        Args:
            lines: List of plain text lines with links marked as [text]

        Returns:
            Urwid text markup (list of tuples or strings)
        """
        import re

        markup = []

        for line in lines:
            # Find all [text] patterns (links)
            link_pattern = r'\[([^\]]+)\]'

            # Split the line by links and build markup
            last_end = 0
            line_markup = []

            for match in re.finditer(link_pattern, line):
                # Add text before the link
                if match.start() > last_end:
                    line_markup.append(line[last_end:match.start()])

                # Add the link with 'link' attribute
                link_text = match.group(0)  # Keep the brackets
                line_markup.append(('link', link_text))

                last_end = match.end()

            # Add remaining text after last link
            if last_end < len(line):
                line_markup.append(line[last_end:])

            # If line has no links, just add it as plain text
            if not line_markup:
                line_markup = [line]

            # Add newline after each line (except the last)
            markup.extend(line_markup)
            markup.append('\n')

        # Remove trailing newline
        if markup and markup[-1] == '\n':
            markup.pop()

        return markup

    def _load_topic(self, relative_path: str) -> bool:
        """Load and render a help topic."""
        full_path = self.help_root / relative_path

        if not full_path.exists():
            error_text = f"Error: Help topic not found\n\nPath: {relative_path}\n\nPress ESC or Q to exit."
            self.text_widget.set_text(error_text)
            self.current_links = []
            self.link_positions = []
            self.title.set_text(f" MBASIC Help: {relative_path} (NOT FOUND) ")
            return False

        # Read and render the markdown
        try:
            with open(full_path, 'r') as f:
                markdown = f.read()

            # Expand macros before rendering
            markdown = self.macros.expand(markdown)

            lines, links = self.renderer.render(markdown)

            # Create text markup with link highlighting
            text_markup = self._create_text_markup_with_links(lines)

            # Set the content
            self.text_widget.set_text(text_markup)

            # Store links and positions
            self.current_links = links
            self.link_positions = [link[0] for link in links]
            self.current_link_index = 0

            # Update title
            self.current_topic = relative_path
            topic_name = relative_path.rsplit('/', 1)[-1].replace('.md', '').replace('-', ' ').title()
            self.title.set_text(f" MBASIC Help: {topic_name} ")

            return True

        except Exception as e:
            import traceback
            error_text = f"Error loading help topic:\n\n{str(e)}\n\n{traceback.format_exc()}\n\nPress ESC or Q to exit."
            self.text_widget.set_text(error_text)
            self.current_links = []
            self.link_positions = []
            return False

    def keypress(self, size, key):
        """Handle keypresses for help navigation."""

        # Search mode input handling
        if self.search_mode:
            if key == 'esc':
                self._cancel_search()
                return None
            elif key == 'enter':
                self._execute_search()
                return None
            elif key == 'backspace':
                if self.search_query:
                    self.search_query = self.search_query[:-1]
                    self.footer.set_text(f" Search: {self.search_query}_ (type query, Enter to search, ESC to cancel)")
                return None
            elif len(key) == 1 and key.isprintable():
                self.search_query += key
                self.footer.set_text(f" Search: {self.search_query}_ (type query, Enter to search, ESC to cancel)")
                return None
            else:
                return None

        # Normal mode navigation
        if key in ('q', 'Q', 'esc'):
            # Signal to close help
            return 'esc'

        elif key == '/':
            # Enter search mode
            self._show_search_prompt()
            return None

        elif key == 'enter':
            # Follow current link
            if self.current_links and self.current_link_index < len(self.current_links):
                _, _, target = self.current_links[self.current_link_index]

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

                # Load new topic
                self._load_topic(new_topic)
                return None

        elif key == 'u' or key == 'U':
            # Go back in history
            if self.history:
                previous_topic = self.history.pop()
                self._load_topic(previous_topic)
                return None

        elif key == 'tab':
            # Move to next link
            if self.link_positions:
                self.current_link_index = (self.current_link_index + 1) % len(self.link_positions)
                return None

        elif key == 'shift tab':
            # Move to previous link
            if self.link_positions:
                self.current_link_index = (self.current_link_index - 1) % len(self.link_positions)
                return None

        # Pass other keys to listbox for scrolling
        return super().keypress(size, key)
