
import React from 'react';

const CodeBlock: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded-md mt-2 overflow-x-auto">
        <code className="text-sm text-gray-800 dark:text-gray-200 font-mono">
            {children}
        </code>
    </pre>
);

const BackendGuide: React.FC = () => {
    return (
        <div className="p-6 md:p-8 max-w-4xl mx-auto text-gray-800 dark:text-gray-200">
            <h1 className="text-3xl font-bold mb-4">Backend Integration Guide</h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
                This guide explains how to set up and run the local backend server that securely proxies requests to the OpenAI Assistants API.
            </p>

            <section className="mb-10">
                <h2 className="text-2xl font-semibold border-b border-gray-300 dark:border-gray-600 pb-2 mb-4">1. Why a Backend?</h2>
                <p>
                    Calling the OpenAI Assistants API directly from the browser would expose your API key, which is a security risk. The backend server acts as a secure proxy:
                </p>
                <ul className="list-disc list-inside mt-2 space-y-1 pl-4">
                    <li>The frontend makes requests to our own backend.</li>
                    <li>The backend, which runs in a secure environment, securely stores the API key.</li>
                    <li>The backend forwards requests to the OpenAI Assistants API and returns the response to the frontend.</li>
                </ul>
            </section>

            <section className="mb-10">
                <h2 className="text-2xl font-semibold border-b border-gray-300 dark:border-gray-600 pb-2 mb-4">2. Setup Instructions</h2>
                <h3 className="text-xl font-medium mt-4 mb-2">Step 2.1: Install Dependencies</h3>
                <p>You'll need Node.js installed. From your project root, install the necessary server packages:</p>
                <CodeBlock>npm install express cors dotenv @google/genai</CodeBlock>
                <p className="mt-2">For TypeScript development, you may also need:</p>
                <CodeBlock>npm install -D @types/express @types/cors ts-node nodemon</CodeBlock>
                
                <h3 className="text-xl font-medium mt-6 mb-2">Step 2.2: Create a <code className="font-mono text-sm bg-gray-200 dark:bg-gray-700 p-1 rounded">.env</code> File</h3>
                <p>
                    In the root directory of the project, create a file named <code className="font-mono text-sm bg-gray-200 dark:bg-gray-700 p-1 rounded">.env</code>. This file will store your secret API key.
                </p>
                <CodeBlock>{`OPENAI_API_KEY="YOUR_API_KEY_HERE"
ASSISTANT_ID="YOUR_ASSISTANT_ID"
VECTOR_STORE_ID="OPTIONAL_VECTOR_STORE_ID"`}</CodeBlock>
                <p className="mt-2 text-sm text-yellow-600 dark:text-yellow-400">
                    <strong>Important:</strong> Never commit the <code className="font-mono text-sm">.env</code> file to version control. Add it to your <code className="font-mono text-sm">.gitignore</code> file.
                </p>
            </section>
            
            <section className="mb-10">
                <h2 className="text-2xl font-semibold border-b border-gray-300 dark:border-gray-600 pb-2 mb-4">3. Running the Application</h2>
                <p>
                    The application consists of two parts: the Vite frontend and the Express backend. They need to run simultaneously. We recommend using a tool like <code className="font-mono text-sm">concurrently</code>.
                </p>
                 <h3 className="text-xl font-medium mt-4 mb-2">Example <code className="font-mono text-sm">package.json</code> scripts:</h3>
                <CodeBlock>
{`"scripts": {
    "dev:frontend": "vite",
    "dev:backend": "nodemon server.ts",
    "dev": "concurrently \\"npm:dev:frontend\\" \\"npm:dev:backend\\""
}`}
                </CodeBlock>
                 <p className="mt-4">Run the following command to start both servers:</p>
                <CodeBlock>npm run dev</CodeBlock>
                <p className="mt-2">The Vite dev server will automatically proxy API requests from the frontend (at <code className="font-mono text-sm">/api</code>) to your backend server running on port 3001.</p>
            </section>

            <section>
                <h2 className="text-2xl font-semibold border-b border-gray-300 dark:border-gray-600 pb-2 mb-4">4. API Endpoint</h2>
                <h3 className="text-xl font-medium mt-4 mb-2">POST <code className="font-mono text-sm">/api/agent/launch</code></h3>
                <p>This is the primary endpoint for interacting with the agent.</p>
                <p className="font-medium mt-4">Request Body:</p>
                <CodeBlock>
{`{
    "agentId": "customer-service",
    "model": "gpt-4o",
    "temperature": 0.7,
    "systemInstruction": "You are a proactive customer support partner.",
    "prompt": "Summarize late delivery issues with empathy."
}`}
                </CodeBlock>
                <p className="font-medium mt-4">Success Response (200 OK):</p>
                <CodeBlock>
{`{
    "text": "The main benefits include enhanced security by protecting API keys..."
}`}
                </CodeBlock>
            </section>
        </div>
    );
};

export default BackendGuide;