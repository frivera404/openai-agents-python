const { Server } = require('mcp');

const app = new Server({ name: "mcp-openai" });

app.tool("get_status", () => {
  return { ok: true };
});

app.tool("openai_chat", async (prompt) => {
  const key = process.env.OPENAI_API_KEY;
  if (!key) {
    return { error: "missing OPENAI_API_KEY" };
  }
  // call OpenAI here (omitted for stub)
  return { content: `echo: ${prompt}` };
});

app.tool("list_files", (path = ".") => {
  const fs = require('fs');
  try {
    const files = fs.readdirSync(path);
    return { files: files.sort() };
  } catch (e) {
    return { error: e.message };
  }
});

if (require.main === module) {
  const port = process.env.PORT || 8080;
  app.listen(port, () => {
    console.log(`Server running on port ${port}`);
  });
}

module.exports = app;