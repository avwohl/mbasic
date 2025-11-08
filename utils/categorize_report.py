#!/usr/bin/env python3
"""
Categorize inconsistency report items into code changes vs documentation changes.
Code changes: actual behavior/functionality changes
Docs changes: comments, docstrings, markdown files (no behavior changes)
"""

def is_code_change(item_type, description, details):
    """
    Determine if item requires actual code behavior change.

    Code changes: logic bugs, missing implementations, wrong behavior
    Docs changes: misleading comments, incorrect docstrings, but code is correct
    """
    text = (item_type + ' ' + description + ' ' + details).lower()

    # Clear doc-only indicators
    doc_only_patterns = [
        'comment says',
        'comment describes',
        'comment claims',
        'comment at line',
        'docstring says',
        'docstring describes',
        'comment placement',
        'confusing since',
        'see above',
        'contradicts comment',
        'but the comment',
        'misleading comment',
        'comment should clarify',
        'incorrect comment',
        'contradicts typical',
        'needs clarification',
    ]

    # Check if it's clearly about fixing a comment/docstring
    for pattern in doc_only_patterns:
        if pattern in text:
            # But check if it also mentions actual code bugs
            if 'bug' in text or 'incorrect behavior' in text or 'should' in description.lower():
                # Might be both - need to check further
                if 'could cause' in text or 'potential' in text:
                    return True  # Potential code bug
            else:
                return False  # Just doc fix

    # Code behavior change indicators
    code_patterns = [
        'not implemented',
        'stub',
        'missing',
        'bug',
        'incorrect behavior',
        'should',
        'does not',
        'doesn\'t',
        'feature appears to be implemented but not integrated',
        'no evidence',
        'never used',
        'not integrated',
        'no imports',
    ]

    for pattern in code_patterns:
        if pattern in text:
            return True

    # Special cases based on description
    if 'actually consistent' in text:
        return False  # False positive, no change needed

    # Default to doc change if unclear
    return False

# Read entire file
with open('docs/history/docs_inconsistencies_report-v14.md', 'r') as f:
    content = f.read()

# Split into sections (items between ---)
sections = content.split('\n---\n')

code_items = []
doc_items = []

# Keep header
header = sections[0] if sections else ''

for section in sections[1:]:
    if not section.strip():
        continue

    # Extract fields
    lines = section.split('\n')
    item_type = ''
    description = ''
    affected_files = ''
    details = ''

    current_field = None
    for line in lines:
        if line.startswith('####'):
            item_type = line.replace('####', '').strip()
        elif line.startswith('**Description:**'):
            current_field = 'desc'
            description = line.replace('**Description:**', '').strip()
        elif line.startswith('**Affected files:**'):
            current_field = 'files'
        elif line.startswith('**Details:**'):
            current_field = 'details'
        elif current_field == 'desc' and line.strip() and not line.startswith('**'):
            description += ' ' + line.strip()
        elif current_field == 'files' and line.strip().startswith('- `'):
            affected_files += line + '\n'
        elif current_field == 'details' and line.strip() and not line.startswith('**'):
            details += line + '\n'

    # Categorize
    if is_code_change(item_type, description, details):
        code_items.append(section)
    else:
        doc_items.append(section)

# Write code changes
with open('docs/history/code-v14.md', 'w') as f:
    f.write('# Code Behavior Changes Required (v14)\n\n')
    f.write('Generated from docs_inconsistencies_report-v14.md\n')
    f.write('Date: 2025-11-08\n\n')
    f.write('**These items require changes to actual code behavior/functionality.**\n\n')
    f.write('---\n\n')
    for item in code_items:
        f.write(item.strip() + '\n\n---\n\n')

# Write doc changes
with open('docs/history/docs-v14.md', 'w') as f:
    f.write('# Documentation Changes Required (v14)\n\n')
    f.write('Generated from docs_inconsistencies_report-v14.md\n')
    f.write('Date: 2025-11-08\n\n')
    f.write('**These items require documentation updates only (comments, docstrings, markdown files).**\n')
    f.write('**No changes to code behavior.**\n\n')
    f.write('---\n\n')
    for item in doc_items:
        f.write(item.strip() + '\n\n---\n\n')

print(f"✓ Code behavior changes: {len(code_items)}")
print(f"✓ Documentation changes: {len(doc_items)}")
print(f"✓ Total items: {len(code_items) + len(doc_items)}")
print(f"\n📄 Output files:")
print(f"  • docs/history/code-v14.md ({len(code_items)} items)")
print(f"  • docs/history/docs-v14.md ({len(doc_items)} items)")
