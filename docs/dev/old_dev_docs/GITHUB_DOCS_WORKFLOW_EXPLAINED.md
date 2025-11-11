# GitHub Documentation Workflow - Explained

## Status: ✅ WORKING (Fixed in v1.0.103)

## Your Questions Answered

### Q: "What does the GitHub workflow do?"

**A:** The workflow `.github/workflows/docs.yml` automatically builds and deploys the MBASIC documentation website to GitHub Pages.

**What it does:**
1. **Triggers** on every push to `main` that touches:
   - `docs/**` (any documentation file)
   - `mkdocs.yml` (site configuration)
   - `.github/workflows/docs.yml` (the workflow itself)

2. **Builds** the documentation using MkDocs:
   - Converts markdown files to HTML
   - Applies Material theme for professional look
   - Creates navigation from file structure (auto-discovery)
   - Runs in `--strict` mode (treats warnings as errors)

3. **Deploys** to GitHub Pages:
   - Uploads built site as artifact
   - Deploys to `https://[username].github.io/mbasic/`
   - Makes docs accessible to users worldwide

### Q: "Why was it disabled / 150 emails?"

**A:** The workflow was temporarily disabled because it was **failing repeatedly** and sending 150+ notification emails.

**The problem:**
- MkDocs `--strict` mode was enabled (treats warnings as errors)
- There were navigation/link issues in the docs
- Every push triggered build → failed → email notification
- GitHub sends email for EVERY failed build
- Result: Email spam flood

**The fix (v1.0.103):**
- Switched from manual navigation to **auto-discovery** (awesome-pages plugin)
- Simplified `mkdocs.yml` from 77 lines → just a few lines
- Re-enabled strict mode (now works!)
- No more build failures
- No more email spam

### Q: "Who/what uses the help index built at GitHub?"

**A:** Two different things - don't confuse them!

#### 1. Help Indexes (`.json` files) - FOR IN-APP HELP

**Location:** `docs/help/*/search_index.json`, `docs/help/*/merged_index.json`

**Built by:** `utils/build_help_indexes.py` (runs locally or in checkpoint.sh)

**Used by:**
- TK UI help browser (`src/ui/tk_help_browser.py`)
- Curses UI help system (`src/ui/curses_help.py`)
- CLI help system
- **Powers the search function** in the in-app help

**Purpose:** Fast keyword search across help topics without loading all markdown files

**Not related to GitHub:** These are used at runtime by the application

#### 2. MkDocs Build (HTML website) - FOR WEB DOCUMENTATION

**Location:** Built site in `./site/` (not committed), deployed to GitHub Pages

**Built by:** GitHub Actions workflow → `mkdocs build`

**Used by:**
- Web visitors to `https://[username].github.io/mbasic/`
- Online documentation browsing
- Public documentation reference
- Google/search engines

**Purpose:** Professional documentation website accessible to anyone

**Related to GitHub:** This IS the GitHub Pages deployment

### Q: "Does it need to be fixed?"

**A:** NO! It was already fixed in v1.0.103 (October 28, 2025).

**Evidence it's working:**
- Strict mode re-enabled: `mkdocs build --strict --verbose` ✅
- Workflow active in `.github/workflows/docs.yml` ✅
- Comment in workflow: "Strict mode re-enabled after fixing nav structure" ✅
- File moved to history: `FIX_MKDOCS_STRICT_MODE_DONE.md` ✅

## Summary

### The Two Systems

| Aspect | In-App Help Indexes | GitHub Pages Docs |
|--------|-------------------|------------------|
| **What** | JSON search indexes | HTML documentation website |
| **Built by** | `utils/build_help_indexes.py` | `mkdocs build` (GitHub Actions) |
| **When** | Locally or in checkpoint.sh | On push to main (if docs changed) |
| **Used by** | TK/Curses/CLI help systems | Web visitors, Google |
| **Location** | `docs/help/*/search_index.json` | `https://github.io/[user]/mbasic/` |
| **Purpose** | Fast in-app help search | Public documentation website |

### Current Status (v1.0.135)

