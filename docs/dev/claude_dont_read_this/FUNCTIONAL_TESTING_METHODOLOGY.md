# Functional Testing Methodology for UI Features

**Status:** ⏳ In Development
**Created:** 2025-10-29
**Purpose:** Document how to functionally test UI features to ensure they actually work, not just exist in code

## Problem Statement

During UI feature parity comparisons, we discovered that **code existence ≠ working functionality**:

### Case Study: Web UI Auto-Numbering

**What code inspection showed:**
- ✅ Auto-numbering code exists in `nicegui_backend.py` (lines 918-970)
- ✅ `_on_enter_key()` handler implements line numbering
- ✅ Logic looks correct

**What functional testing revealed:**
- ✅ Works perfectly in **Program Editor** area (top textarea)
- ❌ Doesn't work in **Command** area (bottom textarea)
- 💡 **This is correct behavior** - Command area should execute immediately, not add line numbers

**User experience:**
- User types `k=23` in Command area
- No line number appears
- User reports: "auto-numbering doesn't work"
- Root cause: User typing in wrong area, not a bug

**Lesson:** Code inspection said "feature exists", but didn't reveal **where and when** it works.

## Methodology

### Level 1: Code Inspection (Current Method)

**What it tells you:**
- ✅ Feature code exists
- ✅ Methods are defined
- ✅ Buttons/menus reference the feature

**What it DOESN'T tell you:**
- ❌ Does it actually work?
- ❌ Are there prerequisites or conditions?
- ❌ Is it accessible to users?
- ❌ Are there edge cases or limitations?

**When to use:** Initial discovery, codebase exploration

### Level 2: Manual Functional Testing (Recommended)

**What it tells you:**
- ✅ Feature works end-to-end
- ✅ User can actually access it
- ✅ Edge cases and limitations
- ✅ User experience quality

**Process:**
1. Launch the UI
2. Follow typical user workflow
3. Exercise the feature completely
4. Note any issues, limitations, or UX problems
5. Document actual behavior vs. expected behavior

**When to use:** After code inspection, before marking feature as "complete"

### Level 3: Automated Testing (Future Goal)

**What it tells you:**
- ✅ Feature continues to work after changes
- ✅ No regressions introduced
- ✅ Consistent behavior across releases

**When to use:** For critical features, after manual testing validates behavior

## Testing Checklist Template

For each feature being tested, document:

### Feature Information
```markdown
**Feature:** [Name]
**UI:** [CLI / Curses / Tkinter / Web / Visual]
**Version Tested:** [Version number]
**Tester:** [Name/Role]
**Date:** [YYYY-MM-DD]
```

### Access Testing
- [ ] Can user find the feature? (Menu, button, keyboard shortcut)
- [ ] Is it clearly labeled?
- [ ] Is it in a logical location?

### Functional Testing
- [ ] Does it work in the happy path?
- [ ] Does it handle errors gracefully?
- [ ] Are there prerequisites? (program loaded, program running, etc.)
- [ ] What happens with invalid input?

### Edge Cases
- [ ] Empty program
- [ ] Very large program
- [ ] Program with errors
- [ ] Mid-execution state
- [ ] Rapid repeated actions

### Documentation
- [ ] Is feature documented?
- [ ] Does documentation match actual behavior?
- [ ] Are limitations documented?

### User Experience
- [ ] Is feedback provided? (status messages, visual indicators)
- [ ] Are errors clear and helpful?
- [ ] Does it match user expectations?

## Feature-Specific Test Plans

### Auto-Numbering

**Feature:** Automatic line numbering when pressing Enter

**CLI:**
```
Test: N/A - CLI uses explicit line numbers
Status: Not applicable
```

**Curses:**
```
Test Steps:
1. Launch: python3 mbasic --ui curses
2. In editor, type: PRINT "HELLO"
3. Press Enter
4. Verify: Line becomes "10 PRINT "HELLO""
5. Type: END
6. Press Enter
7. Verify: Line becomes "20 END"

Expected Result: ✅ Auto-numbering works
Edge Cases:
- Does it skip numbers used in pasted code? [TEST]
- Can user override with manual numbers? [TEST]
- What happens after RENUM? [TEST]
```

**Web:**
```
Test Steps:
1. Launch: python3 mbasic --ui web
2. Open browser to localhost:8080
3. Click in **Program Editor** (top large textarea)
4. Type: PRINT "HELLO"
5. Press Enter
6. Verify: Line becomes "10 PRINT "HELLO""
7. Click in **Command** area (bottom small textarea)
8. Type: PRINT "TEST"
9. Press Enter
10. Verify: Command executes immediately, NO line number added

Expected Result:
✅ Auto-numbering works in Program Editor
✅ Auto-numbering DOESN'T work in Command (by design)

Critical: Document where feature works, not just that it exists
```

### Step Line vs Step Statement

**Feature:** Step execution with two modes

