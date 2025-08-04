# communication/receiving/tools/email_receiving_tools.py
# Tools for receiving and processing incoming emails

from langchain.tools import tool
from typing import Dict, Any, List, Optional
import re
import email
from email.mime.text import MIMEText
from datetime import datetime
from ..channels.venom_receiver import VenomEmailReceiver
from ..channels.imap_receiver import IMAPReceiver
from ..processors.email_processor import EmailProcessor
from ...shared.models.message import IncomingMessage
from ...shared.utils.validators import EmailValidator
import os

class EmailReceivingService:
    def __init__(self):
        self.venom_receiver = VenomEmailReceiver()
        self.imap_receiver = IMAPReceiver()
        self.email_processor = EmailProcessor()
        self.validator = EmailValidator()
        self.primary_method = os.getenv('EMAIL_RECEIVE_METHOD', 'venom')
    
    def fetch_new_emails(self) -> List[Dict[str, Any]]:
        """Fetch new emails from configured source"""
        try:
            if self.primary_method == 'venom':
                return self.venom_receiver.fetch_new_emails()
            else:
                return self.imap_receiver.fetch_new_emails()
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

receiving_service = EmailReceivingService()

@tool
def fetch_incoming_emails() -> Dict[str, Any]:
    """
    Fetch new incoming emails from the configured email service.
    
    Returns:
        Dict containing list of new emails and processing status
    """
    try:
        new_emails = receiving_service.fetch_new_emails()
        
        if not new_emails:
            return {
                "success": True,
                "new_emails_count": 0,
                "emails": [],
                "message": "No new emails found"
            }
        
        processed_emails = []
        for email_data in new_emails:
            # Process each email
            processed = receiving_service.email_processor.process_incoming_email(email_data)
            processed_emails.append(processed)
        
        return {
            "success": True,
            "new_emails_count": len(new_emails),
            "processed_count": len(processed_emails),
            "emails": processed_emails,
            "message": f"Successfully processed {len(processed_emails)} new emails"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching incoming emails: {str(e)}"
        }

@tool
def parse_email_for_ticket_reference(email_content: str, subject: str) -> Dict[str, Any]:
    """
    Parse incoming email to extract ticket references and determine intent.
    
    Args:
        email_content: The body content of the email
        subject: The email subject line
        
    Returns:
        Dict containing parsed information and routing suggestion
    """
    try:
        # Extract ticket IDs from subject and content
        ticket_patterns = [
            r'#(\w+)',                          # #TK123
            r'ticket\s*[#:]?\s*(\w+)',         # ticket TK123, ticket: TK123
            r'TK[-_]?(\d+)',                   # TK-123, TK_123, TK123
            r'case\s*[#:]?\s*(\w+)',           # case 123
            r're:\s*.*#(\w+)',                 # Re: Your ticket #123
        ]
        
        found_tickets = []
        full_text = f"{subject} {email_content}".lower()
        
        for pattern in ticket_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            found_tickets.extend(matches)
        
        # Remove duplicates while preserving order
        unique_tickets = list(dict.fromkeys(found_tickets))
        
        # Determine email intent
        intent = analyze_email_intent(email_content, subject)
        
        # Determine urgency
        urgency = determine_email_urgency(email_content, subject)
        
        return {
            "success": True,
            "ticket_references": unique_tickets,
            "primary_ticket": unique_tickets[0] if unique_tickets else None,
            "intent": intent,
            "urgency": urgency,
            "requires_human_review": urgency == "critical" or intent == "complaint",
            "suggested_routing": get_routing_suggestion(intent, unique_tickets),
            "parsed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error parsing email: {str(e)}"
        }

