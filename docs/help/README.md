# MBASIC In-UI Help System

This directory contains the help documentation accessible from within MBASIC user interfaces.

## Structure

### `/common` - Shared Help Content
General help documentation available to all UI backends:
- Language reference
- Statement and function documentation
- General usage guides
- Examples

This content is UI-agnostic and covers BASIC language features and general interpreter usage.

### `/ui/cli` - CLI Backend Help
Help specific to the command-line interface (CLI) backend.

### `/ui/curses` - Curses/Urwid Backend Help
Help specific to the full-screen terminal UI (urwid):
- Keyboard commands
- Editor features
- Navigation
- UI-specific features

### `/ui/tk` - Tkinter GUI Backend Help
Help specific to the graphical Tkinter interface.

### `/ui/visual` - Visual Backend Help
Help specific to the visual backend.

## Help System Design

UIs should:
1. Load common help content for all users
2. Add UI-specific help sections for their backend
3. Provide navigation between common and UI-specific topics
4. Support markdown rendering or convert to appropriate format

## Entry Points

- **Common Help**: [common/index.md](common/index.md)
- **CLI Help**: [ui/cli/index.md](ui/cli/index.md)
- **Curses Help**: [ui/curses/index.md](ui/curses/index.md)
- **Tk Help**: [ui/tk/index.md](ui/tk/index.md)
- **Visual Help**: [ui/visual/index.md](ui/visual/index.md)
