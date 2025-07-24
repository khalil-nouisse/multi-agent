from langchain_core.tools import tool

# Tools/functions for supervisor agent
@tool("ClientHistory", return_direct=True)
def get_client_history(client_id: str) -> str:
    """
    Retrieve the full history of interactions with a given client ID.
    """
    # Retrieve the client history from the database