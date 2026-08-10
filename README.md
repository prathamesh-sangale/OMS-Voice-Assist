# CEO Executive OMS Voice Agent

A robust, voice-enabled Executive Order Management System (OMS) Agent. This system allows a CEO to query data and make authenticated writes through both text and voice commands.

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

## Security & Production Readiness (Phase 7)
- **Deployment boundary**: Private CEO deployment only.
- **Confirmation Protection**: One-time use confirmation IDs mapped in-memory with strict TTL and replay protection.
- **Data Integrity**: Atomic JSON writes with automatic backup generation before mutation.
- **Middleware**: Secure Headers (CSP, Frame protection) and Correlation IDs (`X-Request-ID`).
- **Rate Limiting**: `slowapi` restricts high-cost endpoints like transcription and TTS.

## Local Development Setup

1. Copy `.env.example` to `.env` in `backend/` and add your `GROQ_API_KEY`.
2. Start the Backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. Start the Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Production Docker Deployment

To deploy in a production environment:

```bash
# Ensure .env is populated with GROQ_API_KEY
docker-compose up -d --build
```

The frontend will be available on port 80, and the backend on port 8000.
