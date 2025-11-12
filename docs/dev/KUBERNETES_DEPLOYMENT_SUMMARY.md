# MBASIC Kubernetes Deployment - Quick Reference

## What Was Created

Complete deployment system for MBASIC web UI on DigitalOcean Kubernetes at `https://mbasic.awohl.com`

## Files Created

```
docs/dev/
└── KUBERNETES_DEPLOYMENT_PLAN.md   # Comprehensive deployment guide

deployment/
├── deploy.sh                        # Automated deployment script
├── landing-page/
│   └── index.html                  # Static landing page
└── README.md                        # Deployment instructions

k8s/
├── namespace.yaml                   # Namespace: mbasic
├── redis-deployment.yaml            # Redis for sessions
├── landing-page-deployment.yaml     # Nginx static page
├── mbasic-deployment.yaml           # MBASIC web pods (3-10)
├── mbasic-configmap.yaml            # Configuration
├── mbasic-secrets.yaml.example      # Credentials template
└── ingress.yaml                     # SSL + routing

src/
└── bot_protection.py                # hCaptcha + rate limiting

Dockerfile                           # Production container
.dockerignore                        # Build optimization
```

## Architecture

```
https://mbasic.awohl.com
    │
    ├── / → Landing Page
    │       (Static nginx, project info)
    │
    └── /ide/ → MBASIC Web IDE
            (Load-balanced, 3-10 pods)
            ├── Redis (sessions)
            └── MySQL (error logging)
```

## Quick Deployment

```bash
# 1. Prerequisites
doctl kubernetes cluster create mbasic-cluster --region nyc1 --node-pool "name=workers;size=s-2vcpu-4gb;count=3"
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/do/deploy.yaml

# 2. Set up database
# Create MySQL via DO dashboard, run: mysql < config/setup_mysql_logging.sql

# 3. Configure secrets
cp k8s/mbasic-secrets.yaml.example k8s/mbasic-secrets.yaml
# Edit with real credentials

# 4. Deploy
./deployment/deploy.sh v1.0

# 5. Configure DNS
# Point mbasic.awohl.com → [LOAD_BALANCER_IP from deploy output]
```

## Bot Protection

**hCaptcha Integration:**
- Free tier: 10,000 requests/month
- Shows CAPTCHA on first visit
- 24-hour verified session
- Stored in Redis

**Rate Limiting:**
- 10 requests/minute per IP
- Configured in nginx-ingress
- Prevents API abuse

## Cost

**DigitalOcean Monthly:**
- 3x nodes ($12): $36
- Load balancer: $12
- Managed MySQL: $15
- **Total: ~$63**

**Budget option:** $36 (in-cluster MySQL)

## Scaling

- **Min:** 3 pods
- **Max:** 10 pods
- **Auto-scale:** CPU > 70% or Memory > 80%
- **Manual:** `kubectl scale deployment mbasic-web --replicas=5 -n mbasic`

## Monitoring

```bash
# View pods
kubectl get pods -n mbasic

# View logs
kubectl logs -f deployment/mbasic-web -n mbasic

# Check errors (from pod)
kubectl exec -it deployment/mbasic-web -n mbasic -- python3 utils/view_error_logs.py --summary

# Check autoscaling
kubectl get hpa -n mbasic
```

## Security

- ✅ HTTPS/SSL (Let's Encrypt)
- ✅ Bot protection (hCaptcha)
- ✅ Rate limiting (nginx)
- ✅ Non-root containers
- ✅ Resource limits
- ✅ Encrypted secrets

## URLs

- **Landing:** https://mbasic.awohl.com/
- **IDE:** https://mbasic.awohl.com/ide/
- **Docs:** https://avwohl.github.io/mbasic/

## Before Launch Checklist

- [ ] Create Kubernetes cluster
- [ ] Create container registry
- [ ] Set up MySQL database
- [ ] Get hCaptcha keys
- [ ] Configure secrets file
- [ ] Update registry URL in deploy.sh
- [ ] Test locally with Docker
- [ ] Deploy to production
- [ ] Configure DNS
- [ ] Verify SSL certificate
- [ ] Test bot protection
- [ ] Load test (50-100 concurrent users)
- [ ] Announce to vintage computing forums

## Rollback

```bash
# Quick rollback
kubectl rollout undo deployment/mbasic-web -n mbasic

# Or scale to zero
kubectl scale deployment mbasic-web --replicas=0 -n mbasic
```

## Support

- **Deployment Plan:** [KUBERNETES_DEPLOYMENT_PLAN.md](KUBERNETES_DEPLOYMENT_PLAN.md)
- **Setup Guide:** `deployment/README.md` (in repository root)
- **Issues:** https://github.com/avwohl/mbasic/issues
