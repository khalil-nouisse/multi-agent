# tools/tech_tools.py
from typing import Dict, Any
from langchain.tools import tool
import requests
from datetime import datetime, timedelta
from communication.email.email_service import email_service
from config import CRM_API_BASE_URL , CRM_API_KEY
import os


#ASYNC TOOLS

@tool
def process_new_ticket(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a new ticket that was already created in the CRM.
    This tool is used for ASYNC QUEUE communication (Redis) - receives complete structured data.
    Its job is to analyze the ticket and prepare it for the agent's workflow.
    
    Args:
        ticket_data: Complete ticket information from CRM.
        
    Returns:
        Dict containing processing result and ticket details.
    """
    try:
        ticket_id = ticket_data.get('ticket_id') or ticket_data.get('id')
        ticket_title = ticket_data.get('ticket_title')
        client_email = ticket_data.get('client_email')
        client_name = ticket_data.get('client_name')
        ticket_status = ticket_data.get('ticket_status')
        ticket_description = ticket_data.get('ticket_description', '')
        ticket_priority = ticket_data.get('ticket_priority', 'Medium')
        ticket_category = ticket_data.get('ticket_category', 'General')
        
        if not all([ticket_id, client_email, client_name, ticket_title]):
            return {
                "success": False,
                "error": "Missing required ticket information (ticket_id, client_email, client_name, title)"
            }
        
        resolution_estimate = estimate_resolution_time_from_data(ticket_priority, ticket_category)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "client_info": {
                "name": client_name,
                "email": client_email
            },
            "ticket_details": {
                "ticket_title": ticket_title,
                "ticket_status": ticket_status,
                "ticket_description": ticket_description,
                "ticket_priority": ticket_priority,
                "ticket_category": ticket_category,
                "resolution_estimate": resolution_estimate
            },
            "message": f"New ticket {ticket_id} processed successfully. The agent can now decide on further actions."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing ticket: {str(e)}"
        }

@tool
def request_satisfaction_survey(ticket_id: str, client_email: str, client_name: str) -> Dict[str, Any]:
    """
    Sends a satisfaction survey link to the client via email.
    
    Args:
        ticket_id: The resolved ticket ID.
        client_email: Client's email address.
        client_name: Client's name.
        
    Returns:
        Dict containing email sending result.
    """
    survey_link = f"https://yourcompany.com/survey?ticket={ticket_id}"
    subject = f"Satisfaction Survey - Ticket #{ticket_id}"
    body = (
        f"Hello {client_name},\n\n"
        f"Your ticket #{ticket_id} has been resolved. We would appreciate it if you could take a moment to provide feedback on our service.\n"
        f"You can fill out the survey here: {survey_link}\n\n"
        f"Best regards,\n"
        f"The Support Team"
    )
    
    # This tool now directly calls the generic email sending tool.
    return send_email_to_customer(to=client_email, subject=subject, body=body)

#QUERY TOOLS : =================================

@tool
def ticket_creator(ticket_title: str , ticket_client: str , ticket_status :str ,ticket_priority :str , ticket_category: str , ticket_description: str) :
    """
    Create new ticket based on the 
    """
    try:
        headers = {
            'Authorization': f'Bearer {CRM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        new_ticket = {
            "ticket_title": ticket_title,
            "ticket_client": ticket_client,
            "ticket_status": ticket_status,
            "ticket_priority": ticket_priority,
            "ticket_category": ticket_category,
            "ticket_description": ticket_description,
            "ticket_creation_date" : datetime.now().isoformat(), 
        }
        
        response = requests.patch(
            f"{CRM_API_BASE_URL}/tickets/{ticket_title}",
            headers=headers,
            json=new_ticket,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "ticket_title": ticket_title,
                "ticket_client": ticket_client,
                "ticket_status": ticket_status,
                "ticket_priority": ticket_priority,
                "ticket_category": ticket_category,
                "ticket_description": ticket_description,
                "ticket_creation_date" : datetime.now().isoformat(), 
                "message": f"Ticket {ticket_title} created successfully"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update ticket: {response.status_code}"
            }         
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }

@tool
def update_ticket_status(ticket_id: str = None, ticket_name: str = None, new_status : str = "" , notes: str = "") -> Dict[str, Any]:
    """
    Update the status of an existing ticket.
    ... (rest of the docstring) ...
    """
    try:
        headers = {
            'Authorization': f'Bearer {CRM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        update_data = {
            "ticket_status": new_status,
            "ticket_update_date": datetime.now().isoformat(),
            "notes": notes
        }
        
        response = requests.patch(
            f"{CRM_API_BASE_URL}/tickets/{ticket_id}",
            headers=headers,
            json=update_data,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "ticket_id": ticket_id,
                "ticket_name" : ticket_name,
                "ticket_status": new_status,
                "ticket_update_date": update_data["ticket_update_date"],
                "notes": notes,
                "message": f"Ticket {ticket_id} status updated to {new_status}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update ticket: {response.status_code}"
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }

@tool
def get_ticket_state_by_id(ticket_id: str) -> Dict[str, Any]:
    """
    Get the current state of a ticket by its ID.
    ... (rest of the docstring) ...
    """
    try:
        headers = {
            'Authorization': f'Bearer {CRM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{CRM_API_BASE_URL}/tickets/{ticket_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            ticket_data = response.json()
            return {
                "success": True,
                "ticket_id": ticket_id,
                "ticket_title": ticket_data.get('ticket_title', 'Unknown'),
                "ticket_status": ticket_data.get('ticket_status', 'Unknown'),
                "ticket_priority": ticket_data.get('ticket_priority', 'Unknown'),
                "ticket_category": ticket_data.get('ticket_category', 'General'),
                "ticket_creation_date": ticket_data.get('ticket_creation_date','Recently'),
                "ticket_client": ticket_data.get('ticket_client','Unknown'),
                "ticket_description": ticket_data.get('ticket_description', 'Unknown')
            }
        else:
            return {
                "success": False,
                "error": f"Ticket not found or API error: {response.status_code}"
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }
    
@tool
def get_ticket_state_by_title(ticket_title: str) -> Dict[str, Any]:
    """
    Get the current state of a ticket by its name.
    ... (rest of the docstring) ...
    """
    try:
        headers = {
            'Authorization': f'Bearer {CRM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{CRM_API_BASE_URL}/tickets/{ticket_title}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            ticket_data = response.json()
            return {
                "success": True,
                "ticket_title": ticket_title,
                "ticket_title": ticket_data.get('ticket_title', 'Unknown'),
                "ticket_status": ticket_data.get('ticket_status', 'Unknown'),
                "ticket_priority": ticket_data.get('ticket_priority', 'Unknown'),
                "ticket_category": ticket_data.get('ticket_category', 'General'),
                "ticket_creation_date": ticket_data.get('ticket_creation_date','Recently'),
                "ticket_client": ticket_data.get('ticket_client','Unknown'),
                "ticket_description": ticket_data.get('ticket_description', 'Unknown')
            }
        else:
            return {
                "success": False,
                "error": f"Ticket not found or API error: {response.status_code}"
            }
            
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Network error: {str(e)}"
        }

@tool
def estimate_resolution_time_from_data(priority: str, category: str) -> Dict[str, Any]:
    """
    Estimate resolution time based on priority and category.
    ... (rest of the docstring) ...
    """
    try:
        priority = priority.lower()
        category = category.lower()
        
        base_hours = {
            "critical": 2,
            "high": 8,
            "medium": 24,
            "low": 72
        }
        
        category_multiplier = {
            "security": 0.5,
            "network": 1.2,
            "software": 1.0,
            "hardware": 1.5,
            "general": 1.0
        }
        
        estimated_hours = base_hours.get(priority, 24) * category_multiplier.get(category, 1.0)
        estimated_completion = datetime.now() + timedelta(hours=estimated_hours)
        
        return {
            "success": True,
            "estimated_hours": round(estimated_hours, 1),
            "estimated_completion": estimated_completion.strftime("%Y-%m-%d %H:%M:%S"),
            "priority": priority.capitalize(),
            "category": category.capitalize()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error estimating resolution time: {str(e)}"
        }

#Email sending tool
@tool
def send_email_to_customer(to: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Sends a custom email to a client. Use this tool when you need to send a specific,
    ad-hoc message to a customer that is not a standard automated notification.
    
    Args:
        to: The recipient's email address.
        subject: The subject of the email.
        body: The content of the email.
        
    Returns:
        Dict containing the email sending result.
    """
    success, message = email_service.send_email(to, subject, body)
    if success:
        return {"success": True, "message": "Email sent successfully."}
    else:
        return {"success": False, "error": message}


# List of all technical support tools
tech_tool_list = [
    ticket_creator,
    get_ticket_state_by_id,
    get_ticket_state_by_title,
    process_new_ticket,
    estimate_resolution_time_from_data,
    send_email_to_customer,
    update_ticket_status,
    request_satisfaction_survey
]