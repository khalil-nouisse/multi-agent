# Agent logic for tech support

# notification multi-canaux pour un nouveau ticket
# confirmation du traitement pour le client
# aussi pour la résolution, la clôture,
# sondage (1-10) note de traitement de ticket

# Agent logic for sales
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from config import llm
from tools.tech_tools import tech_tool_list 
from graph.agents_factory import create_agent

# Tools for the technical support agent
tools = tech_tool_list
tech_system_prompt = "you are ..."
tech_agent = create_agent(llm, tools, tech_system_prompt)
