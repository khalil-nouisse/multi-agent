# communication/email_agent.py
from communication.email.email_service import email_service
from communication.email.email_templates import EMAIL_TEMPLATES
from event_types import EventType

class EmailAgent:
    def __init__(self):
        self.email_service = email_service

    def send_notification(self, event_type, payload):
        recipient_email = payload.get("customer_email") or payload.get("email")
        if not recipient_email:
            print(f"Warning: No recipient email found for event {event_type}")
            return False

        # Get the template, in case falling back to a default if not found
        template = EMAIL_TEMPLATES.get(event_type, EMAIL_TEMPLATES["DEFAULT"])

        subject_template = template["subject"]
        body_template = template["body"]

        # .format()  dynamically fill the templates with payload data
        try:
            subject = subject_template.format(**payload)
            body = body_template.format(**payload)
        except KeyError as e:
            # Handle cases where the payload is missing a key required by the template
            print(f"Error: Missing key {e} for event {event_type} in payload. Using default template.")
            default_template = EMAIL_TEMPLATES["DEFAULT"]
            subject = default_template["subject"]
            body = default_template["body"].format(customer_name=payload.get("customer_name", "customer"))

        return self.email_service.send_email(recipient_email, subject, body)

email_agent = EmailAgent()