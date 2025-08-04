# communication/shared/utils/validators.py
# Validation utilities for communication system

import re
import dns.resolver
from typing import Dict, Any, List
from email.utils import parseaddr

class EmailValidator:
    """Email validation utilities"""
    
    def __init__(self):
        self.email_regex = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        self.disposable_domains = {
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'trash-mail.com', 'yopmail.com'
        }
        self.blocked_domains = {
            'spam.com', 'fake.com'  # Add known spam domains
        }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Comprehensive email validation
        
        Args:
            email: Email address to validate
            
        Returns:
            Dict containing validation results
        """
        try:
            # Basic format validation
            if not email or not isinstance(email, str):
                return {
                    "is_valid": False,
                    "error": "Email is required and must be a string"
                }
            
            email = email.strip().lower()
            
            # Check basic format
            if not self.email_regex.match(email):
                return {
                    "is_valid": False,
                    "error": "Invalid email format"
                }
            
            # Parse email parts
            name, addr = parseaddr(email)
            if not addr:
                return {
                    "is_valid": False,
                    "error": "Could not parse email address"
                }
            
            local_part, domain = addr.split('@')
            
            # Validate local part
            local_validation = self._validate_local_part(local_part)
            if not local_validation['valid']:
                return {
                    "is_valid": False,
                    "error": local_validation['error']
                }
            
            # Validate domain
            domain_validation = self._validate_domain(domain)
            if not domain_validation['valid']:
                return {
                    "is_valid": False,
                    "error": domain_validation['error']
                }
            
            # Check for disposable/temporary email
            is_disposable = domain.lower() in self.disposable_domains
            
            # Check for blocked domains
            is_blocked = domain.lower() in self.blocked_domains
            
            return {
                "is_valid": True,
                "email": addr,
                "local_part": local_part,
                "domain": domain,
                "is_disposable": is_disposable,
                "is_blocked": is_blocked,
                "domain_validation": domain_validation,
                "warnings": self._generate_warnings(is_disposable, is_blocked)
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def _validate_local_part(self, local_part: str) -> Dict[str, Any]:
        """Validate the local part of email (before @)"""
        if len(local_part) > 64:
            return {"valid": False, "error": "Local part too long (max 64 characters)"}
        
        if len(local_part) == 0:
            return {"valid": False, "error": "Local part cannot be empty"}
        
        # Check for valid characters
        valid_chars = re.compile(r'^[a-zA-Z0-9._%+-]+$')
        if not valid_chars.match(local_part):
            return {"valid": False, "error": "Invalid characters in local part"}
        
        # Check for consecutive dots
        if '..' in local_part:
            return {"valid": False, "error": "Consecutive dots not allowed"}
        
        # Check for starting/ending dots
        if local_part.startswith('.') or local_part.endswith('.'):
            return {"valid": False, "error": "Local part cannot start or end with dot"}
        
        return {"valid": True}
    
    def _validate_domain(self, domain: str) -> Dict[str, Any]:
        """Validate the domain part of email"""
        if len(domain) > 255:
            return {"valid": False, "error": "Domain too long (max 255 characters)"}
        
        if len(domain) == 0:
            return {"valid": False, "error": "Domain cannot be empty"}
        
        # Check domain format
        domain_regex = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        if not domain_regex.match(domain):
            return {"valid": False, "error": "Invalid domain format"}
        
        # Check for consecutive dots
        if '..' in domain:
            return {"valid": False, "error": "Consecutive dots not allowed in domain"}
        
        # DNS validation (optional - can be slow)
        dns_valid = self._check_mx_record(domain)
        
        return {
            "valid": True,
            "has_mx_record": dns_valid,
            "domain_parts": domain.split('.')
        }
    
    def _check_mx_record(self, domain: str) -> bool:
        """Check if domain has MX record (DNS validation)"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, Exception):
            return False
    
    def _generate_warnings(self, is_disposable: bool, is_blocked: bool) -> List[str]:
        """Generate warnings for email"""
        warnings = []
        
        if is_disposable:
            warnings.append("Email appears to be from a disposable/temporary email service")
        
        if is_blocked:
            warnings.append("Email domain is in blocked list")
        
        return warnings
    
    def validate_email_list(self, emails: List[str]) -> Dict[str, Any]:
        """Validate a list of emails"""
        results = []
        valid_count = 0
        
        for email in emails:
            validation = self.validate_email(email)
            results.append(validation)
            if validation.get('is_valid'):
                valid_count += 1
        
        return {
            "total_emails": len(emails),
            "valid_emails": valid_count,
            "invalid_emails": len(emails) - valid_count,
            "validation_results": results
        }

