# Linux Mint Developer Setup Guide

Complete setup guide for MBASIC development on Linux Mint (or Ubuntu/Debian-based systems). This covers all system-level packages and tools needed for full development including interpreter, compiler, testing, and documentation.

**Note for Users:** If you only want to RUN MBASIC programs (not develop/compile), see [docs/user/INSTALL.md](../user/INSTALL.md) for simpler user installation.

## Prerequisites

This guide assumes:
- Linux Mint (or Ubuntu/Debian-based distribution)
- Non-root user account with sudo privileges
- Internet connection for downloads

## System Packages (Requires sudo/root)

### Essential Python Development Tools

```bash
# Python virtual environment support (REQUIRED)
sudo apt install python3.12-venv

# Tkinter GUI support (OPTIONAL - for Tk UI backend)
sudo apt install python3-tk
```

### Git Version Control (for development)

```bash
# Install Git
sudo apt install git

# Configure Git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set up SSH keys for GitHub/GitLab (optional but recommended)
# If you already have keys, copy them to ~/.ssh/
# id_rsa (private key)
# id_rsa.pub (public key)
# chmod 600 ~/.ssh/id_rsa
# chmod 644 ~/.ssh/id_rsa.pub
```

### Optional: Text Editor

```bash
# Emacs with GTK support (or use your preferred editor)
sudo apt install emacs-gtk

# Alternatives: vim, nano, code (VS Code), etc.
```

## Compiler Tools (z88dk)

To compile BASIC programs to CP/M executables:

### Install z88dk via Snap

```bash
# Enable snap if disabled on Linux Mint
sudo rm /etc/apt/preferences.d/nosnap.pref

# Install snapd
sudo apt install snapd

# Install z88dk (Z80 C cross-compiler)
sudo snap install z88dk --beta
```

**Verify installation:**
```bash
z88dk-zcc --version
```

See [COMPILER_SETUP.md](COMPILER_SETUP.md) for detailed compiler documentation.

## CP/M Emulator (tnylpo)

For testing compiled programs and running real MBASIC.com:

### Install Dependencies

```bash
# NCurses libraries required by tnylpo
sudo apt install 'ncurses*' 'lib64ncurses*'
```

### Build and Install tnylpo

```bash
# Clone tnylpo repository
cd /tmp
git clone https://gitlab.com/gbrein/tnylpo.git
cd tnylpo

# Build
make

# Install to user bin (or system bin with sudo)
# Option 1: Install to ~/bin (user-local)
mkdir -p ~/bin
cp tnylpo ~/bin/
# Add ~/bin to PATH in ~/.bashrc if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Option 2: Install to /usr/local/bin (system-wide, requires sudo)
sudo cp tnylpo /usr/local/bin/

# Verify installation
tnylpo --version
```

See [TNYLPO_SETUP.md](TNYLPO_SETUP.md) for detailed usage instructions.

## Web UI Dependencies (Optional)

### Single-User Localhost (Basic)

For development and single-user testing:

```bash
# Activate virtual environment first
source venv/bin/activate

# Install web UI dependencies
pip install -r requirements-local.txt
```

### Multi-User Production Server (Advanced)

For production deployment with multiple concurrent users:

```bash
# Redis for session storage
sudo apt install redis

# Apache web server (for serving documentation)
sudo apt install apache2

# Install Python dependencies
source venv/bin/activate
pip install -r requirements-local.txt
```

**Configure web server permissions:**
```bash
# Allow Apache to read your project directory
# Replace $USER with your username
chmod o+x /home/$USER /home/$USER/cl
chmod -R o+rx /home/$USER/cl/mbasic
```

See [REDIS_SESSION_STORAGE_SETUP.md](REDIS_SESSION_STORAGE_SETUP.md) for Redis configuration.

## Claude AI Integration (Optional)

For AI-assisted development and documentation:

### Set Claude Credentials

```bash
# Add to ~/.bashrc
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Install Claude CLI

```bash
# Install Claude AI CLI tool
curl -fsSL https://claude.ai/install.sh | bash

# Verify installation
claude --version
```

### Install Anthropic Python SDK

```bash
source venv/bin/activate
pip install anthropic
```

**Note:** For consistency and bug fixes, always install `anthropic` via pip even if Claude CLI is installed.

## Python Development Environment

### Create Virtual Environment

```bash
# From project root
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt  # if exists
```

### Verify Installation

```bash
# Check available UI backends
python3 mbasic --list-backends

# Expected output should show:
# - cli (always available)
# - curses (if urwid installed)
# - tk (if python3-tk installed)
# - web (if web dependencies installed)
```

## Quick Test

Verify everything works:

```bash
# Test interpreter
python3 mbasic

# Test compiler (if z88dk installed)
cd test_compile
python3 test_compile.py test_varptr_simple.bas
# Should generate test_varptr_simple.com

# Test with tnylpo (if installed)
tnylpo test_varptr_simple.com
```

## Summary Checklist

### Minimal Development Setup
- [ ] `python3.12-venv` - Virtual environment support
- [ ] `git` - Version control
- [ ] Create venv and install Python dependencies
- [ ] Verify `python3 mbasic --list-backends`

### Full Interpreter Development
- [ ] All minimal setup items
- [ ] `python3-tk` - GUI support (optional)
- [ ] `emacs-gtk` or preferred editor
- [ ] Web dependencies via `requirements-local.txt`

### Compiler Development
- [ ] All minimal setup items
- [ ] `snapd` - Snap package manager
- [ ] `z88dk` - Z80 cross-compiler
- [ ] `ncurses*` and `lib64ncurses*` - NCurses libraries
- [ ] `tnylpo` - CP/M emulator (built from source)

### Documentation/Web Deployment
- [ ] `apache2` - Web server (optional)
- [ ] `redis` - Session storage (optional, for multi-user)
- [ ] Configure directory permissions

### AI-Assisted Development
- [ ] Claude CLI
- [ ] `anthropic` Python package
- [ ] API key in environment

## Troubleshooting

### "python3-venv not found"
```bash
# Try with version-specific package
sudo apt install python3-venv python3.12-venv
```

### "z88dk-zcc not found after snap install"
```bash
# Snap binaries might not be in PATH
# Log out and log back in, or:
export PATH="/snap/bin:$PATH"
echo 'export PATH="/snap/bin:$PATH"' >> ~/.bashrc
```

### "tnylpo: error while loading shared libraries"
```bash
# Install missing ncurses libraries
sudo apt install libncurses5 libncurses6 lib64ncurses6
```

### "Permission denied" when running web server
```bash
# Check directory permissions
ls -ld /home/$USER /home/$USER/cl /home/$USER/cl/mbasic

# Fix if needed
chmod o+x /home/$USER /home/$USER/cl
chmod -R o+rx /home/$USER/cl/mbasic
```

## See Also

- [User Installation Guide](../user/INSTALL.md) - Simpler setup for end users
- [Compiler Setup](COMPILER_SETUP.md) - Detailed z88dk configuration
- [tnylpo Setup](TNYLPO_SETUP.md) - CP/M emulator usage
- [Redis Setup](REDIS_SESSION_STORAGE_SETUP.md) - Multi-user web configuration
- [Testing Guide](../../tests/README.md) - Running tests

## Support

For issues specific to:
- **z88dk:** https://github.com/z88dk/z88dk/issues
- **tnylpo:** https://gitlab.com/gbrein/tnylpo/-/issues
- **MBASIC:** https://github.com/avwohl/mbasic/issues
