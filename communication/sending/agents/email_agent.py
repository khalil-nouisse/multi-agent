import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..channels.venom_handler import VenomHandler
from ..channels.smtp_handler import SMTPHandler
from ..templates.template_engine import TemplateEngine
from ..tools.email_tools import EmailComposer, EmailValidator
from ...shared.models.message import EmailMessage, MessagePriority, MessageStatus
from ...shared.models.communication_context import CommunicationContext

logger = logging.getLogger(__name__)

class EmailChannel(Enum):
    VENOM = "venom"
    SMTP = "smtp"

@dataclass
class EmailSendRequest:
    to: List[str]
    subject: str
    template_name: str
    template_data: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    channel: EmailChannel = EmailChannel.VENOM
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    reply_to: Optional[str] = None
    context: Optional[CommunicationContext] = None

class EmailAgent:
    """
    Email sending agent that handles email composition and delivery
    through multiple channels (Venom WhatsApp, SMTP)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.venom_handler = VenomHandler(config.get('venom', {}))
        self.smtp_handler = SMTPHandler(config.get('smtp', {}))
        self.template_engine = TemplateEngine(config.get('templates', {}))
        self.email_composer = EmailComposer()
        self.email_validator = EmailValidator()
        
        # Channel mapping
        self.channels = {
            EmailChannel.VENOM: self.venom_handler,
            EmailChannel.SMTP: self.smtp_handler
        }
        
        logger.info("EmailAgent initialized with channels: %s", 
                   list(self.channels.keys()))
    
    async def send_email(self, request: EmailSendRequest) -> Dict[str, Any]:
        """
        Send email through specified channel
        """
        try:
            # Validate request
            validation_result = await self._validate_request(request)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'message_id': None
                }
            
            # Compose email
            email_content = await self._compose_email(request)
            if not email_content:
                return {
                    'success': False,
                    'error': 'Failed to compose email',
                    'message_id': None
                }
            
            # Create email message object
            email_message = EmailMessage(
                to=request.to,
                cc=request.cc or [],
                bcc=request.bcc or [],
                subject=request.subject,
                html_body=email_content['html'],
                text_body=email_content['text'],
                attachments=request.attachments or [],
                priority=request.priority,
                reply_to=request.reply_to,
                context=request.context
            )
            
            # Send through selected channel
            channel_handler = self.channels.get(request.channel)
            if not channel_handler:
                return {
                    'success': False,
                    'error': f'Channel {request.channel} not available',
                    'message_id': None
                }
            
            result = await channel_handler.send_email(email_message)
            
            # Log result
            if result['success']:
                logger.info("Email sent successfully via %s: %s", 
                           request.channel.value, result['message_id'])
            else:
                logger.error("Failed to send email via %s: %s", 
                            request.channel.value, result['error'])
            
            return result
            
        except Exception as e:
            logger.error("Error in send_email: %s", str(e), exc_info=True)
            return {
                'success': False,
                'error': f'Internal error: {str(e)}',
                'message_id': None
            }
    
    async def send_bulk_emails(self, requests: List[EmailSendRequest]) -> List[Dict[str, Any]]:
        """
        Send multiple emails concurrently
        """
        tasks = [self.send_email(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': f'Exception: {str(result)}',
                    'message_id': None,
                    'request_index': i
                })
            else:
                result['request_index'] = i
                processed_results.append(result)
        
        return processed_results
    
    async def _validate_request(self, request: EmailSendRequest) -> Dict[str, Any]:
        """
        Validate email send request
        """
        try:
            # Validate email addresses
            for email in request.to:
                if not self.email_validator.is_valid_email(email):
                    return {
                        'valid': False,
                        'error': f'Invalid email address: {email}'
                    }
            
            # Validate CC addresses
            if request.cc:
                for email in request.cc:
                    if not self.email_validator.is_valid_email(email):
                        return {
                            'valid': False,
                            'error': f'Invalid CC email address: {email}'
                        }
            
            # Validate BCC addresses
            if request.bcc:
                for email in request.bcc:
                    if not self.email_validator.is_valid_email(email):
                        return {
                            'valid': False,
                            'error': f'Invalid BCC email address: {email}'
                        }
            
            # Validate template exists
            if not await self.template_engine.template_exists(request.template_name):
                return {
                    'valid': False,
                    'error': f'Template not found: {request.template_name}'
                }
            
            return {'valid': True}
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Validation error: {str(e)}'
            }
    
    async def _compose_email(self, request: EmailSendRequest) -> Optional[Dict[str, str]]:
        """
        Compose email content using template engine
        """
        try:
            # Render template
            template_result = await self.template_engine.render_template(
                template_name=request.template_name,
                data=request.template_data,
                context=request.context
            )
            
            if not template_result['success']:
                logger.error("Template rendering failed: %s", template_result['error'])
                return None
            
            # Use email composer to finalize content
            content = await self.email_composer.compose(
                subject=request.subject,
                html_content=template_result['html'],
                text_content=template_result.get('text'),
                context=request.context
            )
            
            return content
            
        except Exception as e:
            logger.error("Error composing email: %s", str(e), exc_info=True)
            return None