# Tools/functions for sales agent
from databse import get_status
from langchain_core.tools import tool

#State opportunity confirmation 

@tool("Opportunity", return_direct=False)
def opportunity_state(title: str):
    state = get_status(title , "Opportunity")
    return state



#appointment reminder (raapel du rdv) automated script that runs in the database and check the date of appointemnts


sales_tool_list = [opportunity_state] 