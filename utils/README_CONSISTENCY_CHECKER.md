# Documentation Consistency Checker

## Overview

`check_docs_consistency2.py` analyzes documentation and source code to identify inconsistencies between:
- Code and comments
- Documentation files
- Python and JSON configuration files

## Recent Fix: Robust JSON Parsing

### Problem
The script would fail to parse Claude API responses when the API returned JSON wrapped in markdown code blocks, even though the prompt explicitly requested plain JSON. This happened intermittently, causing warnings like:

```
Warning: Could not parse Claude's response for src/pc.py
  Response started with: ```json
```

### Solution
Implemented a robust markdown-aware JSON extractor (`json_extractor.py`) that:

1. **Multiple parsing strategies**: Tries 6 different methods to extract valid JSON:
   - Direct JSON parsing (if already clean)
   - Extraction from ````json` code blocks
   - Extraction from plain ``` code blocks
   - Finding embedded markdown blocks anywhere in text
   - Pattern matching for JSON arrays/objects
   - Line trimming to remove non-JSON content

2. **Handles edge cases**:
   - Markdown blocks with language tags
   - Extra whitespace and newlines
   - Explanatory text before/after JSON
   - Multiple JSON blocks (uses first valid one)
   - Mixed content with embedded JSON

### Testing

Use the single-file test utility to verify the fix without running the full scan:

```bash
# Test on a specific file
python3 utils/test_consistency_single_file.py src/pc.py

# Test on another file that had issues
python3 utils/test_consistency_single_file.py src/runtime.py
```

The test utility:
- Shows the raw API response (including any markdown)
- Demonstrates the extraction process
- Displays the successfully parsed JSON
- Provides detailed output for debugging

### Files

- `check_docs_consistency2.py` - Main consistency checker (now uses robust parser)
- `json_extractor.py` - Robust JSON extraction with markdown handling
- `test_consistency_single_file.py` - Test utility for single-file analysis

## Usage

### Full Scan (takes hours)
```bash
python3 utils/check_docs_consistency2.py
```

### Single File Test (for debugging)
```bash
python3 utils/test_consistency_single_file.py <path_to_file>
```

### Example Output

When successful, you'll see:
```
Read src/pc.py
✓ Successfully extracted JSON!
Found 3 conflict(s)
```

When it fails (should be rare now):
```
Warning: Could not parse Claude's response for src/pc.py
  Response started with: ...
```

## Technical Details

### JSON Extractor Module

The `extract_json_from_markdown()` function uses multiple strategies in order:

1. **Direct parsing**: `json.loads(text)`
2. **Markdown blocks**: Regex to find and extract from code blocks
3. **Pattern matching**: Find JSON arrays `[...]` or objects `{...}`
4. **Line trimming**: Remove non-JSON lines from start/end

Each strategy validates the result is actually a list or dict (not just valid JSON like a number).

### Why Multiple Strategies?

Claude's API sometimes returns:
- Clean JSON (strategy 1)
- JSON in markdown blocks (strategies 2-3)
- JSON with explanatory text (strategies 4-5)
- Multiple attempts/revisions (uses first valid JSON)

The multi-strategy approach ensures maximum reliability.

## Development Notes

- The extractor includes comprehensive unit tests (`python3 utils/json_extractor.py`)
- Set `verbose=True` when calling `extract_json_from_markdown()` for debugging
- The test utility is essential for quick iteration without waiting hours for full scans
- Always test changes with both `json_extractor.py` tests and `test_consistency_single_file.py`