class MessageValidator:
    """Message content validation utilities"""
    
    def __init__(self):
        self.max_subject_length = 200
        self.max_content_length = 100000  # 100KB
        self.max_attachment_size = 25 * 1024 * 1024  # 25MB
        self.max_attachments = 10
    
    def validate_message_content(self, subject: str, content: str, 
                                attachments: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate message content
        
        Args:
            subject: Message subject
            content: Message content
            attachments: List of attachments
            
        Returns:
            Dict containing validation results
        """
        try:
            errors = []
            warnings = []
            
            # Validate subject
            if not subject or len(subject.strip()) == 0:
                errors.append("Subject is required")
            elif len(subject) > self.max_subject_length:
                errors.append(f"Subject too long (max {self.max_subject_length} characters)")
            
            # Validate content
            if not content or len(content.strip()) == 0:
                errors.append("Message content is required")
            elif len(content) > self.max_content_length:
                errors.append(f"Content too long (max {self.max_content_length} characters)")
            
            # Validate attachments
            if attachments:
                attachment_validation = self._validate_attachments(attachments)
                errors.extend(attachment_validation.get('errors', []))
                warnings.extend(attachment_validation.get('warnings', []))
            
            # Check for suspicious content
            suspicious_check = self._check_suspicious_content(subject, content)
            warnings.extend(suspicious_check.get('warnings', []))
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "content_stats": {
                    "subject_length": len(subject) if subject else 0,
                    "content_length": len(content) if content else 0,
                    "attachment_count": len(attachments) if attachments else 0
                }
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    def _validate_attachments(self, attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate attachments"""
        errors = []
        warnings = []
        
        if len(attachments) > self.max_attachments:
            errors.append(f"Too many attachments (max {self.max_attachments})")
        
        total_size = 0
        dangerous_extensions = ['.exe', '.bat', '.scr', '.pif', '.vbs', '.jar']
        
        for i, attachment in enumerate(attachments):
            filename = attachment.get('filename', f'attachment_{i}')
            size = attachment.get('size', 0)
            
            # Check file size
            if size > self.max_attachment_size:
                errors.append(f"Attachment '{filename}' too large (max 25MB)")
            
            total_size += size
            
            # Check dangerous extensions
            if any(filename.lower().endswith(ext) for ext in dangerous_extensions):
                warnings.append(f"Potentially dangerous file type: {filename}")
            
            # Check for missing filename
            if not filename or filename.strip() == '':
                warnings.append(f"Attachment {i+1} has no filename")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "total_size": total_size
        }
    
    def _check_suspicious_content(self, subject: str, content: str) -> Dict[str, Any]:
        """Check for suspicious content patterns"""
        warnings = []
        full_text = f"{subject} {content}".lower()
        
        # Suspicious patterns
        suspicious_patterns = [
            (r'urgent.*transfer.*money', "Potential financial scam"),
            (r'lottery.*winner.*claim', "Potential lottery scam"),
            (r'prince.*nigeria.*inheritance', "Potential advance fee fraud"),
            (r'click.*here.*now', "Potential phishing attempt"),
            (r'limited.*time.*offer.*expires', "Potential spam"),
        ]
        
        for pattern, warning in suspicious_patterns:
            if re.search(pattern, full_text):
                warnings.append(warning)
        
        # Check for excessive caps
        if len(re.findall(r'[A-Z]', subject + content)) > len(subject + content) * 0.3:
            warnings.append("Excessive use of capital letters")
        
        # Check for excessive punctuation
        if len(re.findall(r'[!?]', subject + content)) > 5:
            warnings.append("Excessive use of exclamation marks or question marks")
        
        return {"warnings": warnings}

