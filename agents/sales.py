# Agent logic for sales
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from config import llm
from tools.sales_tools import sales_tool_list 
from graph.agents_factory import create_agent

tools = sales_tool_list
sales_system_prompt = "you are ..."
sales_agent = create_agent(llm, tools, sales_system_prompt)
