import imaplib
import email
import time
from config import EMAIL_IMAP_SERVER, EMAIL_LISTENER_PORT, EMAIL_LISTENER_USER, EMAIL_LISTENER_PASSWORD
from email.header import decode_header
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def parse_email(raw_email):
    """
    Parses a raw email message into a dictionary of useful information.
    """
    msg = email.message_from_bytes(raw_email)
    
    # Decode subject
    subject_raw = msg['subject']
    subject, encoding = decode_header(subject_raw)[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or 'utf-8')
    
    sender = msg.get('from')
    body = ""
    
    # Extract the email body
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                try:
                    body = part.get_payload(decode=True).decode()
                except UnicodeDecodeError:
                    body = part.get_payload(decode=True).decode('latin-1')
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode()
        except UnicodeDecodeError:
            body = msg.get_payload(decode=True).decode('latin-1')

    return {
        'sender': sender,
        'subject': subject,
        'body': body
    }

def listen_for_emails(process_callback):
    """
    Connects to the IMAP server, checks for new emails, and processes them.
    
    Args:
        process_callback: A function that handles the email data.
    """
    mail = imaplib.IMAP4_SSL(EMAIL_IMAP_SERVER, EMAIL_LISTENER_PORT)
    try:
        mail.login(EMAIL_LISTENER_USER, EMAIL_LISTENER_PASSWORD)
        mail.select('inbox')
        
        while True:
            status, messages = mail.search(None, 'UNSEEN')
            if status == 'OK':
                for mail_id in messages[0].split():
                    # Fetch the email
                    status, msg_data = mail.fetch(mail_id, '(RFC822)')
                    if status == 'OK':
                        # Parse the email
                        raw_email = msg_data[0][1]
                        email_data = parse_email(raw_email)
                        
                        logging.info(f"New email from: {email_data['sender']}")
                        
                        # Call the callback function to process the email
                        process_callback(email_data)
                        
                        # Mark the email as read to avoid re-processing
                        mail.store(mail_id, '+FLAGS', '\\Seen')
            
            logging.info("Waiting for new emails...")
            time.sleep(30) # Check for new emails every 30 seconds

    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP login or connection error: {e}")
    finally:
        mail.logout()

