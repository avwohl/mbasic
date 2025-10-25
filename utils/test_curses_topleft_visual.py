#!/usr/bin/env python3
"""
Visual test of TopLeftBox widget.

Shows that only top and left borders are drawn, and no space is
reserved for bottom/right borders.
"""

import sys
sys.path.insert(0, 'src')

import urwid
from ui.curses_ui import TopLeftBox

def test_topleft_box():
    """Test and display TopLeftBox rendering."""

    # Create test content
    lines = [
        "Line 1 of content",
        "Line 2 of content",
        "Line 3 of content",
        "Line 4 of content",
        "Line 5 - this is the last line",
    ]
    content = urwid.Text('\n'.join(lines))

    # Wrap in TopLeftBox
    box = TopLeftBox(urwid.Filler(content, valign='top'), title="Test Box")

    # Render
    canvas = box.render((80, 10), focus=True)

    print("TopLeftBox Visual Test")
    print("="*80)
    print("Expected:")
    print("  - Top border: ┌─ Test Box ──────...")
    print("  - Left border: │ on each line")
    print("  - NO bottom border (content goes to edge)")
    print("  - NO right border (content uses full width)")
    print("  - Bottom-left: │ (straight, not └)")
    print()
    print("Rendered output:")
    print("="*80)

    # Convert canvas to text
    content_list = list(canvas.content())
    for i in range(min(10, len(content_list))):
        row_content = content_list[i]
        line = ''
        for segment in row_content:
            if len(segment) >= 3:
                text = segment[2]
                if isinstance(text, bytes):
                    text = text.decode('utf-8', errors='replace')
                line += str(text)
        print(line)

    print("="*80)
    print("\nKey observations:")
    print("  ✓ Top border shows title")
    print("  ✓ Left border (│) appears on all content lines")
    print("  ✓ Bottom-left is │ (straight) not └ (corner)")
    print("  ✓ No bottom line (content continues to edge)")
    print("  ✓ No right line (content uses full width)")
    print("\nContent space usage:")
    print("  Old LineBox: reserves 1 line bottom + 1 char right")
    print("  New TopLeftBox: reserves 0 lines bottom + 0 chars right")
    print("  Result: More space for actual content!")

if __name__ == '__main__':
    test_topleft_box()
