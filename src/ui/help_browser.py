"""
Help browser for curses UI with Info-style navigation.

Provides:
- Up/Down scrolling
- Enter to follow links
- U to go up to parent topic
- N/P for next/previous topic
- Q/ESC to exit help
"""

import curses
import os
from typing import List, Tuple, Optional
from pathlib import Path
from .markdown_renderer import MarkdownRenderer


class HelpBrowser:
    """Info-style help browser for Markdown documentation."""

    def __init__(self, stdscr, help_root: str):
        """
        Initialize help browser.

        Args:
            stdscr: The curses screen
            help_root: Path to help documentation root (e.g., "docs/help")
        """
        self.stdscr = stdscr
        self.help_root = Path(help_root)
        self.renderer = MarkdownRenderer()

        # Navigation state
        self.history = []  # Stack of (path, scroll_pos) for back navigation
        self.current_path = None
        self.current_lines = []
        self.current_links = []
        self.scroll_pos = 0
        self.cursor_line = 0  # Which line the cursor is on (for link selection)

        # Display window (we'll create a pad for scrolling)
        self.height, self.width = stdscr.getmaxyx()
        self.help_win = curses.newpad(1000, self.width - 2)  # Large pad for content

    def show_help(self, relative_path: str = "index.md") -> None:
        """
        Show a help topic and enter navigation loop.

        Args:
            relative_path: Path relative to help_root (e.g., "index.md")
        """
        self._load_topic(relative_path)
        self._navigation_loop()

    def _load_topic(self, relative_path: str) -> bool:
        """Load and render a help topic."""
        full_path = self.help_root / relative_path

        if not full_path.exists():
            self.current_lines = [
                "Error: Help topic not found",
                "",
                f"Path: {relative_path}",
                "",
                "Press Q or ESC to exit help."
            ]
            self.current_links = []
            return False

        # Read and render the Markdown
        with open(full_path, 'r') as f:
            markdown = f.read()

        self.current_lines, self.current_links = self.renderer.render(markdown)
        self.current_path = relative_path
        self.scroll_pos = 0

        # Set cursor to first link, or line 0 if no links
        if self.current_links:
            self.cursor_line = self.current_links[0][0]  # First link's line number
        else:
            self.cursor_line = 0

        return True

    def _navigation_loop(self) -> None:
        """Main navigation loop."""
        while True:
            self._draw()
            key = self.stdscr.getch()

            if key == ord('q') or key == ord('Q') or key == 27:  # Q or ESC
                break

            elif key == curses.KEY_DOWN:
                self._scroll_down()

            elif key == curses.KEY_UP:
                self._scroll_up()

            elif key == ord(' '):  # Space - page down
                self._page_down()

            elif key == ord('b') or key == ord('B'):  # Page up
                self._page_up()

            elif key == 10:  # Enter - follow link
                self._follow_link()

            elif key == ord('u') or key == ord('U'):  # Go up to parent
                self._go_up()

            elif key == ord('n') or key == ord('N'):  # Next topic
                self._next_topic()

            elif key == ord('p') or key == ord('P'):  # Previous topic
                self._prev_topic()

    def _draw(self) -> None:
        """Draw the help content."""
        self.stdscr.clear()

        # Draw title bar
        title = f" MBASIC Help: {self.current_path or 'index'} "
        self.stdscr.addstr(0, 0, title[:self.width], curses.A_REVERSE)

        # Draw content area
        visible_height = self.height - 3  # Leave room for title and status
        for i in range(visible_height):
            line_idx = self.scroll_pos + i
            if line_idx >= len(self.current_lines):
                break

            line = self.current_lines[line_idx]

            # Highlight if this line contains a link
            is_link_line = any(link[0] == line_idx for link in self.current_links)

            # Truncate line to fit
            display_line = line[:self.width - 2]

            try:
                if is_link_line and line_idx == self.cursor_line:
                    # Highlight current link
                    self.stdscr.addstr(i + 1, 1, display_line, curses.A_REVERSE)
                elif is_link_line:
                    # Show links in a different color if available
                    self.stdscr.addstr(i + 1, 1, display_line, curses.A_UNDERLINE)
                else:
                    self.stdscr.addstr(i + 1, 1, display_line)
            except curses.error:
                # Ignore errors from trying to write to last line
                pass

        # Draw status bar
        status = " ↑/↓=Scroll Space=Page Enter=Link U=Up N/P=Next/Prev Q=Exit "
        try:
            self.stdscr.addstr(self.height - 1, 0, status[:self.width], curses.A_REVERSE)
        except curses.error:
            pass

        self.stdscr.refresh()

    def _scroll_down(self) -> None:
        """Scroll down one line and move to next link."""
        # Find next link after current cursor
        next_link = None
        for link_line, _, _ in self.current_links:
            if link_line > self.cursor_line:
                next_link = link_line
                break

        if next_link is not None:
            # Move cursor to next link
            self.cursor_line = next_link
            # Scroll to make it visible if needed
            visible_end = self.scroll_pos + (self.height - 3)
            if self.cursor_line >= visible_end:
                self.scroll_pos = self.cursor_line - (self.height - 4)
        else:
            # No more links, just scroll
            max_scroll = max(0, len(self.current_lines) - (self.height - 3))
            if self.scroll_pos < max_scroll:
                self.scroll_pos += 1
                self.cursor_line = self.scroll_pos

    def _scroll_up(self) -> None:
        """Scroll up one line and move to previous link."""
        # Find previous link before current cursor
        prev_link = None
        for link_line, _, _ in reversed(self.current_links):
            if link_line < self.cursor_line:
                prev_link = link_line
                break

        if prev_link is not None:
            # Move cursor to previous link
            self.cursor_line = prev_link
            # Scroll to make it visible if needed
            if self.cursor_line < self.scroll_pos:
                self.scroll_pos = self.cursor_line
        else:
            # No more links, just scroll
            if self.scroll_pos > 0:
                self.scroll_pos -= 1
                self.cursor_line = self.scroll_pos

    def _page_down(self) -> None:
        """Scroll down one page."""
        page_size = self.height - 3
        max_scroll = max(0, len(self.current_lines) - page_size)
        self.scroll_pos = min(self.scroll_pos + page_size, max_scroll)
        self._adjust_cursor()

    def _page_up(self) -> None:
        """Scroll up one page."""
        page_size = self.height - 3
        self.scroll_pos = max(0, self.scroll_pos - page_size)
        self._adjust_cursor()

    def _adjust_cursor(self) -> None:
        """Adjust cursor to be on a visible link if possible."""
        visible_start = self.scroll_pos
        visible_end = self.scroll_pos + (self.height - 3)

        # Find first link in visible area
        for link_line, _, _ in self.current_links:
            if visible_start <= link_line < visible_end:
                self.cursor_line = link_line
                return

        # No links visible, just use first visible line
        self.cursor_line = visible_start

    def _follow_link(self) -> None:
        """Follow the link at the cursor position."""
        # Find link at cursor line
        for link_line, link_text, link_target in self.current_links:
            if link_line == self.cursor_line:
                # Save current position to history
                if self.current_path:
                    self.history.append((self.current_path, self.scroll_pos))

                # Load the new topic
                self._load_topic(link_target)
                return

        # If no link at cursor, find next link and move cursor there
        for link_line, _, _ in self.current_links:
            if link_line > self.cursor_line:
                self.cursor_line = link_line
                # Scroll to make it visible
                if self.cursor_line >= self.scroll_pos + (self.height - 3):
                    self.scroll_pos = self.cursor_line - (self.height - 4)
                return

    def _go_up(self) -> None:
        """Go up to parent topic or back in history."""
        if self.history:
            # Go back to previous topic
            prev_path, prev_scroll = self.history.pop()
            self._load_topic(prev_path)
            self.scroll_pos = prev_scroll
        else:
            # Go to parent directory's index
            if self.current_path and '/' in self.current_path:
                parent_dir = '/'.join(self.current_path.split('/')[:-1])
                parent_index = f"{parent_dir}/index.md" if parent_dir else "index.md"
                self._load_topic(parent_index)
            else:
                # Already at root
                pass

    def _next_topic(self) -> None:
        """Navigate to next topic at same level."""
        # This would require a table of contents structure
        # For now, just scroll to next link
        for link_line, _, _ in self.current_links:
            if link_line > self.cursor_line:
                self.cursor_line = link_line
                # Scroll to make it visible
                if self.cursor_line >= self.scroll_pos + (self.height - 3):
                    self.scroll_pos = self.cursor_line - (self.height - 4)
                return

    def _prev_topic(self) -> None:
        """Navigate to previous topic at same level."""
        # Find previous link
        prev_link = None
        for link_line, _, _ in self.current_links:
            if link_line >= self.cursor_line:
                break
            prev_link = link_line

        if prev_link is not None:
            self.cursor_line = prev_link
            # Scroll to make it visible
            if self.cursor_line < self.scroll_pos:
                self.scroll_pos = self.cursor_line
