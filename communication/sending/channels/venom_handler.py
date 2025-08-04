import asyncio
import logging
from typing import Dict, Any, Optional, List
import aiohttp
import json

from ...shared.models.message import EmailMessage, MessageStatus

logger = logging.getLogger(__name__)

class VenomHandler:
    """
    Venom WhatsApp handler for sending emails through WhatsApp
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_url = config.get('api_url', 'http://localhost:3000')
        self.session_name = config.get('session_name', 'default')
        self.timeout = config.get('timeout', 30)
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_email(self, email_message: EmailMessage) -> Dict[str, Any]:
        """
        Send email through Venom WhatsApp
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Convert email to WhatsApp message format
            whatsapp_messages = self._convert_email_to_whatsapp(email_message)
            
            results = []
            for message in whatsapp_messages:
                result = await self._send_whatsapp_message(message)
                results.append(result)
            
            # Check if all messages were sent successfully
            success = all(r['success'] for r in results)
            
            return {
                'success': success,
                'message_id': email_message.message_id,
                'channel': 'venom',
                'results': results,
                'error': None if success else 'Some messages failed to send'
            }
            
        except Exception as e:
            logger.error("Error sending via Venom: %s", str(e), exc_info=True)
            return {
                'success': False,
                'message_id': email_message.message_id,
                'channel': 'venom',
                'error': str(e)
            }
    
    def _convert_email_to_whatsapp(self, email_message: EmailMessage) -> List[Dict[str, Any]]:
        """
        Convert email message to WhatsApp message format
        """
        messages = []
        
        # Convert email addresses to phone numbers (if mapping exists)
        recipients = self._emails_to_phone_numbers(email_message.to)
        
        for recipient in recipients:
            # Create message content
            content = f"*{email_message.subject}*\n\n"
            
            # Use text body or convert HTML to text
            if email_message.text_body:
                content += email_message.text_body
            else:
                content += self._html_to_text(email_message.html_body)
            
            message = {
                'phone': recipient,
                'message': content,
                'session': self.session_name
            }
            
            messages.append(message)
            
            # Handle attachments
            for attachment in email_message.attachments:
                attachment_message = {
                    'phone': recipient,
                    'file': attachment,
                    'session': self.session_name
                }
                messages.append(attachment_message)
        
        return messages
    
    async def _send_whatsapp_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send individual WhatsApp message
        """
        try:
            endpoint = '/send-message' if 'message' in message else '/send-file'
            url = f"{self.api_url}{endpoint}"
            
            async with self.session.post(
                url,
                json=message,
                timeout=self.timeout
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return {
                        'success': True,
                        'phone': message['phone'],
                        'message_id': result.get('id'),
                        'response': result
                    }
                else:
                    error_text = await response.text()
                    return {
                        'success': False,
                        'phone': message['phone'],
                        'error': f'HTTP {response.status}: {error_text}'
                    }
                    
        except asyncio.TimeoutError:
            return {
                'success': False,
                'phone': message['phone'],
                'error': 'Request timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'phone': message['phone'],
                'error': str(e)
            }
    
    def _emails_to_phone_numbers(self, emails: List[str]) -> List[str]:
        """
        Convert email addresses to phone numbers using mapping
        This would typically use a database lookup
        """
        # Placeholder implementation
        # In real implementation, this would query your database
        # to find phone numbers associated with email addresses
        
        phone_mapping = self.config.get('email_to_phone_mapping', {})
        phones = []
        
        for email in emails:
            phone = phone_mapping.get(email)
            if phone:
                phones.append(phone)
            else:
                logger.warning("No phone mapping found for email: %s", email)
        
        return phones
    
    def _html_to_text(self, html_content: str) -> str:
        """
        Convert HTML to plain text for WhatsApp
        """
        import re
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)
        
        # Decode HTML entities
        import html
        text = html.unescape(text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text