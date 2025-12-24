from mcp.server import Server  # your framework
import os
import json

app = Server(name="mcp-openai")

@app.tool("get_status")
def get_status():
    return {"ok": True}

@app.tool("openai_chat")
def openai_chat(prompt: str):
    key = os.environ.get("OPENAI_API_KEY")
    if not key: return {"error": "missing OPENAI_API_KEY"}
    # call OpenAI here (omitted)
    return {"content": f"echo: {prompt}"}

@app.tool("list_files")
def list_files(path: str = "."):
    return {"files": sorted(os.listdir(path))}

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", "8080")))