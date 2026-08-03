# PATH-Based Tool Requirements

## Overview

The MBASIC compiler toolchain finds its tools in PATH rather than at hardcoded
locations — in Python via `/usr/bin/env`, and in the documented build pipelines by
plain command name. This approach ensures portability across different installation
methods and operating systems.

There are two supported toolchains. The preferred one is uc80 (with the um80 assembler
and ul80 linker) plus the cpmemu emulator; z88dk and tnylpo are the supported
alternates, still used for MBF floats, 8080 output, and port I/O. See
[TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md).

	Role	Preferred	Supported alternate
	C compiler	uc80 (+ um80, ul80)	z88dk (zcc)
	CP/M emulator	cpmemu	tnylpo

## Tools

### uc80, um80, ul80 (preferred compiler)
- **Purpose**: Compile generated C to a CP/M executable — `uc80` translates C to
  `.mac`, `um80` assembles to `.rel`, `ul80` links the `.COM`
- **Binaries**: `uc80`, `um80`, `ul80`
- **Install**: `pip install uc80 um80` (`ul80` ships in the `um80` package)
- **Used by**: the build pipeline in
  [COMPILER_SETUP.md](COMPILER_SETUP.md), run by hand today
- **Check**: `which uc80 um80 ul80`

The uc80 *library* directory is the one thing not found through PATH: `libc.lib` and
`runtime.lib` live inside the installed package and there is no flag or environment
variable for them, so the pipeline derives the path from the module location:

```bash
UCLIB=$(python3 -c "import uc80,os;print(os.path.join(os.path.dirname(uc80.__file__),'lib'))")
```

### cpmemu (preferred emulator)
- **Purpose**: CP/M 2.2 emulator for running compiled programs; maps host files
  directly, so no disk image is needed
- **Binary**: `cpmemu`
- **Install**: `.deb`/`.rpm` from https://github.com/avwohl/cpmemu, or build from source
- **Used by**: manual test runs — `cpmemu program.com`
- **Check**: `which cpmemu`

### z88dk (alternate compiler)
- **Purpose**: Compiles generated C code to CP/M executables; the route for MBF
  floats, `--cpu 8080`, and `INP`/`OUT`/`WAIT`
- **Binary**: `z88dk.zcc`
- **Used by**: Compiler backend (`src/codegen_backend.py`)
- **Invocation**: `/usr/bin/env z88dk.zcc`
- **Check**: `python3 utils/check_z88dk.py`

### tnylpo (alternate emulator)
- **Purpose**: CP/M emulator for testing compiled programs
- **Binary**: `tnylpo`
- **Used by**: Test scripts (`test_compile/test_compile.py`), and `mbasic --run`
- **Invocation**: `/usr/bin/env tnylpo`
- **Check**: `python3 utils/check_tnylpo.py`

## Quick Setup Check

```bash
# Covers both toolchains, preferred pair first
python3 utils/check_compiler_tools.py

# Or check by hand
which uc80 um80 ul80 cpmemu
```

`check_compiler_tools.py` reports the preferred tools (uc80, um80, ul80, cpmemu)
first and the alternates (z88dk, tnylpo) after, and tells you which combinations you
can actually build with. It also locates uc80's `libc.lib`/`runtime.lib`, which is the
one path that PATH cannot answer — see below.

## Why PATH-Based?

### Portability
- Works with any installation location
- No hardcoded paths to maintain
- Users choose their preferred installation method

