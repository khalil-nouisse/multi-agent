# Tools/functions for tech support agent

from typing import Annotated, List, Tuple, Union
from langchain.tools import BaseTool, StructuredTool, Tool
from langchain_core.tools import tool
from databse import get_status

# => confirmation du traitement pour le client

@tool("Opportunity", return_direct=False)
def opportunity_state(title: str):
    state = get_status(title , "Opportunity")
    return state

# => notification multi-canaux pour un nouveau ticket




# => sondage (1-10) note de traitement de ticket



tech_tool_list = [opportunity_state] 