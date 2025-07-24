# Tools/functions for sales agent
from databse import get_status
from langchain_core.tools import tool

#State opportunity confirmation 

@tool("Opportunity", return_direct=False)
def opportunity_state(title: str):
    """Provide information about the state of the opportunity of the client from the database."""
    state = get_status(title , "Opportunity")
    return state

@tool("ClientHistory", return_direct=True)
def get_client_history(client_id: str) -> str:
    """
    Retrieve the full history of interactions with a given client ID.
    """
    # Retrieve the client history from the database

#appointment reminder (raapel du rdv) automated script that runs in the database and check the date of appointemnts


sales_tool_list = [opportunity_state,get_client_history] 