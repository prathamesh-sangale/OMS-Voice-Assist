# CEO Executive OMS Voice Agent

A robust, voice-enabled Executive Order Management System (OMS) Agent. This system provides executive-level users with the ability to query data, monitor analytics, and make authenticated, secure write operations using natural language text and voice commands.

## Overview

The Executive OMS Voice Agent is designed to streamline complex supply chain and logistics operations. By leveraging a hybrid routing engine (combining deterministic rules with Large Language Model capabilities), the agent can understand complex conversational context, handle follow-up queries naturally, and execute critical business operations with enterprise-grade safety.

## Key Features

- **Conversational Context Management**: The agent understands follow-up queries, allowing users to naturally refine filters or correct previous inputs (e.g., "show reefer orders", then "actually, make that quantity 3"). It features robust state tracking to remember active entities across multiple interactions.
- **Voice & Text Interoperability**: Seamlessly switch between voice commands and text chat, with real-time audio transcription and text-to-speech feedback.
- **Hands-Free Voice Activity Detection (VAD)**: The microphone supports automated Voice Activity Detection, enabling continuous, hands-free conversational loops without needing push-to-talk.
- **Traditional UI Fallbacks**: Bypasses the conversational agent for quick, targeted edits via standard Web UI Modals to provide flexibility between AI interactions and traditional workflows.
- **Native Date Interpretation**: Automatically parses and converts conversational NLP dates (e.g. "next sunday", "in two weeks") into strict valid DD-MM-YYYY formats safely.
- **Strict Execution Safety**: Write operations undergo rigorous draft validation against business rules. Actions are staged for confirmation, ensuring no unintended modifications occur to the repository.
- **Hybrid Intent Routing**: Fast, deterministic rules handle standard navigational and query intents, while an LLM fallback gracefully handles complex or ambiguous conversational requests.

## Architecture

```text
                 PRIVATE CEO APP
                       │
                       ▼
                 Voice / Text
                       │
                       ▼
                  Agent Router
                       │
              ┌────────┴────────┐
              ▼                 ▼
         Rule Engine           LLM
              │                 │
              └────────┬────────┘
                       ▼
                  Validation
                       │
                ┌──────┴──────┐
                ▼             ▼
               READ          WRITE
                              │
                         Confirmation
                              │
                              ▼
                         OMSService
                              │
                              ▼
                           OMS Data
```

## Security & Production Readiness

- **Deployment Boundary**: Designed for private, authenticated executive deployments.
- **Confirmation Protection**: One-time-use confirmation IDs are mapped in-memory with strict Time-To-Live (TTL) and replay protection to prevent unauthorized duplicate executions.
- **Data Integrity**: Atomic JSON writes with automatic backup generation before any mutation occurs.
- **Middleware Security**: Configured with Secure Headers (CSP, Frame protection) and Correlation IDs (`X-Request-ID`) for robust auditing.
- **Rate Limiting**: Integrated `slowapi` restricts high-cost endpoints, such as audio transcription and synthesis, to prevent abuse.

## Local Development Setup

### 1. Environment Configuration
Copy `.env.example` to `.env` in the `backend/` directory and add your `GROQ_API_KEY`.

### 2. Start the Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

## Production Docker Deployment

To deploy in a production environment using Docker Compose:

```bash
# Ensure backend/.env is populated with GROQ_API_KEY
docker-compose up -d --build
```

The frontend will be available on port `80`, and the backend will run on port `8000`.
