# CodeForge — Autonomous Coding Agent

CodeForge is an **agentic AI coding system** that works directly on an existing project workspace.

Instead of only generating code as text, CodeForge can inspect project files, understand a coding task, plan changes, create or update code, generate tests, run validation automatically, and retry when something fails.

In simple terms, CodeForge acts like a small autonomous software engineer.

---

## What It Does

CodeForge can:

- read an existing codebase
- understand a coding task
- create new files
- update existing files
- generate pytest tests
- run validation automatically
- use test failures as feedback
- retry with corrected code
- mark a task complete only after validation succeeds

---

## How It Works

```text
Task
 ↓
Inspect workspace
 ↓
Plan changes
 ↓
Edit files
 ↓
Generate tests
 ↓
Run validation
 ↓
Pass → Complete
Fail → Fix → Retry
```

CodeForge works directly on the existing project inside the `workspace/` directory.

---

## Tech Stack

**Python · LangGraph · Google Gemini API · FastAPI · Pydantic · Pytest · HTML · CSS · JavaScript · Docker · Git · GitHub**

---

## Demo

### CodeForge Interface

![CodeForge Dashboard](assets/codeforge-dashboard.png)

### Successful Autonomous Validation

![CodeForge Validation](assets/codeforge-validation.png)

---

## Example Task

```text
Create a Python string_utils.py module with two typed functions:

reverse_text(text: str) -> str
is_palindrome(text: str) -> bool

Add pytest tests for normal strings, empty strings,
and mixed-case palindromes.

Keep the implementation simple and make all tests pass.
```

For this task, CodeForge automatically:

- inspected the existing workspace
- created `string_utils.py`
- created `test_string_utils.py`
- ran the full pytest suite
- validated the implementation
- completed the task successfully

Example result:

```text
collected 7 items

test_calculator.py .....
test_string_utils.py ..

7 passed
```

The final execution status was:

```text
Completed
Task completed and validation passed.
```

---

## Another Example

CodeForge was also asked to create a Python calculator module.

The agent generated:

- `calculator.py`
- `test_calculator.py`

The implementation included:

- addition
- subtraction
- multiplication
- division
- division-by-zero handling
- type hints
- automated pytest coverage

The generated tests passed successfully.

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/shilpasiddaraj494-pixel/codeforge-autonomous-coding-agent.git
cd codeforge-autonomous-coding-agent
```

### 2. Create a `.env` file

Use `.env.example` as the template.

Add:

```text
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_available_gemini_model
MAX_ITERATIONS=3
```

### 3. Run on Windows

```powershell
.\run_windows.bat
```

Or run directly:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

---

## Example Prompt

```text
Create a small task manager module.

Add a typed Task dataclass containing:

- title
- completed
- priority

Add functions to:

- create tasks
- mark a task as completed
- filter completed tasks
- sort tasks by priority

Add pytest tests covering:

- normal cases
- empty lists
- duplicate titles
- invalid priority values

Keep the implementation clean and make all tests pass.
```

---

## Summary

CodeForge demonstrates how an LLM can be used inside an **autonomous software-engineering workflow**.

Instead of simply returning code, the system can:

**inspect → plan → edit → test → validate → retry → complete**

This makes CodeForge a practical example of **agentic AI applied to software development**.