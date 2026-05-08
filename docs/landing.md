# Operate Your Agents Command Center

Welcome to the mission-control view of the OpenAI Agents SDK. This landing page explains how Agents, MCP Servers, and the Agent Command Center work together so you can build, observe, and scale reliable AI operations.

## Why it matters

Teams rarely succeed with ad-hoc agent scripts. You need a consistent operational layer that:

- Connects specialized agents with the right instructions and guardrails.
- Supplies a catalog of secure Model Context Protocol (MCP) servers so agents can reach code, data, and infrastructure safely.
- Provides a command center that surfaces state, observability, and controls for every run.

The Agents SDK ships all three pieces out of the box.

## Agents: skilled teammates on demand

Agents are LLM personas equipped with goals, instructions, and tools. Combine multiple agents to cover the full development loop:

- **Builder agents** craft code, migrations, or test scenarios.
- **Reviewer agents** run targeted checks or enforce quality gates.
- **Ops agents** keep workflows healthy by rolling back, escalating, or tracing errors.

Learn more in `docs/agents.md` and `docs/multi_agent.md`.

## MCP Servers: secure tool access

MCP servers wrap external resources -- source code, ticketing systems, analytics stores -- behind a standard protocol. Key advantages:

- **Least-privilege design.** Servers expose just the commands an agent needs.
- **Streamable IO.** Large files or logs stream incrementally so agents stay responsive.
- **Deployment flexibility.** Run MCP servers locally, in containers, or as remote services.

See `docs/mcp.md` plus the examples under `examples/tools/` for starting points.

## Agent Command Center

Combine Agents and MCP servers with the built-in tracing UI to get a full command center:

- **Live telemetry.** Every run emits trace events that you can inspect via `visualization.md` to debug loops or tool calls.
- **Interventions.** Use `Runner` APIs or REPL tooling to pause, resume, or hand off work.
- **Compliance.** Guardrails, usage accounting, and reproducible traces make audits straightforward.

The command center is also scriptable: the tracing hooks under `docs/tracing/` let you forward events into your existing observability stack.

## Quick start checklist

1. **Create an agent.** Follow `quickstart.md` or `examples/` to define instructions and attach tools.
2. **Attach MCP servers.** Register filesystem, shell, or custom servers and scope credentials per agent.
3. **Instrument tracing.** Export `OPENAI_API_KEY`, call `trace(...)`, and bookmark the trace URL printed in examples like `examples/senior_developer_agent.py`.
4. **Launch a control panel.** Run agents via `Runner`, the CLI, or the REPL so you can intervene mid-run.
5. **Iterate with confidence.** Use `make format`, `make lint`, `make mypy`, and `make tests` before deploying changes.

## Where to go next

- [Agents overview](agents.md)
- [Running agents in production](running_agents.md)
- [MCP integration guide](mcp.md)
- [Visualization & tracing](visualization.md)
- [Tooling reference](tools.md)

Use this landing page as the mission briefing for teammates who need to orient themselves quickly before diving into the deeper docs.
