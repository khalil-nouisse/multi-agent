# communication/receiving/processors/email_processor.py
# Core email processing logic

import re
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...shared.models.message import IncomingMessage
from ...shared.utils.validators import EmailValidator
from ...shared.utils.formatters import TextFormatter

class EmailProcessor:
    """Main email processing engine"""
    
    def __init__(self):
        self.validator = EmailValidator()
        self.formatter = TextFormatter()
        self.processed_count = 0
        
    def process_incoming_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing method for incoming emails
        
        Args:
            email_data: Raw email data from receiver
            
        Returns:
            Dict containing processed email with routing information
        """
        try:
            # Create incoming message object
            message = IncomingMessage.from_dict(email_data)
            
            # Step 1: Basic validation
            validation_result = self._validate_email(message)
            if not validation_result.get('valid', False):
                return self._create_error_response(message, validation_result.get('error'))
            
            # Step 2: Security screening
            security_result = self._security_screening(message)
            if security_result.get('blocked', False):
                return self._create_security_response(message, security_result)
            
            # Step 3: Content analysis
            content_analysis = self._analyze_content(message)
            
            # Step 4: Classification
            classification = self._classify_email(message, content_analysis)
            
            # Step 5: Routing decision
            routing = self._determine_routing(message, classification, content_analysis)
            
            # Step 6: Auto-response decision
            auto_response = self._should_auto_respond(classification, routing)
            
            # Step 7: Create processed result
            processed_result = {
                "success": True,
                "message_id": message.message_id,
                "processed_at": datetime.now().isoformat(),
                "validation": validation_result,
                "security": security_result,
                "content_analysis": content_analysis,
                "classification": classification,
                "routing": routing,
                "auto_response": auto_response,
                "original_email": email_data,
                "processing_time_ms": self._calculate_processing_time()
            }
            
            self.processed_count += 1
            return processed_result
            
        except Exception as e:
            return self._create_error_response(
                email_data.get('message_id', 'unknown'),
                f"Processing error: {str(e)}"
            )
    
    def _validate_email(self, message: IncomingMessage) -> Dict[str, Any]:
        """Validate basic email structure and sender"""
        try:
            validation_errors = []
            
            # Check sender email
            if not message.sender or not message.sender.get('email'):
                validation_errors.append("Missing sender email")
            else:
                sender_validation = self.validator.validate_email(message.sender['email'])
                if not sender_validation.get('is_valid'):
                    validation_errors.append("Invalid sender email format")
            
            # Check subject
            if not message.subject or len(message.subject.strip()) == 0:
                validation_errors.append("Missing or empty subject")
            
            # Check content
            if not message.content or (not message.content.get('text') and not message.content.get('html')):
                validation_errors.append("Missing email content")
            
            # Check size limits
            if message.metadata and message.metadata.get('size', 0) > 25 * 1024 * 1024:  # 25MB
                validation_errors.append("Email size exceeds limit")
            
            return {
                "valid": len(validation_errors) == 0,
                "errors": validation_errors,
                "sender_valid": not any("sender" in error for error in validation_errors)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    def _security_screening(self, message: IncomingMessage) -> Dict[str, Any]:
        """Perform security screening on the email"""
        try:
            security_issues = []
            risk_score = 0
            
            # Check spam score
            spam_score = message.security.get('spam_score', 0) if message.security else 0
            if spam_score > 8:
                security_issues.append("High spam score")
                risk_score += 3
            elif spam_score > 5:
                risk_score += 1
            
            # Check for suspicious patterns
            suspicious_patterns = self._check_suspicious_patterns(message)
            security_issues.extend(suspicious_patterns)
            risk_score += len(suspicious_patterns)
            
            # Check attachments
            if message.attachments:
                attachment_security = self._screen_attachments(message.attachments)
                security_issues.extend(attachment_security.get('issues', []))
                risk_score += attachment_security.get('risk_score', 0)
            
            # Check sender reputation
            sender_reputation = self._check_sender_reputation(message.sender['email'])
            if sender_reputation.get('suspicious'):
                security_issues.append("Suspicious sender reputation")
                risk_score += 2
            
            return {
                "blocked": risk_score >= 5,
                "risk_score": risk_score,
                "security_issues": security_issues,
                "spam_score": spam_score,
                "sender_reputation": sender_reputation,
                "attachment_scan": attachment_security if message.attachments else None
            }
            
        except Exception as e:
            return {
                "blocked": False,
                "error": f"Security screening error: {str(e)}"
            }
    
    def _analyze_content(self, message: IncomingMessage) -> Dict[str, Any]:
        """Analyze email content for intent, sentiment, and key information"""
        try:
            text_content = message.content.get('text', '')
            subject = message.subject or ''
            
            # Extract key information
            ticket_refs = self._extract_ticket_references(text_content, subject)
            contact_info = self._extract_contact_info(text_content)
            dates_times = self._extract_dates_and_times(text_content)
            
            # Analyze intent
            intent_analysis = self._analyze_intent(text_content, subject)
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_sentiment(text_content, subject)
            
            # Analyze urgency
            urgency_analysis = self._analyze_urgency(text_content, subject)
            
            # Extract entities
            entities = self._extract_entities(text_content)
            
            return {
                "ticket_references": ticket_refs,
                "contact_info": contact_info,
                "dates_and_times": dates_times,
                "intent": intent_analysis,
                "sentiment": sentiment_analysis,
                "urgency": urgency_analysis,
                "entities": entities,
                "word_count": len(text_content.split()),
                "language": self._detect_language(text_content)
            }
            
        except Exception as e:
            return {
                "error": f"Content analysis error: {str(e)}"
            }
    
    def _classify_email(self, message: IncomingMessage, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Classify the email type and priority"""
        try:
            # Determine email type
            email_type = self._determine_email_type(message, content_analysis)
            
            # Calculate priority
            priority = self._calculate_priority(message, content_analysis, email_type)
            
            # Check if customer
            customer_info = self._lookup_customer(message.sender['email'])
            
            # Determine category
            category = self._determine_category(content_analysis, email_type)
            
            return {
                "email_type": email_type,
                "priority": priority,
                "category": category,
                "is_customer": customer_info.get('is_customer', False),
                "customer_tier": customer_info.get('tier', 'standard'),
                "confidence_score": self._calculate_confidence_score(email_type, priority, category)
            }
            
        except Exception as e:
            return {
                "error": f"Classification error: {str(e)}"
            }
    
    def _determine_routing(self, message: IncomingMessage, classification: Dict[str, Any], 
                          content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine routing for the email"""
        try:
            email_type = classification.get('email_type', 'general')
            priority = classification.get('priority', 'normal')
            ticket_refs = content_analysis.get('ticket_references', [])
            
            # Base routing logic
            routing_rules = {
                'ticket_followup': 'technical_support',
                'new_support_request': 'technical_support',
                'technical_issue': 'technical_support',
                'sales_inquiry': 'sales_manager',
                'billing_inquiry': 'customer_relations',
                'complaint': 'customer_relations',
                'general_inquiry': 'supervisor'
            }
            
            primary_agent = routing_rules.get(email_type, 'supervisor')
            
            # Override for ticket references
            if ticket_refs:
                primary_agent = 'technical_support'
            
            # Handle high priority
            escalation_needed = priority in ['critical', 'high'] and email_type == 'complaint'
            
            return {
                "primary_agent": primary_agent,
                "backup_agent": "supervisor" if escalation_needed else None,
                "escalation_needed": escalation_needed,
                "routing_confidence": self._calculate_routing_confidence(email_type, ticket_refs),
                "routing_reason": f"Email type: {email_type}, Priority: {priority}",
                "requires_human_review": priority == 'critical' or classification.get('confidence_score', 0) < 0.7
            }
            
        except Exception as e:
            return {
                "primary_agent": "supervisor",
                "error": f"Routing error: {str(e)}"
            }
    
    def _should_auto_respond(self, classification: Dict[str, Any], routing: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if and how to auto-respond"""
        try:
            email_type = classification.get('email_type', 'general')
            priority = classification.get('priority', 'normal')
            
            # Don't auto-respond to these types
            no_response_types = ['spam', 'bounce', 'auto_reply', 'newsletter']
            
            if email_type in no_response_types:
                return {
                    "should_respond": False,
                    "reason": f"No auto-response for {email_type}"
                }
            
            # Determine response template
            template_mapping = {
                'new_support_request': 'auto_response_support_received',
                'sales_inquiry': 'auto_response_sales_inquiry',
                'billing_inquiry': 'auto_response_billing_inquiry',
                'complaint': 'auto_response_complaint_received',
                'general_inquiry': 'auto_response_general'
            }
            
            template = template_mapping.get(email_type, 'auto_response_general')
            
            # Calculate response time expectation
            response_times = {
                'critical': '1 hour',
                'high': '4 hours',
                'normal': '24 hours',
                'low': '48 hours'
            }
            
            return {
                "should_respond": True,
                "template": template,
                "response_time_expectation": response_times.get(priority, '24 hours'),
                "include_case_number": email_type in ['new_support_request', 'complaint']
            }
            
        except Exception as e:
            return {
                "should_respond": False,
                "error": f"Auto-response decision error: {str(e)}"
            }
    
    # Helper methods
    def _extract_ticket_references(self, text: str, subject: str) -> List[str]:
        """Extract ticket references from text"""
        patterns = [
            r'#(\w+)',
            r'ticket\s*[#:]?\s*(\w+)',
            r'TK[-_]?(\w+)',
            r'case\s*[#:]?\s*(\w+)'
        ]
        
        found_tickets = []
        full_text = f"{subject} {text}".lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            found_tickets.extend(matches)
        
        return list(set(found_tickets))  # Remove duplicates
    
    def _check_suspicious_patterns(self, message: IncomingMessage) -> List[str]:
        """Check for suspicious patterns in email"""
        issues = []
        content = message.content.get('text', '') + ' ' + (message.subject or '')
        
        # Suspicious patterns
        if re.search(r'urgent.*transfer.*money|lottery.*winner|prince.*nigeria', content, re.IGNORECASE):
            issues.append("Potential scam content")
        
        if len(re.findall(r'http[s]?://[^\s]+', content)) > 5:
            issues.append("Excessive external links")
        
        return issues
    
    def _screen_attachments(self, attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Screen attachments for security issues"""
        issues = []
        risk_score = 0
        
        dangerous_extensions = ['.exe', '.bat', '.scr', '.pif', '.vbs', '.jar']
        
        for attachment in attachments:
            filename = attachment.get('filename', '').lower()
            
            if any(filename.endswith(ext) for ext in dangerous_extensions):
                issues.append(f"Dangerous file type: {filename}")
                risk_score += 3
            
            if attachment.get('size', 0) > 10 * 1024 * 1024:  # 10MB
                issues.append(f"Large attachment: {filename}")
                risk_score += 1
        
        return {
            "issues": issues,
            "risk_score": risk_score,
            "attachment_count": len(attachments)
        }
    
    def _determine_email_type(self, message: IncomingMessage, content_analysis: Dict[str, Any]) -> str:
        """Determine the type of email"""
        text = message.content.get('text', '').lower()
        subject = (message.subject or '').lower()
        
        # Check for ticket references
        if content_analysis.get('ticket_references'):
            return 'ticket_followup'
        
        # Check for specific types
        if any(word in f"{subject} {text}" for word in ['support', 'help', 'issue', 'problem', 'bug']):
            return 'new_support_request'
        
        if any(word in f"{subject} {text}" for word in ['price', 'cost', 'demo', 'sales', 'purchase']):
            return 'sales_inquiry'
        
        if any(word in f"{subject} {text}" for word in ['bill', 'invoice', 'payment', 'charge']):
            return 'billing_inquiry'
        
        if any(word in f"{subject} {text}" for word in ['complaint', 'dissatisfied', 'terrible', 'awful']):
            return 'complaint'
        
        return 'general_inquiry'
    
    def _calculate_priority(self, message: IncomingMessage, content_analysis: Dict[str, Any], email_type: str) -> str:
        """Calculate email priority"""
        urgency = content_analysis.get('urgency', {}).get('level', 'normal')
        
        if urgency == 'critical' or email_type == 'complaint':
            return 'critical'
        elif urgency == 'high' or email_type in ['technical_issue', 'billing_inquiry']:
            return 'high'
        elif email_type == 'sales_inquiry':
            return 'normal'
        else:
            return 'low'
    
    def _create_error_response(self, message_id: str, error: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "success": False,
            "message_id": message_id,
            "error": error,
            "processed_at": datetime.now().isoformat()
        }
    
    def _create_security_response(self, message: IncomingMessage, security_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create security block response"""
        return {
            "success": True,
            "message_id": message.message_id,
            "blocked": True,
            "block_reason": "Security screening failed",
            "security_result": security_result,
            "processed_at": datetime.now().isoformat()
        }
    
    # Placeholder methods for advanced features
    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information from text"""
        return {"phones": [], "emails": []}
    
    def _extract_dates_and_times(self, text: str) -> List[str]:
        """Extract dates and times from text"""
        return []
    
    def _analyze_intent(self, text: str, subject: str) -> Dict[str, Any]:
        """Analyze intent from text"""
        return {"primary_intent": "information_request", "confidence": 0.8}
    
    def _analyze_sentiment(self, text: str, subject: str) -> Dict[str, Any]:
        """Analyze sentiment"""
        return {"sentiment": "neutral", "confidence": 0.7}
    
    def _analyze_urgency(self, text: str, subject: str) -> Dict[str, Any]:
        """Analyze urgency level"""
        urgent_words = ['urgent', 'emergency', 'critical', 'asap', 'immediately']
        full_text = f"{subject} {text}".lower()
        
        if any(word in full_text for word in urgent_words):
            return {"level": "critical", "confidence": 0.9}
        else:
            return {"level": "normal", "confidence": 0.6}
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text"""
        return []
    
    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        return "en"  # Simplified
    
    def _lookup_customer(self, email: str) -> Dict[str, Any]:
        """Lookup customer information"""
        return {"is_customer": True, "tier": "standard"}  # Simplified
    
    def _determine_category(self, content_analysis: Dict[str, Any], email_type: str) -> str:
        """Determine email category"""
        return "general"  # Simplified
    
    def _calculate_confidence_score(self, email_type: str, priority: str, category: str) -> float:
        """Calculate confidence score for classification"""
        return 0.85  # Simplified
    
    def _calculate_routing_confidence(self, email_type: str, ticket_refs: List[str]) -> float:
        """Calculate routing confidence"""
        return 0.9 if ticket_refs else 0.8
    
    def _check_sender_reputation(self, email: str) -> Dict[str, Any]:
        """Check sender reputation"""
        return {"suspicious": False, "score": 0.8}
    
    def _calculate_processing_time(self) -> int:
        """Calculate processing time in milliseconds"""
        return 150  # Simplified
    