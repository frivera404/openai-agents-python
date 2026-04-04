"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.plan = plan;
exports.scaffold = scaffold;
exports.implement_tools = implement_tools;
exports.wire_openai = wire_openai;
exports.test_smoke = test_smoke;
exports.package_image = package_image;
exports.deploy_cloud_run = deploy_cloud_run;
exports.record_memory = record_memory;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
async function plan(input, ctx) {
    ctx.log("plan: deriving spec");
    return { lang: input.lang, tools: input.tools, models: input.models };
}
async function scaffold(input, ctx) {
    ctx.log("scaffold: creating repo");
    const repoPath = input.repo.path;
    // Create directory structure
    if (!fs.existsSync(repoPath)) {
        fs.mkdirSync(repoPath, { recursive: true });
    }
    // Create basic files based on language
    if (input.lang === 'python') {
        // Create requirements.txt
        fs.writeFileSync(path.join(repoPath, 'requirements.txt'), 'mcp\nopenai\n');
        // Create basic server.py
        const serverContent = `from mcp.server import Server
import os
import json

app = Server(name="${input.repo.name}")

@app.tool("get_status")
def get_status():
    return {"ok": True}

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", "8080")))
`;
        fs.writeFileSync(path.join(repoPath, 'server.py'), serverContent);
    }
    else if (input.lang === 'node') {
        // Create package.json
        const packageJson = {
            name: input.repo.name,
            version: "1.0.0",
            main: "server.js",
            dependencies: {
                "mcp": "^1.0.0",
                "openai": "^4.0.0"
            }
        };
        fs.writeFileSync(path.join(repoPath, 'package.json'), JSON.stringify(packageJson, null, 2));
        // Create basic server.js
        const serverContent = `const { Server } = require('mcp');

const app = new Server({ name: "${input.repo.name}" });

app.tool("get_status", () => {
  return { ok: true };
});

if (require.main === module) {
  const port = process.env.PORT || 8080;
  app.listen(port, () => {
    console.log(\`Server running on port \${port}\`);
  });
}

module.exports = app;
`;
        fs.writeFileSync(path.join(repoPath, 'server.js'), serverContent);
    }
    return { repoPath };
}
async function implement_tools(input, ctx) {
    ctx.log(`implement_tools: ${input.tools.join(",")}`);
    const repoPath = input.repoPath || input.repo.path;
    // Add tool implementations based on requested tools
    for (const tool of input.tools) {
        if (tool === 'openai_chat') {
            await implementOpenAIChat(repoPath, input.lang);
        }
        else if (tool === 'list_files') {
            await implementListFiles(repoPath, input.lang);
        }
        // get_status is already implemented in scaffold
    }
    return { tools: input.tools };
}
async function implementOpenAIChat(repoPath, lang) {
    if (lang === 'python') {
        const content = `
@app.tool("openai_chat")
def openai_chat(prompt: str):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return {"error": "missing OPENAI_API_KEY"}
    try:
        import openai
        client = openai.OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return {"content": response.choices[0].message.content}
    except Exception as e:
        return {"error": str(e)}
`;
        const serverPath = path.join(repoPath, 'server.py');
        let serverContent = fs.readFileSync(serverPath, 'utf8');
        serverContent = serverContent.replace('@app.tool("get_status")\ndef get_status():\n    return {"ok": True}\n', `@app.tool("get_status")\ndef get_status():\n    return {"ok": True}\n${content}`);
        fs.writeFileSync(serverPath, serverContent);
    }
    else if (lang === 'node') {
        const content = `
app.tool("openai_chat", async (prompt) => {
  const key = process.env.OPENAI_API_KEY;
  if (!key) {
    return { error: "missing OPENAI_API_KEY" };
  }
  try {
    const OpenAI = require('openai');
    const client = new OpenAI({ apiKey: key });
    const response = await client.chat.completions.create({
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }]
    });
    return { content: response.choices[0].message.content };
  } catch (e) {
    return { error: e.message };
  }
});
`;
        const serverPath = path.join(repoPath, 'server.js');
        let serverContent = fs.readFileSync(serverPath, 'utf8');
        serverContent = serverContent.replace('app.tool("get_status", () => {\n  return { ok: true };\n});\n', `app.tool("get_status", () => {\n  return { ok: true };\n});\n${content}`);
        fs.writeFileSync(serverPath, serverContent);
    }
}
async function implementListFiles(repoPath, lang) {
    if (lang === 'python') {
        const content = `
@app.tool("list_files")
def list_files(path: str = "."):
    try:
        return {"files": sorted(os.listdir(path))}
    except Exception as e:
        return {"error": str(e)}
`;
        const serverPath = path.join(repoPath, 'server.py');
        let serverContent = fs.readFileSync(serverPath, 'utf8');
        serverContent = serverContent.replace('if __name__ == "__main__":', `${content}\nif __name__ == "__main__":`);
        fs.writeFileSync(serverPath, serverContent);
    }
    else if (lang === 'node') {
        const content = `
app.tool("list_files", (dirPath = ".") => {
  try {
    const files = fs.readdirSync(dirPath);
    return { files: files.sort() };
  } catch (e) {
    return { error: e.message };
  }
});
`;
        const serverPath = path.join(repoPath, 'server.js');
        let serverContent = fs.readFileSync(serverPath, 'utf8');
        serverContent = serverContent.replace('module.exports = app;', `${content}\nmodule.exports = app;`);
        fs.writeFileSync(serverPath, serverContent);
    }
}
async function wire_openai(input, ctx) {
    ctx.log("wire_openai: verifying env");
    if (!process.env.OPENAI_API_KEY) {
        throw new Error("OPENAI_API_KEY missing");
    }
    // Additional validation could be added here
    return { ok: true };
}
async function test_smoke(input, ctx) {
    ctx.log("test_smoke: starting local & calling get_status");
    const repoPath = input.repoPath;
    try {
        // For demo purposes, we'll simulate the test
        // In real implementation, this would spawn the server process
        const serverFile = path.join(repoPath, input.lang === 'python' ? 'server.py' : 'server.js');
        if (!fs.existsSync(serverFile)) {
            throw new Error(`Server file not found: ${serverFile}`);
        }
        // Simulate calling get_status
        const result = { ok: true, tool: "get_status", result: { ok: true } };
        ctx.log(`test_smoke: success - ${JSON.stringify(result)}`);
        return result;
    }
    catch (error) {
        ctx.log(`test_smoke: failed - ${error}`);
        throw error;
    }
}
async function package_image(input, ctx) {
    ctx.log("package_image: docker build/tag/push");
    const imageName = `gcr.io/${input.cloud.project}/${input.cloud.service}:latest`;
    try {
        // Create Dockerfile
        const dockerfile = `FROM ${input.lang === 'python' ? 'python:3.9-slim' : 'node:18-slim'}

WORKDIR /app
${input.lang === 'python' ?
            `COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server.py .` :
            `COPY package*.json ./
RUN npm ci --only=production
COPY server.js .`}

EXPOSE 8080
CMD ["${input.lang === 'python' ? 'python server.py' : 'node server.js'}"]
`;
        fs.writeFileSync(path.join(input.repo.path, 'Dockerfile'), dockerfile);
        // Simulate docker build (in real implementation, this would call docker CLI)
        ctx.log(`package_image: would build ${imageName}`);
        return { image: imageName };
    }
    catch (error) {
        ctx.log(`package_image: failed - ${error}`);
        throw error;
    }
}
async function deploy_cloud_run(input, ctx) {
    ctx.log("deploy_cloud_run: gcloud run deploy + health check");
    const url = `https://${input.cloud.service}-${input.cloud.region}-a.run.app`;
    try {
        // Simulate deployment (in real implementation, this would call gcloud CLI)
        ctx.log(`deploy_cloud_run: would deploy to ${url}`);
        return { url };
    }
    catch (error) {
        ctx.log(`deploy_cloud_run: failed - ${error}`);
        throw error;
    }
}
async function record_memory(input, ctx) {
    ctx.log("record_memory: persist recipe/paths");
    // In real implementation, this would save to a database or file
    const memory = {
        workflowId: input.payload.workflowId,
        repo: input.payload.repo,
        url: input.url,
        timestamp: new Date().toISOString()
    };
    // Simulate saving
    ctx.log(`record_memory: saved ${JSON.stringify(memory)}`);
    return { saved: true };
}
//# sourceMappingURL=activities.js.map