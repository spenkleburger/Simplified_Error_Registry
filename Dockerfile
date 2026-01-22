# ============================================================================
# Dockerfile - SER Consolidation App
# ============================================================================
# Containerizes the consolidation app for scheduled error consolidation
# ============================================================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Set environment variables (defaults - can be overridden in docker-compose)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV LLM_PROVIDER=ollama
ENV LLM_MODEL=qwen2.5-coder:14b
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

# Default command: run consolidation once (can be overridden for scheduler)
CMD ["python", "-m", "src.consolidation_app.main", "--root", "/projects"]
