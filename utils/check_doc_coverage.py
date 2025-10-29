#!/usr/bin/env python3
"""
Check documentation coverage for MBASIC language features.

Compares implemented functions, statements, and operators against
help documentation to identify missing docs.

Usage:
    python3 utils/check_doc_coverage.py
"""

import re
from pathlib import Path


def normalize_function_name(name):
    """Normalize function name for comparison.

    Converts various representations to a canonical form:
    - STR$ -> STR
    - str_dollar -> STR
    - STR_DOLLAR -> STR
    """
    name = name.upper()
    if name.endswith('$'):
        name = name[:-1]
    if name.endswith('_DOLLAR'):
        name = name[:-7]
    return name


def get_implemented_functions():
    """Extract all function names from basic_builtins.py."""
    builtin_file = Path('src/basic_builtins.py')
    if not builtin_file.exists():
        print(f"Error: {builtin_file} not found")
        return []

    content = builtin_file.read_text()
    # Match: def FUNCTION_NAME(self, ...)
    pattern = r'^\s+def ([A-Z_]+)\(self'
    functions = []
    for match in re.finditer(pattern, content, re.MULTILINE):
        func_name = match.group(1)
        # Normalize: remove _DOLLAR suffix for comparison
        func_name = normalize_function_name(func_name)
        functions.append(func_name)

    return sorted(set(functions))


def get_implemented_statements():
    """Extract statement names from interpreter.py."""
    interp_file = Path('src/interpreter.py')
    if not interp_file.exists():
        print(f"Error: {interp_file} not found")
        return []

    content = interp_file.read_text()
    # Match: def execute_STATEMENT(self, ...)
    pattern = r'def execute_([a-z_]+)\(self'
    statements = []
    for match in re.finditer(pattern, content, re.MULTILINE):
        stmt = match.group(1).upper()
        # Skip internal methods
        if stmt not in ['STATEMENT', 'PROGRAM']:
            statements.append(stmt)

    return sorted(set(statements))


def get_documented_functions():
    """Get list of documented functions from help/common/language/functions/."""
    func_dir = Path('docs/help/common/language/functions')
    if not func_dir.exists():
        print(f"Error: {func_dir} not found")
        return []

    functions = []
    for md_file in func_dir.glob('*.md'):
        if md_file.name == 'index.md':
            continue
        func_name = md_file.stem

        # Handle multi-function docs (e.g., "cvi-cvs-cvd.md")
        if '-' in func_name:
            for part in func_name.split('-'):
                # Normalize each part
                functions.append(normalize_function_name(part))
        else:
            # Normalize: removes _dollar suffix and converts to uppercase
            functions.append(normalize_function_name(func_name))

    return sorted(set(functions))


def normalize_statement_name(name):
    """Normalize statement name for comparison.

    Converts various representations to canonical form:
    - LINEINPUT -> LINE INPUT
    - line-input -> LINE INPUT
    - PRINTUSING -> PRINT USING
    - print-using -> PRINT USING
    - ONERROR -> ON ERROR
    """
    name = name.upper().replace('-', ' ').replace('_', ' ')

    # Special cases with known mappings
    mappings = {
        'LINE INPUT': 'LINEINPUT',
        'PRINT USING': 'PRINTUSING',
        'ON ERROR': 'ONERROR',
        'ON GOTO': 'ONGOTO',
        'ON GOSUB': 'ONGOSUB',
        'OPTION BASE': 'OPTIONBASE',
        'DEF FN': 'DEFFN',
        'FOR NEXT': 'FOR',  # for-next.md documents FOR statement
        'WHILE WEND': 'WHILE',  # while-wend.md documents WHILE
        'GOSUB RETURN': 'GOSUB',  # gosub-return.md documents GOSUB
        'IF THEN ELSE IF GOTO': 'IF',  # if-then-else-if-goto.md
    }

    # Check if normalized name matches any mapping
    if name in mappings:
        return mappings[name]

    # For compound docs, return the first statement
    # e.g., "FOR/NEXT" -> "FOR"
    if '/' in name:
        return name.split('/')[0]
    if ' ' in name:
        # Try to find a mapping, otherwise return first word
        for key, val in mappings.items():
            if key == name:
                return val
        return name.split()[0]

    return name


def get_documented_statements():
    """Get list of documented statements from help/common/language/statements/."""
    stmt_dir = Path('docs/help/common/language/statements')
    if not stmt_dir.exists():
        print(f"Error: {stmt_dir} not found")
        return []

    statements = []
    for md_file in stmt_dir.glob('*.md'):
        if md_file.name == 'index.md':
            continue
        stmt_name = md_file.stem
        # Normalize statement name
        normalized = normalize_statement_name(stmt_name)
        statements.append(normalized)

        # For compound docs, also add the other statements mentioned
        # e.g., "for-next.md" should also count as documenting NEXT
        if '-' in md_file.stem.lower():
            parts = md_file.stem.upper().replace('-', ' ').split()
            for part in parts:
                if part not in ['IF', 'THEN', 'ELSE', 'GOTO']:  # Skip keywords
                    statements.append(part)

    return sorted(set(statements))


def main():
    print("=" * 80)
    print("MBASIC Documentation Coverage Report")
    print("=" * 80)
    print()

    # Check functions
    print("📊 FUNCTIONS")
    print("-" * 80)
    impl_funcs = get_implemented_functions()
    doc_funcs = get_documented_functions()

    print(f"Implemented functions: {len(impl_funcs)}")
    print(f"Documented functions:  {len(doc_funcs)}")
    print()

    missing_docs = set(impl_funcs) - set(doc_funcs)
    extra_docs = set(doc_funcs) - set(impl_funcs)

    if missing_docs:
        print(f"❌ Missing documentation ({len(missing_docs)} functions):")
        for func in sorted(missing_docs):
            print(f"   - {func}")
        print()
    else:
        print("✅ All implemented functions are documented!")
        print()

    if extra_docs:
        print(f"⚠️  Documentation without implementation ({len(extra_docs)} functions):")
        for func in sorted(extra_docs):
            print(f"   - {func}")
        print()

    # Check statements
    print("📊 STATEMENTS")
    print("-" * 80)
    impl_stmts = get_implemented_statements()
    doc_stmts = get_documented_statements()

    print(f"Implemented statements: {len(impl_stmts)}")
    print(f"Documented statements:  {len(doc_stmts)}")
    print()

    # For statements, we need fuzzy matching because file names may not match exactly
    missing_stmt_docs = []
    for stmt in impl_stmts:
        # Check if any doc file matches this statement
        found = False
        for doc in doc_stmts:
            if stmt in doc or doc.replace('/', '_') == stmt:
                found = True
                break
        if not found:
            missing_stmt_docs.append(stmt)

    if missing_stmt_docs:
        print(f"❌ Missing documentation ({len(missing_stmt_docs)} statements):")
        for stmt in sorted(missing_stmt_docs):
            print(f"   - {stmt}")
        print()
    else:
        print("✅ All implemented statements are documented!")
        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_missing = len(missing_docs) + len(missing_stmt_docs)
    if total_missing == 0:
        print("✅ Documentation is complete!")
    else:
        print(f"❌ {total_missing} items need documentation")
        print(f"   - {len(missing_docs)} functions")
        print(f"   - {len(missing_stmt_docs)} statements")
    print()


if __name__ == '__main__':
    main()
