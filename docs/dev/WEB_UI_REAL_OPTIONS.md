# Web UI Options for MBASIC (Real Web UIs)

**Date**: 2025-10-25
**Requirement**: Pure web UI with modern components (not terminal emulation)

## Goal

Create a modern web-based IDE for MBASIC with:
- Code editor with syntax highlighting
- Output panel for program results
- Run/stop/debug controls
- File management
- Pure Python backend (no JavaScript development)

---

## Framework Comparison

### Option 1: NiceGUI (★ Recommended)

**Website**: https://nicegui.io/
**GitHub**: https://github.com/zauberzeug/nicegui

#### Overview
NiceGUI is a Python framework for building web UIs with instant live reload, WebSocket-based real-time updates, and built-in components.

#### Architecture
```
Browser (Vue/Quasar) ←→ WebSocket ←→ FastAPI ←→ MBASIC Interpreter
```

#### Key Features
- ✅ **Code Editor**: nicegui-codemirror extension available
- ✅ **Real-time updates**: Instant UI refresh via WebSockets
- ✅ **Rich components**: Buttons, inputs, logs, charts, etc.
- ✅ **Pure Python**: Zero JavaScript required
- ✅ **Fast development**: Very pythonic API
- ✅ **Good docs**: Extensive examples at nicegui.io

#### Code Editor
**nicegui-codemirror** extension:
```python
from nicegui import ui
from nicegui_codemirror import CodeMirror

editor = CodeMirror(language='python', style={'height': '400px'})
editor.value = '''10 PRINT "HELLO"
20 END'''

@ui.button('Run')
def run():
    code = editor.value
    # Execute BASIC code
```

#### Example MBASIC IDE Layout
```python
from nicegui import ui

# Main layout
with ui.splitter() as splitter:
    with splitter.before:
        # Left: Editor
        ui.label('Program Editor').classes('text-h6')
        editor = CodeMirror(language='basic', height='500px')

        with ui.row():
            ui.button('Run', on_click=run_program)
            ui.button('Stop', on_click=stop_program)
            ui.button('Save', on_click=save_program)
            ui.button('Load', on_click=load_program)

    with splitter.after:
        # Right: Output
        ui.label('Output').classes('text-h6')
        output_log = ui.log(max_lines=1000).classes('h-full')

ui.run()
```

#### Pros
- ✅ Fastest development time
- ✅ Excellent real-time updates (WebSockets)
- ✅ Code editor extension ready to use
- ✅ Beautiful Quasar/Material Design components
- ✅ Active development and community
- ✅ Works great for dashboards and tools

#### Cons
- ❌ Less mature than some alternatives
- ❌ Fewer third-party extensions

#### Estimated Effort
- **Day 1**: Basic layout + editor + run button
- **Day 2**: Output handling + INPUT support
- **Day 3**: File operations + polish
- **Total: 3 days to working IDE**

---

### Option 2: Reflex

**Website**: https://reflex.dev/
**GitHub**: https://github.com/reflex-dev/reflex

#### Overview
Full-stack web framework in pure Python with reactive state management and built-in deployment.

#### Architecture
```
Browser (React) ←→ WebSocket ←→ FastAPI ←→ MBASIC Interpreter
```

#### Key Features
- ✅ **Hot reload**: Instant preview during development
- ✅ **State management**: Built-in reactive state
- ✅ **Rich components**: 60+ built-in components
- ✅ **Production ready**: Includes deployment (Reflex Cloud)
- ✅ **Type safe**: Full type checking with Python types

#### Example MBASIC IDE
```python
import reflex as rx

class State(rx.State):
    code: str = "10 PRINT \"HELLO\"\n20 END"
    output: str = ""

    def run_program(self):
        # Execute MBASIC code
        result = execute_mbasic(self.code)
        self.output = result

def index():
    return rx.hstack(
        # Left: Editor
        rx.vstack(
            rx.heading("Program Editor"),
            rx.text_area(
                value=State.code,
                on_change=State.set_code,
                height="500px",
                width="100%"
            ),
            rx.hstack(
                rx.button("Run", on_click=State.run_program),
                rx.button("Stop"),
                rx.button("Save"),
            )
        ),
        # Right: Output
        rx.vstack(
            rx.heading("Output"),
            rx.text(State.output, white_space="pre")
        )
    )

app = rx.App()
app.add_page(index)
```

