# Tools/functions for tech support agent

from typing import Annotated, List, Tuple, Union
from langchain.tools import BaseTool, StructuredTool, Tool
from langchain_core.tools import tool
from databse import get_status

# => confirmation du traitement pour le client

# @tool("ticket", return_direct=False)
# def ticket_state(title: str):
#     """Provide information about the state of the ticket of the client from the database."""
#     state = get_status(title , "ticket")
#     return "DONE"


# @tool("ClientHistory", return_direct=True)
# def get_client_history(client_id: str) -> str:
#     """
#     Retrieve the full history of interactions with a given client ID.
#     """
#     # Retrieve the client history from the database




# => notification multi-canaux pour un nouveau ticket




# => sondage (1-10) note de traitement de ticket

# Technical Support Agent Tools
from langchain.tools import tool
from typing import Dict, Any, Optional
import json
import requests
from datetime import datetime, timedelta
import os

# CRM API configuration
CRM_API_BASE_URL = os.getenv('CRM_API_URL', 'http://localhost:3000/api')
CRM_API_KEY = os.getenv('CRM_API_KEY', 'your_api_key')

@tool
def get_ticket_state(ticket_id: str) -> Dict[str, Any]:
    """
    Get the current state of a ticket by its ID.
    This tool is used for DIRECT API communication - handles natural language queries.
    
    Args:
        ticket_id: The unique identifier of the ticket
        
    Returns:
        Dict containing ticket state information
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
                "status": ticket_data.get('status', 'Unknown'),
                "priority": ticket_data.get('priority', 'Medium'),
                "category": ticket_data.get('category', 'General'),
                "created_at": ticket_data.get('created_at'),
                "updated_at": ticket_data.get('updated_at'),
                "assigned_to": ticket_data.get('assigned_to'),
                "description": ticket_data.get('description', '')
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
    
    Args:
        priority: Priority level (Critical, High, Medium, Low)
        category: Category of the issue (Security, Network, Software, Hardware, General)
        
    Returns:
        Dict containing estimated resolution time
    """
    try:
        priority = priority.lower()
        category = category.lower()
        
        # Resolution time estimation logic based on priority and category
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

@tool
def process_new_ticket(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a new ticket that was already created in the CRM.
    This tool is used for ASYNC QUEUE communication (Redis) - receives complete structured data.
    
    Args:
        ticket_data: Complete ticket information from CRM containing:
                    - ticket_id, title, client_name, client_email, 
                    - status, priority, category, description, etc.
        
    Returns:
        Dict containing processing result and actions taken
    """
    try:
        # Extract key information
        ticket_id = ticket_data.get('ticket_id') or ticket_data.get('id')
        client_email = ticket_data.get('client_email')
        client_name = ticket_data.get('client_name')
        title = ticket_data.get('title')
        description = ticket_data.get('description', '')
        priority = ticket_data.get('priority', 'Medium')
        category = ticket_data.get('category', 'General')
        
        if not all([ticket_id, client_email, client_name, title]):
            return {
                "success": False,
                "error": "Missing required ticket information (ticket_id, client_email, client_name, title)"
            }
        
        # Prepare email content for the email agent
        email_content = {
            "to": client_email,
            "subject": f"Ticket Confirmation - #{ticket_id}: {title}",
            "template": "ticket_confirmation",
            "data": {
                "client_name": client_name,
                "ticket_id": ticket_id,
                "title": title,
                "description": description,
                "priority": priority,
                "category": category,
                "created_at": ticket_data.get('created_at', datetime.now().isoformat())
            }
        }
        
        # Get resolution estimate
        resolution_estimate = estimate_resolution_time_from_data(priority, category)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "client_info": {
                "name": client_name,
                "email": client_email
            },
            "ticket_details": {
                "title": title,
                "description": description,
                "priority": priority,
                "category": category
            },
            "email_content": email_content,
            "resolution_estimate": resolution_estimate,
            "actions_required": [
                "send_confirmation_email",
                "assign_to_technician",
                "schedule_follow_up"
            ],
            "message": f"New ticket {ticket_id} processed successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing ticket: {str(e)}"
        }

@tool
def request_email_send(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Request the Email Agent to send an email.
    This tool communicates with the Email Agent through the graph.
    
    Args:
        email_data: Dictionary containing email information:
                   - to: recipient email
                   - subject: email subject
                   - template: email template type
                   - data: template variables
        
    Returns:
        Dict containing email send request result
    """
    try:
        # This would typically invoke the email agent through your graph
        # For now, we'll return a structured request that can be handled by the supervisor
        return {
            "success": True,
            "action": "send_email",
            "email_request": email_data,
            "next_agent": "email_agent",
            "message": "Email send request prepared for Email Agent"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing email request: {str(e)}"
        }

@tool
def update_ticket_status(ticket_id: str, new_status: str, notes: str = "") -> Dict[str, Any]:
    """
    Update the status of an existing ticket.
    
    Args:
        ticket_id: The unique identifier of the ticket
        new_status: New status (Open, In Progress, Resolved, Closed)
        notes: Optional notes about the status change
        
    Returns:
        Dict containing update confirmation
    """
    try:
        headers = {
            'Authorization': f'Bearer {CRM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        update_data = {
            "status": new_status,
            "updated_at": datetime.now().isoformat(),
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
                "new_status": new_status,
                "updated_at": update_data["updated_at"],
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
def request_satisfaction_survey(ticket_id: str, client_email: str, client_name: str) -> Dict[str, Any]:
    """
    Request the Email Agent to send a satisfaction survey after ticket resolution.
    
    Args:
        ticket_id: The resolved ticket ID
        client_email: Client's email address
        client_name: Client's name
        
    Returns:
        Dict containing survey email request
    """
    try:
        survey_link = f"https://yourcompany.com/survey?ticket={ticket_id}"
        
        email_data = {
            "to": client_email,
            "subject": f"Satisfaction Survey - Ticket #{ticket_id}",
            "template": "satisfaction_survey",
            "data": {
                "client_name": client_name,
                "ticket_id": ticket_id,
                "survey_link": survey_link
            }
        }
        
        return {
            "success": True,
            "action": "send_email",
            "email_request": email_data,
            "next_agent": "email_agent",
            "message": f"Satisfaction survey request prepared for {client_email}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error preparing satisfaction survey: {str(e)}"
        }

# List of all technical support tools
tech_tool_list = [
    get_ticket_state,
    process_new_ticket,
    estimate_resolution_time_from_data,
    request_email_send,
    update_ticket_status,
    request_satisfaction_survey
]

