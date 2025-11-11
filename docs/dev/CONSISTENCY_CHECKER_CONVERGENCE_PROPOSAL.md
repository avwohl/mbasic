# Proposal: Fixing the Consistency Checker Convergence Problem

## Executive Summary

After 22 iterations, the consistency checker continues to find the same issues repeatedly. The problem is not that we're choosing wrong resolutions, but that the resolutions are not being completely implemented. This proposal outlines why fixes don't stick and presents a systematic approach to achieve convergence.

## The Problem

### Current Symptoms
1. Issues like "ERL in RENUM" persist across multiple versions (v1 through v22)
2. "FileIO integration status" contradictions remain despite multiple fix attempts
3. Each new report contains 60-90% of the same issues from previous reports

### Root Cause Analysis

The fixes fail to persist because:

#### 1. Incomplete Location Discovery
- Agents find 5 instances of an issue
- Fix those 5 instances
- But 3 more instances exist using slightly different wording
- Next checker run finds those 3 "new" instances

#### 2. Non-Exhaustive Search Patterns
Example with ERL/RENUM:
- Agent searches for "ERL renumbering"
- Misses: "error line renum", "ERL in renum", "renumber.*ERL", "ERL.*comparison"
- Each variation gets found in subsequent runs

#### 3. No Fix Verification
- Agent makes edits to 7 files
- Moves on to next issue immediately
- Never verifies that those 7 files now pass consistency check
- Some edits may have failed or been incomplete

#### 4. Batch Processing Problems
- Agents try to fix 20+ issues in parallel
- Context switching causes incomplete fixes
- No systematic tracking of what was actually changed

## Proposed Solution

### Core Principle: Complete Resolution Before Moving On

One issue must be completely eliminated before addressing the next.

### Implementation Strategy

#### Phase 1: Exhaustive Discovery
```python
def find_all_instances(issue_pattern):
    """Find ALL variations of an issue pattern"""
    variations = generate_search_variations(issue_pattern)
    all_locations = set()

    for variant in variations:
        # Use multiple search tools
        locations = grep(variant)
        locations += ast_search(variant)
        locations += comment_search(variant)
        all_locations.update(locations)

    return all_locations
```

#### Phase 2: Comprehensive Fix
```python
def fix_with_verification(issue, resolution):
    """Fix an issue and verify it's gone"""
    # 1. Find everything
    all_locations = find_all_instances(issue)

    # 2. Document what we're fixing
    log_fixes(issue, all_locations, resolution)

    # 3. Apply fixes
    for location in all_locations:
        apply_fix(location, resolution)

    # 4. Verify immediately
    remaining = check_specific_issue(issue, all_locations)

    # 5. Iterate until gone
    attempts = 0
    while remaining and attempts < 3:
        fix_remaining(remaining)
        remaining = check_specific_issue(issue, all_locations)
        attempts += 1

    # 6. Confirm elimination
    if remaining:
        raise Exception(f"Could not eliminate {issue} after {attempts} attempts")
```

#### Phase 3: Regression Prevention
- Add test case that checks for the specific issue
- Test must pass before moving to next issue
- Test prevents issue from reappearing

### Workflow Changes

#### Current (Failing) Workflow:
1. Run consistency checker → 50 issues found
2. Launch 5 agents to fix issues in parallel
3. Agents make best-effort fixes
4. Next run → 45 issues found (including 40 from before)

#### Proposed (Convergent) Workflow:
1. Run consistency checker → 50 issues found
2. Pick ONE high-impact issue (e.g., "ERL in RENUM")
3. Exhaustively find ALL instances (might find 15 places, not just 7)
4. Fix all 15 with same resolution
5. Immediately verify just this issue is gone
6. If still present, investigate why and fix
7. Add regression test
8. Only then move to issue #2
9. Continue until all issues resolved

### Specific Techniques

#### 1. Search Amplification
For each issue, generate multiple search patterns:
```python
# For "ERL in renum" issue:
patterns = [
    r"ERL.*renum",
    r"renum.*ERL",
    r"error\s+line.*renum",
    r"renumber.*error.*line",
    r"ERL.*renumber",
    r"if\s+ERL\s*[<>=]+\s*\d+",  # The actual code pattern
    # ... etc
]
```

#### 2. Fix Verification Loop
```bash
# After claiming to fix an issue:
./utils/checker/check_single_issue.py "ERL in renum" --files src/parser.py src/interpreter.py ...

# If it returns "Issue still present", do NOT proceed to next issue
```

#### 3. Completeness Tracking
Create a fix manifest for each issue:
```yaml
issue: "ERL in RENUM"
first_seen: v1
attempted_fixes: [v3, v7, v15, v22]
locations_found:
  v22:
    - src/parser.py:1000 (comment)
    - src/interpreter.py:234 (code)
    - docs/help/renum.md:45 (documentation)
    - src/codegen.py:89 (comment)
resolution: "ERL comparison should renumber RHS when RHS is a line number"
fix_verified: false  # Changes to true only when issue doesn't appear in next run
```

## Success Metrics

1. **Convergence Rate**: Issues should decrease monotonically (never increase)
2. **Fix Persistence**: Once an issue is marked fixed, it never reappears
3. **Iteration Count**: Reach zero issues within finite iterations (<30)

## Implementation Plan

### Week 1: Tool Development
- Create `check_single_issue.py` for targeted verification
- Create `find_all_variations.py` for exhaustive search
- Create fix tracking database

### Week 2: Process Testing
- Pick the top 3 persistent issues (ERL/RENUM, FileIO status, etc.)
- Apply complete resolution process to each
- Verify they don't appear in next run

### Week 3: Full Rollout
- Apply process to all remaining issues
- One issue at a time, in severity order
- Track metrics

## Risk Mitigation

### Risk: Fix causes new issues
**Mitigation**: Run full checker after each fix, but only proceed if the target issue is eliminated

### Risk: Some issues are inherent/unfixable
**Mitigation**: Create "acknowledged_inconsistencies.md" for documented architectural decisions

### Risk: Process is too slow
**Mitigation**: Prioritize high-impact issues; accept some low-impact inconsistencies

## Alternative Approaches Considered

1. **Fix Everything At Once**: Doesn't work due to context limits and verification difficulty
2. **Code as Single Source of Truth**: Rejected because code has bugs
3. **Rewrite From Spec**: Too expensive and risks breaking working code

## Conclusion

The current approach fails because it attempts partial fixes without verification. By adopting a systematic "complete resolution" approach with immediate verification, we can achieve convergence within a finite number of iterations.

The key insight: **Don't move to the next issue until the current one is provably eliminated.**

## Next Steps

1. Review and approve this proposal
2. Implement verification tooling
3. Test on one persistent issue (recommend: ERL/RENUM)
4. If successful, roll out to all issues

---

*Proposal Date: 2025-11-10*
*Author: Claude (based on analysis of 22 failed iterations)*
*Status: AWAITING REVIEW*