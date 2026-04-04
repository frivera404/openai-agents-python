@echo off
cd /d "C:\Users\frive\MCP Servers\client\openai-agents-python-main"
"C:\Users\frive\MCP Servers\client\openai-agents-python-main\.venv\Scripts\python.exe" -m agent_private_i.task_loop >> "C:\Users\frive\MCP Servers\client\openai-agents-python-main\scripts\logs\task-loop.log" 2>&1