### Installation Flexibility
Supports all these installation methods:
- pip (`~/.local/bin`, or a virtualenv's `bin`)
- System package managers and distro packages (`.deb`, `.rpm`)
- Snap packages (add `/snap/bin` to PATH)
- Building from source
- Docker containers with wrapper scripts
- Custom installations in `~/bin` or elsewhere

### Standard Practice
- `/usr/bin/env` is the standard Unix/Linux way to find executables
- Used by shebangs in scripts worldwide
- Respects user's PATH preferences

## PATH Configuration

### Check Your PATH
```bash
echo $PATH
```

### Add Directory to PATH

#### Temporary (current session only)
```bash
export PATH="$PATH:/new/directory"
```

#### Permanent (add to ~/.bashrc or ~/.profile)
```bash
echo 'export PATH="$PATH:/new/directory"' >> ~/.bashrc
source ~/.bashrc
```

### Common Directories to Add

- **pip --user binaries**: `$HOME/.local/bin` — where `uc80`, `um80`, and `ul80` land,
  and not on the default PATH on every distribution
- **User binaries**: `$HOME/bin` or `~/bin`
- **Local binaries**: `/usr/local/bin`
- **Snap binaries**: `/snap/bin`
- **Custom tools**: Any directory with your tools

## Implementation Details

### Code Changes

#### z88dk Compiler Path
```python
# Before (hardcoded):
return ['/snap/bin/z88dk.zcc', '+cpm', ...]

# After (PATH-based):
return ['/usr/bin/env', 'z88dk.zcc', '+cpm', ...]
```

#### tnylpo Emulator Path
```python
# Before (direct call):
subprocess.run(['tnylpo', com_file])

# After (PATH-based):
subprocess.run(['/usr/bin/env', 'tnylpo', com_file])
```

The uc80 and cpmemu equivalents follow the same convention once the backend can drive
them; today those commands appear only in the documented shell pipeline, where a bare
command name already resolves through PATH.

### Files Modified
- `src/codegen_backend.py` - z88dk compiler invocation
- `test_compile/test_compile.py` - tnylpo emulator invocation

### Documentation Created
- `docs/dev/TOOLCHAIN_POLICY.md` - which toolchain is preferred, and why
- `docs/dev/COMPILER_SETUP.md` - uc80/cpmemu and z88dk installation guide
- `docs/dev/TNYLPO_SETUP.md` - tnylpo installation guide
- `docs/dev/COMPILER_Z88DK_PATH_CHANGE.md` - z88dk path change details
- `docs/dev/PATH_BASED_TOOLS.md` - This document

### Utilities Created
- `utils/check_z88dk.py` - Verify z88dk installation
- `utils/check_tnylpo.py` - Verify tnylpo installation
- `utils/check_compiler_tools.py` - Check the alternate toolchain
- `utils/check_toolchain_policy.py` - Enforce the toolchain preference in docs

## Troubleshooting

### Tool Not Found
If a tool cannot be found:

1. **Check if installed**: `which toolname`
2. **Check PATH**: `echo $PATH`
3. **Find the tool**: `find / -name toolname 2>/dev/null`
4. **Add to PATH**: See "PATH Configuration" above

For `uc80`/`um80`/`ul80` specifically, confirm the package is installed at all with
`python3 -m pip show uc80`, then add `$HOME/.local/bin` to PATH — a successful
`pip install --user` still leaves the commands unreachable on distributions that do
not include that directory by default.

### Permission Denied
If tool exists but won't run:

1. **Check permissions**: `ls -l /path/to/tool`
2. **Make executable**: `chmod +x /path/to/tool`

### Wrong Version Found
If wrong version is in PATH:

1. **Check which is found**: `which -a toolname`
2. **Check PATH order**: Earlier directories take precedence
3. **Adjust PATH order or use full path temporarily

## Benefits Summary

1. **No configuration needed** - Works out of the box if tools are in PATH
2. **Cross-platform** - Same code works on Linux, macOS, WSL, etc.
3. **User choice** - Install tools however you prefer
4. **Future-proof** - New installation methods automatically supported
5. **Standard practice** - Follows Unix/Linux conventions

## See Also

- [TOOLCHAIN_POLICY.md](TOOLCHAIN_POLICY.md) - Preferred vs alternate toolchain
- [COMPILER_SETUP.md](COMPILER_SETUP.md) - Complete compiler setup guide
- [TNYLPO_SETUP.md](TNYLPO_SETUP.md) - tnylpo installation guide
- [UTILITY_SCRIPTS_INDEX.md](https://github.com/avwohl/mbasic/blob/main/utils/UTILITY_SCRIPTS_INDEX.md) - Check utilities
