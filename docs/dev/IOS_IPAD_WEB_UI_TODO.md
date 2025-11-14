# iOS/iPad Web UI Issues - TODO

## Current Status
Multiple attempts to fix iOS/iPad Safari scrolling and keyboard issues have not resolved the problems. The site works fine on desktop Chrome/Firefox but has serious UX issues on iPad.

## Problems to Solve

### 1. Output Pane Does Not Auto-Scroll
**Issue:** When new output appears (e.g., running Super Star Trek), the output pane does not automatically scroll to show the latest output at the bottom.

**What was tried:**
- Multiple `setTimeout()` calls at different intervals (0ms, 10ms, 50ms, 100ms, 200ms)
- `requestAnimationFrame()` for scroll timing
- Removing `.update()` to avoid re-render
- Adding `.update()` back
- Scroll event listeners to track user position
- Always scrolling vs conditional scrolling

**Current code:** `src/ui/web/nicegui_backend.py` lines ~3234-3260

### 2. Window/Page Scrolling Instead of Output Pane
**Issue:** The entire page scrolls (showing/hiding menu/toolbar) instead of only the output pane scrolling.

**What was tried:**
- `position: fixed` on html/body
- `overflow: hidden !important` on html/body/#app
- `touch-action: none` on html/body
- `touch-action: pan-y` on output textarea
- Changed from `height: 100vh` to `height: 100%`
- Multiple combinations of the above

**Current code:** `src/ui/web/nicegui_backend.py` lines ~1298-1337

### 3. iOS Keyboard Accessory Bars Cover Output
**Issue:** When input field is focused (for INPUT statement), iOS shows:
- Formatting toolbar (B, I, microphone icons)
- AutoFill bar (passwords, credit card, location icons)

These bars cover the bottom 2-3 lines of output.

**What was tried:**
- Disabling auto-focus on input fields
- Re-enabling auto-focus after shrinking output pane
- `max-height: 40vh` on output pane
- Aggressive blur after input completes
- `autocomplete=off autocorrect=off autocapitalize=off spellcheck=false`

**Current code:** Output pane height limit in line ~1438, input props in line ~1360

### 4. Manual Scroll "Snaps Back"
**Issue:** When user manually scrolls output pane to review old output, it briefly shows the scrolled position then snaps back to middle or top.

**What was tried:**
- Scroll event listeners to detect user scroll
- Tracking `userScrolledUp` state to disable auto-scroll
- Removing auto-scroll entirely
- Various timing of scroll attempts

## Environment
- **Device:** iPad (iOS Safari)
- **Site:** https://mbasic.awohl.com
- **Current Version:** 1.0.937
- **Working On:** Desktop Chrome/Firefox (Windows)

## Next Steps (For Test Machine)

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
- Mobile web best practices: https://web.dev/mobile/

## Status
**TODO** - Needs testing on dedicated test machine, not production site.

Last updated: 2025-11-14
