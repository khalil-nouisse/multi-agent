#Enum for structured event types (optional)
from enum import Enum

class EventType(Enum):
    # technical support events
    TICKET_CREATE = "ticket create"
    TICKET_STATE_UPDATE = "ticket state update"
    TICKET_UPDATE = "ticket update"
    TICKET_DELETE = "ticket delete"
    TICKET_CLOSE = "ticket close"
    TICKET_RESOLUTION_ESTIMATION = "Estimate resolution time"

    # sales manager events
    OPPORTUNITY_CREATE = "opportunity create"
    OPPORTUNITY_STATE_UPDATE = "opportunity state update"
    OPPORTUNITY_RESOLVE = "opportunity resolve"
    OPPORTUNITY_UPDATE = "opportunity update"
    OPPORTUNITY_LOST = "opportunity_lost"
    OPPORTUNITY_DELETE = "opportunity delete"

    # customer support events
    CUSTOMER_UPDATE = "customer_update"

# Define the lists after the Enum is created
QUEUE_TECH_SUPPORT_EVENTS = [EventType.TICKET_CREATE, EventType.TICKET_STATE_UPDATE, EventType.TICKET_UPDATE, EventType.TICKET_DELETE, EventType.TICKET_CLOSE]
QUEUE_SALES_MANAGER_EVENTS = [EventType.OPPORTUNITY_CREATE, EventType.OPPORTUNITY_STATE_UPDATE, EventType.OPPORTUNITY_RESOLVE, EventType.OPPORTUNITY_UPDATE, EventType.OPPORTUNITY_LOST, EventType.OPPORTUNITY_DELETE]

# Communication Type Constants
class CommunicationType(Enum):
    ASYNC_QUEUE = "async_queue"    # Redis queue with structured data
    DIRECT_API = "direct_api"      # Direct API calls with natural language


class Status(Enum) :
    #ticket status in database
    TICKET_OPEN = "OPEN"
    TICKET_PROGRESS = "IN_PROGRESS"
    TICKET_RESOLVED = "RESOLVED"
    TICKET_CLOSED = "CLOSED"

    #opportunity status in database
    OPPORTUNITY_PROSPECTION = "PROSPECTION"
    OPPORTUNITY_DEMONSTRATION = "DEMONSTRATION"
    OPPORTUNITY_PROPOSITION = "PROPOSITION"
    OPPORTUNITY_NEGOCIATION = "NEGOCIATION"
    OPPORTUNITY_CONTRAT = "CONTRAT"
    OPPORTUNITY_PERDU = "PERDU"