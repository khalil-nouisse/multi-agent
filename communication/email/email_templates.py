# communication/email_templates.py
from event_types import EventType

EMAIL_TEMPLATES = {
    #tickets
    EventType.TICKET_CREATE: {
        "subject": "New Ticket Created: #{ticket_title}",
        "body": (
            "Hello {customer_name},\n\n"
            "We are excited to inform you that a new ticket has been successfully created for your request.\n\n"
            "**Ticket Details:**\n"
            "- **ID:** {ticket_id}\n"
            "- **Title:** {ticket_title}\n"
            "- **Status:** {ticket_status}\n"
            "- **Priority:** {ticket_priority}\n"
            "- **Category:** {ticket_category}\n"
            "- **Description:** {ticket_description}\n"
            "- **Created On:** {ticket_creation_date}\n\n"
            "One of our agents will review your request and respond shortly.\n\n"
            "Best regards,\n"
            "Your Support Team"
        )
    },
    EventType.TICKET_STATE_UPDATE: {
        "subject": "Ticket Status Updated: #{ticket_title}",
        "body": (
            "Hello {customer_name},\n\n"
            "The status of your support ticket **#{ticket_title}** has been updated.\n\n"
            "**Updated Details:**\n"
            "- **ID:** {ticket_id}\n"
            "- **New Status:** {ticket_status}\n"
            "- **Priority:** {ticket_priority}\n"
            "- **Category:** {ticket_category}\n"
            "- **Last Updated:** {ticket_update_date}\n\n"
            "You may reply to this email if you need to provide additional information.\n\n"
            "Best regards,\n"
            "Your Support Team"
        )
    },
    EventType.TICKET_UPDATE: {
        "subject": "Ticket Updated: #{ticket_title}",
        "body": (
            "Hello {customer_name},\n\n"
            "We would like to inform you that your ticket **#{ticket_title}** has been updated.\n\n"
            "**Updated Ticket Details:**\n"
            "- **ID:** {ticket_id}\n"
            "- **Status:** {ticket_status}\n"
            "- **Priority:** {ticket_priority}\n"
            "- **Category:** {ticket_category}\n"
            "- **Description:** {ticket_description}\n"
            "- **Last Updated:** {ticket_update_date}\n\n"
            "Feel free to reply if you have more details to share.\n\n"
            "Best regards,\n"
            "Your Support Team"
        )
    },
    EventType.TICKET_CLOSE: {
        "subject": "Ticket Closed: #{ticket_title}",
        "body": (
                "Hello {customer_name},\n\n"
                "We would like to inform you that your ticket **#{ticket_title}** has been successfully closed.\n\n"
                "**Summary:**\n"
                "- **ID:** {ticket_id}\n"
                "- **Status:** {ticket_status}\n"
                "- **Priority:** {ticket_priority}\n"
                "- **Category:** {ticket_category}\n"
                "- **Description:** {ticket_description}\n"
                "- **Closed On:** {ticket_update_date}\n\n"

                "If you believe this issue is not fully resolved, you may reply to reopen the ticket.\n\n"
                "Best regards,\n"
                "Your Support Team"
            )
    },
    EventType.TICKET_DELETE: {
        "subject": "Ticket Deleted: #{ticket_title}",
        "body": (
            "Hello {customer_name},\n\n"
            "This is to inform you that your ticket **#{ticket_title}** has been deleted from our system.\n\n"
            "**Ticket Summary Before Deletion:**\n"
            "- **ID:** {ticket_id}\n"
            "- **Status:** {ticket_status}\n"
            "- **Priority:** {ticket_priority}\n"
            "- **Category:** {ticket_category}\n"
            "- **Description:** {ticket_description}\n"
            "- **Deleted On:** {ticket_update_date}\n\n"
            "If this deletion was unexpected, please contact our support team immediately.\n\n"
            "Best regards,\n"
            "Your Support Team"
        )
    },
    #opportunity
    EventType.OPPORTUNITY_CREATE: {
        "subject": "New Sales Opportunity Created: {opportunity_name}",
        "body": (
            "Hello {customer_name},\n\n"
            "We are excited to inform you that a new sales opportunity named **'{opportunity_name}'** has been created for your account.\n\n"
            "**Opportunity Details:**\n"
            "- **ID:** {opportunity_id}\n"
            "- **Name:** {opportunity_name}\n"
            "- **Assigned Commercial Representative:** {opportunity_commercial}\n"
            "- **Estimated Amount:** {opportunity_amount}\n"
            "- **Priority:** {opportunity_priority}\n"
            "- **Status:** {status}\n"
            "- **Notes:** {opportunity_notes}\n"
            "- **Creation Date:** {opportunity_creation_date}\n\n"
            "Our sales manager will reach out to you shortly to discuss the next steps.\n\n"
            "Best regards,\n"
            "The Sales Team"
        )
    },
    EventType.OPPORTUNITY_STATE_UPDATE: {
        "subject": "Opportunity Status Updated: {opportunity_name}",
        "body": (
            "Hello {customer_name},\n\n"
            "The status of your sales opportunity **'{opportunity_name}'** (ID: {opportunity_id}) has been updated.\n\n"
            "**Updated Details:**\n"
            "- **ID:** {opportunity_id}\n"
            "- **New Status:** {status}\n"
            "- **Notes:** {opportunity_notes}\n"
            "- **Last Updated On:** {opportunity_update_date}\n\n"
            "If you have any questions or need further information, feel free to reach out.\n\n"
            "Best regards,\n"
            "The Sales Team"
        )
    },
    EventType.OPPORTUNITY_UPDATE: {
        "subject": "Opportunity Updated: {opportunity_name}",
        "body": (
            "Hello {customer_name},\n\n"
            "The details of your sales opportunity **'{opportunity_name}'** (ID: {opportunity_id}) have been updated.\n\n"
            "**Updated Fields:**\n"
            "- **ID:** {opportunity_id}\n"
            "- **Assigned Commercial Representative:** {opportunity_commercial}\n"
            "- **Amount Estimation:** {opportunity_amount}\n"
            "- **Priority:** {opportunity_priority}\n"
            "- **Status:** {status}\n"
            "- **Notes:** {opportunity_notes}\n"
            "- **Last Updated On:** {opportunity_update_date}\n\n"
            "Please let us know if you would like to review or discuss the updates in more detail.\n\n"
            "Best regards,\n"
            "The Sales Team"
        )
    },
    EventType.OPPORTUNITY_RESOLVE: {
        "subject": "Opportunity Resolved: {opportunity_name}",
        "body": (
            "Hello {customer_name},\n\n"
            "We would like to inform you that the sales opportunity **'{opportunity_name}'** (ID: {opportunity_id}) has been marked as resolved.\n\n"
            "**Resolution Details:**\n"
            "- **ID:** {opportunity_id}\n"
            "- **Resolved By:** {opportunity_commercial}\n"
            "- **Final Status:** {status}\n"
            "- **Notes:** {opportunity_notes}\n"
            "- **Resolution Date:** {opportunity_resolution_date}\n\n"
            "Thank you for your continued collaboration. Please don't hesitate to reach out for any future needs.\n\n"
            "Best regards,\n"
            "The Sales Team"
        )
    },
    EventType.OPPORTUNITY_LOST : {
        "subject": "Opportunity Lost: {opportunity_name}",
        "body": (
            "Hello {customer_name},\n\n"
            "We would like to inform you that the sales opportunity **'{opportunity_name}'** (ID: {opportunity_id}) has been marked as lost.\n\n"
            "**Opportunity Details:**\n"
            "- **ID:** {opportunity_id}\n"
            "- **Assigned Commercial By:** {opportunity_commercial}\n"
            "- **Final Status:** {status}\n"
            "- **Notes:** {opportunity_notes}\n"
            "- **Creattion Date:** {opportunity_creation_date}\n\n"
            "Thank you for your continued collaboration. Please don't hesitate to reach out for any future needs.\n\n"
            "Best regards,\n"
            "The Sales Team"
        )
    },
    EventType.OPPORTUNITY_DELETE: {
        "subject": "Opportunity Deleted: {opportunity_name}",
        "body": (
            "Hello {customer_name},\n\n"
            "Please note that the sales opportunity **'{opportunity_name}'** (ID: {opportunity_id}) has been deleted from your account.\n\n"
            "**Details:**\n"
            "- **ID:** {opportunity_id}\n"
            "- **Deleted By:** {opportunity_commercial}\n"
            "- **Reason / Notes:** {opportunity_notes}\n"
            "- **Deletion Date:** {opportunity_deletion_date}\n\n"
            "If this was done in error or if you have any questions, please contact us as soon as possible.\n\n"
            "Best regards,\n"
            "The Sales Team"
        )
    },



    # Add other event types here
    "DEFAULT": {
        "subject": "Update regarding your CRM activity",
        "body": (
            "Hello {customer_name},\n\n"
            "A recent activity has been processed in our system. You can log into your account to view the details.\n\n"
            "Best regards,\n"
            "The team"
        )
    }
}