**Tkinter:**
```
Test Steps:
1. Launch: python3 mbasic --ui tk
2. Enter program:
   10 X=1: Y=2: PRINT X+Y
   20 END
3. Click "Step" button (or "Step Line" button)
4. Observe: Which statement(s) execute?
5. Click "Stmt" button (or "Step Statement" button)
6. Observe: Which statement(s) execute?

Expected Result:
✅ Step Line: Executes X=1, Y=2, PRINT X+Y (entire line 10)
✅ Step Statement: Executes X=1 only (first statement)

If both buttons do the same thing: ❌ Bug or mislabeled button
```

**Web:**
```
Test Steps:
1. Launch: python3 mbasic --ui web
2. Enter program (in Editor area):
   10 X=1: Y=2: PRINT X+Y
   20 END
3. Click "Step Line" button
4. Check output and status
5. Restart, click "Step Stmt" button
6. Check output and status

Expected Result:
✅ Step Line: All of line 10 executes, shows "3"
✅ Step Stmt: Only X=1 executes, pauses before Y=2

Documentation: Explain difference in help docs
```

### Breakpoints

**Feature:** Set/clear breakpoints, program pauses at breakpoint

**Curses:**
```
Test Steps:
1. Launch with program:
   10 PRINT "Before"
   20 PRINT "At breakpoint"
   30 PRINT "After"
   40 END
2. Set breakpoint at line 20:
   - Press Ctrl+B
   - Enter line number: 20
3. Verify: Line 20 shows breakpoint indicator (●)
4. Press Ctrl+R to run
5. Verify: Program outputs "Before" and pauses at line 20
6. Check status: Should say "at breakpoint" or "paused at line 20"
7. Press Ctrl+G to continue
8. Verify: Outputs "At breakpoint", "After"

Expected Result:
✅ Breakpoint sets/displays correctly
✅ Execution pauses at breakpoint
✅ Continue resumes execution

Edge Cases:
- Breakpoint on non-existent line? [TEST]
- Multiple breakpoints? [TEST]
- Breakpoint on END statement? [TEST]
```

**Web:**
```
Test Steps:
1. Launch web UI
2. Enter program in Editor
3. Run → Toggle Breakpoint
4. Enter line number in dialog
5. Run program
6. Verify execution pauses

Critical Tests:
- Can you see which breakpoints are set? (Visual indicator?)
- Does "Clear All Breakpoints" work?
- Do breakpoints persist after program edit?
- Are breakpoints in Run menu easily discoverable?

Expected Result:
✅ Breakpoint dialog accepts line number
✅ Program pauses at breakpoint
✅ Clear All removes all breakpoints
❓ Visual indication of active breakpoints? [INVESTIGATE]
```

## Common Failure Patterns

### Pattern 1: Feature Exists but Hidden
**Symptom:** Code exists, methods work, but no UI access
**Example:** Web UI breakpoints existed but no menu item
**Detection:** Can you access it without reading code?
**Fix:** Add menu item, button, or keyboard shortcut

### Pattern 2: Feature Works but in Wrong Context
**Symptom:** Feature works, but not where user expects
**Example:** Auto-numbering only in Editor, not Command
**Detection:** Try feature in all relevant contexts
**Fix:** Document where it works, or extend to other contexts

### Pattern 3: Feature Works but Poorly Documented
**Symptom:** Feature works great, documentation is wrong/missing
**Example:** Web UI getting-started described "fantasy UI"
**Detection:** Compare docs to actual behavior
**Fix:** Update documentation to match reality

### Pattern 4: Feature Labeled Ambiguously
**Symptom:** Button exists but unclear what it does
**Example:** "Step" button - does it step line or statement?
**Detection:** User can't predict behavior from label
**Fix:** Rename for clarity, add tooltips/help

### Pattern 5: Feature Half-Implemented
**Symptom:** Some part works, other parts missing
**Example:** Set breakpoint works, but no visual indicator
**Detection:** Exercise full workflow, not just core function
**Fix:** Complete the user experience

## Test Documentation Format

### Per-UI Test Report

```markdown
# [UI Name] Functional Test Report

**Version:** 1.0.XXX
**Date:** YYYY-MM-DD
**Tester:** [Name]

## Test Summary
- Total Features Tested: X
- Pass: Y
- Fail: Z
- Partial: W
- Not Applicable: N

## Feature Test Results

### [Feature Name]
**Status:** ✅ Pass / ❌ Fail / ⚠️ Partial / ➖ N/A

**Access:**
- Menu/Button Location: [Path]
- Keyboard Shortcut: [Key combo]
- Discoverability: [High/Medium/Low]

**Functional Test:**
[Describe what was tested and results]

**Issues Found:**
- [Issue 1]
- [Issue 2]

**Documentation Status:**
- Documented: [Yes/No]
- Accurate: [Yes/No]
- Complete: [Yes/No]

**Recommendations:**
[Suggestions for improvement]

---

[Repeat for each feature]
```

