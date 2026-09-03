# Autonomous Self-Healing Data Pipeline

## Track 1: The Autonomous Self-Healing Data Pipeline

A learning-level agentic system that automatically detects and recovers from third-party API schema changes without manual intervention.

## Problem

Data pipelines can break when a third-party API changes its response structure.

The original API returns:

{"name": "Rohit", "age": 22, "city": "Bangalore"}

After the schema changes, it returns:

{"user": {"full_name": "Rohit", "details": {"age": 22, "location": "Bangalore"}}}

The external structure changes, but the internal pipeline must continue producing:

{"name": "Rohit", "age": 22, "city": "Bangalore"}

## Solution

The system automatically follows this workflow:

API
↓
Monitor
↓
Extraction Failure
↓
Semantic Analyzer Agent
↓
Schema Mapping
↓
Coder Agent
↓
Docker Sandbox
↓
Validation
↓
Deployer
↓
Updated Extractor

## Agentic Workflow

### 1. Dynamic Source

A local FastAPI server acts as the third-party data source.

It provides two versions:

/users?version=1

/users?version=2

V1 uses a flat JSON structure.

V2 uses a nested JSON structure.

The internal output format remains unchanged.

### 2. Monitor

The existing extractor processes the API response.

When the API changes and extraction fails, the monitor detects the error.

Example:

KeyError: 'name'

This failure indicates a possible schema change.

### 3. Semantic Analyzer Agent

The Analyzer compares the old response, new response, and extraction error.

It identifies the new locations of the required fields:

name → user.full_name
age → user.details.age
city → user.details.location

Gemini is used for semantic analysis when configured.

### 4. Coder Agent

The Coder Agent uses the discovered mapping to generate a new Python extraction function.

The generated extractor must continue producing the fixed internal schema:

name
age
city

### 5. Sandbox Evaluator

LLM-generated code is treated as untrusted code.

It is NOT executed directly on the host machine.

The generated extractor is executed inside an isolated Docker container.

The sandbox:

- Executes the generated code
- Provides test input
- Validates the output
- Captures errors and stack traces
- Rejects failed code

The demonstration intentionally generates a failed first attempt to show that the sandbox prevents invalid code from being deployed.

### 6. Deployer

Only after the generated extractor passes the Docker sandbox test, it is deployed as:

extractor/active_extractor.py

The pipeline then reloads the updated extractor and successfully processes the changed API response.

## Context Memory

The project maintains lightweight context memory in:

memory/memory.json

It stores information about previous generation attempts, including:

- Generated code
- Schema mapping
- Success/failure status
- Error information

This context can be supplied to the next Coder Agent attempt so that it does not repeatedly make the same mistake.

## Architecture

Mock FastAPI API
        ↓
Active Extractor
        ↓
Monitor
        ↓
Analyzer Agent
        ↓
Coder Agent
        ↓
Docker Sandbox
        ↓
    Pass / Fail
        ↓
   Deployer
        ↓
Updated Extractor

## Project Structure

Principal-AI-Self-Healing-Pipeline/
│
├── agents/
│   ├── analyzer.py
│   └── coder.py
│
├── extractor/
│   └── active_extractor.py
│
├── memory/
│   └── memory.json
│
├── mock_api/
│   └── main.py
│
├── sandbox/
│   └── runner.py
│
├── .env.example
├── main.py
├── memory_store.py
├── requirements.txt
└── README.md

## Technology Stack

Python
FastAPI
Gemini
Docker
JSON
Uvicorn
python-dotenv

## Security

The Coder Agent generates code, but generated code is never blindly executed on the host system.

All generated extraction code is tested inside Docker before deployment.

Only successfully validated code is promoted to the active extractor.

For a production implementation, additional security controls such as resource limits, timeouts, network restrictions, non-root execution, read-only filesystems, and stronger isolation would be required.

## Setup

Create and activate a virtual environment:

python -m venv .venv

.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r requirements.txt

Create the environment file:

Copy-Item .env.example .env

Configure Docker Desktop and make sure Docker is running.

## Configuration

Set the Gemini configuration in .env:

LLM_PROVIDER=gemini
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-3.5-flash

The LLM is optional. A local fallback is available when no API key is provided.

Never commit the actual .env file or API key to GitHub.

## Running

Start the mock API in Terminal 1:

uvicorn mock_api.main:app --reload

Run the pipeline in Terminal 2:

python main.py

## API

V1:

http://127.0.0.1:8000/users?version=1

V2:

http://127.0.0.1:8000/users?version=2

## Example Execution

V1 extraction succeeds:

[MONITOR] Extraction successful

V2 causes the original extractor to fail:

[MONITOR] Extraction failed - schema changed
(KeyError: 'name')

Analyzer discovers:

{"name": "user.full_name", "age": "user.details.age", "city": "user.details.location"}

Coder generates a new extractor.

The first invalid attempt is rejected by the Docker sandbox:

[SANDBOX] Bad attempt rejected

The corrected extractor passes:

[SANDBOX] Corrected extractor passed:
{'name': 'Rohit', 'age': 22, 'city': 'Bangalore'}

The validated extractor is deployed:

[DEPLOY] New extractor is now active

The changed API now works successfully:

[MONITOR] Extraction successful after self-healing

## Proof of Execution

The terminal execution demonstrates:

1. Original extractor successfully processes V1.
2. V2 causes a schema mismatch.
3. Analyzer identifies the changed structure.
4. Coder generates replacement code.
5. Docker rejects an invalid generated attempt.
6. Corrected code passes sandbox validation.
7. The new extractor is deployed.
8. V2 extraction succeeds after self-healing.

## Limitations

This is a learning-level prototype.

The current implementation uses a simple mock API, lightweight JSON memory, and basic Docker sandboxing.

It does not implement production-grade orchestration, monitoring, rollback, or advanced sandbox hardening.

## Future Improvements

- Stronger sandbox isolation
- Automatic rollback
- Versioned extractors
- More complex schema changes
- Persistent memory/database
- Production monitoring
- Automated regression tests
- Kubernetes-based sandbox execution

## Conclusion

The project demonstrates the required self-healing pipeline:

Detect → Understand → Rewrite → Safely Test → Deploy

It shows how an agentic system can automatically recover from an external API schema change while keeping the internal data format fixed.