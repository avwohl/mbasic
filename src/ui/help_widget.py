"""
Urwid-based help browser widget for navigating markdown documentation.

Provides:
- Up/Down scrolling through help content
- Enter to follow links
- ESC/Q to exit
- Navigation breadcrumbs
"""

import urwid
from pathlib import Path
from typing import List, Tuple, Optional
from .markdown_renderer import MarkdownRenderer


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

        # Navigation state
        self.current_topic = initial_topic
        self.history = []  # Stack of previous topics
        self.current_links = []  # List of (line_num, text, target) for current page
        self.link_positions = []  # List of line numbers with links (for navigation)
        self.current_link_index = 0  # Which link is selected

        # Create display widgets
        self.text_widget = urwid.Text("")
        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker([self.text_widget]))

        # Create frame with title and footer
        self.title = urwid.Text("")
        self.footer = urwid.Text(" ↑/↓=Scroll Tab=Next Link Enter=Follow Link U=Back ESC/Q=Exit ")

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

            lines, links = self.renderer.render(markdown)

            # Create text markup - just use plain text for now
            # TODO: Add link highlighting with urwid markup
            text_markup = '\n'.join(lines)

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

        if key in ('q', 'Q', 'esc'):
            # Signal to close help
            return 'esc'

        elif key == 'enter':
            # Follow current link
            if self.current_links and self.current_link_index < len(self.current_links):
                _, _, target = self.current_links[self.current_link_index]

                # Resolve relative path
                current_dir = str(Path(self.current_topic).parent)
                if current_dir == '.':
                    new_topic = target
                else:
                    new_topic = str(Path(current_dir) / target)

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