class AttachmentValidator:
    """Attachment validation utilities"""
    
    def __init__(self):
        self.allowed_extensions = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'spreadsheets': ['.xls', '.xlsx', '.csv'],
            'presentations': ['.ppt', '.pptx']
        }
        
        self.dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.scr', '.pif', '.vbs', '.vbe',
            '.js', '.jse', '.wsf', '.wsh', '.msi', '.jar'
        ]
        
        self.max_file_size = 25 * 1024 * 1024  # 25MB
        
    def validate_attachment(self, filename: str, content_type: str, 
                          size: int, content: bytes = None) -> Dict[str, Any]:
        """
        Validate a single attachment
        
        Args:
            filename: Name of the file
            content_type: MIME type
            size: File size in bytes
            content: File content (optional)
            
        Returns:
            Dict containing validation results
        """
        try:
            errors = []
            warnings = []
            
            # Validate filename
            if not filename or filename.strip() == '':
                errors.append("Filename is required")
                return {"is_valid": False, "errors": errors}
            
            # Check file extension
            file_ext = '.' + filename.lower().split('.')[-1] if '.' in filename else ''
            
            if file_ext in self.dangerous_extensions:
                errors.append(f"Dangerous file type: {file_ext}")
            
            # Check file size
            if size > self.max_file_size:
                errors.append(f"File too large: {size} bytes (max 25MB)")
            
            # Validate content type
            if not content_type:
                warnings.append("Missing content type")
            elif not self._is_valid_content_type(content_type, file_ext):
                warnings.append(f"Content type '{content_type}' doesn't match file extension '{file_ext}'")
            
            # Additional security checks
            if content:
                security_check = self._security_scan_content(content, filename)
                warnings.extend(security_check.get('warnings', []))
                errors.extend(security_check.get('errors', []))
            
            return {
                "is_valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "file_info": {
                    "filename": filename,
                    "extension": file_ext,
                    "content_type": content_type,
                    "size": size,
                    "category": self._categorize_file(file_ext)
                }
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"Attachment validation error: {str(e)}"]
            }
    
    def _is_valid_content_type(self, content_type: str, file_ext: str) -> bool:
        """Check if content type matches file extension"""
        type_mapping = {
            '.pdf': ['application/pdf'],
            '.jpg': ['image/jpeg'],
            '.jpeg': ['image/jpeg'],
            '.png': ['image/png'],
            '.gif': ['image/gif'],
            '.txt': ['text/plain'],
            '.doc': ['application/msword'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            '.zip': ['application/zip'],
        }
        
        expected_types = type_mapping.get(file_ext, [])
        return not expected_types or content_type in expected_types
    
    def _categorize_file(self, file_ext: str) -> str:
        """Categorize file by extension"""
        for category, extensions in self.allowed_extensions.items():
            if file_ext in extensions:
                return category
        return 'other'
    
    def _security_scan_content(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Basic security scan of file content"""
        warnings = []
        errors = []
        
        # Check for embedded executables (simplified)
        if b'MZ' in content[:100]:  # DOS header
            errors.append("File contains executable code")
        
        # Check for script content in non-script files
        if not filename.lower().endswith(('.js', '.vbs', '.bat', '.cmd')):
            script_patterns = [b'<script', b'javascript:', b'vbscript:']
            if any(pattern in content.lower() for pattern in script_patterns):
                warnings.append("File contains script content")
        
        return {
            "warnings": warnings,
            "errors": errors
        }