#!/usr/bin/env python3
"""
Categorize v18 consistency report into docs-only and code behavior issues.

Docs issues = Documentation, comments, docstrings that don't change code behavior
Code issues = Bug fixes, logic errors, missing functionality that changes behavior
"""

import re
import sys

def is_code_behavior_issue(issue_text):
    """Determine if an issue affects code behavior vs just documentation."""

    issue_lower = issue_text.lower()

    # Strong indicators of code behavior issues
    code_indicators = [
        'never populated', 'not populated', 'never called', 'never used',
        'keyerror', 'attributeerror', 'typeerror', 'runtimeerror',
        'undefined reference', 'missing #include', 'will not compile',
        'compilation fails', 'incorrect result', 'wrong value',
        'logic error', 'bug', 'broken', 'fails to', 'crash',
        'exception not handled', 'bare except', 'swallows exception',
        'infinite loop', 'memory leak', 'resource leak',
        'clear_execution_state() doesn\'t clear',
        'editor_lines dict is referenced in multiple methods but never populated',
        'contradicts actual behavior', 'implementation doesn\'t match',
        'code doesn\'t match', 'incorrect implementation',
        'missing validation', 'no error handling', 'unhandled',
        'fallback doesn\'t work', 'dead code executed', 'unreachable executed',
        'inconsistent lifecycle creates orphaned',
        'contradicts when it\'s raised', 'validation missing',
        'sync fails', 'orphaned io handlers', 'state corruption',
        'method never exists', 'field never set', 'variable undefined',
        'function missing', 'not implemented but called',
        'circular dependency', 'import error', 'module not found',
        'prevents execution', 'causes error', 'will fail',
        'produces incorrect', 'calculates wrong', 'returns wrong',
        'doesn\'t preserve', 'loses data', 'corrupts state',
        'race condition', 'thread safety', 'concurrent access'
    ]

    for indicator in code_indicators:
        if indicator in issue_lower:
            return True

    # Check if affected files are pure documentation
    affected_match = re.search(r'\*\*Affected files:\*\*\s*\n((?:- `[^`]+`\s*\n)+)', issue_text)
    if affected_match:
        affected_files = affected_match.group(1)
        files = re.findall(r'- `([^`]+)`', affected_files)

        # If ALL files are .md files in docs/ directories, it's documentation only
        if files and all(f.endswith('.md') and 'docs/' in f for f in files):
            return False

        # If ALL files are .json keybinding files, it's documentation only
        if files and all('keybindings.json' in f for f in files):
            return False

    # Documentation-only indicators (must not have code indicators)
    if any(indicator in issue_lower for indicator in [
        'documentation inconsistency', 'documentation_inconsistency',
        'comment could be clearer', 'docstring could be clearer',
        'wording is confusing', 'phrasing is unclear',
        'description is incomplete', 'should be documented better',
        'cross-reference missing', 'see also section',
        'example formatting', 'markdown formatting',
        '{{kbd:', 'keyboard shortcut placeholder',
        'template placeholder', 'placeholder not replaced',
        'help text', 'user guide', 'reference manual',
        'comment only', 'docstring only', 'documentation only'
    ]):
        return False

    # Check for explicit "comment vs" markers - these are usually doc issues
    if any(marker in issue_text for marker in [
        '#### Code vs Comment conflict\n\n**Description:** Comment',
        '#### code_vs_comment\n\n**Description:** Comment',
        '#### Documentation inconsistency\n\n**Description:**'
    ]):
        # But check if the comment mismatch causes actual code problems
        if any(problem in issue_lower for problem in [
            'code will fail', 'causes exception', 'undefined behavior',
            'produces error', 'will crash', 'data loss'
        ]):
            return True
        return False

    # Default: if unclear and contains "code" in the description type, treat as code
    if '#### code_' in issue_text.lower() or '#### Code ' in issue_text:
        return True

    # Default: documentation issue
    return False

