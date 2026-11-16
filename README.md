# EnterpriseOps AI

**AI-Powered IT Operations Monitoring and Incident Management Platform**

EnterpriseOps AI is an intelligent IT operations platform designed to detect system anomalies, analyze incidents using Generative AI, and assist technical teams in incident investigation and remediation.

It combines Machine Learning, Retrieval-Augmented Generation (RAG), LLMs, and agentic workflows to provide an end-to-end incident management process with human approval and auditability.

## Key Features

- **Log Simulation:** Generate synthetic operational logs for different services.
- **Anomaly Detection:** Detect abnormal system behavior using the Isolation Forest algorithm.
- **Automated Incident Creation:** Convert detected anomalies into structured incidents with severity levels.
- **AI-Powered Diagnosis:** Analyze incidents using an LLM through Groq.
- **Retrieval-Augmented Generation (RAG):** Retrieve relevant technical procedures from Markdown runbooks.
- **Agentic Workflow:** Orchestrate incident analysis and approval steps using LangGraph.
- **MCP Integration:** Expose tools for retrieving logs, incident details, runbooks, and approval status.
- **Human-in-the-Loop:** Require human approval before proceeding with remediation.
- **Audit Trail:** Record remediation decisions and execution results.
- **Interactive Dashboard:** Monitor incidents and manage approvals through a React interface.

## Architecture

```text
              Synthetic Logs
                    |
                    v
             FastAPI Backend
                    |
                    v
          Machine Learning Layer
             Isolation Forest
                    |
                    v
          Anomaly Detection
                    |
                    v
          Incident Management
                    |
          +---------+---------+
          |                   |
          v                   v
       SQLite              RAG Layer
                              |
                         Runbooks
                              |
                              v
                       Groq LLM
                              |
                              v
                     AI Diagnosis
                              |
                              v
                   LangGraph Workflow
                              |
                         MCP Tools
                              |
                              v
                    Human Approval
                       /       \
                  Approved   Rejected/Pending
                      |           |
                      v           v
                 Simulated      Blocked
                 Remediation   Remediation
                      |
                      v
                  Audit Logs
                      |
                      v
                React Dashboard
```

## Technology Stack

| Component | Technologies |
|---|---|
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn, Isolation Forest |
| Database | SQLite, SQLAlchemy |
| Generative AI | Groq API, LLM |
| RAG | Runbooks, Retrieval-Augmented Generation |
| Agentic AI | LangGraph |
| Tool Integration | Model Context Protocol (MCP) |
| Frontend | React, Vite, JavaScript |
| Testing | Pytest |

## Project Structure

```text
EnterpriseOps AI/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── incident_agent.py
│   │   │   └── mcp_server/
│   │   │       ├── server.py
│   │   │       ├── client.py
│   │   │       └── mcp_incident_agent.py
│   │   │
│   │   ├── api/
│   │   ├── core/
│   │   ├── ml/
│   │   │   └── anomaly_detector.py
│   │   ├── services/
│   │   │   ├── log_service.py
│   │   │   ├── storage_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── llm_service.py
│   │   │   └── remediation_service.py
│   │   ├── main.py
│   │   └── models.py
│   │
│   └── tests/
│
├── data/
│   └── runbooks/
│       ├── high_cpu.md
│       ├── database_error.md
│       └── high_latency.md
│
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── App.css
│
├── docs/
├── .env
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd "EnterpriseOps AI"
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

Otherwise, install the project dependencies documented in the backend environment.

### 4. Configure environment variables

Create a `.env` file in the project root and configure the Groq API key and model according to the settings used by `llm_service.py`.

Never commit API keys or other secrets to GitHub.

### 5. Start the backend

From the project root:

```bash
python -m uvicorn backend.app.main:app --reload
```

Backend:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite, usually:

`http://localhost:5173`

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/logs/simulate` | Generate synthetic logs |
| GET | `/logs` | Retrieve logs |
| GET | `/incidents` | Retrieve incidents |
| POST | `/ml/train` | Train the anomaly detection model |
| POST | `/ml/detect` | Detect anomalies |
| POST | `/incidents/process-anomalies` | Create incidents from anomalies |
| GET | `/ml/status` | Check ML model status |
| GET | `/rag/search` | Search technical runbooks |
| POST | `/incidents/{id}/analyze` | Generate an AI diagnosis |
| POST | `/incidents/{id}/approve` | Approve remediation |
| POST | `/incidents/{id}/reject` | Reject remediation |
| GET | `/incidents/{id}/approval` | Retrieve approval status |
| GET | `/incidents/{id}/audit` | Retrieve remediation audit history |

## Example Workflow

Consider a high CPU incident affecting `payment-service`.

1. Synthetic logs are generated.
2. Isolation Forest detects CPU usage exceeding the expected threshold.
3. An incident is created with HIGH severity.
4. The RAG component retrieves the `high_cpu.md` runbook.
5. The LLM generates a structured diagnosis with probable causes and recommended actions.
6. LangGraph orchestrates the workflow and MCP tools provide access to operational information.
7. A human reviews and approves or rejects the proposed remediation.
8. The remediation result and approval decision are recorded in the audit history.

## Testing

Run the backend test suite:

```bash
python -m pytest backend -v
```

The project includes tests for API endpoints, the approval gate, and remediation behavior.

## Safety and Limitations

- Remediation is currently **simulated**; no real service restart or infrastructure modification is performed.
- Human approval is required before the remediation workflow proceeds.
- AI-generated probable causes are hypotheses and must be verified by an operator.
- The current monitoring environment uses synthetic operational logs.

## Future Improvements

- Real-time log ingestion and streaming.
- Integration with production monitoring platforms.
- Real infrastructure remediation with strict access controls.
- Advanced observability dashboards.
- Expanded automated testing and deployment pipelines.

## Project Goal

The goal of EnterpriseOps AI is to explore how Machine Learning, Generative AI, and Agentic AI can work together to improve IT operations, accelerate incident investigation, and support safer operational decisions.