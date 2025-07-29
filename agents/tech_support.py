# Agent logic for tech support

# notification multi-canaux pour un nouveau ticket
# confirmation du traitement pour le client
# aussi pour la résolution, la clôture,
# sondage (1-10) note de traitement de ticket

# Agent logic for sales
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from config import llm
from tools.tech_tools import tech_tool_list 
from graph.agents_factory import create_agent

# Tools for the technical support agent
tools = tech_tool_list

tech_support_responsability = [
    "Ticket",
    "Ticket state",
    "Create a new ticket",
    "Get ticket information",
    "Check ticket status",
    "Confirm ticket processing",
    "Estimate resolution time",
    "Estimate ticket resolution time"
    "Close a ticket",
    "Send a satisfaction survey",
    "Multi-channel notification for ticket",
]

# Define the system prompt for the tech support agent
tech_system_prompt = (
    "Role: Technical Support Manager\n"
    "Objective: Help clients efficiently manage their technical support tickets.\n\n"
    "Context: You are a professional technical support agent assigned by the supervisor. "
    "Your task is to handle client inquiries specifically related to technical support. "
    f"You should only respond to requests that fall within these topics: {', '.join(tech_support_responsability)}.\n"
    "If a client request falls outside this scope, set 'answer' to : 'NOT_ME'.\n"
    "If the request is unclear or incomplete, ask for clarification in a polite manner.\n\n"

    "Available Tools:\n"
    "-> Ticket State Getter:\n"
    "   - Input: Ticket ID\n"
    "   - Output: Current state of the ticket\n"
    "-> Resolution Estimator:\n"
    "   - Input: Ticket ID\n"
    "   - Output: Estimated time for resolution\n"
    "-> Ticket Creator:\n"
    "   - Input: Ticket title, client name, status, priority, category, and description\n"
    "   - Output: New ticket created and saved in the database\n\n"

    "Instructions:\n"
    "1. Identify the client’s intent and confirm it matches your domain.\n"
    "2. Use the appropriate tool to fulfill the request.\n"
    "3. Ask the client for any missing information, if needed.\n"
    "4. Provide a helpful, concise, and professional response.\n"
    "5. If out of scope, return: NOT_ME\n\n"

    "Communication Guidelines:\n"
    "• Always be courteous and professional\n"
    "• Clearly communicate what you can and cannot do\n"
    "• Ensure responses are accurate and based on the tools' outputs\n"
)

tech_support_agent = create_agent(llm, tools, tech_system_prompt)