#### Pros
- ✅ Most mature pure-Python web framework
- ✅ Excellent documentation
- ✅ Built-in deployment solution
- ✅ Active development (VC-backed)
- ✅ React-based (familiar to web devs)

#### Cons
- ❌ More boilerplate than NiceGUI
- ❌ Heavier (compiles to React)
- ❌ Need to learn Reflex state management
- ❌ No built-in code editor (need custom component)

#### Estimated Effort
- **Day 1-2**: Learn Reflex patterns + basic layout
- **Day 3**: Implement code editor (custom component or library)
- **Day 4**: Output handling + INPUT support
- **Day 5**: File operations + polish
- **Total: 5 days to working IDE**

---

### Option 3: Streamlit

**Website**: https://streamlit.io/
**GitHub**: https://github.com/streamlit/streamlit

#### Overview
The most popular Python web app framework for data science and quick prototypes.

#### Architecture
```
Browser ←→ HTTP (reruns on interaction) ←→ Streamlit ←→ MBASIC
```

#### Key Features
- ✅ **Simplest API**: Most pythonic, minimal code
- ✅ **Huge community**: Most popular Python web framework
- ✅ **Free hosting**: Streamlit Cloud
- ✅ **Great for demos**: Perfect for showcasing projects

#### Example MBASIC IDE
```python
import streamlit as st

st.title("MBASIC Web IDE")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Program Editor")
    code = st.text_area("Enter BASIC code:", height=500)

    if st.button("Run"):
        output = execute_mbasic(code)
        st.session_state.output = output

with col2:
    st.subheader("Output")
    if 'output' in st.session_state:
        st.code(st.session_state.output)
```

#### Pros
- ✅ Fastest to prototype
- ✅ Largest community
- ✅ Excellent for demos/MVP
- ✅ Free cloud hosting

#### Cons
- ❌ **Page reruns on every interaction** - Not ideal for IDE
- ❌ Limited real-time I/O (INPUT would be awkward)
- ❌ No WebSocket support (harder for live programs)
- ❌ Less control over layout

#### Estimated Effort
- **Day 1**: Working prototype
- **Day 2**: Handle interactive I/O (workarounds needed)
- **Total: 2 days to demo, but limited functionality**

---

## Detailed Comparison Matrix

| Feature | NiceGUI | Reflex | Streamlit |
|---------|---------|--------|-----------|
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Code Editor** | ✅ Extension | ⚠️ Custom | ⚠️ Basic textarea |
| **Real-time I/O** | ✅ WebSocket | ✅ WebSocket | ❌ Reruns |
| **Interactive INPUT** | ✅ Easy | ✅ Good | ⚠️ Difficult |
| **Layout Control** | ✅ Excellent | ✅ Excellent | ⚠️ Limited |
| **Learning Curve** | Low | Medium | Very Low |
| **Maturity** | Medium | High | Very High |
| **Community** | Growing | Growing | Large |
| **Deployment** | DIY | Reflex Cloud | Streamlit Cloud |
| **Performance** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Best For** | Interactive apps | Production apps | Demos/Dashboards |

---

## Recommendation: NiceGUI

### Why NiceGUI?

1. **Perfect fit for our needs**:
   - Code editor extension ready (`nicegui-codemirror`)
   - Real-time WebSocket updates (critical for interactive BASIC programs)
   - Can handle INPUT prompts naturally
   - Fast development

2. **Technical advantages**:
   - Built on FastAPI (modern, async, fast)
   - Quasar components (Material Design, professional look)
   - Easy to add features later (file browser, debugger, etc.)

