# LLM-based agent that routes the message
#It will use function calling to choose the next worker node OR finish processing.

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import llm 

#name of the nodes of the graph (that represents the agents)
members = ["customer_support", "sales_manager" , "tachnical_support"]
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " following workers:  {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = ["FINISH"] + members
# Using openai function calling can make output parsing easier for us
function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {
            "next": {
                "title": "Next",
                "type": "string",
                "enum": options
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
    | llm.bind_tools(tools=[function_def], function_call="auto")
    | JsonOutputFunctionsParser()
)
# This supervisor chain is the one that will be used to generate the next node . the LLM will output something like:
# {
#     "next": "sales_manager",
# }
# and the JsonOutputFunctionsParser will turn it into a python dict : {"next": "sales_manager"}
