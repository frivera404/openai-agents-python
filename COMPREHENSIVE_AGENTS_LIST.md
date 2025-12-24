
# Comprehensive OpenAI Agents SDK Agent List

This document provides a detailed overview of all available agents in the OpenAI Agents SDK, including their descriptions and specific abilities.

## UI Catalog Agents

### 1. Customer Service Agent

**Description**: Delivers support by analyzing issues, provides recommendations, discounts, helps customers check out, and facilitates transactions using handoffs between specialized agents.

**Abilities**:

- Issue analysis
- Recommendation generation
- Discount management
- Transaction facilitation
- Multi-agent handoffs
- Customer support automation

### 2. Financial Research Agent

**Description**: Composes financial research reports by planning search terms, retrieving data, analyzing fundamentals and risks, writing reports, and verifying accuracy.

**Abilities**:

- Research planning
- Data retrieval
- Fundamental analysis
- Risk assessment
- Report writing
- Accuracy verification

### 3. Research Bot

**Description**: Conducts comprehensive research by planning queries, searching the web, analyzing results, and generating structured reports with citations.

**Abilities**:

- Query planning
- Web searching
- Result analysis
- Structured reporting
- Citation management

### 4. Senior Developer Agent

**Description**: Acts as a senior developer using OpenAI Assistants API with vector store for knowledge retrieval, providing code-related advice and using MCP tools for filesystem operations.

**Abilities**:

- Code advice
- Knowledge retrieval via vector store
- MCP tool integration
- Filesystem operations
- Development guidance

### 5. Data Science

**Description**: Queries diverse data across multiple sources using natural language, builds predictive models, visualizes trends, and communicates key insights.

**Abilities**:

- Natural language data querying
- Multi-source data integration
- Predictive modeling
- Data visualization
- Insight communication

### 6. Retrieval-Augmented Generation (RAG)

**Description**: Uses RAG to get information from specified knowledge sources, ensuring responses are factually grounded, context-aware, and up-to-date.

**Abilities**:

- Knowledge source retrieval
- Fact-checking
- Context-aware generation
- Up-to-date information handling

### 7. Marketing Agency

**Description**: Streamlines new website and product launches. Identifies optimal DNS domains, generates entire websites, and develops marketing strategies.

**Abilities**:

- Website generation
- DNS optimization
- Marketing strategy development
- Launch planning

### 8. Travel Concierge

**Description**: Orchestrates personalized travel experiences and provides support throughout the user's journey, from planning to real-time itinerary alerts.

**Abilities**:

- Itinerary planning
- Personalization
- Real-time alerts
- Travel support coordination

### 9. Time Series Forecasting

**Description**: Automates time-series forecasting by leveraging BigQuery ML. Provides clear, explained predictions to support data-driven business decisions.

**Abilities**:

- Time-series analysis
- BigQuery ML integration
- Prediction generation
- Explanation of results

### 10. LLM Auditor

**Description**: Evaluates LLM-generated answers, verifies actual accuracy using the web, and refines the response to ensure alignment with real-world knowledge.

**Abilities**:

- LLM output evaluation
- Web-based verification
- Response refinement
- Accuracy assurance

### 11. Personalized Shopping

**Description**: Delivers personalized recommendations, tailored to specific brands, merchants, or marketplaces.

**Abilities**:

- Personalized recommendations
- Brand/merchant filtering
- Marketplace integration

### 12. Brand Search Optimization

**Description**: Analyzes top brand-related keywords and competitor search results, and generates suggestions to enhance a brand's search engine ranking.

**Abilities**:

- Keyword analysis
- Competitor research
- SEO suggestions
- Ranking optimization

### 13. FOMC Research

**Description**: Extracts web data, analyzes complex topics, executes custom functions, and generates summary reports from multi-modal data comparisons.

**Abilities**:

- Web data extraction
- Complex topic analysis
- Custom function execution
- Multi-modal data comparison
- Summary reporting

## Backend Agents (Not in UI Catalog)

### 14. Supervisor

**Description**: As a software developer, ChatGPT will offer insights on coding, debugging, and software design, supporting users in their programming endeavors. (Sample Prompt: "Act as if you are a software developer and explain the concept of object-oriented programming.")

**Abilities**:

- Coding insights
- Debugging assistance
- Software design guidance
- Programming support

### 15. Layer Manager

**Description**: You are a layer manager agent responsible for managing and coordinating different layers of the application.

**Abilities**:

- Application layer management
- Coordination
- Layer-specific operations

### 16. Affiliate Manager

**Description**: You are Affiliate Marketing Manager, responsible for overseeing the seamless operation and coordination of our automated agents within the RU Creative ecosystem. My role involves ensuring that each agent—be it "Alex M." (Messaging), "Alex V." (Voice Agent), or "Alex E." (Email Agent)—is functioning optimally and working harmoniously to achieve our automation goals. Personality: Authoritative yet approachable, providing clear direction and support to each agent. My primary focus is on efficiency, accuracy, and ensuring that all processes are aligned with our automation strategies.

**Abilities**:

- Agent coordination
- Messaging management
- Voice agent oversight
- Email agent supervision
- Automation optimization

## Technical Details

- **Model**: All agents use gpt-4.1 as the default OpenAI model
- **API**: OpenAI Assistants API with vector store integration
- **Tools**: MCP (Model Context Protocol) for external service access
- **Launch Method**: Via Express.js backend server at http://localhost:3002/api/agent/launch
- **UI Access**: Available through the React frontend at http://localhost:5173/

## Usage

To launch an agent:

1. Open the UI at http://localhost:5173/
2. Select an agent from the catalog
3. Enter a prompt
4. Click "Launch Agent"

The backend will execute the corresponding Python script with the appropriate environment variables and return the response.
