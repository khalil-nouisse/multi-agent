# Main entry point to run the LangGraph
from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_models import ChatOpenAI
from graph.graph_builder import build_graph
from langsmith1.tracing import get_callback_manager


def main():

    graph = build_graph()
    input_data = {
        "input": "Hello there, how are you",
        #"chat_history": []
    }

    callback_manager = get_callback_manager()

    result = graph.invoke(input_data, config={"callbacks": callback_manager})

    print("\n✅ Final Result:\n", result)


if __name__ == "__main__" :  
    main()