## Integration with Feature Parity Tracking

Update `UI_FEATURE_PARITY_TRACKING.md` testing status:

**Before functional testing:**
```markdown
| **Auto-Numbering** | [✅|📄|⚡] |
```
Meaning: Implemented, code-commented, not tested

**After functional testing:**
```markdown
| **Auto-Numbering** | [✅|📄|🧪] |
```
Meaning: Implemented, code-commented, functionally tested

**Testing Status Legend:**
- 🧪 Automated tests exist
- 🔬 Manual test procedure documented and executed
- 👁️ Visual/manual testing only (informal)
- ⚡ No tests (code inspection only)

## Functional Testing Workflow

### When Adding New Feature

1. **Implement** the feature
2. **Self-test** basic functionality
3. **Document** expected behavior
4. **Create test plan** following template above
5. **Execute test plan** in target UI(s)
6. **Update** feature parity tracking with 🔬 status
7. **Commit** with test results in commit message

### When Comparing UIs

1. **Select feature** to compare
2. **Create test plan** covering all UIs
3. **Execute tests** on each UI
4. **Document** actual behavior vs. expected
5. **Identify gaps:**
   - Missing completely?
   - Hidden (exists but not accessible)?
   - Different behavior?
   - Poorly documented?
6. **Prioritize** fixes based on user impact

### When Reporting Issues

Use this format:

```markdown
**Feature:** [Name]
**UI:** [Which UI]
**Expected Behavior:** [What should happen]
**Actual Behavior:** [What actually happens]
**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Result]

**Test Context:**
- Version: X.X.XXX
- Platform: [OS]
- How accessed: [Menu path / keyboard / button]

**Impact:** [Low/Medium/High] - [Why this matters to users]
```

## Test Automation Strategy (Future)

### Priority for Automation

**High Priority (Automate First):**
- Core execution features (Run, Stop, Step)
- File operations (New, Load, Save)
- Error handling (syntax errors, runtime errors)

**Medium Priority:**
- Debugging features (breakpoints, variable inspection)
- Editor operations (renumber, delete line, insert)

**Low Priority:**
- UI layout and appearance
- Help system navigation
- Settings/preferences

### Automation Tools

**CLI/Curses:**
- Use `pexpect` for terminal interaction
- Existing: `utils/test_curses_comprehensive.py`
- Pattern: Send keys, capture output, verify state

**Tkinter:**
- Use Tkinter's test harness
- Simulate button clicks, menu selections
- Verify widget states

**Web:**
- Use Selenium or Playwright
- Navigate DOM, click elements
- Assert on page content

### Test Coverage Goals

- **Critical features:** 90%+ automated coverage
- **Common features:** 70%+ automated coverage
- **Edge features:** Manual testing acceptable

## Maintenance

### Review Frequency
- Update methodology quarterly
- Review test plans after major UI changes
- Refresh documentation accuracy monthly

### Responsibilities
- **Developers:** Run functional tests before marking features complete
- **Maintainers:** Ensure tests stay updated with UI changes
- **Contributors:** Add test plans for new features

## Example: Complete Feature Test

### Feature: Step Statement Execution (Web UI)

**Test Plan Created:** 2025-10-29
**Test Executed:** 2025-10-29
**Tester:** Claude (AI Assistant)
**Version:** 1.0.300

#### Access Test
- [x] Found in Run menu → "Step Statement"
- [x] Found as toolbar button labeled "Step Stmt"
- [x] Located logically next to "Step Line"

#### Functional Test
- [x] Button click triggers step execution
- [x] Program starts if not running
- [x] Executes exactly one statement
- [x] Status shows current line
- [x] Can step through entire program

#### Edge Cases Tested
- [x] Empty program: Shows warning "No program loaded" ✅
- [x] Program with multi-statement line: Steps one statement at a time ✅
- [x] Rapid clicks: Handles correctly ✅
- [x] Step after error: N/A (program stops on error)

#### Documentation
- [x] Feature documented in getting-started.md
- [x] Example provided showing difference from Step Line
- [x] Documentation matches actual behavior

#### Issues Found
- None

#### User Experience
- [x] Clear visual feedback (status bar updates)
- [x] Intuitive button placement
- [x] Label "Step Stmt" could be clearer (consider "Step Statement")

#### Overall Status: ✅ PASS

**Recommendation:** Consider renaming "Step Stmt" button to "Step Statement" (full word) for clarity, as there's enough toolbar space.

---

## Conclusion

Functional testing is essential for accurate feature parity comparison. **Code inspection finds features; functional testing validates they work.**

The methodology outlined here ensures that when we mark a feature as "implemented," we mean:
1. ✅ Code exists
2. ✅ Feature is accessible in UI
3. ✅ Feature actually works
4. ✅ Documentation is accurate
5. ✅ User experience is acceptable

This prevents the "k=23 didn't auto-number" type of confusion where features work correctly but aren't understood or accessed properly.
