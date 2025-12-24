import { z } from "zod";

export const Payload = z.object({
  workflowId: z.string(),
  repo: z.object({
    name: z.string(),
    path: z.string(),
    gitUrl: z.string().optional()
  }),
  lang: z.union([z.literal("python"), z.literal("node")]),
  tools: z.array(z.string()).default(["get_status", "openai_chat", "list_files"]),
  models: z.object({
    chat: z.string(),
    emb: z.string().optional()
  }),
  cloud: z.object({
    project: z.string(),
    region: z.string(),
    service: z.string()
  }),
  secretsRef: z.record(z.string()),
  deploy: z.object({
    cloudRun: z.boolean().default(true)
  }),
  timeouts: z.object({
    overallSec: z.number().default(900)
  }).default({ overallSec: 900 }),
});

export type Payload = z.infer<typeof Payload>;