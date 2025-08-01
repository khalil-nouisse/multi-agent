#Entry point for Redis Queue events.
import json
from rq.decorators import job
from redis import Redis
from graph.graph_builder import build_graph
from dispatcher.event_dispatcher import EventDispatcher

redis_conn = Redis()

@job('default', connection=redis_conn, timeout=600)

#Receives event_type and payload_json
def process_event(event_type, payload_json):
    try:
        #Converts the payload string into a Python dictionary.
        payload = json.loads(payload_json)
    except json.JSONDecodeError:
        print("Invalid JSON payload")
        return {"error": "Invalid JSON payload"}

    graph = build_graph()
    dispatcher = EventDispatcher(graph)
    # the dispatcher route the event to the correct langGraph node
    result = dispatcher.dispatch(event_type, payload)

    print("Event handled. Output:\n", result)

if __name__ == "__main__":
    process_event()
