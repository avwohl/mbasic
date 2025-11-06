# Web UI Options for MBASIC

**Date**: 2025-10-25

## Goal

Create a web-based UI for MBASIC that allows users to run BASIC programs in their browser, similar to how the Curses and Tk UIs work locally.

## Key Requirements

Based on our existing architecture:

1. **Terminal-like interface** - MBASIC programs expect terminal I/O (PRINT, INPUT)
2. **Program editor** - Need to edit BASIC code
3. **Integration with existing backend** - Should use same interpreter/runtime
4. **Session management** - Multiple users running different programs
5. **Real-time I/O** - Interactive programs need responsive INPUT/PRINT

## Framework Options

### Option 1: Terminal Emulator Approach (Recommended)

**Using xterm.js + Python backend**

#### Architecture
```
Browser (xterm.js) ←→ WebSocket ←→ Flask/FastAPI ←→ MBASIC Interpreter
```

**Pros:**
- ✅ True terminal experience - runs MBASIC exactly as-is
- ✅ Full ANSI/VT100 support for colors, cursor control
- ✅ Copy/paste works naturally
- ✅ Minimal changes to existing codebase
- ✅ Can reuse CLI backend with minor modifications
- ✅ Proven technology (used by VS Code, Replit)

**Cons:**
- ❌ Requires WebSocket infrastructure
- ❌ Need to handle PTY (pseudo-terminal) on server
- ❌ Session management complexity

**Implementation:**

Libraries:
- **xterm.js** (frontend) - Terminal emulator in browser
- **pyxtermjs** (backend) - Python integration with xterm.js
- **Flask** or **FastAPI** - Web framework
- **python-pty** - Pseudo-terminal handling

Example flow:
```python
# Server-side (simplified)
from flask import Flask, render_template
from flask_socketio import SocketIO
import pty
import subprocess

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('input')
def handle_input(data):
    # Send user input to MBASIC process
    pty_process.write(data)

@socketio.on('connect')
def handle_connect():
    # Start MBASIC interpreter in PTY
    master, slave = pty.openpty()
    process = subprocess.Popen(
        ['python3', 'mbasic', '--ui', 'cli'],
        stdin=slave, stdout=slave, stderr=slave
    )
    # Stream output to browser
```

**Estimated Effort:** 2-3 days
- Day 1: Basic xterm.js integration + WebSocket
- Day 2: PTY handling + session management
- Day 3: Testing + polish

---

### Option 2: Custom Web UI with Rich Components

**Using NiceGUI, Streamlit, or Reflex**

#### Architecture
```
Browser ←→ HTTP/WebSocket ←→ Python Framework ←→ MBASIC Interpreter
```

**Pros:**
- ✅ Beautiful, modern UI out of the box
- ✅ Python-only development (no JavaScript)
- ✅ Built-in components (code editor, buttons, etc.)
- ✅ Easy to add extra features (syntax highlighting, debugger UI)

**Cons:**
- ❌ Need custom I/O handling for MBASIC programs
- ❌ May not feel like "authentic" BASIC experience
- ❌ More work to integrate with existing interpreter
- ❌ INPUT/PRINT need special handling

**Framework Comparison:**

| Framework | Best For | Complexity | Real-time I/O |
|-----------|----------|------------|---------------|
| **NiceGUI** | Interactive apps | Low | ✅ Good (WebSockets) |
| **Streamlit** | Data apps | Very Low | ⚠️ Limited (reruns) |
| **Reflex** | Full apps | Medium | ✅ Good (WebSockets) |
| **Dash** | Analytics | Medium | ⚠️ Limited |

**Recommended for this approach:** NiceGUI

Example:
```python
from nicegui import ui

editor = ui.textarea(label='BASIC Program')
output = ui.log()

@ui.button('Run')
async def run():
    # Run MBASIC code
    code = editor.value
    # Need custom I/O bridge here
    result = await run_mbasic(code)
    output.push(result)
```

**Estimated Effort:** 4-5 days
- Day 1-2: UI layout + editor integration
- Day 2-3: Custom I/O bridge for MBASIC
- Day 4-5: Testing + polish

---

### Option 3: Hybrid Approach

**Terminal emulator + enhanced UI**

Combine xterm.js for the terminal with additional UI components:

```
┌─────────────────────────────────────┐
│  MBASIC Web IDE                     │
├─────────────────┬───────────────────┤
│  Code Editor    │  Terminal Output  │
│  (Monaco/Ace)   │  (xterm.js)       │
│                 │                   │
│  [Run] [Save]   │  > 10 PRINT "HI"  │
│  [Load] [Help]  │  > 20 END         │
│                 │  > RUN            │
│                 │  HI               │
└─────────────────┴───────────────────┘
```

**Pros:**
- ✅ Best of both worlds
- ✅ Modern IDE-like experience
- ✅ True terminal compatibility
- ✅ Can add syntax highlighting, breakpoints, etc.

**Cons:**
- ❌ Most complex to build
- ❌ Need frontend development (HTML/CSS/JS)

**Estimated Effort:** 5-7 days

---

## Recommended Solution

### **Option 1: xterm.js Terminal Emulator** (Start here)

**Rationale:**
1. **Fastest to MVP** - Get working web UI in 2-3 days
2. **Minimal code changes** - Reuse CLI backend almost as-is
3. **Authentic experience** - Feels like real MBASIC terminal
4. **Proven approach** - Used by major products (VS Code, etc.)
5. **Foundation for later** - Can enhance with Option 3 features later

**Architecture:**