@tool
def classify_incoming_email(sender_email: str, subject: str, content: str, 
                           attachments: List[str] = None) -> Dict[str, Any]:
    """
    Classify incoming email and determine appropriate handling.
    
    Args:
        sender_email: Email address of sender
        subject: Email subject line
        content: Email body content
        attachments: List of attachment names
        
    Returns:
        Dict containing classification and routing information
    """
    try:
        # Validate sender
        sender_validation = receiving_service.validator.validate_email(sender_email)
        
        # Parse for ticket references
        ticket_info = parse_email_for_ticket_reference(content, subject)
        
        # Classify email type
        email_type = classify_email_type(subject, content, attachments or [])
        
        # Determine department routing
        department_routing = determine_department_routing(subject, content, email_type)
        
        # Check if sender is existing customer
        customer_info = lookup_customer_by_email(sender_email)
        
        # Determine priority
        priority = calculate_email_priority(
            email_type, 
            ticket_info.get('urgency', 'normal'),
            customer_info.get('tier', 'standard')
        )
        
        return {
            "success": True,
            "classification": {
                "email_type": email_type,
                "priority": priority,
                "department": department_routing,
                "requires_immediate_attention": priority in ["critical", "high"],
                "is_existing_customer": customer_info.get("is_customer", False)
            },
            "sender_info": {
                "email": sender_email,
                "is_valid": sender_validation.get("is_valid", False),
                "customer_info": customer_info
            },
            "ticket_info": ticket_info,
            "routing_recommendation": {
                "primary_agent": department_routing,
                "backup_agent": "supervisor" if priority == "critical" else None,
                "auto_response_needed": email_type in ["new_inquiry", "ticket_followup"]
            },
            "classified_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error classifying email: {str(e)}"
        }

