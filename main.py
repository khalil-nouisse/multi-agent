from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from graph.graph_builder import build_graph
from langsmith1.tracing import get_callback_manager
from langsmith import traceable

@traceable(name="ActevaCRM")
def run_direct_user_input(user_input: str):
    graph = build_graph()
    callback_manager = get_callback_manager()
    
    input_data = {
        "messages": [HumanMessage(content=user_input)],
        "next": "supervisor"
    }
    
    result = graph.invoke(input_data, config={"callbacks": callback_manager})
    display_conversation(result["messages"])

def display_conversation(messages):
    shown = set()
    for msg in messages:
        sender = getattr(msg, "name", "user")
        key = (sender, msg.content)
        if key in shown:
            continue
        shown.add(key)
        print(f"{sender}: {msg.content}")

if __name__ == "__main__":
    # Simulating API input for now; this will be replaced later with Flask or FastAPI route
    user_input = "Hello there! help me make a coffee"
    run_direct_user_input(user_input)
