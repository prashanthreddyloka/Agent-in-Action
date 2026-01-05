# LangGraph Triage Agent

A minimal LangGraph agent that classifies support tickets, fetches order status, and drafts replies.
Built with LangGraph, LangChain, and FastAPI.

## Setup

1. **Clone the repository** (if not already done).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Variables**:
   Create a `.env` file with your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-...
   ```
   (Optional) For tracing:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=lsv2-...
   ```

## Usage

### Run the Server
```bash
uvicorn app.server:app --reload
```

### Test via Curl
Use the provided script:
```bash
./curl_example.sh
```

Or manually:
```bash
curl -X POST "http://localhost:8000/triage/invoke" \
     -H "Content-Type: application/json" \
     -d '{"ticket_text": "Where is my order #12345?"}'
```

## Testing

Run unit tests:
```bash
pytest tests/
```

## Architecture

- **State**: Tracks messages, ticket text, issued type, order ID, etc.
- **Nodes**:
  - `ingest`: Prepares state.
  - `classify_issue`: LLM extraction of issue type and order ID.
  - `fetch_order`: Tool to lookup fake order status.
  - `draft_reply`: LLM generation of final response.
- **Graph**: `ingest` -> `classify` -> (conditional) `fetch_order` -> `draft_reply` -> (interrupt) -> `human_review` -> `finalize`.

## Human-in-the-Loop (HITL) Workflow

The agent now stops before sending the final reply to allow for Admin Approval.

1. **Invoke Triage**:
   ```bash
   # Returns a thread_id and pauses at "human_review_node"
   curl -X POST "http://localhost:8000/triage/invoke" ...
   ```

2. **Approve or Reject**:
   ```bash
   curl -X POST "http://localhost:8000/triage/approve" \
        -H "Content-Type: application/json" \
        -d '{
              "thread_id": "<THREAD_ID_FROM_ABOVE>",
              "approved": true
            }'
   ```
   If `approved: false`, provide `"feedback": "Change tone to be friendlier"`. The agent will loop back to draft a new reply.

## Development Process

To complete this assignment efficiently, I utilized an advanced AI coding assistant to accelerate the development of the LangGraph workflow.

**Process:**
1.  **Planning**: I reviewed the requirements and engaged an AI coding assistant to help draft an implementation plan. This ensured I covered all critical components (State management, API endpoints, Testing strategy) before diving into code.
2.  **Implementation**: I used the AI to scaffold the initial project structure and implement the core logic iteratively. I reviewed the generated code for the `AgentState` and node logic (`ingest`, `classify`, `draft`) to ensure it aligned with the design.
3.  **Refactoring for HITL**: To meet the Admin Approval requirement, I refactored the graph to support `thread_id` persistence and interrupt logic, allowing for a seamless "Human-in-the-Loop" workflow.
4.  **Verification**: I set up unit tests and mocked the necessary tools to verify the end-to-end flow, using a curl script to demonstrate the interaction.

