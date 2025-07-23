# LangSmith integration (run tracing & evaluation)
from langsmith import traceable
from graph.graph_builder import build_graph

input_data = f""""customer_input": "I have a question about my delivery",
    "sales_input": "New prospect interested in CRM",
    "supervisor_input": "Review escalation case #782,"
    "tech_input": "Opportunity ticket: Issue with integration"""


@traceable(name="main_graph_run")
def run_graph():
    graph = build_graph()  # your graph_builder code
    return graph.invoke(input_data)



import os
from langchain.callbacks.tracers import LangChainTracer
from langchain_core.tracers import ConsoleCallbackHandler
from langchain_core.callbacks import CallbackManager
from config import LANGCHAIN_PROJECT
def get_callback_manager():
    # Ensure environment variables are set
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
    os.environ["LANGCHAIN_API_KEY"] = "your_langsmith_api_key"  # <-- or load from .env

    tracer = LangChainTracer(project_name=LANGCHAIN_PROJECT)
    console = ConsoleCallbackHandler()

    return CallbackManager([tracer, console])