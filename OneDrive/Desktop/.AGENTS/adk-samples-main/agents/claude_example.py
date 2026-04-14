"""Small example showing how to use `ClaudeConnector`.

Run this from the `agents` folder or update PYTHONPATH accordingly:

    python claude_example.py

Ensure `CLAUDE_API_KEY` is set in your environment before running.
"""

from claude_connector import ClaudeConnector


def main():
    client = ClaudeConnector()
    prompt = "Write a short friendly greeting and one-line usage instruction."
    resp = client.generate(prompt, max_tokens=120)
    print(resp)


if __name__ == "__main__":
    main()
