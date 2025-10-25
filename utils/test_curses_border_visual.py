#!/usr/bin/env python3
"""
Visual test of curses UI borders.

Shows how the borders render with the custom border style.
"""

import sys
sys.path.insert(0, 'src')

import urwid

def test_border_rendering():
    """Test and display border rendering."""

    # Create test widgets with custom borders (no bottom/right)
    text1 = urwid.Text("This is the editor area")
    box1 = urwid.LineBox(
        urwid.Filler(text1, valign='top'),
        title="Editor",
        tlcorner='┌', tline='─', lline='│', trcorner='─',
        blcorner='└', rline=' ', bline=' ', brcorner=' '
    )

    text2 = urwid.Text("This is the output area")
    box2 = urwid.LineBox(
        urwid.Filler(text2, valign='top'),
        title="Output",
        tlcorner='┌', tline='─', lline='│', trcorner='─',
        blcorner='└', rline=' ', bline=' ', brcorner=' '
    )

    status = urwid.Text("Status bar - Press Q to quit")

    # Layout
    pile = urwid.Pile([
        ('weight', 7, box1),
        ('weight', 3, box2),
        ('pack', status)
    ])

    # Render to see how it looks
    canvas = pile.render((80, 24), focus=True)

    print("Border Test - Custom Style (no bottom/right borders)")
    print("="*80)

    # Convert canvas to text
    content = list(canvas.content())
    for i in range(min(24, len(content))):
        row_content = content[i]
        line = ''
        for segment in row_content:
            if len(segment) >= 3:
                text = segment[2]
                if isinstance(text, bytes):
                    text = text.decode('utf-8', errors='replace')
                line += str(text)
        print(line)

    print("="*80)
    print("\nBorder characters used:")
    print("  Top-left:     '┌'")
    print("  Top line:     '─'")
    print("  Top-right:    '─' (no corner)")
    print("  Left line:    '│'")
    print("  Right line:   ' ' (suppressed)")
    print("  Bottom line:  ' ' (suppressed)")
    print("  Bottom-left:  '└'")
    print("  Bottom-right: ' ' (suppressed)")

    print("\nResult: Bottom and right borders should not be visible")

if __name__ == '__main__':
    test_border_rendering()
