# Temporal MCP Scaffold Deploy Workflow

A Temporal-based workflow system for automated MCP (Model Context Protocol) server scaffolding, implementation, testing, and deployment to Google Cloud Run.

## Overview

This system provides an end-to-end automated pipeline for creating MCP servers with the following capabilities:

- **Planning**: Derive specifications from requirements
- **Scaffolding**: Create repository skeleton with basic structure
- **Tool Implementation**: Add MCP tools (get_status, openai_chat, list_files)
- **OpenAI Integration**: Environment checks and client initialization
- **Smoke Testing**: Start server and validate basic functionality
- **Container Packaging**: Docker build, tag, and push
- **Cloud Deployment**: Deploy to Google Cloud Run with health checks
- **Memory Recording**: Persist deployment metadata for future reference

## Architecture

### Workflow Steps
1. `plan()` → Derive language, tools, and models specification
2. `scaffold()` → Create repository skeleton
3. `implement_tools()` → Add MCP tool implementations
4. `wire_openai()` → Validate OpenAI API key and setup
5. `test_smoke()` → Start server and test basic functionality
6. `package_image()` → Build and push Docker container
7. `deploy_cloud_run()` → Deploy to Cloud Run and health check
8. `record_memory()` → Save deployment metadata

### Signals & Queries
- **Signals**: `cancelBuild`, `updateConfig`
- **Queries**: `status`, `logs`

## Setup

### Prerequisites
- Node.js 18+
- Temporal server running (ai-agent-queue task queue)
- Google Cloud SDK (for deployment)
- Docker (for containerization)

### Installation
```bash
cd temporal-mcp-workflow
npm install
npm run build
```

### Environment Variables
Set the following environment variables or use the `.env.runlimited` file:

```bash
# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Google Cloud
GCP_PROJECT=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Temporal
TEMPORAL_ADDRESS=localhost:7233
```

## Usage

### 1. Start Worker
```bash
npm run start:worker
```

### 2. Start Workflow
```bash
npm run start:client
```

### 3. Monitor Workflow
```bash
# Check status
npm run query:status -- --workflow-id mcp-1234567890

# View logs
npm run query:logs -- --workflow-id mcp-1234567890
```

### 4. Control Workflow
```bash
# Cancel workflow
npm run signal:cancel -- --workflow-id mcp-1234567890

# Update configuration
npm run signal:update -- --workflow-id mcp-1234567890 --input '{"lang":"node"}'
```

## Payload Schema

```typescript
{
  workflowId: string,           // Unique workflow identifier
  repo: {
    name: string,               // Repository name
    path: string,               // Local path
    gitUrl?: string            // Optional git URL
  },
  lang: "python" | "node",      // Target language
  tools: string[],              // MCP tools to implement
  models: {
    chat: string,               // Chat model (e.g., "gpt-4o")
    emb?: string               // Optional embedding model
  },
  cloud: {
    project: string,            // GCP project ID
    region: string,             // GCP region
    service: string             // Cloud Run service name
  },
  secretsRef: Record<string, string>, // Secret references
  deploy: {
    cloudRun: boolean          // Enable Cloud Run deployment
  },
  timeouts: {
    overallSec: number          // Overall timeout in seconds
  }
}
```

## Generated MCP Server Structure

### Python Example
```
mcp-openai-chat/
├── server.py          # Main MCP server
├── requirements.txt   # Python dependencies
└── Dockerfile         # Container definition
```

### Node.js Example
```
mcp-openai-chat/
├── server.js          # Main MCP server
├── package.json       # Node dependencies
└── Dockerfile         # Container definition
```

## Operational Policies

- **Idempotency**: All activities are idempotent and can be safely retried
- **Timeouts**: Each activity ≤ 30 seconds, overall workflow ≤ 15 minutes
- **Retries**: Maximum 3 attempts per activity with exponential backoff
- **Secrets**: API keys read from environment, never logged
- **Artifacts**: Only image URL and deployment URL returned; logs via queries

## Development

### Building
```bash
npm run build
```

### Testing
```bash
# Unit tests (when implemented)
npm test

# Integration tests
npm run test:integration
```

### Scripts
- `npm run build` - Compile TypeScript
- `npm run start:worker` - Start Temporal worker
- `npm run start:client` - Start workflow client
- `npm run dev` - Development mode with ts-node

## Integration with Agent Private I

This workflow integrates with the Agent Private I system for automated MCP server deployment:

1. Agent Private I can trigger this workflow for new MCP server requirements
2. Workflow handles the complete CI/CD pipeline
3. Results are recorded in the agent's memory system
4. Deployed servers become available for agent tool usage

## Success Criteria

- ✅ Server starts without errors
- ✅ `get_status` returns `{ok: true}`
- ✅ `openai_chat("ping")` returns valid JSON response
- ✅ Deployed URL responds 200 on `/healthz`
- ✅ Container builds and pushes successfully
- ✅ All activities complete within timeouts

## Troubleshooting

### Common Issues
- **Worker Connection**: Ensure Temporal server is running on `ai-agent-queue`
- **API Keys**: Verify `OPENAI_API_KEY` and GCP credentials are set
- **Docker**: Ensure Docker daemon is running for container builds
- **Permissions**: Check GCP service account has Cloud Run deployment permissions

### Logs and Debugging
Use the query commands to monitor workflow progress:
```bash
temporal workflow query --workflow-id <id> --type logs
temporal workflow query --workflow-id <id> --type status
```

## Contributing

1. Follow TypeScript best practices
2. Ensure all activities are idempotent
3. Add proper error handling and logging
4. Update tests for new functionality
5. Follow the established payload schema

---

**Built for Agent WTClan - Automating MCP server deployment at scale** 🚀