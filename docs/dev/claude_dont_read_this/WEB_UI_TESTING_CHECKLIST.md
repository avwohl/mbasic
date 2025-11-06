# Web UI Testing Checklist

## Status

**TODO** - Test when web UI menus and features are stable

## Multi-User Session Isolation Testing

**Implemented:** Version 1.0.300
**Test Status:** Pending manual verification

### Automated Test

```bash
python3 utils/test_web_session_isolation.py
```

This verifies that session properties are correctly defined.

### Manual Multi-User Testing (TODO)

**Prerequisites:** Web UI menus and basic functionality working

**Test Procedure:**

1. Start web UI:
   ```bash
   python3 mbasic --ui web
   ```

2. Open http://localhost:8080 in **two separate browser tabs** (Tab 1 and Tab 2)

3. **Test 1: Independent Program Loading**
   - Tab 1: Enter program:
     ```basic
     10 PRINT "TAB 1"
     20 END
     ```
   - Tab 2: Enter program:
     ```basic
     10 PRINT "TAB 2"
     20 END
     ```
   - Expected: Each tab shows its own program
   - **VERIFY:** Tab 1 still shows "TAB 1", Tab 2 still shows "TAB 2"

4. **Test 2: Independent Execution**
   - Tab 1: Run program (should output "TAB 1")
   - Tab 2: Run program (should output "TAB 2")
   - Expected: Each tab's output is independent
   - **VERIFY:** Tab 1 output shows "TAB 1", Tab 2 output shows "TAB 2"

5. **Test 3: Independent Variable State**
   - Tab 1: Enter and run:
     ```basic
     10 A = 100
     20 PRINT A
     ```
   - Tab 2: Enter and run:
     ```basic
     10 A = 200
     20 PRINT A
     ```
   - Expected: Each tab has its own variable A
   - **VERIFY:** Tab 1 prints 100, Tab 2 prints 200

6. **Test 4: Independent Execution State**
   - Tab 1: Load a long-running program (with loops)
   - Tab 2: Load a different program
   - Tab 1: Start running
   - Tab 2: Start running (while Tab 1 still running)
   - Expected: Both programs run independently
   - **VERIFY:** Both tabs execute without interfering with each other

7. **Test 5: Incognito Window (Different Session)**
   - Open http://localhost:8080 in incognito/private window
   - Load a different program
   - Expected: Incognito session is completely isolated from normal tabs
   - **VERIFY:** Programs don't appear across normal/incognito sessions

8. **Test 6: File Upload Isolation**
   - Tab 1: Upload/Open file A.bas
   - Tab 2: Upload/Open file B.bas
   - Expected: Each tab shows its own uploaded file
   - **VERIFY:** Files remain separate per tab

9. **Test 7: Breakpoint Isolation**
   - Tab 1: Set breakpoint at line 10
   - Tab 2: Set breakpoint at line 20
   - Expected: Breakpoints are per-session
   - **VERIFY:** Each tab only hits its own breakpoints

10. **Test 8: Recent Files Isolation**
    - Tab 1: Open files A, B, C
    - Tab 2: Open files X, Y, Z
    - Expected: Recent files list is per-session
    - **VERIFY:** Each tab shows its own recent files

## Known Issues / Not Yet Working

- Web UI menus are currently in development
- Some features may not be fully functional yet
- Test this checklist once basic web UI is stable

## Notes

- This testing checklist was created after implementing session isolation (v1.0.300)
- Session isolation is implemented and should work, but needs manual verification
- Add this to regular web UI testing once the interface is more stable
- See `docs/history/WEB_MULTI_USER_SESSION_ISOLATION_DONE.md` for implementation details

## Related Files

- Implementation: `src/ui/web/nicegui_backend.py`
- Automated test: `utils/test_web_session_isolation.py`
- Implementation docs: `docs/history/WEB_MULTI_USER_SESSION_ISOLATION_DONE.md`
