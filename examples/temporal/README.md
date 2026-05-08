# Temporal Integration Example

This example demonstrates how to integrate OpenAI Agents SDK with Temporal workflows for reliable, durable agent execution.

## Prerequisites

1. Start the Temporal dev server:
   ```bash
   temporal server start-dev
   ```

2. Install dependencies with Temporal support:
   ```bash
   uv sync --extra temporal
   ```

## Running the Example

1. In one terminal, start the Temporal worker:
   ```bash
   python examples/temporal/agent_workflow.py
   ```

2. The worker will execute a sample workflow and print the result.

## Monitoring with Temporal Web UI

The Temporal Web UI provides comprehensive monitoring and debugging capabilities for workflow executions:

- **Server**: localhost:7233
- **UI**: http://localhost:8233
- **Metrics**: http://localhost:64597/metrics

### Key UI Features

- **Namespaces**: View all namespaces in your Temporal service
- **Workflows**: List and filter workflow executions by status, ID, type, time, and custom attributes
- **Saved Views**: Save and reuse frequently used visibility queries (up to 20 custom views)
- **History**: View detailed event history, timeline, and JSON data for each workflow
- **Relationships**: See workflow hierarchy with parent/child relationships
- **Workers**: Monitor workers polling on task queues
- **Pending Activities**: View pending activity executions
- **Call Stack**: Debug with stack traces from running workflows
- **Queries**: View queries sent to workflows
- **Metadata**: Access user metadata and event logs

### Workflow Actions

From the UI, you can:
- Cancel workflow executions
- Send signals or updates
- Reset or terminate workflows
- Start new workflows with pre-filled values

### Schedules

Manage scheduled workflows with cron-like syntax for recurring agent runs.

## How it Works

- The `AgentWorkflow` class defines a Temporal workflow that creates and runs an OpenAI Agent.
- The workflow uses a fake model for demonstration purposes.
- Temporal provides durability, retries, and observability for agent executions.

## Benefits

- **Durability**: Workflows survive server restarts and failures.
- **Observability**: Monitor agent executions through Temporal UI.
- **Reliability**: Automatic retries and error handling.
- **Scalability**: Distribute agent workloads across multiple workers.

## Next Steps

- Replace `FakeModel()` with a real OpenAI model for production use.
- Add more complex workflows with multiple agent interactions.
- Integrate with MCP servers for tool-augmented agents.
- Use Temporal's scheduling features for periodic agent runs.
- Set up custom data converters and codec servers for secure data handling.