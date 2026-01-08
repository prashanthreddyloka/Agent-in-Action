# LangGraph Agent

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
OPENAI_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
```

## Architecture

**State:** `messages`, `ticket_text`, `order_id`, `issue_type`, `evidence`, `recommendation`

**Nodes:**
- ingest → prepares state
- classify_issue → determines issue_type + extracts order_id if missing
- fetch_order (ToolNode) → looks up fake order data
- draft_reply → drafts the response
- human_review → Admin approves/rejects before finalize

## Usage

### Run the Server
```
py -m uvicorn app.server:app --port 8080
```

### Test via Curl (HITL)
This is for invoking the issue
```
curl.exe -X POST http://localhost:8080/triage/invoke -H "Content-Type: application/json" -d "@invoke.json"
```
approving the issue
```
curl.exe -X POST http://localhost:8080/triage/invoke -H "Content-Type: application/json" -d "@approve.json"
```
## Development Process
1.  **Manual Planning**: I sat down and outlined the three key entities (customer, assistant, admin) and properly mapped them to LangGraph nodes. I defined the state schema (`AgentState`) manually to ensure it captured all necessary context (`order_id`, `issue_type`) before writing any code.
2.  **Implementation**: Once the architecture was clear, I implemented the modules iteratively. I focused on connecting the nodes (`ingest` -> `classify` -> `tool`) in a logical flow, ensuring the control flow handled missing order IDs correctly.
3.  **Refactoring for HITL**: To meet the Admin Approval requirement, I refactored the graph to support `thread_id` persistence and interrupt logic, enabling a seamless "Human-in-the-Loop" workflow.
4.  **Verification**: I established unit tests and mocked the necessary tool outputs to verify the end-to-end flow, using curl scripts to validate the API interactions.
