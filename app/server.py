from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.graph import app as graph_app
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
import uuid

app = FastAPI(title="LangGraph Triage Agent")

class TriageRequest(BaseModel):
    ticket_text: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None
    thread_id: Optional[str] = None

class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool
    feedback: Optional[str] = None

@app.post("/triage/invoke")
async def invoke_triage(request: TriageRequest):
    """
    Invokes the triage agent. Use thread_id to persist state.
    """
    initial_state = {}
    
    if request.ticket_text:
        initial_state["ticket_text"] = request.ticket_text
        if not request.messages:
             initial_state["messages"] = [HumanMessage(content=request.ticket_text)]
    
    if request.messages:
        converted_messages = []
        for msg in request.messages:
            role = msg.get("role") or msg.get("type")
            content = msg.get("content")
            if role == "user" or role == "human":
                converted_messages.append(HumanMessage(content=content))
            elif role == "assistant" or role == "ai":
                converted_messages.append(AIMessage(content=content))
            # Add other types if necessary
        initial_state["messages"] = converted_messages

    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        # Run until interruption
        result = graph_app.invoke(initial_state, config=config)
        
        # Check next steps
        # If interrupted, graph_app.get_state(config) would show next: human_review_node
        current_state = graph_app.get_state(config)
        next_step = current_state.next
        
        response = {
            "thread_id": thread_id,
            "next_step": next_step,
            "values": convert_messages_to_dict(result) # result is the state at interruption or end
        }
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/triage/approve")
async def approve_response(request: ApprovalRequest):
    """
    Provide feedback and resume execution.
    """
    thread_id = request.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    # Update state with feedback
    graph_app.update_state(
        config,
        {
            "approved": request.approved, 
            "human_feedback": request.feedback
        },
        as_node="human_review_node" # We are updating as if this node just ran?
        # Actually, we interrupted BEFORE human_review_node.
        # So we update the state, and then we want to RESUME.
        # If we just update state keys, user needs to resume.
        # Ideally we update state and continue.
        # If we assume interrupt_before=["human_review_node"], then we are paused right before it.
        # Updating state usually adds to the state history.
    )
    
    try:
        # Resume
        result = graph_app.invoke(None, config=config)
        
        current_state = graph_app.get_state(config)
        next_step = current_state.next
        
        response = {
             "thread_id": thread_id,
             "next_step": next_step,
             "values": convert_messages_to_dict(result)
        }
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def convert_messages_to_dict(state_values):
    """Helper to make messages serializable"""
    new_values = state_values.copy()
    if "messages" in new_values:
        new_values["messages"] = [
            {"type": m.type, "content": m.content} for m in new_values["messages"]
        ]
    return new_values

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
