# Email Agent Tools
from langchain.tools import tool
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
from datetime import datetime

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'email': os.getenv('SUPPORT_EMAIL', 'support@yourcompany.com'),
    'password': os.getenv('EMAIL_PASSWORD', 'your_app_password'),
    'from_name': os.getenv('FROM_NAME', 'Support Team')
}

# Email templates
EMAIL_TEMPLATES = {
    'ticket_confirmation': {
        'subject': 'Ticket Confirmation - #{ticket_id}: {title}',
        'body': '''Dear {client_name},

Thank you for contacting our technical support team. We have successfully received your support request.

Ticket Details:
• Ticket ID: #{ticket_id}
• Subject: {title}
• Description: {description}
• Priority: {priority}
• Category: {category}
• Status: Open
• Created: {created_at}

Our technical support team has been notified and will review your request shortly. 
Based on the priority level ({priority}), you can expect an initial response within our standard response times.

Estimated Resolution Time: {estimated_hours} hours
Expected Completion: {estimated_completion}

For future reference, please include your ticket ID #{ticket_id} in any correspondence regarding this issue.

If you have any urgent concerns, feel free to contact us directly.

Best regards,
Technical Support Team
Your Company Name'''
    },
    
    'ticket_update': {
        'subject': 'Ticket Update - #{ticket_id}: {title}',
        'body': '''Dear {client_name},

We wanted to update you on the status of your support ticket.

Ticket Details:
• Ticket ID: #{ticket_id}
• Subject: {title}
• Previous Status: {previous_status}
• Current Status: {current_status}
• Updated: {updated_at}

{update_message}

{notes}

If you have any questions or concerns, please don't hesitate to contact us.

Best regards,
Technical Support Team
Your Company Name'''
    },
    
    'ticket_resolution': {
        'subject': 'Ticket Resolved - #{ticket_id}: {title}',
        'body': '''Dear {client_name},

Great news! Your support ticket has been successfully resolved.

Ticket Details:
• Ticket ID: #{ticket_id}
• Subject: {title}
• Status: Resolved
• Resolution Date: {resolved_at}
• Total Resolution Time: {resolution_time}

Resolution Summary:
{resolution_summary}

We hope this resolution meets your expectations. If you experience any further issues related to this ticket, please don't hesitate to contact us.

A satisfaction survey will be sent to you shortly to help us improve our services.

Best regards,
Technical Support Team
Your Company Name'''
    },
    
    'satisfaction_survey': {
        'subject': 'Satisfaction Survey - Ticket #{ticket_id}',
        'body': '''Dear {client_name},

We hope your recent technical support experience was satisfactory. Your ticket #{ticket_id} has been resolved.

We value your feedback and would appreciate if you could take a moment to rate our service.

Please rate your experience on a scale of 1-10 by clicking the link below:
{survey_link}

Your feedback helps us improve our services and better serve you in the future.

Thank you for choosing our technical support services.

Best regards,
Technical Support Team
Your Company Name'''
    },
    
    'appointment_confirmation': {
        'subject': 'Appointment Confirmation - {appointment_date}',
        'body': '''Dear {client_name},

This email confirms your upcoming appointment with our sales team.

Appointment Details:
• Date: {appointment_date}
• Time: {appointment_time}
• Duration: {duration}
• Sales Representative: {sales_rep}
• Meeting Type: {meeting_type}
• Location/Link: {location}

Agenda:
{agenda}

Please confirm your attendance by replying to this email or calling us directly.
If you need to reschedule, please let us know at least 24 hours in advance.

We look forward to meeting with you!

Best regards,
{sales_rep}
Sales Team
Your Company Name'''
    },
    
    'follow_up': {
        'subject': 'Follow-up: {subject}',
        'body': '''Dear {client_name},

We wanted to follow up on {follow_up_topic}.

{message}

If you have any questions or need further assistance, please don't hesitate to contact us.

Best regards,
{sender_name}
{department}
Your Company Name'''
    },
    
    'welcome': {
        'subject': 'Welcome to Your Company Name!',
        'body': '''Dear {client_name},

Welcome to Your Company Name! We're excited to have you as our valued customer.

Your account has been successfully created with the following details:
• Customer ID: {customer_id}
• Account Type: {account_type}
• Registration Date: {registration_date}

Getting Started:
{getting_started_info}

Our support team is here to help you every step of the way. If you have any questions, please don't hesitate to reach out.

Welcome aboard!

Best regards,
Customer Relations Team
Your Company Name'''
    }
}

@tool
def validate_email(email: str) -> Dict[str, Any]:
    """
    Validate an email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Dict containing validation result
    """
    try:
        # Basic email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        is_valid = re.match(email_pattern, email) is not None
        
        return {
            "success": True,
            "email": email,
            "is_valid": is_valid,
            "message": "Valid email address" if is_valid else "Invalid email address format"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error validating email: {str(e)}"
        }

@tool
def process_email_template(template_name: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an email template with provided data.
    
    Args:
        template_name: Name of the email template to use
        template_data: Dictionary containing template variables
        
    Returns:
        Dict containing processed email content
    """
    try:
        if template_name not in EMAIL_TEMPLATES:
            return {
                "success": False,
                "error": f"Template '{template_name}' not found. Available templates: {list(EMAIL_TEMPLATES.keys())}"
            }
        
        template = EMAIL_TEMPLATES[template_name]
        
        # Process subject
        subject = template['subject'].format(**template_data)
        
        # Process body
        body = template['body'].format(**template_data)
        
        return {
            "success": True,
            "template_name": template_name,
            "subject": subject,
            "body": body,
            "processed_at": datetime.now().isoformat()
        }
        
    except KeyError as e:
        return {
            "success": False,
            "error": f"Missing template variable: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"failed : {str(e)}"
        }