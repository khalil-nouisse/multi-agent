from langchain_core.messages import HumanMessage
from event_types import EventType
class EventDispatcher:
    def __init__(self, graph):
        self.graph = graph
        self.routes = {
            EventType.TICKET_CREATED : self.handle_ticket_created,
            EventType.CUSTOMER_UPDATE : self.handle_customer_update,
        }

    def dispatch(self, event_type, payload):
        #this searchs for the right function to call based on the event type
        handler = self.routes.get(event_type, self.handle_default)
        return handler(payload)   #call the function chosen whith the content

    def handle_ticket_created(self, payload):
        print("[Dispatch] Ticket created:", payload)
        message = payload.get("message", "New ticket created.")
        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "technical_support"
        })

    def handle_customer_update(self, payload):
        print("[Dispatch] Customer updated:", payload)
        message = f"Customer update: {payload.get('info', str(payload))}"
        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "sales_manager"
        })
    
    def handle_default(self, payload):
        print("[Dispatch] Unknown event type")
        return {"error": "Unknown event type"}
