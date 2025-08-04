from typing import Dict, Any, Optional
from enum import Enum

class TicketTemplateType(Enum):
    TICKET_CREATED = "ticket_created"
    TICKET_UPDATED = "ticket_updated"
    TICKET_RESOLVED = "ticket_resolved"
    TICKET_CLOSED = "ticket_closed"
    AGENT_ASSIGNED = "agent_assigned"
    CUSTOMER_REPLY = "customer_reply"
    ESCALATION = "escalation"
    FOLLOW_UP = "follow_up"

class TicketTemplates:
    """
    Predefined ticket email templates
    """
    
    @staticmethod
    def get_template_data(
        template_type: TicketTemplateType,
        ticket_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        agent_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get template data for specific ticket template type
        """
        
        base_data = {
            'ticket': ticket_data,
            'customer': customer_data,
            'agent': agent_data or {},
            'company': {
                'name': 'Your Company',
                'support_email': 'support@company.com',
                'website': 'https://company.com'
            }
        }
        
        template_specific_data = {
            TicketTemplateType.TICKET_CREATED: {
                'subject': f"Ticket Created: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'created',
                'message': 'Your support ticket has been created and assigned to our team.'
            },
            
            TicketTemplateType.TICKET_UPDATED: {
                'subject': f"Ticket Updated: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'updated',
                'message': 'Your support ticket has been updated with new information.'
            },
            
            TicketTemplateType.TICKET_RESOLVED: {
                'subject': f"Ticket Resolved: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'resolved',
                'message': 'Your support ticket has been resolved. Please review the solution.'
            },
            
            TicketTemplateType.TICKET_CLOSED: {
                'subject': f"Ticket Closed: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'closed',
                'message': 'Your support ticket has been closed. Thank you for contacting us.'
            },
            
            TicketTemplateType.AGENT_ASSIGNED: {
                'subject': f"Agent Assigned: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'assigned',
                'message': f"Your ticket has been assigned to {agent_data.get('name', 'an agent') if agent_data else 'an agent'}."
            },
            
            TicketTemplateType.CUSTOMER_REPLY: {
                'subject': f"Customer Reply: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'replied',
                'message': 'Thank you for your reply. We will review and respond shortly.'
            },
            
            TicketTemplateType.ESCALATION: {
                'subject': f"Ticket Escalated: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'escalated',
                'message': 'Your ticket has been escalated to our senior support team.'
            },
            
            TicketTemplateType.FOLLOW_UP: {
                'subject': f"Follow-up: {ticket_data.get('subject', 'N/A')} [#{ticket_data.get('id')}]",
                'action': 'follow_up',
                'message': 'We are following up on your support ticket.'
            }
        }
        
        # Merge base data with template-specific data
        if template_type in template_specific_data:
            base_data.update(template_specific_data[template_type])
        
        return base_data