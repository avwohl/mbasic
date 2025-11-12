# MBASIC Web UI - Production Docker Image
# Multi-stage build for smaller final image

# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy MBASIC source
COPY . .

# Stage 2: Runtime
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash mbasic

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/mbasic/.local

# Copy MBASIC application
COPY --chown=mbasic:mbasic . .

# Set up PATH for user-installed packages
ENV PATH=/home/mbasic/.local/bin:$PATH

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health', timeout=2)" || exit 1

# Switch to non-root user
USER mbasic

# Expose port
EXPOSE 8080

# Run MBASIC web UI
CMD ["python3", "mbasic.py", "--ui", "web", "--port", "8080"]
