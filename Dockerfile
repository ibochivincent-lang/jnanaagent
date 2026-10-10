# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging specifications
COPY pyproject.toml README.md ./

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy source code and reports
COPY src/ ./src/
COPY reports/ ./reports/

# Default environment defaults
ENV RESEARCH_AGENT_MODEL=claude-haiku
ENV LITELLM_BASE_URL=https://litellm.vision.aivar.app/v1

EXPOSE 8000

CMD ["python", "-m", "research_agent.server", "--host", "0.0.0.0", "--port", "8000"]
