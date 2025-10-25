#!/usr/bin/env python3
"""
Extract BASIC statement documentation from basic_ref.pdf into individual markdown files.
"""

import re
from pathlib import Path

def extract_statements(input_file, output_dir):
    """Extract all statement documentation into individual markdown files."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r') as f:
        content = f.read()

    # Strategy: Find each statement by its "2.X STATEMENT" marker

    statement_pattern = r'^2\.(\d+[a-z]?)\s+(.+?)\s*$'
    statements = []

    lines = content.split('\n')
    in_chapter2 = False

    # Find all statement start positions
    statement_starts = []
    for i, line in enumerate(lines):
        # Check if we're in Chapter 2 (skip TOC at beginning)
        if re.search(r'CHAPTER 2\s*$', line) and i > 500:
            in_chapter2 = True
            continue

        # Check for Chapter 3 (end of Chapter 2)
        if in_chapter2 and re.search(r'CHAPTER 3\s*$', line):
            break

        if not in_chapter2:
            continue

        match = re.match(statement_pattern, line)
        if match:
            stmt_num = match.group(1)
            stmt_name = match.group(2).strip()
            statement_starts.append((i, stmt_num, stmt_name))

    # Extract content for each statement
    for idx, (line_num, stmt_num, stmt_name) in enumerate(statement_starts):
        # Determine end position (next statement or end of list)
        if idx + 1 < len(statement_starts):
            end_line = statement_starts[idx + 1][0]
        else:
            end_line = len(lines)

        # Extract content between this statement and the next
        content_lines = lines[line_num:end_line]
        statements.append((stmt_name, '\n'.join(content_lines)))

    print(f"Found {len(statements)} statements")

    # Create markdown files
    for stmt_name, stmt_content in statements:
        # Clean up statement name for filename
        # Handle multi-part names like "IF...THEN...ELSE" or "GOSUB...RETURN"
        filename = stmt_name.lower()

        # Replace common patterns
        filename = filename.replace('$', '_dollar')
        filename = filename.replace('#', '_hash')
        filename = filename.replace('...', '-')
        filename = filename.replace('••• ', '-')
        filename = filename.replace(' and ', '-')
        filename = filename.replace('[ ', '')
        filename = filename.replace(' ]', '')
        filename = filename.replace('[', '')
        filename = filename.replace(']', '')
        filename = filename.replace('/', '-')
        filename = filename.replace(',', '')
        filename = filename.replace(' ', '-')

        # Remove any remaining special characters
        filename = re.sub(r'[^a-z0-9_-]', '', filename)

        # Remove duplicate dashes
        filename = re.sub(r'-+', '-', filename)
        filename = filename.strip('-')

        # Parse content
        md_content = format_statement_markdown(stmt_name, stmt_content)

        # Write file
        output_file = output_dir / f"{filename}.md"
        with open(output_file, 'w') as f:
            f.write(md_content)

        print(f"Created: {output_file}")

def format_statement_markdown(name, content):
    """Convert statement text to markdown format.

    The PDF extraction with layout gives us:
    2.X STATEMENT

    Format:     <format>
    Versions:   <versions>
    Purpose:    <purpose>
    Remarks:    <remarks>
    Example:    <example>

    Where each section may span multiple lines.
    """

    lines = [line.rstrip() for line in content.split('\n')]

    # Remove the statement header line (2.X STATEMENT)
    if lines and re.match(r'^2\.\d+', lines[0]):
        lines = lines[1:]

    # Remove empty lines at start
    while lines and not lines[0].strip():
        lines = lines[1:]

    # Parse sections using "Label:" markers
    format_text = []
    versions_text = []
    purpose_text = []
    remarks_text = []
    example_text = []

    current_section = None

    for line in lines:
        # Check for section markers
        if line.startswith('Format:'):
            current_section = 'format'
            content_after = line[7:].strip()
            if content_after:
                format_text.append(content_after)
            continue
        elif line.startswith('Versions:') or line.startswith('Version:'):
            current_section = 'versions'
            content_after = line.split(':', 1)[1].strip()
            if content_after:
                versions_text.append(content_after)
            continue
        elif line.startswith('Purpose:'):
            current_section = 'purpose'
            content_after = line[8:].strip()
            if content_after:
                purpose_text.append(content_after)
            continue
        elif line.startswith('Remarks:'):
            current_section = 'remarks'
            content_after = line[8:].strip()
            if content_after:
                remarks_text.append(content_after)
            continue
        elif line.startswith('Example:') or line.startswith('Examples:'):
            current_section = 'example'
            content_after = line.split(':', 1)[1].strip() if ':' in line else ''
            if content_after:
                example_text.append(content_after)
            continue

        # Skip page markers and section headers
        if (line.startswith('Page 2-') or
            line.startswith('BASIC-80 COMMANDS') or
            line.startswith('BASIC-SO COMMANDS')):
            continue

        # Add line to current section (if not empty)
        if line.strip():
            if current_section == 'format':
                format_text.append(line.strip())
            elif current_section == 'versions':
                versions_text.append(line.strip())
            elif current_section == 'purpose':
                purpose_text.append(line.strip())
            elif current_section == 'remarks':
                remarks_text.append(line.strip())
            elif current_section == 'example':
                example_text.append(line)  # Keep indentation for examples

    # Build markdown
    md = f"# {name}\n\n"

    # Format/Syntax
    if format_text:
        format_str = '\n'.join(format_text).strip()
        if format_str:
            md += f"## Syntax\n\n```basic\n{format_str}\n```\n\n"

    # Versions
    if versions_text:
        version_str = ' '.join(versions_text).strip()
        if version_str and version_str not in ['8K, Extended, Disk', 'Extended, Disk']:
            md += f"**Versions:** {version_str}\n\n"

    # Purpose
    if purpose_text:
        purpose = ' '.join(purpose_text).strip()
        if purpose:
            md += f"## Purpose\n\n{purpose}\n\n"

    # Remarks/Description
    if remarks_text:
        remarks = ' '.join(remarks_text).strip()
        if remarks:
            md += f"## Remarks\n\n{remarks}\n\n"

    # Example
    if example_text:
        example = '\n'.join(example_text).strip()
        if example:
            md += f"## Example\n\n```basic\n{example}\n```\n\n"

    md += "## See Also\n\n*Related statements will be linked here*\n"

    return md

if __name__ == '__main__':
    import subprocess
    import os

    # First, extract text from PDF with layout preservation
    pdf_file = 'docs/external/basic_ref.pdf'
    txt_file = '/tmp/basic_ref_layout.txt'

    if not os.path.exists(txt_file) or os.path.getmtime(pdf_file) > os.path.getmtime(txt_file):
        print(f"Extracting text from {pdf_file}...")
        subprocess.run(['pdftotext', '-layout', pdf_file, txt_file], check=True)

    extract_statements(
        txt_file,
        'docs/help/common/language/statements'
    )
