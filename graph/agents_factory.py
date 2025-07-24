from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langsmith import traceable
from langsmith1.tracing import get_callback_manager,LangChainTracer
from config import LANGCHAIN_PROJECT


@traceable(name="create_agent")
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
    callback_manager = get_callback_manager()
    executor = AgentExecutor(agent=agent,
                             tools=tools,
                             callback_manager=callback_manager
                             )
    return executor

# agent node
def agent_node(state, agent, name):
    
    result = agent.invoke(state)

    output = result.get("output")
    if not isinstance(output, str):
        output = "Sorry, I couldn’t generate a response."

    return {"messages": [HumanMessage(content=output, name=name)]}
