#!/usr/bin/env python3
"""Generate compact deep GOSUB stack test"""

def generate_test(depth, filename):
    lines = []
    lines.append(f'10 PRINT "{depth} level test"')
    lines.append('20 GOSUB 100')
    lines.append('30 PRINT "SUCCESS"')
    lines.append('40 END')

    for i in range(depth):
        base = 100 + i * 10
        next_base = base + 10
        level = i + 1

        lines.append(f'{base} PRINT "{level}"')
        if i < depth - 1:
            lines.append(f'{base+1} GOSUB {next_base}')
            lines.append(f'{base+2} PRINT "R{level}"')
        lines.append(f'{base+3} RETURN')

    program = '\n'.join(lines) + '\n'

    # Write with CRLF
    with open(filename, 'wb') as f:
        f.write(program.replace('\n', '\r\n').encode('ascii'))

if __name__ == '__main__':
    for depth in [15, 20, 25, 30, 35, 40]:
        filename = f'tests/s{depth}.bas'
        generate_test(depth, filename)
        print(f"Generated {filename}")
