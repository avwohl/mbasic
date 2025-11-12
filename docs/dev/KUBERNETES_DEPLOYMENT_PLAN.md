# MBASIC Web UI - Kubernetes Deployment Plan

## Overview

Deploy MBASIC web UI to DigitalOcean Kubernetes cluster for public access at `https://mbasic.awohl.com`.

**Goals:**
- Public web UI for vintage computing community
- Load-balanced across multiple pods
- Bot protection (CAPTCHA/rate limiting)
- Landing page with links to GitHub Pages docs
- Production-ready monitoring and error logging

## Implementation Status

**Code Implementation: ✅ Complete**
- Dockerfile with multi-stage build and health checks
- Kubernetes manifests (namespace, deployments, services, ingress)
- Bot protection module (hCaptcha integration)
- Landing page HTML
- Deployment automation script
- Health check endpoint at `/health`
- All dependencies added to requirements.txt

**Pending: Infrastructure Setup**
- DigitalOcean Kubernetes cluster creation
- Container registry setup
- MySQL database provisioning
- hCaptcha account and keys
- DNS configuration
- SSL certificate issuance

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  mbasic.awohl.com (DNS)                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│            DigitalOcean Load Balancer (HTTPS)                   │
│                  SSL Termination                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│              Kubernetes Ingress Controller                      │
│                    (nginx-ingress)                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐
│  Landing     │  │  MBASIC Web  │  │  MBASIC Web │
│  Page        │  │  Pod 1       │  │  Pod 2      │
│  (Static)    │  │              │  │             │
└──────────────┘  └───────┬──────┘  └──────┬──────┘
                          │                 │
        ┌─────────────────┼─────────────────┘
        │                 │
┌───────▼──────┐  ┌───────▼──────┐
│   Redis      │  │   MySQL      │
│   (Session)  │  │   (Errors)   │
└──────────────┘  └──────────────┘
```

## URL Structure

- **Landing Page:** `https://mbasic.awohl.com/`
  - Static page with project overview
  - Links to GitHub Pages docs
  - "Launch Web IDE" button → `/ide/`

- **Web IDE:** `https://mbasic.awohl.com/ide/`
  - MBASIC web UI (load-balanced pods)
  - Bot protection (CAPTCHA on first visit)
  - Session-based access after verification

- **Documentation:** `https://avwohl.github.io/mbasic/`
  - GitHub Pages (already deployed)
  - No change needed

## Components

### 1. Docker Container

**Base Image:** `python:3.12-slim`

**Includes:**
- MBASIC interpreter
- NiceGUI web framework
- Redis client (session storage)
- MySQL client (error logging)
- Bot protection middleware

**Size Target:** < 200MB compressed

### 2. Kubernetes Resources

**Deployments:**
- `mbasic-web` - MBASIC IDE pods (3 replicas)
- `landing-page` - Static landing page (1 replica)
- `redis` - Session storage (1 replica with persistence)

**Services:**
- `mbasic-web-service` - ClusterIP for IDE pods
- `landing-page-service` - ClusterIP for landing page
- `redis-service` - ClusterIP for Redis

