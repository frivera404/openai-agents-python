# Main Agent Controller Example

This example demonstrates how to run a primary agent controller as both a command line tool and an HTTP service. The implementation is based on the standalone `gpt-cli-starter` project and re-packaged so that it works inside the OpenAI Agents examples tree.

## Features

- Session based CLI with optional streaming output.
- Command line JSON schema validation helpers.
- Example tool calling with a built-in `ping` tool.
- FastAPI server with synchronous, streaming, and schema validated JSON endpoints.
- Simple Dockerfile for containerised deployment.

## Setup

Install the optional dependencies for this example:

```bash
uv pip install -r examples/main_agent_controller/requirements.txt
```

Create a `.env` file (or export the variables directly) with your OpenAI credentials:

```bash
cp .env.example .env
# Edit the file and fill in OPENAI_API_KEY, optionally OPENAI_BASE_URL and APP_API_KEY
```

### CLI usage

```bash
uv run python examples/main_agent_controller/gpt_cli.py --session main -s "You are my Main Orchestrator Agent." "Draft a launch plan."
```

### API usage

```bash
uv run uvicorn examples.main_agent_controller.server:app --host 0.0.0.0 --port 8080
```

Refer to the in-file docstrings for more details about the available flags and routes.
