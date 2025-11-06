# Simple Breakpoint Test

Please run this command and tell me what you see:

```bash
DEBUG_BP=1 python3 mbasic --ui curses test_continue.bas 2>&1 | tee /tmp/test_output.txt
```

Then:
1. **When the IDE opens:**
   - Can you see the program code in the editor?
   - Move cursor to line 20
   - Press 'b'
   - **Question: Do you see a ● symbol appear next to line 20?**

2. **Press Ctrl+R to run**
   - **Question: Do you see output in the output window?**

3. **Press Ctrl+Q to quit**

4. **Run this command:**
   ```bash
   cat /tmp/test_output.txt
   ```

5. **Copy and paste EVERYTHING from that file here**

That will show me exactly what's happening!

---

## Even Simpler: Just Answer These Two Questions

**Question 1:** When you press 'b', do you see a **●** (bullet) symbol appear next to the line number?
- YES or NO?

**Question 2:** When you press Ctrl+R, does program output appear in the bottom window?
- YES or NO?

That's all I need to know to diagnose this!
