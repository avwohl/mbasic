#!/bin/bash
# MBASIC Kubernetes Deployment Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MBASIC Kubernetes Deployment ===${NC}"
echo

# Configuration
REGISTRY="registry.digitalocean.com/YOUR_REGISTRY"  # CHANGE THIS
IMAGE_NAME="mbasic-web"
VERSION="${1:-latest}"
NAMESPACE="mbasic"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl not found${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: docker not found${NC}"
    exit 1
fi

if ! command -v doctl &> /dev/null; then
    echo -e "${RED}Error: doctl not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:${VERSION} .
echo -e "${GREEN}✓ Image built${NC}"
echo

# Tag and push to registry
echo -e "${YELLOW}Pushing to registry...${NC}"
docker tag ${IMAGE_NAME}:${VERSION} ${REGISTRY}/${IMAGE_NAME}:${VERSION}
doctl registry login
docker push ${REGISTRY}/${IMAGE_NAME}:${VERSION}
echo -e "${GREEN}✓ Image pushed${NC}"
echo

# Create namespace if it doesn't exist
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl apply -f deployment/k8s_templates/namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"
echo

# Deploy ConfigMaps
echo -e "${YELLOW}Deploying ConfigMaps...${NC}"

# Update landing page ConfigMap with actual HTML
kubectl create configmap landing-page-html \
    --from-file=deployment/landing-page/index.html \
    --namespace=${NAMESPACE} \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f deployment/k8s_templates/mbasic-configmap.yaml
echo -e "${GREEN}✓ ConfigMaps deployed${NC}"
echo

# Check for secrets
if [ ! -f "k8s/mbasic-secrets.yaml" ]; then
    echo -e "${RED}Error: k8s/mbasic-secrets.yaml not found${NC}"
    echo "Copy k8s/mbasic-secrets.yaml.example to k8s/mbasic-secrets.yaml"
    echo "and fill in your credentials."
    exit 1
fi

# Deploy secrets
echo -e "${YELLOW}Deploying secrets...${NC}"
kubectl apply -f k8s/mbasic-secrets.yaml
echo -e "${GREEN}✓ Secrets deployed${NC}"
echo

# Deploy Redis
echo -e "${YELLOW}Deploying Redis...${NC}"
kubectl apply -f deployment/k8s_templates/redis-deployment.yaml
echo -e "${GREEN}✓ Redis deployed${NC}"
echo

# Deploy Landing Page
echo -e "${YELLOW}Deploying landing page...${NC}"
kubectl apply -f deployment/k8s_templates/landing-page-deployment.yaml
echo -e "${GREEN}✓ Landing page deployed${NC}"
echo

# Deploy MBASIC Web
echo -e "${YELLOW}Deploying MBASIC Web...${NC}"
# Update image in deployment
sed "s|registry.digitalocean.com/YOUR_REGISTRY/mbasic-web:latest|${REGISTRY}/${IMAGE_NAME}:${VERSION}|g" \
    deployment/k8s_templates/mbasic-deployment.yaml | kubectl apply -f -
echo -e "${GREEN}✓ MBASIC Web deployed${NC}"
echo

# Deploy Ingress
echo -e "${YELLOW}Deploying Ingress...${NC}"
kubectl apply -f deployment/k8s_templates/ingress.yaml
echo -e "${GREEN}✓ Ingress deployed${NC}"
echo

# Wait for deployments
echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
kubectl rollout status deployment/redis -n ${NAMESPACE}
kubectl rollout status deployment/landing-page -n ${NAMESPACE}
kubectl rollout status deployment/mbasic-web -n ${NAMESPACE}
echo -e "${GREEN}✓ All deployments ready${NC}"
echo

# Get load balancer IP
echo -e "${YELLOW}Getting load balancer IP...${NC}"
echo "Waiting for external IP (this may take a few minutes)..."
for i in {1..60}; do
    EXTERNAL_IP=$(kubectl get ingress mbasic-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ -n "$EXTERNAL_IP" ]; then
        break
    fi
    sleep 5
done

if [ -z "$EXTERNAL_IP" ]; then
    echo -e "${RED}Warning: Could not get external IP${NC}"
    echo "Check manually with: kubectl get ingress -n ${NAMESPACE}"
else
    echo -e "${GREEN}✓ Load Balancer IP: ${EXTERNAL_IP}${NC}"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Point mbasic.awohl.com DNS A record to ${EXTERNAL_IP}"
    echo "2. Wait for SSL certificate to be issued (5-30 minutes)"
    echo "3. Check certificate: kubectl describe certificate mbasic-tls -n ${NAMESPACE}"
fi

echo
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo
echo "View pods:    kubectl get pods -n ${NAMESPACE}"
echo "View logs:    kubectl logs -f deployment/mbasic-web -n ${NAMESPACE}"
echo "View ingress: kubectl get ingress -n ${NAMESPACE}"
echo "Scale pods:   kubectl scale deployment mbasic-web --replicas=5 -n ${NAMESPACE}"
