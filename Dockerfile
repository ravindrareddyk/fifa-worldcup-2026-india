# =============================================================================
# WC India Hub 2026 - Professional DevOps Showcase Dockerfile
# =============================================================================
# Best practices applied:
# - Small base image (slim)
# - Non-root user for security
# - Layer caching (requirements before code)
# - Healthcheck for orchestrators
# - Clear labels for image metadata
# =============================================================================

FROM python:3.11-slim

LABEL org.opencontainers.image.title="WC India Hub 2026"
LABEL org.opencontainers.image.description="FIFA World Cup 2026 fan dashboard for Indian supporters - Streamlit + ML + DevOps"
LABEL org.opencontainers.image.authors="Indian IT Faculty"
LABEL org.opencontainers.image.source="https://github.com/your-org/wc-india-hub-2026"

# Create non-root user early
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps first (best cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Fix permissions for non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root
USER appuser

# Streamlit port
EXPOSE 8501

# Healthcheck (used by Docker, compose, k8s, etc.)
HEALTHCHECK --interval=30s --timeout=10s --start-period=8s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Production-grade Streamlit launch
CMD ["streamlit", "run", "wc_india_hub.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true", \
     "--browser.gatherUsageStats=false"]

