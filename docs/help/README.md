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

### `/ui/curses` - Curses Backend Help
Help specific to the full-screen terminal UI:
- Keyboard commands
- Editor features
- Navigation
- UI-specific features

### `/ui/tk` - Tkinter GUI Backend Help
Help specific to the graphical Tkinter interface.

### `/ui/web` - Web UI Backend Help
Help specific to the web browser interface.

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
- **Web Help**: [ui/web/index.md](ui/web/index.md)

**Note:** MBASIC supports four UI backends: CLI (command-line interface), Curses (terminal full-screen), Tk (desktop GUI), and Web (browser-based). The help system provides both common content (shared across all backends) and UI-specific documentation for each interface. Help content is built using MkDocs and served locally at `http://localhost/mbasic_docs` for the Tk and Web UIs, while the CLI and Curses UIs use built-in markdown rendering. (Legacy code may reference `http://localhost:8000`, which is deprecated in favor of the `/mbasic_docs` path.)
