from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from app.state import AgentState
from app.tools import fetch_order
import json

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def ingest(state: AgentState):
    """
    Ensures ticket_text is populated from the latest message if not already present.
    """
    messages = state.get("messages", [])
    if not state.get("ticket_text") and messages:
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage) or msg.type == 'human':
                return {"ticket_text": msg.content}
    return {}

def classify_issue(state: AgentState):
    """
    Classifies the issue and extracts order_id.
    """
    ticket_text = state.get("ticket_text", "")
    
    system_prompt = """You are a helpful assistant for a customer support system.
    Your task is to analyze the incoming ticket and extract the following information:
    1. issue_type: One of ['shipping', 'product_defect', 'billing', 'other'].
    2. order_id: The order ID if mentioned (usually a 5-digit number). If not found, return null.
    
    Return the result as valid JSON with keys: "issue_type", "order_id".
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}")
    ])
    
    chain = prompt | llm
    try:
        response = chain.invoke({"text": ticket_text})
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        
        data = json.loads(content)
        return {
            "issue_type": data.get("issue_type"),
            "order_id": data.get("order_id")
        }
    except Exception as e:
        print(f"Error in classification: {e}")
        return {"issue_type": "other", "order_id": None}

def execute_order_lookup(state: AgentState):
    """
    Manually executes the fetch_order tool logic.
    """
    order_id = state.get("order_id")
    result = fetch_order.invoke({"order_id": order_id})
    return {"evidence": result}

def draft_reply(state: AgentState):
    """
    Drafts a reply based on the gathered information.
    """
    issue_type = state.get("issue_type")
    order_id = state.get("order_id")
    human_feedback = state.get("human_feedback")
    
    # Use evidence instead of message history for tool output
    tool_output = state.get("evidence")
    
    system_prompt = f"""You are a customer support agent.
    Issue Type: {issue_type}
    Order ID: {order_id}
    Back-end Order Status: {tool_output if tool_output else "Not checked or Not found"}
    """
    
    if human_feedback:
        system_prompt += f"\n\nIMPORTANT: The admin has rejected your previous draft with the following feedback: {human_feedback}\nPlease incorporate this feedback and generate a revised reply."
    else:
        system_prompt += "\n\nDraft a helpful, professional, and concise reply to the customer."
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{text}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"text": state.get("ticket_text", "")})
    
    # We don't add to messages yet, allows revision. We store in recommendation.
    return {"recommendation": response.content}

def human_review_node(state: AgentState):
    """
    Output placeholder for human review.
    Does nothing logic-wise, just serves as an interruption point or a pass-through.
    Real logic happens in the conditional edge *after* this or *before* this?
    Actually we interrupt BEFORE this node.
    So this node runs AFTER the human has provided input (via state update).
    """
    pass
    # If we are here, it means we resumed.
    # The state should have been updated with 'approved' and 'human_feedback'.
    # We can handle routing in the conditional edge.
    return {}

def finalize_response(state: AgentState):
    """
    Commits the approved recommendation to messages.
    """
    recommendation = state.get("recommendation")
    return {"messages": [AIMessage(content=recommendation)]}