@tool
def process_email_attachments(attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process email attachments for security and content extraction.
    
    Args:
        attachments: List of attachment data with filename, content_type, data
        
    Returns:
        Dict containing processed attachment information
    """
    try:
        processed_attachments = []
        security_alerts = []
        
        for attachment in attachments:
            filename = attachment.get('filename', 'unknown')
            content_type = attachment.get('content_type', 'application/octet-stream')
            size = attachment.get('size', 0)
            
            # Security checks
            security_check = perform_attachment_security_check(filename, content_type, size)
            
            if not security_check.get('safe', True):
                security_alerts.append({
                    "filename": filename,
                    "reason": security_check.get('reason', 'Unknown security issue'),
                    "action": "quarantined"
                })
                continue
            
            # Process safe attachments
            processed = {
                "filename": filename,
                "content_type": content_type,
                "size": size,
                "safe": True,
                "extracted_text": None,
                "file_type": get_file_type_category(filename, content_type)
            }
            
            # Extract text from supported file types
            if content_type in ['text/plain', 'application/pdf', 'application/msword']:
                try:
                    extracted_text = extract_text_from_attachment(attachment)
                    processed["extracted_text"] = extracted_text[:1000]  # Limit size
                except Exception as e:
                    processed["extraction_error"] = str(e)
            
            processed_attachments.append(processed)
        
        return {
            "success": True,
            "processed_attachments": processed_attachments,
            "total_attachments": len(attachments),
            "safe_attachments": len(processed_attachments),
            "security_alerts": security_alerts,
            "has_security_issues": len(security_alerts) > 0
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing attachments: {str(e)}"
        }

@tool
def create_auto_response(email_classification: Dict[str, Any], 
                        sender_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create automatic response based on email classification.
    
    Args:
        email_classification: Classification data from classify_incoming_email
        sender_info: Sender information
        
    Returns:
        Dict containing auto-response data for sending
    """
    try:
        email_type = email_classification.get('email_type', 'general')
        priority = email_classification.get('priority', 'normal')
        department = email_classification.get('department', 'general')
        
        # Determine if auto-response is appropriate
        if email_type in ['spam', 'bounce', 'auto_reply']:
            return {
                "success": True,
                "send_auto_response": False,
                "reason": f"No auto-response needed for {email_type}"
            }
        
        # Select appropriate template
        template_mapping = {
            "new_inquiry": "auto_response_new_inquiry",
            "ticket_followup": "auto_response_ticket_update", 
            "support_request": "auto_response_support_received",
            "sales_inquiry": "auto_response_sales_inquiry",
            "complaint": "auto_response_complaint_received"
        }
        
        template_name = template_mapping.get(email_type, "auto_response_general")
        
        # Prepare response data
        response_data = {
            "recipient": sender_info.get('email'),
            "subject": f"Re: Your message - We've received your {email_type.replace('_', ' ')}",
            "template_name": template_name,
            "template_data": {
                "sender_name": sender_info.get('name', 'Valued Customer'),
                "email_type": email_type,
                "priority": priority,
                "department": department,
                "response_time_expectation": get_response_time_expectation(priority),
                "case_number": generate_case_number() if email_type == "new_inquiry" else None
            },
            "sender_agent": "email_receiver",
            "auto_response": True
        }
        
        return {
            "success": True,
            "send_auto_response": True,
            "response_data": response_data,
            "estimated_response_time": get_response_time_expectation(priority)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error creating auto-response: {str(e)}"
        }

# Helper functions
def analyze_email_intent(content: str, subject: str) -> str:
    """Analyze email content to determine intent"""
    content_lower = content.lower()
    subject_lower = subject.lower()
    full_text = f"{subject_lower} {content_lower}"
    
    intent_keywords = {
        "complaint": ["complaint", "dissatisfied", "unhappy", "terrible", "awful", "worst"],
        "urgent_support": ["urgent", "critical", "emergency", "asap", "immediately"],
        "ticket_followup": ["status", "update", "progress", "when will", "how long"],
        "new_inquiry": ["question", "help", "support", "assistance", "how do i"],
        "sales_inquiry": ["price", "cost", "purchase", "buy", "demo", "quote"],
        "billing_inquiry": ["bill", "invoice", "payment", "charge", "refund"]
    }
    
    for intent, keywords in intent_keywords.items():
        if any(keyword in full_text for keyword in keywords):
            return intent
    
    return "general"

def determine_email_urgency(content: str, subject: str) -> str:
    """Determine urgency level of email"""
    urgent_indicators = ["urgent", "critical", "emergency", "asap", "immediately", "down", "broken"]
    full_text = f"{subject} {content}".lower()
    
    if any(indicator in full_text for indicator in urgent_indicators):
        return "critical"
    elif "important" in full_text or "priority" in full_text:
        return "high"
    else:
        return "normal"

def get_routing_suggestion(intent: str, ticket_refs: List[str]) -> str:
    """Suggest routing based on intent and ticket references"""
    if ticket_refs:
        return "technical_support"  # Has ticket reference
    
    routing_map = {
        "complaint": "customer_relations",
        "urgent_support": "technical_support", 
        "ticket_followup": "technical_support",
        "new_inquiry": "supervisor",  # Let supervisor route
        "sales_inquiry": "sales_manager",
        "billing_inquiry": "customer_relations"
    }
    
    return routing_map.get(intent, "supervisor")

def classify_email_type(subject: str, content: str, attachments: List[str]) -> str:
    """Classify the type of email received"""
    # Implementation for email type classification
    # This would include logic to identify spam, auto-replies, support requests, etc.
    return "support_request"  # Simplified for example

def determine_department_routing(subject: str, content: str, email_type: str) -> str:
    """Determine which department should handle this email"""
    # Implementation for department routing logic
    return "technical_support"  # Simplified for example

def lookup_customer_by_email(email: str) -> Dict[str, Any]:
    """Look up customer information by email address"""
    # Implementation to check CRM for existing customer
    return {"is_customer": True, "tier": "standard"}  # Simplified for example

def calculate_email_priority(email_type: str, urgency: str, customer_tier: str) -> str:
    """Calculate overall email priority"""
    # Implementation for priority calculation
    return "normal"  # Simplified for example

def perform_attachment_security_check(filename: str, content_type: str, size: int) -> Dict[str, Any]:
    """Perform security checks on attachments"""
    dangerous_extensions = ['.exe', '.bat', '.scr', '.pif', '.vbs']
    max_size = 25 * 1024 * 1024  # 25MB
    
    if any(filename.lower().endswith(ext) for ext in dangerous_extensions):
        return {"safe": False, "reason": "Dangerous file extension"}
    
    if size > max_size:
        return {"safe": False, "reason": "File too large"}
    
    return {"safe": True}

def get_file_type_category(filename: str, content_type: str) -> str:
    """Categorize file type"""
    if content_type.startswith('image/'):
        return "image"
    elif content_type == 'application/pdf':
        return "document"
    elif content_type.startswith('text/'):
        return "text"
    else:
        return "other"

def extract_text_from_attachment(attachment: Dict[str, Any]) -> str:
    """Extract text content from attachment"""
    # Implementation would depend on file type
    return "Extracted text content..."  # Simplified for example

def get_response_time_expectation(priority: str) -> str:
    """Get expected response time based on priority"""
    time_map = {
        "critical": "within 1 hour",
        "high": "within 4 hours", 
        "normal": "within 24 hours",
        "low": "within 48 hours"
    }
    return time_map.get(priority, "within 24 hours")

def generate_case_number() -> str:
    """Generate a unique case number"""
    from datetime import datetime
    return f"CASE-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# Email receiving tools list
email_receiving_tool_list = [
    fetch_incoming_emails,
    parse_email_for_ticket_reference,
    classify_incoming_email,
    process_email_attachments,
    create_auto_response
]