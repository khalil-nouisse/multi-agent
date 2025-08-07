# agents/supervisor.py
# LLM-based agent orchestrator
# It will use function calling to choose the next node or by answering OR finish processing.

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputToolsParser
from agents.sales import sales_manager_responsability
from agents.tech_support import tech_support_responsability
from event_types import CommunicationType
from config import llm
import json

#system agents
members = ["customer_support", "sales_manager", "technical_support", "diagnostic_agent"]

supervisor_system_prompt = (
    "Role: Conversation Supervisor\n"
    "Objective: Manage routing of user requests to the appropriate agent or answer directly.\n"
    "Context: You are a high-level AI orchestrator coordinating between specialized agents: "
    f"{', '.join(members)}.\n"
    "Task:\n"
    "1. Receive the latest message from the conversation.\n"
    "2. If the message is a general greeting, question, or can be handled directly, answer in the 'answer' field and set 'next' to 'FINISH'.\n"
    "3. If the message is a request for a specialist, choose the appropriate agent in 'next' and leave 'answer' blank.\n"
    "4. If the message comes from another agent and contains a routing instruction (e.g., 'next: diagnostic_agent'), follow that instruction precisely.\n"
    "5. If a previous agent responded with 'NOT_ME', you must re-evaluate the conversation and route the request to a different, more appropriate agent.\n"
    "6. If the request is off-topic, respond with a short polite message in 'answer' and set 'next' to 'FINISH'.\n\n"
    "Routing Guidelines:\n"
    "To determine which agent to route the request to, use the following logic:\n"
    "- If the request is about sales opportunities, quotes, or appointments, route to 'sales_manager'.\n"
    "- If the request is about tickets ,managing or getting the status of technical support tickets (e.g., 'what is the status of my ticket'), route to 'technical_support'.\n"
    "- If the request is for general customer assistance, route to 'customer_support'.\n"
    "Always use the `route` function with `answer` and `next` fields.\n"
    "If a message from a user or another agent is unclear, choose the most likely agent and let them ask for clarification.\n\n"
    "Examples:"
    "User: I want to create a new opportunity → 'next': 'sales_manager', 'answer': ''"
    "User: I need to know the state of my ticket: id=1 → 'next': 'technical_support', 'answer': ''"
    "Tech_Support: I have a complex problem that needs diagnosis → 'next': 'diagnostic_agent', 'answer': ''"
    "User: I can't access my account → 'next': 'customer_support', 'answer': ''"
    "User: What's the weather today? → 'next': 'FINISH', 'answer': 'I am sorry, but I can only assist with topics related to our services. For weather information, please use a dedicated weather application.'"
    "Customer_Support: NOT_ME, the request is about a technical issue. → 'next': 'technical_support', 'answer': ''"
    "Communication Guidelines:\n"
    "- Never respond directly in plain text — always use the `route` function.\n"
    "- Your goal is to streamline the conversation and ensure user queries are handled by the correct agent.\n"
)

# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["FINISH"] + members
# Using openai function calling for output parsing
function_def = {
    "name": "route",
    "description": "Select the next role or answer directly.",
    "parameters": {
        "type": "object",
        "properties": {
            "next": {
                "type": "string",
                "enum": options
            },
            "answer": {
                "type": "string",
                "description": "If you want to answer the user directly, provide the answer here. Otherwise, leave blank."
            }
        },
        "required": ["next"],
    },
}

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", supervisor_system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next?"
            " Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options), members=", ".join(members))

# chain that will be used by the graph
supervisor_chain = (
    prompt
    | llm.bind(functions=[function_def], function_call={"name": "route"})
    | JsonOutputToolsParser()
)

def supervisor_node(state):
    # Check if the last message is from an agent with a routing instruction (eg : tech_support --> diagnostic_agent)
    last_message = state["messages"][-1]
    if hasattr(last_message, "name") and last_message.name in members:
        if "next: diagnostic_agent" in last_message.content.lower():
            print("[Supervisor] Routing to Diagnostic Agent based on agent instruction.")
            return {**state, "next": "diagnostic_agent"}
    
    # to prevent infinite loops: check if all agents have said NOT_ME
    # This is a fallback to gracefully end the conversation if no one can help
    not_me_count = sum(1 for msg in state["messages"] if hasattr(msg, 'name') and msg.name in members and msg.content == "NOT_ME")
    if not_me_count >= len(members): 
        return {**state, "next": "FINISH", "messages": state["messages"] + [
            type(state["messages"][0])(content="I'm sorry, but your request is outside the scope of our available services.", name="supervisor")
        ]}
    
    # Get the raw LLM output for normal routing
    raw_chain = prompt | llm.bind(functions=[function_def], function_call={"name": "route"})
    
    # Truncate conversation history if it gets too long (keep last 5 messages)
    message_history = 5
    if len(state["messages"]) > message_history:
        state["messages"] = state["messages"][-message_history:]
    
    raw_output = raw_chain.invoke(state)
    function_call = raw_output.additional_kwargs.get("function_call")

    if not function_call or "arguments" not in function_call:
        # Invalid output from LLM, respond politely and finish
        return {**state, "next": "FINISH", "messages": state["messages"] + [
            type(state["messages"][0])(content="Sorry, I couldn't understand the request.", name="supervisor")
        ]}
    
    args = json.loads(function_call["arguments"])
    next_value = args.get("next")
    answer = args.get("answer", "").strip()
    
    print(f"[Supervisor] Next: {next_value}, Answer: {answer or 'N/A'}")

    # If the supervisor wants to answer directly
    if answer:
        messages = list(state["messages"]) + [
            type(state["messages"][0])(content=answer, name="supervisor")
        ]
        return {**state, "messages": messages, "next": "FINISH"}

    # Route to the next agent
    messages = list(state["messages"])
    return {**state, "next": next_value, "messages": messages , "communication_type" : CommunicationType.DIRECT_API}
# This function is the one that will be used to generate the next node or the answer. the LLM will output something like:
# {
#     "next": "sales_manager",
#     "answer" : ""
# }

# or

# {
#     "next": "FINISH",
#     "answer" : "hello there !..."
# }
