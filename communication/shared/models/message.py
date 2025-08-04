# communication/shared/models/message.py
# Data models for communication system

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class IncomingMessage:
    """Model for incoming email messages"""
    message_id: str
    sender: Dict[str, str]  # {"email": "...", "name": "..."}
    recipients: List[Dict[str, str]]
    subject: str
    content: Dict[str, str]  # {"text": "...", "html": "..."}
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    security: Optional[Dict[str, Any]] = None
    received_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IncomingMessage':
        """Create IncomingMessage from dictionary"""
        return cls(
            message_id=data.get('message_id', ''),
            sender=data.get('sender', {}),
            recipients=data.get('recipients', []),
            subject=data.get('subject', ''),
            content=data.get('content', {}),
            attachments=data.get('attachments', []),
            metadata=data.get('metadata', {}),
            headers=data.get('headers', {}),
            security=data.get('security', {}),
            received_at=data.get('received_at', datetime.now().isoformat())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'recipients': self.recipients,
            'subject': self.subject,
            'content': self.content,
            'attachments': self.attachments,
            'metadata': self.metadata,
            'headers': self.headers,
            'security': self.security,
            'received_at': self.received_at
        }

@dataclass
class OutgoingMessage:
    """Model for outgoing messages"""
    recipient: str
    subject: str
    template_name: str
    template_data: Dict[str, Any]
    sender_agent: str
    message_id: Optional[str] = None
    priority: str = "normal"
    delivery_method: str = "venom"
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.message_id is None:
            self.message_id = f"out_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'message_id': self.message_id,
            'recipient': self.recipient,
            'subject': self.subject,
            'template_name': self.template_name,
            'template_data': self.template_data,
            'sender_agent': self.sender_agent,
            'priority': self.priority,
            'delivery_method': self.delivery_method,
            'attachments': self.attachments,
            'metadata': self.metadata,
            'created_at': self.created_at
        }

@dataclass
class CommunicationContext:
    """Context for communication routing and processing"""
    communication_type: str  # "async_queue" or "direct_api"
    event_type: str
    source_agent: str
    target_agent: Optional[str] = None
    priority: str = "normal"
    requires_human_review: bool = False
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'communication_type': self.communication_type,
            'event_type': self.event_type,
            'source_agent': self.source_agent,
            'target_agent': self.target_agent,
            'priority': self.priority,
            'requires_human_review': self.requires_human_review,
            'metadata': self.metadata,
            'created_at': self.created_at
        }