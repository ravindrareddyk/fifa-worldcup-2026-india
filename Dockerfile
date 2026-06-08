# WC India Hub 2026 - DevOps Showcase Dockerfile
# Simple, production-style container for Streamlit app

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for pandas, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Healthcheck (optional but good for DevOps demos)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app
# Use --server.headless true for container environments
CMD ["streamlit", "run", "wc_india_hub.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
