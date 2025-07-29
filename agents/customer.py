# Agent for customer service
#
# => Confirmation of processing of the request
# => sending the progress status of processing requests

from typing import Annotated, List, Tuple, Union
from langchain.tools import BaseTool, StructuredTool, Tool
from tools.customer_tools import customer_tool_list
from config import llm
from graph.agents_factory import create_agent

tools = customer_tool_list
customer_system_prompt = ("Role : Customer support agent"
                          "Objective : ")

customer_agent = create_agent(llm, tools, customer_system_prompt)
