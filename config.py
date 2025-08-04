# Global config: API keys, env vars, etc.
from dotenv import load_dotenv
load_dotenv()  # Assure-toi que c'est au tout début
import os
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")


EMAIL_CONFIG = {
    'venom': {
        'api_url': os.getenv('VENOM_API_URL', 'http://localhost:3000'),
        'session_name': os.getenv('VENOM_SESSION', 'crm_session'),
        'timeout': int(os.getenv('VENOM_TIMEOUT', '30')),
        'email_to_phone_mapping': {
            # This would typically be loaded from database
            'customer@example.com': '+1234567890',
            'user@company.com': '+0987654321'
        }
    },
    'smtp': {
        'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('SMTP_USERNAME'),
        'password': os.getenv('SMTP_PASSWORD'),
        'from_email': os.getenv('FROM_EMAIL', 'support@yourcompany.com'),
        'use_tls': os.getenv('SMTP_TLS', 'true').lower() == 'true'
    },
    'templates': {
        'template_dir': 'communication/templates',
        'system_name': os.getenv('SYSTEM_NAME', 'CRM System')
    }
}

REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', '6379')),
    'db': int(os.getenv('REDIS_DB', '0')),
    'password': os.getenv('REDIS_PASSWORD')
}


EMAIL_CONFIG1 = {
            "venom": {
                "api_key": os.getenv('VENOM_API_KEY'),
                "base_url": os.getenv('VENOM_BASE_URL', 'https://api.venom.com/v1'),
                "webhook_secret": os.getenv('VENOM_WEBHOOK_SECRET'),
                "from_email": os.getenv('VENOM_FROM_EMAIL', 'support@yourcompany.com'),
                "from_name": os.getenv('VENOM_FROM_NAME', 'Support Team')
            },
            
            # SMTP Configuration (Fallback)
            "smtp": {
                "server": os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                "port": int(os.getenv('SMTP_PORT', '587')),
                "email": os.getenv('SMTP_EMAIL', 'support@yourcompany.com'),
                "password": os.getenv('SMTP_PASSWORD'),
                "use_tls": os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
            },
            
            # Communication Preferences
            "communication": {
                "primary_send_method": os.getenv('EMAIL_SEND_METHOD', 'venom'),  # venom or smtp
                "primary_receive_method": os.getenv('EMAIL_RECEIVE_METHOD', 'venom'),  # venom or imap
                "auto_response_enabled": os.getenv('AUTO_RESPONSE_ENABLED', 'true').lower() == 'true',
                "email_monitoring_interval": int(os.getenv('EMAIL_MONITOR_INTERVAL', '30')),  # seconds
                "max_email_size": int(os.getenv('MAX_EMAIL_SIZE', str(25 * 1024 * 1024))),  # 25MB
                "max_attachments": int(os.getenv('MAX_ATTACHMENTS', '10'))
            },
            
            # Security Settings
            "security": {
                "spam_threshold": float(os.getenv('SPAM_THRESHOLD', '8.0')),
                "virus_scan_enabled": os.getenv('VIRUS_SCAN_ENABLED', 'true').lower() == 'true',
                "attachment_scan_enabled": os.getenv('ATTACHMENT_SCAN_ENABLED', 'true').lower() == 'true',
                "quarantine_suspicious": os.getenv('QUARANTINE_SUSPICIOUS', 'true').lower() == 'true'
            },
            
            # Logging and Monitoring
            "logging": {
                "email_log_file": os.getenv('EMAIL_LOG_FILE', 'logs/email_activity.log'),
                "log_level": os.getenv('LOG_LEVEL', 'INFO'),
                "log_retention_days": int(os.getenv('LOG_RETENTION_DAYS', '30'))
            },
            
            # CRM Integration
            "crm": {
                "api_url": os.getenv('CRM_API_URL', 'http://localhost:3000/api'),
                "api_key": os.getenv('CRM_API_KEY'),
                "timeout": int(os.getenv('CRM_TIMEOUT', '30'))
            }
}