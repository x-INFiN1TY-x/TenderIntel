# TenderIntel Multi-stage Dockerfile
# Supports both development and production deployments

# Base image with Python and system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies including Tesseract OCR
RUN apt-get update && apt-get install -y \
    curl \
    git \
    sqlite3 \
    libsqlite3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements files
COPY pyproject.toml README.md ./

# Setup stage - for database initialization
FROM base as setup

# Install Python dependencies for setup
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e ".[tenderx]"

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Set up data directory
RUN mkdir -p /app/data

# Expose setup command
CMD ["python", "scripts/setup/initialize_project.py"]

# Runtime stage - for API server
FROM base as runtime

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -e ".[tenderx,prod]"

# Install Chrome for Selenium (optional for scraping)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 1000 tenderintel \
    && useradd --uid 1000 --gid tenderintel --shell /bin/bash --create-home tenderintel

# Copy application code
COPY --chown=tenderintel:tenderintel src/ ./src/
COPY --chown=tenderintel:tenderintel config/ ./config/
COPY --chown=tenderintel:tenderintel scripts/ ./scripts/

# Create directories with proper permissions
RUN mkdir -p /app/data /app/downloads /app/logs \
    && chown -R tenderintel:tenderintel /app

# Switch to non-root user
USER tenderintel

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port
EXPOSE 8002

# Default command
CMD ["python", "-m", "uvicorn", "src.tenderintel.api.server:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]

# Development stage - for development with hot reload
FROM runtime as development

# Install development dependencies
USER root
RUN pip install -e ".[dev,tenderx,opensearch]"

# Install development tools
RUN apt-get update && apt-get install -y \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

USER tenderintel

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "src.tenderintel.api.server:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]
