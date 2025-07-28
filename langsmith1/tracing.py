# LangSmith integration (run tracing & evaluation)
from dotenv import load_dotenv
import os
from langsmith import Client
load_dotenv()
from langsmith import traceable
from langchain.callbacks.tracers import LangChainTracer
from langchain_core.tracers import ConsoleCallbackHandler
from langchain_core.callbacks import CallbackManager
from config import LANGCHAIN_PROJECT
from langsmith import Client as LangSmithClient

def get_callback_manager():

    #tracer = LangChainTracer(project_name=LANGCHAIN_PROJECT)
    tracer = LangChainTracer(
        project_name=os.getenv("LANGCHAIN_PROJECT"),
        client=LangSmithClient(
            #api_url=os.getenv("LANGCHAIN_ENDPOINT"),
            api_key=os.getenv("LANGCHAIN_API_KEY")
        )
    )
    console = ConsoleCallbackHandler()

    return CallbackManager([tracer, console])