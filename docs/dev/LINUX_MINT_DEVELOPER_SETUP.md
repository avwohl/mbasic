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

#### Install Redis (Session Storage)

```bash
# Redis for session storage (load-balanced deployments)
sudo apt-get install redis-server

# Start and enable Redis
sudo systemctl start redis
sudo systemctl enable redis

# Test connection
redis-cli ping  # Should return: PONG
```

See [REDIS_SESSION_STORAGE_SETUP.md](REDIS_SESSION_STORAGE_SETUP.md) for Redis configuration.

#### Install MariaDB (Error Logging)

```bash
# MariaDB for error logging
sudo apt-get install mariadb-server mariadb-client

# Start and enable MariaDB
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

**Setup database and user:**

```bash
# Connect to MariaDB as root
sudo mysql

# In MySQL prompt, run these commands:
# Replace 'wohl' with the user that will run the web UI
# Replace '[fill in password]' with a secure password (or leave empty for Unix socket only)
```

```sql
-- Create user with password authentication (for remote connections)
CREATE USER 'wohl'@'%' IDENTIFIED BY '[fill in password]';

-- Create databases
CREATE DATABASE wohl;
CREATE DATABASE mbasic_logs;

-- Grant privileges for Unix socket authentication (local, no password needed)
GRANT ALL PRIVILEGES ON mbasic_logs.* TO 'wohl'@'localhost' IDENTIFIED VIA unix_socket;

-- Grant privileges for password authentication (remote or local with password)
GRANT ALL PRIVILEGES ON mbasic_logs.* TO 'wohl'@'%';

-- Apply changes
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

**Create error logging tables:**

```bash
# From MBASIC project directory
mysql < config/setup_mysql_logging.sql
```

**Verify setup:**

```bash
# Test Unix socket connection (no password)
mysql mbasic_logs -e "SHOW TABLES;"

# Should show: web_errors, error_summary, recent_errors
```

See [WEB_ERROR_LOGGING.md](WEB_ERROR_LOGGING.md) for error logging configuration.

#### Install Apache (Documentation Server - Optional)

```bash
# Apache web server (for serving documentation)
sudo apt-get install apache2

# Start and enable Apache
sudo systemctl start apache2
sudo systemctl enable apache2
```

**Configure web server permissions:**
```bash
# Allow Apache to read your project directory
# Replace $USER with your username
chmod o+x /home/$USER /home/$USER/cl
chmod -R o+rx /home/$USER/cl/mbasic
```

#### Install Python Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install web UI and multi-user dependencies
pip install nicegui>=3.2.0
pip install redis>=5.0.0
pip install mysql-connector-python>=8.0

# Or install all at once
pip install -r requirements.txt
```

## Kubernetes & Cloud Deployment (Optional)

For deploying MBASIC web UI to Kubernetes clusters (e.g., DigitalOcean):

### Install Docker

```bash
# Install Docker
sudo apt-get install -y docker.io

# Add user to docker group (replace 'wohl' with your username)
sudo usermod -aG docker wohl

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Note: Existing logins need to relog to gain the docker group
# Or use newgrp to activate group in current shell:
newgrp docker
```

**Verify Docker installation:**
```bash
docker --version
docker ps  # Should work without sudo
```

### Install DigitalOcean CLI (doctl)

```bash
# Install doctl via snap
sudo snap install doctl

# Connect snap permissions
sudo snap connect doctl:kube-config
sudo snap connect doctl:dot-docker

# Initialize doctl with your DigitalOcean API token
# (Create token at: https://cloud.digitalocean.com/account/api/tokens)
doctl auth init
# Follow prompts to enter your API token
```

**Verify doctl installation:**
```bash
doctl account get  # Should show your DigitalOcean account info
```

### Install kubectl (Kubernetes CLI)

```bash
# Install kubectl via snap
sudo snap install kubectl --classic

# Verify installation
kubectl version --client
```

### Configure Kubernetes Cluster Access

```bash
# Download your cluster's kubeconfig (replace CLUSTER_ID with your cluster ID)
doctl kubernetes cluster kubeconfig save CLUSTER_ID

