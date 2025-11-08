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
        # Note: Help navigation keys are HARDCODED (not loaded from keybindings JSON) to avoid
        # circular dependency issues. The help widget uses fixed keys (U for back, / for search,
        # ESC/Q to exit) that work regardless of user keybinding customization.
        #
        # Note: HelpMacros (instantiated below) DOES load keybindings from JSON, but only for
        # macro expansion in help content ({{kbd:action}} substitution). The help widget's
        # own navigation doesn't consult those loaded keybindings - it uses hardcoded keys.
        #
        # MAINTENANCE: If help navigation keys change, update:
        # 1. All footer text assignments (search for 'self.footer' in this file - multiple locations):
        #    - Initial footer (line ~73 below)
        #    - _cancel_search() around line ~166
        #    - _execute_search() around lines ~185, ~204, ~212
        #    - _start_search() around line ~159
        #    - keypress() search mode around lines ~444, ~448
        # 2. The keypress() method (handle_key mapping around line 150+)
        # 3. Help documentation that mentions these keys
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
        # Note: Tier labels are determined from tier_labels dict ('language', 'mbasic'),
        # startswith('ui/') check for UI tiers ('ui/curses', 'ui/tk'), or '📙 Other' fallback.
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

    def _set_content(self, line_markups):
        """Set content in the listbox, converting line markups to line widgets."""
        # line_markups is a list of line markups (each line is a list of strings/tuples)

        if not isinstance(line_markups, list):
            line_markups = [line_markups]

        # If first element is not a list, it's old format (flat markup) - wrap it
        if line_markups and not isinstance(line_markups[0], list):
            # Old format: single flat markup, treat as one line
            line_markups = [line_markups]

        # Create Text widgets for each line
        line_widgets = []
        for i, line_markup in enumerate(line_markups):
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
            text_markup, new_link_positions = self._create_text_markup_with_links(
                self.current_rendered_lines,
                self.current_links,
                self.current_link_index
            )
            # Update link positions with the accurate positions from markup creation
            self.link_positions = new_link_positions
            self._set_content(text_markup)

    def _create_text_markup_with_links(self, lines: List[str], links: List[tuple], current_link_index: int = 0) -> tuple[List[List], List[int]]:
        """
        Convert plain text lines to urwid markup with link highlighting.

        Links are marked with [text] or [text](url) in the rendered output. This method
        finds ALL such patterns for display/navigation using regex r'\\[([^\\]]+)\\](?:\\([^)]+\\))?',
        which matches both formats. The renderer's links list is used for target mapping when
        following links.

        Args:
            lines: List of plain text lines with links marked as [text] or [text](url)
            links: List of (line_number, link_text, target) tuples from the renderer (for targets)
            current_link_index: Index of the currently selected link (for highlighting)

        Returns:
            Tuple of (line markups, link_positions):
            - line markups: List of line markups (each line is a list of tuples/strings for urwid)
            - link_positions: List of line numbers where each link appears
        """
        import re

        all_line_markups = []
        link_positions = []  # Track which line each visual link is on
        link_counter = 0  # Track ALL visual links (not just renderer's links)

        for line_idx, line in enumerate(lines):
            # Find all [text] patterns (all visual links)
            # Match both [text] and [text](url) formats
            link_pattern = r'\[([^\]]+)\](?:\([^)]+\))?'

            # Split the line by links and build markup
            last_end = 0
            line_markup = []

            for match in re.finditer(link_pattern, line):
                # Add text before the link
                if match.start() > last_end:
                    line_markup.append(line[last_end:match.start()])

                # Add the link with appropriate attribute
                # Use just [text] part for display, not the (url) part
                link_text = f'[{match.group(1)}]'  # group(1) is the text inside brackets

                # Use 'focus' attribute for current link, 'link' for others
                if link_counter == current_link_index:
                    line_markup.append(('focus', link_text))
                else:
                    line_markup.append(('link', link_text))

                # Track which line this visual link is on
                link_positions.append(line_idx)
                link_counter += 1
                last_end = match.end()

            # Add remaining text after last link
            if last_end < len(line):
                line_markup.append(line[last_end:])

            # If line has no links, just add it as plain text
            if not line_markup:
                line_markup = [line]

            all_line_markups.append(line_markup)

        return (all_line_markups, link_positions)

    def _build_link_mapping(self, lines: List[str], links: List[tuple]):
        """
        Build a mapping from visual link indices (all [text] patterns) to
        renderer link indices (only links with targets).

        This allows us to show all [text] as clickable, but only follow the ones
        that have actual targets from the renderer.

        For links in headings like [text](url), we parse the URL directly since
        the renderer doesn't extract them.
        """
        import re

        # Build map of (line_num, link_text) -> renderer_link_idx
        renderer_links_map = {}
        for renderer_idx, (line_num, link_text, _) in enumerate(links):
            key = (line_num, link_text)
            renderer_links_map[key] = renderer_idx

        # Scan all visual links and build mapping
        self.visual_to_renderer_link = {}  # visual_idx -> renderer_idx or None
        self.visual_link_urls = {}  # visual_idx -> url (for [text](url) format)
        visual_idx = 0

        for line_idx, line in enumerate(lines):
            # Match both [text] and [text](url) formats, capturing the URL if present
            link_pattern = r'\[([^\]]+)\](?:\(([^)]+)\))?'
            for match in re.finditer(link_pattern, line):
                link_text = match.group(1)  # Text without brackets
                link_url = match.group(2)   # URL if present (None otherwise)
                key = (line_idx, link_text)

                if key in renderer_links_map:
                    # This visual link has a target from the renderer
                    self.visual_to_renderer_link[visual_idx] = renderer_links_map[key]
                else:
                    # This visual link has no renderer target
                    self.visual_to_renderer_link[visual_idx] = None

                    # But if it has a URL in [text](url) format, save it
                    if link_url:
                        self.visual_link_urls[visual_idx] = link_url

                visual_idx += 1

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

            # Store links first
            self.current_links = links
            self.current_link_index = 0

            # Create text markup with link highlighting using the renderer's link info
            text_markup, link_positions = self._create_text_markup_with_links(
                lines,
                links,
                self.current_link_index
            )

            # Set the content
            self._set_content(text_markup)

            # Store positions from markup creation
            self.link_positions = link_positions

            # Build a mapping from visual link index to renderer link index
            # This handles cases where some [text] patterns don't have targets
            self._build_link_mapping(lines, links)

            # Scroll to top of the document
            if len(self.walker) > 0:
                self.listbox.set_focus(0)

            # If there's a first link, make sure it's visible (but don't scroll to it, keep at top)
            # This ensures the highlight is in the viewport
            # Actually, just leave at top - user can press right arrow to move to first link if needed

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
            # Follow current link - map visual link index to renderer link index
            if hasattr(self, 'visual_to_renderer_link') and self.current_link_index in self.visual_to_renderer_link:
                renderer_idx = self.visual_to_renderer_link[self.current_link_index]

                # Check if this visual link has a target
                if renderer_idx is None:
                    # No renderer target, but check if we have a direct URL from [text](url)
                    if hasattr(self, 'visual_link_urls') and self.current_link_index in self.visual_link_urls:
                        target = self.visual_link_urls[self.current_link_index]
                    else:
                        # Truly decorative link with no target, ignore
                        return None
                else:
                    # Get target from renderer link
                    if renderer_idx < len(self.current_links):
                        _, _, target = self.current_links[renderer_idx]
                    else:
                        return None
            else:
                # Fallback to old behavior if mapping not available
                return None

            # Check if target is already an absolute path (from search results)
            # Absolute paths start with common/ or ui/
            if target.startswith('common/') or target.startswith('ui/'):
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
                # Scroll to make the link visible and centered
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

        elif key == ' ':
            # Space key scrolls down one page (like browsers)
            return super().keypress(size, 'page down')

        # Pass other keys to listbox for scrolling
        return super().keypress(size, key)
