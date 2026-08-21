#!/usr/bin/env python3
"""
Extract BASIC function documentation from the reference manual into markdown files.

The manual is not kept in this repository - see utils/basic_ref.py for where it
lives and how to get it.

This is a one-shot bootstrap tool, not a regenerator.  The pages under
docs/help/common/language/ were hand-corrected after it first ran: the manual's
text layer garbles some names (CDBL reads as COBL, CHR$ as CRR$, INPUT# as
INPUTI) and drops others entirely.  Re-running overwrites the corrected pages
with the raw extraction and adds the garbled names alongside them, so diff the
output before letting it near the help tree.
"""

import re
from pathlib import Path

def extract_functions(input_file, output_dir):
    """Extract all function documentation into individual markdown files."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_file, 'r') as f:
        content = f.read()

    # The text file has a weird structure - the labels (Format:, Versions:, etc.) appear first,
    # then the next function starts, then the actual content appears.
    # This suggests the original PDF had labels in left column, content in right column,
    # and text extraction read top-to-bottom in each column instead of left-to-right.

    # Strategy: Find each function by its "3.X FUNCNAME" marker, then look for the NEXT
    # function to know where content ends. The content between markers needs to be parsed carefully.

    function_pattern = r'^3\.(\d+)\s+(.+?)\s*$'
    functions = []

    lines = content.split('\n')
    in_chapter3 = False

    # Find all function start positions
    function_starts = []
    for i, line in enumerate(lines):
        # Check if we're in Chapter 3 (skip TOC at beginning)
        if re.search(r'CHAPTER 3\s*$', line) and i > 1000:
            in_chapter3 = True
            continue

        # Check for appendix (end of Chapter 3)
        if in_chapter3 and re.search(r'APPENDIX A\s*$', line):
            break

        if not in_chapter3:
            continue

        match = re.match(function_pattern, line)
        if match:
            func_num = match.group(1)
            func_name = match.group(2).strip()
            function_starts.append((i, func_num, func_name))

    # Extract content for each function
    for idx, (line_num, func_num, func_name) in enumerate(function_starts):
        # Determine end position (next function or end of list)
        if idx + 1 < len(function_starts):
            end_line = function_starts[idx + 1][0]
        else:
            end_line = len(lines)

        # Extract content between this function and the next
        content_lines = lines[line_num:end_line]
        functions.append((func_name, '\n'.join(content_lines)))

    print(f"Found {len(functions)} functions")

    # Create markdown files
    for func_name, func_content in functions:
        # Clean up function name for filename
        filename = func_name.lower().replace('$', '_dollar').replace('(', '').replace(')', '').replace(',', '').replace(' ', '-')
        filename = re.sub(r'[^a-z0-9_-]', '', filename)

        # Parse content
        md_content = format_function_markdown(func_name, func_content)

        # Write file
        output_file = output_dir / f"{filename}.md"
        with open(output_file, 'w') as f:
            f.write(md_content)

        print(f"Created: {output_file}")

def format_function_markdown(name, content):
    """Convert function text to markdown format.

    The PDF extraction with layout gives us:
    3.X FUNCNAME

    Format:     <format>
    Versions:   <versions>
    Action:     <action>
    Example:    <example>

    Where each section may span multiple lines.
    """

    lines = [line.rstrip() for line in content.split('\n')]

    # Remove the function header line (3.X FUNCNAME)
    if lines and re.match(r'^3\.\d+\s+', lines[0]):
        lines = lines[1:]

    # Remove empty lines at start
    while lines and not lines[0].strip():
        lines = lines[1:]

    # Parse sections using "Label:" markers
    format_text = []
    versions_text = []
    action_text = []
    example_text = []

    current_section = None

    for line in lines:
        # Check for section markers (Format:, Versions:, etc.)
        if line.startswith('Format:'):
            current_section = 'format'
            # Get content after "Format:" on same line
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
        elif line.startswith('Action:'):
            current_section = 'action'
            content_after = line[7:].strip()
            if content_after:
                action_text.append(content_after)
            continue
        elif line.startswith('Example:'):
            current_section = 'example'
            content_after = line[8:].strip()
            if content_after:
                example_text.append(content_after)
            continue

        # Skip page markers and section headers
        if (line.startswith('Page 3-') or line.startswith('Paae 3-') or
            line.startswith('BASIC-80 FUNCTIONS') or line.startswith('BASIC-SO FUNCTIONS')):
            continue

        # Add line to current section (if not empty)
        if line.strip():
            if current_section == 'format':
                format_text.append(line.strip())
            elif current_section == 'versions':
                versions_text.append(line.strip())
            elif current_section == 'action':
                action_text.append(line.strip())
            elif current_section == 'example':
                example_text.append(line)  # Keep indentation for examples

    # Build markdown
    md = f"# {name}\n\n"

    # Format/Syntax
    if format_text:
        format_str = ' '.join(format_text).strip()
        if format_str:
            md += f"## Syntax\n\n```basic\n{format_str}\n```\n\n"

    # Versions
    if versions_text:
        version_str = ' '.join(versions_text).strip()
        if version_str and version_str not in ['8K, Extended, Disk']:
            md += f"**Versions:** {version_str}\n\n"

    # Description (Action)
    if action_text:
        description = ' '.join(action_text).strip()
        if description:
            md += f"## Description\n\n{description}\n\n"

    # Example
    if example_text:
        example = '\n'.join(example_text).strip()
        if example:
            md += f"## Example\n\n```basic\n{example}\n```\n\n"

    md += "## See Also\n\n*Related functions will be linked here*\n"

    return md

if __name__ == '__main__':
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from basic_ref import basic_ref_layout_text

    # The manual lives in the retro_docs archive, not in this repository.
    txt_file = basic_ref_layout_text()

    extract_functions(
        txt_file,
        'docs/help/common/language/functions'
    )
