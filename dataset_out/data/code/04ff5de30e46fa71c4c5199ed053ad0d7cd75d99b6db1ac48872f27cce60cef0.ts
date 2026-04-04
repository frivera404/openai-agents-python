import { Connection, Client } from "@temporalio/client";
import { Payload } from "./defs";

async function main() {
  const conn = await Connection.connect();
  const client = new Client({ connection: conn });

  // Load configuration from environment or .env.runlimited
  const openaiKey = process.env.OPENAI_API_KEY || "your-openai-key-here";
  const gcpProject = process.env.GCP_PROJECT || "your-gcp-project-id";

  const input: Payload = {
    workflowId: `mcp-${Date.now()}`,
    repo: {
      name: "mcp-openai-chat",
      path: "/workspace/mcp"
    },
    lang: "python",
    tools: ["get_status", "openai_chat", "list_files"],
    models: { chat: "gpt-4o" },
    cloud: {
      project: gcpProject,
      region: "us-central1",
      service: "mcp-openai"
    },
    secretsRef: { OPENAI_API_KEY: "env" },
    deploy: { cloudRun: true },
    timeouts: { overallSec: 900 }
  };

  console.log("Starting MCP Scaffold Deploy Workflow...");
  console.log(`Workflow ID: ${input.workflowId}`);
  console.log(`Language: ${input.lang}`);
  console.log(`Tools: ${input.tools.join(", ")}`);

  const handle = await client.workflow.start("McpScaffoldDeployWorkflow", {
    taskQueue: "ai-agent-queue",
    workflowId: input.workflowId,
    args: [input],
  });

  console.log("Workflow started successfully!");
  console.log(`Workflow ID: ${handle.workflowId}`);

  try {
    const result = await handle.result();
    console.log("Workflow completed!");
    console.log("Result:", result);
  } catch (error) {
    console.error("Workflow failed:", error);
  }
}

main().catch(console.error);