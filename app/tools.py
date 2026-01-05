from langchain_core.tools import tool
import random

@tool
def fetch_order(order_id: str) -> str:
    """
    Fetches the status of an order given its ID.
    Returns a string describing the order status.
    """
    # Mock database lookup
    mock_orders = {
        "12345": "Order #12345 is currently in transit. Expected delivery: Tomorrow.",
        "67890": "Order #67890 has been delivered on 2024-12-25.",
        "55555": "Order #55555 is still processing in the warehouse.",
    }
    
    return mock_orders.get(order_id, f"Order #{order_id} not found in the system.")
