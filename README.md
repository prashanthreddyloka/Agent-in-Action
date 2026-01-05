# LangGraph Triage Agent

Minimal LangGraph + FastAPI service that:
1) classifies a support ticket,
2) fetches a fake order record (when an order ID is available),
3) drafts a reply, then pauses for Admin approval.

## Setup

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
OPENAI_API_KEY=sk-...
# Optional tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2-...
```

## Architecture

**State:** `messages`, `ticket_text`, `order_id`, `issue_type`, `evidence`, `recommendation`

**Nodes:**
- `ingest` → prepares state
- `classify_issue` → determines issue_type + extracts order_id if missing
- `fetch_order` (ToolNode) → looks up fake order data
- `draft_reply` → drafts the response
- `human_review` → Admin approves/rejects before finalize

## Usage

### Run the Server
```bash
uvicorn app.server:app --reload
```

### Test via Curl (HITL)
```bash
./curl_example.sh
```

## Development Process

To complete this assignment efficiently, I utilized an advanced AI coding assistant to accelerate the development of the LangGraph workflow.

**Process:**
1.  **Planning**: I reviewed the requirements and engaged an AI coding assistant to help draft an implementation plan. This ensured I covered all critical components (State management, API endpoints, Testing strategy) before diving into code.
2.  **Implementation**: I used the AI to scaffold the initial project structure and implement the core logic iteratively. I reviewed the generated code for the `AgentState` and node logic (`ingest`, `classify`, `draft`) to ensure it aligned with the design.
3.  **Refactoring for HITL**: To meet the Admin Approval requirement, I refactored the graph to support `thread_id` persistence and interrupt logic, allowing for a seamless "Human-in-the-Loop" workflow.
4.  **Verification**: I set up unit tests and mocked the necessary tools to verify the end-to-end flow, using a curl script to demonstrate the interaction.
