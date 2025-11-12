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

## Setup Steps

### 1. Create Kubernetes Cluster

```bash
# Via DigitalOcean dashboard or CLI
doctl kubernetes cluster create mbasic-cluster \
    --region nyc1 \
    --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=3"

# Get kubeconfig
doctl kubernetes cluster kubeconfig save mbasic-cluster
```

### 2. Install cert-manager (SSL Certificates)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
```

### 3. Install nginx-ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml

# Wait for load balancer to be created
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s
```

### 4. Create Container Registry

```bash
# Via DigitalOcean dashboard or:
doctl registry create YOUR_REGISTRY_NAME

# Login
doctl registry login
```

### 5. Set Up MySQL Database

**Option A: DigitalOcean Managed Database (Recommended)**

1. Create MySQL cluster via DigitalOcean dashboard
2. Create database: `mbasic_logs`
3. Download CA certificate
4. Run schema:
   ```bash
   mysql -h your-db-host -u doadmin -p --ssl-ca=ca-certificate.crt < config/setup_mysql_logging.sql
   ```

**Option B: In-cluster MySQL**

Deploy StatefulSet (see `k8s/mysql-statefulset.yaml.example`)

### 6. Get hCaptcha Keys

1. Sign up at https://www.hcaptcha.com/
2. Create a new site
3. Get site key and secret key
4. Add to `k8s/mbasic-secrets.yaml`

### 7. Configure Secrets

```bash
# Copy template to working directory
cp deployment/k8s_templates/mbasic-secrets.yaml.example k8s/mbasic-secrets.yaml
```

Edit `k8s/mbasic-secrets.yaml`:
- MySQL host, user, password
- hCaptcha site and secret keys
- MySQL CA certificate (from DigitalOcean)

**Important:** Never commit `mbasic-secrets.yaml` to Git!

### 8. Update Configuration

Edit `deployment/k8s_templates/ingress.yaml`:
- Change email address for Let's Encrypt

Edit `deployment/deploy.sh`:
- Set your container registry URL (line 16)

### 9. Deploy

```bash
./deployment/deploy.sh v1.0
```

### 10. Configure DNS

Get load balancer IP:
```bash
kubectl get ingress -n mbasic
```

Add DNS A record:
```
mbasic.awohl.com → [LOAD_BALANCER_IP]
```

### 11. Wait for SSL Certificate

```bash
# Check certificate status
kubectl describe certificate mbasic-tls -n mbasic

# Wait for "Certificate issued successfully"
```

### 12. Test

Open browser:
- https://mbasic.awohl.com/ (landing page)
- https://mbasic.awohl.com/ide/ (web IDE)

## Monitoring

**View pods:**
```bash
kubectl get pods -n mbasic
```

**View logs:**
```bash
# MBASIC web
kubectl logs -f deployment/mbasic-web -n mbasic

# Landing page
kubectl logs -f deployment/landing-page -n mbasic

# Redis
kubectl logs -f deployment/redis -n mbasic
```

**Check autoscaling:**
```bash
kubectl get hpa -n mbasic
```

**View error logs:**
```bash
# SSH to a pod
kubectl exec -it deployment/mbasic-web -n mbasic -- bash

# Run error log viewer
python3 utils/view_error_logs.py --summary
```

## Scaling

**Manual scaling:**
```bash
kubectl scale deployment mbasic-web --replicas=5 -n mbasic
```

**Auto-scaling is configured** (3-10 replicas based on CPU/memory)

## Updates

**Deploy new version:**
```bash
./deployment/deploy.sh v1.1
```

**Rollback:**
```bash
kubectl rollout undo deployment/mbasic-web -n mbasic
```

**Check rollout status:**
```bash
kubectl rollout status deployment/mbasic-web -n mbasic
```

## Troubleshooting

**Pods not starting:**
```bash
kubectl describe pod -n mbasic
kubectl logs <pod-name> -n mbasic
```

**SSL certificate not issued:**
```bash
kubectl describe certificate mbasic-tls -n mbasic
kubectl logs -n cert-manager deployment/cert-manager
```

**Load balancer IP not assigned:**
```bash
kubectl get svc -n ingress-nginx
# Check if LoadBalancer has EXTERNAL-IP
```

**Database connection issues:**
```bash
# Test from pod
kubectl exec -it deployment/mbasic-web -n mbasic -- bash
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD mbasic_logs
```

**Rate limiting too strict:**
Edit `k8s/ingress.yaml` and adjust:
```yaml
nginx.ingress.kubernetes.io/limit-rps: "10"  # Increase this
```

## Cost Management

**Current setup costs** (approximate):
- Kubernetes cluster (3x $12 nodes): $36/month
- Load Balancer: $12/month
- Managed MySQL: $15/month
- **Total: ~$63/month**

**To reduce costs:**
- Use 2 nodes instead of 3: $24/month
- Use in-cluster MySQL: Save $15/month
- Use smaller nodes: $4/node/month minimum

## Security

**Best practices:**
- [x] Non-root containers
- [x] Secrets encrypted at rest
- [x] TLS/SSL enabled
- [x] Rate limiting configured
- [x] Bot protection (CAPTCHA)
- [x] Resource limits set
- [x] Network policies (TODO)

**Regular maintenance:**
- Update images monthly
- Rotate secrets quarterly
- Review logs for abuse
- Monitor error rates
- Check for security patches

## Backup

**Redis (sessions):**
- Automatically backed up via PersistentVolume
- Can lose sessions without data loss

**MySQL (error logs):**
- DigitalOcean automatic daily backups
- Or manual: `mysqldump` to object storage

**Configuration:**
- All manifests in Git
- Tag each deployment version

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
