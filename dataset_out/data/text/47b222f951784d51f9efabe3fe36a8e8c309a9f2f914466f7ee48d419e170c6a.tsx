import { useEffect, useState } from 'react';
import type { McpToolsMap, ToolDefinition } from '../api/types';
import { listMcpTools, listTools } from '../api/agentApi';

export function ToolsPage() {
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mcpTools, setMcpTools] = useState<McpToolsMap | null>(null);
  const [mcpError, setMcpError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      setMcpError(null);
      try {
        const [coreTools, discoveredMcpTools] = await Promise.all([
          listTools(),
          listMcpTools().catch((err) => {
            const message = err instanceof Error ? err.message : 'Failed to load MCP tools';
            if (!cancelled) setMcpError(message);
            // Fallback to empty map if MCP listing fails so core tools still show.
            return {} as McpToolsMap;
          }),
        ]);

        if (!cancelled) {
          setTools(coreTools);
          setMcpTools(discoveredMcpTools);
        }
      } catch (err) {
        if (!cancelled) {
          const message = err instanceof Error ? err.message : 'Failed to load tools';
          setError(message);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="min-h-full flex flex-col items-center justify-center py-16">
      <div className="max-w-3xl w-full px-6 text-center">
        <div className="flex flex-col items-center gap-4 mb-8">
          <div className="h-16 w-16 rounded-full bg-blue-500/10 border border-blue-500/40 flex items-center justify-center">
            <span className="text-3xl">⚙️</span>
          </div>
          <div>
            <h2 className="text-3xl font-semibold mb-2">Tools</h2>
            <p className="text-gray-300 max-w-xl mx-auto">
              Manage your custom tools and integrations here. Connect to APIs, databases,
              and other services that your agents can call.
            </p>
          </div>
        </div>

        <button
          type="button"
          className="inline-flex items-center px-6 py-3 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium shadow-lg shadow-blue-900/40 transition-colors mb-8"
          onClick={() => {
            // Re-run the effect by toggling loading state; simple manual refresh.
            window.location.reload();
          }}
        >
          Explore Tools
        </button>

        {loading && <p className="text-gray-300">Loading tools...</p>}
        {error && <p className="text-red-400 text-sm mb-4">{error}</p>}
        {mcpError && (
          <p className="text-yellow-400 text-xs mb-2">
            MCP tools could not be listed: {mcpError}
          </p>
        )}

        {!loading && !error && tools.length === 0 && (
          <p className="text-gray-400">No tools are currently registered for this agent backend.</p>
        )}

        {!loading && tools.length > 0 && (
          <div className="text-left mt-4 space-y-8">
            <div>
              <h3 className="text-lg font-semibold mb-3 text-white">Core Agent Tools</h3>
              <div className="grid gap-4">
                {tools.map((tool) => (
                  <div
                    key={tool.name}
                    className="rounded-lg border border-gray-700 bg-black/40 px-4 py-3 flex flex-col gap-1"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-white">{tool.name}</span>
                        {tool.type && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/40">
                            {tool.type}
                          </span>
                        )}
                      </div>
                      {tool.provider && (
                        <span className="text-xs text-gray-400">{tool.provider}</span>
                      )}
                    </div>
                    {tool.description && (
                      <p className="text-sm text-gray-300">{tool.description}</p>
                    )}
                    {tool.usage && (
                      <p className="text-xs text-gray-400 mt-1">Usage: {tool.usage}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {mcpTools && Object.keys(mcpTools).length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-3 text-white">MCP Tools by Server</h3>
                <div className="space-y-3">
                  {Object.entries(mcpTools).map(([server, serverTools]) => {
                    const toolsForServer = serverTools as string[];
                    return (
                    <div
                      key={server}
                      className="rounded-lg border border-gray-700 bg-black/30 px-4 py-3"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-white">{server}</span>
                        <span className="text-xs text-gray-400">
                          {toolsForServer.length} tool{toolsForServer.length === 1 ? '' : 's'}
                        </span>
                      </div>
                      {toolsForServer.length > 0 ? (
                        <div className="flex flex-wrap gap-2 mt-1">
                          {toolsForServer.map((t) => (
                            <span
                              key={t}
                              className="text-xs px-2 py-0.5 rounded-full bg-gray-700 text-gray-100 border border-gray-600"
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="text-xs text-gray-500">No tools reported.</p>
                      )}
                    </div>
                  );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
