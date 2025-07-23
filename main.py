# Main entry point to run the LangGraph

from graph.graph_builder import build_graph
from langsmith1.tracing import get_callback_manager
def main():
    graph = build_graph()
    input_data = {
        "input": "A customer wants to know why their subscription was canceled.",
        #"chat_history": []
    }

    callback_manager = get_callback_manager()

    result = graph.invoke(input_data, config={"callbacks": callback_manager})

    print("\n✅ Final Result:\n", result)


if __name__ == "__main__" :  
    main()

