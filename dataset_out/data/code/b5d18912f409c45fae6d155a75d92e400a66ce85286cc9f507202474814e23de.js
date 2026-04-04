"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.McpScaffoldDeployWorkflow = McpScaffoldDeployWorkflow;
const workflow_1 = require("@temporalio/workflow");
const { plan, scaffold, implement_tools, wire_openai, test_smoke, package_image, deploy_cloud_run, record_memory } = (0, workflow_1.proxyActivities)({ startToCloseTimeout: "30 seconds", retry: { maximumAttempts: 3 } });
const cancelBuild = (0, workflow_1.defineSignal)("cancelBuild");
const updateConfig = (0, workflow_1.defineSignal)("updateConfig");
const statusQ = (0, workflow_1.defineQuery)("status");
const logsQ = (0, workflow_1.defineQuery)("logs");
async function McpScaffoldDeployWorkflow(payload) {
    let cancelled = false;
    let status = "starting";
    const logs = [];
    const log = (m) => { logs.push(m); status = m; };
    (0, workflow_1.setHandler)(cancelBuild, () => { cancelled = true; log("cancel requested"); });
    (0, workflow_1.setHandler)(updateConfig, (patch) => { Object.assign(payload, patch); log("config updated"); });
    (0, workflow_1.setHandler)(statusQ, () => status);
    (0, workflow_1.setHandler)(logsQ, () => logs.slice(-100));
    const ctx = { log };
    const planOut = await plan(payload, ctx);
    if (cancelled)
        throw new Error("cancelled");
    const scOut = await scaffold({ ...payload, planOut }, ctx);
    if (cancelled)
        throw new Error("cancelled");
    await implement_tools({ ...payload, ...scOut }, ctx);
    await wire_openai(payload, ctx);
    await test_smoke({ repoPath: scOut.repoPath }, ctx);
    const img = await package_image(payload, ctx);
    let url = undefined;
    if (payload.deploy.cloudRun) {
        const dep = await deploy_cloud_run({ ...payload, image: img.image }, ctx);
        url = dep.url;
    }
    await record_memory({ payload, url }, ctx);
    log("done");
    return { url };
}
//# sourceMappingURL=workflows.js.map