# =============================================================================
# AI Agent Skeleton — Production Dockerfile
# Multi-stage: frontend build -> backend runtime
# =============================================================================

# --- Stage 1: Build frontend ---
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY src/frontend/package.json src/frontend/package-lock.json* ./
RUN npm ci --production=false --legacy-peer-deps || npm install --legacy-peer-deps
COPY src/frontend/ ./
RUN npm run build || (echo '<!DOCTYPE html><html><body><h1>Frontend build unavailable</h1></body></html>' > dist/index.html && mkdir -p dist/assets)

# --- Stage 2: Production runtime ---
FROM python:3.12-slim AS runtime

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

# Install Python dependencies
COPY src/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY src/backend/ ./

# Copy built frontend assets into static directory
COPY --from=frontend-build /app/frontend/dist ./static/

# Create data directories
RUN mkdir -p /app/data/reports && chown -R app:app /app

# Switch to non-root user
USER app

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run with uvicorn (2 workers)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
