import { z } from "zod";
export declare const Payload: z.ZodObject<{
    workflowId: z.ZodString;
    repo: z.ZodObject<{
        name: z.ZodString;
        path: z.ZodString;
        gitUrl: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        path: string;
        name: string;
        gitUrl?: string | undefined;
    }, {
        path: string;
        name: string;
        gitUrl?: string | undefined;
    }>;
    lang: z.ZodUnion<[z.ZodLiteral<"python">, z.ZodLiteral<"node">]>;
    tools: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    models: z.ZodObject<{
        chat: z.ZodString;
        emb: z.ZodOptional<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        chat: string;
        emb?: string | undefined;
    }, {
        chat: string;
        emb?: string | undefined;
    }>;
    cloud: z.ZodObject<{
        project: z.ZodString;
        region: z.ZodString;
        service: z.ZodString;
    }, "strip", z.ZodTypeAny, {
        project: string;
        region: string;
        service: string;
    }, {
        project: string;
        region: string;
        service: string;
    }>;
    secretsRef: z.ZodRecord<z.ZodString, z.ZodString>;
    deploy: z.ZodObject<{
        cloudRun: z.ZodDefault<z.ZodBoolean>;
    }, "strip", z.ZodTypeAny, {
        cloudRun: boolean;
    }, {
        cloudRun?: boolean | undefined;
    }>;
    timeouts: z.ZodDefault<z.ZodObject<{
        overallSec: z.ZodDefault<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        overallSec: number;
    }, {
        overallSec?: number | undefined;
    }>>;
}, "strip", z.ZodTypeAny, {
    workflowId: string;
    repo: {
        path: string;
        name: string;
        gitUrl?: string | undefined;
    };
    lang: "python" | "node";
    tools: string[];
    models: {
        chat: string;
        emb?: string | undefined;
    };
    cloud: {
        project: string;
        region: string;
        service: string;
    };
    secretsRef: Record<string, string>;
    deploy: {
        cloudRun: boolean;
    };
    timeouts: {
        overallSec: number;
    };
}, {
    workflowId: string;
    repo: {
        path: string;
        name: string;
        gitUrl?: string | undefined;
    };
    lang: "python" | "node";
    models: {
        chat: string;
        emb?: string | undefined;
    };
    cloud: {
        project: string;
        region: string;
        service: string;
    };
    secretsRef: Record<string, string>;
    deploy: {
        cloudRun?: boolean | undefined;
    };
    tools?: string[] | undefined;
    timeouts?: {
        overallSec?: number | undefined;
    } | undefined;
}>;
export type Payload = z.infer<typeof Payload>;
//# sourceMappingURL=defs.d.ts.map