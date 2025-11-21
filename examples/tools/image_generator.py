import asyncio
import base64
import os
import subprocess
import sys
import tempfile
import logging

from agents import Agent, ImageGenerationTool, Runner, trace

logger = logging.getLogger(__name__)


def open_file(path: str) -> None:
    if sys.platform.startswith("darwin"):
        subprocess.run(["open", path], check=False)  # macOS
    elif os.name == "nt":  # Windows
        os.startfile(path)  # type: ignore
    elif os.name == "posix":
        subprocess.run(["xdg-open", path], check=False)  # Linux/Unix
    else:
        logger.warning("Don't know how to open files on this platform: %s", sys.platform)


async def main():
    agent = Agent(
        name="Image generator",
        instructions="You are a helpful agent.",
        tools=[
            ImageGenerationTool(
                tool_config={"type": "image_generation", "quality": "low"},
            )
        ],
    )

    with trace("Image generation example"):
        logger.info("Generating image, this may take a while...")
        result = await Runner.run(
            agent, "Create an image of a frog eating a pizza, comic book style."
        )
        logger.info("%s", result.final_output)
        for item in result.new_items:
            if (
                item.type == "tool_call_item"
                and item.raw_item.type == "image_generation_call"
                and (img_result := item.raw_item.result)
            ):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(base64.b64decode(img_result))
                    temp_path = tmp.name

                # Open the image
                open_file(temp_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
