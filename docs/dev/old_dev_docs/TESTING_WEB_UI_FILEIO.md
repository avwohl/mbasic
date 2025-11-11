# Testing Web UI FileIO (SandboxedFileIO)

## How to Test FILES in Web UI

The web UI uses `SandboxedFileIO` which stores files in browser localStorage with the prefix `mbasic_file_`.

### Test Procedure

1. **Start the web UI:**
   ```bash
   python3 mbasic --ui web
   ```

2. **Open browser console** (F12 → Console tab)

3. **Add test files to localStorage:**
   ```javascript
   // Add test BASIC files
   localStorage.setItem('mbasic_file_test1.bas', '10 PRINT "HELLO FROM TEST1"\n20 END\n');
   localStorage.setItem('mbasic_file_test2.bas', '10 PRINT "HELLO FROM TEST2"\n20 END\n');
   localStorage.setItem('mbasic_file_readme.txt', 'This is a readme file\n');
   localStorage.setItem('mbasic_file_data.dat', 'Some data here\n');

   console.log("Test files created!");
   ```

4. **Test FILES command in immediate mode:**
   ```
   > files
   [Should list all mbasic_file_* files]

   > files "*.bas"
   [Should list only .bas files]

   > files "*.txt"
   [Should list only .txt files]
   ```

5. **Test FILES in a program:**
   ```basic
   10 PRINT "Listing all files:"
   20 FILES
   30 PRINT
   40 PRINT "Listing only .BAS files:"
   50 FILES "*.bas"
   60 END
   ```
   Then RUN the program.

### Expected Results

**After adding test files, FILES should show:**
```
> files

Directory listing for: *
--------------------------------------------------
data.dat                                 15 bytes
readme.txt                               24 bytes
test1.bas                                35 bytes
test2.bas                                35 bytes

4 File(s)
```

**With pattern matching:**
```
> files "*.bas"

Directory listing for: *.bas
--------------------------------------------------
test1.bas                                35 bytes
test2.bas                                35 bytes

2 File(s)
```

### Troubleshooting

**If you see JavaScript errors:**
- Check browser console for errors
- The `ui.run_javascript()` call might need to be `await`ed
- JavaScript string escaping might be wrong

**If FILES shows no files:**
- Check localStorage in browser DevTools → Application → Storage → Local Storage
- Look for keys starting with `mbasic_file_`
- Verify the JavaScript commands ran successfully

**If you get "No module named 'nicegui'":**
- The `ui.run_javascript()` import might be wrong
- Check that NiceGUI is installed: `pip install nicegui`

### Verify localStorage Contents

In browser console, check what's stored:
```javascript
// List all mbasic files
for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key.startsWith('mbasic_file_')) {
        console.log(key, '=', localStorage.getItem(key).length, 'bytes');
    }
}
```

### Clean Up

To remove test files:
```javascript
// Remove all test files
localStorage.removeItem('mbasic_file_test1.bas');
localStorage.removeItem('mbasic_file_test2.bas');
localStorage.removeItem('mbasic_file_readme.txt');
localStorage.removeItem('mbasic_file_data.dat');

// Or remove ALL mbasic files
for (let i = localStorage.length - 1; i >= 0; i--) {
    const key = localStorage.key(i);
    if (key.startsWith('mbasic_file_')) {
        localStorage.removeItem(key);
    }
}
```

## Known Issues / TODO

1. **ui.run_javascript() might need async/await**
   - Current implementation uses `ui.run_javascript()` synchronously
   - Might need to be `await ui.run_javascript()` in async context
   - May need to refactor SandboxedFileIO methods to be async

2. **JavaScript string escaping**
   - Current implementation escapes `\`, `'`, `\n`
   - Might miss other special characters
   - Should use JSON.stringify() instead?

3. **Error handling**
   - JavaScript errors might not propagate correctly
   - Need better error messages if localStorage fails

4. **Testing needed**
   - This is theoretical - needs actual browser testing
   - May need adjustments based on how NiceGUI's `run_javascript()` works
