import argparse
import asyncio
import logging

from agents import (
    Agent,
    HostedMCPTool,
    MCPToolApprovalFunctionResult,
    MCPToolApprovalRequest,
    Runner,
)

logger = logging.getLogger(__name__)

"""This example demonstrates how to use the hosted MCP support in the OpenAI Responses API, with
approval callbacks."""


def approval_callback(request: MCPToolApprovalRequest) -> MCPToolApprovalFunctionResult:
    # Keep the interactive prompt as `input()` so callers can approve interactively.
    answer = input(f"Approve running the tool `{request.data.name}`? (y/n) ")
    result: MCPToolApprovalFunctionResult = {"approve": answer == "y"}
    if not result["approve"]:
        result["reason"] = "User denied"
        logger.info("User denied approval for tool %s", request.data.name)
    else:
        logger.info("User approved tool %s", request.data.name)
    return result


async def main(verbose: bool, stream: bool):
    agent = Agent(
        name="Assistant",
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "gitmcp",
                    "server_url": "https://gitmcp.io/openai/codex",
                    "require_approval": "always",
                },
                on_approval_request=approval_callback,
            )
        ],
    )

    if stream:
        result = Runner.run_streamed(agent, "Which language is this repo written in?")
        async for event in result.stream_events():
            if event.type == "run_item_stream_event":
                logger.debug("Got event of type %s", event.item.__class__.__name__)
        logger.info("Done streaming; final result: %s", result.final_output)
        # Expose a consistent `res` variable for downstream verbose inspection.
        res = result
    else:
        res = await Runner.run(
            agent,
            "Which language is this repo written in? Your MCP server should know what the repo is.",
        )
        logger.info("Run final output: %s", res.final_output)

    if verbose:
        for item in res.new_items:
            logger.debug("New item: %s", item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--stream", action="store_true", default=False)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(args.verbose, args.stream))
