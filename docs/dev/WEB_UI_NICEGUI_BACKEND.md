# Web UI (NiceGUI Backend) Details

This page gives the detail for the NiceGUI web UI in `src/ui/web/`. The steps to
install and start the web UI are in
[src/ui/web/README.md](https://github.com/avwohl/mbasic/blob/main/src/ui/web/README.md).
The text of this page was checked against `src/ui/web/nicegui_backend.py` when the
page was last changed. If the code and this page disagree, the code is right.

## Features

- **Program editor.** One CodeMirror 5 editor holds the whole program. Auto-numbering
  is a setting. The editor shows syntax errors, and `Check Syntax` in the toolbar runs
  the check on request.
- **Output pane.** A text area that scrolls on. Output is sent in batches, and
  no menu or button clears the pane unless you choose `Run > Clear Output`.
- **INPUT works.** The prompt is added to the output pane and the pane accepts
  typing at the end of the text. `Enter` sends the line to the program. The code is
  `_enable_inline_input`, `_get_input` and `_get_input_async`. There is no modal dialog.
- **Immediate mode.** A line under the toolbar runs a statement at once. The commands
  `LIST`, `DELETE`, `RENUM`, `FILES`, `SAVE`, `LOAD`, `MERGE`, `CHAIN` and `SYSTEM` work there.
- **Debugger.** Step Line, Step Statement, Continue, breakpoints, a Variables window
  and a Stack window.
- **Settings.** A settings dialog. Each browser session has its own settings.
- **Help.** Help Topics and the Web Games Library open in a new tab. `Browse Example
  Programs` loads an example from the server.
- **Sessions.** Each browser session has its own interpreter, program and virtual
  file system. With `NICEGUI_REDIS_URL` set, the session state is kept in Redis.
  See [WEB_MULTIUSER_DEPLOYMENT.md](WEB_MULTIUSER_DEPLOYMENT.md).

### Limitations

- **File menu.** `Open` uploads a file from the computer of the user. `Save` and
  `Save As` send a download to the browser. The server has no program file store. The
  BASIC statements `OPEN`, `PRINT#` and `FILES` use an in-memory virtual file system
  that is private to the session and is lost when the server stops.
- **Recent Files.** The menu shows the files opened in this page. The list is written to
  the `localStorage` of the browser, but the code never reads the list back
  (`_load_recent_files` is not called), so the list is empty after a reload.
- **SYSTEM.** `SYSTEM` ends the program of the session and prints `Goodbye`. It does
  not stop the server, and the other sessions are not affected. A statement after
  `SYSTEM` does not run, and `CONT` does nothing. The CLI, curses and Tk UIs
  leave the process at `SYSTEM`.
- **File > Exit.** `File > Exit` calls `app.shutdown()`. That call stops the whole
  server and so all sessions. Use `File > Exit` only on a server that has one user.

## User Interface

The window has, from top to bottom:

1. A menu bar: File, Edit, Run, Debug, Help.
2. A toolbar: Run, Stop, Step, Stmt, Cont, and Check Syntax.
3. The editor and the output pane, side by side (one above the other on a phone).
4. The immediate-mode line, with an Execute button.
5. A status bar with the status text, the auto-number state, the resource use and the
   version.

### Menus

- **File:** New, Open, Save, Save As, Merge, Recent Files, Exit.
- **Edit:** Find/Replace, Delete Lines, Renumber, Sort Lines, Smart Insert, Settings.
- **Run:** Run Program, Stop, List Program, Clear Output.
- **Debug:** Step Line, Step Statement, Continue, Toggle Breakpoint, Clear All
  Breakpoints, Show Variables, Show Stack.
- **Help:** Help Topics, Web Games Library, Browse Example Programs, About.

The keys of the web UI are in `src/ui/web_keybindings.json` and are handled in
`src/ui/web/web_keyboard.py`. Use control keys and not function keys.

## Architecture

**NiceGUIBackend** (`src/ui/web/nicegui_backend.py`) builds the page, owns the
`Runtime`, the `Interpreter` and the program of one session, and carries out the
immediate commands (`cmd_list`, `cmd_renum`, `cmd_delete`, `cmd_load`, `cmd_save`,
`cmd_merge`, `cmd_files`, `cmd_chain`, `cmd_system`). The interpreter calls these
through `interpreter.interactive_mode`.

**SimpleWebIOHandler** sends `PRINT` output to the output pane and starts the inline
INPUT.

**SandboxedFileIO** (`src/file_io.py`) is the file interface of the interpreter in
the web UI. Program files are handled by the upload and download of the browser. Its
`system_exit()` halts the program of the session.

**CodeMirror5Editor** (`src/ui/web/codemirror5_editor.py` and the `.js` and `.css`
files beside it) is the editor component.

**SessionState** (`src/ui/web/session_state.py`) is the form in which a session is saved
to Redis.

### Execution model

A program runs in ticks, so the page stays responsive:

1. The user chooses `Run`. The backend makes the program and starts the interpreter.
2. A NiceGUI timer calls `_execute_tick()` every 10 ms.
3. Each tick runs a number of statements and sends the output to the output pane.
4. At an `INPUT`, the tick loop waits until the user presses `Enter`.
5. The timer stops when the program ends, stops at a breakpoint or at `STOP`, or when
   the user chooses `Stop`.

## Tests

`nicegui` is needed to run the tests of the page itself:

```bash
pytest tests/nicegui/ -v
```

These tests use the NiceGUI `user` fixture and need no browser. They cover the page
load, adding lines, `NEW`, clear output, list, run and `INPUT`.

The tests in `tests/regression/ui/test_web_immediate_commands.py` replace `nicegui` with a
mock, so they run without it. They cover the immediate commands and `SYSTEM`.

## Known issues

- Recent Files is not restored after a reload (see Limitations).
- `File > Exit` stops the whole server (see Limitations).
- The methods `load_file`, `save_file`, `delete_file` and `file_exists` of
  `SandboxedFileIO` raise `IOError`. The browser upload and download take their place.

## Development

1. Add a method to `NiceGUIBackend`.
2. Connect the method to a button or a menu item.
3. Add a test in `tests/nicegui/`, or in `tests/regression/ui/` when the test can use a
   mock of `nicegui`.
4. Start the page with `python3 mbasic --ui web` and try the change.

Use `.mark('name')` on an element that a test must find. Keep the logic of the
language in the interpreter and not in the page.

## Related documents

- [WEB_MULTIUSER_DEPLOYMENT.md](WEB_MULTIUSER_DEPLOYMENT.md): servers with many users.
- [WEB_PROGRAM_KEYBOARD.md](WEB_PROGRAM_KEYBOARD.md): keys for a running program.
- [WEB_ERROR_LOGGING.md](WEB_ERROR_LOGGING.md): how the web UI logs errors.
