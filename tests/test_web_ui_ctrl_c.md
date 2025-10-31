# Test for Web UI Ctrl+C Bug

## Problem
After running programs in the web UI for a while, `Ctrl+C` stops working in the shell that launched `./mbasic --backend web`. User has to use `Ctrl+Z` and `kill`.

## Symptoms
- **Short sessions**: `Ctrl+C` works immediately after startup
- **Long sessions**: After running programs, `Ctrl+C` does nothing
- Must use `Ctrl+Z` to background and then `kill`

## Root Cause
The web UI uses `ui.timer(0.01, self._execute_tick, once=False)` to execute the BASIC interpreter in 10ms intervals. During program execution:

1. Timer fires every 10ms
2. Calls `interpreter.tick(max_statements=1000)`
3. Executes up to 1000 BASIC statements
4. This keeps the async event loop constantly busy
5. Python signal handlers only run between bytecode instructions
6. With the loop busy, SIGINT delivery gets delayed indefinitely

## The Fix Needed

The signal handler in `start_web_ui()` (nicegui_backend.py:2190) is correct, but NiceGUI's `ui.run()` likely overrides it. We need to:

1. Ensure SIGINT can interrupt the async event loop
2. Stop the execution timer when program is interrupted
3. Handle KeyboardInterrupt gracefully in the tick loop

## Manual Test Procedure

1. Start web UI: `./mbasic --backend web`
2. Load a long-running program:
   ```basic
   10 FOR I=1 TO 1000000
   20 PRINT I
   30 NEXT I
   ```
3. Run the program
4. Try to press `Ctrl+C` in the shell
5. **Expected**: Server shuts down
6. **Actual (bug)**: Nothing happens, must use `Ctrl+Z` and `kill`

## Automated Test (TODO)
Need to create a test that:
- Starts web server
- Simulates long-running program
- Sends SIGINT
- Verifies server shuts down within reasonable time (< 1 second)
