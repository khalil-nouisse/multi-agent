# LangGraph setup and conditional routing

import operator
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
import functools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from langchain_core.messages import BaseMessage

#load agents
from agents.sales import sales_agent
from agents.customer import customer_agent
from agents.tech_support import tech_support_agent
from agents.supervisor import supervisor_chain

from graph.agents_factory import agent_node

# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

# class AgentState(TypedDict):
#     # Message history with auto-append
#     messages: Annotated[List[BaseMessage], operator.add]
    
#     # Routing and flow control
#     next: str
#     current_agent: str
    
#     # Shared context between agents
#     context: Dict[str, Any]
    
#     # Track conversation metadata
#     conversation_id: str
#     user_intent: Optional[str]
    
#     # Agent-specific data storage
#     customer_data: Dict[str, Any]
#     sales_data: Dict[str, Any]
#     tech_support_data: Dict[str, Any]
    
#     # Flow control
#     retry_count: int
#    max_retries: int




def build_graph() -> Runnable:

    #create graph nodes
    customer_node = functools.partial(agent_node, agent=customer_agent, name="customer_support")
    sales_node = functools.partial(agent_node, agent=sales_agent, name="sales_manager")
    tech_node = functools.partial(agent_node, agent=tech_support_agent, name="tachnical_support")

    #build the graoh
    workflow = StateGraph(AgentState)
    
    #graph entry
    workflow.set_entry_point("supervisor")

    #add nodes to the graph
    workflow.add_node("supervisor",supervisor_chain)
    workflow.add_node("customer_support", customer_node)
    workflow.add_node("sales_manager", sales_node)
    workflow.add_node("tachnical_support", tech_node)

    agents = ["customer_support" ,"sales_manager" ,"tachnical_support"]


    #add adges to the graph
    for member in agents :
        workflow.add_edge(member, "supervisor")

    # The supervisor populates the "next" field in the graph state
    # which routes to a node or finishes
    conditional_map = {k: k for k in agents}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)

    graph = workflow.compile()

    return graph