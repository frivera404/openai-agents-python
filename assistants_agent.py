#!/usr/bin/env python
"""
AssistantsAgent: thin wrapper around the OpenAI Assistants API.
python
Usage examples:

  # 0) Export your key
  #   setx OPENAI_API_KEY "sk-..."   (Windows)
  #   export OPENAI_API_KEY="sk-..." (Linux/macOS)

  # 1) Create an assistant
  python assistants_agent.py create-assistant \
    --name "Dev Orchestrator" \
    --model "gpt-4.1" \
    --instructions "You are a dev assistant that helps manage assistants/threads."

  # 2) List assistants
  python assistants_agent.py list-assistants

  # 3) Chat (uses existing assistant, creates thread+run under the hood)
  python assistants_agent.py chat \
    --assistant-id asst_123... \
    --message "Test message from CLI"

  # 4) Upload a file for assistants
  python assistants_agent.py upload-file --path ./knowledge.txt

  # 5) Create a vector store and attach files
  python assistants_agent.py create-vector-store \
    --name "kb-store" \
    --file-id file_123... \
    --file-id file_456...
"""

import argparse
import os
import time
from typing import Any, Optional

from openai import OpenAI


class AssistantsAgent:
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

        # assistants=v2 header is required
        self.client = OpenAI(
            api_key=api_key,
            default_headers={"OpenAI-Beta": "assistants=v2"},
        )

    # ---------------------
    # Models
    # ---------------------

    def list_models(self, search: Optional[str] = None):
        """List models, optionally filtered by a substring in the model id.

        Example: list_models("gpt-4.1")
        """
        models = self.client.models.list()
        if not search:
            return models

        search_lower = search.lower()
        filtered = [m for m in models.data if search_lower in m.id.lower()]

        # Wrap filtered list back into a simple namespace-like object
        class _Result:
            def __init__(self, data):
                self.data = data

        return _Result(filtered)

    # ---------------------
    # Assistants
    # ---------------------

    def create_assistant(
        self,
        name: str,
        model: str,
        instructions: str,
        tools: Optional[list] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        tools = tools or []
        payload: dict[str, Any] = {
            "name": name,
            "model": model,
            "instructions": instructions,
            "tools": tools,
        }
        if metadata:
            payload["metadata"] = metadata
        return self.client.beta.assistants.create(**payload)

    def update_assistant(self, assistant_id: str, **fields: Any):
        """Update assistant fields such as name, instructions, tools, model, metadata."""
        return self.client.beta.assistants.update(assistant_id, **fields)

    def retrieve_assistant(self, assistant_id: str):
        return self.client.beta.assistants.retrieve(assistant_id)

    def list_assistants(self, limit: int = 20):
        return self.client.beta.assistants.list(limit=limit)

    def delete_assistant(self, assistant_id: str):
        return self.client.beta.assistants.delete(assistant_id)

    # ---------------------
    # Threads
    # ---------------------

    def create_thread(self, messages: Optional[list] = None, metadata: Optional[dict] = None):
        payload: dict[str, Any] = {}
        if messages:
            payload["messages"] = messages
        if metadata:
            payload["metadata"] = metadata
        return self.client.beta.threads.create(**payload)

    def retrieve_thread(self, thread_id: str):
        return self.client.beta.threads.retrieve(thread_id)

    def update_thread_metadata(self, thread_id: str, metadata: dict):
        return self.client.beta.threads.update(thread_id, metadata=metadata)

    def delete_thread(self, thread_id: str):
        return self.client.beta.threads.delete(thread_id)

    def list_threads(self, limit: int = 20):
        # Threads listing is not yet generally available in all SDKs; keep for completeness.
        return self.client.beta.threads.list(limit=limit)

    # ---------------------
    # Messages
    # ---------------------

    def create_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        file_ids: Optional[list[str]] = None,
    ):
        """Create a message on a thread.

        The current Assistants v2 API does not accept a top-level "file_ids" argument
        on messages.create; files are attached via the "attachments" field instead.
        For simple text messages (the common case here), we only send role+content.
        """
        kwargs: dict[str, Any] = {
            "thread_id": thread_id,
            "role": role,
            "content": content,
        }

        # If file_ids are provided, map them into attachments for forward compatibility.
        if file_ids:
            kwargs["attachments"] = [{"file_id": fid} for fid in file_ids]

        return self.client.beta.threads.messages.create(**kwargs)

    def retrieve_message(self, thread_id: str, message_id: str):
        return self.client.beta.threads.messages.retrieve(
            thread_id=thread_id,
            message_id=message_id,
        )

    def list_messages(self, thread_id: str, limit: int = 20, order: str = "desc"):
        return self.client.beta.threads.messages.list(
            thread_id=thread_id,
            limit=limit,
            order=order,
        )

    # ---------------------
    # Runs
    # ---------------------

    def create_run(
        self,
        thread_id: str,
        assistant_id: str,
        instructions: Optional[str] = None,
        additional_tools: Optional[list] = None,
        tool_resources: Optional[dict] = None,
    ):
        payload: dict[str, Any] = {
            "thread_id": thread_id,
            "assistant_id": assistant_id,
        }
        if instructions:
            payload["instructions"] = instructions
        if additional_tools:
            payload["tools"] = additional_tools
        if tool_resources:
            payload["tool_resources"] = tool_resources
        return self.client.beta.threads.runs.create(**payload)

    def retrieve_run(self, thread_id: str, run_id: str):
        return self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )

    def list_runs(self, thread_id: str, limit: int = 20):
        return self.client.beta.threads.runs.list(
            thread_id=thread_id,
            limit=limit,
        )

    def cancel_run(self, thread_id: str, run_id: str):
        return self.client.beta.threads.runs.cancel(
            thread_id=thread_id,
            run_id=run_id,
        )

    def submit_tool_outputs(self, thread_id: str, run_id: str, tool_outputs: list[dict[str, Any]]):
        return self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
        )

    def submit_message(self, thread_id: str, run_id: str, role: str, content: str):
        # Some variants name this differently.
        # Use threads.messages.create + runs.submit_tool_outputs/message style as needed.
        return self.client.beta.threads.runs.submit_message(
            thread_id=thread_id,
            run_id=run_id,
            role=role,
            content=content,
        )

    def wait_for_run_completion(
        self,
        thread_id: str,
        run_id: str,
        poll_interval: float = 1.0,
        max_wait_seconds: int = 120,
    ):
        elapsed = 0.0
        while True:
            run = self.retrieve_run(thread_id, run_id)
            status = run.status
            if status in ("completed", "failed", "cancelled", "expired"):
                return run
            time.sleep(poll_interval)
            elapsed += poll_interval
            if elapsed >= max_wait_seconds:
                return run

    # ---------------------
    # Files
    # ---------------------

    def upload_file(self, path: str, purpose: str = "assistants"):
        with open(path, "rb") as f:
            file_obj = self.client.files.create(file=f, purpose=purpose)
        return file_obj

    def list_files(self, purpose: Optional[str] = None):
        kwargs: dict[str, Any] = {}
        if purpose:
            kwargs["purpose"] = purpose
        return self.client.files.list(**kwargs)

    def retrieve_file(self, file_id: str):
        return self.client.files.retrieve(file_id)

    def delete_file(self, file_id: str):
        return self.client.files.delete(file_id)

    # ---------------------
    # Vector stores
    # ---------------------

    def create_vector_store(
        self,
        name: str,
        file_ids: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        file_ids = file_ids or []
        payload: dict[str, Any] = {"name": name, "file_ids": file_ids}
        if metadata:
            payload["metadata"] = metadata
        return self.client.vector_stores.create(**payload)

    def update_vector_store(self, vector_store_id: str, **fields: Any):
        return self.client.vector_stores.update(vector_store_id, **fields)

    def list_vector_stores(self, limit: int = 20):
        return self.client.vector_stores.list(limit=limit)

    def retrieve_vector_store(self, vector_store_id: str):
        return self.client.vector_stores.retrieve(vector_store_id)

    def delete_vector_store(self, vector_store_id: str):
        return self.client.vector_stores.delete(vector_store_id)

    # ---------------------
    # Vector store files
    # ---------------------

    def add_file_to_vector_store(self, vector_store_id: str, file_id: str):
        return self.client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_id,
        )

    def list_vector_store_files(self, vector_store_id: str, limit: int = 20):
        return self.client.vector_stores.files.list(
            vector_store_id=vector_store_id,
            limit=limit,
        )

    def retrieve_vector_store_file(self, vector_store_id: str, file_id: str):
        return self.client.vector_stores.files.retrieve(
            vector_store_id=vector_store_id,
            file_id=file_id,
        )

    def delete_vector_store_file(self, vector_store_id: str, file_id: str):
        return self.client.vector_stores.files.delete(
            vector_store_id=vector_store_id,
            file_id=file_id,
        )

    # ---------------------
    # High-level "chat" op
    # ---------------------

    def chat_once(
        self,
        assistant_id: str,
        user_message: str,
        thread_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Single-turn chat helper.

        Creates a thread (if needed), sends the user message, runs the
        assistant, and returns the assistant reply.
        """
        if thread_id is None:
            thread = self.create_thread()
            thread_id = thread.id

        self.create_message(
            thread_id=thread_id,
            role="user",
            content=user_message,
        )

        run = self.create_run(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        run = self.wait_for_run_completion(thread_id, run.id)
        if run.status != "completed":
            raise RuntimeError(f"Run not completed. Status: {run.status}")

        messages = self.list_messages(thread_id=thread_id, limit=1, order="desc")
        if not messages.data:
            return {"thread_id": thread_id, "assistant_reply": None}

        latest = messages.data[0]
        text_chunks: list[str] = []
        for c in latest.content:
            if c.type == "text":
                text_chunks.append(c.text.value)
        reply_text = "\n".join(text_chunks) if text_chunks else None

        return {"thread_id": thread_id, "assistant_reply": reply_text}


# -------------------------
# CLI helpers
# -------------------------


def cmd_create_assistant(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    assistant = agent.create_assistant(
        name=args.name,
        model=args.model,
        instructions=args.instructions,
    )
    print("ASSISTANT CREATED")
    print(f"id:   {assistant.id}")
    print(f"name: {assistant.name}")
    print(f"model:{assistant.model}")


def cmd_list_assistants(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    res = agent.list_assistants(limit=args.limit)
    for a in res.data:
        print(f"{a.id} | {a.name} | {a.model}")


def cmd_chat(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    result = agent.chat_once(
        assistant_id=args.assistant_id,
        user_message=args.message,
        thread_id=args.thread_id,
    )
    print("THREAD:", result["thread_id"])
    print("ASSISTANT:\n", result["assistant_reply"] or "<no reply>")


def cmd_upload_file(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    file_obj = agent.upload_file(args.path, purpose=args.purpose)
    print("FILE UPLOADED")
    print(f"id:      {file_obj.id}")
    print(f"purpose: {file_obj.purpose}")
    print(f"filename:{getattr(file_obj, 'filename', None)}")


def cmd_list_files(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    res = agent.list_files(purpose=args.purpose)
    for f in res.data:
        print(f"{f.id} | {f.purpose} | {getattr(f, 'filename', None)}")


def cmd_create_vector_store(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    vs = agent.create_vector_store(
        name=args.name,
        file_ids=args.file_id or [],
    )
    print("VECTOR STORE CREATED")
    print(f"id:   {vs.id}")
    print(f"name: {vs.name}")


def cmd_list_vector_stores(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    res = agent.list_vector_stores(limit=args.limit)
    for vs in res.data:
        print(f"{vs.id} | {vs.name}")


def cmd_add_file_to_vector_store(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    res = agent.add_file_to_vector_store(
        vector_store_id=args.vector_store_id,
        file_id=args.file_id,
    )
    print("VECTOR STORE FILE ATTACHED")
    print(f"id: {res.id} | vs: {res.vector_store_id} | file: {res.file_id}")


def cmd_list_models(agent: AssistantsAgent, args: argparse.Namespace) -> None:
    res = agent.list_models(search=args.search)
    for m in res.data:
        # Print id and optional description/capabilities if present
        desc = getattr(m, "description", "") or ""
        print(f"{m.id} | {desc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AssistantsAgent CLI – wraps OpenAI Assistants API commands.",
    )
    # Do not require a subcommand at the argparse level so that running
    # the script with no arguments can show the help message cleanly.
    sub = parser.add_subparsers(dest="command")

    # create-assistant
    p = sub.add_parser("create-assistant", help="Create a new assistant")
    p.add_argument("--name", required=True)
    p.add_argument("--model", required=True, help="e.g. gpt-4.1, gpt-4o, gpt-4.1-mini")
    p.add_argument("--instructions", required=True)
    p.set_defaults(func=cmd_create_assistant)

    # list-assistants
    p = sub.add_parser("list-assistants", help="List assistants")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_list_assistants)

    # chat
    p = sub.add_parser("chat", help="Single-turn chat using assistant+thread+run")
    p.add_argument("--assistant-id", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--thread-id", required=False, help="Existing thread; if omitted, creates one")
    p.set_defaults(func=cmd_chat)

    # upload-file
    p = sub.add_parser("upload-file", help="Upload file for assistants")
    p.add_argument("--path", required=True)
    p.add_argument("--purpose", default="assistants")
    p.set_defaults(func=cmd_upload_file)

    # list-files
    p = sub.add_parser("list-files", help="List files")
    p.add_argument("--purpose", required=False)
    p.set_defaults(func=cmd_list_files)

    # create-vector-store
    p = sub.add_parser("create-vector-store", help="Create vector store and attach files")
    p.add_argument("--name", required=True)
    p.add_argument(
        "--file-id",
        action="append",
        help="File ID(s) to attach; use multiple --file-id flags for more",
    )
    p.set_defaults(func=cmd_create_vector_store)

    # list-vector-stores
    p = sub.add_parser("list-vector-stores", help="List vector stores")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_list_vector_stores)

    # add-file-to-vector-store
    p = sub.add_parser("add-file-to-vector-store", help="Attach an existing file to a vector store")
    p.add_argument("--vector-store-id", required=True)
    p.add_argument("--file-id", required=True)
    p.set_defaults(func=cmd_add_file_to_vector_store)

    # list-models (search for models)
    p = sub.add_parser("list-models", help="List models, optionally filtered by substring")
    p.add_argument("--search", required=False, help="Substring to filter model ids, e.g. gpt-4.1")
    p.set_defaults(func=cmd_list_models)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    # If no subcommand was provided, print help and exit gracefully.
    if not getattr(args, "command", None):
        parser.print_help()
        return

    agent = AssistantsAgent()
    args.func(agent, args)


if __name__ == "__main__":
    main()
