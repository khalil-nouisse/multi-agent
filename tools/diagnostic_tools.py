# tools/diagnostic_tools.py
from typing import Dict, Any, List, Optional
from langchain.tools import tool
import os
import json
import requests
from datetime import datetime
from config import ENGINEERING_TEAM_EMAIL , CHROMA_DB_URL ,LOG_AGGREGATION_API_URL
from tools.tech_tools import send_email_to_customer


@tool
def search_knowledge_base(query: str) -> List[Dict[str, Any]]:
    """
    Searches the internal knowledge base for solutions to known problems using semantic search.
    
    This tool is the primary source for finding solutions to common issues. It makes an API call to
    a vector database (Chroma DB) to find the most relevant articles or solutions.
    
    Args:
        query: A natural language string representing the problem, error message, or keyword.
        
    Returns:
        A list of dictionaries, where each dictionary represents a potential solution.
        Each dictionary contains: 'title', 'summary', and 'steps_to_resolve'.
        Returns an empty list if no solutions are found or the service is unavailable.
    """
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'query': query, 'n_results': 5} # Requesting top 5 results
        
        # This simulates an API call to a Chroma DB service
        response = requests.post(f"{CHROMA_DB_URL}/search", json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Knowledge Base API error: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Knowledge Base API network error: {e}")
        return []

@tool
def search_log_files(error_pattern: str, timeframe_hours: Optional[int] = 1) -> List[str]:
    """
    Searches a centralized log aggregation service for a specific error pattern.
    
    This tool is used to find recent occurrences of a specific error message in the system logs.
    It makes an API call to a log service (e.g., Loki, Elasticsearch).
    
    Args:
        error_pattern: A string pattern (e.g., 'Error code: 500' or 'database connection failure').
        timeframe_hours: The number of hours to search back from the current time.
    
    Returns:
        A list of log entries that match the pattern, or an empty list if none are found.
    """
    try:
        headers = {'Content-Type': 'application/json'}
        params = {'pattern': error_pattern, 'timeframe_hours': timeframe_hours}
        
        # This simulates an API call to a log aggregation service
        response = requests.get(LOG_AGGREGATION_API_URL, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json().get('logs', [])
        else:
            print(f"Log Aggregation API error: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Log Aggregation API network error: {e}")
        return []

@tool
def escalate_to_engineering(problem_summary: str, logs: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Escalates a problem to the human engineering team for further investigation.
    
    This tool sends a detailed summary and relevant log snippets to the engineering team's email.
    
    Args:
        problem_summary: A concise summary of the issue.
        logs: Optional list of relevant log entries.
        
    Returns:
        Dict confirming the escalation email was sent.
    """
    subject = f"Urgent: Escalation from Diagnostic Agent - {problem_summary}"
    
    body = f"Problem Summary:\n{problem_summary}\n\n"
    if logs:
        body += "Relevant Log Entries:\n" + "\n".join(logs)
    else:
        body += "No specific logs were found during the automated diagnosis."
    
    return send_email_to_customer(to=ENGINEERING_TEAM_EMAIL, subject=subject, body=body)

# --- Final list of all diagnostic tools ---
diagnostic_tool_list = [
    search_knowledge_base,
    search_log_files,
    escalate_to_engineering,
    send_email_to_customer
]