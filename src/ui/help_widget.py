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

    def __init__(self, help_root: str, initial_topic: str = "index.md", on_close=None):
        """
        Initialize help browser widget.

        Args:
            help_root: Path to help documentation root (e.g., "docs/help")
            initial_topic: Initial topic to display (relative to help_root)
            on_close: Optional callback function to call when help is closed
        """
        self.help_root = Path(help_root)
        self.on_close = on_close
        self.renderer = MarkdownRenderer()
        # HelpWidget is curses-specific (uses urwid), so hardcode 'curses' UI name
        self.macros = HelpMacros('curses', help_root)

        # Navigation state
        self.current_topic = initial_topic
        self.history = []  # Stack of previous topics
        self.current_links = []  # List of (line_num, text, target) for current page
        self.link_positions = []  # List of line numbers with links (for navigation)
        self.current_link_index = 0  # Which link is selected
        self.current_rendered_lines = []  # Cache of rendered lines for re-rendering

        # Search state
        self.search_indexes = self._load_search_indexes()
        self.search_mode = False
        self.search_query = ""
        self.search_results = []
        self.search_result_index = 0

        # Create display widgets
        # Use SimpleFocusListWalker to hold list of line widgets for scrolling
        self.walker = urwid.SimpleFocusListWalker([])
        self.listbox = urwid.ListBox(self.walker)

        # Create frame with title and footer
        self.title = urwid.Text("")
        # Footer shows navigation keys for the help system specifically
        # Note: Help navigation keys are hardcoded here and in keypress() method, not loaded from
        # keybindings. The help widget uses fixed keys (U for back, / for search, ESC/Q to exit)
        # to avoid dependency on keybinding configuration. HelpMacros does load the full keybindings
        # from JSON (for {{kbd:action}} macro expansion in help content), but the help widget itself
        # doesn't use those loaded keybindings. If help navigation keys change, update here and keypress().
        self.footer = urwid.Text(" ↑/↓=Scroll →/←=Next/Prev Link Enter=Follow /=Search U=Back ESC/Q=Exit ")

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

    def _load_search_indexes(self) -> Dict:
        """Load pre-built merged search index for this UI."""
        merged_index_path = self.help_root / 'ui/curses/merged_index.json'

        try:
            if merged_index_path.exists():
                with open(merged_index_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass

        # Return empty index if load fails
        return {'files': []}

    def _search_indexes(self, query: str) -> List[Tuple[str, str, str, str]]:
        """
        Search the merged index.

        Returns list of (tier, path, title, description) tuples.
        """
        results = []
        query_lower = query.lower()

        # Merged index has pre-built structure with all files and metadata
        if 'files' not in self.search_indexes:
            return results

        # Map tier to labels for search result display
        # Note: UI tier (e.g., 'ui/curses', 'ui/tk') is detected via startswith('ui/')
        # check below and gets '📘 UI' label. Other unrecognized tiers get '📙 Other'.
        tier_labels = {
            'language': '📕 Language',
            'mbasic': '📗 MBASIC',
        }

        for file_info in self.search_indexes['files']:
            # Check if query matches title, description, type, or keywords
            title = file_info.get('title', '').lower()
            desc = file_info.get('description', '').lower()
            file_type = file_info.get('type', '').lower()
            category = file_info.get('category', '').lower()
            keywords = [kw.lower() for kw in file_info.get('keywords', [])]

            # Match against query
            if (query_lower in title or
                query_lower in desc or
                query_lower in file_type or
                query_lower in category or
                any(query_lower in kw for kw in keywords)):

                # Determine tier label from tier field or path
                tier_name = file_info.get('tier', '')
                if tier_name.startswith('ui/'):
                    tier_label = '📘 UI'
                else:
                    tier_label = tier_labels.get(tier_name, '📙 Other')

                results.append((
                    tier_label,
                    file_info.get('path', ''),
                    file_info.get('title', ''),
                    file_info.get('description', '')
                ))

        return results

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
            self.footer.set_text(" ↑/↓=Scroll →/←=Next/Prev Link Enter=Follow /=Search U=Back ESC/Q=Exit ")
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
            self._set_content(result_text)
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

            self._set_content(result_text)
            self.link_positions = [link[0] for link in self.current_links]
            self.current_link_index = 0
            self.search_mode = False
            self.footer.set_text(" ↑/↓=Scroll Tab=Next Result Enter=Open /=New Search ESC=Back ")

        self.title.set_text(f" Search: {self.search_query} ")

    def _cancel_search(self):
        """Cancel search and return to previous topic."""
        self.search_mode = False
        self.search_query = ""
        self.footer.set_text(" ↑/↓=Scroll →/←=Next/Prev Link Enter=Follow /=Search U=Back ESC/Q=Exit ")
        self._load_topic(self.current_topic)

    def _set_content(self, text_markup):
        """Set content in the listbox, converting markup to line widgets."""
        # Convert markup list into separate line widgets for proper scrolling
        # text_markup is a list of strings and (attr, text) tuples

        if not isinstance(text_markup, list):
            text_markup = [text_markup]

        # Collect line data by processing markup
        current_line = []
        all_lines = []

        for item in text_markup:
            if isinstance(item, tuple):
                # (attr, text) tuple
                text = item[1]
                # Check for newlines within the text
                if '\n' in text:
                    parts = text.split('\n')
                    for i, part in enumerate(parts):
                        if part:
                            current_line.append((item[0], part))
                        if i < len(parts) - 1:  # Not the last part
                            all_lines.append(current_line if current_line else [('', '')])
                            current_line = []
                else:
                    current_line.append(item)
            else:
                # Plain string
                text = str(item)
                if '\n' in text:
                    parts = text.split('\n')
                    for i, part in enumerate(parts):
                        if part:
                            current_line.append(part)
                        if i < len(parts) - 1:
                            all_lines.append(current_line if current_line else [''])
                            current_line = []
                else:
                    if text:
                        current_line.append(text)

        # Add final line if non-empty
        if current_line:
            all_lines.append(current_line)

        # Create Text widgets for each line
        line_widgets = []
        for line_markup in all_lines:
            if not line_markup:
                line_markup = ['']
            text_widget = urwid.Text(line_markup)
            line_widgets.append(text_widget)

        # Update walker
        self.walker[:] = line_widgets if line_widgets else [urwid.Text('')]

    def _refresh_display(self):
        """Re-render the current display with updated link highlighting."""
        # Re-render using cached lines (preserves scroll position)
        if self.current_rendered_lines:
            text_markup = self._create_text_markup_with_links(
                self.current_rendered_lines,
                self.current_link_index
            )
            self._set_content(text_markup)

    def _create_text_markup_with_links(self, lines: List[str], current_link_index: int = 0) -> List:
        """
        Convert plain text lines to urwid markup with link highlighting.

        Links are marked with [text] in the rendered output. This method
        converts them to use the 'link' attribute for highlighting, and
        the 'focus' attribute for the currently selected link.

        Args:
            lines: List of plain text lines with links marked as [text]
            current_link_index: Index of the currently selected link (for highlighting)

        Returns:
            Urwid text markup (list of tuples or strings)
        """
        import re

        markup = []
        link_counter = 0  # Track which link we're on

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

                # Add the link with appropriate attribute
                link_text = match.group(0)  # Keep the brackets

                # Use 'focus' attribute for current link, 'link' for others
                if link_counter == current_link_index:
                    line_markup.append(('focus', link_text))
                else:
                    line_markup.append(('link', link_text))

                link_counter += 1
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
            self._set_content(error_text)
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

            # Cache the rendered lines for later re-rendering
            self.current_rendered_lines = lines

            # Create text markup with link highlighting
            text_markup = self._create_text_markup_with_links(lines, self.current_link_index)

            # Set the content
            self._set_content(text_markup)

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
            self._set_content(error_text)
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
            # Close help by calling the callback
            if self.on_close:
                self.on_close()
            return None

        elif key == '/':
            # Enter search mode
            self._show_search_prompt()
            return None

        elif key == 'enter':
            # Follow current link
            if self.current_links and self.current_link_index < len(self.current_links):
                _, _, target = self.current_links[self.current_link_index]

                # Check if target is already an absolute path (from search results)
                # Absolute paths don't start with . or .., or start with common/
                if not target.startswith('.') or target.startswith('common/'):
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

        elif key in ('tab', 'right'):
            # Move to next link
            if self.link_positions:
                self.current_link_index = (self.current_link_index + 1) % len(self.link_positions)
                # Re-render to update highlighting
                self._refresh_display()
                # Scroll to make the link visible with padding
                link_line = self.link_positions[self.current_link_index]
                if link_line < len(self.walker):
                    # Set alignment first, then focus to trigger scroll
                    self.listbox.set_focus_valign('middle')
                    self.listbox.set_focus(link_line)
                    # Force invalidate to ensure redraw
                    self.listbox._invalidate()
                return None

        elif key in ('shift tab', 'left'):
            # Move to previous link
            if self.link_positions:
                self.current_link_index = (self.current_link_index - 1) % len(self.link_positions)
                # Re-render to update highlighting
                self._refresh_display()
                # Scroll to make the link visible with padding
                link_line = self.link_positions[self.current_link_index]
                if link_line < len(self.walker):
                    # Set alignment first, then focus to trigger scroll
                    self.listbox.set_focus_valign('middle')
                    self.listbox.set_focus(link_line)
                    # Force invalidate to ensure redraw
                    self.listbox._invalidate()
                return None

        # Pass other keys to listbox for scrolling
        return super().keypress(size, key)
