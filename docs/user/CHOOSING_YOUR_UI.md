# Choosing Your MBASIC User Interface

This guide helps you select the best MBASIC UI for your specific needs and use cases.

## Quick Decision Tree

```
Start Here
    ↓
Do you need a graphical interface?
    ├─ No → Do you have terminal access only?
    │        ├─ Yes → Use CURSES (full terminal IDE)
    │        └─ No → Use CLI (command line)
    │
    └─ Yes → Do you need to install software?
             ├─ No → Use WEB (browser-based)
             └─ Yes → Use TK (desktop GUI)
```

## UI Comparison at a Glance

| UI | Best For | Avoid If |
|----|----------|----------|
| **CLI** | Automation, testing, purists | You want visual editing |
| **Curses** | SSH/remote, terminal fans | You need mouse support |
| **Tk** | Full IDE experience | You can't install Tkinter |
| **Web** | Sharing, teaching, quick access | You need local files |

## Detailed UI Profiles

### 🖥️ CLI (Command Line Interface)

**Choose CLI when you:**
- Want the authentic MBASIC-80 experience
- Need to automate with scripts
- Run automated tests
- Process batch files
- Work with pipes and redirection
- Debug with command-line tools
- Have minimal resources

**CLI is perfect for:**
```bash
# Automation
echo "10 PRINT \"Hello\"
20 END
RUN" | python3 mbasic

# Testing
python3 mbasic test.bas > output.txt

# Debugging
python3 mbasic --debug program.bas
```

**Real-world use cases:**
- CI/CD pipelines
- Automated testing
- Batch processing
- System administration
- Learning classic BASIC
- Minimal environments

**Unique advantages:**
- Fastest startup time
- Lowest memory usage
- Best for scripting
- Command-line debugging (BREAK, STEP, STACK commands)
- True to original MBASIC

**Limitations:**
- Line-by-line editing only
- No visual debugging interface (debugging via text commands only)
- No mouse support
- No Save without filename

> **Note:** CLI has full debugging capabilities through text commands (BREAK, STEP, STACK, etc.), but lacks visual debugging features (Variables Window, clickable breakpoints, graphical interface) found in Curses, Tk, and Web UIs.

### 📟 Curses (Terminal UI)

**Choose Curses when you:**
- Work over SSH/remote terminal
- Prefer keyboard-only navigation
- Like terminal applications
- Need a TUI without X11
- Want split-screen editing
- Use tmux/screen

**Curses is perfect for:**
```bash
# SSH sessions
ssh server
python3 mbasic --ui curses

# Terminal multiplexers
tmux new
python3 mbasic --ui curses

# Console-only systems
# (no GUI installed)
```

**Real-world use cases:**
- Remote development
- Server administration
- Embedded systems
- Low-bandwidth connections
- Terminal enthusiasts
- Retro computing feel

**Unique advantages:**
- Full IDE in terminal
- Works over SSH
- Keyboard shortcuts
- Split-screen layout
- Low bandwidth needs
- No GUI dependencies

**Limitations:**
- Limited mouse support
- Partial variable editing
- No clipboard integration
- Terminal color limits
- No Find/Replace

### 🪟 Tk (Desktop GUI)

**Choose Tk when you:**
- Want a full-featured IDE
- Need Find/Replace
- Prefer mouse interaction
- Want visual debugging
- Edit multiple files
- Need all features

**Tk is perfect for:**
```bash
# Desktop development
python3 mbasic --ui tk

# Teaching/presentations
# (full visual interface)

# Complex debugging
# (visual breakpoints)
```

**Real-world use cases:**
- Desktop development
- Educational settings
- Complex programs
- Professional development
- Documentation writing
- Code demonstrations

**Unique advantages:**
- Most complete feature set
- Find/Replace dialogs
- Smart Insert mode
- Native file dialogs
- Full debugging UI
- Recent files list
- Mouse support
- Web browser help

**Limitations:**
- Requires Tkinter
- Desktop only
- Larger resource usage
- Not for remote access

### 🌐 Web (Browser-based)

**Choose Web when you:**
- Can't install software
- Need to share programs
- Teach/learn BASIC
- Want modern UI
- Use multiple devices
- Need zero setup

**Web is perfect for:**
```bash
# Start server
python3 mbasic --ui web

# Open browser
http://localhost:8080

# Share with others
# (network accessible)
```

**Real-world use cases:**
- Online tutorials
- Classroom teaching
- Quick demonstrations
- Cross-platform access
- Chromebook users
- Tablet/mobile access

**Unique advantages:**
- No installation
- Modern interface
- Auto-save
- Browser-based
- Touch support
- Theme options
- Share via URL
- Conditional breakpoints

**Limitations:**
- Needs web server
- Browser storage only
- No local file access
- Session-based
- Network dependency

## Use Case Scenarios

### Scenario 1: Teaching a Class

**Best choice: Web UI**

Why:
- Students need no installation
- Share code via URL
- Works on any device
- Modern, familiar interface

Setup:
```bash
# Teacher's machine
python3 mbasic --ui web --host 0.0.0.0

# Students browse to teacher's IP
http://teacher-ip:8080
```

### Scenario 2: Remote Server Development

**Best choice: Curses UI**

Why:
- Works over SSH
- Full IDE features
- No X11 forwarding needed
- Low bandwidth

Setup:
```bash
ssh myserver
cd mbasic
python3 mbasic --ui curses
```

### Scenario 3: Automated Testing

**Best choice: CLI**

Why:
- Scriptable
- Fast execution
- CI/CD friendly
- Output capture

Setup:
```bash
#!/bin/bash
for test in tests/*.bas; do
    python3 mbasic "$test" > "${test}.out"
    diff "${test}.out" "${test}.expected"
done
```