3. **Integration with MBASIC**:
   - Can run MBASIC interpreter in background thread
   - Stream output to UI log component
   - Handle INPUT with dialog or inline prompt
   - Minimal changes to existing interpreter

---

## Proposed Architecture

### NiceGUI MBASIC IDE

```
┌─────────────────────────────────────────────────────────┐
│                  Browser (http://localhost:8080)         │
│                                                          │
│  ┌────────────────────────┬─────────────────────────┐  │
│  │  Program Editor        │  Output Window          │  │
│  │  ┌──────────────────┐  │  ┌──────────────────┐  │  │
│  │  │ 10 PRINT "HI"    │  │  │ MBASIC 5.21      │  │  │
│  │  │ 20 FOR I=1 TO 3  │  │  │ Ready            │  │  │
│  │  │ 30   PRINT I     │  │  │ > RUN            │  │  │
│  │  │ 40 NEXT I        │  │  │ HI               │  │  │
│  │  │ 50 END           │  │  │ 1                │  │  │
│  │  └──────────────────┘  │  │ 2                │  │  │
│  │                        │  │ 3                │  │  │
│  │  [Run] [Stop] [Clear] │  │ >                 │  │  │
│  │  [Save] [Load] [Help] │  │                   │  │  │
│  └────────────────────────┴──────────────────────────┘  │
│                                                          │
│  Status: Running | Line 30 | 0.5s                      │
└─────────────────────────────────────────────────────────┘
                          ↕ WebSocket
┌─────────────────────────────────────────────────────────┐
│              NiceGUI + FastAPI Backend                   │
│                                                          │
│  ┌──────────────┐      ┌─────────────────────────┐    │
│  │ UI Manager   │ ←→   │ MBASIC Interpreter      │    │
│  │ - Editor     │      │ - Runtime               │    │
│  │ - Output log │      │ - Program Manager       │    │
│  │ - Controls   │      │ - IOHandler (custom)    │    │
│  └──────────────┘      └─────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ File Storage (per session)                   │      │
│  │ - user_123/program.bas                       │      │
│  │ - user_123/data.txt                          │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### Key Components

1. **WebIOHandler** (new)
   - Custom IOHandler for web UI
   - Queues PRINT output to UI log
   - Handles INPUT with async prompts
   - Inherits from base IOHandler

2. **Session Manager**
   - One MBASIC instance per browser session
   - File isolation per user
   - Cleanup on disconnect

3. **UI Components**
   - CodeMirror editor (syntax highlighting for BASIC)
   - Log component (scrollable output)
   - Control buttons (Run, Stop, Clear, etc.)
   - File picker (Load/Save)

---

## Implementation Plan

### Phase 1: Basic IDE (Day 1)

**Goal**: Run BASIC programs and see output

```python
from nicegui import ui
from nicegui_codemirror import CodeMirror

class MBasicIDE:
    def __init__(self):
        self.editor = None
        self.output_log = None
        self.running = False

    def create_ui(self):
        with ui.splitter() as splitter:
            with splitter.before:
                ui.label('MBASIC Program').classes('text-h6')
                self.editor = CodeMirror(
                    language='basic',
                    height='500px'
                )
                self.editor.value = '10 PRINT "HELLO"\n20 END'

                with ui.row():
                    ui.button('Run', on_click=self.run)
                    ui.button('Stop', on_click=self.stop)
                    ui.button('Clear', on_click=self.clear)

            with splitter.after:
                ui.label('Output').classes('text-h6')
                self.output_log = ui.log(max_lines=1000)

    async def run(self):
        self.output_log.clear()
        code = self.editor.value

        # Execute MBASIC
        from lexer import Lexer
        from parser import Parser
        from interpreter import Interpreter

        # Run in background to keep UI responsive
        result = await run_mbasic_async(code, self.output_log)

    def stop(self):
        # Stop execution
        pass

    def clear(self):
        self.output_log.clear()