**In-App Help Indexes:**
- ✅ Built automatically by `checkpoint.sh` when help docs change
- ✅ Working correctly
- ✅ Powers TK UI help browser with comprehensive 582-line guide

**GitHub Pages Docs:**
- ✅ Fixed in v1.0.103 using auto-discovery navigation
- ✅ Strict mode re-enabled (high quality)
- ✅ Workflow active and working
- ✅ No more email spam

## What Changed in v1.0.103

**Before (broken):**
- Manual navigation in `mkdocs.yml` with 77 lines of nav structure
- Strict mode failed on nav warnings
- Workflow disabled to stop email spam

**After (fixed):**
- Auto-discovery using `mkdocs-awesome-pages-plugin`
- Clean `mkdocs.yml` with just theme/plugins
- Strict mode re-enabled and passing
- Workflow active and deploying successfully

**The magic:** Awesome Pages plugin automatically discovers markdown files and builds navigation without manual configuration. This means:
- No more broken nav references
- New docs appear automatically
- Strict mode passes
- No maintenance needed

## GitHub Pages Visibility

### Is it publicly readable?

**YES** - GitHub Pages sites are **publicly accessible** by default, even if your repository is private!

**Your site URL:** `https://avwohl.github.io/mbasic/`

**Visibility:**
- If your repo is **public** → Docs are public (anyone can read)
- If your repo is **private** → Docs are STILL public by default!
- GitHub Pages is designed for public documentation

### How to check if it's deployed:

1. Visit: `https://avwohl.github.io/mbasic/`
2. If you see documentation → it's public
3. If you get 404 → either not deployed yet or disabled

### How to disable GitHub Pages (if you want privacy):

**Option 1: Disable the workflow (keeps repo, stops deployment)**
```bash
# Rename to disable
mv .github/workflows/docs.yml .github/workflows/docs.yml.disabled
git add .github/workflows/
git commit -m "Disable docs deployment until ready for public release"
git push
```

**Option 2: Delete deployed site on GitHub:**
1. Go to: `https://github.com/avwohl/mbasic/settings/pages`
2. Under "Source" → Select "None"
3. Click "Save"
4. Site will be unpublished (404)

**Option 3: Make site private (requires GitHub Pro/Enterprise):**
- GitHub Pages can be made private with paid plans
- Free plans only support public pages

### Recommended approach before open source release:

**If you want docs private now:**
```bash
# Disable workflow
mv .github/workflows/docs.yml .github/workflows/docs.yml.disabled

# Or just remove the file
rm .github/workflows/docs.yml

# Commit
./checkpoint.sh "Disable public docs deployment until ready for release"
```

**When ready for open source:**
```bash
# Re-enable workflow
git mv .github/workflows/docs.yml.disabled .github/workflows/docs.yml

# Or restore the file
# Commit
./checkpoint.sh "Enable public documentation deployment"
```

The workflow will automatically deploy on next push that touches docs!

## For the Future

### When adding documentation:

**In-App Help (`docs/help/`):**
1. Add/edit markdown files
2. Run `./checkpoint.sh "message"` - automatically rebuilds indexes
3. Test in TK UI (Ctrl+?) or Curses UI

**Web Docs (any `docs/`):**
1. Add/edit markdown files
2. Commit and push to main
3. GitHub Actions automatically builds and deploys
4. Check `https://[username].github.io/mbasic/` in ~2 minutes

### If workflow fails:

1. Check GitHub Actions tab for error details
2. Run `mkdocs build --strict --verbose` locally to reproduce
3. Fix markdown errors (broken links, missing files, etc.)
4. Commit and push - workflow will retry

### The "150 emails" will never happen again because:

- Auto-discovery handles navigation automatically
- Strict mode passes (we fixed the issues)
- Workflow only runs when docs actually change
- No more manual nav maintenance → no more nav errors

## References

- Workflow: `.github/workflows/docs.yml`
- Configuration: `mkdocs.yml`
- Fix commit: `829b278` (v1.0.103)
- Help indexes: Built by `utils/build_help_indexes.py`
- Checkpoint: `checkpoint.sh` auto-rebuilds help indexes
