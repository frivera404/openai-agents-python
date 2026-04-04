"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Payload = void 0;
const zod_1 = require("zod");
exports.Payload = zod_1.z.object({
    workflowId: zod_1.z.string(),
    repo: zod_1.z.object({
        name: zod_1.z.string(),
        path: zod_1.z.string(),
        gitUrl: zod_1.z.string().optional()
    }),
    lang: zod_1.z.union([zod_1.z.literal("python"), zod_1.z.literal("node")]),
    tools: zod_1.z.array(zod_1.z.string()).default(["get_status", "openai_chat", "list_files"]),
    models: zod_1.z.object({
        chat: zod_1.z.string(),
        emb: zod_1.z.string().optional()
    }),
    cloud: zod_1.z.object({
        project: zod_1.z.string(),
        region: zod_1.z.string(),
        service: zod_1.z.string()
    }),
    secretsRef: zod_1.z.record(zod_1.z.string()),
    deploy: zod_1.z.object({
        cloudRun: zod_1.z.boolean().default(true)
    }),
    timeouts: zod_1.z.object({
        overallSec: zod_1.z.number().default(900)
    }).default({ overallSec: 900 }),
});
//# sourceMappingURL=defs.js.map