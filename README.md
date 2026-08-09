# Crystal OMS Executive Agent

Crystal OMS Executive Agent is an experimental, modern Order Management System dashboard designed specifically for executive leadership (the CEO). The project is built to eventually support a fully functional, LLM-driven Voice Assistant capable of querying, analyzing, and commanding the OMS through natural language.

> **Status:** Phase 2.4 completed. The read-only OMS data layer and Executive Dashboard UI are fully integrated and hardened. The system is now preparing for Phase 3 (Voice Agent Architecture).

---

## 🏗️ Architecture

The project follows a strictly typed, decoupled modular monolith pattern. 

- **Frontend**: React, TypeScript, Vite, Tailwind CSS v4, React Router.
- **Backend**: FastAPI, Pydantic, Python 3.12.
- **Data Source**: A local static JSON file (`crystal-oms-demo.json`) powers the application using an isolated `JSONOMSRepository` pattern, meaning it can easily be swapped out for a real database (PostgreSQL/Redis) or downstream APIs later.

### Data Flow (Read-Only)
The application currently operates under a strict read-only boundary to ensure stability before introducing the Agent. 

```text
React UI -> FastAPI (HTTP) -> OMSService -> JSONOMSRepository -> crystal-oms-demo.json
```

---

## 🚀 Features Currently Implemented

* **Executive Dashboard**: Real-time business metrics aggregated safely from the OMS dataset.
* **Derived Customer View**: Since the original OMS demo file is highly transactional, the system dynamically derives and aggregates a deduplicated Customer Directory with lifetime value and active order calculations.
* **Order Tracking**: Paginated list and detailed view of commercial orders, tracking nesting container structures, product configurations, and locations.
* **Workflow Tasks**: Tracking departmental assignments, turnaround times (TAT), and task status.
* **Analytics**: High-level dimensional distributions of Business Models, Order Statuses, Product Types, and Sales Executives.
* **Agent-Ready Contracts**: The `OMSService` requires strictly typed python objects (`OrderQuery`, `TaskQuery`, etc.) bypassing HTTP entirely. This guarantees the future LLM Agent will interact with the system securely and predictably.

---

## 📚 Documentation
Detailed architectural and behavioral contracts can be found in the `/docs` directory:
- [API Contract (`docs/api.md`)](./docs/api.md)
- [OMS Capabilities (`docs/oms-capabilities.md`)](./docs/oms-capabilities.md)
- [Agent-OMS Interface (`docs/agent-oms-interface.md`)](./docs/agent-oms-interface.md)
- [Analytics Derivation Rules (`docs/oms/analytics-rules.md`)](./docs/oms/analytics-rules.md)
- [Security & Write Boundaries (`docs/security-boundary.md`)](./docs/security-boundary.md)

---

## 🛠️ How to Run Locally

### 1. Start the Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend runs on `http://127.0.0.1:8000`.

### 2. Start the Frontend (Vite)
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
The frontend runs on `http://localhost:5173`.

---

## 🛣️ Roadmap

- [x] **Phase 1**: Frontend Foundation & Design System (Tailwind v4, Layout, Routing).
- [x] **Phase 2**: Backend Architecture & Data Integration (FastAPI, Repository Pattern, Derivations, Contracts).
- [ ] **Phase 3**: Voice Agent Architecture (STT, LLM Intent Classification, Tool Calling).
- [ ] **Phase 4**: Agent Polish & Write Capabilities (Command execution via Voice).
