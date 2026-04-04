import { Worker } from "@temporalio/worker";
import * as activities from "./activities";

async function run() {
  const worker = await Worker.create({
    workflowsPath: require.resolve("./workflows"),
    activities,
    taskQueue: "ai-agent-queue",
  });
  console.log("Worker started successfully! Listening on ai-agent-queue");
  await worker.run();
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});