# Main entry point to run the LangGraph
from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_models import ChatOpenAI
from graph.graph_builder import build_graph
from langsmith1.tracing import get_callback_manager
from langchain_core.messages import HumanMessage

def main():

    graph = build_graph()
    input_data = {
        "messages": [HumanMessage(content="i need help from the technical support agent ! i need to know the state of my ticket with title : ticket123")],
        "next": "supervisor"
    }

    callback_manager = get_callback_manager()

    result = graph.invoke(input_data, config={"callbacks": callback_manager})

    #print("\n✅ Final Result:\n", result)
    final_message = result["messages"][-1]
    print("Agent:", final_message.content)


if __name__ == "__main__" :  
    main()

