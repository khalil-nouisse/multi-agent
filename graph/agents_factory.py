from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from config import LANGCHAIN_PROJECT


def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    # Each worker node will be given a name and some tools.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

# agent node
# #handle the NOT_ME response :
# return {
#     "status": "NOT_ME",
#     "reason": "The request relates to appointment reminders, which I don't handle.",
#     "agent": "sales_manager"
# }

def agent_node(state, agent, name):
    result = agent.invoke(state)
    output = result.get("output")
    if not isinstance(output, str):
        output = "Sorry, I couldn’t generate a response."
    # Append the new message to the existing messages
    messages = list(state["messages"]) + [HumanMessage(content=output, name=name)]
    return {**state, "messages": messages}
