FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml uv.lock ./
COPY README.md ./

# Install uv package manager
RUN pip install uv

# Install dependencies including the project
# Install dependencies
RUN uv sync --frozen

# Install the project in editable mode
RUN uv pip install -e .

# Ensure the uv-created virtual environment is used for subsequent commands
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Install FastAPI and uvicorn for the MCP server
RUN pip install "fastapi>=0.104.0,<1" "uvicorn[standard]>=0.24.0,<1"

# Copy source code
COPY src/ ./src/
COPY examples/ ./examples/
COPY mcp_filesystem_server.py ./mcp_filesystem_server.py

# Make the script executable
RUN chmod +x /app/mcp_filesystem_server.py

# Create workspace directory
RUN mkdir -p /workspace

# Set the default command
CMD ["python", "mcp_filesystem_server.py", "--http", "--host", "0.0.0.0", "--port", "3000"]
