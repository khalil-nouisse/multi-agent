from langchain_core.messages import HumanMessage
from event_types import EventType , CommunicationType
class EventDispatcher:
    def __init__(self, graph):
        self.graph = graph
        self.routes = {
            #techical support events
            EventType.TICKET_CREATE : self.handle_ticket_create,
            EventType.TICKET_STATE_UPDATE : self.handle_ticket_state_update,
            EventType.TICKET_UPDATE : self.handle_ticket_update,
            EventType.TICKET_DELETE : self.handle_ticket_delete,
            EventType.TICKET_CLOSE : self.handle_ticket_close,
            
            #sales manager events
            EventType.OPPORTUNITY_CREATE : self.handle_opportunity_create,
            EventType.OPPORTUNITY_STATE_UPDATE : self.handle_opportunity_state_update,
            EventType.OPPORTUNITY_UPDATE : self.handle_opportunity_update,
            EventType.OPPORTUNITY_RESOLVE : self.handle_opportunity_resolve,
            EventType.OPPORTUNITY_DELETE : self.handle_opportunity_delete,

            #costumer support events
            EventType.CUSTOMER_UPDATE : self.handle_customer_update,    
        }
        self.communication_type = CommunicationType

    def dispatch(self, event_type, payload):
        #this searchs for the right function to call based on the event type
        handler = self.routes.get(event_type, self.handle_default)
        return handler(payload)   #call the function chosen whith the content
    
    #technical support Rooting
    def handle_ticket_create(self, payload):

        print("[Dispatch] Ticket created:", payload)

        #Extract message from payload, with fallback
        message = payload.get("message", "New ticket created.")

        #Invoke a graph/workflow system , Safely extracts the "message" field from the payload dictionary ,If "message" doesn't exist, uses "New ticket created." as default
        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "technical_support",
            "communication_type" : self.communication_type
        })

    def handle_ticket_state_update(self, payload):

        print("[Dispatch] Ticket state update:", payload)

        message = payload.get("message", "ticket state updated.")

        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "technical_support",
            "communication_type" : self.communication_type
        }) 

    def handle_ticket_update(self, payload):

        print("[Dispatch] Ticket update:", payload)

        message = payload.get("message", "ticket updated.")

        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "technical_support",
            "communication_type" : self.communication_type
        }) 

    def handle_ticket_close(self, payload):

        print("[Dispatch] Ticket closed:", payload)

        message = payload.get("message", "ticket closed.")

        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "technical_support",
            "communication_type" : self.communication_type
        })
    
    def handle_ticket_delete(self, payload):

        print("[Dispatch] Ticket deleted:", payload)

        #Extract message from payload, with fallback
        message = payload.get("message", "ticket deleted.")

        #Invoke a graph/workflow system , Safely extracts the "message" field from the payload dictionary ,If "message" doesn't exist, uses "New ticket created." as default
        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "technical_support",
            "communication_type" : self.communication_type
        })                  


    #sales_Agent Rooting
    def handle_opportunity_create(self , payload):

        print("[Dispatch] Opportunity Created:", payload)

        message = payload.get("message", "New opportunity created")
    
        return self.graph.invoke({
            "message": [HumanMessage(content=message)],
            "next": "sales_manager",
            "communication_type" : self.communication_type
        })
    
    def handle_opportunity_state_update(self , payload):

        print("[Dispatch] opportunity state updated:", payload)

        message = payload.get("message", "opportunity state update")

        return self.graph.invoke({
            "message": [HumanMessage(content=message)],
            "next": "sales_manager",
            "communication_type" : self.communication_type
        })
    
    def handle_opportunity_update(self , payload):

        print("[Dispatch] opportunity updated:", payload)

        message = payload.get("message", "opportunity update")

        return self.graph.invoke({
            "message": [HumanMessage(content=message)],
            "next": "sales_manager",
            "communication_type" : self.communication_type
        })

    def handle_opportunity_resolve(self , payload):

        print("[Dispatch] opportunity resolved:", payload)

        message = payload.get("message", "opportunity resolved")

        return self.graph.invoke({
            "message": [HumanMessage(content=message)],
            "next": "sales_manager",
            "communication_type" : self.communication_type
        })

    def handle_opportunity_delete(self , payload):

        print("[Dispatch] opportunity delted:", payload)

        message = payload.get("message", "opportunity delete")

        return self.graph.invoke({
            "message": [HumanMessage(content=message)],
            "next": "sales_manager",
            "communication_type" : self.communication_type
        })    
    

    # Customer support Rooting
    def handle_customer_update(self, payload):
        print("[Dispatch] Customer updated:", payload)
        message = f"Customer update: {payload.get('info', str(payload))}"
        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "sales_manager",
            "communication_type" : self.communication_type
        })
    

    #default handler
    def handle_default(self, payload):
        print("[Dispatch] Unknown event type")
        return {"error": "Unknown event type"}
