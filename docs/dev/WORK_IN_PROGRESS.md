# Work in progress: fix GitHub issues #30 to #57

Task: fix the divergences from MBASIC 5.21 that are filed as issues #30 to
#57 (see `docs/dev/MBASIC_521_DIVERGENCES_TODO.md`).

Status: a workflow fixes the issues on eight branches. Each branch gets three
reviews (correctness, fidelity to the binary, tests) and fix rounds.

Branches:

- `fix-on-error`: #37, #44, #45, #46, #47
- `fix-string-file-errors`: #30, #31, #32, #33
- `fix-load-merge`: #34, #35, #36
- `fix-int16-checks`: #42, #43, #56
- `fix-js-backend`: #40, #41, #55 (JavaScript), #57
- `fix-c-backend-ops`: #54, #55 (C)
- `fix-ui-prompts`: #48, #49, #50, #51
- `fix-entry-time`: #38, #39, #52, #53

Next steps:

1. Merge the branches on an integration branch and resolve conflicts.
2. Run `python3 tests/run_regression.py` (baseline: 41 passed, 9 failed for
   missing urwid, nicegui or tk, 19 skipped) and the corpus load check.
3. Fast-forward main, delete this file, run `./utils/checkpoint.sh`.
