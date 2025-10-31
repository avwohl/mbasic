# Classic BASIC Games

This directory contains 106 classic BASIC games recently downloaded from various archives.

## Status

**Most games are currently UNTESTED and may not run correctly.**

These programs were written for various BASIC dialects and may require fixes to work with MBASIC 5.21.

### Working Games

- **superstartrek.bas** - Fixed and tested (briefly). The classic Super Star Trek game should be playable.

### Known Issues

Many games may have:
- Missing spaces after keywords (THEN, GOTO, etc.)
- Syntax differences from MBASIC 5.21
- Unsupported features or commands
- Logic errors or bugs

## Fixing Games

If you find issues with any game, you can:

1. Use the `utils/fix_keyword_spacing.py` utility to fix missing spaces after keywords:
   ```bash
   python3 utils/fix_keyword_spacing.py games/gamename.bas --execute
   ```

2. Report problems or contribute fixes

## Running Games

To play a game:

```bash
python3 mbasic games/gamename.bas
```

## Feedback

Please report any:
- Games that work correctly
- Bugs or errors you encounter
- Fixes you've made

This will help improve both the games collection and the MBASIC interpreter.
