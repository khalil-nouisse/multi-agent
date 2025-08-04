# communication/shared/utils/formatters.py
# Text formatting and processing utilities

import re
import html
from typing import Dict, Any, List, Optional
from datetime import datetime

class TextFormatter:
    """Text formatting and cleaning utilities"""
    
    def __init__(self):
        self.email_patterns = {
            'quoted_text': re.compile(r'^>.*$', re.MULTILINE),
            'email_headers': re.compile(r'^(From|To|Cc|Bcc|Subject|Date):\s*.*$', re.MULTILINE | re.IGNORECASE),
            'forward_headers': re.compile(r'^-+ ?Forwarded message ?-+', re.MULTILINE | re.IGNORECASE),
            'reply_headers': re.compile(r'^On .* wrote:', re.MULTILINE),
            'signature': re.compile(r'^--\s*$.*', re.MULTILINE | re.DOTALL),
            'urls': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'emails': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone_numbers': re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        }
    
    def clean_email_content(self, content: str, remove_quoted: bool = True, 
                           remove_signatures: bool = True) -> Dict[str, Any]:
        """
        Clean and format email content
        
        Args:
            content: Raw email content
            remove_quoted: Whether to remove quoted text
            remove_signatures: Whether to remove email signatures
            
        Returns:
            Dict containing cleaned content and extracted elements
        """
        try:
            if not content:
                return {
                    "cleaned_content": "",
                    "original_length": 0,
                    "cleaned_length": 0,
                    "removed_elements": []
                }
            
            original_length = len(content)
            cleaned = content
            removed_elements = []
            
            # Remove HTML tags if present
            if '<html>' in cleaned.lower() or '<body>' in cleaned.lower():
                cleaned = self._html_to_text(cleaned)
                removed_elements.append("html_tags")
            
            # Remove quoted text
            if remove_quoted:
                quoted_matches = self.email_patterns['quoted_text'].findall(cleaned)
                if quoted_matches:
                    cleaned = self.email_patterns['quoted_text'].sub('', cleaned)
                    removed_elements.append("quoted_text")
            
            # Remove email signatures
            if remove_signatures:
                signature_match = self.email_patterns['signature'].search(cleaned)
                if signature_match:
                    cleaned = cleaned[:signature_match.start()]
                    removed_elements.append("signature")
            
            # Remove forward/reply headers
            cleaned = self.email_patterns['forward_headers'].sub('', cleaned)
            cleaned = self.email_patterns['reply_headers'].sub('', cleaned)
            cleaned = self.email_patterns['email_headers'].sub('', cleaned)
            
            if self.email_patterns['forward_headers'].search(content) or \
               self.email_patterns['reply_headers'].search(content):
                removed_elements.append("email_headers")
            
            # Clean up whitespace
            cleaned = self._normalize_whitespace(cleaned)
            
            return {
                "cleaned_content": cleaned.strip(),
                "original_length": original_length,
                "cleaned_length": len(cleaned.strip()),
                "removed_elements": removed_elements,
                "reduction_percentage": round((1 - len(cleaned.strip()) / max(original_length, 1)) * 100, 2)
            }
            
        except Exception as e:
            return {
                "cleaned_content": content,
                "error": f"Cleaning error: {str(e)}"
            }
    
    def extract_urls(self, text: str) -> List[Dict[str, Any]]:
        """Extract URLs from text"""
        try:
            urls = self.email_patterns['urls'].findall(text)
            url_info = []
            
            for url in urls:
                url_info.append({
                    "url": url,
                    "domain": self._extract_domain(url),
                    "is_secure": url.startswith('https://'),
                    "is_shortened": self._is_shortened_url(url)
                })
            
            return url_info
            
        except Exception as e:
            return [{"error": f"URL extraction error: {str(e)}"}]
    
    def extract_contact_info(self, text: str) -> Dict[str, List[str]]:
        """Extract contact information from text"""
        try:
            emails = self.email_patterns['emails'].findall(text)
            phones = self.email_patterns['phone_numbers'].findall(text)
            
            # Clean up phone numbers
            cleaned_phones = []
            for phone in phones:
                if isinstance(phone, tuple):
                    phone = ''.join(phone)
                cleaned_phone = re.sub(r'[^\d+]', '', phone)
                if len(cleaned_phone) >= 10:  # Minimum phone length
                    cleaned_phones.append(phone)
            
            return {
                "emails": list(set(emails)),  # Remove duplicates
                "phone_numbers": list(set(cleaned_phones))
            }
            
        except Exception as e:
            return {
                "emails": [],
                "phone_numbers": [],
                "error": f"Contact extraction error: {str(e)}"
            }
    
    def format_for_display(self, content: str, max_length: int = 500) -> Dict[str, Any]:
        """
        Format content for display purposes
        
        Args:
            content: Content to format
            max_length: Maximum length for preview
            
        Returns:
            Dict containing formatted content
        """
        try:
            if not content:
                return {
                    "preview": "",
                    "full_content": "",
                    "is_truncated": False,
                    "word_count": 0
                }
            
            # Clean content
            cleaned_result = self.clean_email_content(content)
            cleaned_content = cleaned_result.get('cleaned_content', content)
            
            # Create preview
            if len(cleaned_content) > max_length:
                preview = cleaned_content[:max_length].rsplit(' ', 1)[0] + '...'
                is_truncated = True
            else:
                preview = cleaned_content
                is_truncated = False
            
            # Count words
            word_count = len(cleaned_content.split())
            
            return {
                "preview": preview,
                "full_content": cleaned_content,
                "is_truncated": is_truncated,
                "word_count": word_count,
                "character_count": len(cleaned_content),
                "estimated_reading_time": max(1, word_count // 200)  # ~200 words per minute
            }
            
        except Exception as e:
            return {
                "preview": content[:max_length] if content else "",
                "error": f"Formatting error: {str(e)}"
            }
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text"""
        try:
            # Remove script and style elements
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Replace common HTML elements with text equivalents
            html_content = re.sub(r'<br[^>]*>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<p[^>]*>', '\n\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</p>', '', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'<div[^>]*>', '\n', html_content, flags=re.IGNORECASE)
            html_content = re.sub(r'</div>', '', html_content, flags=re.IGNORECASE)
            
            # Remove all other HTML tags
            html_content = re.sub(r'<[^>]+>', '', html_content)
            
            # Decode HTML entities
            html_content = html.unescape(html_content)
            
            return html_content
            
        except Exception as e:
            return html_content  # Return original if conversion fails
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with maximum of 2
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from lines
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        
        return text
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            # Remove protocol
            domain = url.replace('https://', '').replace('http://', '')
            # Remove path
            domain = domain.split('/')[0]
            # Remove port
            domain = domain.split(':')[0]
            return domain
        except Exception:
            return url
    
    def _is_shortened_url(self, url: str) -> bool:
        """Check if URL is from a URL shortening service"""
        shortener_domains = {
            'bit.ly', 'tinyurl.com', 'short.link', 'ow.ly', 't.co',
            'goo.gl', 'is.gd', 'buff.ly', 'adf.ly', 'bl.ink'
        }
        
        domain = self._extract_domain(url).lower()
        return domain in shortener_domains

class MessageFormatter:
    """Message-specific formatting utilities"""
    
    def __init__(self):
        self.text_formatter = TextFormatter()
    
    def format_ticket_reference(self, ticket_id: str) -> str:
        """Format ticket ID for display"""
        if not ticket_id:
            return ""
        
        # Ensure ticket ID has proper prefix
        if not ticket_id.upper().startswith(('TK-', 'TICKET-', '#')):
            return f"TK-{ticket_id.upper()}"
        
        return ticket_id.upper()
    
    def format_email_subject(self, subject: str, context: str = None) -> str:
        """Format email subject with context"""
        if not subject:
            return "No Subject"
        
        # Clean subject
        subject = subject.strip()
        
        # Add context prefix if provided
        if context:
            context_prefixes = {
                'reply': 'Re:',
                'forward': 'Fwd:',
                'urgent': '[URGENT]',
                'ticket': '[TICKET]'
            }
            
            prefix = context_prefixes.get(context.lower(), f'[{context.upper()}]')
            
            # Don't duplicate prefixes
            if not subject.upper().startswith(prefix.upper()):
                subject = f"{prefix} {subject}"
        
        return subject
    
    def format_response_time(self, priority: str) -> str:
        """Format expected response time based on priority"""
        response_times = {
            'critical': 'within 1 hour',
            'high': 'within 4 hours',
            'normal': 'within 24 hours',
            'low': 'within 48 hours'
        }
        
        return response_times.get(priority.lower(), 'within 24 hours')
    
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size for human readability"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"
    
    def format_timestamp(self, timestamp: str, format_type: str = 'friendly') -> str:
        """Format timestamp for display"""
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = timestamp
            
            if format_type == 'friendly':
                now = datetime.now(dt.tzinfo)
                diff = now - dt
                
                if diff.days == 0:
                    if diff.seconds < 3600:  # Less than 1 hour
                        minutes = diff.seconds // 60
                        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                    else:  # Less than 24 hours
                        hours = diff.seconds // 3600
                        return f"{hours} hour{'s' if hours != 1 else ''} ago"
                elif diff.days == 1:
                    return "yesterday"
                elif diff.days < 7:
                    return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
                else:
                    return dt.strftime('%Y-%m-%d')
            
            elif format_type == 'full':
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            elif format_type == 'date_only':
                return dt.strftime('%Y-%m-%d')
        except Exception as e:
            return str(e)