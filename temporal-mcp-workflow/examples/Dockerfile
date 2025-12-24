# Multi-stage Dockerfile for MCP server
FROM node:18-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python stage
FROM base as python-builder
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Node.js stage
FROM base as node-builder
COPY package*.json ./
RUN npm ci --only=production

# Final stage
FROM base
COPY --from=python-builder /usr/local/lib/python3.*/site-packages /usr/local/lib/python3.*/site-packages
COPY --from=node-builder /app/node_modules /app/node_modules

# Copy application code
COPY . .

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Default to Python server, can be overridden
CMD ["python3", "server.py"]