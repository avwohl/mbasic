# Feature Completion Requirements

## The 5 Requirements

**A feature is NOT complete until ALL of these exist:**

1. **Implementation** - Code that makes it work
2. **Canonical List Entry** - Added to `docs/dev/ALL_FEATURES_CANONICAL_NAMES.txt`
3. **Feature Tracking Entry** - Added to `docs/dev/UI_FEATURE_PARITY_TRACKING.md` with status for ALL UIs
4. **Documentation** - User-facing docs in `docs/help/` or `docs/user/`
5. **Tests** - At minimum, manual test procedure documented

**NEVER mark a feature as "100% complete" or "✅ Done" without ALL FIVE.**

## Why This Matters: Real Examples

### Auto-numbering Bug (2025-01)
- **What happened**: Auto-numbering was marked "working" in Web UI but never tested
- **Result**: Broken for months - JavaScript selector was wrong, function wasn't async
- **Lesson**: "Implemented" ≠ "Tested". Silent failures in UI code went undetected.

### Settings Feature Gap (2025-01)
- **What happened**: Settings system existed but wasn't in canonical list or tracking table
- **Result**: Web UI gap went unnoticed - no settings dialog implemented
- **Lesson**: If not in canonical list → not tracked → gaps invisible

### Games Library (2025-01)
- **What happened**: Games Library implemented but not tracked in feature parity table
- **Result**: Appeared "missing" despite being functional
- **Lesson**: Without tracking entry, work becomes invisible

## Process for Adding a Feature

### Step-by-Step Checklist

1. **Implement the code**
   - Write the functionality
   - Test it works in at least one UI

2. **Add to canonical list** (`docs/dev/ALL_FEATURES_CANONICAL_NAMES.txt`)
   - Insert alphabetically
   - Use consistent naming with existing features
   - Example: "Settings Dialog" not "Settings" or "Configuration"

3. **Add to feature tracking** (`docs/dev/UI_FEATURE_PARITY_TRACKING.md`)
   - Find appropriate category (or create new one)
   - Add row with feature name
   - Document status for EACH UI:
     - CLI, Curses, TK, Web, Visual
   - Use status format: `[Implementation|Documentation|Testing]`
     - `[✅|✅|✅]` - All three complete
     - `[✅|📚|🧪]` - Implemented but needs docs/tests
     - `[❌|❌|❌]` - Not implemented

4. **Write user documentation**
   - Language features → `docs/help/common/statements/` or `docs/help/common/functions/`
   - UI features → `docs/help/ui/{backend}/`
   - External guides → `docs/user/`
   - Include examples and usage notes

5. **Create test procedure**
   - Automated test: Add to test suite (preferred)
   - Manual test: Document procedure in `docs/dev/` or in tracking table notes
   - Minimum: Written steps to verify feature works

6. **Mark as complete**
   - Only mark `[✅|✅|✅]` when all above exist
   - If any element missing, use `[✅|📚|🧪]` or similar

### Quick Reference

```
Before: Feature idea
↓
Step 1: Write code, test it works
↓
Step 2: Add to ALL_FEATURES_CANONICAL_NAMES.txt (alphabetically)
↓
Step 3: Add to UI_FEATURE_PARITY_TRACKING.md (all UIs documented)
↓
Step 4: Write user-facing documentation
↓
Step 5: Create test (automated or documented manual procedure)
↓
After: Feature complete! Mark [✅|✅|✅] in tracking table
```

## Red Flags: Incomplete Features

Watch for these warning signs:

| Red Flag | Why It's Incomplete | What's Missing |
|----------|-------------------|----------------|
| "Code exists" but no docs | Users can't discover or use feature | Documentation (#4) |
| "Marked as working" but no tests | May be silently broken | Tests (#5) |
| "In tracking table" but not in canonical list | Not properly registered, may be lost | Canonical entry (#2) |
| "Working in one UI" but not documented in all UIs | Other UIs show as incomplete | Tracking entry (#3) |
| "Implemented" but not in tracking table | Work is invisible, gaps unnoticed | Tracking entry (#3) |

## Examples

### Complete Feature: FOR...NEXT Loop

1. ✅ **Implementation**: `src/interpreter.py` execute_for(), execute_next()
2. ✅ **Canonical List**: Listed as "FOR...NEXT Loops"
3. ✅ **Feature Tracking**: Category 1, status `[✅|✅|✅]` for all UIs
4. ✅ **Documentation**: `docs/help/common/statements/for.md`
5. ✅ **Tests**: Automated tests in `tests/` directory

Status: **COMPLETE** ✅

### Incomplete Feature: New Feature (Hypothetical)

1. ✅ **Implementation**: Code written in src/interpreter.py
2. ❌ **Canonical List**: Not added to ALL_FEATURES_CANONICAL_NAMES.txt
3. ❌ **Feature Tracking**: Not in UI_FEATURE_PARITY_TRACKING.md
4. ❌ **Documentation**: No help file created
5. ❌ **Tests**: Not tested

Status: **INCOMPLETE** - Only 1/5 requirements met ❌

### Partially Complete: Implemented but Untested

1. ✅ **Implementation**: Code written and manually tested once
2. ✅ **Canonical List**: Added to ALL_FEATURES_CANONICAL_NAMES.txt
3. ✅ **Feature Tracking**: Added to UI_FEATURE_PARITY_TRACKING.md
4. ✅ **Documentation**: Help file exists
5. ❌ **Tests**: No test procedure documented

Status: **INCOMPLETE** - 4/5 requirements met ❌
Tracking status should be: `[✅|✅|🧪]` (needs tests)

## FAQ

### Q: Can I mark a feature complete if only one UI has it?

No. You must document the status in ALL UIs in the tracking table. If only Web UI has it, mark Web as `[✅|✅|✅]` and others as `[❌|❌|❌]`.

### Q: What if a feature doesn't need documentation?

All features need some documentation. Even internal features should have developer documentation explaining what they do and how to use them.

### Q: What counts as "testing"?

Minimum: A written procedure showing how to verify the feature works (can be in tracking table notes).
Better: Manual test script that can be followed step-by-step.
Best: Automated test in test suite.

### Q: What if I'm adding a feature that already exists in some UIs?

Follow all 5 steps:
1. Implement in your UI
2. Ensure it's in canonical list (may already be there)
3. Update tracking table with your UI's status
4. Ensure documentation covers all UIs (add your UI if needed)
5. Test and document test procedure

### Q: Can I defer documentation/testing to later?

You can implement and commit code without completing all 5 requirements, BUT:
- Mark the feature as incomplete in tracking table: `[✅|📚|🧪]`
- Create a TODO file to track remaining work
- Do NOT mark as "100% complete" or `[✅|✅|✅]` until all 5 exist

## Related Documentation

- `docs/dev/ALL_FEATURES_CANONICAL_NAMES.txt` - Master list of all features
- `docs/dev/UI_FEATURE_PARITY_TRACKING.md` - Per-UI implementation status
- `.claude/CLAUDE.md` - Triggers and workflows (lightweight version)
