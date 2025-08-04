# communication/receiving/channels/venom_receiver.py
# Venom service integration for receiving emails

import os
import json
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta

class VenomEmailReceiver:
    """Handler for receiving emails via Venom service"""
    
    def __init__(self):
        self.api_key = os.getenv('VENOM_API_KEY')
        self.base_url = os.getenv('VENOM_BASE_URL', 'https://api.venom.com/v1')
        self.webhook_secret = os.getenv('VENOM_WEBHOOK_SECRET')
        self.last_fetch_time = None
        
        if not self.api_key:
            raise ValueError("VENOM_API_KEY environment variable is required")
    
    def fetch_new_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch new emails from Venom service
        
        Args:
            limit: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries
        """
        try:
            # Calculate time range for fetching
            if self.last_fetch_time:
                since = self.last_fetch_time
            else:
                # First run - fetch emails from last hour
                since = datetime.now() - timedelta(hours=1)
            
            params = {
                'limit': limit,
                'since': since.isoformat(),
                'status': 'unread',  # Only fetch unread emails
                'folder': 'inbox'
            }
            
            response = requests.get(
                f"{self.base_url}/emails/inbox",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                venom_response = response.json()
                emails = venom_response.get('emails', [])
                
                # Convert Venom format to our internal format
                processed_emails = []
                for email_data in emails:
                    processed_email = self._convert_venom_email(email_data)
                    processed_emails.append(processed_email)
                
                # Update last fetch time
                self.last_fetch_time = datetime.now()
                
                return processed_emails
            else:
                print(f"Venom API error: {response.status_code} - {response.text}")
                return []
                
        except requests.RequestException as e:
            print(f"Venom network error: {str(e)}")
            return []
        except Exception as e:
            print(f"Venom receiver error: {str(e)}")
            return []
    
    def _convert_venom_email(self, venom_email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Venom email format to our internal format
        
        Args:
            venom_email: Email data from Venom API
            
        Returns:
            Email in our internal format
        """
        return {
            "message_id": venom_email.get('id'),
            "sender": {
                "email": venom_email.get('from', {}).get('email'),
                "name": venom_email.get('from', {}).get('name', '')
            },
            "recipients": [
                {
                    "email": recipient.get('email'),
                    "name": recipient.get('name', '')
                }
                for recipient in venom_email.get('to', [])
            ],
            "subject": venom_email.get('subject', ''),
            "content": {
                "text": venom_email.get('text_body', ''),
                "html": venom_email.get('html_body', '')
            },
            "attachments": self._process_venom_attachments(venom_email.get('attachments', [])),
            "metadata": {
                "received_at": venom_email.get('received_at'),
                "size": venom_email.get('size', 0),
                "message_id": venom_email.get('message_id'),
                "thread_id": venom_email.get('thread_id'),
                "labels": venom_email.get('labels', []),
                "source": "venom"
            },
            "headers": venom_email.get('headers', {}),
            "security": {
                "spam_score": venom_email.get('spam_score', 0),
                "is_spam": venom_email.get('is_spam', False),
                "virus_scan_result": venom_email.get('virus_scan', 'clean')
            }
        }
    
    def _process_venom_attachments(self, venom_attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process attachments from Venom format
        
        Args:
            venom_attachments: List of attachments from Venom
            
        Returns:
            List of processed attachments
        """
        processed = []
        
        for attachment in venom_attachments:
            processed_attachment = {
                "filename": attachment.get('filename'),
                "content_type": attachment.get('content_type'),
                "size": attachment.get('size', 0),
                "attachment_id": attachment.get('id'),
                "is_inline": attachment.get('is_inline', False),
                "download_url": attachment.get('download_url'),
                "security_scan": attachment.get('security_scan', {})
            }
            processed.append(processed_attachment)
        
        return processed
    
    def mark_email_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark an email as read in Venom
        
        Args:
            message_id: The Venom message ID
            
        Returns:
            Dict containing operation result
        """
        try:
            response = requests.patch(
                f"{self.base_url}/emails/{message_id}",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={"status": "read"},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message_id": message_id,
                    "status": "marked_as_read"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to mark as read: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error marking email as read: {str(e)}"
            }
    
    def download_attachment(self, attachment_id: str, download_url: str) -> Dict[str, Any]:
        """
        Download an attachment from Venom
        
        Args:
            attachment_id: The attachment ID
            download_url: The download URL from Venom
            
        Returns:
            Dict containing attachment data
        """
        try:
            response = requests.get(
                download_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}'
                },
                timeout=60  # Longer timeout for file downloads
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "attachment_id": attachment_id,
                    "data": response.content,
                    "size": len(response.content)
                }
            else:
                return {
                    "success": False,
                    "error": f"Download failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error downloading attachment: {str(e)}"
            }
    
    def setup_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """
        Setup webhook for real-time email notifications
        
        Args:
            webhook_url: URL where Venom should send notifications
            
        Returns:
            Dict containing webhook setup result
        """
        try:
            webhook_config = {
                "url": webhook_url,
                "events": ["email.received", "email.bounced"],
                "secret": self.webhook_secret
            }
            
            response = requests.post(
                f"{self.base_url}/webhooks",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json=webhook_config,
                timeout=30
            )
            
            if response.status_code == 201:
                webhook_data = response.json()
                return {
                    "success": True,
                    "webhook_id": webhook_data.get('id'),
                    "webhook_url": webhook_url,
                    "events": webhook_config["events"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Webhook setup failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error setting up webhook: {str(e)}"
            }
    
    def process_webhook_notification(self, webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming webhook notification from Venom
        
        Args:
            webhook_payload: The webhook payload from Venom
            
        Returns:
            Dict containing processed notification
        """
        try:
            event_type = webhook_payload.get('event_type')
            email_data = webhook_payload.get('data', {})
            
            if event_type == 'email.received':
                # Process new email notification
                processed_email = self._convert_venom_email(email_data)
                return {
                    "success": True,
                    "event_type": "new_email",
                    "email": processed_email,
                    "requires_processing": True
                }
            
            elif event_type == 'email.bounced':
                # Process bounce notification
                return {
                    "success": True,
                    "event_type": "email_bounce",
                    "bounce_info": {
                        "original_message_id": email_data.get('original_message_id'),
                        "bounce_reason": email_data.get('bounce_reason'),
                        "recipient": email_data.get('recipient'),
                        "bounce_type": email_data.get('bounce_type')
                    },
                    "requires_processing": True
                }
            
            else:
                return {
                    "success": True,
                    "event_type": "unknown",
                    "requires_processing": False,
                    "message": f"Unknown webhook event: {event_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing webhook: {str(e)}"
            }