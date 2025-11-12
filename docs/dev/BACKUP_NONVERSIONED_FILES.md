# Files to Backup (Not in Git)

This document lists files and directories that should be backed up but are NOT committed to git because they contain secrets, local configurations, or instance-specific data.

## Deployment Configurations

### k8s/ - Kubernetes Filled-In Configs
**Location:** `/home/wohl/cl/mbasic/k8s/`
**Backup Priority:** HIGH
**Contains:** Filled-in Kubernetes configurations with real secrets

- `k8s/mbasic-secrets.yaml` - Database passwords, hCaptcha keys, CA certificates
- `k8s/*.yaml` - Any customized deployment configs

**Why not in git:** Contains production secrets and credentials
**Template location:** `deployment/k8s_templates/` (committed to git)
**Restore process:** Copy templates from `deployment/k8s_templates/` to `k8s/` and fill in secrets

### config/multiuser.json - Runtime Configuration
**Location:** `/home/wohl/cl/mbasic/config/multiuser.json`
**Backup Priority:** MEDIUM
**Contains:** Local runtime configuration for web UI

- Database connection details (MySQL socket path, credentials)
- Session storage settings
- Rate limiting configuration
- Feature flags

**Why not in git:** Contains local paths and potentially sensitive settings
**Template location:** `config/multiuser.json.example` (committed to git)
**Restore process:** Copy `config/multiuser.json.example` to `config/multiuser.json` and customize

## Database Files

### MySQL Error Logs Database
**Location:** Varies by installation (DigitalOcean managed DB or local MySQL)
**Backup Priority:** MEDIUM
**Contains:** Web UI error logs from production

- Database: `mbasic_logs`
- Table: `web_errors`

**Why not in git:** Runtime data, not configuration
**Schema location:** `config/setup_mysql_logging.sql` (committed to git)
**Restore process:** Run `config/setup_mysql_logging.sql` to recreate schema

### Redis Session Data
**Location:** Varies (DigitalOcean managed Redis or in-cluster)
**Backup Priority:** LOW
**Contains:** Active user sessions

**Why not in git:** Ephemeral runtime data, sessions can be recreated
**Restore process:** No restore needed, sessions will be recreated on access

## SSL/TLS Certificates

### Let's Encrypt Certificates
**Location:** Managed by cert-manager in Kubernetes
**Backup Priority:** LOW (auto-renewed)
**Contains:** SSL certificates for `mbasic.awohl.com`

**Why not in git:** Auto-generated and renewed by cert-manager
**Restore process:** cert-manager will automatically request new certificates

### DigitalOcean MySQL CA Certificate
**Location:** Downloaded from DigitalOcean dashboard
**Backup Priority:** MEDIUM
**Contains:** CA certificate for TLS connection to managed database

**Why not in git:** Provided by DigitalOcean, could be regenerated
**Stored in:** `k8s/mbasic-secrets.yaml` (see above)
**Restore process:** Download from DigitalOcean dashboard → Databases → Your Cluster → Connection Details

## Service Account Credentials

### hCaptcha API Keys
**Location:** `k8s/mbasic-secrets.yaml`
**Backup Priority:** HIGH
**Contains:** hCaptcha site key and secret key

**Why not in git:** API secrets
**Restore process:** Log in to https://www.hcaptcha.com/ and retrieve keys

### DigitalOcean Container Registry
**Location:** Local `~/.docker/config.json` (not in repo)
**Backup Priority:** LOW
**Contains:** Docker registry authentication token

**Why not in git:** Auto-generated token
**Restore process:** Run `doctl registry login`

## Backup Strategy

### Development Machine
**What to backup:**
- `config/multiuser.json` - Local configuration
- Database dumps: `mysqldump mbasic_logs > backup.sql`

**Backup frequency:** Weekly or before major changes

### Production Kubernetes Cluster
**What to backup:**
- `k8s/` directory with filled-in configs - CRITICAL!
- Database dumps from DigitalOcean managed MySQL
- Kubernetes secrets: `kubectl get secret mbasic-secrets -n mbasic -o yaml > backup-secrets.yaml`

**Backup frequency:**
- Secrets: After any change (store encrypted)
- Database: Daily automatic backups via DigitalOcean
- k8s configs: After any change (before running deployment)

### Recommended Backup Locations
1. **Encrypted USB drive** - For k8s/mbasic-secrets.yaml and credentials
2. **Private password manager** - For individual API keys and passwords
3. **Encrypted cloud storage** - For database dumps and config backups
4. **DO NOT use:**
   - Unencrypted cloud storage
   - Email
   - Shared drives
   - Anything that could leak secrets

## Recovery Process

### Disaster Recovery
If you lose the local repository and need to restore:

1. **Clone repository:**
   ```bash
   git clone https://github.com/avwohl/mbasic.git
   cd mbasic
   ```

2. **Restore k8s configs:**
   ```bash
   # Retrieve from encrypted backup
   cp ~/backup/k8s/ ./k8s/ -r
   ```

3. **Restore local config:**
   ```bash
   cp ~/backup/multiuser.json config/multiuser.json
   ```

4. **Verify secrets are correct:**
   ```bash
   grep -E "MYSQL_PASSWORD|HCAPTCHA" k8s/mbasic-secrets.yaml
   # Ensure no placeholder values remain
   ```

5. **Redeploy:**
   ```bash
   ./deployment/deploy.sh
   ```

### If Secrets Are Lost
If you lose the secrets backup:

1. **Regenerate hCaptcha keys:**
   - Log in to https://www.hcaptcha.com/
   - Create new site or retrieve existing keys

2. **Get database credentials:**
   - Log in to DigitalOcean
   - Navigate to Databases → Your Cluster
   - View connection details and CA certificate

3. **Update k8s/mbasic-secrets.yaml:**
   ```bash
   cp deployment/k8s_templates/mbasic-secrets.yaml.example k8s/mbasic-secrets.yaml
   # Edit with new values
   ```

## Security Notes

⚠️ **NEVER:**
- Commit `k8s/mbasic-secrets.yaml` to git
- Commit `config/multiuser.json` with real credentials
- Share secrets via unencrypted channels
- Store secrets in plain text on cloud storage
- Include secrets in screenshots or documentation

✅ **ALWAYS:**
- Encrypt backups of secret files
- Use different passwords for each service
- Rotate secrets quarterly
- Audit git commits before pushing (check for accidentally committed secrets)
- Use .gitignore to prevent accidental commits

## Quick Reference

| File/Directory | In Git? | Backup? | Priority | Contains |
|----------------|---------|---------|----------|----------|
| `k8s/mbasic-secrets.yaml` | ❌ | ✅ | HIGH | Secrets |
| `k8s/*.yaml` | ❌ | ✅ | MEDIUM | Custom configs |
| `config/multiuser.json` | ❌ | ✅ | MEDIUM | Local config |
| `deployment/k8s_templates/` | ✅ | ❌ | N/A | Templates |
| `config/*.example` | ✅ | ❌ | N/A | Templates |
| MySQL `mbasic_logs` | ❌ | ✅ | MEDIUM | Error logs |
| Redis sessions | ❌ | ❌ | LOW | Ephemeral |

## See Also

- `deployment/README.md` - Deployment instructions
- `config/README.md` - Configuration documentation
- `deployment/k8s_templates/mbasic-secrets.yaml.example` - Secrets template
- `.gitignore` - Files excluded from git