**Ingress:**
- Single ingress resource with path-based routing
- `/` → landing page
- `/ide/*` → MBASIC web pods
- TLS certificate (Let's Encrypt via cert-manager)

**ConfigMaps:**
- `mbasic-config` - multiuser.json configuration
- `landing-page-html` - Static HTML content

**Secrets:**
- `mysql-credentials` - Database connection details
- `bot-protection-secret` - CAPTCHA keys

**PersistentVolumeClaims:**
- `redis-data` - Redis persistence (10GB)
- `mysql-data` - MySQL data (if in-cluster, 50GB)

### 3. External Services

**DigitalOcean Managed Database (Recommended):**
- MySQL 8.0
- Shared across all pods
- Automatic backups
- High availability

**Alternative:** In-cluster MySQL StatefulSet

### 4. Bot Protection Strategy

**Option A: hCaptcha (Recommended)**
- Free tier: 10,000 requests/month
- Privacy-focused
- Easy integration with NiceGUI
- Show CAPTCHA on first visit, store verified session in Redis

**Option B: Cloudflare Turnstile**
- Free, unlimited
- Invisible CAPTCHA
- Good bot detection

**Option C: Simple Challenge**
- "Click here to prove you're human"
- Less robust but free and simple

**Implementation:**
- CAPTCHA page before IDE access
- 24-hour session cookie after verification
- Rate limiting: 60 requests/minute per IP

### 5. Monitoring & Logging

**Prometheus Metrics:**
- Pod health
- Request rate
- Active sessions
- Error rate

**Logging:**
- Container logs → DigitalOcean Logging
- Application errors → MySQL (existing system)
- Access logs for bot analysis

## Implementation Plan

### Phase 1: Containerization

1. **Create Dockerfile**
   - Multi-stage build for smaller image
   - Non-root user for security
   - Health check endpoint

2. **Build and test locally**
   ```bash
   docker build -t mbasic-web:latest .
   docker run -p 8080:8080 mbasic-web:latest
   ```

3. **Push to DigitalOcean Container Registry**
   ```bash
   doctl registry login
   docker tag mbasic-web:latest registry.digitalocean.com/YOUR_REGISTRY/mbasic-web:v1.0
   docker push registry.digitalocean.com/YOUR_REGISTRY/mbasic-web:v1.0
   ```

### Phase 2: Database Setup

**Option A: DigitalOcean Managed Database (Recommended)**
1. Create MySQL cluster via DigitalOcean dashboard
2. Create database: `mbasic_logs`
3. Run schema: `mysql < config/setup_mysql_logging.sql`
4. Get connection details (host, port, CA cert)
5. Create Kubernetes secret with credentials

**Option B: In-cluster MySQL**
1. Deploy MySQL StatefulSet
2. Create persistent volume
3. Initialize database
4. Configure backups

### Phase 3: Kubernetes Deployment

1. **Install cert-manager (SSL certificates)**
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

2. **Deploy Redis**
   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/redis-service.yaml
   ```

3. **Deploy MBASIC Web**
   ```bash
   kubectl apply -f k8s/mbasic-configmap.yaml
   kubectl apply -f k8s/mbasic-secrets.yaml
   kubectl apply -f k8s/mbasic-deployment.yaml
   kubectl apply -f k8s/mbasic-service.yaml
   ```

4. **Deploy Landing Page**
   ```bash
   kubectl apply -f k8s/landing-page-configmap.yaml
   kubectl apply -f k8s/landing-page-deployment.yaml
   kubectl apply -f k8s/landing-page-service.yaml
   ```

5. **Deploy Ingress**
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

### Phase 4: DNS & SSL

1. **Get Load Balancer IP**
   ```bash
   kubectl get ingress mbasic-ingress
   # Note the EXTERNAL-IP
   ```

2. **Configure DNS**
   - Add A record: `mbasic.awohl.com` → Load Balancer IP
   - Wait for propagation (5-30 minutes)

3. **SSL Certificate**
   - cert-manager automatically requests Let's Encrypt cert
   - Verify: `kubectl describe certificate mbasic-tls`

### Phase 5: Bot Protection

1. **Sign up for hCaptcha**
   - Get site key and secret key
   - Add to Kubernetes secrets

2. **Add CAPTCHA middleware to MBASIC**
   - Show CAPTCHA before IDE access
   - Store verified sessions in Redis
   - 24-hour expiration

3. **Add rate limiting**
   - nginx-ingress rate limiting annotations
   - 60 requests/minute per IP

### Phase 6: Testing & Monitoring

1. **Load testing**
   ```bash
   # Test with 10 concurrent users
   ab -n 1000 -c 10 https://mbasic.awohl.com/ide/
   ```

2. **Monitor pods**
   ```bash
   kubectl top pods
   kubectl logs -f deployment/mbasic-web
   ```

3. **Check error logging**
   ```bash
   # SSH to a pod
   kubectl exec -it deployment/mbasic-web -- bash
   python3 utils/view_error_logs.py --summary
   ```

### Phase 7: Launch

1. **Create landing page content**
   - Project description
   - Features list
   - Links to docs/GitHub
   - "Launch IDE" button

2. **Soft launch**
   - Test with small group
   - Monitor for issues
   - Check bot protection

3. **Public announcement**
   - Vintage computing forums
   - Include usage guidelines
   - Request feedback

## Cost Estimate (DigitalOcean)

**Kubernetes Cluster:**
- 3x Basic nodes ($12/month each): $36/month
- Load Balancer: $12/month

**Managed Database (Recommended):**
- MySQL Basic (1GB RAM, 10GB storage): $15/month

**Container Registry:**
- 500GB transfer/month: Included

**Total:** ~$63/month

**Cheaper Alternative (In-cluster MySQL):**
- 2x Basic nodes: $24/month
- Load Balancer: $12/month
- Total: ~$36/month (but less reliable database)

## Security Considerations

1. **Container Security**
   - Non-root user
   - Read-only filesystem
   - No privileged containers
   - Scan images for vulnerabilities

2. **Network Security**
   - Internal services use ClusterIP (not exposed)
   - Only ingress is public
   - NetworkPolicies to restrict pod communication

3. **Secrets Management**
   - Use Kubernetes secrets
   - Encrypt secrets at rest
   - Rotate credentials periodically

4. **Resource Limits**
   - Set CPU/memory limits on pods
   - Prevent resource exhaustion
   - Auto-scaling based on load

5. **Bot Protection**
   - CAPTCHA verification
   - Rate limiting
   - IP blocking for abuse
   - Monitor for unusual patterns

## Scaling Strategy

**Horizontal Pod Autoscaler:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mbasic-web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mbasic-web
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Scaling triggers:**
- CPU > 70%: Add pods
- Concurrent sessions > 50: Add pods
- Automatically scale down when load decreases

## Backup Strategy

**Redis (Sessions):**
- RDB snapshots every 15 minutes
- AOF logging for durability
- Can lose sessions, not critical

**MySQL (Error Logs):**
- DigitalOcean automatic daily backups
- Or manual mysqldump to object storage
- Retain 7 days

**Configuration:**
- All Kubernetes manifests in Git
- Easy to redeploy

## Monitoring Checklist

- [ ] Pod health checks working
- [ ] SSL certificate valid
- [ ] DNS resolving correctly
- [ ] Load balancer distributing traffic
- [ ] Redis sessions persisting
- [ ] MySQL errors logging
- [ ] CAPTCHA blocking bots
- [ ] Rate limiting working
- [ ] No memory leaks
- [ ] Logs being collected
- [ ] Alerts configured

## Launch Checklist

- [ ] Docker image built and pushed
- [ ] Kubernetes cluster created
- [ ] Redis deployed and tested
- [ ] MySQL database created and initialized
- [ ] MBASIC web pods deployed (3 replicas)
- [ ] Landing page deployed
- [ ] Ingress configured
- [ ] SSL certificate issued
- [ ] DNS pointed to load balancer
- [ ] Bot protection enabled
- [ ] Rate limiting configured
- [ ] Monitoring/logging set up
- [ ] Load testing completed
- [ ] Backup strategy implemented
- [ ] Documentation updated
- [ ] Soft launch with test users
- [ ] Ready for public announcement

## Rollback Plan

If issues arise:

1. **Scale down pods**
   ```bash
   kubectl scale deployment mbasic-web --replicas=0
   ```

2. **Update landing page**
   - Show "Temporarily offline for maintenance"
   - Provide alternative links

3. **Investigate and fix**
   - Check logs: `kubectl logs -f deployment/mbasic-web`
   - Check events: `kubectl get events`
   - Check database connectivity

4. **Deploy fix**
   ```bash
   docker build -t mbasic-web:v1.1 .
   docker push registry.digitalocean.com/YOUR_REGISTRY/mbasic-web:v1.1
   kubectl set image deployment/mbasic-web mbasic-web=registry.digitalocean.com/YOUR_REGISTRY/mbasic-web:v1.1
   ```

5. **Rollback if needed**
   ```bash
   kubectl rollout undo deployment/mbasic-web
   ```

## Next Steps

1. Review this plan and adjust based on requirements
2. Create Dockerfile and test locally
3. Create Kubernetes manifests
4. Set up DigitalOcean resources (cluster, database)
5. Implement bot protection
6. Deploy to staging environment
7. Load test
8. Deploy to production
9. Create landing page
10. Announce to community

## Questions to Answer

1. **Database:** Managed DigitalOcean MySQL or in-cluster StatefulSet?
2. **Bot Protection:** hCaptcha, Cloudflare Turnstile, or simple challenge?
3. **Initial Replicas:** Start with 3 or 5 MBASIC pods?
4. **Session Duration:** How long should verified sessions last? (24 hours?)
5. **Rate Limits:** 60 requests/minute per IP too strict or too lenient?
6. **Monitoring:** Use DigitalOcean built-in or deploy Prometheus/Grafana?
7. **Backup:** Automated daily or manual weekly?

## Resources

- [DigitalOcean Kubernetes Docs](https://docs.digitalocean.com/products/kubernetes/)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [cert-manager](https://cert-manager.io/docs/)
- [hCaptcha](https://www.hcaptcha.com/)
- [nginx-ingress rate limiting](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#rate-limiting)
