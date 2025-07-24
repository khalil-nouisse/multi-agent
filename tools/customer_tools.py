# Tools/functions for customer agent
from langchain_core.tools import tool


# => Confirmation of processing of the request


# => sending the progress status of processing requests


@tool("ClientHistory", return_direct=True)
def get_client_history(client_id: str) -> str:
    """
    Retrieve the full history of interactions with a given client ID.
    """
    # Retrieve the client history from the database


@tool("CustomerInfo", return_direct=True)
def get_customer_info(name: str) -> str:
    """Get info about a customer by name."""
    return f"Info about customer {name}"

customer_tool_list = [get_client_history,get_customer_info]



