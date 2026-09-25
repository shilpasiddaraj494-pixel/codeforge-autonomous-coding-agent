<<<<<<< HEAD
# CodeForge — Autonomous Coding Agent

A portfolio-ready autonomous software-engineering agent built with **Python, FastAPI, LangGraph and the OpenAI API**.

It can:

- inspect an existing project workspace
- plan code changes
- create, update and delete files
- run restricted validation commands
- inspect failures
- retry its implementation automatically
- expose the workflow through a FastAPI backend and browser UI

## Architecture

```text
User task
   |
   v
FastAPI
   |
   v
LangGraph workflow
   |
   +--> Planner (LLM)
   |
   +--> Editor (sandboxed file tools)
   |
   +--> Validator (safe command allowlist)
   |
   +--> Retry on failure
   |
   v
Completed implementation
```

## Safety design

The model does **not** receive unrestricted shell access.

- File edits are limited to `workspace/`.
- Path traversal is rejected.
- Validation commands are allowlisted.
- Shell operators and arbitrary network/system commands are not executed.
- The agent retries at most `MAX_ITERATIONS` times.

## Quick start — Windows

### 1. Extract the project and open it in VS Code

### 2. Create your environment file

Copy:

```text
.env.example
```

to:

```text
.env
```

Then replace:

```text
OPENAI_API_KEY=your_api_key_here
```

with your OpenAI API key.

### 3. Run

Double-click:

```text
run_windows.bat
```

or run:

```bash
run_windows.bat
```

### 4. Open

```text
http://127.0.0.1:8000
```

## Quick start — macOS / Linux

```bash
cp .env.example .env
chmod +x run_mac_linux.sh
./run_mac_linux.sh
```

Open:

```text
http://127.0.0.1:8000
```

## Docker

Create `.env`, then:

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

## API

### Health

```http
GET /health
```

### Workspace snapshot

```http
GET /api/workspace
```

### Run the coding agent

```http
POST /api/agent/run
Content-Type: application/json
```

Example:

```json
{
  "task": "Create a Python calculator module with pytest tests."
}
```

## Suggested demo

Paste this into the UI:

```text
Create a small Python expense tracker. Add expense.py with an Expense dataclass,
functions to add expenses and calculate totals by category, and pytest tests.
Handle invalid negative amounts with ValueError.
```

The agent should:

1. inspect the current workspace
2. produce a plan
3. create the implementation and tests
4. run validation
5. automatically retry if validation fails

## Run project tests

```bash
pytest
```

## Tech stack

- Python
- FastAPI
- LangGraph
- OpenAI Responses API
- Pydantic
- HTML/CSS/JavaScript
- Pytest
- Docker

## Resume bullet

**Autonomous Coding Agent — Python, LangGraph, FastAPI, OpenAI, Docker**

Built an autonomous software-engineering agent that analyzes repository context, plans multi-file code changes, applies sandboxed edits, validates implementations through automated tests, and self-corrects across iterative LangGraph workflows; exposed the system through a FastAPI API and interactive web interface.

## Portfolio description

**CodeForge — Autonomous Coding Agent**

An agentic AI system that moves beyond question-answering by executing an end-to-end software-development loop. CodeForge inspects a project workspace, plans implementation steps, modifies multiple files, runs controlled validation commands and uses test failures as feedback for autonomous correction.

## Repository structure

```text
autonomous-coding-agent/
├── app/
│   ├── agent.py
│   ├── config.py
│   ├── llm.py
│   ├── main.py
│   ├── models.py
│   ├── workspace.py
│   ├── static/
│   │   ├── app.js
│   │   └── style.css
│   └── templates/
│       └── index.html
├── tests/
│   └── test_workspace.py
├── workspace/
│   └── README.md
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run_windows.bat
└── run_mac_linux.sh
```
=======
# autonomous-ai-incident-intelligence-platform
Production-grade AI incident investigation platform using deep learning, agentic AI, RAG, MCP, Kubernetes and AWS.
>>>>>>> a842bb4d5a665040382b398d19a612593c30309f
