import { proxyActivities, defineSignal, defineQuery, setHandler } from "@temporalio/workflow";
import type * as acts from "./activities";
import type { Payload } from "./defs";

const { plan, scaffold, implement_tools, wire_openai, test_smoke, package_image, deploy_cloud_run, record_memory } =
  proxyActivities<typeof acts>({ startToCloseTimeout: "30 seconds", retry: { maximumAttempts: 3 } });

const cancelBuild = defineSignal("cancelBuild");
const updateConfig = defineSignal<[Partial<Payload>]>("updateConfig");
const statusQ = defineQuery<string>("status");
const logsQ = defineQuery<string[]>("logs");

export async function McpScaffoldDeployWorkflow(payload: Payload): Promise<{ url?: string }> {
  let cancelled = false;
  let status = "starting";
  const logs: string[] = [];
  const log = (m: string) => { logs.push(m); status = m; };

  setHandler(cancelBuild, () => { cancelled = true; log("cancel requested"); });
  setHandler(updateConfig, (patch) => { Object.assign(payload, patch); log("config updated"); });
  setHandler(statusQ, () => status);
  setHandler(logsQ, () => logs.slice(-100));

  const ctx = { log };

  const planOut = await plan(payload, ctx);
  if (cancelled) throw new Error("cancelled");

  const scOut = await scaffold({ ...payload, planOut }, ctx);
  if (cancelled) throw new Error("cancelled");

  await implement_tools({ ...payload, ...scOut }, ctx);
  await wire_openai(payload, ctx);
  await test_smoke({ repoPath: scOut.repoPath }, ctx);

  const img = await package_image(payload, ctx);
  let url: string | undefined = undefined;
  if (payload.deploy.cloudRun) {
    const dep = await deploy_cloud_run({ ...payload, image: img.image }, ctx);
    url = dep.url;
  }

  await record_memory({ payload, url }, ctx);
  log("done");
  return { url };
}