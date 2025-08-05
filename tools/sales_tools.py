# tools/sales_tools.py
from typing import Dict, Any, Optional
from langchain.tools import tool
import requests
from datetime import datetime, timedelta
import os
import json

# Import the generic email sending tool from the tech_tools file
# In a real-world scenario, you might have a shared 'communication_tools' module
from tools.tech_tools import send_email_to_customer

# CRM API configuration
CRM_API_BASE_URL = os.getenv('CRM_API_URL', 'http://localhost:3000/api')
CRM_API_KEY = os.getenv('CRM_API_KEY', 'your_api_key')

# --- Opportunity-Related Tools ---

@tool
def process_new_opportunity(opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a new opportunity that was already created in the CRM.
    This tool is used for ASYNC QUEUE communication (Redis) - receives complete structured data.
    Its job is to analyze the opportunity and prepare it for the agent's workflow.

    Args:
        opportunity_data: Complete opportunity information from CRM containing:
                          - opportunity_id, opportunity_name, client_name, client_email,
                          - status, estimated_value, etc.

    Returns:
        Dict containing processing result and opportunity details.
    """
    try:
        opportunity_id = opportunity_data.get('opportunity_id') or opportunity_data.get('id')
        client_email = opportunity_data.get('client_email')
        client_name = opportunity_data.get('client_name')
        opportunity_name = opportunity_data.get('opportunity_name')
        
        if not all([opportunity_id, client_email, client_name, opportunity_name]):
            return {
                "success": False,
                "error": "Missing required opportunity information (id, client_email, name)"
            }
        
        # Here we could perform other CRM-related actions like lead enrichment
        # or initial qualification.

        return {
            "success": True,
            "opportunity_id": opportunity_id,
            "client_info": {
                "name": client_name,
                "email": client_email
            },
            "opportunity_details": {
                "name": opportunity_name,
                "status": opportunity_data.get('status'),
                "estimated_value": opportunity_data.get('estimated_value')
            },
            "message": f"New opportunity {opportunity_id} processed successfully. The agent can now decide on further actions."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing opportunity: {str(e)}"
        }

@tool
def get_opportunity_details(opportunity_id: str = None, opportunity_name: str = None) -> Dict[str, Any]:
    """
    Get the details of an opportunity by its ID or name.
    Use this tool when a client asks for information about a specific opportunity.

    Args:
        opportunity_id: The unique identifier of the opportunity.
        opportunity_name: The name of the opportunity.
        
    Returns:
        Dict containing opportunity details.
    """
    if not opportunity_id and not opportunity_name:
        return {"success": False, "error": "Either opportunity_id or opportunity_name must be provided."}
    
    try:
        headers = {'Authorization': f'Bearer {CRM_API_KEY}', 'Content-Type': 'application/json'}
        url = f"{CRM_API_BASE_URL}/opportunities"
        
        if opportunity_id:
            url += f"/{opportunity_id}"
            response = requests.get(url, headers=headers, timeout=10)
        else: # Search by name
            response = requests.get(url, params={'name': opportunity_name}, headers=headers, timeout=10)
            if response.status_code == 200 and response.json():
                opportunity_data = response.json()[0] # Assume first match is the correct one
                response = requests.get(f"{url}/{opportunity_data['id']}", headers=headers, timeout=10)
            else:
                return {"success": False, "error": "Opportunity not found."}

        if response.status_code == 200:
            opportunity_data = response.json()
            return {
                "success": True,
                "opportunity_id": opportunity_data.get('id'),
                "name": opportunity_data.get('name'),
                "status": opportunity_data.get('status'),
                "estimated_value": opportunity_data.get('estimated_value'),
                "client_name": opportunity_data.get('client_name'),
                "client_email": opportunity_data.get('client_email'),
                "last_activity": opportunity_data.get('last_activity')
            }
        else:
            return {"success": False, "error": f"API error: {response.status_code}"}
    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}


@tool
def create_new_opportunity(company_name: str, opportunity_name: str, commercial_name: str, estimated_turnover: float) -> Dict[str, Any]:
    """
    Create a new sales opportunity in the CRM.
    This is used when a client asks to create a new opportunity from a direct message.

    Args:
        company_name: The name of the company.
        opportunity_name: The name of the opportunity.
        commercial_name: The name of the commercial contact.
        estimated_turnover: The estimated value of the opportunity.

    Returns:
        Dict confirming the creation and including the new opportunity ID.
    """
    try:
        headers = {'Authorization': f'Bearer {CRM_API_KEY}', 'Content-Type': 'application/json'}
        payload = {
            "company_name": company_name,
            "opportunity_name": opportunity_name,
            "commercial_name": commercial_name,
            "estimated_turnover": estimated_turnover,
            "status": "New"  # Default status
        }
        
        response = requests.post(f"{CRM_API_BASE_URL}/opportunities", headers=headers, json=payload, timeout=10)

        if response.status_code == 201:
            new_opportunity = response.json()
            return {
                "success": True,
                "opportunity_id": new_opportunity.get('id'),
                "message": f"Successfully created new opportunity: {opportunity_name}"
            }
        else:
            return {"success": False, "error": f"API error: {response.status_code}"}
    except requests.RequestException as e:
        return {"success": False, "error": f"Network error: {str(e)}"}

# --- Appointment-Related Tools ---

@tool
def get_appointment_details(client_name: str = None, appointment_id: str = None) -> Dict[str, Any]:
    """
    Retrieve details of an appointment by client name or appointment ID.
    
    Args:
        client_name: The name of the client.
        appointment_id: The unique identifier of the appointment.
    
    Returns:
        Dict with appointment details.
    """
    if not client_name and not appointment_id:
        return {"success": False, "error": "Either client_name or appointment_id must be provided."}
    
    try:
        # Placeholder for real API call
        return {
            "success": True,
            "appointment_id": appointment_id or "app123",
            "client_name": client_name or "Test Client",
            "date": "2025-09-15",
            "time": "14:00",
            "purpose": "Discuss new opportunity",
            "location": "Online Meeting"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
def schedule_appointment(client_name: str, preferred_date: str, preferred_time: str, purpose: str) -> Dict[str, Any]:
    """
    Schedules a new appointment with a client.
    
    Args:
        client_name: The name of the client.
        preferred_date: The preferred date for the appointment (e.g., 'YYYY-MM-DD').
        preferred_time: The preferred time (e.g., 'HH:MM').
        purpose: The purpose of the meeting.
        
    Returns:
        Dict with the newly scheduled appointment details.
    """
    try:
        # Placeholder for real API call to the CRM's calendar service
        return {
            "success": True,
            "appointment_id": "new_app456",
            "client_name": client_name,
            "scheduled_date": preferred_date,
            "scheduled_time": preferred_time,
            "message": f"Appointment scheduled for {client_name} on {preferred_date} at {preferred_time}."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@tool
def send_appointment_reminder(client_email: str, appointment_id: str) -> Dict[str, Any]:
    """
    Sends an email reminder for an upcoming appointment.
    
    Args:
        client_email: The client's email address.
        appointment_id: The ID of the appointment.
        
    Returns:
        Dict with email sending status.
    """
    details = get_appointment_details(appointment_id=appointment_id)
    if not details.get('success'):
        return details

    subject = f"Appointment Reminder: {details['purpose']}"
    body = (
        f"Hello {details['client_name']},\n\n"
        f"This is a reminder for your upcoming appointment with our sales team.\n"
        f"Date: {details['date']}\n"
        f"Time: {details['time']}\n"
        f"Purpose: {details['purpose']}\n"
        f"Location: {details['location']}\n\n"
        f"We look forward to speaking with you.\n\n"
        f"Best regards,\n"
        f"The Sales Team"
    )

    return send_email_to_customer(to=client_email, subject=subject, body=body)

# --- Other Tools ---

@tool
def estimate_quote(product_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates an estimated quote for a product or service.
    
    Args:
        product_details: A dictionary containing details like product name, quantity, and customizations.
        
    Returns:
        Dict with the estimated quote and a message.
    """
    try:
        base_price = 1000
        quantity = product_details.get('quantity', 1)
        estimated_price = base_price * quantity
        
        return {
            "success": True,
            "estimated_price": estimated_price,
            "currency": "USD",
            "message": f"An estimated quote for your request is {estimated_price} USD."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}



sales_tool_list = [
    process_new_opportunity,
    get_opportunity_details,
    create_new_opportunity,
    get_appointment_details,
    schedule_appointment,
    send_appointment_reminder,
    estimate_quote,
    send_email_to_customer # The generic email tool should be in all tool lists that might need it
]