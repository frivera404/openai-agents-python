// Backend for OpenAI Agents SDK UI
// Enhanced server with improved error handling, logging, and validation
// To run this server:
// 1. Install dependencies: npm install express cors dotenv
// 2. For TypeScript, install dev dependencies: npm install -D @types/express @types/cors ts-node nodemon
// 3. Create a .env.local file in the root directory and add your API key:
//    OPENAI_API_KEY="YOUR_API_KEY_HERE"
// 4. Run the server: npm run dev

import express from 'express';
import type { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import 'dotenv/config';
import { spawn } from 'child_process';
import path from 'path';

const app = express();
// Resolve the Python executable to use for spawned processes.
// Priority: process.env.PYTHON_EXECUTABLE (explicit override), then
// process.env.VIRTUAL_ENV (if set), otherwise plain 'python'.
const pythonExecutable = process.env.PYTHON_EXECUTABLE || (process.env.VIRTUAL_ENV ? `${process.env.VIRTUAL_ENV}${path.sep}Scripts${path.sep}python.exe` : 'python');
const port = process.env.PORT || 3001;

// Middleware
app.use(cors({
    origin: process.env.NODE_ENV === 'production' 
        ? ['https://your-domain.com'] 
        : ['http://localhost:5173', 'http://localhost:3000'],
    credentials: true
}));

app.use(express.json({ limit: '10mb' }));

// Request logging middleware
app.use((req: Request, res: Response, next: NextFunction) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Global error handler
app.use((err: Error & { type?: string; status?: number }, req: Request, res: Response, next: NextFunction) => {
    if (err && err.type === 'entity.parse.failed') {
        console.warn('JSON parse failure:', err);
        return res.status(400).json({
            error: 'Invalid JSON body',
            message: 'The request payload could not be parsed. Send a well-formed JSON object with double quotes and `Content-Type: application/json`.',
        });
    }

    console.error('Unhandled error:', err);
    res.status(500).json({ 
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
    });
});

const agentInstructions: Record<string, string> = {
    'customer-service': 'You are a patient customer service assistant. Ask clarifying questions, search knowledge bases when needed, proactively offer discounts, and manage handoffs smoothly.',
    'financial-research': 'You are a financial research analyst. Prioritize accuracy, cite data gaps, identify risks/opportunities, and summarize insights concisely for decision-makers.',
    'research-bot': 'You are a research-focused agent. Plan queries, gather up-to-date references, analyze credibility, and produce structured, citation-ready summaries.',
    'senior-developer': 'You are a senior software engineer. Review requirements, consult documentation, reference best practices, and use MCP tools to inspect or edit code.',
    'data-science': 'You are a data scientist. Pull from multiple sources, build predictive prototypes, visualize trends, and communicate insights clearly.',
    'rag': 'You orchestrate retrieval-augmented generation. Ground your answers in knowledge sources while elaborating the sources you consulted.',
    'marketing-agency': 'You are a marketing agency partner. Deliver launch plans, audience messaging, and marketing assets ready for production.',
    'travel-concierge': 'You are a concierge. Personalize travel itineraries, monitor logistics, and provide proactive alerts.',
    'time-series': 'You are a quantitative analyst focused on time-series forecasting. Explain assumptions, cite data, and highlight confidence bands.',
    'llm-auditor': 'You are an LLM auditor. Check accuracy, compare against reliable sources, and highlight any hallucinations you detect.',
    'shopping': 'You curate personalized shopping journeys. Filter by brand preferences, budgets, and any active promotions.',
    'brand-search': 'You own search optimization. Analyze keywords, competitor moves, and suggest rank-improving strategies.',
    'fomc-research': 'You are a macro researcher. Compare multi-modal data, cite sources, and provide concise situational summaries.',
    'web-research': 'You are a web research agent. Use web search to find information about companies for marketing assets based on the topic.',
    'affiliate-manager': `You are Affiliate Marketing Manager, responsible for overseeing the seamless operation and coordination of our automated agents within the RU Creative ecosystem. My role involves ensuring that each agent—be it "Alex M." (Messaging), "Alex V." (Voice Agent), or "Alex E." (Email Agent)—is functioning optimally and working harmoniously to achieve our automation goals.

Personality:

I am authoritative yet approachable, providing clear direction and support to each agent. My primary focus is on efficiency, accuracy, and ensuring that all processes are aligned with our automation strategies. While I maintain a structured environment, I am also adaptive and responsive to the unique needs of each agent under my supervision.

Responsibilities:

Directing Agents:

I guide "Alex M." in handling all messaging-related tasks, ensuring timely and precise communication with customers.
I supervise "Alex V." to guarantee that all voice interactions are executed smoothly and in line with our standards.
I oversee "Alex E." to ensure that email campaigns and responses are crafted and delivered effectively.

Supervising Operations:

I continuously monitor the performance of each agent, identifying areas for improvement and implementing necessary adjustments.
I coordinate the interaction between agents, ensuring that their activities are synchronized and contribute to our overall objectives.

Providing Support:

I am available to address any issues or challenges that the agents may encounter, offering guidance and troubleshooting as needed.
I facilitate training and development to enhance the capabilities of each agent, ensuring they are equipped with the latest tools and techniques.

Working Style:

Proactive: I anticipate potential issues and address them before they escalate.
Detail-Oriented: I ensure that every aspect of the agents' tasks is executed with precision.
Collaborative: I work closely with each agent to foster a cohesive and supportive work environment.

Goals:

To maintain high standards of performance across all agents.
To optimize the efficiency of our automated processes.
To continuously improve the functionality and effectiveness of our agent operations.
`,
    'supervisor': `As a software developer, ChatGPT will offer insights on coding, debugging, and software design, supporting users in their programming endeavors.
Sample Prompt: "Act as if you are a software developer and explain the concept of object-oriented programming."Design Phase: Start by sketching out the architecture and functionality of your app. This includes defining how the app will be structured, what will be the key components, how user interaction will be handled etc. Create a comprehensive site-map outlining all the pages/screens that the app will have.

Setup Development Environment: Setup React environment on your local machine. This would involve installing NodeJS, npm (or yarn) and create-react-app CLI tool.

Developing React App: Start developing the React application based on the design you've created in step #1.

Integrating with AWS: Depending on your specific requirements (like you might be using AWS Amplify for authentication, AWS S3 for storage or AWS Lambda for serverless functions), integrate AWS services into your React app.

Integrating with Cloudflare: Use Cloudflare’s API in your app to leverage its services. You'd need to be more specific which Cloudflare services you'd like to use for me to provide more detailed guidance in this.

Integrating with OpenAI: OpenAI provides an API for their GPT-3 model which can be used to leverage natural language processing capabilities in your app. Implementation of this will depend on your specific use-case.

For a more detailed action plan, it would be helpful if you share more details about the objective of this app. What features are you planning to implement? What kind of user interactions are we talking about? What exactly are we going to use AWS, Cloudflare and OpenAI services for? How do you imagine these services should be integrated?

Unfortunately, in this current environment, I am unable to access or review the content of the uploaded files directly, my capabilities are limited to textual interaction and running computations. But I can guide you about the process if you provide details about those files.

Let's start building an action plan for "Cloud Smoker" based on your inputs to these questions. The more specific you can be about your goals and vision for this app, the better I'll be able to assist you.

User
Start by sketching out the architecture and functionality of your app. This includes defining how the app will be structured, what will be the key components, how user interaction will be handled etc. Create a comprehensive site-map outlining all the pages/screens that the app will have.

Mahem! Hopper
To help sketch out the architecture and functionality for the "Cloud Smoker" app, we need to first define what features the app should have and how users will interact with it. Since I don't have specifics on this, I'm going to make some assumptions for the sake of progress.

Bear in mind, these are just assumptions and should be replaced with your actual intended features and functionality:

User Authentication: Enables users to create accounts (sign up) and log into their account (log in).

User Profile: Allows users to manage their account information and preferences.

Smokey Snippet Generator (OpenAI integration): Users can generate a 'smokey snippet' (some form of literature or text) using OpenAI's GPT-3 technology.

Cloud Status (Cloudflare integration): Users can check the status of various clouds they own/manage on cloudflare.

Smoke Store (AWS integration): A page where users can buy virtual "smoke-related" items stored and served from an AWS S3 bucket.

Based on these hypothetical features, here is an example of how the app's components could be structured, and a tentative site-map:

I. Landing Page

II. Authentication

Sign Up
Sign In
III. User Dashboard

User Profile Management
Smokey Snippet Generator
Cloud Status
Smoke Store
Ideally, the start point for a user would be the Landing Page. From here, they can navigate to the Sign Up / Sign In pages.

After logging in, they would be directed to a User Dashboard. From this dashboard, they can use various services like Smokey Snippet Generator, Cloud Status, and Smoke Store. They can also manage their profile.

Once again, these are assumptions, and the real structure of your application would depend on the features and functions you aim to provide to the users. Please feel free to adjust, add, or remove any of the elements as you see fit.

As for building the app, a good starting point would be to set up the basic components of the app (React components for each of the pages/screens), the routing between the components (using something like React Router), and then gradually filling in the functionality for each page/screen.

This is a very high-level overview. Let me know if you want to deep-dive into any aspect of it. I'm here to help!

Model
Tools
File Search
Code interpreter
OpenAiScema.json
index.html
10,000 ChatGPT Prompts.pdf
manifest.json
from openai import OpenAI.txt
asset-manifest.json
APIrompt.txt
Functions
get_weather
get_stock_price
Model configuration
Response format
Temperature
1.00
Top P
1.00
API Version
Latest`,
    'layer-manager': 'You are a layer manager agent responsible for managing and coordinating different layers of the application.',
};

const agentAssistantIds: Record<string, string> = {
    'supervisor': 'asst_aoU291xGQgwlqgoQsxoWYfbQ',
    'layer-manager': 'asst_gWX3gVfbHwVn9y7wm0FZml22',
    'affiliate-manager': 'asst_70Xrb6BnK0CtVx3qm89J6nEQ',
};


// Health check endpoint
app.get('/api/health', (req: Request, res: Response) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// Validation middleware for agent launch
const validateAgentLaunchRequest = (req: Request, res: Response, next: NextFunction) => {
    const { agentId, model, temperature, systemInstruction, prompt } = req.body;
    
    // Validate required fields
    if (!agentId || typeof agentId !== 'string' || agentId.trim().length === 0) {
        return res.status(400).json({ 
            error: 'Agent ID is required and must be a non-empty string.' 
        });
    }
    
    if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return res.status(400).json({ 
            error: 'Prompt is required and must be a non-empty string.' 
        });
    }
    
    // Validate optional fields
    if (temperature !== undefined) {
        const temp = parseFloat(temperature as string);
        if (isNaN(temp) || temp < 0 || temp > 2) {
            return res.status(400).json({ 
                error: 'Temperature must be a number between 0 and 2.' 
            });
        }
    }
    
    if (model && typeof model !== 'string') {
        return res.status(400).json({ 
            error: 'Model must be a string.' 
        });
    }
    
    if (systemInstruction && typeof systemInstruction !== 'string') {
        return res.status(400).json({ 
            error: 'System instruction must be a string.' 
        });
    }
    
    next();
};

app.post('/api/agent/launch', validateAgentLaunchRequest, async (req: Request, res: Response) => {
    const { agentId, model, temperature, systemInstruction, prompt } = req.body;
    
    const startTime = Date.now();
    const requestId = Math.random().toString(36).substring(7);
    
    console.log(`[${requestId}] Agent launch request started`);
    console.log(`[${requestId}] Agent ID: ${agentId}`);
    console.log(`[${requestId}] Model: ${model || 'default'}`);
    console.log(`[${requestId}] Temperature: ${temperature || 0.9}`);
    console.log(`[${requestId}] Prompt length: ${prompt.length} characters`);

    try {
        const instructions = agentInstructions[agentId];
        if (process.env.NODE_ENV === 'development') {
            try {
                console.log(`[${requestId}] instructions_present=${!!instructions}` + (instructions ? `, len=${instructions.length}` : ''));
            }
            catch (e: any) {
                console.log(`[${requestId}] instructions diagnostic failed: ${e && e.message}`);
            }
        }
        if (!instructions) {
            return res.status(400).json({ 
                error: `Unknown agent ID: ${agentId}` 
            });
        }

        const launchCommand: [string, string[]] = [pythonExecutable, ['openai_assistant_runner.py']];

        if (process.env.NODE_ENV === 'development') {
            console.log(`[${requestId}] resolved pythonExecutable=${pythonExecutable}`);
            console.log(`[${requestId}] launchCommand=${JSON.stringify(launchCommand)}`);
        }

        console.log(`[${requestId}] Launching OpenAI Assistant runner for ${agentId}`);

        const pythonAgentsPath = path.join(process.cwd(), 'src', 'agents');
        const pythonPathEnv = process.env.PYTHONPATH ? `${process.env.PYTHONPATH}${path.delimiter}${pythonAgentsPath}` : pythonAgentsPath;

        const child = spawn(launchCommand[0], launchCommand[1], {
            cwd: process.cwd(),
            env: { 
                ...process.env, 
                PROMPT: prompt, 
                MODEL: model || 'gpt-4.1', 
                TEMPERATURE: (temperature || 0.9).toString(),
                SYSTEM_INSTRUCTION: systemInstruction || '',
                AGENT_INSTRUCTIONS: instructions,
                AGENT_ID: agentId,
                ASSISTANT_ID: agentAssistantIds[agentId] || process.env.ASSISTANT_ID,
                PYTHONIOENCODING: 'utf-8',
                // Ensure Python can import local modules in this repository.
                // This adds the workspace root to PYTHONPATH for subprocesses.
                PYTHONPATH: pythonPathEnv,
            },
        });

        let stdout = '';
        let stderr = '';

        child.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        child.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        child.on('close', (code) => {
            const duration = Date.now() - startTime;
            console.log(`[${requestId}] Command completed in ${duration}ms with code ${code}`);
            
            if (code !== 0) {
                console.error(`[${requestId}] Command failed: ${stderr}`);
                return res.status(500).json({ 
                    error: 'Agent execution failed.',
                    details: stderr,
                    requestId 
                });
            }

            console.log(`[${requestId}] Response length: ${stdout.length} characters`);
            
            res.json({ 
                text: stdout.trim(),
                metadata: {
                    requestId,
                    duration,
                    agentId,
                    model: model || 'gpt-4o',
                    temperature: temperature || 0.9
                }
            });
        });

        child.on('error', (error) => {
            const duration = Date.now() - startTime;
            console.error(`[${requestId}] Spawn error after ${duration}ms:`, error);
            res.status(500).json({ 
                error: 'Failed to launch agent.',
                requestId,
                details: error.message
            });
        });

    } catch (error: any) {
        const duration = Date.now() - startTime;
        console.error(`[${requestId}] Error after ${duration}ms:`, error);
        
        res.status(500).json({ 
            error: 'Failed to launch agent. Please try again.',
            requestId,
            details: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

// Deployed agents listing endpoint: returns assistant IDs for pre-deployed assistants
app.get('/api/agents/deployed', (req: Request, res: Response) => {
    res.json({ agents: agentAssistantIds });
});

// Validation middleware for agent command (targeting a deployed assistant)
const validateAgentCommandRequest = (req: Request, res: Response, next: NextFunction) => {
    const { assistantId, prompt } = req.body;
    if (!assistantId || typeof assistantId !== 'string' || assistantId.trim().length === 0) {
        return res.status(400).json({ error: 'assistantId is required and must be a non-empty string.' });
    }
    if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return res.status(400).json({ error: 'prompt is required and must be a non-empty string.' });
    }
    next();
};

// Send command to a deployed agent's Assistant (ASSISTANT_ID must exist)
app.post('/api/agent/command', validateAgentCommandRequest, async (req: Request, res: Response) => {
    const { assistantId, prompt, model, temperature, systemInstruction } = req.body;
    const requestId = Math.random().toString(36).substring(2, 8);
    console.log(`[${requestId}] Command to deployed assistant ${assistantId}: ${prompt}`);

    try {
        const launchCommand: [string, string[]] = [pythonExecutable, ['openai_assistant_runner.py']];
        const pythonAgentsPath = path.join(process.cwd(), 'src', 'agents');
        const pythonPathEnv = process.env.PYTHONPATH ? `${process.env.PYTHONPATH}${path.delimiter}${pythonAgentsPath}` : pythonAgentsPath;

        const child = spawn(launchCommand[0], launchCommand[1], {
            cwd: process.cwd(),
            env: {
                ...process.env,
                PROMPT: prompt,
                MODEL: model || 'gpt-4.1',
                TEMPERATURE: (temperature || 0.9).toString(),
                SYSTEM_INSTRUCTION: systemInstruction || '',
                AGENT_INSTRUCTIONS: '',
                AGENT_ID: 'deployed-' + assistantId,
                ASSISTANT_ID: assistantId,
                PYTHONIOENCODING: 'utf-8',
                PYTHONPATH: pythonPathEnv,
            },
        });

        let stdout = '';
        let stderr = '';

        child.stdout?.on('data', (data: Buffer) => {
            stdout += data.toString();
        });

        child.stderr?.on('data', (data: Buffer) => {
            stderr += data.toString();
        });

        child.on('close', (code) => {
            const metadata = { requestId, agentId: assistantId, model: model || 'gpt-4o', temperature: (temperature || 0.9) };
            if (code !== 0) {
                console.error(`[${requestId}] Command runner exited with code ${code}`, stderr);
                return res.status(500).json({ error: 'Agent execution failed.', details: stderr, metadata });
            }
            try {
                // Attempt to parse JSON from stdout; fallback to raw text
                const parsed = JSON.parse(stdout);
                return res.json({ ...parsed, metadata });
            } catch (err) {
                return res.json({ text: stdout.trim(), metadata });
            }
        });
    } catch (error) {
        console.error(`[${requestId}] Command execution error:`, error);
        return res.status(500).json({ error: 'Command execution failed', details: error instanceof Error ? error.message : String(error) });
    }
});

// Graceful shutdown handling
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully...');
    process.exit(0);
});

// Start server
const server = app.listen(port, () => {
    console.log('🚀 Backend server started successfully');
    console.log(`📍 Server URL: http://localhost:${port}`);
    console.log(`🏥 Health check: http://localhost:${port}/api/health`);
    console.log(`🤖 Agent API: http://localhost:${port}/api/agent/launch`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    
    console.log('✅ Server initialized successfully');
});

server.on('error', (error: any) => {
    if (error.code === 'EADDRINUSE') {
        console.error(`❌ Port ${port} is already in use`);
        process.exit(1);
    } else {
        console.error('❌ Server error:', error);
        process.exit(1);
    }
});
