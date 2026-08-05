# iOS/iPad Web UI Issues - TODO

## Current Status (2025-11-14)
Implemented new approach using CSS media queries and smart scroll tracking to fix iOS/iPad issues without breaking desktop.

**Previous attempts:** Multiple iOS fixes broke desktop by applying `position: fixed` and `max-height: 40vh` globally.

**New implementation (dev branch):**
1. CSS media queries (max-width: 768px) - iOS fixes only apply to mobile
2. Smart scroll tracking - respects user scroll position, only auto-scrolls when at bottom
3. Desktop unaffected - no changes to desktop layout

**Testing needed:** iPad Safari to verify fixes work

## Problems to Solve

### 0. Desktop Regression - Blank Area at Bottom
**Status:** ✅ FIXED - Reverted all global iOS fixes, desktop works perfectly again

**Solution:** All iOS-specific CSS now in `@media (max-width: 768px)` block (lines ~1321-1345)

**Commit:** 0ca9813b - Revert all iOS/iPad scrolling fixes - they broke desktop Chrome

### 1. Output Pane Does Not Auto-Scroll
**Status:** 🔧 IN PROGRESS - New implementation using scroll event tracking

**Solution implemented (dev branch):**
- JavaScript scroll event listener tracks if user is at bottom (within 50px)
- Auto-scroll only happens if user hasn't manually scrolled up
- Uses `textarea.dataset.userScrolledUp` to persist state
- Event listener installed once per textarea on first output

**Code:** `src/ui/web/nicegui_backend.py` lines ~3245-3272

**Testing needed:** Verify auto-scroll works on iPad Safari

### 2. Window/Page Scrolling Instead of Output Pane
**Status:** 🔧 IN PROGRESS - Media query solution implemented

**Solution implemented (dev branch):**
- CSS media query `@media (max-width: 768px)` for mobile only
- `position: fixed` on html/body/#app (mobile only)
- `touch-action: none` on body, `touch-action: pan-y` on output textarea (mobile only)
- Desktop unaffected - keeps original simple CSS

**Code:** `src/ui/web/nicegui_backend.py` lines ~1322-1345

**Testing needed:** Verify page doesn't scroll on iPad Safari, only output pane scrolls

### 3. iOS Keyboard Accessory Bars Cover Output
**Status:** 🔧 IN PROGRESS - Reserved space with media query

**Solution implemented (dev branch):**
- `max-height: 50vh` on output textarea (mobile only via media query)
- Reserves top half of screen for output, bottom half for keyboard
- Desktop keeps full height since media query doesn't apply

**Code:** `src/ui/web/nicegui_backend.py` line ~1343

**Testing needed:** Verify keyboard doesn't cover output on iPad Safari

### 4. Manual Scroll "Snaps Back"
**Status:** 🔧 IN PROGRESS - Fixed with scroll event tracking

**Solution implemented (dev branch):**
- Scroll event listener detects when user scrolls up
- Auto-scroll is disabled when `userScrolledUp` is true
- Automatically re-enables when user scrolls back to bottom
- No more fighting between user scroll and auto-scroll

**Code:** `src/ui/web/nicegui_backend.py` lines ~3260-3264

**Testing needed:** Verify can scroll up on iPad and position is maintained

## Environment
- **Device:** iPad (iOS Safari)
- **Site:** https://mbasic.awohl.com (main branch), dev branch for testing
- **Current Version:** main: 1.0.938, dev: testing new approach
- **Desktop Status:** ✅ Working perfectly on Chrome/Firefox (Windows/Linux)

## Implementation Summary (Dev Branch)

### Changes Made
1. **CSS Media Queries** - All iOS fixes now in `@media (max-width: 768px)`:
   - `position: fixed` on html/body/#app (prevents page scroll)
   - `touch-action: none` on body (blocks page gestures)
   - `touch-action: pan-y` on output textarea (allows vertical scroll)
   - `max-height: 50vh` on output textarea (reserves space for keyboard)

2. **Smart Scroll Tracking** - JavaScript detects user scroll intent:
   - Scroll event listener tracks position
   - `userScrolledUp` flag prevents auto-scroll when user scrolls up
   - Auto-scroll only when user is at bottom (within 50px)
   - State persists via `dataset` attributes

### Advantages of This Approach
- ✅ Desktop completely unaffected (no media query match)
- ✅ No global CSS changes that break layout
- ✅ Respects user scroll position
- ✅ Easier to debug (inspect media query in Safari DevTools)
- ✅ Can adjust breakpoint if 768px isn't ideal

### Testing Checklist (iPad Safari)
- [ ] Output auto-scrolls when program runs
- [ ] Can manually scroll up to review old output
- [ ] Manual scroll position is maintained (doesn't snap back)
- [ ] Page doesn't scroll (menu/toolbar stay visible)
- [ ] Keyboard doesn't cover output when typing INPUT
- [ ] Desktop Chrome still works (no blank area)

## Next Steps

### Approach 1: Use Native Mobile Framework
Consider building a dedicated iOS app using:
- React Native with native ScrollView
- Flutter with native scrolling widgets
- Native Swift/UIKit app

This would give full control over scroll behavior and keyboard handling.

### Approach 2: Different Web Framework
Try replacing NiceGUI with a framework that has better mobile support:
- React with mobile-first CSS framework
- Vue with Ionic
- Plain HTML/CSS/JS with careful mobile testing

### Approach 3: Debugging on Actual Device
Set up remote debugging:
- Enable Safari Web Inspector on iPad
- Connect iPad to Mac
- Debug live in Safari DevTools
- See actual CSS computed values and scroll events
- Test scroll behavior with real touch events

### Approach 4: Simplified Mobile-Only View
Create a separate mobile-optimized view:
- No split panes, just stacked vertically
- Output fills most of screen
- Simple input at bottom
- No rich text editor, just plain textarea
- Minimal UI chrome

## Files Modified During Attempts
- `src/ui/web/nicegui_backend.py` (lines 1298-1337, 1358-1438, 2110-2432, 3230-3260)
- Multiple commits: 1.0.928 through 1.0.937

## Commits to Review
```
a79a6d5b - Fix iPad scrolling issue - only auto-scroll output if user at bottom
eb48a08c - Fix textarea scroll - check position BEFORE value update, not after
01bee319 - Fix iOS scroll and keyboard - remove .update(), force blur, disable autocomplete
c381eaaf - Disable auto-focus on input field - prevents iOS keyboard from hiding output
836cf7d8 - Fix iOS page scrolling - use position:fixed to lock viewport, always auto-scroll output
c017bcd7 - Disable editor auto-focus on load and aggressively blur all inputs
58d77cab - Shrink output pane to 40vh max height - prevents iOS keyboard from covering it
bf96dffa - Fix auto-scroll and prevent window scrolling with touch-action
```

## References
- NiceGUI docs: https://nicegui.io/
- iOS Safari quirks: https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/
- Mobile web best practices: https://web.dev/learn/design/

## Status
**TODO** - Needs testing on dedicated test machine, not production site.

Last updated: 2025-11-14
