export type Ctx = {
    log: (m: string) => void;
};
export declare function plan(input: any, ctx: Ctx): Promise<{
    lang: any;
    tools: any;
    models: any;
}>;
export declare function scaffold(input: any, ctx: Ctx): Promise<{
    repoPath: any;
}>;
export declare function implement_tools(input: any, ctx: Ctx): Promise<{
    tools: any;
}>;
export declare function wire_openai(input: any, ctx: Ctx): Promise<{
    ok: boolean;
}>;
export declare function test_smoke(input: any, ctx: Ctx): Promise<{
    ok: boolean;
    tool: string;
    result: {
        ok: boolean;
    };
}>;
export declare function package_image(input: any, ctx: Ctx): Promise<{
    image: string;
}>;
export declare function deploy_cloud_run(input: any, ctx: Ctx): Promise<{
    url: string;
}>;
export declare function record_memory(input: any, ctx: Ctx): Promise<{
    saved: boolean;
}>;
//# sourceMappingURL=activities.d.ts.map