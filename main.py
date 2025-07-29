# Main entry point to run the LangGraph
from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_models import ChatOpenAI
from graph.graph_builder import build_graph
from langsmith1.tracing import get_callback_manager
from langchain_core.messages import HumanMessage
from langsmith import traceable

@traceable(name="ActevaCRM")
def main():
    graph = build_graph()
    input_data = {
        "messages": [HumanMessage(content="Hello there ! i need the help from the to know the state of my opportunity called : opportunity123")],
        "next": "supervisor"
    }
    callback_manager = get_callback_manager()
    result = graph.invoke(input_data, config={"callbacks": callback_manager})

    def display_conversation(messages):
        shown = set()
        for msg in messages:
            sender = getattr(msg, "name", "user")
            # Optionally skip duplicate messages
            key = (sender, msg.content)
            if key in shown:
                continue
            shown.add(key)
            print(f"{sender}: {msg.content}")

    
    display_conversation(result["messages"])

    # def show_last_exchange(messages):
    #     # Find the last agent message
    #     last_agent_msg = next((m for m in reversed(messages) if getattr(m, "name", None) and m.name != "user"), None)
    #     # Find the last user message before that
    #     last_user_msg = None
    #     if last_agent_msg:
    #         idx = messages.index(last_agent_msg)
    #         last_user_msg = next((m for m in reversed(messages[:idx]) if not getattr(m, "name", None)), None)
    #     if last_user_msg:
    #         print(f"User: {last_user_msg.content}")
    #     if last_agent_msg:
    #         print(f"{last_agent_msg.name}: {last_agent_msg.content}")
            
if __name__ == "__main__" :  
    main()