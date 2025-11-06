# Parsed Inconsistencies

## Overview

This directory contains a parsed and structured version of the inconsistencies report from `docs/history/docs_inconsistencies_report-v7.md`.

## Files

- **parsed_inconsistencies.json** - Structured JSON containing all 467 parsed issues
- **PARSED_INCONSISTENCIES_README.md** - This file

## Statistics

- **Total Issues:** 467
- **High Severity:** 41 (needs immediate attention)
- **Medium Severity:** 188 (should be addressed)
- **Low Severity:** 238 (minor improvements)

### Issue Type Breakdown

- `documentation_inconsistency`: 212 issues
- `code_vs_comment`: 173 issues
- `code_vs_documentation`: 38 issues
- `code_internal_inconsistency`: 21 issues
- Others: 23 issues

### Files with Most Issues

1. `src/ui/tk_ui.py` - 29 issues (4 high, 12 medium, 13 low)
2. `src/ui/curses_ui.py` - 28 issues (3 high, 13 medium, 12 low)
3. `src/ui/web/nicegui_backend.py` - 27 issues (3 high, 12 medium, 12 low)
4. `src/interpreter.py` - 24 issues (3 high, 12 medium, 9 low)
5. `src/parser.py` - 18 issues (0 high, 7 medium, 11 low)

## JSON Structure

```json
{
  "metadata": {
    "source_file": "docs/history/docs_inconsistencies_report-v7.md",
    "generated_date": "2025-11-05",
    "total_issues": 467,
    "code_comment_conflicts": 183,
    "other_inconsistencies": 284
  },
  "issues_by_severity": {
    "high": [ ... ],
    "medium": [ ... ],
    "low": [ ... ]
  }
}
```

Each issue has:
- `severity`: "high", "medium", or "low"
- `type`: Issue classification (e.g., "code_vs_comment", "documentation_inconsistency")
- `description`: Brief summary of the issue
- `affected_files`: List of file paths involved
- `details`: Full details and context

## Using the Query Tool

A helper script is available to filter and search issues:

```bash
# Show all high severity issues
python3 utils/query_inconsistencies.py --severity high

# Show issues for a specific file
python3 utils/query_inconsistencies.py --file src/interpreter.py

# Show issues of a specific type
python3 utils/query_inconsistencies.py --type code_vs_comment

# Search for specific keywords
python3 utils/query_inconsistencies.py --search "GOTO"

# Combine filters
python3 utils/query_inconsistencies.py --severity high --file src/interpreter.py --details

# Export filtered results to JSON
python3 utils/query_inconsistencies.py --severity high --output high_priority.json

# Just get a count
python3 utils/query_inconsistencies.py --file src/interpreter.py --count
```

## Using jq for Queries

If you have `jq` installed, you can query the JSON directly:

```bash
# Get all high severity issues
jq ".issues_by_severity.high[]" docs/dev/parsed_inconsistencies.json

# Get issues affecting a specific file
jq '.issues_by_severity[][] | select(.affected_files[] | contains("src/interpreter.py"))' docs/dev/parsed_inconsistencies.json

# Get all code_vs_comment issues
jq '.issues_by_severity[][] | select(.type | contains("code_vs_comment"))' docs/dev/parsed_inconsistencies.json

# Count issues by file
jq -r '.issues_by_severity[][] | .affected_files[]' docs/dev/parsed_inconsistencies.json | sort | uniq -c | sort -rn

# Get issue descriptions for a file
jq -r '.issues_by_severity[][] | select(.affected_files[] | contains("src/interpreter.py")) | "\(.severity): \(.description)"' docs/dev/parsed_inconsistencies.json
```

## Using Python

```python
import json

# Load issues
with open('docs/dev/parsed_inconsistencies.json', 'r') as f:
    data = json.load(f)

# Get all high severity issues
high_issues = data['issues_by_severity']['high']

# Filter by file
interpreter_issues = [
    issue for issue in data['issues_by_severity']['high']
    if 'src/interpreter.py' in issue['affected_files']
]

# Filter by type
comment_issues = [
    issue for severity in ['high', 'medium', 'low']
    for issue in data['issues_by_severity'][severity]
    if 'code_vs_comment' in issue['type']
]

# Group by file
from collections import defaultdict
by_file = defaultdict(list)
for severity in ['high', 'medium', 'low']:
    for issue in data['issues_by_severity'][severity]:
        for file in issue['affected_files']:
            by_file[file].append(issue)
```

## Workflow Recommendations

1. **Start with high severity issues** - These need immediate attention
2. **Group by file** - Fix all issues in one file at once for efficiency
3. **Focus on code_vs_comment issues** - These often indicate actual bugs or missing functionality
4. **Use the query tool** - Filter issues to create manageable work batches
5. **Track progress** - Export filtered results to separate JSON files as you work through them

## Example Workflow

```bash
# 1. Create a high priority work list
python3 utils/query_inconsistencies.py --severity high --output work/high_priority.json

# 2. Start with the most affected file
python3 utils/query_inconsistencies.py --file src/ui/tk_ui.py --severity high --details

# 3. As you fix issues, you can search for specific patterns
python3 utils/query_inconsistencies.py --search "docstring" --type code_vs_comment --count

# 4. Track specific issue types
python3 utils/query_inconsistencies.py --type code_internal_inconsistency --output work/refactoring_needed.json
```

## Notes

- The original report claimed 705 issues, but parsing extracted 467 distinct issues
- Some issues may have been consolidated or mis-formatted in the original report
- The parser focuses on the standard issue format and may have skipped malformed entries
- All issues are preserved with full details, description, and affected files
