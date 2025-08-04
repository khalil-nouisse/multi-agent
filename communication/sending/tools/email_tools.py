import re
import logging
from typing import Dict, Any, Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64

from ...shared.models.communication_context import CommunicationContext

logger = logging.getLogger(__name__)

class EmailValidator:
    """
    Email validation utilities
    """
    
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    def is_valid_email(self, email: str) -> bool:
        """
        Validate email address format
        """
        if not email or not isinstance(email, str):
            return False
        
        return bool(self.EMAIL_REGEX.match(email.strip()))
    
    def validate_email_list(self, emails: List[str]) -> Dict[str, Any]:
        """
        Validate list of email addresses
        """
        valid_emails = []
        invalid_emails = []
        
        for email in emails:
            if self.is_valid_email(email):
                valid_emails.append(email.strip())
            else:
                invalid_emails.append(email)
        
        return {
            'valid_emails': valid_emails,
            'invalid_emails': invalid_emails,
            'all_valid': len(invalid_emails) == 0
        }

class EmailComposer:
    """
    Email composition utilities
    """
    
    async def compose(
        self, 
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        context: Optional[CommunicationContext] = None
    ) -> Dict[str, str]:
        """
        Compose email content
        """
        try:
            # Generate text version if not provided
            if not text_content:
                text_content = self._html_to_text(html_content)
            
            # Add context-specific elements
            if context:
                html_content = self._add_context_elements(html_content, context)
                text_content = self._add_context_elements(text_content, context)
            
            return {
                'html': html_content,
                'text': text_content,
                'subject': subject
            }
            
        except Exception as e:
            logger.error("Error composing email: %s", str(e))
            raise
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Convert HTML to plain text (basic implementation)
        """
        import html
        
        # Remove HTML tags (basic approach)
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _add_context_elements(
        self, 
        content: str, 
        context: CommunicationContext
    ) -> str:
        """
        Add context-specific elements to email content
        """
        # Add tracking pixels, unsubscribe links, etc.
        if context.ticket_id:
            # Add ticket reference
            content = content.replace(
                '</body>',
                f'<p style="font-size: 10px; color: #666;">Ticket: {context.ticket_id}</p></body>'
            )
        
        return content
    
    def create_mime_message(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> MIMEMultipart:
        """
        Create MIME message for SMTP sending
        """
        msg = MIMEMultipart('alternative')
        
        # Headers
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join(to_emails)
        
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        
        # Body parts
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Attachments
        if attachments:
            for attachment in attachments:
                self._add_attachment(msg, attachment)
        
        return msg
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """
        Add attachment to MIME message
        """
        try:
            part = MIMEBase('application', 'octet-stream')
            
            if 'content' in attachment:
                part.set_payload(attachment['content'])
            elif 'file_path' in attachment:
                with open(attachment['file_path'], 'rb') as f:
                    part.set_payload(f.read())
            
            encoders.encode_base64(part)
            
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment.get("filename", "attachment")}'
            )
            
            msg.attach(part)
            
        except Exception as e:
            logger.error("Error adding attachment: %s", str(e))