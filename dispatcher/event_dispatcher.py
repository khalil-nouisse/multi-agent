# communication/event_dispatcher.py

from langchain_core.messages import HumanMessage
from event_types import EventType, CommunicationType
from communication.email.email_agent import email_agent # Import the new email agent

class EventDispatcher:
    def __init__(self, graph):
        self.graph = graph
        self.email_agent = email_agent # Use the instantiated email agent
        self.routes = {
            # Each event now maps to a list of handlers : agents rooting and email rooting
            EventType.TICKET_CREATE: [self.handle_ticket_create_agent, self.handle_email_notification],
            EventType.TICKET_STATE_UPDATE: [self.handle_ticket_state_update_agent, self.handle_email_notification],
            EventType.TICKET_UPDATE: [self.handle_ticket_update_agentm, self.handle_email_notification ],
            EventType.TICKET_CLOSE: [self.handle_ticket_close_agent, self.handle_email_notification],
            EventType.TICKET_DELETE: [self.handle_ticket_delete_agentm, self.handle_email_notification],

            EventType.OPPORTUNITY_CREATE: [self.handle_opportunity_create_agent, self.handle_email_notification],
            EventType.OPPORTUNITY_STATE_UPDATE: [self.handle_opportunity_state_update_agent, self.handle_email_notification],
            EventType.OPPORTUNITY_UPDATE: [self.handle_opportunity_update_agent, self.handle_email_notification],
            EventType.OPPORTUNITY_RESOLVE: [self.handle_opportunity_resolve_agent, self.handle_email_notification],
            EventType.OPPORTUNITY_LOST :  [self.handle_opportunity_lost_agent, self.handle_email_notification],
            EventType.OPPORTUNITY_DELETE: [self.handle_opportunity_delete_agentm, self.handle_email_notification],

            #EventType.CUSTOMER_UPDATE: [self.handle_customer_update_agent],
        }
        self.communication_type = CommunicationType

    def dispatch(self, event_type, payload):
        handlers = self.routes.get(event_type, [self.handle_default])
        for handler in handlers:
            handler(event_type, payload) # Pass event_type to handlers

    #email handler
    def handle_email_notification(self, event_type, payload):
        self.email_agent.send_notification(event_type, payload)


    # --- Agent-specific handlers  ---
    #technical support rooting
    def handle_ticket_create_agent(self, event_type, payload):
        # ... your existing logic for invoking the technical_support graph
        print("[Dispatch] Ticket created:", payload)
        message = payload.get("message", "New ticket created.")
        return self.graph.invoke({
            "messages": [HumanMessage(content=message)],
            "next": "technical_support",
            "communication_type": self.communication_type,
            "event_type": event_type
        })
    
    def handle_ticket_update_agent(self ,event_type, payload):
        print("[Dispatch] Ticket updated", payload)
        message = payload.get("message" , "Ticket updated.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })
    
    def handle_ticket_state_update_agent(self ,event_type, payload):
        print("[Dispatch] Ticket state updated", payload)
        message = payload.get("message" , "Ticket state updated.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })    

    def handle_ticket_close_agent(self ,event_type, payload):
        print("[Dispatch] Ticket closed", payload)
        message = payload.get("message" , "Ticket closed.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })    

    def handle_ticket_delete_agent(self ,event_type, payload):
        print("[Dispatch] Ticket deleted", payload)
        message = payload.get("message" , "Ticket deleted.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })    
    

    #sales manager rooting
    def handle_opportunity_create_agent(self ,event_type, payload):
        print("[Dispatch] opportunity deleted", payload)
        message = payload.get("message" , "opportunity deleted.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })      


    def handle_opportunity_state_update_agent(self ,event_type, payload):
        print("[Dispatch] opportunity state updated", payload)
        message = payload.get("message" , "opportunity state updated.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })   
    
    def handle_opportunity_update_agent(self ,event_type, payload):
        print("[Dispatch] opportunity updated", payload)
        message = payload.get("message" , "opportunity updated.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })         

    def handle_opportunity_resolve_agent(self ,event_type, payload):
        print("[Dispatch] opportunity resolved", payload)
        message = payload.get("message" , "opportunity resolved.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })      

    def handle_opportunity_lost_agent(self ,event_type, payload):
        print("[Dispatch] opportunity lost", payload)
        message = payload.get("message" , "opportunity lost.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })     
    
    def handle_opportunity_delete_agent(self ,event_type, payload):
        print("[Dispatch] opportunity deleted", payload)
        message = payload.get("message" , "opportunity deleted.")
        return self.graph.invoke({
            "message" : [HumanMessage(content=message)],
            "next" : "technical_support",
            "communication" : self.communication_type,
            "event_type" : event_type
        })      



    def handle_default(self, event_type, payload):
        print(f"[Dispatch] Unknown event type: {event_type}")
        return {"error": "Unknown event type"}