```
┌──────────────────────────────────────────────────────┐
│                    Browser                           │
│  ┌────────────────────────────────────────────────┐ │
│  │          xterm.js Terminal                     │ │
│  │  MBASIC 5.21 Interpreter                       │ │
│  │  Ready                                         │ │
│  │  > _                                           │ │
│  └────────────────────────────────────────────────┘ │
│           ↕ WebSocket                                │
└──────────────────────────────────────────────────────┘
                    ↕
┌──────────────────────────────────────────────────────┐
│              Python Backend (Flask/FastAPI)          │
│  ┌────────────────────────────────────────────────┐ │
│  │  Session Manager                               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │ │
│  │  │ User 1   │  │ User 2   │  │ User 3   │    │ │
│  │  │ PTY +    │  │ PTY +    │  │ PTY +    │    │ │
│  │  │ MBASIC   │  │ MBASIC   │  │ MBASIC   │    │ │
│  │  └──────────┘  └──────────┘  └──────────┘    │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

**File Structure:**
```
src/ui/web/
├── static/
│   ├── xterm.css           # Terminal styling
│   └── xterm.js            # Terminal library
├── templates/
│   └── index.html          # Main page
├── web_backend.py          # Flask/FastAPI server
└── session_manager.py      # Manage multiple MBASIC sessions
```

**Implementation Steps:**

1. **Phase 1: Basic Terminal** (1 day)
   - Set up Flask/FastAPI with WebSocket
   - Integrate xterm.js
   - Single-user PTY connection
   - Test PRINT/INPUT

2. **Phase 2: Session Management** (1 day)
   - Multiple concurrent users
   - Session cleanup
   - File persistence per user

3. **Phase 3: Polish** (1 day)
   - Proper error handling
   - Reconnection logic
   - Performance tuning
   - Add help/about page

**Total: 3 days to working web UI**

---

## Future Enhancements (After MVP)

Once basic web terminal works, can add:

1. **File browser** - Upload/download .BAS files
2. **Syntax highlighting** - Monaco editor for code
3. **Debugger UI** - Visual breakpoints, step through
4. **Examples gallery** - Pre-loaded BASIC programs
5. **Sharing** - Share programs via URL
6. **Collaboration** - Multiple users editing same program
7. **Mobile support** - Touch-friendly controls

---

## Technology Stack (Recommended)

**Backend:**
- **FastAPI** (modern, async, auto-docs) or **Flask** (simpler)
- **python-socketio** - WebSocket support
- **pty** (built-in Python) - Pseudo-terminal

**Frontend:**
- **xterm.js** - Terminal emulator
- **xterm-addon-fit** - Auto-resize terminal
- **xterm-addon-web-links** - Clickable URLs

**Deployment:**
- Docker container (easy deployment)
- Nginx reverse proxy (production)
- Can run on Heroku, Railway, Fly.io, etc.

**Optional:**
- **Redis** - Session state (if scaling to multiple servers)
- **PostgreSQL** - User programs/files persistence

---

## Security Considerations

**Important:** Web UI exposes Python interpreter to internet

**Mitigations:**
1. **Sandboxing** - Run MBASIC in Docker container
2. **Resource limits** - CPU/memory/time restrictions
3. **File system isolation** - No access outside work directory
4. **Rate limiting** - Prevent abuse
5. **Authentication** (optional) - User accounts
6. **No file I/O to dangerous paths** - Restrict OPEN statements
7. **Process timeout** - Kill long-running programs

**Example Docker isolation:**
```dockerfile
FROM python:3.11-slim
RUN useradd -m mbasic
USER mbasic
WORKDIR /home/mbasic
# Copy MBASIC files
# Set resource limits
CMD ["python3", "web_ui.py"]
```

---

## Comparison to Existing UIs

| Feature | CLI | Curses | Tk | Web (xterm.js) |
|---------|-----|--------|----|----|
| Interactive | ✅ | ✅ | ✅ | ✅ |
| Visual Editor | ❌ | ✅ | ✅ | ⚠️ (future) |
| Syntax Highlighting | ❌ | ✅ | ✅ | ⚠️ (future) |
| Debugger | ❌ | ✅ | ✅ | ⚠️ (future) |
| Remote Access | ❌ | ⚠️ (SSH) | ❌ | ✅ |
| Multi-user | ❌ | ❌ | ❌ | ✅ |
| Mobile-friendly | ❌ | ❌ | ❌ | ✅ |
| Install Required | ✅ | ✅ | ✅ | ❌ |
| Shareability | ❌ | ❌ | ❌ | ✅ |

---

## Next Steps

1. **Prototype** - Build minimal xterm.js proof of concept (4-6 hours)
2. **Evaluate** - Test with real MBASIC programs
3. **Decide** - Confirm approach or pivot
4. **Implement** - Build full web UI
5. **Deploy** - Make available online

**Quick Start Prototype:**
```bash
# Install dependencies
pip install flask flask-socketio python-socketio

# Create minimal web UI
# (see implementation guide below)

# Test locally
python3 web_ui.py
# Open http://localhost:5000
```

---

## Alternative: Cloud IDE Approach

Instead of building from scratch, could integrate MBASIC into existing cloud IDE:

- **Jupyter Notebook** - MBASIC kernel
- **Google Colab** - MBASIC magic commands
- **Replit** - MBASIC template

**Pros:** Leverage existing infrastructure
**Cons:** Less control over UX

---

## Conclusion

**Recommendation:** Start with **Option 1 (xterm.js terminal emulator)**

- Fastest path to working web UI
- Minimal changes to existing code
- Authentic MBASIC experience
- Can enhance later with modern IDE features

**Timeline:** 3 days to MVP, 1 week to production-ready

**Risk:** Low - proven technology stack
