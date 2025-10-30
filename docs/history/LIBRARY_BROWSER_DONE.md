# Library Browser Feature - DONE

✅ **Status:** COMPLETE - Games library fully implemented and integrated (2025-10-30)

## Overview

Add a library browser feature that allows users to browse and load example BASIC programs, games, and utilities from within the UI. Implemented using static HTML documentation approach instead of API.

## Motivation

- **372 BASIC programs** already exist in the `basic/` directory
- Users (especially beginners) would benefit from discovering example programs
- Games like blackjack, baccarat, calendar utilities, etc. are immediately runnable
- Makes the UI more discoverable and educational
- Web UI especially benefits since users can't easily browse the server filesystem

## Current State

### Existing Programs

The repository contains 372+ BASIC programs including:
- **Games**: bacarrat.bas, blkjk.bas, tankie.bas, othello.bas
- **Utilities**: calendar.bas, convert.bas, diary.bas, budget.bas
- **Educational**: mathtest.bas, benchmk.bas, sample*.bas
- **Technical**: Various RBS, RBB, and communication programs

### Current Load Mechanisms

Each UI has its own file loading:
- **CLI**: LOAD "filename" command
- **Curses**: Ctrl+L opens file browser dialog
- **Tkinter**: File → Open menu, file browser dialog
- **Web**: Open button uploads file from user's computer (cannot access server files)

## Implemented Solution

### Architecture (Static HTML Approach)

**Documentation-Based:**
1. Create `docs/library/games.json` with metadata pointing to source files
2. Use `utils/build_library_docs.py` to generate static HTML
3. Generated files go to `docs/library/games/`:
   - `index.md` - Main page with game descriptions
   - `*.bas` files - Copied from source during build
4. Published to web docs site (http://localhost/mbasic_docs)

**UI Integration:**

**Web UI (✅ Done):**
- Added "Games Library" menu item to Help menu
- Opens library at `library/games/` in browser
- Uses existing `open_help_in_browser()` infrastructure

**Tkinter UI (✅ Done):**
- Added "Games Library" menu item to Help menu
- Opens library in default browser

**Build Process:**
- `utils/build_library_docs.py` generates docs from metadata
- Copies .bas files from source (always current version)
- Generated during doc build / deployment

### Advantages of Static Approach

- ✅ No API needed - just static files
- ✅ Reuses existing web deployment (MkDocs)
- ✅ Works with existing file upload in Web UI
- ✅ Can be browsed independently
- ✅ Search works automatically (MkDocs feature)
- ✅ .bas files always current (copied during build)
- ✅ No security concerns (read-only static files)

## Implementation (Completed)

### Phase 1: Games Library (✅ Done)
- [x] Created `docs/library/games.json` with metadata
- [x] Curated 5 games from existing collection:
  - blackjack.bas (from basic/blkjk.bas)
  - spacewar.bas (from basic/spacewar.bas)
  - nim.bas (from basic/bas_tests/nim.bas)
  - poker.bas (from basic/bas_tests/poker.bas)
  - battle.bas (from basic/bas_tests/battle.bas)

### Phase 2: Build System (✅ Done)
- [x] Created `utils/build_library_docs.py`
- [x] Generates `docs/library/games/index.md` from metadata
- [x] Copies .bas files from source during build
- [x] Auto-generates download links

### Phase 3: UI Integration (✅ Done)
- [x] Web UI: Added "Games Library" to Help menu
- [x] Tkinter UI: Added "Games Library" to Help menu
- [x] Both open library at `library/games/` in browser

### Phase 4: Build Integration (✅ Done)
- [x] Integrated into `utils/build_docs.py`
- [x] Added to GitHub Actions workflow
- [x] Auto-builds before mkdocs deployment
- [x] Triggers on .bas file changes

### Future Enhancements (Optional)
- [ ] Add more categories (demos, tutorials, utilities)
- [ ] Add more games from the 372+ available
- [ ] Curses: Add Ctrl+E examples browser (optional)
- [ ] CLI: Add EXAMPLES command (optional)

## Example Programs to Include

### Games (Immediate Fun)
- Blackjack (blkjk.bas)
- Baccarat (bacarrat.bas)
- Tankie (tankie.bas) - if it's a tank game

### Tutorials (Learning)
- Hello World (create simple one if not exists)
- FOR loop examples
- INPUT/PRINT examples
- Array examples
- File I/O examples

### Utilities (Useful Tools)
- Calendar (calendar.bas, calendr5.bas)
- Unit converter (convert.bas)
- Math test (mathtest.bas)
- Benchmark (benchmk.bas)

### Demos (Visual/Interesting)
- Astronomy calculator (astrnmy2.bas)
- Big calendar printer (bigcal2.bas)
- Character frequency analyzer (charfreq.bas)

## Testing Criteria

- [ ] All library programs parse without errors
- [ ] All library programs run to completion (or clean exit)
- [ ] Library browser shows all categories
- [ ] Clicking program loads it correctly
- [ ] Confirmation dialog appears before replacing current program
- [ ] Server endpoints secure (no path traversal)
- [ ] Works on all supported browsers (Web UI)
- [ ] Documentation is clear and complete

## Related Files

- `src/ui/web/nicegui_backend.py` - Web UI implementation
- `src/ui/tk_ui.py` - Tkinter UI implementation
- `src/ui/curses_ui.py` - Curses UI implementation
- `src/cli.py` - CLI command handling
- `basic/` - Current program storage
- `docs/help/ui/*/` - UI-specific documentation

## Future Enhancements (Post-MVP)

- User-contributed programs (upload to library)
- Program rating/favorites system
- Search/filter programs by keyword
- "Run in sandbox" button to preview without loading
- Syntax highlighting in preview
- Export library to static HTML catalog
- Download entire library as ZIP

## Priority

**MEDIUM** - Nice-to-have feature that improves user experience significantly, especially for beginners and the Web UI. Not blocking any core functionality.

## Estimated Effort

**8-12 hours total** (spread across phases)

## Dependencies

- No blocking dependencies
- Web UI already has dialog/menu infrastructure
- File serving already works for Open button
- Just needs organization and UI integration

## Success Metrics

- Users can discover and load example programs without documentation
- At least 20 high-quality examples available
- Feature documented in all UI help guides
- No security vulnerabilities in file serving
- Positive user feedback on discoverability

---

**Created:** 2025-10-29
**Last Updated:** 2025-10-29
