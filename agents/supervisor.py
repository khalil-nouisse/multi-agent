# LLM-based agent that routes the message
#It will use function calling to choose the next worker node OR finish processing.

from langchain_core.output_parsers import JsonOutputKeyToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.output_parsers import JsonOutputToolsParser
from config import llm 
import json

#name of the nodes of the graph (that represents the agents)
members = ["customer_support", "sales_manager" , "tachnical_support"]
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the following workers: {members}. "
    "Given the following user request, you must always respond by calling the 'route' function. "
    "If the user's request is a general question, greeting, or something you can answer directly, provide the answer in the 'answer' field and set 'next' to 'FINISH'. "
    "If the request is about sales, customer support, or technical support, set 'answer' to an empty string and select the next agent in the 'next' field. "
    "Never answer directly in text; always use the function call."
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
        ("system", system_prompt),
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
# This supervisor chain is the one that will be used to generate the next node . the LLM will output something like:
# {
#     "next": "sales_manager",
# }
# and the JsonOutputFunctionsParser will turn it into a python dict : {"next": "sales_manager"}

def supervisor_node(state):
    # Get the raw LLM output
    raw_chain = prompt | llm.bind(functions=[function_def], function_call={"name": "route"})
    raw_output = raw_chain.invoke(state)
    #print("Raw LLM output:", raw_output)
    function_call = raw_output.additional_kwargs.get("function_call")
    next_value = None
    answer = None
    if function_call and "arguments" in function_call:
        args = json.loads(function_call["arguments"])
        next_value = args.get("next")
        answer = args.get("answer")
    print("Supervisor chose next:", next_value, "answer:", answer)
    valid_options = ["customer_support", "sales_manager", "tachnical_support", "FINISH"]
    if answer and answer.strip():
        messages = list(state["messages"]) + [
            type(state["messages"][0])(content=answer, name="supervisor")
        ]
        return {**state, "messages": messages, "next": "FINISH"}
    if next_value not in valid_options:
        print("Invalid next value from supervisor:", next_value)
        next_value = "FINISH"
    return {**state, "next": next_value}