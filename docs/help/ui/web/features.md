# Web UI Features

**IMPORTANT:** This document describes both **currently implemented features** and **planned enhancements**. Many advanced features described below are **planned for future releases** and not yet implemented.

**Status Indicators:**
- **(Currently Implemented)** - Feature is available now
- **(Planned)** - Feature is not yet available, planned for future release
- **(Partially Implemented)** - Some aspects work, others are planned
- No marker - Feature section contains both implemented and planned features (check subsections)

For a quick overview of currently implemented features only, see [Getting Started](getting-started.md).

Complete reference of features available and planned for the MBASIC Web UI.

## Editor Features

### Syntax Highlighting

**Currently Implemented:**
- **Keywords** in blue (PRINT, FOR, IF)
- **Strings** in green ("Hello")
- **Numbers** in orange (42, 3.14)
- **Comments** in gray (REM, ')
- **Line numbers** in purple
- **Operators** in red (+, -, *, /)

### Code Intelligence (Planned)

**Auto-completion (Planned):**
- BASIC keywords
- Variable names
- Function names
- Line numbers

**Syntax Checking (Planned):**
- Real-time validation
- Error underlining
- Hover for details
- Quick fixes

**Code Folding (Planned):**
- Collapse/expand FOR loops
- Hide/show subroutines
- Fold long IF blocks

### Line Management

**Smart Line Numbering (Currently Implemented):**
- Auto-increment by configurable step (default 10)
- Manual line number entry supported

**Line Operations (Planned):**
- Select multiple lines
- Bulk delete
- Copy with line numbers
- Paste with renumbering
- Insert with intermediate numbers
- Automatic renumbering
- Duplicate detection

### Search and Replace (Planned)

**Find ({{kbd:find:web}}) (Planned):**
- Search in editor
- Case sensitive option
- Whole word option
- Regular expressions

**Replace ({{kbd:replace:web}}) (Planned):**
- Replace single
- Replace all
- Preview changes

## File Management

### Local Storage

**Currently Implemented:**
- Program content stored in Python server memory (session-only, lost on page refresh)
- Recent files list (filenames only) stored in browser localStorage (persists across sessions)
- Editor settings stored in browser localStorage (persists across sessions)

**Automatic Saving (Planned):**
- Saves programs to browser localStorage for persistence
- Every 30 seconds
- On significant changes
- Before running

**Session Recovery (Planned):**
- Restores last program from browser storage
- Recovers after crash or page refresh
- Maintains breakpoints
- Preserves variables

### File Operations

**Currently Implemented:**
- Load .BAS files from local filesystem
- Save/download programs as .BAS files

**Open Files (Planned):**
- Click to browse
- Drag and drop
- Recent files list
- Multiple format support

**Save Options (Currently Implemented):**
- Download as .BAS file

### Format Support

**Input Formats (Currently Implemented):**
- .BAS files
- .TXT files
- ASCII text

**Output Formats (Currently Implemented):**
- Standard .BAS

## Program Execution

### Run Modes

**Normal Run (Currently Implemented):**
- Full speed execution
- Output to panel
- Error handling
- Input prompts

**Debug Mode (Partially Implemented):**
- Basic breakpoint support (via Run menu)
- Step execution ({{kbd:step:web}}, {{kbd:step_line:web}})
- Basic variable inspection (via Run → Show Variables)
- Call stack display (via Run → Show Stack)
- Advanced debugging features (planned: conditional breakpoints, watch expressions, etc.)

**Trace Mode (Planned):**
- Line-by-line output
- Show all statements
- Variable changes
- Execution path

### Input/Output

**Output Panel (Currently Implemented):**
- Scrollable output
- Clear button
- Copy text

**Export log (Planned)**

**Input Handling (Currently Implemented):**
- Modal input dialog for INPUT statements
- Basic validation

**Advanced Input (Planned):**
- Inline input field
- Default values
- Custom validators

### Error Handling

**Error Display (Currently Implemented):**
- Error message display
- Line number indication

**Advanced Error Display (Planned):**
- Line highlighting
- Stack trace
- Quick fix suggestions

**Error Recovery (Planned):**
- Continue option
- Edit and retry
- Skip statement
- Reset program

## Debugging Tools

### Breakpoints

**Currently Implemented:**
- Line breakpoints (toggle via Run menu)
- Clear all breakpoints
- Visual indicators in editor

**Management:**
- Toggle via Run menu → Toggle Breakpoint
- Clear all via Run menu → Clear All Breakpoints
- Persistent within session

### Variable Inspector

**Currently Implemented:**
- Basic variable viewing via Debug menu

**Display Features (Planned):**
- Tree view
- Type indicators
- Array expansion
- Search/filter

**Editing (Planned):**
- Double-click edit
- Type validation
- Immediate update

### Execution Control

**Currently Implemented:**
- Run ({{kbd:run:web}})
- Continue ({{kbd:continue:web}})
- Step statement ({{kbd:step:web}})
- Step line ({{kbd:step_line:web}})
- Stop ({{kbd:stop:web}})

**Advanced Controls (Planned):**
- Step over (planned for future release)
- Step into (planned for future release)
- Step out (planned for future release)
- Run to cursor (planned for future release)
- Pause (planned for future release)
- Restart (planned for future release)

## User Interface

### Layout Options

**Currently Implemented:**
- Basic panel layout (editor, output, menu)

**Panel Configuration (Planned):**
- Resizable panels
- Hide/show panels
- Horizontal/vertical split
- Full-screen mode

**Themes (Planned):**
- Light mode
- Dark mode
- High contrast
- Custom colors

### Customization

**Currently Implemented:**
- Auto-numbering settings (via Settings dialog)
- Line number increment configuration

**Editor Settings (Planned):**
- Font size
- Font family
- Tab size
- Line wrapping

**Behavior Settings (Planned):**
- Auto-save interval
- Syntax check delay
- Execution speed
- Debug options

### Accessibility

**Keyboard Navigation (Partially Implemented):**
- Basic keyboard shortcuts (see [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md))

**Keyboard Navigation (Planned):**
- Full keyboard control
- Customizable shortcuts
- Vim mode (optional)
- Screen reader support

**Visual Aids (Planned):**
- Zoom in/out
- High contrast
- Large fonts
- Focus indicators

## Advanced Features

### Session Management

**Note:** Collaboration features (sharing, collaborative editing, version control) are not currently implemented. Programs are stored locally in browser storage only.

### Performance (Planned)

**Optimization (Planned):**
- Lazy loading
- Virtual scrolling
- Web workers
- Efficient rendering

**Resource Management (Planned):**
- Memory monitoring
- CPU usage display
- Storage quotas
- Cache control

### Integration

**Browser APIs (Partially Implemented):**
- File system access (load/save files)
- localStorage (program storage)

**Browser APIs (Planned):**
- Clipboard access
- Notifications
- Fullscreen API

## Productivity Tools

### Templates (Planned)

**Program Templates (Planned):**
- Hello World
- Input example
- Loop examples
- Game templates

**Code Snippets (Planned):**
- Common patterns
- Error handling
- Input validation
- Utility functions

### Documentation

**Help Panel (Currently Implemented):**
- Access to documentation via Help menu
- Context-sensitive help

**Inline Help (Planned):**
- Hover documentation
- Parameter hints
- Example code
- Quick links

**Advanced Help (Planned):**
- Searchable docs
- Offline capable

### Testing (Planned)

**Test Support (Planned):**
- Test file detection
- Expected output
- Assertion checking
- Test runner

**Benchmarking (Planned):**
- Execution timing
- Performance metrics
- Memory usage
- Comparison tools

## Settings and Preferences

**Currently Implemented:**
See [Settings](settings.md) for currently available settings (auto-numbering, line increment).

### General Settings (Planned)

**Planned settings:**
```
☑ Auto-save enabled
  └─ Interval: 30 seconds
☑ Syntax checking
  └─ Delay: 500ms
☑ Auto-completion
☑ Show line numbers
☑ Word wrap
```

### Editor Preferences (Planned)

**Planned preferences:**
```
Font: Consolas, monospace
Size: 14px
Theme: Dark
Tab Size: 4
Insert Spaces: No
```

### Debug Preferences (Planned)

**Planned preferences:**
```
☑ Break on error
☐ Break on warning
☑ Show variable types
☑ Highlight current line
Execution Speed: Normal
```

### Advanced Options (Planned)

**Planned options:**
```
☑ Enable web workers
☑ Use localStorage
☐ Telemetry
Cache Size: 10MB
History Size: 50
```

## Mobile Support

**Currently Implemented:**
- Basic responsive layout
- Touch-friendly interface

### Touch Interface (Partially Implemented)

**Currently works:**
- Touch to place cursor
- Swipe to scroll
- Virtual keyboard support

**Planned:**
- Pinch to zoom
- Long press for context menu
- Touch gestures for debugging

### Responsive Design (Partially Implemented)

**Currently works:**
- Adapts to screen size
- Mobile-optimized layout
- Touch-friendly buttons

### Mobile Features (Planned)

**Planned:**
- Simplified interface
- Essential features only
- Optimized performance
- Reduced memory usage

## Security Features

### Sandboxing (Currently Implemented)

**Currently Implemented:**
- Isolated execution in browser
- No direct file system access (uses browser File API)
- No network access from BASIC programs
- Safe program execution

### Data Protection (Currently Implemented)

**Currently Implemented:**
- Local storage only (browser localStorage)
- No server uploads
- Data stays in browser

**Planned:**
- Encrypted storage
- Session isolation

### Privacy (Currently Implemented)

**Currently Implemented:**
- No tracking
- No analytics
- Local processing
- Data stays in browser

## Browser Requirements

### Minimum Requirements

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Recommended

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Required APIs

- localStorage
- IndexedDB
- Web Workers
- Clipboard API

## Known Limitations

### Browser Limits

- localStorage: 5-10MB
- Max file size: 10MB
- Stack depth: Browser dependent
- Execution timeout: 10 seconds

### Feature Limitations

- No file system access
- No network operations
- No binary data
- No external commands

### Performance Limits

- Large programs may be slow
- Many variables impact speed
- Complex calculations limited
- Graphics operations basic

## Troubleshooting

### Common Issues

**Program won't run:**
- Check syntax errors
- Verify line numbers
- Clear browser cache
- Check console errors

**Lost changes:**
- Check localStorage
- Use recovery option
- Check downloads
- Enable auto-save

**Performance problems:**
- Clear output panel
- Reduce program size
- Close other tabs
- Update browser

### Getting Help

- Press {{kbd:help:web}} for help
- Check documentation
- View examples
- Report issues on GitHub

## See Also

- [Getting Started](getting-started.md) - First steps
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Quick reference
- [Debugging Guide](debugging.md) - Debug features
- [Settings](settings.md) - Configuration options