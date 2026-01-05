from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.state import AgentState
from app.nodes import ingest, classify_issue, draft_reply, human_review_node, finalize_response, execute_order_lookup

# Checkpointer
checkpointer = MemorySaver()

def should_fetch_order(state: AgentState):
    order_id = state.get("order_id")
    if order_id:
        return "execute_order_lookup"
    return "draft_reply"

def route_human_review(state: AgentState):
    """
    Routes based on admin approval.
    """
    if state.get("approved"):
        return "finalize_response"
    return "draft_reply"

# Define the graph
workflow = StateGraph(AgentState)

workflow.add_node("ingest", ingest)
workflow.add_node("classify_issue", classify_issue)
workflow.add_node("execute_order_lookup", execute_order_lookup)
workflow.add_node("draft_reply", draft_reply)
workflow.add_node("human_review_node", human_review_node)
workflow.add_node("finalize_response", finalize_response)

# Edges
workflow.set_entry_point("ingest")
workflow.add_edge("ingest", "classify_issue")

workflow.add_conditional_edges(
    "classify_issue",
    should_fetch_order,
    {
        "execute_order_lookup": "execute_order_lookup",
        "draft_reply": "draft_reply"
    }
)

workflow.add_edge("execute_order_lookup", "draft_reply")

# From draft to human review
workflow.add_edge("draft_reply", "human_review_node")

# Conditional edge after human review
workflow.add_conditional_edges(
    "human_review_node",
    route_human_review,
    {
        "finalize_response": "finalize_response",
        "draft_reply": "draft_reply"
    }
)

workflow.add_edge("finalize_response", END)

# Compile with checkpointer and interrupt
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review_node"]
)
