from typing import TypedDict, Optional, List, Annotated
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    ticket_text: str
    order_id: Optional[str]
    issue_type: Optional[str]
    evidence: Optional[str]
    recommendation: Optional[str]
    human_feedback: Optional[str]
    approved: Optional[bool]
