#Enum for structured event types (optional)
from enum import Enum

class EventType(Enum):
    TICKET_CREATED = "ticket_created"
    CUSTOMER_UPDATE = "customer_update"