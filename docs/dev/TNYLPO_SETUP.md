# tnylpo Setup Guide

## Overview

tnylpo is a CP/M 2.2 emulator for Unix/Linux that runs CP/M .COM executables. It's required for testing MBASIC programs compiled to CP/M format.

**Important**: `tnylpo` must be in your PATH for test scripts to work.

## Installation

tnylpo must be built from source - there are no package manager installations available.

### Prerequisites

Install ncurses development libraries:

#### Ubuntu/Debian
```bash
sudo apt-get install libncurses5-dev
```

#### Fedora/RHEL/CentOS
```bash
sudo dnf install ncurses-devel
# or
sudo yum install ncurses-devel
```

#### macOS
Should be included with Xcode Command Line Tools:
```bash
xcode-select --install
```

#### Arch Linux
```bash
sudo pacman -S ncurses
```

### Building tnylpo

1. **Clone the repository**
```bash
git clone https://gitlab.com/gbrein/tnylpo.git
cd tnylpo
```

2. **Build tnylpo**
```bash
make
```

3. **Install Option A: System-wide (requires sudo)**
```bash
sudo make install
# Installs to /usr/local/bin
```

4. **Install Option B: User directory (no sudo needed)**
```bash
mkdir -p ~/bin
cp tnylpo ~/bin/
```

5. **Add to PATH (if using Option B)**
```bash
# Add to current session
export PATH="$PATH:$HOME/bin"

# Make permanent - add to ~/.bashrc or ~/.profile
echo 'export PATH="$PATH:$HOME/bin"' >> ~/.bashrc

# Reload bashrc
source ~/.bashrc
```

## Verification

### Check Installation
```bash
# Verify tnylpo is in PATH
which tnylpo

# Check with our utility
python3 utils/check_tnylpo.py
```

### Test with a CP/M Program
```bash
# Compile a BASIC program
python3 test_compile.py test_loop.bas

# Run with tnylpo
tnylpo test.com
```

## Usage

### Basic Usage
```bash
tnylpo program.com
```

### With CP/M Command Line Arguments
```bash
tnylpo program.com arg1 arg2
```

### Configuration

tnylpo can be configured via `~/.tnylpo/tnylpo.conf`. Common settings:

```conf
# Terminal settings
set terminal_lines 24
set terminal_columns 80

# Disk configuration
mount a: /path/to/cpm/disk/a
mount b: /path/to/cpm/disk/b

# Printer output
printer /tmp/tnylpo-printer.txt
```

## Features

- Full CP/M 2.2 BDOS/BIOS emulation
- Console I/O with ncurses
- File system access through Unix directories
- Printer support (output to file)
- Accurate Z80 CPU emulation
- Supports most CP/M programs

## Troubleshooting

### "tnylpo: command not found"
- tnylpo is not installed or not in PATH
- Run `echo $PATH` to check your PATH
- Run `find / -name tnylpo 2>/dev/null` to locate the binary

### Build Errors

#### "curses.h: No such file or directory"
Install ncurses development package (see Prerequisites)

#### "make: command not found"
Install build tools:
- Ubuntu/Debian: `sudo apt-get install build-essential`
- Fedora/RHEL: `sudo dnf group install "Development Tools"`
- macOS: Install Xcode Command Line Tools

### Runtime Issues

#### Screen corruption
- Try different terminal emulator (xterm, gnome-terminal, etc.)
- Check TERM environment variable: `echo $TERM`
- Try: `export TERM=xterm-256color`

#### Program hangs
- Press Ctrl+C to interrupt
- Press Ctrl+Z to suspend, then `kill %1` to terminate

## Integration with MBASIC Compiler

The MBASIC compiler test scripts use `/usr/bin/env tnylpo` to find tnylpo in PATH. This approach is portable across different installation locations.

### Complete Workflow Example

```bash
# 1. Write BASIC program
cat > hello.bas << 'EOF'
10 PRINT "Hello from CP/M!"
20 END
EOF

# 2. Compile to C
python3 test_compile.py hello.bas

# 3. Review generated C code
cat hello.c

# 4. Compile C to CP/M .COM file (done by test_compile.py)
# Uses: /usr/bin/env z88dk.zcc +cpm hello.c -create-app -o hello

# 5. Run on CP/M emulator
tnylpo hello.com
```

## Alternative CP/M Emulators

If tnylpo doesn't work for your system, alternatives include:

- **RunCPM**: https://github.com/MockbaTheBorg/RunCPM
- **z80pack**: https://github.com/udo-munk/z80pack
- **YAZE-AG**: http://www.mathematik.uni-ulm.de/users/ag/yaze-ag/

However, test scripts are configured for tnylpo specifically.

## References

- tnylpo on GitLab: https://gitlab.com/gbrein/tnylpo
- CP/M 2.2 Manual: http://www.cpm.z80.de/manuals/cpm22-m.pdf
- Z80 Instruction Set: http://www.z80.info/z80ins.txt

## Implementation Note

Test scripts use `/usr/bin/env tnylpo` to locate tnylpo in PATH. See:
- `test_compile/test_compile.py` - Test compilation and execution script
- `utils/check_tnylpo.py` - Installation verification utility