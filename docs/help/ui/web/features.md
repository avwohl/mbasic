# Web UI Features

Complete reference of all features available in the MBASIC Web UI.

## Editor Features

### Syntax Highlighting

- **Keywords** in blue (PRINT, FOR, IF)
- **Strings** in green ("Hello")
- **Numbers** in orange (42, 3.14)
- **Comments** in gray (REM, ')
- **Line numbers** in purple
- **Operators** in red (+, -, *, /)

### Code Intelligence

**Auto-completion:**
- BASIC keywords
- Variable names
- Function names
- Line numbers

**Syntax Checking:**
- Real-time validation
- Error underlining
- Hover for details
- Quick fixes

**Code Folding:**
- Collapse/expand FOR loops
- Hide/show subroutines
- Fold long IF blocks

### Line Management

**Smart Line Numbering:**
- Auto-increment by 10
- Insert with intermediate numbers
- Automatic renumbering
- Duplicate detection

**Line Operations:**
- Select multiple lines
- Bulk delete
- Copy with line numbers
- Paste with renumbering

### Search and Replace

**Find (Ctrl+F):**
- Search in editor
- Case sensitive option
- Whole word option
- Regular expressions

**Replace (Ctrl+H):**
- Replace single
- Replace all
- Preview changes

## File Management

### Local Storage

**Automatic Saving:**
- Saves to browser storage
- Every 30 seconds
- On significant changes
- Before running

**Session Recovery:**
- Restores last program
- Recovers after crash
- Maintains breakpoints
- Preserves variables

### File Operations

**Open Files:**
- Click to browse
- Drag and drop
- Recent files list
- Multiple format support

**Save Options:**
- Save to browser
- Download as file
- Export to GitHub
- Share via link

### Format Support

**Input Formats:**
- .BAS files
- .TXT files
- Tokenized BASIC
- ASCII text

**Output Formats:**
- Standard .BAS
- Formatted text
- Tokenized format
- PDF export

## Program Execution

### Run Modes

**Normal Run:**
- Full speed execution
- Output to panel
- Error handling
- Input prompts

**Debug Mode:**
- Breakpoint support
- Step execution
- Variable inspection
- Call stack

**Trace Mode:**
- Line-by-line output
- Show all statements
- Variable changes
- Execution path

### Input/Output

**Output Panel:**
- Scrollable output
- Clear button
- Copy text
- Export log

**Input Handling:**
- Modal input dialog
- Inline input field
- Validation
- Default values

### Error Handling

**Error Display:**
- Line highlighting
- Error message
- Stack trace
- Quick fix suggestions

**Error Recovery:**
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

**Display Features:**
- Tree view
- Type indicators
- Array expansion
- Search/filter

**Editing:**
- Double-click edit
- Type validation
- Immediate update

### Execution Control

**Step Controls:**
- Step over (F10)
- Step into (F11)
- Step out (Shift+F11)
- Run to cursor

**Flow Control:**
- Continue (F5)
- Pause
- Stop (Shift+F5)
- Restart

## User Interface

### Layout Options

**Panel Configuration:**
- Resizable panels
- Hide/show panels
- Horizontal/vertical split
- Full-screen mode

**Themes:**
- Light mode
- Dark mode
- High contrast
- Custom colors

### Customization

**Editor Settings:**
- Font size
- Font family
- Tab size
- Line wrapping

**Behavior Settings:**
- Auto-save interval
- Syntax check delay
- Execution speed
- Debug options

### Accessibility

**Keyboard Navigation:**
- Full keyboard control
- Customizable shortcuts
- Vim mode (optional)
- Screen reader support

**Visual Aids:**
- Zoom in/out
- High contrast
- Large fonts
- Focus indicators

## Advanced Features

### Collaboration

**Sharing:**
- Share via link
- Read-only mode
- Collaborative editing
- Live output sharing

**Version Control:**
- Local history
- Snapshot saves
- Diff viewer

### Performance

**Optimization:**
- Lazy loading
- Virtual scrolling
- Web workers
- Efficient rendering

**Resource Management:**
- Memory monitoring
- CPU usage display
- Storage quotas
- Cache control

### Integration

**Browser APIs:**
- Clipboard access
- File system access
- Notifications
- Fullscreen API

**External Tools:**
- Export to GitHub
- Import from URL
- WebDAV support
- Cloud storage

## Productivity Tools

### Templates

**Program Templates:**
- Hello World
- Input example
- Loop examples
- Game templates

**Code Snippets:**
- Common patterns
- Error handling
- Input validation
- Utility functions

### Documentation

**Inline Help:**
- Hover documentation
- Parameter hints
- Example code
- Quick links

**Help Panel:**
- Searchable docs
- Context sensitive
- Examples included
- Offline capable

### Testing

**Test Support:**
- Test file detection
- Expected output
- Assertion checking
- Test runner

**Benchmarking:**
- Execution timing
- Performance metrics
- Memory usage
- Comparison tools

## Settings and Preferences

### General Settings

```
☑ Auto-save enabled
  └─ Interval: 30 seconds
☑ Syntax checking
  └─ Delay: 500ms
☑ Auto-completion
☑ Show line numbers
☑ Word wrap
```

### Editor Preferences

```
Font: Consolas, monospace
Size: 14px
Theme: Dark
Tab Size: 4
Insert Spaces: No
```

### Debug Preferences

```
☑ Break on error
☐ Break on warning
☑ Show variable types
☑ Highlight current line
Execution Speed: Normal
```

### Advanced Options

```
☑ Enable web workers
☑ Use localStorage
☐ Telemetry
Cache Size: 10MB
History Size: 50
```

## Mobile Support

### Touch Interface

- Touch to place cursor
- Pinch to zoom
- Swipe to scroll
- Long press for context menu

### Responsive Design

- Adapts to screen size
- Mobile-optimized layout
- Touch-friendly buttons
- Virtual keyboard support

### Mobile Features

- Simplified interface
- Essential features only
- Optimized performance
- Reduced memory usage

## Security Features

### Sandboxing

- Isolated execution
- No file system access
- Limited network access
- Safe program execution

### Data Protection

- Local storage only
- No server uploads
- Encrypted storage
- Session isolation

### Privacy

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

- Press F1 for help
- Check documentation
- View examples
- Report issues on GitHub

## See Also

- [Getting Started](getting-started.md) - First steps
- [Keyboard Shortcuts](../../../user/keyboard-shortcuts.md) - Quick reference
- [Debugging Guide](debugging.md) - Debug features
- [Settings](settings.md) - Configuration options