# Verify cluster access
kubectl get nodes
kubectl get namespaces
```

### Setup hCaptcha (Bot Protection)

For web deployments with bot protection:

1. Sign up at https://www.hcaptcha.com
2. Create a new site and obtain:
   - Site Key (public)
   - Secret Key (private)
3. Store keys as Kubernetes secrets or environment variables

### Additional Resources

- **Deploy to DigitalOcean Kubernetes:** https://docs.digitalocean.com/products/kubernetes/getting-started/deploy-image-to-cluster/
- **Kubernetes Deployment Guide:** [KUBERNETES_DEPLOYMENT_SETUP.md](KUBERNETES_DEPLOYMENT_SETUP.md)
- **Docker Registry Setup:** Configure DigitalOcean Container Registry for storing Docker images

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

## Documentation Development

### Local Documentation Server

For developing/testing documentation changes before publishing to GitHub Pages:

```bash
# Install MkDocs (if not already in venv)
source venv/bin/activate
pip install mkdocs mkdocs-material mkdocs-awesome-pages-plugin

# Start local documentation server
mkdocs serve
# Opens at: http://localhost:8000/
```

### Environment Variable for Local Docs

By default, MBASIC UIs link to GitHub Pages documentation (`https://avwohl.github.io/mbasic/help/`).

To test documentation changes locally before publishing:

```bash
# Set environment variable to use local docs
export MBASIC_DOCS_URL="http://localhost:8000/help/"

# Run MBASIC with local docs
python3 mbasic --ui tk
# Help > Help Topics now opens localhost instead of GitHub Pages
```

**Documentation URLs:**
- **Production (default)**: `https://avwohl.github.io/mbasic/help/`
- **Local development**: `http://localhost:8000/help/` (with `MBASIC_DOCS_URL` set)

See [DOCS_URL_CONFIGURATION.md](DOCS_URL_CONFIGURATION.md) for complete documentation URL configuration details.

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
- [ ] `redis-server` - Session storage (optional, for multi-user)
- [ ] `mariadb-server` and `mariadb-client` - Error logging database (optional)
- [ ] Setup MariaDB user and databases
- [ ] Run `config/setup_mysql_logging.sql`
- [ ] `apache2` - Web server (optional)
- [ ] Configure directory permissions
- [ ] Install Python packages: `nicegui`, `redis`, `mysql-connector-python`

### Kubernetes/Cloud Deployment
- [ ] `docker.io` - Container runtime
- [ ] Add user to docker group (`usermod -aG docker username`)
- [ ] `doctl` - DigitalOcean CLI (via snap)
- [ ] Connect doctl snap permissions
- [ ] Configure doctl authentication (API token)
- [ ] `kubectl` - Kubernetes CLI (via snap)
- [ ] Configure cluster kubeconfig
- [ ] Setup hCaptcha account (optional, for bot protection)

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

### MariaDB connection issues

**"Access denied" with Unix socket:**
```bash
# Check if user has Unix socket authentication
sudo mysql -e "SELECT user, host, plugin FROM mysql.user WHERE user='wohl';"

# Should show: unix_socket for localhost
# If not, run the GRANT command again:
sudo mysql -e "GRANT ALL PRIVILEGES ON mbasic_logs.* TO 'wohl'@'localhost' IDENTIFIED VIA unix_socket; FLUSH PRIVILEGES;"
```

**"Can't connect to MySQL server":**
```bash
# Check if MariaDB is running
sudo systemctl status mariadb

# Start if needed
sudo systemctl start mariadb
```

**Test connection:**
```bash
# Unix socket (no password)
mysql mbasic_logs -e "SELECT COUNT(*) FROM web_errors;"

# Password authentication
mysql -u wohl -p mbasic_logs -e "SELECT COUNT(*) FROM web_errors;"
```

## See Also

- [User Installation Guide](../user/INSTALL.md) - Simpler setup for end users
- [Web Multi-User Deployment](WEB_MULTIUSER_DEPLOYMENT.md) - Complete web deployment guide
- [Web Error Logging](WEB_ERROR_LOGGING.md) - Error logging system setup
- [Redis Setup](REDIS_SESSION_STORAGE_SETUP.md) - Redis session storage configuration
- [Compiler Setup](COMPILER_SETUP.md) - Detailed z88dk configuration
- [tnylpo Setup](TNYLPO_SETUP.md) - CP/M emulator usage
- [Testing Guide](https://github.com/avwohl/mbasic/blob/main/tests/README.md) - Running tests

## Support

For issues specific to:
- **z88dk:** https://github.com/z88dk/z88dk/issues
- **tnylpo:** https://gitlab.com/gbrein/tnylpo/-/issues
- **MBASIC:** https://github.com/avwohl/mbasic/issues
