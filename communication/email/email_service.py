#responsible for handling the low-level details of sending emails using smtplib.
#class EmailService

# communication/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
from datetime import datetime
import logging

# Configure logging to a file
logging.basicConfig(filename='logs/email_activity.log', 
                    level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.sender_email = SMTP_USER

    def send_email(self, recipient_email, subject, body):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = Header(subject, 'utf-8')
            msg.attach(MIMEText(body, 'plain', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Use TLS for security
                server.login(self.smtp_user, self.smtp_password)
                text = msg.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
                time = datetime.now()
                logging.info(f"Email sent successfully to {recipient_email} for subject: '{subject}' at {time}")
                return True, "Email sent successfully."
        except Exception as e:
            logging.error(f"Failed to send email to {recipient_email}. Error: {e}")
            return False, f"Failed to send email: {e}"


email_service = EmailService()