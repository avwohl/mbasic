# MBASIC Kubernetes Deployment

This directory contains everything needed to deploy MBASIC web UI to DigitalOcean Kubernetes.

## Quick Start

```bash
# 1. Configure your registry (edit deployment/deploy.sh line 16)
export REGISTRY="registry.digitalocean.com/YOUR_REGISTRY"

# 2. Set up secrets
cp deployment/k8s_templates/mbasic-secrets.yaml.example k8s/mbasic-secrets.yaml
# Edit k8s/mbasic-secrets.yaml with real credentials

# 3. Deploy
./deployment/deploy.sh v1.0
```

## Prerequisites

**Local Tools:**
- `kubectl` - Kubernetes CLI
- `docker` - Container runtime
- `doctl` - DigitalOcean CLI

**DigitalOcean Resources:**
- Kubernetes cluster (3+ nodes recommended)
- Container registry
- Managed MySQL database (optional but recommended)

**External Services:**
- hCaptcha account (free tier: https://www.hcaptcha.com/)
- Domain name pointing to cluster (`mbasic.awohl.com`)

## Full Guide

The [Kubernetes Deployment Guide](../docs/dev/KUBERNETES_DEPLOYMENT_GUIDE.md) has the
12 setup steps, monitoring, scaling, updates, troubleshooting, cost management,
security, and backup.

## URLs

- **Landing Page:** https://mbasic.awohl.com/
- **Web IDE:** https://mbasic.awohl.com/ide/
- **Documentation:** https://avwohl.github.io/mbasic/

## Support

- **Issues:** https://github.com/avwohl/mbasic/issues
- **DigitalOcean Docs:** https://docs.digitalocean.com/products/kubernetes/
- **Kubernetes Docs:** https://kubernetes.io/docs/

## Files

```
deployment/
├── deploy.sh                         # Main deployment script
├── k8s_templates/                    # Kubernetes YAML templates
│   ├── namespace.yaml                # Namespace definition
│   ├── redis-deployment.yaml         # Redis (sessions)
│   ├── landing-page-deployment.yaml  # Static landing page
│   ├── mbasic-deployment.yaml        # MBASIC web pods
│   ├── mbasic-configmap.yaml         # Configuration
│   ├── mbasic-secrets.yaml.example   # Secrets template
│   └── ingress.yaml                  # Ingress + SSL
├── landing-page/
│   └── index.html                    # Landing page HTML
└── README.md                         # This file

config/
├── multiuser.json.example            # Multi-user config template
├── setup_mysql_logging.sql           # MySQL schema
└── README.md                         # Config documentation

k8s/                                  # Working directory (not in git)
└── mbasic-secrets.yaml               # Your filled-in secrets

Dockerfile                            # Container definition
.dockerignore                         # Docker build exclusions