def main():
    input_file = '/home/wohl/cl/mbasic/docs/history/docs_inconsistencies_report-v18.md'
    docs_file = '/home/wohl/cl/mbasic/docs/history/docs-v18.md'
    code_file = '/home/wohl/cl/mbasic/docs/history/code-v18.md'

    with open(input_file, 'r') as f:
        content = f.read()

    # Split by severity sections
    sections = re.split(r'(^### [🔴🟡🟢] (?:High|Medium|Low) Severity\s*\n)', content, flags=re.MULTILINE)

    # Extract header (everything before first severity section)
    header = sections[0]

    # Group sections with their headers
    severity_sections = []
    for i in range(1, len(sections), 2):
        if i+1 < len(sections):
            severity_header = sections[i]
            severity_content = sections[i+1]
            severity_sections.append((severity_header, severity_content))

    # Categorize issues within each severity
    docs_content = {'🔴': [], '🟡': [], '🟢': []}
    code_content = {'🔴': [], '🟡': [], '🟢': []}

    for severity_header, severity_content in severity_sections:
        # Extract severity level emoji
        severity_match = re.search(r'[🔴🟡🟢]', severity_header)
        if not severity_match:
            continue
        severity = severity_match.group(0)

        # Split into individual issues
        issues = re.split(r'\n(?=####\s)', severity_content)

        for issue in issues:
            if not issue.strip() or issue.strip() == '---':
                continue

            # Categorize
            if is_code_behavior_issue(issue):
                code_content[severity].append(issue)
            else:
                docs_content[severity].append(issue)

    # Write docs file
    with open(docs_file, 'w') as f:
        f.write("# Documentation Consistency Report (v18)\n\n")
        f.write("Generated: 2025-11-09 21:24:14\n")
        f.write("Category: Documentation, comments, and docstring issues only\n")
        f.write("Status: Issues that do NOT change code behavior\n\n")

        for severity, emoji_name in [('🔴', 'High'), ('🟡', 'Medium'), ('🟢', 'Low')]:
            if docs_content[severity]:
                f.write(f"## {severity} {emoji_name} Severity\n\n")
                for issue in docs_content[severity]:
                    f.write(issue)
                    if not issue.endswith('\n'):
                        f.write('\n')
                    f.write('---\n\n')

        # Summary
        total = sum(len(docs_content[s]) for s in docs_content)
        f.write(f"## Summary\n\n")
        f.write(f"- Total documentation issues: {total}\n")
        f.write(f"- High severity: {len(docs_content['🔴'])}\n")
        f.write(f"- Medium severity: {len(docs_content['🟡'])}\n")
        f.write(f"- Low severity: {len(docs_content['🟢'])}\n")

    # Write code file
    with open(code_file, 'w') as f:
        f.write("# Code Behavior Issues Report (v18)\n\n")
        f.write("Generated: 2025-11-09 21:24:14\n")
        f.write("Category: Code behavior changes, bug fixes, logic errors\n")
        f.write("Status: Issues that CHANGE what the code does\n\n")

        for severity, emoji_name in [('🔴', 'High'), ('🟡', 'Medium'), ('🟢', 'Low')]:
            if code_content[severity]:
                f.write(f"## {severity} {emoji_name} Severity\n\n")
                for issue in code_content[severity]:
                    f.write(issue)
                    if not issue.endswith('\n'):
                        f.write('\n')
                    f.write('---\n\n')

        # Summary
        total = sum(len(code_content[s]) for s in code_content)
        f.write(f"## Summary\n\n")
        f.write(f"- Total code behavior issues: {total}\n")
        f.write(f"- High severity: {len(code_content['🔴'])}\n")
        f.write(f"- Medium severity: {len(code_content['🟡'])}\n")
        f.write(f"- Low severity: {len(code_content['🟢'])}\n")

    # Print summary
    total_docs = sum(len(docs_content[s]) for s in docs_content)
    total_code = sum(len(code_content[s]) for s in code_content)
    print(f"✓ Created {docs_file}")
    print(f"  Documentation issues: {total_docs} (High: {len(docs_content['🔴'])}, Medium: {len(docs_content['🟡'])}, Low: {len(docs_content['🟢'])})")
    print(f"✓ Created {code_file}")
    print(f"  Code behavior issues: {total_code} (High: {len(code_content['🔴'])}, Medium: {len(code_content['🟡'])}, Low: {len(code_content['🟢'])})")
    print(f"Total issues processed: {total_docs + total_code}")

if __name__ == '__main__':
    main()
