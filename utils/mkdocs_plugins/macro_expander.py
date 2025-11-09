"""
MkDocs plugin to expand {{kbd:...}} and other macros in help documentation.

This plugin preprocesses markdown files before mkdocs builds them,
replacing macros like {{kbd:find:curses}} with actual keyboard shortcuts.
"""

import sys
from pathlib import Path

# Add src to path for importing HelpMacros
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from src.ui.help_macros import HelpMacros


class MacroExpanderPlugin(BasePlugin):
    """Expands help system macros during mkdocs build."""

    config_scheme = (
        ('ui_name', config_options.Type(str, default='curses')),
    )

    def __init__(self):
        super().__init__()
        self.macro_expander = None

    def on_config(self, config, **kwargs):
        """Initialize macro expander with UI name."""
        ui_name = self.config.get('ui_name', 'curses')
        docs_dir = Path(config['docs_dir'])

        # HelpMacros expects help root, which is docs/ in our case
        self.macro_expander = HelpMacros(ui_name, str(docs_dir))
        return config

    def on_page_markdown(self, markdown, page, config, files):
        """Expand macros in markdown content before processing."""
        if not self.macro_expander:
            return markdown

        # Only expand macros in help/ directory files
        if page.file.src_path.startswith('help/'):
            return self.macro_expander.expand(markdown)

        return markdown
