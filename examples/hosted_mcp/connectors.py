import argparse
import asyncio
import json
import os
import logging
from datetime import datetime

from agents import Agent, HostedMCPTool, Runner

logger = logging.getLogger(__name__)


async def main(verbose: bool, stream: bool):
    # 1. Visit https://developers.google.com/oauthplayground/
    # 2. Input https://www.googleapis.com/auth/calendar.events as the required scope
    # 3. Grab the access token starting with "ya29."
    authorization = os.environ["GOOGLE_CALENDAR_AUTHORIZATION"]
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant that can help a user with their calendar.",
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "google_calendar",
                    # see https://platform.openai.com/docs/guides/tools-connectors-mcp#connectors
                    "connector_id": "connector_googlecalendar",
                    "authorization": authorization,
                    "require_approval": "never",
                }
            )
        ],
    )

    today = datetime.now().strftime("%Y-%m-%d")
    if stream:
        result = Runner.run_streamed(agent, f"What is my schedule for {today}?")
        async for event in result.stream_events():
                if event.type == "raw_response_event":
                    if event.data.type.startswith("response.output_item"):
                        logger.debug(json.dumps(event.data.to_dict(), indent=2))
                    if event.data.type.startswith("response.mcp"):
                        logger.debug(json.dumps(event.data.to_dict(), indent=2))
                    if event.data.type == "response.output_text.delta":
                        # Keep streaming deltas printed to stdout for interactive UX.
                        print(event.data.delta, end="", flush=True)
            print()
    else:
        res = await Runner.run(agent, f"What is my schedule for {today}?")
        logger.info(res.final_output)

    if verbose:
        for item in res.new_items:
            logger.info(item)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", default=False)
    parser.add_argument("--stream", action="store_true", default=False)
    args = parser.parse_args()
    import logging as _logging
    _logging.basicConfig(level=_logging.INFO)

    asyncio.run(main(args.verbose, args.stream))
