import asyncio
from typing import Annotated, Any, Optional

from agents import Agent, Runner, function_tool
import logging
from openai.types.responses import ResponseFunctionCallArgumentsDeltaEvent


@function_tool
def write_file(filename: Annotated[str, "Name of the file"], content: str) -> str:
    """Write content to a file."""
    return f"File {filename} written successfully"


@function_tool
def create_config(
    project_name: Annotated[str, "Project name"],
    version: Annotated[str, "Project version"],
    dependencies: Annotated[Optional[list[str]], "Dependencies (list of packages)"],
) -> str:
    """Generate a project configuration file."""
    return f"Config for {project_name} v{version} created"


async def main():
    """
    Demonstrates real-time streaming of function call arguments.

    Function arguments are streamed incrementally as they are generated,
    providing immediate feedback during parameter generation.
    """
    agent = Agent(
        name="CodeGenerator",
        instructions="You are a helpful coding assistant. Use the provided tools to create files and configurations.",
        tools=[write_file, create_config],
    )

    logging.getLogger(__name__).info("🚀 Function Call Arguments Streaming Demo")

    result = Runner.run_streamed(
        agent,
        input="Create a Python web project called 'my-app' with FastAPI. Version 1.0.0, dependencies: fastapi, uvicorn",
    )

    # Track function calls for detailed output
    function_calls: dict[Any, dict[str, Any]] = {}  # call_id -> {name, arguments}
    current_active_call_id = None

    async for event in result.stream_events():
        if event.type == "raw_response_event":
            # Function call started
            if event.data.type == "response.output_item.added":
                if getattr(event.data.item, "type", None) == "function_call":
                    function_name = getattr(event.data.item, "name", "unknown")
                    call_id = getattr(event.data.item, "call_id", "unknown")

                    function_calls[call_id] = {"name": function_name, "arguments": ""}
                    current_active_call_id = call_id
                    logging.getLogger(__name__).info(
                        "\n📞 Function call streaming started: %s()", function_name
                    )
                    logging.getLogger(__name__).info("📝 Arguments building...")

            # Real-time argument streaming
            elif isinstance(event.data, ResponseFunctionCallArgumentsDeltaEvent):
                    if current_active_call_id and current_active_call_id in function_calls:
                        function_calls[current_active_call_id]["arguments"] += event.data.delta
                        logging.getLogger(__name__).info(event.data.delta)

            # Function call completed
            elif event.data.type == "response.output_item.done":
                if hasattr(event.data.item, "call_id"):
                    call_id = getattr(event.data.item, "call_id", "unknown")
                        if call_id in function_calls:
                            function_info = function_calls[call_id]
                            logging.getLogger(__name__).info(
                                "\n✅ Function call streaming completed: %s", function_info["name"]
                            )
                            logging.getLogger(__name__).info("")
                        if current_active_call_id == call_id:
                            current_active_call_id = None

    logging.getLogger(__name__).info("Summary of all function calls:")
    for call_id, info in function_calls.items():
        logging.getLogger(__name__).info("  - #%s: %s(%s)", call_id, info["name"], info["arguments"])

    logging.getLogger(__name__).info("\nResult: %s", result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
