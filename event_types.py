#Enum for structured event types (optional)
from enum import Enum

class EventType(Enum):
    #technical support events
    TICKET_CREATE = "ticket create"
    TICKET_STATE_UPDATE = "ticket state update"
    TICKET_UPDATE = "ticket update"
    TICKET_DELETE = "ticket delete"
    TICKET_CLOSE = "ticket close"
    TICKET_RESOLUTION_ESTIMATION = "Estimate resolution time"

    #sales manager events
    OPPORTUNITY_CREATE = "opportunity create"
    OPPORTUNITY_STATE_UPDATE = "opportunity state update"
    OPPORTUNITY_RESOLVE = "opportunity resolve"
    OPPORTUNITY_UPDATE = "opportunity update"
    OPPORTUNITY_LOST = "opportunity_lost"
    OPPORTUNITY_DELETE = "opportunity delete"

    #customer support events
    CUSTOMER_UPDATE = "customer_update"

    QUEUE_TECH_SUPPORT_EVENTS = [TICKET_CREATE ,TICKET_STATE_UPDATE ,TICKET_UPDATE ,TICKET_DELETE ,TICKET_CLOSE]

# Communication Type Constants
class CommunicationType(Enum):
    ASYNC_QUEUE = "async_queue"    # Redis queue with structured data
    DIRECT_API = "direct_api"      # Direct API calls with natural language


