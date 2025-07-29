# LLM-based agent that routes the message
#It will use function calling to choose the next node or by answering OR finish processing.

from langchain_core.output_parsers import JsonOutputKeyToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.output_parsers import JsonOutputToolsParser
from agents.sales import sales_manager_responsability
from agents.tech_support import tech_support_responsability
from config import llm 
import json

#name of the nodes of the graph (that represents the agents)
members = ["customer_support", "sales_manager" , "technical_support"]

# system_prompt = (
#     f"You are a supervisor tasked with managing a conversation between the following workers: {','.join(members)}. "
#     "Given the following user request, you must always respond by calling the 'route' function. "
#     "If the user's request is a general question, greeting, or something you can answer directly, provide the answer in the 'answer' field and set 'next' to 'FINISH'. "
#     "If the request is about sales, customer support, or technical support, set 'answer' to an empty string and select the next agent in the 'next' field. "
#     "If the user goes off-topic, gently guide them back to the main objective.\n"
#     "Never answer directly in text; always use the function call."
# )
supervisor_system_prompt = (
    "Role: Conversation Supervisor\n"
    "Objective: Manage routing of user requests to the appropriate agent.\n"
    "Context: You are a high-level AI orchestrator coordinating between specialized agents: "
    f"{', '.join(members)}.\n"
    "Task:\n"
    "1. Receive user input from the conversation.\n"
    "2. If it's a general greeting, question, or you can handle it directly, answer in the 'answer' field and set 'next' to 'FINISH'.\n"
    "3. If it's about sales process, customer support, or technical support, set 'answer' to an empty string and choose the appropriate agent in 'next'.\n"
    "4. If the request is off-topic, respond with a short polite message and set 'next' to 'FINISH'.\n\n"
    "Routing Guidelines:\n"
    "To determine which agent to route the request to, use the following logic:\n"
    f"- If the request is about {','.join(sales_manager_responsability)}, route to 'sales'.\n"
    #"- If the request is about account help, user satisfaction, , or non-technical issues, route to 'customer_support'.\n"
    f"- If the request is about {','.join(tech_support_responsability)}, route to 'tech_support'.\n"
    "Always use the `route` function with `answer=''` and `next='<agent_name>'`.\n"
    "If unsure, choose the most appropriate based on the keywords, and let the agent clarify.\n"
    "Examples:"
    "I want to create a new opportunity → sales"
    #"I can't access my account → customer_support "
    "i need to know the state of my ticket : id=1 → technical_support"
    "Communication Guidelines:\n"
    "- Never respond directly in plain text — always use the `route` function.\n"
    "- Your goal is to streamline the conversation and ensure user queries are handled by the correct agent.\n"
    "- If unsure, choose the most likely agent and let them ask for clarification.\n"
)

# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["FINISH"] + members
# Using openai function calling can make output parsing easier for us
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

# The actual chain that will be used by the graph
supervisor_chain = (
    prompt
    | llm.bind(functions=[function_def], function_call={"name": "route"})
    | JsonOutputToolsParser()
)


def supervisor_node(state):
    # Count how many agents have responded with "NOT_ME"
    not_me_count = 0
    for msg in state["messages"]:
        if hasattr(msg, 'name') and msg.name in {"customer_support", "sales_manager", "technical_support"} and msg.content == "NOT_ME":
            not_me_count += 1
    
    # If all agents have responded with "NOT_ME", provide final response
    if not_me_count >= 3:
        return {**state, "next": "FINISH", "messages": state["messages"] + [
            type(state["messages"][0])(content="I'm sorry, but your request is outside the scope of our available services. We can help with sales processes, customer support, and technical support for our products, but we cannot assist with general coding or programming tasks. Please contact a software development specialist for coding assistance.", name="supervisor")
        ]}
    
    # Get the raw LLM output
    raw_chain = prompt | llm.bind(functions=[function_def], function_call={"name": "route"})
    
    # Truncate conversation history if it gets too long (keep last 5 messages)
    if len(state["messages"]) > 5:
        state["messages"] = state["messages"][-5:]
    
    raw_output = raw_chain.invoke(state)
    function_call = raw_output.additional_kwargs.get("function_call")

    if not function_call or "arguments" not in function_call:
        # Invalid output
        return {**state, "next": "FINISH", "messages": state["messages"] + [
            type(state["messages"][0])(content="Sorry, I couldn't understand the request.", name="supervisor")
        ]}
    
    args = json.loads(function_call["arguments"])
    next_value = args.get("next")
    answer = args.get("answer", "").strip()
    
    print(f"[Supervisor] Next: {next_value}, Answer: {answer or 'N/A'}, NOT_ME count: {not_me_count}")

    # If the supervisor wants to answer directly
    if answer and answer.strip():
        messages = list(state["messages"]) + [
            type(state["messages"][0])(content=answer, name="supervisor")
        ]
        return {**state, "messages": messages, "next": "FINISH"}

    # Route to the next agent
    if next_value not in {"customer_support", "sales_manager", "technical_support"} and next_value != "FINISH":
        print("Invalid next value from supervisor:", next_value)
        next_value = "FINISH"

    messages = list(state["messages"])
    return {**state, "next": next_value, "messages": messages}
   

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
