FROM python:3.11-slim

WORKDIR /app

RUN pip install "openai-agents" "fastapi>=0.104.0,<1" "uvicorn[standard]>=0.24.0,<1"

COPY mcp_filesystem_server.py .

CMD ["python", "mcp_filesystem_server.py"]
