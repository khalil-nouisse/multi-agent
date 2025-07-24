# Tools/functions for tech support agent

from typing import Annotated, List, Tuple, Union
from langchain.tools import BaseTool, StructuredTool, Tool
from langchain_core.tools import tool
from databse import get_status

# => confirmation du traitement pour le client

@tool("ticket", return_direct=False)
def ticket_state(title: str):
    """Provide information about the state of the ticket of the client from the database."""
    state = get_status(title , "ticket")
    return state


@tool("ClientHistory", return_direct=True)
def get_client_history(client_id: str) -> str:
    """
    Retrieve the full history of interactions with a given client ID.
    """
    # Retrieve the client history from the database




# => notification multi-canaux pour un nouveau ticket




# => sondage (1-10) note de traitement de ticket



tech_tool_list = [ticket_state,get_client_history] 