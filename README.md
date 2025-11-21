
<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/drive/1ne2T75hjtSb8NIhSdnqp0S3icBVGgy6l

## Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Copy `.env.local.example` to `.env.local` and populate `OPENAI_API_KEY` (and optionally `ASSISTANT_ID`/`VECTOR_STORE_ID`).
3. Run the app:
   `npm run dev`

### Backend configuration

The backend server that powers `/api/agent/launch` runs `openai_assistant_runner.py`, which proxies every agent request through the OpenAI Assistants API. Before starting the backend you must populate the following variables in `.env` or your shell:

- `OPENAI_API_KEY` – your OpenAI API key with access to the Assistants & Vector Stores features.
- `ASSISTANT_ID` – the assistant ID you created in the OpenAI dashboard (defaults to the value stored in `openai_assistant_config.json`).
- `VECTOR_STORE_ID` – optional vector store if you rely on knowledge retrieval, otherwise the runner falls back to the configuration file.

You can keep the JSON defaults in `openai_assistant_config.json` but override them via environment variables when launching the server.

### Environment hints for agent launches

Each `/api/agent/launch` request streams the prompt, system overrides, and per-agent instructions through the runner script. Use the UI or your integration to pass the following request fields:

- `agentId` – one of the preconfigured agent IDs listed in the UI (`customer-service`, `financial-research`, `senior-developer`, etc.).
- `prompt` – the user message that will be forwarded to the assistant.
- `model` / `temperature` / `systemInstruction` – optional tuning parameters that are forwarded as environment variables to `openai_assistant_runner.py` so that the assistant run honors them.

Because the backend communicates with OpenAI's beta Threads API (which only supports `user` and `assistant` roles), any system instruction is emitted as an assistant message with a `"[System instructions]"` prefix before the user prompt.

Keep in mind the backend expects valid JSON. If you build requests manually (for example with `curl`), wrap keys and strings in double quotes and include the `Content-Type: application/json` header:

```bash
curl -X POST http://localhost:3001/api/agent/launch \
   -H "Content-Type: application/json" \
   -d '{"agentId":"customer-service","prompt":"Summarize late delivery issues.","model":"gpt-4o","temperature":0.7}'
```

Sending malformed JSON (like missing double quotes or relying on single quotes alone) will trigger the server's JSON parser and return an `entity.parse.failed` error so you can adjust the payload before retrying.

With these values in place, `npm run dev` starts both the Vite client and the Express server that now launches the OpenAI Assistants API for every agent call.
