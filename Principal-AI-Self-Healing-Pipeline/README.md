# Autonomous Self-Healing Data Pipeline

A learning-level prototype that automatically detects and recovers when a third-party API changes its response structure.

## Problem

The original API returns:

{"name": "Rohit", "age": 22, "city": "Bangalore"}

After a schema change, it returns:

{"user": {"full_name": "Rohit", "details": {"age": 22, "location": "Bangalore"}}}

The existing extractor fails because the fields are no longer at the expected locations.

## Solution

The system automatically:

1. Detects the extraction failure.
2. Analyzes the old and new API responses.
3. Identifies the new field mapping.
4. Generates a new extractor.
5. Tests the generated code inside Docker.
6. Rejects failed code.
7. Deploys the code only after successful testing.

## Architecture

Mock API
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
Validation
   ↓
Deploy New Extractor

## Schema Mapping

Old field → New field

name → user.full_name
age  → user.details.age
city → user.details.location

The internal output remains:

{"name": "...", "age": 0, "city": "..."}

## Project Structure

Principal-AI-Self-Healing-Pipeline/
├── agents/
│   ├── analyzer.py
│   └── coder.py
├── extractor/
│   └── active_extractor.py
├── memory/
├── mock_api/
│   └── main.py
├── sandbox/
│   └── runner.py
├── .env.example
├── main.py
├── memory_store.py
├── requirements.txt
└── README.md

## Components

mock_api/main.py
Provides the mock third-party API with V1 and V2 responses.

agents/analyzer.py
Uses Gemini to understand the API schema change and generate the field mapping.

agents/coder.py
Generates a new Python extractor using the mapping.

sandbox/runner.py
Runs generated code inside an isolated Docker container and returns the result or error.

memory_store.py
Stores previous generation attempts and errors for context.

main.py
Controls the complete self-healing workflow.

## Security

LLM-generated code is never executed directly on the host machine.

Generated code is first executed inside a Docker container.

Only code that passes the sandbox test is deployed as the active extractor.

For production, additional controls such as resource limits, network restrictions, timeouts, non-root containers, and stronger isolation would be required.

## Context Memory

The system stores the previous generated code, mapping, success/failure status, and error.

This information can be provided to the next Coder Agent attempt to help avoid repeated mistakes.

## Technology Stack

Python
FastAPI
Gemini
Docker
JSON
Uvicorn
python-dotenv

## Setup

Create a virtual environment:

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

Install dependencies:

python -m pip install -r requirements.txt

Create the environment file:

Copy-Item .env.example .env

Make sure Docker Desktop is installed and running.

## Configuration

Set the following in .env:

LLM_PROVIDER=gemini
LLM_API_KEY=your_api_key_here
LLM_MODEL=gemini-3.5-flash

The LLM is optional. Without an API key, the project uses the local fallback.

Never commit .env or an actual API key to GitHub.

## Running

Terminal 1:

uvicorn mock_api.main:app --reload

Terminal 2:

python main.py

## API Endpoints

V1:

http://127.0.0.1:8000/users?version=1

V2:

http://127.0.0.1:8000/users?version=2

V1 represents the original API structure.

V2 represents the changed API structure that triggers self-healing.

## Example Flow

V1 API
↓
Extractor succeeds
↓
V2 API
↓
Extractor fails with KeyError
↓
Analyzer identifies schema change
↓
Coder generates new extractor
↓
Docker sandbox tests code
↓
Failed attempt is rejected
↓
Corrected code passes
↓
New extractor is deployed
↓
V2 extraction succeeds

## Example Output

[MONITOR] Extraction successful

[MONITOR] Extraction failed - schema changed
(KeyError: 'name')

[ANALYZER] Mapping discovered:
{"name": "user.full_name", "age": "user.details.age", "city": "user.details.location"}

[CODER] Testing an intentionally bad first attempt

[SANDBOX] Bad attempt rejected

[CODER] Generating corrected extractor

[SANDBOX] Corrected extractor passed:
{'name': 'Rohit', 'age': 22, 'city': 'Bangalore'}

[DEPLOY] New extractor is now active

[MONITOR] Extraction successful after self-healing

## Design Decisions

The mock API makes the schema change deterministic and easy to reproduce.

The Analyzer Agent provides semantic understanding of the schema change.

The Coder Agent generates replacement extraction code.

Docker provides isolation for generated code before deployment.

Context memory provides previous attempts and errors to future generations.

The internal schema remains fixed even when the external API changes.

## Limitations

This is a learning-level prototype.

It uses a simple mock API, lightweight JSON memory, and basic Docker sandboxing.

It does not currently provide production-grade monitoring, rollback, distributed orchestration, or advanced security controls.

## Future Improvements

- Stronger sandbox isolation
- Automatic rollback
- Versioned extractors
- Better schema-diff detection
- Persistent database memory
- Production monitoring
- Automated regression tests
- Kubernetes-based execution
- Human approval for high-risk changes

## Goal

The project demonstrates an autonomous self-healing pipeline:

Detect → Understand → Generate → Safely Test → Deploy