### Scenario 4: Professional Development

**Best choice: Tk UI**

Why:
- Full IDE features
- Find/Replace
- Visual debugging
- Best productivity

Setup:
```bash
python3 mbasic --ui tk
# Or create desktop shortcut
```

### Scenario 5: Quick Program Testing

**Best choice: CLI or Web**

CLI for speed:
```bash
python3 mbasic test.bas
```

Web for convenience:
```bash
python3 mbasic --ui web --open
```

## Performance Comparison

> **Note:** These measurements are approximate, taken on typical development hardware (modern CPU, 8GB+ RAM, Python 3.9+). Actual performance varies based on your system. Startup times are "cold start" measurements. Memory usage shown is Python process only; Web UI browser memory not included.

### Startup Time
1. **CLI**: ~0.1s (fastest)
2. **Curses**: ~0.3s
3. **Tk**: ~0.8s
4. **Web**: ~2s (includes browser launch time)

### Memory Usage (approximate)
1. **CLI**: 20MB (lowest)
2. **Curses**: 25MB
3. **Tk**: 40MB
4. **Web**: 50MB+ (Python process only; browser adds 100MB+)

### Large File Handling
1. **CLI**: Best (streaming)
2. **Curses**: Good
3. **Tk**: Good
4. **Web**: Limited (browser constraints)

### Execution Speed
All UIs use the same interpreter core, so execution speed is identical. Differences appear in:
- UI responsiveness
- Display updates
- Input handling

## Installation Requirements

### CLI
```bash
# Just Python 3.8+
python3 mbasic
```

### Curses
```bash
# Requires urwid
pip install urwid
python3 mbasic --ui curses
```

### Tk
```bash
# Requires tkinter (usually pre-installed)
# Ubuntu/Debian:
sudo apt-get install python3-tk
python3 mbasic --ui tk
```

### Web
```bash
# Requires nicegui
pip install nicegui
python3 mbasic --ui web
```

## Migration Guide

### Moving from CLI to GUI

If you're comfortable with CLI but want GUI features:

1. **Start with Curses**: Familiar commands, visual enhancement
2. **Try Tk next**: Full GUI with familiar concepts
3. **Explore Web**: Modern features, different paradigm

### Moving from GUI to CLI

If you know Tk/Web but need CLI:

1. **Learn commands**: LOAD, SAVE, RUN, LIST
2. **Master line editing**: Edit by number
3. **Use HELP often**: Built-in documentation
4. **Practice debugging**: BREAK, STEP, STACK

### Your Programs Work Everywhere

**Important**: All UIs run the same MBASIC-2025 interpreter. Your .bas files work identically in any UI.

## Multi-UI Workflow

Many users combine UIs:

### Development Workflow
1. **Write** in Tk (best editor)
2. **Debug** in Tk or Web (visual)
3. **Test** in CLI (automation)
4. **Deploy** in CLI (production)

### Teaching Workflow
1. **Prepare** in Tk (full features)
2. **Present** in Web (students access)
3. **Test** in CLI (quick checks)

### Remote Workflow
1. **Develop locally** in Tk
2. **Deploy remotely** in CLI
3. **Debug remotely** in Curses

## Frequently Asked Questions

### Can I use multiple UIs simultaneously?

Yes! Run different UIs in separate terminals:
```bash
# Terminal 1
python3 mbasic --ui tk

# Terminal 2
python3 mbasic --ui curses

# Terminal 3
python3 mbasic --ui web
```

### Which UI is most compatible with original MBASIC?

**CLI** is closest to original MBASIC-80. It maintains command compatibility and behavior.

### Which UI is best for beginners?

**Web** for absolute beginners (familiar interface)
**Tk** for those comfortable installing software
**CLI** for those learning classic BASIC

### Can I switch UIs mid-project?

Yes! Save your program and open in another UI:
```bash
# In CLI
SAVE "myprogram.bas"
SYSTEM

# Switch to Tk
python3 mbasic --ui tk
# Then: File → Open → myprogram.bas
```

### Which UI gets new features first?

Features are typically added to:
1. Tk (most complete)
2. Web (modern features)
3. Curses (terminal features)
4. CLI (compatibility focused)

## Decision Matrix

| Factor | CLI | Curses | Tk | Web |
|--------|-----|--------|----|-----|
| **No dependencies** | ✅ | ❌ | ❌ | ❌ |
| **Remote access** | ✅ | ✅ | ❌ | ✅ |
| **Visual editing** | ❌ | ✅ | ✅ | ✅ |
| **Mouse support** | ❌ | ⚠️ Limited | ✅ | ✅ |
| **Find/Replace** | ❌ | ❌ | ✅ | ❌ |
| **Debugging** | ✅ | ✅ | ✅ | ✅ |
| **Automation** | ✅ | ❌ | ❌ | ❌ |
| **Resource usage** | Low | Low | Med | High |
| **Learning curve** | Med | Low | Low | Low |

## Conclusion

There's no "best" UI—only the best UI for your current task:

- **CLI**: When you need speed, scripting, or authenticity
- **Curses**: When you're in a terminal and want an IDE
- **Tk**: When you want all features on desktop
- **Web**: When you need accessibility and sharing

Try them all and see what fits your workflow!

## Getting Started

```bash
# Try each UI for 5 minutes:
python3 mbasic --ui cli
python3 mbasic --ui curses
python3 mbasic --ui tk
python3 mbasic --ui web

# Your favorite will become clear quickly!
```

## More Information

- [UI Feature Comparison](UI_FEATURE_COMPARISON.md) - Detailed feature matrix
- [Installation Guide](INSTALLATION.md) - Setup instructions
- Individual UI documentation in `docs/help/ui/`