ide = MBasicIDE()
ide.create_ui()
ui.run(port=8080)
```

### Phase 2: Interactive I/O (Day 2)

**Handle INPUT statements**:

```python
class WebIOHandler(IOHandler):
    def __init__(self, output_log):
        self.output_log = output_log
        self.input_queue = asyncio.Queue()

    def print(self, text):
        self.output_log.push(text)

    async def input(self, prompt):
        # Show input dialog in UI
        result = await show_input_dialog(prompt)
        return result

async def show_input_dialog(prompt):
    # NiceGUI dialog for user input
    with ui.dialog() as dialog:
        with ui.card():
            ui.label(prompt)
            input_field = ui.input()
            ui.button('OK', on_click=dialog.submit)

    await dialog
    return input_field.value
```

### Phase 3: File Management (Day 3)

**Save/Load programs**:

```python
def save_program(self):
    code = self.editor.value
    filename = await ui.prompt('Filename:', value='program.bas')

    # Save to server
    with open(f'sessions/{session_id}/{filename}', 'w') as f:
        f.write(code)

    ui.notify(f'Saved {filename}')

async def load_program(self):
    # File picker dialog
    files = list_user_files(session_id)
    selected = await ui.select('Load file:', options=files)

    with open(f'sessions/{session_id}/{selected}', 'r') as f:
        code = f.read()

    self.editor.value = code
```

### Phase 4: Enhancement (Days 4-5)

- Syntax highlighting for BASIC
- Breakpoint support (visual indicators)
- Variable watch window
- Line numbers in output
- Example programs gallery
- Dark/light theme toggle

---

## Code Structure

```
src/ui/web/
├── __init__.py
├── web_ui.py              # Main NiceGUI app
├── web_io_handler.py      # Custom IOHandler for web
├── session_manager.py     # Manage user sessions
├── components/
│   ├── editor.py          # Code editor component
│   ├── output.py          # Output log component
│   ├── toolbar.py         # Control buttons
│   └── file_browser.py    # File management
├── static/
│   ├── styles.css         # Custom CSS
│   └── examples/          # Example BASIC programs
│       ├── hello.bas
│       ├── loops.bas
│       └── fibonacci.bas
└── sessions/              # User session storage
    └── {session_id}/
        └── *.bas          # User programs
```

---

## Deployment Options

### Development
```bash
python3 src/ui/web/web_ui.py
# Opens http://localhost:8080
```

### Production

**Option 1: Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install nicegui nicegui-codemirror
CMD ["python", "src/ui/web/web_ui.py"]
```

**Option 2: Cloud Platforms**
- Fly.io (easiest)
- Railway
- Render
- Heroku
- Google Cloud Run

### Security
- Resource limits per session
- Timeout long-running programs
- File system sandboxing
- Rate limiting
- Optional authentication

---

## Next Steps

1. **Install NiceGUI**:
   ```bash
   pip install nicegui nicegui-codemirror
   ```

2. **Create prototype** (4-6 hours):
   - Basic editor + output
   - Run button
   - Test with simple BASIC program

3. **Evaluate**: Does it meet requirements?

4. **Implement full IDE**: 3-5 days

5. **Deploy**: Make publicly accessible

---

## Comparison to Existing UIs

| Feature | CLI | Curses | Tk | Web (NiceGUI) |
|---------|-----|--------|----|----|
| Remote Access | ❌ | ⚠️ SSH | ❌ | ✅ |
| Multi-user | ❌ | ❌ | ❌ | ✅ |
| Install Required | ✅ | ✅ | ✅ | ❌ |
| Syntax Highlighting | ❌ | ✅ | ✅ | ✅ |
| Mobile Friendly | ❌ | ❌ | ❌ | ✅ |
| Share URL | ❌ | ❌ | ❌ | ✅ |
| Works Offline | ✅ | ✅ | ✅ | ❌ |

---

## Conclusion

**Recommended**: Start with **NiceGUI**

- Fastest development (3 days to working IDE)
- Perfect feature match (code editor, real-time output)
- Pure Python (no JavaScript)
- Modern, professional UI
- Easy to enhance later

**Timeline**:
- Prototype: 1 day
- MVP: 3 days
- Production-ready: 5 days
