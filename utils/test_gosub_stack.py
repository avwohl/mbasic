#!/usr/bin/env python3
"""
Test GOSUB stack depth in MBASIC 5.21
Generates a BASIC program with nested GOSUBs to find the stack limit.
"""

def generate_gosub_test(max_depth=100):
    """Generate a BASIC program that tests GOSUB stack depth"""
    lines = []

    # Main program
    lines.append('10 DEPTH=0')
    lines.append('20 GOSUB 1000')
    lines.append('30 PRINT "Maximum depth reached:", DEPTH')
    lines.append('40 END')

    # Recursive GOSUB chain
    for i in range(max_depth):
        line_num = 1000 + i * 10
        lines.append(f'{line_num} DEPTH=DEPTH+1')
        lines.append(f'{line_num+1} PRINT "Depth:", DEPTH')
        if i < max_depth - 1:
            lines.append(f'{line_num+2} GOSUB {line_num+10}')
        lines.append(f'{line_num+3} RETURN')

    return '\n'.join(lines)

if __name__ == '__main__':
    # Generate test for various depths
    # Use short names for CP/M compatibility (8.3 format)
    tests = [
        (10, 'gosub10'),
        (20, 'gosub20'),
        (30, 'gosub30'),
        (40, 'gosub40'),
        (50, 'gosub50'),
        (60, 'gosub60'),
        (70, 'gosub70'),
    ]

    for depth, name in tests:
        filename = f'basic/bas_tests/{name}.bas'
        with open(filename, 'w') as f:
            f.write(generate_gosub_test(depth))
        print(f"Generated {filename} (depth {depth})")
