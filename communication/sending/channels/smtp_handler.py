import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from ...shared.models.message import EmailMessage, MessageStatus
from ..tools.email_tools import EmailComposer

logger = logging.getLogger(__name__)

class SMTPHandler:
    """
    SMTP handler for sending emails through traditional email servers
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_server = config.get('server', 'localhost')
        self.smtp_port = config.get('port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.use_tls = config.get('use_tls', True)
        self.from_email = config.get('from_email')
        self.email_composer = EmailComposer()
        
    async def send_email(self, email_message: EmailMessage) -> Dict[str, Any]:
        """
        Send email through SMTP
        """
        try:
            # Create MIME message
            mime_message = self.email_composer.create_mime_message(
                to_emails=email_message.to,
                subject=email_message.subject,
                html_content=email_message.html_body,
                text_content=email_message.text_body or '',
                from_email=self.from_email or self.username,
                cc_emails=email_message.cc,
                bcc_emails=email_message.bcc,
                attachments=email_message.attachments
            )
            
            # Send email
            result = await self._send_mime_message(mime_message, email_message)
            
            return result
            
        except Exception as e:
            logger.error("Error sending via SMTP: %s", str(e), exc_info=True)
            return {
                'success': False,
                'message_id': email_message.message_id,
                'channel': 'smtp',
                'error': str(e)
            }
    
    async def _send_mime_message(
        self, 
        mime_message: MIMEMultipart, 
        email_message: EmailMessage
    ) -> Dict[str, Any]:
        """
        Send MIME message through SMTP server
        """
        try:
            # Run SMTP operations in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._smtp_send, 
                mime_message, 
                email_message
            )
            
            return result
            
        except Exception as e:
            logger.error("Error in SMTP send: %s", str(e))
            return {
                'success': False,
                'message_id': email_message.message_id,
                'channel': 'smtp',
                'error': str(e)
            }
    
    def _smtp_send(self, mime_message: MIMEMultipart, email_message: EmailMessage) -> Dict[str, Any]:
        """
        Synchronous SMTP send operation
        """
        server = None
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            if self.use_tls:
                server.starttls()
            
            if self.username and self.password:
                server.login(self.username, self.password)
            
            # Prepare recipient list
            recipients = email_message.to.copy()
            if email_message.cc:
                recipients.extend(email_message.cc)
            if email_message.bcc:
                recipients.extend(email_message.bcc)
            
            # Send email
            text = mime_message.as_string()
            server.sendmail(
                from_addr=self.from_email or self.username,
                to_addrs=recipients,
                msg=text
            )
            
            logger.info("Email sent successfully via SMTP: %s", email_message.message_id)
            
            return {
                'success': True,
                'message_id': email_message.message_id,
                'channel': 'smtp',
                'recipients': recipients,
                'error': None
            }
            
        except smtplib.SMTPException as e:
            logger.error("SMTP error: %s", str(e))
            return {
                'success': False,
                'message_id': email_message.message_id,
                'channel': 'smtp',
                'error': f'SMTP error: {str(e)}'
            }
        except Exception as e:
            logger.error("Unexpected error in SMTP send: %s", str(e))
            return {
                'success': False,
                'message_id': email_message.message_id,
                'channel': 'smtp',
                'error': f'Unexpected error: {str(e)}'
            }
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass